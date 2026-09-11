#!/usr/bin/env python3
"""Fit only з across six masters with a shared error-directed subdivision tree."""
import importlib.util
import json
from pathlib import Path
import numpy as np
from ordered_contours import fit_compatible_sections

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ze_fit', ROOT/'scripts/reconstruct-ze.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


def main():
    root = ROOT/'build/ze-reconstruction/masters'
    masters = []
    for weight in (100, 400, 900):
        for size, mode in ((16, 'text'), (64, 'display')):
            folder = root/f'{weight}-{size}'/'baseline'
            settings = json.loads((folder/'render-settings.json').read_text())
            r = settings['records'][0]
            ref = pilot.coverage(folder/r['system']['file'])
            loop, knots, sections = pilot.sections(ref, .5)
            masters.append({'weight': weight, 'mode': mode, 'size': size, 'settings': settings,
                            'record': r, 'ref': ref, 'sections': sections, 'segments': []})
    for section in range(len(pilot.LANDMARKS)):
        parts = [m['sections'][section] for m in masters]
        # The tolerance is in em, independent of capture magnification.
        tolerances = [.4*m['size']*m['settings']['pixelScale']/128 for m in masters]
        fitted = fit_compatible_sections(parts, tolerances)
        for m, pieces in zip(masters, fitted):
            for p in pieces:
                p['section'] = pilot.LANDMARKS[section][0]
            m['segments'].extend(pieces)
    data = {'method': 'Independent Cyrillic з, closed cubic outline fitted to ordered raster isocontours; shared adaptive subdivision at maximum measured contour errors.',
            'threshold': .5, 'fitToleranceEm': .4/128, 'glyphs': {'з': {}}, 'validation': []}
    for m in masters:
        folder = root/f"{m['weight']}-{m['size']}"/'compatible'
        folder.mkdir(exist_ok=True)
        shape = {'threshold': .5, 'segments': m['segments']}
        font = folder/'pilot.ttf'
        pilot.make_font(shape, m['settings'], m['record']['tabuna']['advance'], font)
        pilot.run([ROOT/'build/render-pairs', font, folder, m['size'], 'з', m['settings']['pixelScale'], m['weight'], 'axis'])
        own = pilot.coverage(folder/'0437-tabuna.png')
        validation = {'weight': m['weight'], 'size': m['size'], 'segments': len(m['segments']), **pilot.metrics(m['ref'], own)}
        print(json.dumps(validation, ensure_ascii=False), flush=True)
        data['validation'].append(validation)
        ox, oy = m['settings']['originPixels']
        factor = 1000/(m['size']*m['settings']['pixelScale'])
        curves = []
        for seg in m['segments']:
            points = np.array(seg['points'])
            points = (points-[ox, oy])*[factor, -factor]
            curves.append(points.tolist())
        data['glyphs']['з'].setdefault(str(m['weight']), {})[m['mode']] = {'curves': curves}
    data['segmentsPerMaster'] = len(masters[0]['segments'])
    path = ROOT/'sources/ze-curves.json'
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__': main()
