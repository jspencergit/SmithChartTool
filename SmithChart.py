import matplotlib
matplotlib.use('Qt5Agg')  # Use Qt5Agg to match Spyder's default backend
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk

# Global variables
Z0 = 50  # Characteristic impedance (50 Ω)
gamma_value = 0.50  # Initial reflection coefficient magnitude
show_circle = False
db_value = -6.0  # Initial dB value corresponding to gamma_value
load_impedance = None  # Initial load impedance (R + jX)
current_impedance = None  # Current impedance after matching
impedance_points = []  # List to store impedance points for plotting trajectory
frequency = 1e9  # Initial frequency for reactance calculations (1 GHz)
gamma_patch = None  # Initialize gamma_patch at the module level
smith_chart_patches = []  # Store original Smith Chart patches
smith_chart_lines = []  # Store original Smith Chart lines

def update_circle():
    global gamma_patch, show_circle, gamma_value
    if gamma_patch is not None:  # Check if gamma_patch has been initialized
        gamma_patch.set_radius(gamma_value)
        gamma_patch.set_visible(show_circle)
        plt.gcf().canvas.draw()

def impedance_to_gamma(Z):
    """Convert impedance to reflection coefficient."""
    z_normalized = Z / Z0
    gamma = (z_normalized - 1) / (z_normalized + 1)
    return gamma

def gamma_to_impedance(gamma):
    """Convert reflection coefficient to impedance."""
    z_normalized = (1 + gamma) / (1 - gamma)
    return z_normalized * Z0

def add_series_component(Z, reactance):
    """Add a series component (inductor or capacitor) with given reactance."""
    return Z + 1j * reactance

def add_shunt_component(Z, reactance):
    """Add a shunt component (inductor or capacitor) with given reactance."""
    Y = 1 / Z  # Current admittance
    Y_component = -1j / reactance if reactance != 0 else 0  # Admittance of shunt component (Y = -j / X)
    Y_new = Y + Y_component
    return 1 / Y_new if Y_new != 0 else Z

def draw_smith_chart():
    global gamma_patch, smith_chart_patches, smith_chart_lines
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
    smith_chart_patches = [outer_circle]

    # Constant resistance circles
    resistance_values = [0, 0.5, 1, 2, 5]
    r_colors = ['blue', 'green', 'red', 'purple', 'orange']
    for r, color in zip(resistance_values, r_colors):
        if r == 0:
            line, = ax.plot(-1, 0, 'o', color=color, markersize=5)
            smith_chart_lines.append(line)
        else:
            center_x = r / (1 + r)
            radius = 1 / (1 + r)
            circle = plt.Circle((center_x, 0), radius, fill=False, color=color, linewidth=1)
            ax.add_patch(circle)
            smith_chart_patches.append(circle)

    # Constant reactance arcs
    reactance_values = [0, 0.5, 1, 2]
    x_colors = ['gray', 'cyan', 'magenta', 'brown']
    for i, (x, color) in enumerate(zip(reactance_values, x_colors)):
        if x == 0:
            line, = ax.plot([-1, 1], [0, 0], color=color, linewidth=1, linestyle='--')
            smith_chart_lines.append(line)
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
            line_upper, = ax.plot(x_upper[mask_upper], y_upper[mask_upper], color=color, linewidth=1, linestyle='--')
            line_lower, = ax.plot(x_lower[mask_lower], y_lower[mask_lower], color=color, linewidth=1, linestyle='--')
            smith_chart_lines.extend([line_upper, line_lower])

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
    ax.add_patch(gamma_circle)
    global gamma_patch
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

    # Plot load impedance and matching trajectory
    def plot_impedance_trajectory():
        global gamma_patch
        # Clear only dynamic elements (impedance markers, trajectory lines, and labels)
        for artist in ax.patches[len(smith_chart_patches):]:  # Skip original Smith Chart patches
            artist.remove()
        for line in ax.lines[len(smith_chart_lines):]:  # Skip original Smith Chart lines
            line.remove()
        for text in ax.texts[len(labels):]:  # Skip the chart labels
            text.remove()

        # Re-add or update the reflection circle
        if gamma_patch is None:
            gamma_circle = plt.Circle((0, 0), gamma_value, fill=False, color='black', linestyle='dotted', linewidth=1.5)
            ax.add_patch(gamma_circle)
            gamma_patch = gamma_circle
        gamma_patch.set_radius(gamma_value)
        gamma_patch.set_visible(show_circle)

        if impedance_points:
            # Plot each point and connect them with lines
            for i, Z in enumerate(impedance_points):
                gamma = impedance_to_gamma(Z)
                gamma_x, gamma_y = gamma.real, gamma.imag
                # Plot point
                color = 'blue' if i == 0 else 'green'  # Blue for initial load, green for matching points
                ax.plot(gamma_x, gamma_y, 'o', color=color, markersize=8)
                # Add impedance label
                R = Z.real
                X = Z.imag
                if abs(X) < 0.1:
                    impedance_str = f'Z{i} = {R:.1f} Ω'
                else:
                    sign = '+' if X >= 0 else '-'
                    impedance_str = f'Z{i} = {R:.1f} {sign} j{abs(X):.1f} Ω'
                offset = 0.1
                ha = 'left' if gamma_x < 0 else 'right'
                va = 'bottom' if gamma_y < 0 else 'top'
                text_x = gamma_x + offset if gamma_x < 0 else gamma_x - offset
                text_y = gamma_y + offset if gamma_y < 0 else gamma_y - offset
                ax.text(text_x, text_y, impedance_str, fontsize=10, ha=ha, va=va, 
                        color='black', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
                # Connect points with lines
                if i > 0:
                    prev_gamma = impedance_to_gamma(impedance_points[i-1])
                    ax.plot([prev_gamma.real, gamma_x], [prev_gamma.imag, gamma_y], 'g-', linewidth=1)

        fig.canvas.draw_idle()

    # Store plot_impedance_trajectory for access in other functions
    draw_smith_chart.plot_impedance_trajectory = plot_impedance_trajectory

    # Show the Matplotlib figure
    plt.show()

# Create Tkinter window for controls
root = tk.Tk()
root.title("Return Loss and Impedance Matching Controls")
root.geometry("650x250")  # Adjusted height and width for new controls

# Frame for controls
control_frame = tk.Frame(root)
control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

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
                        command=on_gamma_slider_change, length=150)
gamma_slider.set(gamma_value)
gamma_slider.pack(side=tk.TOP, pady=2)

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
                     command=on_db_slider_change, length=150)
db_slider.set(db_value)
db_slider.pack(side=tk.TOP, pady=2)

# Show |Γ| Circle checkbox
show_var = tk.BooleanVar(value=show_circle)
tk.Checkbutton(control_frame, text="Show |Γ| Circle", variable=show_var).pack(side=tk.LEFT, padx=5)

def update_show_circle():
    global show_circle
    show_circle = show_var.get()
    update_circle()

show_var.trace('w', lambda *args: update_show_circle())

# Load impedance input and matching controls
matching_frame = tk.Frame(root)
matching_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

# Load impedance input
load_frame = tk.Frame(matching_frame)
load_frame.pack(side=tk.LEFT, padx=5)

tk.Label(load_frame, text="Load Z (R + jX):").pack(side=tk.LEFT)
load_r_entry = tk.Entry(load_frame, width=5)
load_r_entry.insert(0, "75")
load_r_entry.pack(side=tk.LEFT, padx=2)
tk.Label(load_frame, text="+ j").pack(side=tk.LEFT)
load_x_entry = tk.Entry(load_frame, width=5)
load_x_entry.insert(0, "25")
load_x_entry.pack(side=tk.LEFT, padx=2)

def set_load():
    global load_impedance, current_impedance, impedance_points
    try:
        R = float(load_r_entry.get())
        X = float(load_x_entry.get())
        if R < 0:
            raise ValueError("Resistance must be non-negative")
        load_impedance = complex(R, X)
        current_impedance = load_impedance
        impedance_points = [load_impedance]  # Reset trajectory with initial load
        draw_smith_chart.plot_impedance_trajectory()
    except ValueError:
        load_r_entry.delete(0, tk.END)
        load_r_entry.insert(0, "75")
        load_x_entry.delete(0, tk.END)
        load_x_entry.insert(0, "25")

tk.Button(load_frame, text="Set Load", command=set_load).pack(side=tk.LEFT, padx=5)

# Matching component controls
component_frame = tk.Frame(matching_frame)
component_frame.pack(side=tk.LEFT, padx=5)

tk.Label(component_frame, text="Matching Component:").pack(side=tk.LEFT)
component_type = ttk.Combobox(component_frame, values=["Series Inductor", "Series Capacitor", "Shunt Inductor", "Shunt Capacitor"], width=15)
component_type.set("Series Inductor")
component_type.pack(side=tk.LEFT, padx=2)

# Slider for component value
def update_component_value(value):
    global component_value
    component_value = float(value)

component_value = 1.0  # Initial value in nH/pF
component_value_slider = tk.Scale(component_frame, from_=0.1, to=100.0, resolution=0.1, orient=tk.HORIZONTAL,
                                  command=update_component_value, length=100, label="Value (nH/pF)")
component_value_slider.set(component_value)
component_value_slider.pack(side=tk.LEFT, padx=2)

# Slider for frequency
def update_frequency(value):
    global frequency
    frequency = float(value) * 1e6  # Convert MHz to Hz

frequency_value = 1000.0  # Initial value in MHz (1 GHz)
frequency_slider = tk.Scale(component_frame, from_=100.0, to=10000.0, resolution=10.0, orient=tk.HORIZONTAL,
                            command=update_frequency, length=100, label="Freq (MHz)")
frequency_slider.set(frequency_value)
frequency_slider.pack(side=tk.LEFT, padx=2)

def add_component():
    global current_impedance, impedance_points
    if current_impedance is None:
        set_load()  # Ensure a load is set
    try:
        component = component_type.get()
        # Calculate reactance using current slider values
        if "Inductor" in component:
            L = component_value * 1e-9  # Convert nH to H
            reactance = 2 * np.pi * frequency * L
        else:  # Capacitor
            C = component_value * 1e-12  # Convert pF to F
            reactance = -1 / (2 * np.pi * frequency * C) if C != 0 else 0
        # Add component
        if "Series" in component:
            new_impedance = add_series_component(current_impedance, reactance)
        else:  # Shunt
            new_impedance = add_shunt_component(current_impedance, reactance)
        current_impedance = new_impedance
        impedance_points.append(current_impedance)
        draw_smith_chart.plot_impedance_trajectory()
    except ValueError:
        pass  # Slider values should always be valid

tk.Button(component_frame, text="Add Component", command=add_component).pack(side=tk.LEFT, padx=5)

# Reset button
def reset_matching():
    global load_impedance, current_impedance, impedance_points
    load_impedance = None
    current_impedance = None
    impedance_points = []
    draw_smith_chart.plot_impedance_trajectory()

tk.Button(matching_frame, text="Reset Matching", command=reset_matching).pack(side=tk.LEFT, padx=5)

# Draw the Smith Chart
draw_smith_chart()

# Start the Tkinter event loop
root.mainloop()

if __name__ == "__main__":
    pass
