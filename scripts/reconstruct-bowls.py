#!/usr/bin/env python3
"""Isolated pilot and compatible-master fitting for independent З and 3.

Each stage is explicit; fitting never overwrites the production font or source.
"""
import argparse
import hashlib
import importlib.util
import json
import shutil
import time
from pathlib import Path
import numpy as np
from bowl_landmarks import LANDMARKS
from ordered_contours import fit_compatible_sections

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/bowl-reconstruction'
spec = importlib.util.spec_from_file_location('raster_fit', ROOT/'scripts/reconstruct-ze.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


def capture(font, folder, character, weight, size, scale):
    pilot.run([ROOT/'build/render-pairs', font, folder, size, character, scale, weight, 'axis'])
    settings = json.loads((folder/'render-settings.json').read_text())
    record = settings['records'][0]
    assert record['character'] == character
    assert record['system']['renderedFonts'] == [settings['systemPostScriptName']]
    assert record['tabuna']['renderedFonts'] == [settings['customPostScriptName']]
    return settings, record, pilot.coverage(folder/record['system']['file'])


def measure(shape, folder, character, settings, advance, ref):
    folder.mkdir(parents=True, exist_ok=True)
    font = folder/'pilot.ttf'
    pilot.make_font(shape, settings, advance, font, character)
    generated, record, target = capture(font, folder, character, settings['weight'], settings['pointSize'], settings['pixelScale'])
    assert generated['originPixels'] == settings['originPixels']
    assert np.array_equal(target, ref)
    own = pilot.coverage(folder/record['tabuna']['file'])
    pilot.error_image(ref, own, folder/'errors.png')
    return pilot.metrics(ref, own)


def prepare_control():
    OUT.mkdir(parents=True, exist_ok=True)
    control = OUT/'control.ttf'
    if not control.exists():
        shutil.copy2(ROOT/'dist/TabunaSansVariable.ttf', control)
        shutil.copy2(ROOT/'build/full-score.json', OUT/'full-score-before.json')
        shutil.copy2(ROOT/'build/full-score/64/comparison.json', OUT/'comparison-before.json')
    return control


def run_pilot(character):
    start = time.monotonic()
    control = prepare_control()
    out = OUT/f'{ord(character):04X}'
    out.mkdir(exist_ok=True)
    settings, record, ref = capture(control, out/'control', character, 400, 64, 2)
    old = pilot.coverage(out/'control'/record['tabuna']['file'])
    baseline = {'name': 'control', **pilot.metrics(ref, old)}
    pilot.error_image(ref, old, out/'control/errors.png')
    rows = [baseline]
    for threshold in (.25, .5, .75):
        folder = out/f'contour-{threshold:.2f}'
        shape = pilot.reconstruct(ref, threshold, LANDMARKS[character])
        result = measure(shape, folder, character, settings, record['tabuna']['advance'], ref)
        write(folder/'geometry.json', shape)
        row = {'name': folder.name, 'constructionThreshold': threshold, 'segments': len(shape['segments']), **result}
        rows.append(row)
        print(json.dumps({'glyph': character, **row}, ensure_ascii=False), flush=True)
    eligible = [r for r in rows[1:] if r['referenceTopology'] == r['renderTopology']
                and r['largestFN'] < baseline['largestFN'] and r['largestFP'] <= baseline['largestFP']
                and r['inkIoU'] > baseline['inkIoU'] and r['loss'] < baseline['loss']]
    selected = min(eligible, key=lambda r: r['loss']) if eligible else None
    report = {'glyph': character, 'fontSHA256': settings['fontSHA256'], 'rows': rows,
              'maskEvaluationThreshold': .5, 'selected': selected, 'elapsedSeconds': time.monotonic()-start}
    write(out/'pilot-report.json', report)
    pilot.sheet(rows, ref, out)
    print(json.dumps({'glyph': character, 'selected': selected['name'] if selected else None, 'seconds': report['elapsedSeconds']}, ensure_ascii=False))


def fit_masters(character):
    control = prepare_control()
    out = OUT/f'{ord(character):04X}'
    report = json.loads((out/'pilot-report.json').read_text())
    assert report['selected'], 'Pilot must pass before master fitting'
    threshold = report['selected']['constructionThreshold']
    masters = []
    for weight in (100, 400, 900):
        for size, mode, scale in ((16, 'text', 32), (64, 'display', 8)):
            folder = out/'masters'/f'{weight}-{size}'/'baseline'
            settings, record, ref = capture(control, folder, character, weight, size, scale)
            _, _, sections = pilot.sections(ref, threshold, LANDMARKS[character])
            masters.append({'weight': weight, 'size': size, 'mode': mode, 'settings': settings,
                            'record': record, 'ref': ref, 'sections': sections, 'segments': [],
                            'baseline': pilot.metrics(ref, pilot.coverage(folder/record['tabuna']['file']))})
    for index, landmark in enumerate(LANDMARKS[character]):
        parts = [m['sections'][index] for m in masters]
        tolerance = [.4*m['size']*m['settings']['pixelScale']/128 for m in masters]
        fitted = fit_compatible_sections(parts, tolerance)
        for master, segments in zip(masters, fitted):
            for seg in segments: seg['section'] = landmark[0]
            master['segments'].extend(segments)
    data = {'glyph': character, 'threshold': threshold, 'evaluationThreshold': .5,
            'method': 'Independent ordered raster contour, shared error-directed subdivision across six masters',
            'fitToleranceEm': .4/128, 'weights': {}, 'masters': []}
    for m in masters:
        folder = out/'masters'/f"{m['weight']}-{m['size']}"/'candidate'
        shape = {'threshold': threshold, 'segments': m['segments']}
        result = measure(shape, folder, character, m['settings'], m['record']['tabuna']['advance'], m['ref'])
        assert result['inkIoU'] > m['baseline']['inkIoU'], (m['weight'], m['size'], result)
        assert result['referenceTopology'] == result['renderTopology'], (m['weight'], m['size'], result)
        diag = {'weight': m['weight'], 'size': m['size'], 'segments': len(m['segments']), 'before': m['baseline'], 'after': result}
        data['masters'].append(diag)
        print(json.dumps({'glyph': character, 'weight': m['weight'], 'size': m['size'],
                          'segments': len(m['segments']), 'before': m['baseline']['inkIoU'], 'after': result['inkIoU']}, ensure_ascii=False), flush=True)
        ox, oy = m['settings']['originPixels']
        factor = 1000/(m['size']*m['settings']['pixelScale'])
        curves = [((np.array(s['points'])-[ox, oy])*[factor, -factor]).tolist() for s in m['segments']]
        data['weights'].setdefault(str(m['weight']), {})[m['mode']] = {'curves': curves}
    write(out/'candidate.json', data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('character', choices=list(LANDMARKS))
    parser.add_argument('stage', choices=['pilot', 'fit'])
    args = parser.parse_args()
    (run_pilot if args.stage == 'pilot' else fit_masters)(args.character)
