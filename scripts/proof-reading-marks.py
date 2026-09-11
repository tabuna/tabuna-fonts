#!/usr/bin/env python3
"""Native pixel, normalization and advance-model proof for reading diacritics."""
from pathlib import Path
from PIL import Image,ImageChops,ImageOps,ImageDraw,ImageFont
from fontTools.ttLib import TTFont
import json,hashlib,unicodedata as ud,argparse
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/reading-marks-baseline';OUT=ROOT/'proofs/reading-marks'
parser=argparse.ArgumentParser();parser.add_argument('--holdout',action='store_true');args=parser.parse_args()
cfg=json.loads((BASE/'validation.json').read_text());strings=cfg['composed']+cfg['unencoded'] if args.holdout else cfg['strings']
weights=(200,300,500,600,700,800) if args.holdout else (100,400,900);sizes=(14,20,24,48,96) if args.holdout else (16,32,64,128)
fontpath=ROOT/'dist/TabunaSansVariable.ttf';baseline=BASE/'TabunaSans-before.ttf';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];canonical=[]
for weight in weights:
    for size in sizes:
        prefix='holdout-' if args.holdout else ''
        folders=[OUT/f'{prefix}{stage}-{weight}-{size}' for stage in ('before','after')]
        old,new=[json.loads((p/'comparison.json').read_text()) for p in folders]
        assert old['fontSHA256']==sha(baseline) and new['fontSHA256']==sha(fontpath)
        assert old['referenceWeightMode']==new['referenceWeightMode']=='axis'
        assert old['weight']==new['weight']==weight and old['pointSize']==new['pointSize']==size
        assert [r['character'] for r in old['records']]==[r['character'] for r in new['records']]==strings
        for a,b in zip(old['records'],new['records']):
            system=[Image.open(p/r['system']['file']).convert('RGB') for p,r in zip(folders,(a,b))]
            assert ImageChops.difference(*system).getbbox() is None,(b['character'],'Reference changed')
            own=[Image.open(p/r['tabuna']['file']).convert('RGB') for p,r in zip(folders,(a,b))]
            ch=b['character'];group=next((g for g in ('composed','decomposed','unencoded','controls') if ch in cfg[g]))
            rows.append({'weight':weight,'size':size,'text':ch,'group':group,'beforeInkIoU':a['inkIoU'],'afterInkIoU':b['inkIoU'],
                         'beforeDifferentPixels':a['differentPixels'],'differentPixels':b['differentPixels'],'exactPixels':b['exactMatch'],'exactAdvance':b['exactAdvance'],
                         'beforeAdvance':a['tabuna']['advance'],'afterAdvance':b['tabuna']['advance'],'advanceUnchanged':a['tabuna']['advance']==b['tabuna']['advance'],
                         'complete':b['completeMatch'],'ownPixelsUnchanged':ImageChops.difference(*own).getbbox() is None,
                         'fallback':a['customFallback'] or a['referenceFallback'] or b['customFallback'] or b['referenceFallback']})
        if not args.holdout:
            records={r['character']:r for r in new['records']}
            for c in cfg['composed']:
                a,b=records[c],records[ud.normalize('NFD',c)];equal={}
                for side in ('tabuna','system'):
                    images=[Image.open(folders[1]/r[side]['file']).convert('RGB') for r in (a,b)]
                    equal[side+'Pixels']=ImageChops.difference(*images).getbbox() is None
                    equal[side+'Advance']=a[side]['advance']==b[side]['advance']
                    equal[side]=equal[side+'Pixels'] and equal[side+'Advance']
                canonical.append({'weight':weight,'size':size,'text':c,**equal})
def stats(rs):
    return {'total':len(rs),'improved':sum(r['afterInkIoU']>r['beforeInkIoU'] for r in rs),'worse':sum(r['afterInkIoU']<r['beforeInkIoU'] for r in rs),
            'unchanged':sum(r['afterInkIoU']==r['beforeInkIoU'] for r in rs),'exactPixels':sum(r['exactPixels'] for r in rs),'exactAdvance':sum(r['exactAdvance'] for r in rs),
            'complete':sum(r['complete'] for r in rs),'ownPixelsUnchanged':sum(r['ownPixelsUnchanged'] for r in rs),'advanceChanges':sum(not r['advanceUnchanged'] for r in rs),'fallbacks':sum(r['fallback'] for r in rs),
            'beforeMeanInkIoU':sum(r['beforeInkIoU'] for r in rs)/len(rs) if rs else None,'afterMeanInkIoU':sum(r['afterInkIoU'] for r in rs)/len(rs) if rs else None}
before=TTFont(baseline);after=TTFont(fontpath)
def advance_model(font,name):
    model={}
    for v in font['gvar'].variations.get(name,[]):
        key=tuple((axis,tuple(support)) for axis,support in sorted(v.axes.items()));left,right=v.coordinates[-4:-2]
        delta=(right[0] if right is not None else 0)-(left[0] if left is not None else 0);model[key]=model.get(key,0)+delta
    return {k:v for k,v in model.items() if v}
for name in before.getGlyphOrder():
    assert before['hmtx'][name][0]==after['hmtx'][name][0],name
    assert advance_model(before,name)==advance_model(after,name),(name,'Advance field changed')
added=sorted(set(after.getGlyphOrder())-set(before.getGlyphOrder()))
for name in added:assert after['hmtx'][name][0]==0 and not advance_model(after,name)
report={'fontSHA256':sha(fontpath),'beforeFontSHA256':sha(baseline),'holdout':args.holdout,'allReferencePixelsIdentical':True,
        'allExistingAdvanceModelsIdentical':True,'addedZeroAdvanceGlyphs':added,'all':stats(rows),
        'groups':{g:stats([r for r in rows if r['group']==g]) for g in ('composed','decomposed','unencoded','controls')},
        'byWeight':{str(w):stats([r for r in rows if r['weight']==w and r['group']=='composed']) for w in weights},
        'canonical':{'total':len(canonical),'ownEqual':sum(r['tabuna'] for r in canonical),'systemEqual':sum(r['system'] for r in canonical),
                     'ownPixelsEqual':sum(r['tabunaPixels'] for r in canonical),'systemPixelsEqual':sum(r['systemPixels'] for r in canonical),
                     'ownAdvancesEqual':sum(r['tabunaAdvance'] for r in canonical),'systemAdvancesEqual':sum(r['systemAdvance'] for r in canonical),
                     'misses':[r for r in canonical if not r['tabuna'] or not r['system']]},
        'regressions':[r for r in rows if r['afterInkIoU']<r['beforeInkIoU']],
        'byText':{t:stats([r for r in rows if r['text']==t]) for t in strings if t not in cfg['controls']},'rows':rows}
(OUT/('holdout-results.json' if args.holdout else 'results.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('rows','byText','regressions')},ensure_ascii=False,indent=2))
if not args.holdout:
    sheet=Image.new('RGB',(1500,1020),'white');draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=20)
    for col,title in enumerate(('BEFORE / 0.790','CURRENT / 0.800','SYSTEM REFERENCE')):draw.text((col*500+25,20),title,font=font,fill='#444444')
    before=json.loads((OUT/'before-400-128/comparison.json').read_text());after=json.loads((OUT/'after-400-128/comparison.json').read_text())
    for row,ch in enumerate(('ĝ','й','ģ')):
        a=next(r for r in before['records'] if r['character']==ch);b=next(r for r in after['records'] if r['character']==ch)
        paths=[OUT/'before-400-128'/a['tabuna']['file'],OUT/'after-400-128'/b['tabuna']['file'],OUT/'after-400-128'/b['system']['file']]
        ims=[Image.open(p).convert('RGB') for p in paths];boxes=[ImageOps.invert(im).getbbox() for im in ims]
        box=(min(b[0] for b in boxes)-8,min(b[1] for b in boxes)-8,max(b[2] for b in boxes)+8,max(b[3] for b in boxes)+8)
        for col,im in enumerate(ims):
            crop=im.crop(box);sheet.paste(crop,(col*500+(500-crop.width)//2,65+row*300))
        draw.text((25,330+row*300),f'U+{ord(ch):04X} / 400 / 128 pt / native 2x',font=font,fill='#555555')
    draw.text((25,985),'Same origin and baseline; no registration or error tolerance.',font=font,fill='#444444');sheet.save(OUT/'progress.png')
