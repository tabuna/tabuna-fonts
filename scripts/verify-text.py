#!/usr/bin/env python3
"""Measure complete strings in native layout; exact means no tolerance."""
from pathlib import Path
import json,subprocess

ROOT=Path(__file__).resolve().parents[1]
records=[]
for weight in (100,400,900):
    for size in (16,32,64,128):
        path=ROOT/f'proofs/text/{weight}-{size}.json'
        subprocess.run([str(ROOT/'build/measure-text'),str(ROOT/'dist/TabunaSansVariable.ttf'),
            str(ROOT/'sources/text-validation.json'),str(path),str(size),str(weight)],check=True,stdout=subprocess.DEVNULL)
        report=json.loads(path.read_text())
        for row in report['records']:
            records.append({'weight':weight,'pointSize':size,'text':row['text'],
                'own':row['own'],'system':row['system'],
                'advanceDifference':row['own']-row['system'],
                'kerningDifferenceFU':row['ownAdjustment']-row['systemAdjustment'],
                'exactAdvance':row['own']==row['system'] and not row['fallback']})
result={'fontSHA256':report['fontSHA256'],'os':report['os'],
    'referenceWeightMode':report['referenceWeightMode'],
    'scope':'Native complete-string advances at three weights; no pixel or cross-browser acceptance',
    'records':records,'exactAdvanceCount':sum(r['exactAdvance'] for r in records),
    'total':len(records),'byWeight':{str(w):{'exact':sum(r['exactAdvance'] for r in records if r['weight']==w),
        'total':sum(r['weight']==w for r in records)} for w in (100,400,900)}}
(ROOT/'proofs/text/results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('total','exactAdvanceCount','byWeight')},indent=2))
assert all(r['exactAdvance'] for r in records),'Text advances do not yet match the system in every tested case'
