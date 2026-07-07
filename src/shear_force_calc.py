import numpy as np


def shear_force(support_reactions, point_loads, distributed_loads, beam_length, resolution):
    """
    All inputs in kN / kN/m. Reactions already in kN from reaction_calc.
    Returns shear force in N.

    Sign convention (beam mechanics, left-to-right):
      - Upward forces  → positive shear to the LEFT of the force
      - Downward forces → negative contribution
    The shear at any section x is the algebraic sum of all vertical forces
    to the LEFT of x.
    """
    x_coords = np.linspace(0, beam_length, int(beam_length * resolution) + 1)
    shear = np.zeros_like(x_coords)

    # --- Support reactions (kN → N) ---
    # Reaction at fixed support is upward (+ve) to balance downward loads.
    for pos, mag in support_reactions:
        mag_N = mag * 1000.0
        # Add reaction to all sections to the right of (or at) its position
        shear[x_coords >= pos] += mag_N

    # --- Point loads (kN → N) ---
    # Downward point loads are stored as negative magnitudes (e.g. -0.5 kN).
    for pos, mag in point_loads:
        mag_N = mag * 1000.0
        shear[x_coords >= pos] += mag_N

    # --- Distributed loads (kN/m → N/m) ---
    # For each x, add the resultant of the distributed load acting to the
    # LEFT of x (i.e. the area of the load diagram from start to min(x, end)).
    for start, end, start_mag, end_mag in distributed_loads:
        w0 = start_mag * 1000.0   # N/m at start (negative = downward)
        w1 = end_mag * 1000.0     # N/m at end   (negative = downward)
        L_load = end - start

        for i, x in enumerate(x_coords):
            if x <= start:
                # Load hasn't started yet
                continue
            elif x >= end:
                # Entire load is to the left: full resultant
                full_resultant = 0.5 * (w0 + w1) * L_load
                shear[i] += full_resultant
            else:
                # Partial load from start to x
                t = x - start
                # Interpolate intensity at x
                w_x = w0 + (w1 - w0) * t / L_load
                # Area of trapezoid from start to x
                partial_resultant = 0.5 * (w0 + w_x) * t
                shear[i] += partial_resultant

    return x_coords, shear