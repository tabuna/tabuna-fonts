#!/usr/bin/env python3
"""Calibrate scalar extreme-weight proportions from an immutable own baseline."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/weight-metrics-baseline'
p=BASE/'own-dimensions.json';own=json.loads(p.read_text())
result={'method':'Scalar bounds and advances; original topology retained; Regular correction only for explicitly listed symbols',
        'weights':[100,900],'regularCharacters':own.get('regularCharacters',''),'ownDimensions':str(p.relative_to(ROOT)),
        'ownDimensionsSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'glyphs':{},'referenceRuns':[]}
for weight in (100,400,900):
    for size,mode in [(16,'text'),(64,'display')]:
        path=BASE/f'{weight}-{size}'/'render-settings.json';report=json.loads(path.read_text())
        assert report['referenceWeightMode']=='axis' and report['weight']==weight
        expected=own['regularCharacters'] if weight==400 else own['characters']
        assert set(r['character'] for r in report['records'])==set(expected)
        rows={r['character']:r for r in report['records']}
        node=own['nodes'][str(weight)][mode]
        own_body=node['x']['bounds'][3] if 'x' in node else 0
        flat=rows['x']['system']['inkBounds'] if 'x' in rows else [0,0,0,0]
        target_body=(flat[1]+flat[3])*1000/size
        for ch,basis in node.items():
            r=rows[ch];assert r['system']['renderedFonts']==[report['systemPostScriptName']]
            x0,y0,x1,y1=basis['bounds'];rx,ry,rw,rh=[v*1000/size for v in r['system']['inkBounds']]
            assert rw>0 and rh>0 and x1>x0 and y1>y0
            sx=rw/(x1-x0);knots=[(y0,ry),(y1,ry+rh)]
            if ch.islower():
                if y0<0<y1 and ry<0<ry+rh:knots.append((0.,0.))
                if y0<own_body<y1-1e-6 and ry<target_body<ry+rh:knots.append((own_body,target_body))
            knots.sort()
            assert all(a[0]<b[0] and a[1]<b[1] for a,b in zip(knots,knots[1:])),(ch,knots)
            result['glyphs'].setdefault(basis['key'],{'character':ch,'nodes':{}})['nodes'].setdefault(str(weight),{})[mode]={
                'sx':sx,'dx':rx-x0*sx,'y':knots,'baseAdvance':basis['advance'],'advance':r['system']['advance']*1000/size}
        result['referenceRuns'].append({'report':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'weight':weight,'pointSize':size,'os':report['os']})
(ROOT/'sources/weight-metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(f'Calibrated scalar proportions of {len(result["glyphs"])} base glyphs at weights 100/900.')
