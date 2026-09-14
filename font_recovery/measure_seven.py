"""Measure bar dimensions and fit seven's diagonal equations to sections."""
import argparse
import json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten, scan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    font = TTFont('/System/Library/Fonts/SFNS.ttf')
    data = dict(weights={}, measurements=[])
    for weight in [100, 400, 900]:
        for label, optical in [('text', 17), ('display', 28)]:
            gs = font.getGlyphSet(location=dict(wght=weight, opsz=optical, wdth=100, GRAD=400))
            flat = Flatten(gs)
            gs[font.getBestCmap()[ord('7')]].draw(flat)
            contours = [(np.array(c)*1000/font['head'].unitsPerEm).tolist() for c in flat.contours]
            points = np.concatenate(contours)
            left, bottom = points.min(0)
            right, top = points.max(0)
            floor = scan(contours, left+(right-left)*.02, vertical=True, nonzero=True)[0][0]
            ys = np.linspace(bottom+(top-bottom)*.1, bottom+(top-bottom)*.65, 81)
            runs = [scan(contours, y, nonzero=True) for y in ys]
            assert all(len(r)==1 for r in runs)
            edges = np.array(runs)[:, 0, :]
            p = dict(left=float(left), right=float(right), top=float(top), bottom=float(bottom), floor=float(floor))
            residuals = []
            for i, key in enumerate(['diagonal_left', 'diagonal_right']):
                a, b = np.polyfit(ys, edges[:, i], 1)
                p[key] = [float(a), float(b)]
                residuals.append(float(max(abs(edges[:, i]-(a*ys+b)))))
            data['weights'].setdefault(str(weight), {})[label] = p
            data['measurements'].append(dict(weight=weight, optical=optical, line_residuals=residuals))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2)+'\n')
    print(json.dumps(data['measurements']))


if __name__ == '__main__':
    main()
