import numpy as np


def calculate_reactions(supports, point_loads, distributed_loads, moments, beam_length):
    num_supports = len(supports)

    if num_supports == 1:
        for sup_type, pos in supports:
            if sup_type == "Fixed":
                fixed_pos = pos
                sum_forces = 0.0
                sum_moments = 0.0

                for p, mag in point_loads:
                    sum_forces += mag
                    sum_moments += mag * (p - fixed_pos)

                for start, end, start_mag, end_mag in distributed_loads:
                    length = end - start
                    resultant = 0.5 * (start_mag + end_mag) * length
                    if abs(start_mag + end_mag) > 1e-12:
                        centroid_from_start = (length / 3.0) * (start_mag + 2 * end_mag) / (start_mag + end_mag)
                    else:
                        centroid_from_start = length / 2.0
                    centroid_x = start + centroid_from_start
                    sum_forces += resultant
                    sum_moments += resultant * (centroid_x - fixed_pos)

                for p, mag in moments:
                    sum_moments += mag

                return [(fixed_pos, -sum_forces), (fixed_pos, -sum_moments)]

    elif num_supports == 2:
        if any(sup_type == "Fixed" for sup_type, pos in supports):
            return False

        sup_positions = [pos for sup_type, pos in supports]
        posA, posB = sup_positions[0], sup_positions[1]

        sum_forces = 0.0
        sum_mom_about_A = 0.0

        for p, mag in point_loads:
            sum_forces += mag
            sum_mom_about_A += mag * (p - posA)

        for start, end, start_mag, end_mag in distributed_loads:
            length = end - start
            resultant = 0.5 * (start_mag + end_mag) * length
            if abs(start_mag + end_mag) > 1e-12:
                centroid_from_start = (length / 3.0) * (start_mag + 2 * end_mag) / (start_mag + end_mag)
            else:
                centroid_from_start = length / 2.0
            centroid_x = start + centroid_from_start
            sum_forces += resultant
            sum_mom_about_A += resultant * (centroid_x - posA)

        for p, mag in moments:
            sum_mom_about_A += mag

        span = posB - posA
        if abs(span) < 1e-12:
            return False

        RB = -sum_mom_about_A / span
        RA = -sum_forces - RB

        return [(posA, RA), (posB, RB)]

    else:
        return False