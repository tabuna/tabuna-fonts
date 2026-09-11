#!/usr/bin/env python3
"""Strict before/after proof for two original lower-case e glyphs and 40 controls."""
from pathlib import Path
from PIL import Image,ImageOps,ImageChops,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'proofs/lower-e'
sha=hashlib.sha256((ROOT/'dist/TabunaSansVariable.ttf').read_bytes()).hexdigest()
base_sha=hashlib.sha256((ROOT/'references/lower-e-baseline/TabunaSans-before.ttf').read_bytes()).hexdigest()
rows=[]
for weight in (100,400,900):
    for size in (16,32,64,128):
        before=json.loads((folder/f'before-{weight}-{size}/comparison.json').read_text())
        after=json.loads((folder/f'after-{weight}-{size}/comparison.json').read_text())
        assert after['fontSHA256']==sha and before['fontSHA256']==base_sha
        assert before['weight']==after['weight']==weight
        assert before['referenceWeightMode']==after['referenceWeightMode']=='axis'
        assert before['pointSize']==after['pointSize']==size
        assert [r['character'] for r in before['records']]==[r['character'] for r in after['records']]==list('eеaаnhmIHEFLЕІПпШшЦцЩщТтНнЬьЪъЫыPРDBВвoOоО')
        for a,b in zip(before['records'],after['records']):
            paths=[folder/f'{stage}-{weight}-{size}'/r['system']['file'] for stage,r in [('before',a),('after',b)]]
            images=[Image.open(p).convert('RGB') for p in paths]
            assert ImageChops.difference(*images).getbbox() is None
            own=[Image.open(folder/f'{stage}-{weight}-{size}'/r['tabuna']['file']).convert('RGB') for stage,r in [('before',a),('after',b)]]
            rows.append({'weight':weight,'size':size,'character':b['character'],
                         'beforeInkIoU':a['inkIoU'],'afterInkIoU':b['inkIoU'],
                         'beforeAdvanceDifference':a['advanceDifference'],'advanceDifference':b['advanceDifference'],
                         'differentPixels':b['differentPixels'],'exactAdvance':b['exactAdvance'],
                         'exactPixels':b['exactMatch'],'completeMatch':b['completeMatch'],
                         'ownPixelsUnchanged':ImageChops.difference(*own).getbbox() is None})
def stats(selected):
    return {'total':len(selected),'exactPixels':sum(r['exactPixels'] for r in selected),'complete':sum(r['completeMatch'] for r in selected),
            'exactAdvance':sum(r['exactAdvance'] for r in selected),'ownPixelsUnchanged':sum(r['ownPixelsUnchanged'] for r in selected),
            'improved':sum(r['afterInkIoU']>r['beforeInkIoU'] for r in selected),
            'unchanged':sum(r['afterInkIoU']==r['beforeInkIoU'] for r in selected),
            'worse':sum(r['afterInkIoU']<r['beforeInkIoU'] for r in selected),
            'beforeMeanInkIoU':sum(r['beforeInkIoU'] for r in selected)/len(selected),
            'afterMeanInkIoU':sum(r['afterInkIoU'] for r in selected)/len(selected)}
report={'fontSHA256':sha,'beforeFontSHA256':base_sha,'scope':'2 original lower-case e glyphs and 40 controls, 3 weights, 4 native sizes; no full-font or browser acceptance',
        'allReferencesIdentical':True,'total':len(rows),
        'newGlyphsByWeight':{str(w):stats([r for r in rows if r['weight']==w and r['character'] in 'eе']) for w in (100,400,900)},
        'controls':stats([r for r in rows if r['character'] not in 'eе']),
        'regular':stats([r for r in rows if r['weight']==400]),'rows':rows}
(folder/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
sheet=Image.new('RGB',(1200,900),'white');draw=ImageDraw.Draw(sheet);label=ImageFont.load_default(size=19)
for col,title in enumerate(('BEFORE / 0.730','CURRENT / 0.740','SYSTEM REFERENCE')):
    draw.text((col*400+25,22),title,font=label,fill='#444444')
for row,weight in enumerate((100,400,900)):
    paths=[folder/f'before-{weight}-128/0065-tabuna.png',folder/f'after-{weight}-128/0065-tabuna.png',folder/f'after-{weight}-128/0065-system.png']
    images=[Image.open(p).convert('RGB') for p in paths];boxes=[ImageOps.invert(im.convert('L')).getbbox() for im in images]
    box=(min(b[0] for b in boxes)-8,min(b[1] for b in boxes)-8,max(b[2] for b in boxes)+8,max(b[3] for b in boxes)+8)
    for col,im in enumerate(images):
        crop=im.crop(box);sheet.paste(crop,(col*400+(400-crop.width)//2,65+row*265))
    draw.text((25,290+row*265),f'e / weight {weight} / 128 pt / native 2x',font=label,fill='#555555')
draw.text((25,866),'Same origin and baseline; no image registration or error tolerance.',font=label,fill='#444444')
sheet.save(folder/'progress.png')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
