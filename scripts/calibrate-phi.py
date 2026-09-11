#!/usr/bin/env python3
"""Fit original ellipse/stem parameters to native Φ/φ PNG distance fields."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, gaussian_filter, map_coordinates
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]


def sources(weight, size):
    if weight == 400:
        folder = ROOT / f'references/phi-baseline/400-{size}'
    else:
        folder = ROOT / f'references/weight-metrics-baseline/{weight}-{size}'
    return folder, json.loads((folder / 'render-settings.json').read_text())


def cubic_ellipse(l, b, r, t, n=24):
    # Sampling the same four cubic arcs as Drawing.ellipse keeps the fitted
    # parameters smooth while retaining our authored four-segment topology.
    k = .5522847498307936
    cx, cy = (l + r) / 2, (b + t) / 2
    rx, ry = (r - l) / 2, (t - b) / 2
    arcs = [
        ((l, cy), (l, cy + k * ry), (cx - k * rx, t), (cx, t)),
        ((cx, t), (cx + k * rx, t), (r, cy + k * ry), (r, cy)),
        ((r, cy), (r, cy - k * ry), (cx + k * rx, b), (cx, b)),
        ((cx, b), (cx - k * rx, b), (l, cy - k * ry), (l, cy)),
    ]
    out = []
    for p0, p1, p2, p3 in arcs:
        for i in range(n):
            u = i / n; v = 1 - u
            out.append(np.array(v**3 * np.array(p0) + 3*v*v*u*np.array(p1) +
                                3*v*u*u*np.array(p2) + u**3*np.array(p3)))
    return np.asarray(out)


def edge_rect(l, b, r, t, n=32):
    out = []
    for a, z in [((l, b), (r, b)), ((r, b), (r, t)),
                 ((r, t), (l, t)), ((l, t), (l, b))]:
        for u in np.linspace(0, 1, n, endpoint=False):
            out.append(np.asarray(a) * (1-u) + np.asarray(z) * u)
    return np.asarray(out)


def contours(ch, p):
    outer_x, outer_y, inner_x, inner_y, stem_w, stem_bottom, stem_top = p
    l, b, r, t = outer_x, outer_y, 1 - outer_x, 1 - outer_y
    inner = (l + inner_x, b + inner_y, r - inner_x, t - inner_y)
    out = [cubic_ellipse(l, b, r, t), cubic_ellipse(*inner)]
    out.append(edge_rect(.5 - stem_w/2, stem_bottom, .5 + stem_w/2, stem_top))
    return out


def fit(folder, report, ch):
    rec = next(x for x in report['records'] if x['character'] == ch)
    size, scale = report['pointSize'], report['pixelScale']
    ox, oy = report['originPixels']
    l, b, w, h = rec['system']['inkBounds']
    raw = np.asarray(Image.open(folder / rec['system']['file']).convert('L'), float)
    x0 = int(ox + l * scale) - 10; y0 = int(oy - (b + h) * scale) - 10
    x1 = int(ox + (l + w) * scale) + 11; y1 = int(oy - b * scale) + 11
    target = raw[y0:y1, x0:x1]
    mask = target < 128
    sdf = gaussian_filter((distance_transform_edt(~mask) - distance_transform_edt(mask)).astype(float), .35)
    # Outer bounds and stem overshoots are deliberately held at the measured
    # box.  Only the counter and stroke thickness are fitted.
    lower = -.22 if ch == 'ф' else -.03
    upper = 1.06 if ch == 'ф' else 1.03
    initial = np.array([0.0, 0.0, .090, .090, .060 if ch == 'ф' else .065,
                        lower, upper])
    lo = np.array([0, 0, .015, .015, .015, lower - .03, upper - .03])
    hi = np.array([.04, .04, .20, .20, .20, lower + .03, upper + .03])
    variable = [2, 3, 4, 5, 6]

    def residual(v):
        p = initial.copy(); p[variable] = v
        samples = []
        for contour in contours(ch, p):
            for px, py in contour:
                samples.append((oy - (b + py * h) * scale - y0 - .5,
                                ox + (l + px * w) * scale - x0 - .5))
        return map_coordinates(sdf, np.asarray(samples).T, order=1, mode='nearest')

    result = least_squares(residual, initial[variable], bounds=(lo[variable], hi[variable]),
                           max_nfev=320, ftol=1e-9, xtol=1e-9, gtol=1e-9)
    p = initial.copy(); p[variable] = result.x
    preview = Image.new('L', mask.shape[::-1], 255); draw = ImageDraw.Draw(preview)
    for contour in contours(ch, p):
        draw.line([(ox + (x[0] * w + l) * scale - x0,
                    oy - (x[1] * h + b) * scale - y0) for x in contour], fill=0, width=1)
    preview.save(ROOT / 'build' / f'phi-fit-{ord(ch):04X}-{report["weight"]}-{size}.png')
    return {
        'parameters': [float(x) for x in p],
        'bounds': [float(l * 1000 / size), float(b * 1000 / size),
                   float(w * 1000 / size), float(h * 1000 / size)],
        'advance': float(rec['system']['advance'] * 1000 / size),
        'diagnostic': {'character': ch, 'weight': report['weight'], 'size': size,
                       'cost': float(result.cost), 'evaluations': result.nfev,
                       'success': bool(result.success)},
    }


def main():
    out = {'method': 'Original ellipse, counter and stem fitted to native PNG distance fields; no reference vectors',
           'glyphs': {}, 'runs': []}
    for weight in (100, 400, 900):
        for size, mode in ((16, 'text'), (64, 'display')):
            folder, report = sources(weight, size)
            for ch in 'Фф':
                out['glyphs'].setdefault(ch, {}).setdefault(str(weight), {})[mode] = fit(folder, report, ch)
            out['runs'].append({'report': str((folder / 'render-settings.json').relative_to(ROOT)),
                                'sha256': hashlib.sha256((folder / 'render-settings.json').read_bytes()).hexdigest(),
                                'weight': weight, 'pointSize': size})
    (ROOT / 'sources/phi.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print('Calibrated original Φ/φ ellipse constructions')


if __name__ == '__main__':
    main()
