import numpy as np


def bending_moment(supports, support_reactions, support_moments,
                   point_loads, distributed_loads, external_moments,
                   beam_length, resolution):
    x_coords = np.linspace(0, beam_length, int(beam_length * resolution) + 1)
    bending = np.zeros_like(x_coords)

    fixed_support_pos = None
    for sup_type, pos in supports:
        if sup_type == "Fixed":
            fixed_support_pos = pos

    if fixed_support_pos is not None:
        if len(support_reactions) == 2:
            pos_f, force = support_reactions[0]      # vertical reaction (kN)
            pos_m, moment_r = support_reactions[1]   # moment reaction (kNm)
            force_N = force * 1000.0                 # convert to N
            moment_Nm = moment_r * 1000.0            # convert to N·m

            mask = x_coords >= pos_f

            # Vertical reaction contribution: R * (x - x_fixed)
            bending[mask] += force_N * (x_coords[mask] - pos_f)

            # Fixed-end moment reaction contribution.
            # The moment reaction returned from reaction_calc is the
            # balancing moment (positive = hogging at root for a left-fixed
            # cantilever with downward loads).
            # Applied loads cause a sagging tendency → reactions resist that.
            # We subtract moment_Nm so that at the root (x=x_fixed) the net
            # bending moment equals -(applied moment sum), i.e. hogging.
            bending[mask] -= moment_Nm

    else:
        # Simply-supported or pin-roller: only vertical reactions
        for pos, mag in support_reactions:
            mag_N = mag * 1000.0
            mask = x_coords >= pos
            bending[mask] += mag_N * (x_coords[mask] - pos)

    # --- Point loads (kN → N) ---
    for pos, mag in point_loads:
        mag_N = mag * 1000.0
        mask = x_coords >= pos
        bending[mask] += mag_N * (x_coords[mask] - pos)

    # --- Distributed loads (kN/m → N/m) ---
    for start, end, start_mag, end_mag in distributed_loads:
        w0 = start_mag * 1000.0   # N/m at start
        w1 = end_mag * 1000.0     # N/m at end
        L_load = end - start

        for i, x in enumerate(x_coords):
            if x < start:
                continue
            elif x >= end:
                # Full resultant: rectangular + triangular
                rect_resultant = w0 * L_load
                rect_arm = x - (start + L_load / 2.0)
                tri_resultant = 0.5 * (w1 - w0) * L_load
                tri_arm = x - (start + 2.0 * L_load / 3.0)
                bending[i] += rect_resultant * rect_arm + tri_resultant * tri_arm
            else:
                # Partial: from start to x
                t = x - start
                w_t = w0 + (w1 - w0) * t / L_load
                bending[i] += w0 * t * (t / 2.0) + 0.5 * (w_t - w0) * t * (t / 3.0)

    # --- External moments (kNm → N·m) ---
    # Positive external moment causes downward jump → subtract
    for pos, mag in external_moments:
        mag_Nm = mag * 1000.0
        bending[x_coords >= pos] -= mag_Nm

    return x_coords, bending