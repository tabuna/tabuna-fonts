#!/usr/bin/env python3
"""One measured handle correction for the reported three/point-84 kink."""
import importlib.util
import json
from pathlib import Path
import numpy as np
from fontTools.varLib.interpolatable import test
from ufoLib2 import Font

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fit', ROOT/'scripts/reconstruct-bowls.py')
fit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fit)
out = fit.OUT/'0033'
data = json.loads((out/'candidate.json').read_text())
control = data['weights']['100']['display']['curves']
point = np.array(control[28][0])
ratio = np.linalg.norm(point-control[27][2])/np.linalg.norm(np.array(control[28][1])-point)
curves = data['weights']['400']['text']['curves']
point = np.array(curves[28][0])
before = np.array(curves[27][2])
direction = (point-before)/np.linalg.norm(point-before)
after = point-direction*np.linalg.norm(np.array(curves[28][1])-point)*ratio
assert np.linalg.norm(after-before)*32/1000 <= 2
curves[27][2] = after.tolist()
fonts, names = [], []
for weight in ('100', '400', '900'):
    for mode in ('text', 'display'):
        font = Font()
        glyph = font.newGlyph('three')
        pen = glyph.getPen()
        cs = data['weights'][weight][mode]['curves']
        pen.moveTo(cs[0][0])
        for c in cs: pen.curveTo(*c[1:])
        pen.closePath()
        fonts.append(font)
        names.append(weight+'-'+mode)
diagnostics = test(fonts, glyphs=['three'], names=names, upem=1000)
assert not diagnostics, diagnostics
folder = out/'masters/400-16/baseline'
settings = json.loads((folder/'render-settings.json').read_text())
ref = fit.pilot.coverage(folder/'0033-system.png')
ox, oy = settings['originPixels']
factor = settings['pointSize']*settings['pixelScale']/1000
shape = {'threshold': .5, 'segments': [{'kind': 'cubic', 'points': (np.array(c)*[factor, -factor]+[ox, oy]).tolist()} for c in curves]}
result = fit.measure(shape, out/'join-fix', '3', settings, settings['records'][0]['tabuna']['advance'], ref)
old = next(m for m in data['masters'] if m['weight'] == 400 and m['size'] == 16)['after']
data['joinCorrection'] = {'master': '400-text', 'segment': 27, 'handle': 2,
                         'before': before.tolist(), 'after': after.tolist(),
                         'native16pt2xDisplacementPixels': float(np.linalg.norm(after-before)*32/1000),
                         'reason': 'The incoming/outgoing handle ratio caused a kink between masters; match the ratio at the corresponding thin-master join.',
                         'metricsBefore': old, 'metricsAfter': result,
                         'accepted': result['inkIoU'] >= old['inkIoU'] and result['loss'] <= old['loss']}
fit.write(out/'candidate-join-fixed.json', data)
fit.write(out/'interpolation-after-join-fix.json', diagnostics)
print(json.dumps({'before': old['inkIoU'], 'after': result['inkIoU'], 'accepted': data['joinCorrection']['accepted'],
                  'fpBefore': old['fp'], 'fpAfter': result['fp'], 'fnBefore': old['fn'], 'fnAfter': result['fn']}, ensure_ascii=False))
