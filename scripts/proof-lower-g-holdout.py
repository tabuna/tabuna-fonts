#!/usr/bin/env python3
"""Independent native validation of five glyphs outside fitted weight/size nodes."""
from pathlib import Path
from PIL import Image,ImageChops
from fontTools.ttLib import TTFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'proofs/lower-g'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
font=ROOT/'dist/TabunaSansVariable.ttf';baseline=ROOT/'references/lower-g-baseline/TabunaSans-before.ttf'
rows=[]
for weight in (200,300,500,600,700,800):
    for size in (14,20,24,48,96):
        folders=[OUT/f'holdout-{stage}-{weight}-{size}' for stage in ('before','after')]
        old,new=[json.loads((p/'comparison.json').read_text()) for p in folders]
        assert old['fontSHA256']==sha(baseline) and new['fontSHA256']==sha(font)
        assert old['weight']==new['weight']==weight and old['pointSize']==new['pointSize']==size
        assert old['referenceWeightMode']==new['referenceWeightMode']=='axis'
        assert [r['character'] for r in old['records']]==[r['character'] for r in new['records']]==list('gĝğġģ')
        for a,b in zip(old['records'],new['records']):
            images=[Image.open(p/r['system']['file']).convert('RGB') for p,r in zip(folders,(a,b))]
            assert ImageChops.difference(*images).getbbox() is None
            assert a['tabuna']['advance']==b['tabuna']['advance'] and a['system']['advance']==b['system']['advance']
            assert not a['customFallback'] and not b['customFallback'] and not a['referenceFallback'] and not b['referenceFallback']
            rows.append({'weight':weight,'size':size,'character':b['character'],'beforeInkIoU':a['inkIoU'],'afterInkIoU':b['inkIoU'],
                         'exactPixels':b['exactMatch'],'exactAdvance':b['exactAdvance'],'complete':b['completeMatch'],'differentPixels':b['differentPixels']})
def stats(rs):
    return {'total':len(rs),'improved':sum(r['afterInkIoU']>r['beforeInkIoU'] for r in rs),'worse':sum(r['afterInkIoU']<r['beforeInkIoU'] for r in rs),
            'exactPixels':sum(r['exactPixels'] for r in rs),'exactAdvance':sum(r['exactAdvance'] for r in rs),'complete':sum(r['complete'] for r in rs),
            'beforeMeanInkIoU':sum(r['beforeInkIoU'] for r in rs)/len(rs),'afterMeanInkIoU':sum(r['afterInkIoU'] for r in rs)/len(rs)}
before=TTFont(baseline);after=TTFont(font)
unchanged=[]
for tag in ['hmtx','avar','GPOS','GSUB','GDEF','MVAR','fvar','STAT']:
    assert before[tag].compile(before)==after[tag].compile(after),tag
    unchanged.append(tag)
def advance_model(font,name):
    model={}
    for v in font['gvar'].variations.get(name,[]):
        key=tuple((axis,tuple(support)) for axis,support in sorted(v.axes.items()))
        left,right=v.coordinates[-4:-2]
        delta=(right[0] if right is not None else 0)-(left[0] if left is not None else 0)
        model[key]=model.get(key,0)+delta
    return {k:v for k,v in model.items() if v}
for name in before.getGlyphOrder():
    assert advance_model(before,name)==advance_model(after,name),(name,'Advance variation model changed')
changed=[]
for name in before.getGlyphOrder():
    a=before['gvar'].variations.get(name,[]);b=after['gvar'].variations.get(name,[])
    if len(a)!=len(b) or any(x.axes!=y.axes or x.coordinates!=y.coordinates for x,y in zip(a,b)):changed.append(name)
assert changed==['g'],changed
report={'fontSHA256':sha(font),'beforeFontSHA256':sha(baseline),'scope':'g and four derivatives × six unfitted weights × five unfitted sizes; native pixel and scalar comparison, no tolerance',
        'allNativeAdvancesUnchanged':True,'allGlyphAdvanceModelsIdentical':True,'allReferencePixelsIdentical':True,'unchangedTables':unchanged,'changedVariationGlyphs':changed,
        'all':stats(rows),'byCharacter':{ch:stats([r for r in rows if r['character']==ch]) for ch in 'gĝğġģ'},'byWeight':{str(w):stats([r for r in rows if r['weight']==w]) for w in (200,300,500,600,700,800)},'rows':rows}
(OUT/'holdout-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
