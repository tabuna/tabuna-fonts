"""Measure straight-band equations from scanline intervals, not outline nodes."""
import argparse
import json
from pathlib import Path
import numpy as np
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.boundsPen import BoundsPen
from font_recovery.measure import Flatten, scan


def profile(font, character='K', junction_floor=False):
    gs = font.getGlyphSet()
    name = font.getBestCmap()[ord(character)]
    flat, bounds = Flatten(gs), BoundsPen(gs)
    gs[name].draw(flat)
    gs[name].draw(bounds)
    left, bottom, right, top = bounds.bounds
    assert bottom == 0
    stems, result, residuals = [], {'top': top / 2.048}, {}
    for band, fractions in [('upper', [.82, .86, .90, .94, .98]),
                            ('lower', [.02, .06, .10, .14, .18])]:
        levels = np.array(fractions) * top
        edges = []
        for level in levels:
            runs = scan(flat.contours, level)
            assert len(runs) == 2, (band, level, runs)
            stems.append(runs[0])
            edges.append(runs[1])
        result[band] = {}
        for index, side in enumerate(['left', 'right']):
            observations = np.array(edges)[:, index]
            slope, intercept = np.polyfit(levels, observations, 1)
            result[band][side] = [float(slope), float(intercept / 2.048)]
            residuals[f'{band}_{side}'] = float(np.max(np.abs(observations - (slope * levels + intercept))))
    result['stem'] = (np.mean(stems, axis=0) / 2.048).tolist()
    if junction_floor:
        left, right = np.mean(stems, axis=0)
        observations = [scan(flat.contours, right+(right-left)*fraction,
                             vertical=True, nonzero=True)[0][0]
                        for fraction in [.01,.02,.03]]
        assert np.ptp(observations)<.01, 'Junction floor is not horizontal'
        result['upper']['floor'] = float(np.mean(observations)/2.048)
    return result, residuals


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--chars', default='K')
    parser.add_argument('--junction-floor', action='store_true')
    args = parser.parse_args()
    font = TTFont('/System/Library/Fonts/SFNS.ttf')
    options = subset.Options()
    options.layout_features = []
    selector = subset.Subsetter(options=options)
    selector.populate(text=args.chars)
    selector.subset(font)
    data, evidence = {}, []
    for weight in [100, 400, 900]:
        for label, optical in [('text', 17), ('display', 28)]:
            instance = instantiateVariableFont(font, {'wght': weight, 'opsz': optical, 'wdth': 100, 'GRAD': 400}, inplace=False)
            for character in args.chars:
                parameters, residuals = profile(instance, character, args.junction_floor)
                key=character if ord(character)<128 else f'uni{ord(character):04X}'
                data.setdefault(key,{}).setdefault(str(weight),{})[label]=parameters
                evidence.append({'character':character,'weight': weight, 'optical': optical, 'max_line_residual_units': residuals})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({'glyphs': data}, indent=2) + '\n')
    args.out.with_suffix('.measurement.json').write_text(json.dumps({
        'method': 'Least-squares boundary lines from fixed horizontal scan intervals; no source vertices exported',
        'samples': evidence,
    }, indent=2) + '\n')
    print(args.out)


if __name__ == '__main__':
    main()
