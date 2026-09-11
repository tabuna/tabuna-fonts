#!/usr/bin/env python3
"""Fit our four-arc B/В/в construction to scalar raster profiles."""
from pathlib import Path
from PIL import Image
import hashlib, importlib.util, json

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bowl_fit', ROOT/'scripts/calibrate-bowls.py')
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
edges, fit_profile = shared.edges, shared.fit_profile


def measure(folder, rec, settings):
    im = Image.open(folder/rec['system']['file']).convert('L')
    pix = im.load()
    ox, oy = settings['originPixels']
    scale, size = settings['pixelScale'], settings['pointSize']
    unit = 1000/size
    left, bottom, width, height = rec['system']['inkBounds']
    right, top = left+width, bottom+height
    xl, xr = int(ox+left*scale)-3, int(ox+right*scale)+4
    yt, yb = int(oy-top*scale)-3, int(oy-bottom*scale)+4
    rows = []
    for py in range(yt, yb):
        es = [(v+xl-ox)/scale for v in edges([1-pix[x, py]/255 for x in range(xl, xr)])]
        if len(es) in (2, 4):
            rows.append(((oy-py-.5)/scale, es))
    stem = [es for y, es in rows if len(es) == 4]
    assert stem, rec['character']
    sl = sum(es[0] for es in stem)/len(stem)
    # Near the curved counter cap the first gap may vanish. Its straight
    # left wall is the minimum second edge, not the average of cap pixels.
    sr = min(es[1] for es in stem)
    columns = []
    # Use the attachment side: farther right the outside waist can create
    # an extra white interval that must not be mistaken for a counter.
    counter_limit = round(ox+(sr+(right-sr)*.25)*scale)
    for px in range(round(ox+sr*scale)+3, counter_limit):
        es = edges([1-pix[px, y]/255 for y in range(yt, yb)])
        if len(es) == 6:
            columns.append([(oy-e-yt)/scale for e in es])
    assert columns, rec['character']
    upper_top = max(v[1] for v in columns)
    upper_bottom = min(v[2] for v in columns)
    lower_top = max(v[3] for v in columns)
    lower_bottom = min(v[4] for v in columns)
    # The outside has two lobes separated by a narrow waist. Keep the
    # authored short connector between independently fitted quarter arcs.
    middle = [(y, es[-1]) for y, es in rows if lower_top < y < upper_bottom]
    assert middle, rec['character']
    narrowest = min(x for y, x in middle)
    waist_rows = [y for y, x in middle if x <= narrowest+.1/scale]
    waist_upper, waist_lower = max(waist_rows)+.5/scale, min(waist_rows)-.5/scale
    waist = (waist_upper+waist_lower)/2
    outer_upper = [(y*unit, es[-1]*unit) for y, es in rows if waist_upper+.5/scale < y < top-.5/scale]
    outer_lower = [(y*unit, es[-1]*unit) for y, es in rows if bottom+.5/scale < y < waist_lower-.5/scale]
    inner_upper = [(y*unit, es[-2]*unit) for y, es in rows if len(es) == 4 and y > waist]
    inner_lower = [(y*unit, es[-2]*unit) for y, es in rows if len(es) == 4 and y < waist]
    return {
        'stemLeft': sl*unit, 'stemRight': sr*unit,
        'top': top*unit, 'bottom': bottom*unit,
        'advance': rec['system']['advance']*unit,
        'outerUpper': fit_profile(outer_upper, waist_upper*unit, top*unit, sr*unit),
        'outerLower': fit_profile(outer_lower, bottom*unit, waist_lower*unit, sr*unit),
        'innerUpper': fit_profile(inner_upper, upper_bottom*unit, upper_top*unit, sr*unit),
        'innerLower': fit_profile(inner_lower, lower_bottom*unit, lower_top*unit, sr*unit),
    }


def main():
    data = {'method': 'Authored four-arc outer contour and two counters fitted to scalar raster profiles; no reference paths',
            'weights': [100, 400, 900], 'glyphs': {}, 'runs': []}
    for weight in (100, 400, 900):
        for size, mode in [(16, 'text'), (64, 'display')]:
            folder = ROOT/'references/css-weights-baseline/double-bowls'/f'{weight}-{size}'
            p = folder/'render-settings.json'
            settings = json.loads(p.read_text())
            assert settings['weight'] == weight
            assert settings['referenceWeightMode']=='axis'
            for rec in settings['records']:
                assert rec['system']['renderedFonts'] == [settings['systemPostScriptName']]
                result = measure(folder, rec, settings)
                data['glyphs'].setdefault(rec['character'], {}).setdefault(str(weight), {})[mode] = result
                print(weight, mode, rec['character'], {k: [round(result[k][q]['rms'], 3) for q in ('upper', 'lower')]
                      for k in ('outerUpper', 'outerLower', 'innerUpper', 'innerLower')}, flush=True)
            data['runs'].append({'report': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    (ROOT/'sources/double-bowls.json').write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
