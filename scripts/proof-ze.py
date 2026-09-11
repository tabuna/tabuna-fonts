#!/usr/bin/env python3
"""Compare the accepted variable з with the frozen control on unseen sizes/weights."""
import hashlib
import importlib.util
import json
import pathops
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ze_fit', ROOT/'scripts/reconstruct-ze.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


def main():
    out = ROOT/'build/ze-reconstruction'
    previous = out/'control.ttf'
    current = ROOT/'dist/TabunaSansVariable.ttf'
    fonts = {'before': previous, 'after': current}
    cases = [(w, s) for w in (100, 400, 900) for s in (9, 14, 16, 20, 32, 64, 128)]
    cases += [(w, s) for w in (250, 700) for s in (16, 64)]
    rows = []
    for weight, size in cases:
        row = {'weight': weight, 'size': size}
        for name, path in fonts.items():
            folder = out/'holdout'/f'{weight}-{size}'/name
            pilot.run([ROOT/'build/render-pairs', path, folder, size, 'з', 2, weight, 'axis'])
            settings = json.loads((folder/'render-settings.json').read_text())
            record = settings['records'][0]
            assert record['tabuna']['renderedFonts'] == [settings['customPostScriptName']]
            row[name] = pilot.metrics(pilot.coverage(folder/'0437-system.png'), pilot.coverage(folder/'0437-tabuna.png'))
            row[name]['advance'] = record['tabuna']['advance']
        row['deltaInkIoU'] = row['after']['inkIoU']-row['before']['inkIoU']
        assert row['deltaInkIoU'] > 0, row
        assert row['after']['advance'] == row['before']['advance'], row
        rows.append(row)
        print(json.dumps({'weight': weight, 'size': size, 'before': row['before']['inkIoU'],
                          'after': row['after']['inkIoU'], 'delta': row['deltaInkIoU']}, ensure_ascii=False), flush=True)
    # Changing a single outline must not silently alter other glyphs or advances.
    a, b = TTFont(previous), TTFont(current)
    for row in rows:
        glyphs = b.getGlyphSet(location={'wght': row['weight'], 'opsz': row['size']})
        path = pathops.Path()
        glyphs['uni0437'].draw(path.getPen())
        contours = list(pathops.simplify(path).contours)
        assert len(contours) == 1, (row['weight'], row['size'], 'Unexpected vector topology')
    changed = []
    for name in a.getGlyphOrder():
        assert a['hmtx'][name][0] == b['hmtx'][name][0], name
        if a['glyf'][name].compile(a['glyf']) != b['glyf'][name].compile(b['glyf']):
            changed.append(name)
        if name != 'uni0437':
            assert a['gvar'].variations[name] == b['gvar'].variations[name], name
    assert changed == ['uni0437'], changed
    report = {'controlSHA256': hashlib.sha256(previous.read_bytes()).hexdigest(),
              'acceptedSHA256': hashlib.sha256(current.read_bytes()).hexdigest(),
              'changedGlyphs': changed, 'cases': rows,
              'allCasesImproved': True, 'allAdvancesUnchanged': True,
              'otherGlyphsAndVariationsUnchanged': True,
              'vectorTopologyAllCases': 'One connected filled outline, no holes',
              'rasterTopologyCaveat': 'At weight 100 and 14/16/20 pt, threshold 0.5 breaks the subpixel-thin stroke into 4-connected islands in both fonts; the island counts differ by one. Vector topology stays intact.'}
    (out/'holdout-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    ref = pilot.coverage(out/'holdout/400-64/after/0437-system.png')
    final_rows = []
    for name in ('before', 'after'):
        own = pilot.coverage(out/f'holdout/400-64/{name}/0437-tabuna.png')
        folder = out/name
        folder.mkdir(exist_ok=True)
        pilot.error_image(ref, own, folder/'errors.png')
        final_rows.append({'name': name, **pilot.metrics(ref, own)})
    pilot.sheet(final_rows, ref, out)
    (out/'final-metrics.json').write_text(json.dumps(final_rows, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__': main()
