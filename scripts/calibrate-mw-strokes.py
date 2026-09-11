#!/usr/bin/env python3
"""Fit separate, interpolation-safe stroke contours for M and W."""
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, gaussian_filter, map_coordinates
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'references/mw-baseline'

# Normalized centre-line topology. Every master keeps the same four contours
# for W and the two stems plus two diagonals for M; only scalar parameters vary.
INITIAL = {
    'M': np.array([.117, .137, .145, .855, .00, .00], dtype=float),
    'W': np.array([.103, .050, .500, .218, .782], dtype=float),
}


def quad(a, b, width):
    a, b = np.asarray(a, float), np.asarray(b, float)
    v = b - a
    n = np.array([-v[1], v[0]]) / max(np.hypot(*v), 1e-9) * width / 2
    return np.array([a+n, b+n, b-n, a-n])


def edge_samples(poly, n=72):
    t = np.linspace(0, 1, n, endpoint=False)
    out=[]
    for a,b in zip(poly, np.concatenate([poly[1:], poly[:1]])):
        out.append(a[None,:]*(1-t[:,None]) + b[None,:]*t[:,None])
    return np.concatenate(out)


def contours(ch, p):
    if ch == 'M':
        sw, dw, top_l, top_r, valley, _ = p
        return [
            np.array([(0, 0), (sw, 0), (sw, 1), (0, 1)]),
            np.array([(1-sw, 0), (1, 0), (1, 1), (1-sw, 1)]),
            quad((top_l, 1), (.5, valley), dw),
            quad((.5, valley), (top_r, 1), dw),
        ]
    # W consists of the four diagonal strokes of the system glyph.
    dw, outer_top, central_top, valley_l, valley_r = p
    central_top = .5
    valley_r = 1 - valley_l
    return [
        quad((outer_top, 1), (valley_l, 0), dw),
        quad((valley_l, 0), (central_top, 1), dw),
        quad((1-valley_l, 0), (1-central_top, 1), dw),
        quad((valley_r, 0), (1-outer_top, 1), dw),
    ]


def fit(folder, report, ch):
    rec = next(x for x in report['records'] if x['character'] == ch)
    size, scale = report['pointSize'], report['pixelScale']
    ox, oy = report['originPixels']
    l, b, w, h = rec['system']['inkBounds']
    raw = np.asarray(Image.open(folder / rec['system']['file']).convert('L'), float)
    # Work in a compact window around the scalar bounds.
    x0 = int(ox + l*scale) - 10; y0 = int(oy - (b+h)*scale) - 10
    x1 = int(ox + (l+w)*scale) + 11; y1 = int(oy - b*scale) + 11
    target = raw[y0:y1, x0:x1]
    mask = target < 128
    sdf = distance_transform_edt(~mask) - distance_transform_edt(mask)
    sdf = gaussian_filter(sdf.astype(float), .35)
    # Parameter bounds preserve symmetry and keep joins inside the advance.
    x = INITIAL[ch].copy()
    if ch == 'M':
        # Apple’s vertical and diagonal strokes grow nonlinearly with weight.
        x[:2] = {100:(.055,.065), 400:(.120,.125), 900:(.205,.205)}[report['weight']]
        lo = np.array([max(.02,x[0]-.045), max(.025,x[1]-.045), .02, .74, -.03, 0])
        hi = np.array([min(.30,x[0]+.045), min(.30,x[1]+.045), .28, .98, .16, 0])
        variable = [0, 1, 2, 3, 4]
    else:
        x[0] = {100:.055, 400:.105, 900:.205}[report['weight']]
        lo = np.array([max(.025,x[0]-.055), .00, .40, .12, .64])
        hi = np.array([min(.34,x[0]+.055), .25, .60, .36, .88])
        variable = [0, 1, 3]
    def unpack(v):
        p = x.copy(); p[variable] = v; return p
    # Fit the target distance field at candidate contour edges. Sampling edges
    # rather than thresholding a raster gives useful gradients at subpixel scale.
    def residual(v):
        p = unpack(v); samples=[]
        for poly in contours(ch, p):
            for px,py in edge_samples(poly):
                samples.append((oy-(b+py*h)*scale-y0-.5,
                                ox+(l+px*w)*scale-x0-.5))
        yy=np.asarray(samples).T
        return map_coordinates(sdf, yy, order=1, mode='nearest')
    result = least_squares(residual, x[variable], bounds=(lo[variable], hi[variable]),
                           max_nfev=260, ftol=1e-8, xtol=1e-8, gtol=1e-8)
    p = unpack(result.x)
    preview = Image.new('L', mask.shape[::-1], 255); d = ImageDraw.Draw(preview)
    for poly in contours(ch, p): d.polygon([(ox+(l+px*w)*scale-x0, oy-(b+py*h)*scale-y0) for px,py in poly], fill=0)
    sheet = Image.new('L', (preview.width*2, preview.height), 255); sheet.paste(preview, (0,0)); sheet.paste(Image.fromarray(np.uint8(raw[y0:y1,x0:x1])), (preview.width,0))
    out = ROOT / 'build' / f'mw-strokes-fit-{ch}-{report["weight"]}-{size}.png'; sheet.save(out)
    return {
        'parameters': [float(v) for v in p],
        'bounds': [float(l*1000/size), float(b*1000/size),
                   float(w*1000/size), float(h*1000/size)],
        'advance': rec['system']['advance'] * 1000 / size,
        'diagnostic': {'character':ch,'weight':report['weight'],'size':size,
                       'cost':float(result.cost),'evaluations':result.nfev,
                       'success':bool(result.success),'preview':str(out.relative_to(ROOT))},
    }


def main():
    out={'method':'Four independent authored M/W stroke contours fitted to native PNG distance fields; no reference vectors','glyphs':{},'runs':[]}
    for weight in (100,400,900):
        for size, mode in ((16,'text'), (64,'display')):
            folder=BASE/f'{weight}-{size}'; settings=json.loads((folder/'render-settings.json').read_text())
            for ch in 'MW':
                fitted=fit(folder,settings,ch)
                out['glyphs'].setdefault(ch,{}).setdefault(str(weight),{})[mode]=fitted
            out['runs'].append({'report':str((folder/'render-settings.json').relative_to(ROOT)), 'sha256':hashlib.sha256((folder/'render-settings.json').read_bytes()).hexdigest(), 'weight':weight,'size':size})
    (ROOT/'sources/mw-strokes.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print('Calibrated M/W stroke contours')

if __name__ == '__main__': main()
