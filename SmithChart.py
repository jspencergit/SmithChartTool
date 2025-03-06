import matplotlib
matplotlib.use('Qt5Agg')  # Use Qt5Agg to match Spyder's default backend
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk

# Global variables to share between Tkinter and Matplotlibf
Z0 = 50
gamma_value = 0.50  # Initial value with two decimal places
show_circle = False
db_value = -6.0  # Initial dB value corresponding to gamma_value

def update_circle():
    global gamma_patch, show_circle, gamma_value
    if 'gamma_patch' in globals():
        gamma_patch.set_radius(gamma_value)
        gamma_patch.set_visible(show_circle)
        plt.gcf().canvas.draw()

def draw_smith_chart():
    global gamma_patch
    print("Starting draw_smith_chart...")  # Debug print
    # Create figure and axes
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_axes([0.15, 0.05, 0.80, 0.90])
    ax.set_aspect('equal')
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis('off')

    # Draw the outer boundary
    outer_circle = plt.Circle((0, 0), 1, fill=False, color='black', linewidth=1.5)
    ax.add_patch(outer_circle)

    # Constant resistance circles
    resistance_values = [0, 0.5, 1, 2, 5]
    r_colors = ['blue', 'green', 'red', 'purple', 'orange']
    for r, color in zip(resistance_values, r_colors):
        if r == 0:
            ax.plot(-1, 0, 'o', color=color, markersize=5)
        else:
            center_x = r / (1 + r)
            radius = 1 / (1 + r)
            circle = plt.Circle((center_x, 0), radius, fill=False, color=color, linewidth=1)
            ax.add_patch(circle)

    # Constant reactance arcs
    reactance_values = [0, 0.5, 1, 2]
    x_colors = ['gray', 'cyan', 'magenta', 'brown']
    for i, (x, color) in enumerate(zip(reactance_values, x_colors)):
        if x == 0:
            ax.plot([-1, 1], [0, 0], color=color, linewidth=1, linestyle='--')
        else:
            center_x = 1
            center_y = 1 / x
            radius = 1 / x
            theta_max = 2 * np.arctan(1 / x)
            theta = np.linspace(0, theta_max, 100)
            x_upper = center_x - radius * np.cos(theta)
            y_upper = center_y - radius * np.sin(theta)
            x_lower = x_upper
            y_lower = -y_upper
            mask_upper = (x_upper**2 + y_upper**2) <= 1.01
            mask_lower = (x_lower**2 + y_lower**2) <= 1.01
            ax.plot(x_upper[mask_upper], y_upper[mask_upper], color=color, linewidth=1, linestyle='--')
            ax.plot(x_lower[mask_lower], y_lower[mask_lower], color=color, linewidth=1, linestyle='--')

    # Labels
    labels = [
        ('0 Ω', -1.05, 0.0, 'blue', 9, 'right', 'center', 0),
        ('25 Ω', -0.20, 0.05, 'green', 9, 'right', 'center', 0),
        ('50 Ω', 0.15, 0.05, 'red', 9, 'right', 'center', 0),
        ('100 Ω', 0.50, 0.05, 'purple', 9, 'right', 'center', 0),
        ('250 Ω', 0.90, 0.10, 'orange', 9, 'right', 'center', 0),
        ('j0 Ω', -0.75, 0.025, 'gray', 9, 'left', 'bottom', 0),
        ('j25 Ω', -0.52, 0.65, 'cyan', 9, 'center', 'center', -45),
        ('-j25 Ω', -0.52, -0.65, 'cyan', 9, 'center', 'center', 45),
        ('j50 Ω', -0.01, 0.75, 'magenta', 9, 'center', 'center', -70),
        ('-j50 Ω', -0.01, -0.75, 'magenta', 9, 'center', 'center', 70),
        ('j100 Ω', 0.45, 0.402, 'brown', 9, 'center', 'center', -85),
        ('-j100 Ω', 0.45, -0.402, 'brown', 9, 'center', 'center', 85),
    ]
    for text, x, y, color, fontsize, ha, va, rotation in labels:
        ax.text(x, y, text, color=color, fontsize=fontsize, ha=ha, va=va, 
                rotation=rotation, rotation_mode='anchor')

    # Dynamic impedance display for mouse movement
    coord_text = ax.text(0.05, 0.95, '', transform=ax.transAxes, fontsize=10, 
                         bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

    def update_coords(event):
        if event.inaxes == ax:
            gamma_x = event.xdata
            gamma_y = event.ydata
            if gamma_x**2 + gamma_y**2 <= 1:
                gamma = complex(gamma_x, gamma_y)
                z_normalized = (1 + gamma) / (1 - gamma)
                Z = z_normalized * Z0
                R = Z.real
                X = Z.imag
                if abs(X) < 0.1:
                    coord_str = f'Z = {R:.1f} Ω'
                else:
                    sign = '+' if X >= 0 else '-'
                    coord_str = f'Z = {R:.1f} {sign} j{abs(X):.1f} Ω'
                coord_text.set_text(coord_str)
            else:
                coord_text.set_text('Outside Smith Chart')
        else:
            coord_text.set_text('')
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('motion_notify_event', update_coords)

    # Title centered above chart
    fig.text(0.5, 0.97, f"Smith Chart (Z₀ = {Z0} Ω) with Constant Resistance and Reactance", 
             fontsize=12, ha='center', va='top')

    # Reflection coefficient circle (initially off)
    gamma_circle = plt.Circle((0, 0), gamma_value, fill=False, color='black', linestyle='dotted', linewidth=1.5)
    gamma_patch = ax.add_patch(gamma_circle)
    gamma_patch.set_visible(show_circle)
    print("Gamma circle created, initial radius:", gamma_value, "visibility:", show_circle)  # Debug print

    # Click event handling for marking a single impedance
    click_marker = None
    click_text = None

    def on_click(event):
        nonlocal click_marker, click_text
        if event.inaxes != ax:
            return
        gamma_x = event.xdata
        gamma_y = event.ydata
        if gamma_x**2 + gamma_y**2 > 1:
            return

        # Remove previous marker and text if they exist
        if click_marker is not None:
            click_marker.remove()
        if click_text is not None:
            click_text.remove()

        # Calculate impedance
        gamma = complex(gamma_x, gamma_y)
        z_normalized = (1 + gamma) / (1 - gamma)
        Z = z_normalized * Z0
        R = Z.real
        X = Z.imag
        if abs(X) < 0.1:
            impedance_str = f'Z = {R:.1f} Ω'
        else:
            sign = '+' if X >= 0 else '-'
            impedance_str = f'Z = {R:.1f} {sign} j{abs(X):.1f} Ω'

        # Add colored dot
        click_marker, = ax.plot(gamma_x, gamma_y, 'ro', markersize=8)

        # Add impedance text next to the dot
        offset = 0.1
        ha = 'left' if gamma_x < 0 else 'right'
        va = 'bottom' if gamma_y < 0 else 'top'
        text_x = gamma_x + offset if gamma_x < 0 else gamma_x - offset
        text_y = gamma_y + offset if gamma_y < 0 else gamma_y - offset
        click_text = ax.text(text_x, text_y, impedance_str, fontsize=10, ha=ha, va=va, 
                             color='black', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('button_press_event', on_click)

    # Show the Matplotlib figure in a separate window
    plt.show()

# Create Tkinter window for controls
root = tk.Tk()
root.title("Return Loss Controls")
root.geometry("600x150")  # Increased height to accommodate sliders

# Frame for controls
control_frame = tk.Frame(root)
control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

# Gamma (|Γ|) text box, buttons, and slider
gamma_frame = tk.Frame(control_frame)
gamma_frame.pack(side=tk.LEFT, padx=5)

# Text box and buttons
gamma_input_frame = tk.Frame(gamma_frame)
gamma_input_frame.pack(side=tk.TOP)

tk.Label(gamma_input_frame, text="|Γ|:").pack(side=tk.LEFT)
gamma_entry = tk.Entry(gamma_input_frame)
gamma_entry.insert(0, f'{gamma_value:.2f}')  # Two decimal places
gamma_entry.pack(side=tk.LEFT, padx=5)

def increment_gamma():
    global gamma_value, db_value
    try:
        current_gamma = float(gamma_entry.get())
        new_gamma = round(min(1, current_gamma + 0.01), 2)  # Two decimal places
        if new_gamma != current_gamma:
            gamma_value = new_gamma
            db_value = 20 * np.log10(gamma_value) if gamma_value > 0 else -float('inf')
            gamma_entry.delete(0, tk.END)
            gamma_entry.insert(0, f'{gamma_value:.2f}')
            db_entry.delete(0, tk.END)
            db_entry.insert(0, f'{db_value:.1f}' if db_value > -float('inf') else '-inf')
            gamma_slider.set(gamma_value)  # Update slider position
            db_slider.set(db_value)  # Update dB slider position
            update_circle()
    except ValueError:
        gamma_entry.delete(0, tk.END)
        gamma_entry.insert(0, f'{gamma_value:.2f}')

def decrement_gamma():
    global gamma_value, db_value
    try:
        current_gamma = float(gamma_entry.get())
        new_gamma = round(max(0, current_gamma - 0.01), 2)  # Two decimal places
        if new_gamma != current_gamma:
            gamma_value = new_gamma
            db_value = 20 * np.log10(gamma_value) if gamma_value > 0 else -float('inf')
            gamma_entry.delete(0, tk.END)
            gamma_entry.insert(0, f'{gamma_value:.2f}')
            db_entry.delete(0, tk.END)
            db_entry.insert(0, f'{db_value:.1f}' if db_value > -float('inf') else '-inf')
            gamma_slider.set(gamma_value)  # Update slider position
            db_slider.set(db_value)  # Update dB slider position
            update_circle()
    except ValueError:
        gamma_entry.delete(0, tk.END)
        gamma_entry.insert(0, f'{gamma_value:.2f}')

tk.Button(gamma_input_frame, text="↑", command=increment_gamma, width=2).pack(side=tk.LEFT)
tk.Button(gamma_input_frame, text="↓", command=decrement_gamma, width=2).pack(side=tk.LEFT)

def update_from_gamma(event=None):
    global gamma_value, db_value
    try:
        new_gamma = float(gamma_entry.get())
        if 0 <= new_gamma <= 1:
            gamma_value = round(new_gamma, 2)  # Two decimal places
            db_value = 20 * np.log10(gamma_value) if gamma_value > 0 else -float('inf')
            gamma_entry.delete(0, tk.END)
            gamma_entry.insert(0, f'{gamma_value:.2f}')
            db_entry.delete(0, tk.END)
            db_entry.insert(0, f'{db_value:.1f}' if db_value > -float('inf') else '-inf')
            gamma_slider.set(gamma_value)  # Update slider position
            db_slider.set(db_value)  # Update dB slider position
            update_circle()
        else:
            gamma_entry.delete(0, tk.END)
            gamma_entry.insert(0, f'{gamma_value:.2f}')
    except ValueError:
        gamma_entry.delete(0, tk.END)
        gamma_entry.insert(0, f'{gamma_value:.2f}')

gamma_entry.bind('<Return>', update_from_gamma)

def scroll_gamma(event):
    global gamma_value, db_value
    try:
        current_gamma = float(gamma_entry.get())
        # Normalize delta (positive up, negative down)
        step = 0.01 * (event.delta // 120)  # Positive for up, negative for down
        new_gamma = round(max(0, min(1, current_gamma + step)), 2)  # Two decimal places
        if new_gamma != current_gamma:
            gamma_value = new_gamma
            db_value = 20 * np.log10(gamma_value) if gamma_value > 0 else -float('inf')
            gamma_entry.delete(0, tk.END)
            gamma_entry.insert(0, f'{gamma_value:.2f}')
            db_entry.delete(0, tk.END)
            db_entry.insert(0, f'{db_value:.1f}' if db_value > -float('inf') else '-inf')
            gamma_slider.set(gamma_value)  # Update slider position
            db_slider.set(db_value)  # Update dB slider position
            update_circle()
    except ValueError:
        gamma_entry.delete(0, tk.END)
        gamma_entry.insert(0, f'{gamma_value:.2f}')

# Bind mouse wheel events for gamma_entry
gamma_entry.bind('<MouseWheel>', scroll_gamma)  # Windows
gamma_entry.bind('<Button-4>', lambda event: scroll_gamma(event.__setitem__('delta', 120)))  # Linux (scroll up)
gamma_entry.bind('<Button-5>', lambda event: scroll_gamma(event.__setitem__('delta', -120)))  # Linux (scroll down)

# Slider for |Γ|
def on_gamma_slider_change(value):
    global gamma_value, db_value
    new_gamma = round(float(value), 2)
    if new_gamma != gamma_value:
        gamma_value = new_gamma
        db_value = 20 * np.log10(gamma_value) if gamma_value > 0 else -float('inf')
        gamma_entry.delete(0, tk.END)
        gamma_entry.insert(0, f'{gamma_value:.2f}')
        db_entry.delete(0, tk.END)
        db_entry.insert(0, f'{db_value:.1f}' if db_value > -float('inf') else '-inf')
        db_slider.set(db_value)  # Update dB slider position
        update_circle()

gamma_slider = tk.Scale(gamma_frame, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, 
                        command=on_gamma_slider_change, length=100)
gamma_slider.set(gamma_value)
gamma_slider.pack(side=tk.TOP)

# dB text box, buttons, and slider
db_frame = tk.Frame(control_frame)
db_frame.pack(side=tk.LEFT, padx=5)

# Text box and buttons
db_input_frame = tk.Frame(db_frame)
db_input_frame.pack(side=tk.TOP)

tk.Label(db_input_frame, text="dB:").pack(side=tk.LEFT)
db_entry = tk.Entry(db_input_frame)
db_entry.insert(0, f'{db_value:.1f}')  # One decimal place
db_entry.pack(side=tk.LEFT, padx=5)

def update_from_db(event=None):
    global gamma_value, db_value
    try:
        new_db = float(db_entry.get())
        if new_db <= 0:
            gamma_value = round(10**(new_db / 20), 2)
            db_value = new_db  # Update global db_value with the new valid value
            db_entry.delete(0, tk.END)
            db_entry.insert(0, f'{db_value:.1f}')
            gamma_entry.delete(0, tk.END)
            gamma_entry.insert(0, f'{gamma_value:.2f}')
            gamma_slider.set(gamma_value)  # Update |Γ| slider position
            db_slider.set(db_value)  # Update dB slider position
            update_circle()
        else:
            db_entry.delete(0, tk.END)
            db_entry.insert(0, f'{db_value:.1f}')  # Use global db_value for reset
    except ValueError:
        db_entry.delete(0, tk.END)
        db_entry.insert(0, f'{db_value:.1f}')  # Use global db_value for reset

db_entry.bind('<Return>', update_from_db)

def increment_db():
    global db_value, gamma_value
    try:
        current_db = float(db_entry.get())
        new_db = round(min(0, current_db + 0.1), 1)  # One decimal place, constrained to 0
        if new_db != current_db:
            db_value = new_db
            gamma_value = round(10**(db_value / 20), 2)
            db_entry.delete(0, tk.END)
            db_entry.insert(0, f'{db_value:.1f}')
            gamma_entry.delete(0, tk.END)
            gamma_entry.insert(0, f'{gamma_value:.2f}')
            gamma_slider.set(gamma_value)  # Update |Γ| slider position
            db_slider.set(db_value)  # Update dB slider position
            update_circle()
    except ValueError:
        db_entry.delete(0, tk.END)
        db_entry.insert(0, f'{db_value:.1f}')

def decrement_db():
    global db_value, gamma_value
    try:
        current_db = float(db_entry.get())
        new_db = round(current_db - 0.1, 1)  # One decimal place
        if new_db != current_db:
            db_value = new_db
            gamma_value = round(10**(db_value / 20), 2)
            db_entry.delete(0, tk.END)
            db_entry.insert(0, f'{db_value:.1f}')
            gamma_entry.delete(0, tk.END)
            gamma_entry.insert(0, f'{gamma_value:.2f}')
            gamma_slider.set(gamma_value)  # Update |Γ| slider position
            db_slider.set(db_value)  # Update dB slider position
            update_circle()
    except ValueError:
        db_entry.delete(0, tk.END)
        db_entry.insert(0, f'{db_value:.1f}')

tk.Button(db_input_frame, text="↑", command=increment_db, width=2).pack(side=tk.LEFT)
tk.Button(db_input_frame, text="↓", command=decrement_db, width=2).pack(side=tk.LEFT)

def scroll_db(event):
    global gamma_value, db_value
    try:
        current_db = float(db_entry.get())
        # Normalize delta (positive up, negative down)
        step = 0.1 * (event.delta // 120)  # Positive for up, negative for down
        new_db = round(current_db + step, 1)  # One decimal place
        if new_db <= 0 and new_db != current_db:
            gamma_value = round(10**(new_db / 20), 2)
            db_value = new_db  # Update global db_value with the new valid value
            db_entry.delete(0, tk.END)
            db_entry.insert(0, f'{new_db:.1f}')
            gamma_entry.delete(0, tk.END)
            gamma_entry.insert(0, f'{gamma_value:.2f}')
            gamma_slider.set(gamma_value)  # Update |Γ| slider position
            db_slider.set(db_value)  # Update dB slider position
            update_circle()
        elif new_db > 0:
            db_entry.delete(0, tk.END)
            db_entry.insert(0, f'{db_value:.1f}')  # Reset to last valid global db_value
    except ValueError:
        db_entry.delete(0, tk.END)
        db_entry.insert(0, f'{db_value:.1f}')  # Reset to last valid global db_value

# Bind mouse wheel events for db_entry
db_entry.bind('<MouseWheel>', scroll_db)  # Windows
db_entry.bind('<Button-4>', lambda event: scroll_db(event.__setitem__('delta', 120)))  # Linux (scroll up)
db_entry.bind('<Button-5>', lambda event: scroll_db(event.__setitem__('delta', -120)))  # Linux (scroll down)

# Slider for dB
def on_db_slider_change(value):
    global gamma_value, db_value
    new_db = round(float(value), 1)
    if new_db != db_value:
        db_value = new_db
        gamma_value = round(10**(db_value / 20), 2)
        db_entry.delete(0, tk.END)
        db_entry.insert(0, f'{db_value:.1f}')
        gamma_entry.delete(0, tk.END)
        gamma_entry.insert(0, f'{gamma_value:.2f}')
        gamma_slider.set(gamma_value)  # Update |Γ| slider position
        update_circle()

db_slider = tk.Scale(db_frame, from_=-30.0, to=0.0, resolution=0.1, orient=tk.HORIZONTAL, 
                     command=on_db_slider_change, length=100)
db_slider.set(db_value)
db_slider.pack(side=tk.TOP)

# Show |Γ| Circle checkbox
show_var = tk.BooleanVar(value=show_circle)
tk.Checkbutton(control_frame, text="Show |Γ| Circle", variable=show_var).pack(side=tk.LEFT, padx=5)

def update_show_circle():
    global show_circle
    show_circle = show_var.get()
    update_circle()

show_var.trace('w', lambda *args: update_show_circle())

# Draw the Smith Chart
draw_smith_chart()

# Start the Tkinter event loop
root.mainloop()

if __name__ == "__main__":
    pass
