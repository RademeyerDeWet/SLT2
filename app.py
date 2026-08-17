import os
import subprocess
import sys

import streamlit as st

IMAGE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

def ensure_dependencies():
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        import numpy as np
        from scipy.integrate import cumulative_trapezoid
        return plt, np, Axes3D
    except ModuleNotFoundError as exc:
        requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
        if os.path.exists(requirements_file):
            with st.spinner("Installing missing Python packages..."):
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
                except subprocess.CalledProcessError:
                    st.error(f"Could not install the missing dependency '{exc.name}'. Run 'pip install -r requirements.txt' manually.")
                    st.stop()
        else:
            st.error(f"Missing dependency: {exc.name}. Install the project requirements with 'pip install -r requirements.txt'.")
            st.stop()

        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            import numpy as np
            from scipy.integrate import cumulative_trapezoid
            return plt, np, Axes3D
        except ModuleNotFoundError as exc:
            st.error(f"Missing dependency: {exc.name}. Please restart the app after installation completes.")
            st.stop()


plt, np, Axes3D = ensure_dependencies()

from src.bending_moment_calc import bending_moment
from src.reaction_calc import calculate_reactions
from src.shear_force_calc import shear_force
from src.Deflection import beam_deflection


st.sidebar.title("Options")
option = st.sidebar.radio("Select", ["Axial", "Torsional", "Bending", "Complex"])

if option == "Axial":

    st.header("Axial Deflection Visualization")

    # Material properties
    st.subheader("Material Properties")
    E = st.number_input("Young's Modulus E (Pa)", value=2.1e11, step=1e10, format="%.1e")
    nu = st.number_input("Poisson's Ratio ν", value=0.3, step=0.01, format="%.2f")
    yield_strength = st.number_input("Yield Strength (Pa)", value=250e6, step=1e7, format="%.1e")

    # Geometry and load
    st.subheader("Geometry and Load")
    L = st.number_input("Beam Length L (m)", min_value=0.1, value=2.0, step=0.1)
    A = st.number_input("Cross-sectional Area A (m²)", min_value=1e-6, value=1e-3, step=1e-4, format="%.6f")
    P = st.number_input("Axial Load P (N)", value=1e4, step=1e3, format="%.1f")

    # Calculations
    stress = P / A
    strain = stress / E
    delta_L = (P * L) / (A * E)
    lateral_strain = -nu * strain

    st.subheader("Results")
    st.write(f"Axial Stress: {stress:.2e} Pa")
    st.write(f"Axial Strain: {strain:.2e}")
    st.write(f"Axial Deflection ΔL: {delta_L:.6f} m")
    st.write(f"Lateral Strain (due to ν): {lateral_strain:.2e}")

    # Yield check
    if stress > yield_strength:
        st.error("⚠️ Stress exceeds yield strength! Material will yield.")
    else:
        st.success("Stress is below yield strength. Material remains elastic.")

       # --- Visualization 1: Rectangle deformation with arrows ---
    fig1, ax1 = plt.subplots(figsize=(8, 3))

    # Original dimensions
    L0 = 4.0   # base drawn length for visualization
    w0, h0 = 1.0, 0.5

    # Apply axial strain (length change) and lateral strain (width/height change)
    L_vis = L0 * (1 + strain)          # elongation in length
    w = w0 * (1 + lateral_strain)      # contraction in width
    h = h0 * (1 + lateral_strain)      # contraction in height

    # Draw rectangle centered at origin
    rect = plt.Rectangle((-L_vis/2, -h/2), L_vis, h, fill=False, color='blue', linewidth=2)
    ax1.add_patch(rect)

    # Add arrows showing axial load direction
    arrow_length = 0.5
    ax1.arrow(-L_vis/2, 0, -arrow_length, 0, head_width=0.1, head_length=0.1, fc='red', ec='red')
    ax1.arrow(L_vis/2, 0, arrow_length, 0, head_width=0.1, head_length=0.1, fc='red', ec='red')

    ax1.set_xlim(-L0*1.5, L0*1.5)
    ax1.set_ylim(-1, 1)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.set_title("Axial Load Visualization")
    st.pyplot(fig1)

    # --- Visualization 2: Deflection curve along the bar ---
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    x_coords = np.linspace(0, L, 100)
    deflection_curve = (delta_L / L) * x_coords  # linear elongation along the bar
    ax2.plot(x_coords, deflection_curve, 'g-', linewidth=2, label='Axial Deflection')
    ax2.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
    ax2.plot(L, delta_L, 'ro', label=f'Max ΔL = {delta_L:.6f} m')  # marker at free end
    ax2.set_xlabel('Position along bar (m)', fontsize=12)
    ax2.set_ylabel('Deflection (m)', fontsize=12)
    ax2.set_title('Axial Deflection Curve', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    st.pyplot(fig2)

    
    # Quiz section
    st.subheader("Quiz")
    quiz_option = st.radio("What will happen if the strain value is increased?", 
                           ["A: The rectangle will contract horizontally.", 
                            "B: The rectangle will expand horizontally.", 
                            "C: Nothing will happen."])
    
    if st.button("Submit Answer"):
        if "B:" in quiz_option:
            st.success("Correct! The rectangle expands horizontally.")
        else:
            st.error("Incorrect. The correct answer is B: The rectangle will expand horizontally.")
    
elif option == "Torsional":
    st.header("Torsional Strain Visualization")

    # Material properties
    st.subheader("Material Properties")
    G = st.number_input("Shear Modulus G (Pa)", value=8e10, step=1e9, format="%.1e")
    J = st.number_input("Polar Moment of Inertia J (m⁴)", value=1e-6, step=1e-7, format="%.1e")
    yield_shear = st.number_input("Yield Shear Strength (Pa)", value=250e6, step=1e7, format="%.1e")

    # Geometry and load
    st.subheader("Geometry and Load")
    L = st.number_input("Beam Length L (m)", min_value=0.1, value=4.0, step=0.1)
    w = st.number_input("Beam Width (m)", min_value=0.1, value=1.0, step=0.1)
    h = st.number_input("Beam Height (m)", min_value=0.1, value=0.5, step=0.1)
    T = st.number_input("Applied Torque T (Nm)", value=1000.0, step=100.0)

    # Engineering calculations
    theta = (T * L) / (G * J)  # angle of twist (radians)
    tau_max = (T * (w/2)) / J  # shear stress at surface (approx for rectangular section)

    st.subheader("Results")
    st.write(f"Angle of Twist: {np.degrees(theta):.2f}°")
    st.write(f"Max Shear Stress: {tau_max:.2e} Pa")

    if tau_max > yield_shear:
        st.error("⚠️ Shear stress exceeds yield strength! Material will yield.")
    else:
        st.success("Shear stress is below yield strength. Material remains elastic.")

    # --- Visualization: Twisting bar ---
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    num_sections = 20
    z = np.linspace(0, L, num_sections)

    for i, zi in enumerate(z):
        angle = (zi / L) * theta  # twist angle at section

        verts = np.array([[-w/2, -h/2, zi],
                          [w/2, -h/2, zi],
                          [w/2, h/2, zi],
                          [-w/2, h/2, zi]])

        rot_matrix = np.array([[np.cos(angle), -np.sin(angle), 0],
                               [np.sin(angle),  np.cos(angle), 0],
                               [0,              0,             1]])

        verts_rot = verts @ rot_matrix.T
        ax.plot(verts_rot[:, 0], verts_rot[:, 1], verts_rot[:, 2], 'b-')

        if i < len(z) - 1:
            next_zi = z[i+1]
            next_angle = (next_zi / L) * theta
            next_rot_matrix = np.array([[np.cos(next_angle), -np.sin(next_angle), 0],
                                        [np.sin(next_angle),  np.cos(next_angle), 0],
                                        [0,                  0,                 1]])
            next_verts = np.array([[-w/2, -h/2, next_zi],
                                   [w/2, -h/2, next_zi],
                                   [w/2, h/2, next_zi],
                                   [-w/2, h/2, next_zi]])
            next_verts_rot = next_verts @ next_rot_matrix.T

            for j in range(4):
                ax.plot([verts_rot[j, 0], next_verts_rot[j, 0]],
                        [verts_rot[j, 1], next_verts_rot[j, 1]],
                        [verts_rot[j, 2], next_verts_rot[j, 2]], 'b-')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_box_aspect([w, h, L])
    ax.set_title("Twisting Bar Visualization")
    st.pyplot(fig)

    # --- Graph 1: Angle of twist vs torque ---
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    torques = np.linspace(0, T*1.5, 50)
    angles = (torques * L) / (G * J)
    ax1.plot(torques, np.degrees(angles), 'g-', linewidth=2, label='Angle of Twist (deg)')
    ax1.set_xlabel('Applied Torque (Nm)', fontsize=12)
    ax1.set_ylabel('Angle of Twist (deg)', fontsize=12)
    ax1.set_title('Torque vs Angle of Twist', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    st.pyplot(fig1)

    # --- Graph 2: Shear stress vs torque ---
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    stresses = (torques * (w/2)) / J
    ax2.plot(torques, stresses, 'r-', linewidth=2, label='Max Shear Stress (Pa)')
    ax2.axhline(y=yield_shear, color='k', linestyle='--', label='Yield Shear Strength')
    ax2.set_xlabel('Applied Torque (Nm)', fontsize=12)
    ax2.set_ylabel('Shear Stress (Pa)', fontsize=12)
    ax2.set_title('Torque vs Shear Stress', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    st.pyplot(fig2)

    
elif option == "Bending":
    st.header("Bending Analysis")
    
    # Beam parameters
    beam_length = st.number_input("Beam Length (m)", min_value=0.1, value=4.0, step=0.5)
    resolution = 100
    
    # Support configuration
    st.subheader("Supports")

    col1, col2 = st.columns(2)
    with col1:
     sup1_pos = st.number_input("Support A Position (m)", min_value=0.0, max_value=beam_length, value=0.0, step=0.1)
     sup1_type = st.selectbox("Support A Type", ["Pin", "Roller", "Fixed"], key="sup1_type")
    with col2:
     sup2_pos = st.number_input("Support B Position (m)", min_value=0.0, max_value=beam_length, value=beam_length, step=0.1)
     sup2_type = st.selectbox("Support B Type", ["None", "Pin", "Roller", "Fixed"], key="sup2_type")

    # Build supports list
    supports = []
    if sup1_type != "None":
     supports.append((sup1_type, sup1_pos))
    if sup2_type != "None":
     supports.append((sup2_type, sup2_pos))


    
    # Loads
    st.subheader("Loads")
    
    point_loads = []
    distributed_loads = []
    external_moments = []


    num_point_loads = st.number_input("Number of Point Loads", min_value=0, value=1, step=1)
    point_loads = []
    if num_point_loads > 0:
        st.caption("⬇ Enter a **negative** magnitude for downward forces (positive = upward).")
    for i in range(num_point_loads):
     pos = st.number_input(f"Point Load {i+1} Position (m)", min_value=0.0, max_value=beam_length, value=beam_length/2, step=0.1)
     mag = st.number_input(f"Point Load {i+1} Magnitude (kN)", value=-10.0, step=1.0,
                            help="Negative = downward, Positive = upward")
     point_loads.append((pos, mag))
     
    num_moments = st.number_input("Number of External Moments", min_value=0, value=0, step=1, key="num_moments")
    external_moments = []
    for i in range(num_moments):
        pos = st.number_input(f"Moment {i+1} Position (m)", 
                          min_value=0.0, max_value=beam_length, 
                          value=beam_length/2, step=0.1, 
                          key=f"moment_pos_{i}")
        mag = st.number_input(f"Moment {i+1} Magnitude (kNm)", 
                          value=5.0, step=1.0, 
                       key=f"moment_mag_{i}")
        external_moments.append((pos, mag))

    # Distributed Loads
    st.subheader("Distributed Loads")
    num_dist_loads = st.number_input("Number of Distributed Loads", min_value=0, value=0, step=1, key="num_dist_loads")
    distributed_loads = []

    if num_dist_loads > 0:
        st.caption("⬇ Enter a **negative** magnitude for downward forces (positive = upward).")
    for i in range(num_dist_loads):
        start = st.number_input(f"Load {i+1} Start (m)", min_value=0.0, max_value=beam_length,
                            value=0.0, step=0.1, key=f"dist_start_{i}")
        end = st.number_input(f"Load {i+1} End (m)", min_value=0.0, max_value=beam_length,
                          value=beam_length, step=0.1, key=f"dist_end_{i}")
        start_mag = st.number_input(f"Load {i+1} Start Magnitude (kN/m)", value=-5.0, step=1.0,
                                key=f"dist_start_mag_{i}", help="Negative = downward, Positive = upward")
        end_mag = st.number_input(f"Load {i+1} End Magnitude (kN/m)", value=-5.0, step=1.0,
                              key=f"dist_end_mag_{i}", help="Negative = downward, Positive = upward")
        distributed_loads.append((start, end, start_mag, end_mag))



    # Beam Visualization
    st.subheader("Beam Visualization")
    fig_beam, ax_beam = plt.subplots(figsize=(12, 4))

    # Draw beam as horizontal line
    ax_beam.plot([0, beam_length], [0, 0], 'k-', linewidth=4, label='Beam')

    # Add supports
    for sup_type, sup_pos in supports:
     if sup_type == "Pin":
        ax_beam.scatter(sup_pos, -0.1, s=300, marker='^', color='blue',
                        edgecolors='black', linewidth=2, label='Hinge Support')
     elif sup_type == "Roller":
        ax_beam.scatter(sup_pos, -0.1, s=300, marker='o', color='green',
                        edgecolors='black', linewidth=2, label='Roller Support')
     elif sup_type == "Fixed":
        # Draw vertical line
        ax_beam.plot([sup_pos, sup_pos], [-0.2, 0.2], 'k-', linewidth=4)
        # Add diagonal hatch lines
        for y in np.linspace(-0.2, 0.2, 6):
            ax_beam.plot([sup_pos-0.1, sup_pos], [y-0.1, y], 'k-', linewidth=2)
        # Add legend entry
        ax_beam.plot([], [], 'k-', linewidth=4, label='Fixed Support')


    # Point loads
    if point_loads and len(point_loads) > 0:
     for pos, mag in point_loads:
        if mag >= 0:  # upward - draw below the beam, pointing up into it
            ax_beam.arrow(pos, -0.5, 0, 0.4,
                          head_width=0.1, head_length=0.1,
                          fc='red', ec='red', linewidth=2)
        else:  # downward - draw above the beam, pointing down into it
            ax_beam.arrow(pos, 0.5, 0, -0.4,
                          head_width=0.1, head_length=0.1,
                          fc='red', ec='red', linewidth=2)
    # External moments
    import matplotlib.patches as patches
    from matplotlib.patches import FancyArrowPatch

    if external_moments and len(external_moments) > 0:
     for pos, mag in external_moments:
        radius = 0.4
        theta1, theta2 = (90, 10) if mag > 0 else (160, 70)
        arc = patches.Arc((pos, 0), radius, radius, angle=0,
                          theta1=theta1, theta2=theta2,
                          color='purple', linewidth=2)
        ax_beam.add_patch(arc)

        if mag > 0:  # clockwise
            arrow = FancyArrowPatch((pos+radius/2, 0),
                                    (pos+radius/2-0.05, 0.1+radius/2),
                                    arrowstyle='->,head_length=8,head_width=6',
                                    color='purple', linewidth=2)
        else:        # anticlockwise
            arrow = FancyArrowPatch((pos-radius/2, 0),
                                    (pos-radius/2+0.05, 0.1+radius/2),
                                    arrowstyle='->,head_length=8,head_width=6',
                                    color='purple', linewidth=2)
        ax_beam.add_patch(arrow)

    # Distributed loads
    if distributed_loads and len(distributed_loads) > 0:
     for start, end, start_mag, end_mag in distributed_loads:
        # upward loads are drawn below the beam, pointing up into it
        upward = start_mag >= 0 and end_mag >= 0
        sign = -1 if upward else 1
        base, tip = 0.4 * sign, 0.6 * sign

        if start_mag == end_mag:
            # Rectangular load
            rect = plt.Rectangle((start, min(base, tip)), end - start, 0.2,
                                 color='orange', alpha=0.3)
            ax_beam.add_patch(rect)
            for x in np.linspace(start, end, 5):
                ax_beam.arrow(x, tip, 0, base - tip,
                              head_width=0.05, head_length=0.05,
                              fc='orange', ec='orange')
        else:
            # Triangular load, flip depending on which side is larger
            if abs(start_mag) > abs(end_mag):
                tri = plt.Polygon([[start, tip], [end, base], [start, base]],
                                  color='orange', alpha=0.3)
            else:
                tri = plt.Polygon([[start, base], [end, tip], [end, base]],
                                  color='orange', alpha=0.3)
            ax_beam.add_patch(tri)
            for x in np.linspace(start, end, 5):
                ax_beam.arrow(x, tip, 0, base - tip,
                              head_width=0.05, head_length=0.05,
                              fc='orange', ec='orange')

    # Final formatting
    ax_beam.set_xlim(-0.5, beam_length + 0.5)
    ax_beam.set_ylim(-1, 1)
    ax_beam.axis('off')
    ax_beam.legend(loc='upper right')
    st.pyplot(fig_beam)


    
    

    #material properties
    st.subheader("Material Properties")
    E_GPa = st.number_input("Young's Modulus E (GPa)", value=210.0, step=1.0, format="%.2f")
    I_mm4 = st.number_input("Second Moment of Area I (mm⁴)", value=8.33e6, step=1e4, format="%.2f")
    E = E_GPa * 1e9      # convert GPa -> Pa
    I = I_mm4 * 1e-12    # convert mm^4 -> m^4
    
    # Calculate reactions
    st.subheader("Results")
    reactions = calculate_reactions(supports, point_loads, distributed_loads, external_moments, beam_length)
    if reactions and reactions != False:
        st.markdown("**Support Reactions**")
        is_single_fixed = len(supports) == 1 and supports[0][0] == "Fixed"
        if is_single_fixed:
            fixed_pos, force = reactions[0]
            _, moment = reactions[1]
            c1, c2 = st.columns(2)
            c1.metric(f"Fixed Support — Reaction Force (x = {fixed_pos:.2f} m)",
                      f"{force:.3f} kN",
                      "upward ↑" if force >= 0 else "downward ↓")
            c2.metric(f"Fixed Support — Reaction Moment (x = {fixed_pos:.2f} m)",
                      f"{moment:.3f} kN·m",
                      "clockwise ↻" if moment >= 0 else "anticlockwise ↺")
        else:
            support_labels = ["A", "B"]
            cols = st.columns(len(reactions))
            for col, (pos, force), label in zip(cols, reactions, support_labels):
                sup_type = next((s for s, p in supports if abs(p - pos) < 1e-9), "")
                col.metric(f"Support {label} ({sup_type}) at x = {pos:.2f} m",
                           f"{force:.3f} kN",
                           "upward ↑" if force >= 0 else "downward ↓")

        # Calculate shear force and bending moment
        shear_reactions = [reactions[0]] if any(s == "Fixed" for s, p in supports) else reactions
        x_sf, shear = shear_force(shear_reactions, point_loads, distributed_loads, beam_length, resolution)
        x_bm, bending = bending_moment(supports, reactions, [], point_loads, distributed_loads, external_moments, beam_length, resolution)

        
        # Plot diagrams
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        
        # Shear Force Diagram
        axes[0].plot(x_sf, shear, 'b-', linewidth=2, label='Shear Force')
        axes[0].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        axes[0].fill_between(x_sf, 0, shear, alpha=0.3)
        axes[0].set_ylabel('Shear Force (N)', fontsize=12)
        axes[0].set_title('Shear Force Diagram', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()
        
        # Bending Moment Diagram
        axes[1].plot(x_bm, bending, 'r-', linewidth=2, label='Bending Moment')
        axes[1].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        axes[1].fill_between(x_bm, 0, bending, alpha=0.3, color='red')
        axes[1].set_xlabel('Position along beam (m)', fontsize=12)
        axes[1].set_ylabel('Bending Moment (N·m)', fontsize=12)
        axes[1].set_title('Bending Moment Diagram', fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()
                # Deflection Diagram
        deflection, slope_curve = beam_deflection(x_bm, bending, E, I, supports)

        fig_def, ax_def = plt.subplots(figsize=(12, 4))
        ax_def.plot(x_bm, deflection, 'g-', linewidth=2, label='Deflection')
        ax_def.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        ax_def.set_xlabel('Position along beam (m)', fontsize=12)
        ax_def.set_ylabel('Deflection (m)', fontsize=12)
        ax_def.set_title('Deflection Curve', fontsize=14, fontweight='bold')
        ax_def.grid(True, alpha=0.3)
        ax_def.legend()
       #   NEW (correct — finds largest absolute deflection):
        idx_max = np.argmax(np.abs(deflection))
        max_deflection = deflection[idx_max]
        max_position = x_bm[idx_max]
        direction = "downward" if max_deflection < 0 else "upward"
        st.write(
            f"Maximum Deflection: {abs(max_deflection):.6e} m "
            f"({direction}) at x = {max_position:.4f} m"
        )
        
        st.pyplot(fig_def)
        # Slope Diagram
        fig_slope, ax_slope = plt.subplots(figsize=(12, 4))
        ax_slope.plot(x_bm, slope_curve, 'm-', linewidth=2, label='Slope')
        ax_slope.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        ax_slope.fill_between(x_bm, 0, slope_curve, alpha=0.2, color='purple')
        ax_slope.set_xlabel('Position along beam (m)', fontsize=12)
        ax_slope.set_ylabel('Slope (rad)', fontsize=12)
        ax_slope.set_title('Slope Diagram', fontsize=14, fontweight='bold')
        ax_slope.grid(True, alpha=0.3)
        ax_slope.legend()

        idx_max_slope = np.argmax(np.abs(slope_curve))
        max_slope_rad = slope_curve[idx_max_slope]
        max_slope_pos = x_bm[idx_max_slope]
        st.pyplot(fig_slope)
        st.write(
            f"Maximum Slope: {abs(max_slope_rad):.6f} rad "
            f"at x = {max_slope_pos:.4f} m"
        )
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.error("Unable to calculate reactions. Check your support and load configuration.")
     

# =====================================================================
# COMPLEX TAB - Combined loading, strain gauge prediction, Mohr's circles
# =====================================================================
# Drop this in to REPLACE your existing:
#     elif option == "Complex":
#         st.header("Complex")
#         picture = st.camera_input("Take a picture")
#         if picture:
#             st.image(picture)
#
# Assumes plt and np are already available in scope (they are, via your
# ensure_dependencies() call at the top of the file). No new imports needed.
#
# Modelling notes / assumptions baked into this code:
#   - Effective section properties: A_e = 0.6*b*h, I_e = 0.4*(b*h^3/12)
#     (per the tutorial's extruded-strut correction factors)
#   - Self-weight of strut C only counts the FREE length k (the portion
#     that actually bends), not the full strut length Lc
#   - The b/2 term in scenarios 2 & 3 accounts for the right-angle
#     bracket's offset between strut C and strut D
#   - Torsional shear stress uses tau_max = 4.81*T/a^3 (solid square
#     section approximation, a = b) throughout - a simplification you
#     confirmed is fine
#   - Gauge reading is epsilon_x for scenarios 1-3, epsilon_y for
#     scenario 4 (that gauge is bonded transverse, so it picks up the
#     Poisson strain instead of the direct bending strain)
#   - Scenario 3's "combined stress at R" (base of strut A) only sums
#     the axial term and the M3x bending term, matching your reference
#     worksheet. M3y is still computed and shown, but not added in -
#     double check whether your specific point needs it included too.
# =====================================================================

# ---------------------------------------------------------------
# Helper functions - define once, used by every scenario below
# ---------------------------------------------------------------

def macaulay(x, a, n=1):
    """Singularity bracket <x-a>^n : 0 if x <= a, else (x-a)^n."""
    return (x - a) ** n if x > a else 0.0


def moment_at(x_eval, R0, M0, point_loads):
    """
    Internal bending moment (tutorial's 'My' convention) at x_eval,
    measured from a cantilever's fixed support at x=0.

    R0, M0   : support shear and moment reactions (already computed
               from global equilibrium of ALL point_loads)
    point_loads : list of (position_m, force_N) tuples, downward positive

    Handles any load position automatically - if a load sits behind
    x_eval (closer to the support), it's picked up by the Macaulay term.
    """
    My = -M0 + R0 * x_eval
    for pos, force in point_loads:
        My -= force * macaulay(x_eval, pos, 1)
    return My


def effective_properties(b_mm, h_mm):
    """Converts nominal b, h (mm) to effective A, I (m^2, m^4) for the
    extruded struts: A_e = 0.6*A_solid, I_e = 0.4*I_solid."""
    b, h = b_mm / 1000.0, h_mm / 1000.0
    A_solid = b * h
    I_solid = b * h ** 3 / 12
    return 0.6 * A_solid, 0.4 * I_solid


def plot_stress_element(sigma_x, sigma_y, tau_xy):
    """Small square stress element with labeled arrows."""
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.add_patch(plt.Rectangle((-1, -1), 2, 2, fill=False, edgecolor='black', linewidth=2))
    arrow_kw = dict(head_width=0.1, head_length=0.1, fc='red', ec='red', linewidth=1.5)

    sx_dir = 1 if sigma_x >= 0 else -1
    ax.arrow(1, 0, 0.4 * sx_dir, 0, **arrow_kw)
    ax.arrow(-1, 0, -0.4 * sx_dir, 0, **arrow_kw)
    ax.text(1.7 * sx_dir, 0, f"σx={sigma_x/1e6:.2f} MPa", fontsize=8, ha='center')

    if abs(sigma_y) > 1e-9:
        sy_dir = 1 if sigma_y >= 0 else -1
        ax.arrow(0, 1, 0, 0.4 * sy_dir, **arrow_kw)
        ax.arrow(0, -1, 0, -0.4 * sy_dir, **arrow_kw)
        ax.text(0, 1.7 * sy_dir, f"σy={sigma_y/1e6:.2f} MPa", fontsize=8, ha='center')

    if abs(tau_xy) > 1e-9:
        s_kw = dict(head_width=0.08, head_length=0.08, fc='blue', ec='blue', linewidth=1.5)
        ax.arrow(1, -0.3, 0, 0.6, **s_kw)
        ax.arrow(-1, 0.3, 0, -0.6, **s_kw)
        ax.arrow(-0.3, 1, 0.6, 0, **s_kw)
        ax.arrow(0.3, -1, -0.6, 0, **s_kw)
        ax.text(1.75, -0.3, f"τxy={tau_xy/1e6:.2f} MPa", fontsize=8, color='blue')

    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(-2.6, 2.6)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Stress Element at Gauge")
    return fig


def plot_mohr_circle(a_x, a_y, a_xy, label="Stress", unit="Pa", scale=1.0):
    """
    Draws a Mohr's circle for a plane stress OR plane strain state.
    For stress: pass (sigma_x, sigma_y, tau_xy) directly, unit="Pa".
    For strain: pass (eps_x, eps_y, gamma_xy/2) - note the /2 - and
        set unit="" (values are typically shown scaled to micro-strain).
    'scale' divides the plotted/reported numbers for display (e.g. 1e6
    to show MPa from Pa, or 1e6 to show micro-strain from strain).

    Shear axis convention: positive shear is plotted DOWNWARD (the
    axis is inverted after plotting), matching the standard Mohr's
    circle construction convention. Under this convention, rotation
    direction read directly off the circle (CA -> CB, etc.) matches
    the physical rotation direction on the element.
    """
    center = (a_x + a_y) / 2
    radius = np.sqrt(((a_x - a_y) / 2) ** 2 + a_xy ** 2)
    a_1 = center + radius
    a_2 = center - radius
    theta_p_deg = 0.5 * np.degrees(np.arctan2(2 * a_xy, a_x - a_y))
    # Max in-plane shear planes are always 45 deg from the principal planes
    theta_s_deg = theta_p_deg - 45.0

    theta = np.radians(45)
    a_45 = center + (a_x - a_y) / 2 * np.cos(2 * theta) + a_xy * np.sin(2 * theta)
    b_45 = -(a_x - a_y) / 2 * np.sin(2 * theta) + a_xy * np.cos(2 * theta)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.add_patch(plt.Circle((center * scale, 0), radius * scale, fill=False, color='blue', linewidth=2))

    ax.plot(a_x * scale, a_xy * scale, 'ro', markersize=8, label="0° (as given)")
    ax.plot(a_y * scale, -a_xy * scale, 'ro', markersize=8, alpha=0.5)
    ax.plot([a_x * scale, a_y * scale], [a_xy * scale, -a_xy * scale], 'r--', linewidth=1)

    ax.plot(a_45 * scale, b_45 * scale, 'gs', markersize=8, label="45°")
    ax.plot(a_1 * scale, 0, 'k^', markersize=8, label=f"Principal 1 = {a_1*scale:.3f}")
    ax.plot(a_2 * scale, 0, 'kv', markersize=8, label=f"Principal 2 = {a_2*scale:.3f}")

    # Max in-plane shear points E (top of circle, +R) and F (bottom, -R)
    ax.plot(center * scale, radius * scale, 'D', color='purple', markersize=7,
            label=f"Max shear E,F = ±{radius*scale:.3f}")
    ax.plot(center * scale, -radius * scale, 'D', color='purple', markersize=7, alpha=0.5)

    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axvline(0, color='gray', linewidth=0.5)
    ax.set_xlabel(f"Normal ({unit})" if unit else "Normal (µε)")
    ax.set_ylabel(f"Shear ({unit})" if unit else "Shear (µε)")
    ax.set_title(f"{label} Mohr's Circle")
    ax.set_aspect('equal')
    ax.invert_yaxis()  # shear axis positive downward, per construction convention
    ax.legend(fontsize=7, loc='best')
    ax.grid(alpha=0.3)

    info = {
        "a_1": a_1, "a_2": a_2, "theta_p_deg": theta_p_deg,
        "a_45": a_45, "b_45": b_45,
        "max_shear": radius, "theta_s_deg": theta_s_deg,
    }
    return fig, info

# ---------------------------------------------------------------
# Main Complex tab
# ---------------------------------------------------------------
if option == "Complex":
    st.header("Combined Loading - Demonstrator Structure")

    # Images folder (keep images inside the project so deployments include them)
    IMAGE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

    from pathlib import Path

    def find_image_file(basename):
        """Return the first matching file in IMAGE_FOLDER for basename (any extension), or None."""
        p = Path(IMAGE_FOLDER)
        if not p.exists():
            return None
        for f in p.glob(f"{basename}.*"):
            return str(f)
        return None

    # Map the human-readable scenario to the image basename you created
    image_map = {
        "Scenario 1: Straight cantilever (strut C-D)": "Case 1",
        "Scenario 2: L-shaped cantilever, eccentric load": "Case 2",
        "Scenario 3: L-shaped cantilever + axial load on strut A": "Case 3",
        "Scenario 4: Base beam (strut B, fixed-fixed)": "Case 4",
    }

    scenario = st.selectbox(
        "Loading Scenario",
        [
            "Scenario 1: Straight cantilever (strut C-D)",
            "Scenario 2: L-shaped cantilever, eccentric load",
            "Scenario 3: L-shaped cantilever + axial load on strut A",
            "Scenario 4: Base beam (strut B, fixed-fixed)",
        ],
    )

    # Show the scenario image if available (works with deployment since images are bundled)
    img_basename = image_map.get(scenario)
    img_path = find_image_file(img_basename) if img_basename else None
    if img_path:
        st.image(img_path, use_container_width=True, caption=scenario)
    else:
        st.info(f"No image found for '{scenario}' in assets/ (looking for '{img_basename}.*')")

    # -----------------------------------------------------------
    # TODO: add your own scenario photo/diagram here, e.g.:
    #   image_paths = {
    #       "Scenario 1: Straight cantilever (strut C-D)": "assets/scenario1.png",
    #       "Scenario 2: L-shaped cantilever, eccentric load": "assets/scenario2.png",
    #       "Scenario 3: L-shaped cantilever + axial load on strut A": "assets/scenario3.png",
    #       "Scenario 4: Base beam (strut B, fixed-fixed)": "assets/scenario4.png",
    #   }
    #   st.image(image_paths[scenario], use_container_width=True)
    # -----------------------------------------------------------

    st.subheader("Material & Section Properties")
    col1, col2, col3 = st.columns(3)
    with col1:
        E = st.number_input("Young's Modulus E (GPa)", value=70.0, step=1.0) * 1e9
        nu = st.number_input("Poisson's ratio", value=0.33, step=0.01, format="%.2f")
    with col2:
        b = st.number_input("Strut width b (mm)", value=30.0, step=1.0)
        h = st.number_input("Strut height h (mm)", value=30.0, step=1.0)
    with col3:
        st.write("")  # spacing
        st.caption("A_e = 0.6·b·h, I_e = 0.4·b·h³/12 (extruded strut correction)")

    G = E / (2 * (1 + nu))
    A_e, I_e = effective_properties(b, h)

    override_I = st.checkbox("Override effective I manually", value=False)
    if override_I:
        I_e = st.number_input(
            "Manual effective second moment of area I_e (m⁴)",
            value=float(I_e),
            format="%.11e",
            help="Enter a known effective second moment of area directly instead of using the default extruded-strut formula.",
            key="complex_manual_I",
        )
        st.caption("Using manually entered I_e for beam/strut calculations.")
    else:
        st.caption("Effective section properties are calculated from b and h using the extruded-strut correction factors.")

    g = 9.81  # m/s^2

    # =============================================================
    # SCENARIO 1
    # =============================================================
    if scenario.startswith("Scenario 1"):
        st.subheader("Scenario 1: Straight Cantilever (Strut C-D)")

        col1, col2 = st.columns(2)
        with col1:
            LD = st.number_input("Strut D length, LD (mm)", value=250.0, key="s1_LD")
            k = st.number_input("Free length of strut C, k (mm)", value=190.0, key="s1_k")
        with col2:
            x_gauge = st.number_input("Gauge position from clamp, x (mm)", value=45.0, key="s1_x")

        with st.expander("Self-weight inputs (optional - set to 0 to ignore)"):
            colA, colB, colC = st.columns(3)
            with colA:
                density_C = st.number_input("Strut C linear density (kg/m)", value=0.9, key="s1_dC")
            with colB:
                density_D = st.number_input("Strut D linear density (kg/m)", value=0.9, key="s1_dD")
            with colC:
                m_conn = st.number_input("Connector mass (kg)", value=0.13, key="s1_mconn")

        st.markdown("**Applied load - movable weight**")
        col3, col4 = st.columns(2)
        with col3:
            mass = st.number_input("Hanging mass (kg)", min_value=0.0, max_value=5.0,
                                    value=1.0, step=0.0001, format="%.4f", key="s1_mass")
        with col4:
            d_load = st.number_input("Load position from clamp, d (mm)", min_value=0.0,
                                      max_value=float(k + LD), value=float(k + LD) * 0.85,
                                      step=0.0001, format="%.4f", key="s1_d")

        Wc_free = density_C * (k / 1000) * g   # self-weight of the FREE k-length only
        WD = density_D * (LD / 1000) * g
        Wcon = m_conn * g
        W = mass * g

        point_loads = [
            (k / 2 / 1000, Wc_free),
            (k / 1000, Wcon),
            ((k + LD / 2) / 1000, WD),
            (d_load / 1000, W),
        ]
        R0 = sum(f for _, f in point_loads)
        M0 = sum(f * p for p, f in point_loads)
        My = moment_at(x_gauge / 1000, R0, M0, point_loads)

        sigma_x = -My * (h / 2000) / I_e
        sigma_y = 0.0
        tau_xy = 0.0

        eps_x = sigma_x / E
        eps_y = -nu * sigma_x / E
        gamma_xy = tau_xy / G

        gauge_reading, gauge_label = eps_x, "εx"

        st.subheader("Reactions & internal forces")
        c1, c2, c3 = st.columns(3)
        c1.metric("Support shear R", f"{R0:.3f} N")
        c2.metric("Support moment M", f"{M0:.4f} N·m")
        c3.metric("Moment at gauge", f"{My:.4f} N·m")

    # =============================================================
    # SCENARIO 2
    # =============================================================
    elif scenario.startswith("Scenario 2"):
        st.subheader("Scenario 2: L-Shaped Cantilever, Eccentric Load")

        col1, col2 = st.columns(2)
        with col1:
            k = st.number_input("Free length of strut C, k (mm)", value=190.0, key="s2_k")
            LD = st.number_input("Strut D length, LD (mm)", value=250.0, key="s2_LD")
        with col2:
            x_gauge = st.number_input("Gauge position from clamp, x (mm)", value=45.0, key="s2_x")

        st.markdown("**Applied load - movable weight, slides along strut D**")
        col3, col4 = st.columns(2)
        with col3:
            mass = st.slider("Hanging mass (kg)", 0.0, 5.0, 1.0, 0.05, key="s2_mass")
        with col4:
            d_D = st.slider("Load position along strut D, from corner (mm)",
                             0.0, float(LD), float(LD) * 0.9, 1.0, key="s2_dD")

        W = mass * g

        # Bending moment only depends on the fixed corner-to-gauge distance -
        # it does NOT change with where along strut D the load sits.
        My = W * ((k - x_gauge + b / 2) / 1000)
        # Torque DOES depend on load position along D.
        Tx = W * ((d_D - b / 2) / 1000)

        sigma_x = My * (h / 2000) / I_e
        sigma_y = 0.0
        a = b / 1000  # simplifying assumption: roughly square section
        tau_xy = 4.81 * Tx / a ** 3

        eps_x = sigma_x / E
        eps_y = -nu * sigma_x / E
        gamma_xy = tau_xy / G

        gauge_reading, gauge_label = eps_x, "εx"

        st.subheader("Internal forces at the gauge")
        c1, c2 = st.columns(2)
        c1.metric("Bending moment My", f"{My:.4f} N·m")
        c2.metric("Torque Tx", f"{Tx:.4f} N·m")

    # =============================================================
    # SCENARIO 3
    # =============================================================
    elif scenario.startswith("Scenario 3"):
        st.subheader("Scenario 3: L-Shaped Cantilever + Axial Load on Strut A")

        col1, col2 = st.columns(2)
        with col1:
            k = st.number_input("Free length of strut C, k (mm)", value=190.0, key="s3_k")
            LD = st.number_input("Strut D length, LD (mm)", value=250.0, key="s3_LD")
        with col2:
            Lc = st.number_input("Strut C total length, Lc (mm)", value=250.0, key="s3_Lc")
            x_gauge = st.number_input("Gauge position from clamp, x (mm)", value=45.0, key="s3_x")

        st.markdown("**Applied loads - movable weight W, plus fixed axial load V**")
        col3, col4, col5 = st.columns(3)
        with col3:
            mass = st.slider("Hanging mass W (kg)", 0.0, 5.0, 1.0, 0.05, key="s3_mass")
        with col4:
            d_D = st.slider("Load position along strut D (mm)", 0.0, float(LD),
                             float(LD) * 0.9, 1.0, key="s3_dD")
        with col5:
            V_mass = st.number_input("Axial load on strut A, V (kg)", value=1.0, key="s3_Vmass")

        W = mass * g
        V = V_mass * g

        # Gauge is still on strut C - identical formula to scenario 2, unaffected by V
        My = W * ((k - x_gauge + b / 2) / 1000)
        Tx = W * ((d_D - b / 2) / 1000)

        sigma_x = My * (h / 2000) / I_e
        sigma_y = 0.0
        a = b / 1000
        tau_xy = 4.81 * Tx / a ** 3

        eps_x = sigma_x / E
        eps_y = -nu * sigma_x / E
        gamma_xy = tau_xy / G

        gauge_reading, gauge_label = eps_x, "εx"

        st.subheader("Gauge on strut C (identical to Scenario 2)")
        c1, c2 = st.columns(2)
        c1.metric("Bending moment My", f"{My:.4f} N·m")
        c2.metric("Torque Tx", f"{Tx:.4f} N·m")

        st.markdown("---")
        st.markdown("**Supplementary check - combined stress at the base of strut A (point R)**  \n"
                     "Not a physical gauge reading, just a design check.")
        N3 = V + W
        M3x = W * ((LD - b / 2) / 1000)
        M3y = W * ((Lc + b) / 1000)

        sigma_N = -N3 / A_e
        sigma_M = -M3x * (b / 2000) / I_e
        sigma_R = sigma_N + sigma_M   # M3y NOT included here - see header note

        c3, c4, c5 = st.columns(3)
        c3.metric("N3 (axial)", f"{N3:.3f} N")
        c4.metric("M3x", f"{M3x:.4f} N·m")
        c5.metric("M3y (informational only)", f"{M3y:.4f} N·m")
        st.metric("Combined σ at R (axial + M3x)", f"{sigma_R/1e6:.4f} MPa")

    # =============================================================
    # SCENARIO 4
    # =============================================================
    elif scenario.startswith("Scenario 4"):
        st.subheader("Scenario 4: Base Beam (Strut B, Fixed-Fixed)")
        st.caption("Same top structure/load as Scenario 1. The total force and moment "
                   "transmitted into strut B are found first, then strut B is solved as "
                   "a fixed-fixed indeterminate beam using Macaulay brackets.")

        col1, col2 = st.columns(2)
        with col1:
            LD = st.number_input("Strut D length, LD (mm)", value=250.0, key="s4_LD")
            k = st.number_input("Free length of strut C, k (mm)", value=190.0, key="s4_k")
        with col2:
            L_base = st.number_input("Strut B total length (mm)", value=600.0, key="s4_Lbase")
            r = st.number_input("Strut A attachment position on B, r (mm)", value=195.0, key="s4_r")
        t_gauge = st.number_input("Gauge position on strut B, t (mm)", value=100.0, key="s4_t")

        with st.expander("Self-weight inputs (optional - set to 0 to ignore)"):
            colA, colB, colC = st.columns(3)
            with colA:
                density_C = st.number_input("Strut C linear density (kg/m)", value=0.9, key="s4_dC")
            with colB:
                density_D = st.number_input("Strut D linear density (kg/m)", value=0.9, key="s4_dD")
            with colC:
                m_conn = st.number_input("Connector mass (kg)", value=0.13, key="s4_mconn")

        st.markdown("**Applied load - movable weight (top structure, same as Scenario 1)**")
        col3, col4 = st.columns(2)
        with col3:
            mass = st.number_input("Hanging mass (kg)", min_value=0.0, max_value=5.0,
                                    value=1.0, step=0.0001, format="%.4f", key="s4_mass")
        with col4:
            d_load = st.number_input("Load position from top clamp, d (mm)", min_value=0.0,
                                      max_value=float(k + LD), value=float(k + LD) * 0.85,
                                      step=0.0001, format="%.4f", key="s4_d")

        # Step 1: total force & moment transmitted into strut B (same as scenario 1)
        Wc_free = density_C * (k / 1000) * g
        WD = density_D * (LD / 1000) * g
        Wcon = m_conn * g
        W = mass * g

        top_loads = [
            (k / 2 / 1000, Wc_free),
            (k / 1000, Wcon),
            ((k + LD / 2) / 1000, WD),
            (d_load / 1000, W),
        ]
        W_tot = sum(f for _, f in top_loads)
        M_tot = sum(f * p for p, f in top_loads)

        # Step 2: solve the fixed-fixed beam for R_left, M_left
        # (EI cancels out of both equations for a uniform beam - only
        # geometry and load matter for how the reactions split)
        L = L_base / 1000
        r_m = r / 1000
        coef = np.array([[L ** 2 / 2, -L],
                          [L ** 3 / 6, -L ** 2 / 2]])
        rhs = np.array([
            W_tot * (L - r_m) ** 2 / 2 - M_tot * (L - r_m),
            W_tot * (L - r_m) ** 3 / 6 - M_tot * (L - r_m) ** 2 / 2,
        ])
        R_left, M_left = np.linalg.solve(coef, rhs)

        t = t_gauge / 1000
        M_t = R_left * t - M_left - W_tot * macaulay(t, r_m, 1) + M_tot * macaulay(t, r_m, 0)

        sigma_x = M_t * (h / 2000) / I_e
        sigma_y = 0.0
        tau_xy = 0.0

        eps_x = sigma_x / E
        eps_y = -nu * sigma_x / E   # <-- the gauge is bonded TRANSVERSE, so it reads THIS
        gamma_xy = tau_xy / G

        gauge_reading, gauge_label = eps_y, "εy (transverse gauge - reads Poisson strain)"

        st.subheader("Reactions & internal forces")
        c1, c2, c3 = st.columns(3)
        c1.metric("Force into strut B", f"{W_tot:.3f} N")
        c2.metric("Moment into strut B", f"{M_tot:.4f} N·m")
        c3.metric("Moment at gauge", f"{M_t:.4f} N·m")
        c4, c5 = st.columns(2)
        c4.metric("Left reaction R_left", f"{R_left:.3f} N")
        c5.metric("Left reaction moment M_left", f"{M_left:.4f} N·m")

    # =============================================================
    # SHARED OUTPUT - gauge reading, stress element, Mohr's circles
    # =============================================================
    st.divider()
    st.subheader("Predicted Strain Gauge Reading")
    st.metric(f"Gauge output ({gauge_label})", f"{gauge_reading*1e6:.2f} µε")

    st.subheader("Stress Element at the Gauge")
    st.pyplot(plot_stress_element(sigma_x, sigma_y, tau_xy))

    st.subheader("Mohr's Circles - 0° and 45°")
    colM1, colM2 = st.columns(2)

    with colM1:
        fig_s, info_s = plot_mohr_circle(sigma_x, sigma_y, tau_xy, label="Stress",
                                          unit="MPa", scale=1e-6)
        st.pyplot(fig_s)
        st.write(f"σ1 = {info_s['a_1']/1e6:.4f} MPa,  σ2 = {info_s['a_2']/1e6:.4f} MPa,  "
                 f"θp = {info_s['theta_p_deg']:.2f}°")
        st.write(f"At 45°: σ = {info_s['a_45']/1e6:.4f} MPa,  τ = {info_s['b_45']/1e6:.4f} MPa")
        st.write(f"Max in-plane shear τmax = {info_s['max_shear']/1e6:.4f} MPa, "
                 f"σavg = {(sigma_x+sigma_y)/2/1e6:.4f} MPa,  θs = {info_s['theta_s_deg']:.2f}°")

    with colM2:
        fig_e, info_e = plot_mohr_circle(eps_x, eps_y, gamma_xy / 2, label="Strain",
                                          unit="µε", scale=1e6)
        st.pyplot(fig_e)
        st.write(f"ε1 = {info_e['a_1']*1e6:.2f} µε,  ε2 = {info_e['a_2']*1e6:.2f} µε,  "
                 f"θp = {info_e['theta_p_deg']:.2f}°")
        st.write(f"At 45°: ε = {info_e['a_45']*1e6:.2f} µε,  γ/2 = {info_e['b_45']*1e6:.2f} µε")
        st.write(f"Max in-plane shear γ/2 max = {info_e['max_shear']*1e6:.2f} µε, "
                 f"εavg = {(eps_x+eps_y)/2*1e6:.2f} µε,  θs = {info_e['theta_s_deg']:.2f}°")

