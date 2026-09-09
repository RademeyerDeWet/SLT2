import numpy as np

from src.reaction_calc import calculate_reactions
from src.bending_moment_calc import bending_moment


def _moment_diagram(fixed_pos, point_loads, distributed_loads, moments, beam_length, resolution):
    """Bending moment diagram for a cantilever with a single Fixed support,
    reusing the already-tested single-support branch of calculate_reactions /
    bending_moment. Returns (x_coords, M(x), reactions)."""
    supports = [("Fixed", fixed_pos)]
    reactions = calculate_reactions(supports, point_loads, distributed_loads, moments, beam_length)
    x, M = bending_moment(supports, reactions, [], point_loads, distributed_loads, moments, beam_length, resolution)

    # bending_moment's inclusive "x >= pos" masking mis-evaluates any
    # concentrated force/moment sitting exactly at x = beam_length (the very
    # last sample): it picks up the post-jump value instead of the value
    # approaching the tip from inside the beam, corrupting just that one
    # point. Repair it by extrapolating the smooth interior trend, since
    # every load type here is otherwise continuous right up to the tip.
    if len(M) >= 3:
        M[-1] = 2 * M[-2] - M[-3]

    return x, M, reactions


def solve_propped_cantilever(fixed_pos, prop_pos, point_loads, distributed_loads, moments,
                              beam_length, resolution=2000):
    """
    One Fixed support + one Pin/Roller support (1x statically indeterminate).
    Solved with the force method: the Pin/Roller reaction is treated as the
    redundant, released against a cantilever fixed only at `fixed_pos`, and
    found from the compatibility condition that deflection at `prop_pos` is
    zero (unit-load / virtual-work theorem; EI cancels for a uniform beam).

    moments must already be in the internal anticlockwise-positive convention
    used by reaction_calc / bending_moment.

    Returns:
        {
          "fixed": {"pos": fixed_pos, "force": kN, "moment": kN.m},
          "prop":  {"pos": prop_pos, "force": kN},
        }
    """
    x, M0, _ = _moment_diagram(fixed_pos, point_loads, distributed_loads, moments, beam_length, resolution)

    unit_load = [(prop_pos, 1.0)]
    _, m1, _ = _moment_diagram(fixed_pos, unit_load, [], [], beam_length, resolution)

    delta0 = np.trapezoid(M0 * m1, x)
    delta1 = np.trapezoid(m1 * m1, x)
    R_prop = -delta0 / delta1

    full_point_loads = list(point_loads) + [(prop_pos, R_prop)]
    _, _, react_final = _moment_diagram(fixed_pos, full_point_loads, distributed_loads, moments, beam_length, resolution)
    R_fixed = react_final[0][1]
    M_fixed = react_final[1][1]

    return {
        "fixed": {"pos": fixed_pos, "force": R_fixed, "moment": M_fixed},
        "prop": {"pos": prop_pos, "force": R_prop},
    }


def solve_fixed_fixed(posA, posB, point_loads, distributed_loads, moments,
                       beam_length, resolution=2000):
    """
    Both ends Fixed (2x statically indeterminate). Solved with the force
    method: the force RB and moment MB at end B are the redundants, released
    against a cantilever fixed only at posA, found from the two compatibility
    conditions that deflection AND slope at posB are both zero.

    moments must already be in the internal anticlockwise-positive convention
    used by reaction_calc / bending_moment.

    Returns:
        {
          "A": {"pos": posA, "force": kN, "moment": kN.m},
          "B": {"pos": posB, "force": kN, "moment": kN.m},
        }
    """
    x, M0, _ = _moment_diagram(posA, point_loads, distributed_loads, moments, beam_length, resolution)

    unit_force_B = [(posB, 1.0)]
    _, m1, _ = _moment_diagram(posA, unit_force_B, [], [], beam_length, resolution)

    unit_moment_B = [(posB, 1.0)]
    _, m2, _ = _moment_diagram(posA, [], [], unit_moment_B, beam_length, resolution)

    d_B1 = np.trapezoid(m1 * m1, x)
    d_B2 = np.trapezoid(m1 * m2, x)
    th_B2 = np.trapezoid(m2 * m2, x)

    d_B0 = np.trapezoid(M0 * m1, x)
    th_B0 = np.trapezoid(M0 * m2, x)

    A_mat = np.array([[d_B1, d_B2],
                       [d_B2, th_B2]])
    rhs = -np.array([d_B0, th_B0])
    R_B, M_B = np.linalg.solve(A_mat, rhs)

    full_point_loads = list(point_loads) + [(posB, R_B)]
    full_moments = list(moments) + [(posB, M_B)]
    _, _, react_final = _moment_diagram(posA, full_point_loads, distributed_loads, full_moments, beam_length, resolution)
    R_A = react_final[0][1]
    M_A = react_final[1][1]

    return {
        "A": {"pos": posA, "force": R_A, "moment": M_A},
        "B": {"pos": posB, "force": R_B, "moment": M_B},
    }
