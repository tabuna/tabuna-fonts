#!/usr/bin/env python3
"""Native calibration regression, explicitly limited to I at weight 400."""
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
records=[]
for size in (9,12,14,16,18,20,24,28,32,40,48,56,64,72,96,128):
    directory=ROOT/f'proofs/rectangle-calibration/{size}'
    subprocess.run([str(ROOT/'build/render-pairs'),str(ROOT/'dist/TabunaSansVariable.ttf'),
                    str(directory),str(size),'I'],check=True,stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable,str(ROOT/'scripts/compare-pixels.py'),str(directory)],
                   check=True,stdout=subprocess.DEVNULL)
    report=json.loads((directory/'comparison.json').read_text());row=report['records'][0]
    records.append({'pointSize':size,'differentPixels':row['differentPixels'],
                    'advanceDifference':row['advanceDifference'],'completeMatch':row['completeMatch']})
result={'fontSHA256':report['fontSHA256'],'systemFont':report['systemPostScriptName'],
    'os':report['os'],'records':records,'completeCount':sum(r['completeMatch'] for r in records),
    'pixelExactCount':sum(r['differentPixels']==0 for r in records),
    'scope':'I only, weight 400 in native CoreText; not full-font or web acceptance'}
(ROOT/'proofs/rectangle-calibration/results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('completeCount','pixelExactCount','scope')},indent=2))
assert all(r['differentPixels']==0 for r in records),'Native raster calibration regressed'
assert all(r['completeMatch'] for r in records if r['pointSize'] in (16,32,64,128)), 'Primary calibration advances regressed'
