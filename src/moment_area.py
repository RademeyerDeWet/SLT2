"""Component bending-moment curves for the moment-area method.

The moment-area construction never draws the resultant diagram directly: it
draws a separate M/EI curve for every load and superposes them, because the
area and centroid of each simple shape are easy to write down (Hibbeler
Fig. 12-35/12-36).

`from_left` picks which end of the beam x is measured from:
  from_left=True  - x = 0 at the left end, increasing to the right. At each x,
                     only loads with pos <= x (to the left of x) are included:
                     a load's curve turns on once the cut passes it and stays
                     on for the rest of the beam.
  from_left=False - the mirror image, measured from the right end: only loads
                     with pos >= x (to the right of x) are included.

Either way, the one load that sits exactly at the end you are NOT measuring
from is carried straight into that support and isn't drawn as its own curve
(its contribution would be a trivial zero line in that convention). Both
choices superpose to the same resultant, the true bending moment diagram of
the beam once the redundants are known.

Conventions match src/bending_moment_calc.py: moments are sagging-positive
kN.m, forces upward-positive kN, couples anticlockwise-positive kN.m.
"""

import numpy as np

_ROOT_TOL = 1e-6


def _force_curve(x, pos, mag, anchor_left):
    """anchor_left=True: the load at the LEFT end is the one skipped, so every
    other load's curve must be computable without it - i.e. built from the
    free body to the right of the cut, nonzero only while x <= pos."""
    if anchor_left:
        return np.where(x <= pos, mag * (pos - x), 0.0)
    return np.where(x >= pos, mag * (x - pos), 0.0)


def _couple_curve(x, pos, mag, anchor_left):
    if anchor_left:
        return np.where(x <= pos, float(mag), 0.0)
    return np.where(x >= pos, -float(mag), 0.0)


def _udl_curve(x, start, end, w, anchor_left):
    """Uniform intensity `w` between `start` and `end`."""
    span = end - start
    centroid = 0.5 * (start + end)
    M = np.zeros_like(x)
    inside = (x >= start) & (x <= end)
    if anchor_left:
        M[inside] = 0.5 * w * (end - x[inside]) ** 2
        outside = x < start
        M[outside] = w * span * (centroid - x[outside])
    else:
        M[inside] = 0.5 * w * (x[inside] - start) ** 2
        outside = x > end
        M[outside] = w * span * (x[outside] - centroid)
    return M


def _sample_points(components, beam_length, resolution):
    # Duplicated samples either side of a discontinuity keep the couple jumps
    # vertical instead of smearing them over one grid step.
    eps = 1e-9
    pts = [np.linspace(0.0, beam_length, resolution)]
    for c in components:
        if c["kind"] == "udl":
            pts.append(np.array([c["start"], c["end"]]))
        else:
            pts.append(np.array([c["pos"] - eps, c["pos"], c["pos"] + eps]))
    x = np.unique(np.concatenate(pts))
    return x[(x >= 0.0) & (x <= beam_length)]


def moment_area_curves(components, beam_length, from_left, resolution=401):
    """Per-load bending moment curves and their superposition.

    components: one dict per load,
        {"kind": "force",  "pos": m, "mag": kN,    "label": str}
        {"kind": "couple", "pos": m, "mag": kN.m,  "label": str}
        {"kind": "udl", "start": m, "end": m, "w": kN/m, "label": str}
    Support reactions are passed in as ordinary force/couple components.

    See the module docstring for what `from_left` means. Returns
    (x, [(label, M), ...], M_total) with M in kN.m.
    """
    x = _sample_points(components, beam_length, resolution)

    # The component sitting at the END OPPOSITE the one x is measured from is
    # the one that gets carried straight into its support instead of drawn -
    # see _force_curve's docstring for why that pairing is the one that keeps
    # every other curve computable without knowing that reaction.
    anchor_left = not from_left
    root = 0.0 if anchor_left else beam_length

    curves = []
    for c in components:
        if c["kind"] == "udl":
            M = _udl_curve(x, c["start"], c["end"], c["w"], anchor_left)
        elif abs(c["pos"] - root) < _ROOT_TOL:
            continue
        elif c["kind"] == "force":
            M = _force_curve(x, c["pos"], c["mag"], anchor_left)
        else:
            M = _couple_curve(x, c["pos"], c["mag"], anchor_left)
        curves.append((c["label"], M))

    total = np.zeros_like(x)
    for _, M in curves:
        total += M
    return x, curves, total
