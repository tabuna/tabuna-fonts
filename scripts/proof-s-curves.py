#!/usr/bin/env python3
"""Strict native raster and advance invariants for S/s, Cyrillic dze and their canonical derivatives."""
from pathlib import Path
from PIL import Image,ImageChops,ImageOps,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
import json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/s-curves-baseline';OUT=ROOT/'proofs/s-curves'
parser=argparse.ArgumentParser();parser.add_argument('--holdout',action='store_true');args=parser.parse_args()
cfg=json.loads((BASE/'validation.json').read_text());strings=cfg['affected'] if args.holdout else cfg['strings']
weights=(200,300,500,600,700,800) if args.holdout else (100,400,900);sizes=(14,20,24,48,96) if args.holdout else (16,32,64,128)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();fontpath=ROOT/'dist/TabunaSansVariable.ttf';baseline=BASE/'TabunaSans-before.ttf'
rows=[]
for weight in weights:
    for size in sizes:
        prefix='holdout-' if args.holdout else '';folders=[OUT/f'{prefix}{s}-{weight}-{size}' for s in ('before','after')]
        old,new=[json.loads((p/'comparison.json').read_text()) for p in folders]
        assert old['fontSHA256']==sha(baseline) and new['fontSHA256']==sha(fontpath)
        assert old['referenceWeightMode']==new['referenceWeightMode']=='axis'
        assert old['weight']==new['weight']==weight and old['pointSize']==new['pointSize']==size
        assert [r['character'] for r in old['records']]==[r['character'] for r in new['records']]==strings
        for a,b in zip(old['records'],new['records']):
            system=[Image.open(p/r['system']['file']).convert('RGB') for p,r in zip(folders,(a,b))]
            assert ImageChops.difference(*system).getbbox() is None
            own=[Image.open(p/r['tabuna']['file']).convert('RGB') for p,r in zip(folders,(a,b))]
            assert a['tabuna']['advance']==b['tabuna']['advance']
            ch=b['character'];rows.append({'weight':weight,'size':size,'text':ch,'group':'base' if ch in 'SsЅѕ' else 'derivatives' if ch in cfg['affected'] else 'controls',
                'beforeInkIoU':a['inkIoU'],'afterInkIoU':b['inkIoU'],'exactPixels':b['exactMatch'],'differentPixels':b['differentPixels'],
                'exactAdvance':b['exactAdvance'],'complete':b['completeMatch'],'ownPixelsUnchanged':ImageChops.difference(*own).getbbox() is None,
                'fallback':a['customFallback'] or a['referenceFallback'] or b['customFallback'] or b['referenceFallback']})
def stats(rs):
    return {'total':len(rs),'improved':sum(r['afterInkIoU']>r['beforeInkIoU'] for r in rs),'worse':sum(r['afterInkIoU']<r['beforeInkIoU'] for r in rs),
            'unchanged':sum(r['afterInkIoU']==r['beforeInkIoU'] for r in rs),'exactPixels':sum(r['exactPixels'] for r in rs),'exactAdvance':sum(r['exactAdvance'] for r in rs),
            'complete':sum(r['complete'] for r in rs),'ownPixelsUnchanged':sum(r['ownPixelsUnchanged'] for r in rs),'fallbacks':sum(r['fallback'] for r in rs),
            'beforeMeanInkIoU':sum(r['beforeInkIoU'] for r in rs)/len(rs) if rs else None,'afterMeanInkIoU':sum(r['afterInkIoU'] for r in rs)/len(rs) if rs else None}
before=TTFont(baseline);after=TTFont(fontpath)
def advance_model(font,name):
    model={}
    for v in font['gvar'].variations.get(name,[]):
        key=tuple((axis,tuple(support)) for axis,support in sorted(v.axes.items()));left,right=v.coordinates[-4:-2]
        delta=(right[0] if right is not None else 0)-(left[0] if left is not None else 0);model[key]=model.get(key,0)+delta
    return {k:v for k,v in model.items() if v}
assert before.getGlyphOrder()==after.getGlyphOrder()
for name in before.getGlyphOrder():
    assert before['hmtx'][name][0]==after['hmtx'][name][0] and advance_model(before,name)==advance_model(after,name),name
changed_gvar=[n for n in before.getGlyphOrder() if before['gvar'].variations[n]!=after['gvar'].variations[n]]
assert changed_gvar==['S','s','uni0405','uni0455'],changed_gvar
tables=['hmtx','avar','GPOS','GSUB','GDEF','MVAR','fvar','STAT']
for tag in tables:assert before[tag].compile(before)==after[tag].compile(after),tag
report={'fontSHA256':sha(fontpath),'beforeFontSHA256':sha(baseline),'holdout':args.holdout,'allReferencesIdentical':True,'allAdvanceModelsIdentical':True,
        'unchangedTables':tables,'changedGvarGlyphs':changed_gvar,'all':stats(rows),'groups':{g:stats([r for r in rows if r['group']==g]) for g in ('base','derivatives','controls')},
        'baseByWeight':{ch:{str(w):stats([r for r in rows if r['weight']==w and r['text']==ch]) for w in weights} for ch in 'SsЅѕ'},
        'regressions':[r for r in rows if r['afterInkIoU']<r['beforeInkIoU']],'rows':rows}
(OUT/('holdout-results.json' if args.holdout else 'results.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('rows','regressions')},ensure_ascii=False,indent=2))
if not args.holdout:
    sheet=Image.new('RGB',(1200,1070),'white');draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=18)
    for col,title in enumerate(('BEFORE / 0.820','CURRENT / 0.830','SYSTEM REFERENCE')):draw.text((col*400+25,20),title,font=font,fill='#444444')
    for row,(ch,w) in enumerate((('S',400),('s',100),('s',900))):
        ds=[next(r for r in json.loads((OUT/f'{stage}-{w}-128/comparison.json').read_text())['records'] if r['character']==ch) for stage in ('before','after')]
        paths=[OUT/f'before-{w}-128'/ds[0]['tabuna']['file'],OUT/f'after-{w}-128'/ds[1]['tabuna']['file'],OUT/f'after-{w}-128'/ds[1]['system']['file']]
        ims=[Image.open(p).convert('RGB') for p in paths];boxes=[ImageOps.invert(im).getbbox() for im in ims]
        box=(min(b[0] for b in boxes)-8,min(b[1] for b in boxes)-8,max(b[2] for b in boxes)+8,max(b[3] for b in boxes)+8)
        for col,im in enumerate(ims):
            crop=im.crop(box);sheet.paste(crop,(col*400+(400-crop.width)//2,65+row*315))
        draw.text((25,350+row*315),f'{ch} / {w} / 128 pt / native 2x',font=font,fill='#555555')
    draw.text((25,1030),'Same origin and baseline; no registration or error tolerance.',font=font,fill='#444444');sheet.save(OUT/'progress.png')
