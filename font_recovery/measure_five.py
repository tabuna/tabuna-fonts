"""Fit an authored cap/stem/open-bowl model to scalar scanline moments."""
import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from font_recovery.measure import Flatten, scan
from font_recovery.fitting import shape_features


def fit_profile(font, construction):
    gs = font.getGlyphSet()
    flat = Flatten(gs)
    gs[font.getBestCmap()[ord('5')]].draw(flat)
    points = np.concatenate(flat.contours)
    left, bottom = points.min(axis=0)
    right, top = points.max(axis=0)
    normalized = [[((x-left)/(right-left), (y-bottom)/(top-bottom)) for x, y in c]
                  for c in flat.contours]
    target = shape_features(normalized, [0, 0, 1, 1], count=81)
    # A designer's normalized starting proportions, shared by every master.
    # They are not taken from reference contour node positions.
    p = {'bounds': [0, 0, 1, 1],
         'cap': {'left': .1, 'right': .92, 'bottom': .88},
         'stem': {'inner_top': .25, 'inner_bottom': .2, 'outer_bottom': .03,
                  'bottom': .43, 'join_x': .18},
         'outer': {'shoulder_y': .56, 'shoulder_slope': 1.3, 'top_x': .52,
                   'top': .66, 'axis': .34, 'bottom_x': .5, 'cut': .28,
                   'handles': [[.4, .4] for _ in range(4)]},
         'inner': {'cut_x': .17, 'bottom_x': .5, 'bottom': .11, 'right': .82,
                   'axis': .34, 'top_x': .5, 'top': .55, 'join_slope': 1.4,
                   'handles': [[.4, .4] for _ in range(4)]}}
    # Measure the straight cap and stem, and the bowl's extrema independently.
    # This also initializes thin and heavy profiles with their actual stroke.
    rows = [.70, .74, .78]
    stem_runs = np.array([scan(normalized, y)[0] for y in rows])
    outer_line = np.polyfit(rows, stem_runs[:, 0], 1)
    inner_line = np.polyfit(rows, stem_runs[:, 1], 1)
    vertical = scan(normalized, .5, vertical=True)
    assert len(vertical) == 3
    p['cap'] = {'left':float(np.polyval(outer_line, 1)),
                'right':scan(normalized, .995)[-1][1], 'bottom':vertical[-1][0]}
    p['stem']['inner_top'] = float(np.polyval(inner_line, p['cap']['bottom']))
    norm_points = np.concatenate(normalized)
    p['outer']['cut'] = float(norm_points[np.argmin(norm_points[:, 0]), 1])
    p['outer']['axis'] = float(norm_points[np.argmax(norm_points[:, 0]), 1])
    p['inner']['axis'] = p['outer']['axis']
    p['inner']['bottom'], p['inner']['top'] = vertical[0][1], vertical[1][0]
    p['outer']['top'] = vertical[1][1]
    p['inner']['right'] = scan(normalized, p['outer']['axis'])[-1][0]
    p['inner']['cut_x'] = 1 - p['inner']['right']
    p['stem']['bottom'] = p['inner']['top'] - .12
    p['stem']['outer_bottom'] = float(np.polyval(outer_line, p['stem']['bottom']))
    p['stem']['join_x'] = float(np.polyval(inner_line, p['stem']['bottom']))
    p['outer']['shoulder_y'] = p['outer']['top'] - .1
    p['stem']['inner_bottom'] = float(np.polyval(inner_line, p['outer']['shoulder_y']))
    keys, values, low, high = [], [], [], []
    for role in ('cap', 'stem', 'outer', 'inner'):
        for key, value in p[role].items():
            if key == 'handles':
                for i in range(4):
                    for j in range(2):
                        keys.append((role, key, i, j)); values.append(value[i][j])
                        low.append(.08); high.append(.9)
            else:
                keys.append((role, key)); values.append(value)
                if 'slope' in key:
                    low.append(.2); high.append(4)
                else:
                    low.append(max(-.04, value-.23)); high.append(min(1.04, value+.23))

    def profile(v):
        result = copy.deepcopy(p)
        for path, value in zip(keys, v):
            field = result
            for key in path[:-1]:
                field = field[key]
            field[path[-1]] = float(value)
        return result

    def residual(v):
        drawing = Flatten(None)
        construction(profile(v)).replay(drawing)
        return shape_features(drawing.contours, [0, 0, 1, 1], count=81) - target

    fit = least_squares(residual, values, bounds=(low, high), max_nfev=100,
                        diff_step=1e-4, x_scale='jac',
                        ftol=1e-8, xtol=1e-8, gtol=1e-8)
    result = profile(fit.x)
    result['bounds'] = [float(v/font['head'].unitsPerEm*1000) for v in (left,bottom,right,top)]
    return result, {'residual_norm': float(np.linalg.norm(fit.fun)),
                    'evaluations': fit.nfev, 'converged': bool(fit.success)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--weights', default='100,400,900')
    args = parser.parse_args()
    sys.path.insert(0, str(args.workspace/'scripts'))
    spec = importlib.util.spec_from_file_location('five_bowl', args.workspace/'scripts/five_bowl.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    font = TTFont('/System/Library/Fonts/SFNS.ttf')
    options = subset.Options(); options.layout_features = []
    selector = subset.Subsetter(options=options); selector.populate(text='5'); selector.subset(font)
    data, evidence = {}, []
    for weight in map(int, args.weights.split(',')):
        data[str(weight)] = {}
        for label, optical in [('text', 17), ('display', 28)]:
            instance = instantiateVariableFont(font, {'wght':weight, 'opsz':optical, 'wdth':100, 'GRAD':400}, inplace=False)
            shape, result = fit_profile(instance, module.construction)
            data[str(weight)][label] = shape
            evidence.append({'weight':weight, 'optical':optical, **result})
            out = args.workspace/'sources/five-bowl.json'
            out.write_text(json.dumps({'weights':data}, indent=2)+'\n')
            out.with_suffix('.measurement.json').write_text(json.dumps({'method':'Scalar scanline moments; authored eight-arc topology; no source vertices exported', 'profiles':evidence}, indent=2)+'\n')
            print(evidence[-1], flush=True)


if __name__ == '__main__':
    main()
