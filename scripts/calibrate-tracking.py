#!/usr/bin/env python3
"""Measure size-dependent advances using our font and native system rendering.

No system font tables or outlines are opened. The known rectangle I isolates
spacing from curves. HVAR stores integer deltas; rounding remains in the report.
"""
from pathlib import Path
import hashlib
import json
import subprocess
from fontTools.ttLib import TTFont
import optical as optics

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'proofs/tracking-calibration'
OUT.mkdir(parents=True,exist_ok=True)
baseline=ROOT/'build/tracking-baseline.ttf'
font=TTFont(ROOT/'build/TabunaSans-untracked.ttf',recalcTimestamp=False)
optical_path=ROOT/'sources/optical-map.json'
if optical_path.exists():
    optical_map=json.loads(optical_path.read_text())
    assert optical_map['axisRange']==optics.AXIS_RANGE
    font['avar'].segments['opsz'].update({r['normalizedInput']:r['normalizedOutput'] for r in optical_map['records']})
if 'trak' in font:del font['trak']
font.save(baseline)
upm=font['head'].unitsPerEm
sizes=(9,12,14,16,18,20,24,28,32,40,48,56,64,72,96,128)
records=[]
for size in sizes:
    directory=OUT/str(size)
    subprocess.run([str(ROOT/'build/render-pairs'),str(baseline),str(directory),str(size),'I'],
                   check=True,stdout=subprocess.DEVNULL)
    data=json.loads((directory/'render-settings.json').read_text())
    pair=data['records'][0]
    delta=(pair['system']['advance']-pair['tabuna']['advance'])*upm/size
    stored=round(delta)
    records.append({'pointSize':size,'fontUnits':stored,'measuredFontUnits':delta,
        'roundingErrorFontUnits':stored-delta,
        'ownAdvance':pair['tabuna']['advance'],'referenceAdvance':pair['system']['advance'],
        'ownInkBounds':pair['tabuna']['inkBounds'],'referenceInkBounds':pair['system']['inkBounds']})
result={'purpose':'Measured normal tracking for the current original I construction',
    'axisRange':optics.AXIS_RANGE,
    'basisSHA256':hashlib.sha256(baseline.read_bytes()).hexdigest(),
    'referenceFont':data['systemPostScriptName'],'os':data['os'],'weight':400,
    'unitsPerEm':upm,'records':records,
    'note':'Recalibrate after changing the base advances of I. Rounded values are not evidence of exact matching.'}
(ROOT/'sources/tracking.json').write_text(json.dumps(result,indent=2)+'\n')
for r in records:
    print(r['pointSize'],r['fontUnits'],'rounding error',round(r['roundingErrorFontUnits'],6))
