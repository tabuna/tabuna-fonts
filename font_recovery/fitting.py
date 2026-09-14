"""Shape measurements used by several template families.

Fixed scanlines measure occupied width, its first moment and second moment.
These are scalar observations, not a parameterization of the source outline.
"""
import numpy as np


def scan_moments(contours, levels, origin, span, vertical=False, nonzero=False):
    starts = np.concatenate([np.asarray(c, dtype=float) for c in contours])
    ends = np.concatenate([np.roll(np.asarray(c, dtype=float), -1, axis=0) for c in contours])
    if vertical:
        starts, ends = starts[:, ::-1], ends[:, ::-1]
    levels = np.asarray(levels)[:, None]
    x0, y0 = starts[:, 0], starts[:, 1]
    x1, y1 = ends[:, 0], ends[:, 1]
    crosses = ((y0 <= levels) & (levels < y1)) | ((y1 <= levels) & (levels < y0))
    denominator = np.where(y1 == y0, 1, y1 - y0)
    intersections = (x0 + (levels - y0) * (x1 - x0) / denominator - origin) / span
    intersections = np.where(crosses, intersections, np.inf)
    if nonzero:
        # Font outlines use nonzero winding. Overlapping same-direction parts
        # remain filled; parity would incorrectly turn their overlap into holes.
        order = np.argsort(intersections, axis=1)
        positions = np.take_along_axis(intersections, order, axis=1)
        signs = np.where(crosses, np.where(y1 > y0, 1, -1), 0)
        winding = np.cumsum(np.take_along_axis(signs, order, axis=1), axis=1)
        left, right = positions[:, :-1], positions[:, 1:]
        filled = (winding[:, :-1] != 0) & np.isfinite(left) & np.isfinite(right)
        left, right = np.where(filled, left, 0), np.where(filled, right, 0)
        return np.stack([((right**power-left**power)/power).sum(axis=1)
                         for power in (1,2,3)], axis=1).ravel()
    intersections = np.sort(intersections, axis=1)
    # A closed contour has an even number of crossings on each scanline.
    assert np.all(crosses.sum(axis=1) % 2 == 0)
    if intersections.shape[1] % 2:
        intersections = np.pad(intersections, ((0, 0), (0, 1)), constant_values=np.inf)
    left, right = intersections[:, ::2], intersections[:, 1::2]
    left = np.where(np.isfinite(left), left, 0)
    right = np.where(np.isfinite(right), right, 0)
    return np.stack([((right**power - left**power) / power).sum(axis=1)
                     for power in (1, 2, 3)], axis=1).ravel()


def shape_features(contours, bounds, count=35, nonzero=False):
    left, bottom, right, top = bounds
    fractions = np.linspace(.015, .985, count)
    horizontal = scan_moments(contours, bottom + fractions * (top-bottom), left, right-left, nonzero=nonzero)
    vertical = scan_moments(contours, left + fractions * (right-left), bottom, top-bottom, True, nonzero=nonzero)
    return np.concatenate([horizontal, vertical])


def measure_closed_bowl(contour):
    """Fit a four-quarter model to contour dimensions and scan moments."""
    from scipy.optimize import least_squares
    from font_recovery.measure import Flatten
    from font_recovery.primitives import closed_bowl
    points = np.asarray(contour)
    low, high = points.min(axis=0), points.max(axis=0)
    bounds = [float(low[0]), float(low[1]), float(high[0]), float(high[1])]

    def extremum(axis, value):
        selected = points[np.abs(points[:, axis]-value) < 1e-6, 1-axis]
        return float(np.unique(selected).mean())

    extrema = {'top_x': extremum(1, high[1]), 'bottom_x': extremum(1, low[1]),
               'left_y': extremum(0, low[0]), 'right_y': extremum(0, high[0])}
    corners = ['top_left', 'top_right', 'bottom_right', 'bottom_left']
    target = shape_features([contour], bounds, count=45)

    def profile(v):
        return {'bbox': bounds, 'extrema': extrema,
                'tangents': {corner: [float(v[2*i]), float(v[2*i+1])]
                             for i, corner in enumerate(corners)}}

    def residual(v):
        candidate = Flatten(None)
        closed_bowl(candidate, profile(v))
        return shape_features(candidate.contours, bounds, count=45)-target

    fit = least_squares(residual, [.6]*8, bounds=([.2]*8, [.95]*8),
                        max_nfev=300, ftol=1e-10, xtol=1e-10, gtol=1e-10)
    return {**profile(fit.x), 'fit_residual_norm': float(np.linalg.norm(fit.fun))}
