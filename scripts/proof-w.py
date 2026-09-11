#!/usr/bin/env python3
"""Strict proof for the W-only composite contour candidate."""
from pathlib import Path
from PIL import Image, ImageChops
from fontTools.ttLib import TTFont
import json, hashlib, argparse
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/'references/mw-baseline'; OUT=ROOT/'proofs/mw'
ap=argparse.ArgumentParser(); ap.add_argument('--holdout',action='store_true'); args=ap.parse_args()
cfg=json.loads((BASE/('holdout.json' if args.holdout else 'validation.json')).read_text()); strings=cfg['strings']
weights=(200,300,500,600,700,800) if args.holdout else (100,400,900); sizes=(14,20,24,48,96) if args.holdout else (16,32,64,128)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest(); fontpath=ROOT/'dist/TabunaSansVariable.ttf'; baseline=BASE/'TabunaSans-before.ttf'; rows=[]
for weight in weights:
 for size in sizes:
  if args.holdout:
   folders=[OUT/f'w-only-holdout-base-{weight}-{size}',OUT/f'w-only-holdout-0.830-{weight}-{size}']
  else:
   folders=[OUT/f'w-only-base-{weight}-{size}',OUT/f'w-only-0.830-{weight}-{size}']
  old,new=[json.loads((p/'comparison.json').read_text()) for p in folders]
  assert old['fontSHA256']==sha(baseline) and new['fontSHA256']==sha(fontpath)
  assert old['referenceWeightMode']==new['referenceWeightMode']=='axis' and old['weight']==new['weight']==weight and old['pointSize']==new['pointSize']==size
  assert [r['character'] for r in old['records']]==[r['character'] for r in new['records']]==strings
  for a,b in zip(old['records'],new['records']):
   assert ImageChops.difference(Image.open(folders[0]/a['system']['file']).convert('RGB'),Image.open(folders[1]/b['system']['file']).convert('RGB')).getbbox() is None
   own=ImageChops.difference(Image.open(folders[0]/a['tabuna']['file']).convert('RGB'),Image.open(folders[1]/b['tabuna']['file']).convert('RGB')).getbbox() is None
   assert a['tabuna']['advance']==b['tabuna']['advance']
   rows.append({'weight':weight,'size':size,'text':b['character'],'group':'target' if b['character']=='W' else 'controls','beforeInkIoU':a['inkIoU'],'afterInkIoU':b['inkIoU'],'exactPixels':b['exactMatch'],'exactAdvance':b['exactAdvance'],'complete':b['completeMatch'],'ownPixelsUnchanged':own,'fallback':a['customFallback'] or a['referenceFallback'] or b['customFallback'] or b['referenceFallback']})
def stats(rs):
 return {'total':len(rs),'improved':sum(r['afterInkIoU']>r['beforeInkIoU'] for r in rs),'worse':sum(r['afterInkIoU']<r['beforeInkIoU'] for r in rs),'unchanged':sum(r['afterInkIoU']==r['beforeInkIoU'] for r in rs),'exactPixels':sum(r['exactPixels'] for r in rs),'exactAdvance':sum(r['exactAdvance'] for r in rs),'complete':sum(r['complete'] for r in rs),'ownPixelsUnchanged':sum(r['ownPixelsUnchanged'] for r in rs),'fallbacks':sum(r['fallback'] for r in rs),'beforeMeanInkIoU':sum(r['beforeInkIoU'] for r in rs)/len(rs) if rs else None,'afterMeanInkIoU':sum(r['afterInkIoU'] for r in rs)/len(rs) if rs else None}
before=TTFont(baseline); after=TTFont(fontpath)
def model(font,name):
 out={}
 for v in font['gvar'].variations.get(name,[]):
  key=tuple((axis,tuple(support)) for axis,support in sorted(v.axes.items())); left,right=v.coordinates[-4:-2]; out[key]=out.get(key,0)+(right[0] if right is not None else 0)-(left[0] if left is not None else 0)
 return {k:v for k,v in out.items() if v}
for name in before.getGlyphOrder(): assert before['hmtx'][name][0]==after['hmtx'][name][0] and model(before,name)==model(after,name),name
changed=[n for n in before.getGlyphOrder() if before['gvar'].variations[n]!=after['gvar'].variations[n]]; assert changed==['W'],changed
report={'fontSHA256':sha(fontpath),'beforeFontSHA256':sha(baseline),'holdout':args.holdout,'allReferencesIdentical':True,'allAdvanceModelsIdentical':True,'changedGvarGlyphs':changed,'all':stats(rows),'groups':{g:stats([r for r in rows if r['group']==g]) for g in ('target','controls')},'regressions':[r for r in rows if r['afterInkIoU']<r['beforeInkIoU']],'rows':rows}
(OUT/('w-only-holdout-results.json' if args.holdout else 'w-only-results.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n'); print(json.dumps({k:v for k,v in report.items() if k not in ('rows','regressions')},ensure_ascii=False,indent=2))
