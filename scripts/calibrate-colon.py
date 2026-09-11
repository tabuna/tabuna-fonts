#!/usr/bin/env python3
"""Measure a contextual colon through shaped text runs, without paths."""
from pathlib import Path
import json,hashlib

ROOT=Path(__file__).resolve().parents[1]
nodes={};context_sets=[];provenance=[]
def advance(layout,index):return sum(g['advance'] for g in layout if g['index']==index)
for weight in (100,400,900):
    nodes[str(weight)]={}
    for label,size in [('text',16),('display',64)]:
        path=ROOT/f'references/css-weights-baseline/colon-context/{weight}-{size}.json';data=json.loads(path.read_text())
        assert data['referenceWeightMode']=='axis'
        assert data['fallbackCount']==0
        rows={r['text']:r for r in data['records']}
        base=rows[':']['systemUnkernedLayout'][0]
        sample=next(g for g in rows['H:H']['systemUnkernedLayout'] if g['index']==1)
        bx,by,bw,bh=base['bounds'];cx,cy,cw,ch=sample['bounds']
        sx,sy=cw/bw,ch/bh
        left={};right={}
        for text,row in rows.items():
            if len(text)!=3:continue
            colon=next(g for g in row['systemLayout'] if g['index']==1)
            if colon['glyph']==base['glyph']:continue
            if text.endswith(':H'):
                left[text[0]]=(advance(row['systemLayout'],0)-advance(row['systemUnkernedLayout'],0))*2048/size
            if text.startswith('H:'):
                right[text[-1]]=(advance(row['systemLayout'],1)-advance(row['systemUnkernedLayout'],1))*2048/size
        context_sets.append((set(left),set(right)))
        nodes[str(weight)][label]={'transform':[sx,0,0,sy,(cx-bx*sx)*2048/size,(cy-by*sy)*2048/size],
            'advance':sample['advance']*2048/size,'left':left,'right':right}
        provenance.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'weight':weight,'size':size,'referenceFont':data['referenceFont'],'os':data['os']})
assert all(s==context_sets[0] for s in context_sets),'Casing context varies across masters'
result={'method':'Shaped glyph identity, scalar bounding-box transform, and glyph advances',
    'unitsPerEm':2048,'leftContext':sorted(context_sets[0][0]),'rightContext':sorted(context_sets[0][1]),
    'nodes':nodes,'referenceRuns':provenance}
(ROOT/'sources/colon-context.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('Contextual colon:',len(result['leftContext']),len(result['rightContext']),'context characters')
