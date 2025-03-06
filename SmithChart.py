import matplotlib.pyplot as plt
import numpy as np

def draw_smith_chart(Z0=50):
    # Create a figure and axis with equal aspect ratio
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')

    # Set chart limits and remove axes for a clean look
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis('off')

    # Draw the outer boundary (r = 0 circle, |Γ| = 1)
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

    # --- Label Positions Defined Here ---
    # Format: (text, x, y, color, fontsize, ha, va, rotation)
    labels = [
        # Resistance labels (left side of circles)
        ('0 Ω', -1.05, 0.0, 'blue', 9, 'right', 'center', 0),
        ('25 Ω', -0.20, 0.05, 'green', 9, 'right', 'center', 0),
        ('50 Ω', 0.15, 0.05, 'red', 9, 'right', 'center', 0),
        ('100 Ω', 0.50, 0.05, 'purple', 9, 'right', 'center', 0),
        ('250 Ω', 0.90, 0.10, 'orange', 9, 'right', 'center', 0),
        # Reactance labels (angled along arcs)
        ('j0 Ω', -0.75, 0.025, 'gray', 9, 'left', 'bottom', 0),
        ('j25 Ω', -0.52, 0.65, 'cyan', 9, 'center', 'center', -45),    # Approx angle
        ('-j25 Ω', -0.52, -0.65, 'cyan', 9, 'center', 'center', 45),
        ('j50 Ω', -0.01, 0.75, 'magenta', 9, 'center', 'center', -70),
        ('-j50 Ω', -0.01, -0.75, 'magenta', 9, 'center', 'center', 70),
        ('j100 Ω', 0.45, 0.402, 'brown', 9, 'center', 'center', -85),
        ('-j100 Ω', 0.45, -0.402, 'brown', 9, 'center', 'center', 85),
    ]

    # Plot all labels
    for text, x, y, color, fontsize, ha, va, rotation in labels:
        ax.text(x, y, text, color=color, fontsize=fontsize, ha=ha, va=va, 
                rotation=rotation, rotation_mode='anchor')

    ax.set_title(f"Smith Chart (Z₀ = {Z0} Ω) with Constant Resistance and Reactance", pad=20)
    plt.show()

if __name__ == "__main__":
    draw_smith_chart(Z0=50)