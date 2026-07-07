import numpy as np
from scipy.integrate import cumulative_trapezoid

def beam_deflection(x_coords, bending_moment, E, I, supports):
    EI = E * I
    curvature = np.array(bending_moment, dtype=float) / EI
    slope = cumulative_trapezoid(curvature, x_coords, initial=0.0)
    deflection = cumulative_trapezoid(slope, x_coords, initial=0.0)

    support_positions = [pos for sup_type, pos in supports]
    support_types = [sup_type for sup_type, pos in supports]

    if len(support_positions) >= 1 and "Fixed" in support_types:
        fixed_idx = support_types.index("Fixed")
        fixed_pos = support_positions[fixed_idx]
        idx_fixed = np.argmin(np.abs(x_coords - fixed_pos))
        slope_corrected = slope - slope[idx_fixed]
        deflection = cumulative_trapezoid(slope_corrected, x_coords, initial=0.0)
        deflection = deflection - deflection[idx_fixed]
        final_slope = slope_corrected

    elif len(support_positions) == 2 and "Fixed" not in support_types:
        idx_A = np.argmin(np.abs(x_coords - support_positions[0]))
        idx_B = np.argmin(np.abs(x_coords - support_positions[1]))
        def_A = deflection[idx_A]
        def_B = deflection[idx_B]
        xA = x_coords[idx_A]
        xB = x_coords[idx_B]
        A_mat = np.array([[xA, 1.0], [xB, 1.0]])
        b_vec = np.array([-def_A, -def_B])
        try:
            C1, C2 = np.linalg.solve(A_mat, b_vec)
        except np.linalg.LinAlgError:
            C1, C2 = 0.0, 0.0
        deflection = deflection + C1 * x_coords + C2
        final_slope = slope + C1  # same constant corrects the slope

    else:
        if support_positions:
            idx_A = np.argmin(np.abs(x_coords - support_positions[0]))
            deflection = deflection - deflection[idx_A]
        final_slope = slope

    return deflection, final_slope