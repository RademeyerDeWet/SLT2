import os
import subprocess
import sys

import streamlit as st


def ensure_dependencies():
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        import numpy as np
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
    for i in range(num_point_loads):
     pos = st.number_input(f"Point Load {i+1} Position (m)", min_value=0.0, max_value=beam_length, value=beam_length/2, step=0.1)
     mag = st.number_input(f"Point Load {i+1} Magnitude (kN)", value=-10.0, step=1.0)
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

    for i in range(num_dist_loads):
        start = st.number_input(f"Load {i+1} Start (m)", min_value=0.0, max_value=beam_length,
                            value=0.0, step=0.1, key=f"dist_start_{i}")
        end = st.number_input(f"Load {i+1} End (m)", min_value=0.0, max_value=beam_length,
                          value=beam_length, step=0.1, key=f"dist_end_{i}")
        start_mag = st.number_input(f"Load {i+1} Start Magnitude (kN/m)", value=-5.0, step=1.0,
                                key=f"dist_start_mag_{i}")
        end_mag = st.number_input(f"Load {i+1} End Magnitude (kN/m)", value=-5.0, step=1.0,
                              key=f"dist_end_mag_{i}")
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
        if start_mag == end_mag:
            # Rectangular load
            rect = plt.Rectangle((start, 0.4), end - start, 0.2,
                                 color='orange', alpha=0.3)
            ax_beam.add_patch(rect)
            for x in np.linspace(start, end, 5):
                ax_beam.arrow(x, 0.6, 0, -0.2,
                              head_width=0.05, head_length=0.05,
                              fc='orange', ec='orange')
        else:
            # Triangular load, flip depending on which side is larger
            if abs(start_mag) > abs(end_mag):
                tri = plt.Polygon([[start, 0.6], [end, 0.4], [start, 0.4]],
                                  color='orange', alpha=0.3)
            else:
                tri = plt.Polygon([[start, 0.4], [end, 0.6], [end, 0.4]],
                                  color='orange', alpha=0.3)
            ax_beam.add_patch(tri)
            for x in np.linspace(start, end, 5):
                ax_beam.arrow(x, 0.6, 0, -0.2,
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
    E = st.number_input("Young's Modulus E (Pa)", value=2.1e11, step=1e10, format="%.1f")
    I = st.number_input("Second Moment of Area I (m⁴)", value=8.33e-6, step=1e-6, format="%.11f")
    
    # Calculate reactions
    st.subheader("Results")
    reactions = calculate_reactions(supports, point_loads, distributed_loads, external_moments, beam_length)
    st.write(reactions)
    if reactions and reactions != False:
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
        ax_slope.plot(x_bm, np.degrees(slope_curve), 'm-', linewidth=2, label='Slope')
        ax_slope.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        ax_slope.fill_between(x_bm, 0, np.degrees(slope_curve), alpha=0.2, color='purple')
        ax_slope.set_xlabel('Position along beam (m)', fontsize=12)
        ax_slope.set_ylabel('Slope (degrees)', fontsize=12)
        ax_slope.set_title('Slope Diagram', fontsize=14, fontweight='bold')
        ax_slope.grid(True, alpha=0.3)
        ax_slope.legend()

        idx_max_slope = np.argmax(np.abs(slope_curve))
        max_slope_deg = np.degrees(slope_curve[idx_max_slope])
        max_slope_pos = x_bm[idx_max_slope]
        st.pyplot(fig_slope)
        st.write(
            f"Maximum Slope: {abs(max_slope_deg):.4f}° "
            f"at x = {max_slope_pos:.4f} m"
        )
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.error("Unable to calculate reactions. Check your support and load configuration.")
    
elif option == "Complex":
    st.header("Complex")
    picture = st.camera_input("Take a picture")
    if picture:
        st.image(picture)





