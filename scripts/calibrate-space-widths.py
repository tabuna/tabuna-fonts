#!/usr/bin/env python3
"""Construct a full-range space advance field from public native scalar layout."""
from pathlib import Path
import hashlib,json
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import AxisLimits
from fontTools.misc.roundTools import otRound
from fontTools.varLib.models import supportScalar
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/space-widths-baseline'
font=TTFont(BASE/'TabunaSans-with-hvar.ttf');grid=json.loads((BASE/'grid.json').read_text())
upm=font['head'].unitsPerEm;measurements={};runs=[]
for weight in grid['weights']:
    for size in grid['sizes']:
        path=BASE/f'{weight}-{size}.json';data=json.loads(path.read_text())
        assert data['referenceWeightMode']=='axis' and data['weight']==weight and data['pointSize']==size
        assert data['fontSHA256']==hashlib.sha256((BASE/'TabunaSans-before.ttf').read_bytes()).hexdigest()
        rows=[r for r in data['records'] if r['text'] in (' ','\u00a0')]
        assert len(rows)==2 and all(not r['fallback'] for r in rows)
        assert rows[0]['system']==rows[1]['system'],'Normal and nonbreaking space require separate models'
        measurements[(weight,size)]=otRound(rows[0]['system']*upm/size)
        runs.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
def location(weight,size):return AxisLimits({'wght':weight,'opsz':size}).limitAxesAndPopulateDefaults(font).normalize(font).defaultLocation()
wcoords={w:location(w,14)['wght'] for w in grid['weights']}
ocoords={s:location(400,s)['opsz'] for s in grid['sizes']}
assert len(set(wcoords.values()))==len(wcoords) and len(set(ocoords.values()))==len(ocoords)
def tent(values,key):
    keys=list(values);i=keys.index(key)
    return (values[keys[max(0,i-1)]],values[key],values[keys[min(len(keys)-1,i+1)]])
base=measurements[(400,14)];supports=[];deltas=[]
def add(support,delta):
    if delta:supports.append(support);deltas.append(delta)
for w in grid['weights']:
    if w!=400:add({'wght':tent(wcoords,w)},measurements[(w,14)]-base)
for s in grid['sizes']:
    if s!=14:add({'opsz':tent(ocoords,s)},measurements[(400,s)]-base)
for w in grid['weights']:
    if w==400:continue
    for s in grid['sizes']:
        if s==14:continue
        add({'wght':tent(wcoords,w),'opsz':tent(ocoords,s)},measurements[(w,s)]-measurements[(w,14)]-measurements[(400,s)]+base)
records=[]
for (w,s),target in measurements.items():
    predicted=base+sum(delta*supportScalar(location(w,s),support) for delta,support in zip(deltas,supports))
    assert predicted==target,(w,s,predicted,target)
    records.append({'weight':w,'size':s,'roundedTargetFU':target})
result={'method':'Tensor-product linear tents for nine weights and 24 optical sizes; native scalar advances rounded at 2048 UPM',
        'unitsPerEm':upm,'axes':{a.axisTag:[a.minValue,a.defaultValue,a.maxValue] for a in font['fvar'].axes},
        'avar':font['avar'].segments,'baseAdvance':base,'supports':supports,'deltas':deltas,'characters':[' ','\u00a0'],
        'records':records,'runs':runs,'baselineSHA256':hashlib.sha256((BASE/'TabunaSans-before.ttf').read_bytes()).hexdigest(),
        'note':'Replaces both space metric models after common tracking and local optical corrections. Does not modify outlines or other glyphs. Unmeasured sizes and weights require separate validation.'}
(ROOT/'sources/space-widths.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'samples':len(records),'baseAdvance':base,'nonzeroRegions':len(supports)}))
