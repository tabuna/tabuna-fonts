"""Class-specific measurements for open bowls and stemmed bowls."""
import copy
import numpy as np
from scipy.optimize import least_squares
from fontTools.pens.recordingPen import RecordingPen

from font_recovery.measure import Flatten, scan
from font_recovery.fitting import shape_features
from font_recovery.primitives import open_bowl


def measure_open_bowl(font, character, measured, flattened):
    left, bottom, right, top = measured['bbox']
    width, height = right-left, top-bottom
    recording = RecordingPen()
    font.getGlyphSet()[font.getBestCmap()[ord(character)]].draw(recording)
    caps, current = [], None
    for operation, points in recording.value:
        if operation == 'lineTo' and current is not None:
            endpoint = points[0]
            if (abs(endpoint[1]-current[1]) < 1e-6
                    and min(endpoint[0], current[0]) > left+width*.5
                    and width*.04 < abs(endpoint[0]-current[0]) < width*.4):
                caps.append({'outer': [max(endpoint[0], current[0]), endpoint[1]],
                             'inner': [min(endpoint[0], current[0]), endpoint[1]]})
        if operation not in ('closePath', 'endPath'):
            current = points[-1]
    assert len(caps) == 2, (character, 'two flat terminal cuts required', caps)
    lower, upper = sorted(caps, key=lambda cap: cap['outer'][1])

    # Open counters have no separate contour. Measure their three closed sides
    # with scanlines that lie behind the opening instead of treating them as 0.
    horizontal = [scan(flattened.contours, y)[0]
                  for y in np.linspace(bottom+height*.35, bottom+height*.65, 41)]
    vertical = [scan(flattened.contours, x, vertical=True)
                for x in np.linspace(left+width*.35, left+width*.7, 101)]
    assert all(len(runs) == 2 for runs in vertical)
    inner_left = min(run[1] for run in horizontal)
    inner_bottom = min(runs[0][1] for runs in vertical)
    inner_top = max(runs[1][0] for runs in vertical)
    common = {'top_x': (left+right)/2, 'bottom_x': (left+right)/2,
              'axis_y': (bottom+top)/2, 'kx': .6, 'ky': .6,
              'back_kx': .6, 'back_ky': .6, 'departure': .08}
    parameters = {
        **measured, 'template': 'open_bowl',
        'lower_terminal': lower, 'upper_terminal': upper,
        'outer': {**common, 'left': left, 'bottom': bottom, 'top': top},
        'inner': {**common, 'left': inner_left, 'bottom': inner_bottom, 'top': inner_top},
    }
    keys = [(role, key) for role in ('outer', 'inner')
            for key in ('top_x', 'bottom_x', 'axis_y', 'kx', 'ky', 'back_kx', 'back_ky', 'departure')]
    keys += [('inner', key) for key in ('left', 'bottom', 'top')]
    horizontal_keys = {'top_x', 'bottom_x', 'left'}
    vertical_keys = {'axis_y', 'top', 'bottom'}

    def normalize(key, value):
        return ((value-left)/width if key in horizontal_keys else
                (value-bottom)/height if key in vertical_keys else value)

    def profile(values):
        result = copy.deepcopy(parameters)
        for (role, key), value in zip(keys, values):
            result[role][key] = (left+value*width if key in horizontal_keys else
                                 bottom+value*height if key in vertical_keys else float(value))
        return result

    start = [normalize(key, parameters[role][key]) for role, key in keys]
    limits = {'top_x': (.25, .8), 'bottom_x': (.25, .8), 'axis_y': (.3, .7),
              'kx': (.2, .95), 'ky': (.2, .95), 'departure': (0, .5),
              'back_kx': (.2, .95), 'back_ky': (.2, .95),
              'left': (.02, .45), 'bottom': (.02, .4), 'top': (.6, .98)}
    target = shape_features(flattened.contours, measured['bbox'])

    def residual(values):
        candidate = Flatten(None)
        open_bowl(candidate, profile(values))
        return shape_features(candidate.contours, measured['bbox']) - target

    fit = least_squares(residual, start,
                        bounds=([limits[key][0] for _, key in keys],
                                [limits[key][1] for _, key in keys]),
                        max_nfev=400, ftol=1e-9, xtol=1e-9, gtol=1e-9)
    result = profile(fit.x)
    result['fit_residual_norm'] = float(np.linalg.norm(fit.fun))
    result['observed_scan_features'] = target.tolist()
    return result


def measure_flat_bowl(contour):
    from font_recovery.primitives import flat_bowl
    points = np.asarray(contour)
    left, bottom = points.min(axis=0)
    right, top = points.max(axis=0)
    width, height = right-left, top-bottom
    bounds = [float(left), float(bottom), float(right), float(top)]
    target = shape_features([contour], bounds)

    def profile(v):
        return {'bbox': bounds, 'top_x': float(left+v[0]*width),
                'bottom_x': float(left+v[1]*width), 'axis_y': float(bottom+v[2]*height),
                'kx': float(v[3]), 'ky': float(v[4])}

    def residual(v):
        candidate = Flatten(None)
        flat_bowl(candidate, profile(v))
        return shape_features(candidate.contours, bounds)-target

    fit = least_squares(residual, [.4, .4, .5, .6, .6],
                        bounds=([.05, .05, .3, .2, .2], [.7, .7, .7, .95, .95]),
                        max_nfev=300, ftol=1e-10, xtol=1e-10, gtol=1e-10)
    return {**profile(fit.x), 'fit_residual_norm': float(np.linalg.norm(fit.fun))}


def measure_stem_bowl(font, character, measured, flattened):
    from font_recovery.primitives import stem_bowl
    from font_recovery.measure_templates import moments
    from font_recovery.fitting import measure_closed_bowl
    left, bottom, right, top = measured['bbox']
    mirror = character in 'dq'
    if mirror:
        flattened.contours = [[(left+right-x, y) for x, y in contour]
                              for contour in flattened.contours]
    body_height = font['OS/2'].sxHeight
    level = (body_height+top)/2 if character in 'bd' else bottom/2
    runs = scan(flattened.contours, level)
    assert len(runs) == 1, (character, 'isolated upright expected')
    stem = runs[0][1]-runs[0][0]
    stem_bottom, stem_top = scan(flattened.contours, left+stem/2, vertical=True)[0]
    contours = sorted(flattened.contours, key=lambda c: moments(c)[0], reverse=True)
    assert len(contours) == 2, (character, 'one outer boundary and one counter required')
    bowl_points = [(x, y) for x, y in contours[0] if x > left+stem+1]
    bowl_bottom = min(y for x, y in bowl_points)
    bowl_top = max(y for x, y in bowl_points)
    height, width = bowl_top-bowl_bottom, right-left
    inner = measure_closed_bowl(contours[1])
    parameters = {**measured, 'template': 'stem_bowl', 'mirror': mirror,
                  'stem': stem, 'stem_bottom': stem_bottom, 'stem_top': stem_top,
                  'bowl_bottom': bowl_bottom, 'bowl_top': bowl_top, 'inner': inner}
    keys = ['top_x', 'bottom_x', 'axis_y', 'join_top', 'join_bottom', 'kx', 'ky',
            'departure_top_x', 'departure_top_y', 'departure_bottom_x', 'departure_bottom_y']

    def profile(v):
        result = copy.deepcopy(parameters)
        for key, value in zip(keys, v):
            if key in ('top_x', 'bottom_x'):
                value = left+value*width
            elif key in ('axis_y', 'join_top', 'join_bottom'):
                value = bowl_bottom+value*height
            result[key] = float(value)
        return result

    target_bounds = [left, bowl_bottom, right, bowl_top]
    target = shape_features(flattened.contours, target_bounds)

    def residual(v):
        candidate = Flatten(None)
        stem_bowl(candidate, profile(v))
        return shape_features(candidate.contours, target_bounds)-target

    minimum_center = stem/width+.03
    fit = least_squares(residual, [.6, .6, .5, .8, .2, .6, .6, .2, .8, .2, .8],
                        bounds=([minimum_center, minimum_center, .35, .55, .03, .2, .2, .02, .02, .02, .02],
                                [.85, .85, .65, .97, .45, .95, .95, .9, .95, .9, .95]),
                        max_nfev=400, ftol=1e-9, xtol=1e-9, gtol=1e-9)
    result = profile(fit.x)
    result['fit_residual_norm'] = float(np.linalg.norm(fit.fun))
    result['observed_scan_features'] = target.tolist()
    return result
