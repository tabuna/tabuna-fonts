"""Measure A's four straight edges, crossbar and truncated counter apex."""
import argparse
import json
from pathlib import Path
import numpy as np
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.boundsPen import BoundsPen
from font_recovery.measure import Flatten, scan


def profile(font, character):
    gs = font.getGlyphSet(); name = font.getBestCmap()[ord(character)]
    flat, bounds = Flatten(gs), BoundsPen(gs)
    gs[name].draw(flat); gs[name].draw(bounds)
    left, bottom, right, top = bounds.bounds
    assert bottom == 0
    center = scan(flat.contours, (left + right) / 2, vertical=True, nonzero=True)
    assert len(center) == 2
    p = {'top': top / 2.048, 'bar_bottom': center[0][0] / 2.048,
         'bar_top': center[0][1] / 2.048, 'counter_top': center[1][0] / 2.048}
    levels = np.array([.08, .12, .16, .20]) * center[0][0]
    edges = []
    for y in levels:
        runs = scan(flat.contours, y, nonzero=True)
        assert len(runs) == 2
        edges.append([*runs[0], *runs[1]])
    residuals = {}
    for j, key in enumerate(['outer_left', 'inner_left', 'inner_right', 'outer_right']):
        values = np.array(edges)[:, j]
        slope, offset = np.polyfit(levels, values, 1)
        p[key] = [float(slope), float(offset / 2.048)]
        # Check the same equations above the crossbar, independently of fit rows.
        check = np.linspace(center[0][1] + 10, center[1][0] - 10, 7)
        error = []
        for y in check:
            runs = scan(flat.contours, y, nonzero=True)
            assert len(runs) == 2
            observed = [*runs[0], *runs[1]][j]
            error.append(abs(observed - (slope * y + offset)))
        residuals[key] = max(error)
    return p, residuals


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    font = TTFont('/System/Library/Fonts/SFNS.ttf')
    selector = subset.Subsetter(); selector.populate(text='AА'); selector.subset(font)
    data = {key: {} for key in ['A', 'uni0410']}; evidence = []
    for weight in [100, 400, 900]:
        for key in data: data[key][str(weight)] = {}
        for label, optical in [('text', 17), ('display', 28)]:
            instance = instantiateVariableFont(font, {'wght': weight, 'opsz': optical, 'wdth': 100, 'GRAD': 400})
            for character, key in [('A', 'A'), ('А', 'uni0410')]:
                p, residuals = profile(instance, character)
                data[key][str(weight)][label] = p
                evidence.append({'character': character, 'weight': weight, 'opsz': optical,
                                 'independent_upper_edge_residual_units': residuals})
    args.out.write_text(json.dumps({'glyphs': data}, indent=2) + '\n')
    args.out.with_suffix('.measurement.json').write_text(json.dumps({'method': __doc__, 'samples': evidence}, indent=2) + '\n')
    print(json.dumps(evidence, ensure_ascii=False))


if __name__ == '__main__': main()
