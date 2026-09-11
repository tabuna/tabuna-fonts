#!/usr/bin/env python3
"""Save pair positioning measured by CoreText, not reference font tables."""
from pathlib import Path
import json,hashlib
from fontTools.misc.roundTools import otRound

ROOT=Path(__file__).resolve().parents[1]
chars=json.loads((ROOT/'sources/kerning-charset.json').read_text())['characters']
nodes={};pairs=set();provenance=[]
for weight in (100,400,900):
    for size in (16,64):
        path=ROOT/f'references/css-weights-baseline/kerning/{weight}-{size}.json'
        report=json.loads(path.read_text())
        assert report['referenceWeightMode']=='axis'
        assert report['pairMode'] and report['measuredCount']==len(chars)**2
        assert report['fallbackCount']==0, 'Reference fallback requires separate treatment'
        values={r['text']:r['systemAdjustment'] for r in report['records']}
        nodes[weight,size]=values
        pairs.update(p for p,v in values.items() if v)
        provenance.append({'path':str(path.relative_to(ROOT)),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'weight':weight,'pointSize':size,'referenceFont':report['referenceFont'],
            'os':report['os'],'measuredCount':report['measuredCount'],
            'maximumRoundingError':max(abs(v-otRound(v)) for v in values.values())})
result={'method':'Normal minus disabled kerning; ligatures disabled during pair measurement',
    'unitsPerEm':2048,'characters':chars,'weights':[100,400,900],
    'opticalEndpoints':[16,64],'referenceRuns':provenance,
    'pairs':{p:{str(w):[nodes[w,s].get(p,0) for s in (16,64)] for w in (100,400,900)} for p in sorted(pairs)},
    'scope':'Zero pairs were measured too. Fractional deltas are retained here and rounded only for OpenType output.'}
(ROOT/'sources/kerning.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(f'{len(pairs)} nonzero pairs from {len(chars)**2} pairs × 6 locations')
