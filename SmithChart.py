import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import CheckButtons, TextBox

def draw_smith_chart(Z0=50):
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

    # Dynamic impedance display
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
    gamma_circle = plt.Circle((0, 0), 0.5, fill=False, color='black', linestyle='dotted', linewidth=1.5)
    gamma_patch = ax.add_patch(gamma_circle)
    gamma_patch.set_visible(False)

    # "Return Loss" section with improved design
    return_loss_ax = fig.add_axes([0.03, 0.15, 0.20, 0.30])  # Increased width to 0.18, height to 0.30
    return_loss_ax.set_facecolor('#E6F0FA')  # Soft pastel blue
    return_loss_ax.spines['top'].set_visible(True)
    return_loss_ax.spines['bottom'].set_visible(True)
    return_loss_ax.spines['left'].set_visible(True)
    return_loss_ax.spines['right'].set_visible(True)
    return_loss_ax.spines['top'].set_color('#4682B4')  # Steel blue border
    return_loss_ax.spines['bottom'].set_color('#4682B4')
    return_loss_ax.spines['left'].set_color('#4682B4')
    return_loss_ax.spines['right'].set_color('#4682B4')
    return_loss_ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    # Title for the section
    return_loss_ax.text(0.5, 0.85, 'Return Loss', fontsize=12, ha='center', va='top', 
                        transform=return_loss_ax.transAxes, weight='bold', color='#333333')

    # Checkbox for reflection coefficient circle
    rax = plt.axes([0.06, 0.20, 0.10, 0.04])  # Shifted right to 0.06, reduced width to 0.10
    check = CheckButtons(rax, ['Show |Γ| Circle'], [False])
    check.labels[0].set_fontsize(10)
    check.labels[0].set_color('#333333')

    def toggle_circle(label):
        gamma_patch.set_visible(check.get_status()[0])
        fig.canvas.draw_idle()

    check.on_clicked(toggle_circle)

    # Text boxes for |Γ| and dB
    ax_gamma = plt.axes([0.06, 0.34, 0.10, 0.04])  # Shifted right to 0.06, lowered to 0.34
    ax_db = plt.axes([0.06, 0.28, 0.10, 0.04])     # Shifted right to 0.06, lowered to 0.28
    text_gamma = TextBox(ax_gamma, '|Γ| ', initial='0.5', label_pad=0.01, textalignment='center')
    text_db = TextBox(ax_db, 'dB ', initial='-6.0', label_pad=0.01, textalignment='center')
    text_gamma.text_disp.set_fontsize(11)
    text_db.text_disp.set_fontsize(11)
    text_gamma.label.set_fontsize(11)
    text_db.label.set_fontsize(11)
    text_gamma.label.set_color('#333333')
    text_db.label.set_color('#333333')
    text_gamma.text_disp.set_color('#333333')
    text_db.text_disp.set_color('#333333')

    def update_gamma(text):
        try:
            gamma = float(text)
            if 0 <= gamma <= 1:
                db = 20 * np.log10(gamma)
                text_db.set_val(f'{db:.1f}')
                gamma_patch.set_radius(gamma)
                if check.get_status()[0]:
                    fig.canvas.draw_idle()
            else:
                text_gamma.set_val('0.5')
                update_db('-6.0')
        except ValueError:
            text_gamma.set_val('0.5')
            update_db('-6.0')

    def update_db(text):
        try:
            db = float(text)
            if db <= 0:
                gamma = 10**(db / 20)
                text_gamma.set_val(f'{gamma:.3f}')
                gamma_patch.set_radius(gamma)
                if check.get_status()[0]:
                    fig.canvas.draw_idle()
            else:
                text_db.set_val('-6.0')
                update_gamma('0.5')
        except ValueError:
            text_db.set_val('-6.0')
            update_gamma('0.5')

    text_gamma.on_submit(update_gamma)
    text_db.on_submit(update_db)

    plt.show()

if __name__ == "__main__":
    draw_smith_chart(Z0=50)
