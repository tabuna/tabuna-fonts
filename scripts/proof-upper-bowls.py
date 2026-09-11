#!/usr/bin/env python3
"""Before/after native verification for the three-weight Cyrillic bowl calibration."""
from pathlib import Path
from PIL import Image,ImageOps,ImageChops,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'proofs/upper-bowls'
sha=hashlib.sha256((ROOT/'dist/TabunaSansVariable.ttf').read_bytes()).hexdigest()
rows=[]
for weight in (100,400,900):
    for size in (16,32,64,128):
        before=json.loads((folder/f'before-{weight}-{size}/comparison.json').read_text())
        after=json.loads((folder/f'after-{weight}-{size}/comparison.json').read_text())
        assert after['fontSHA256']==sha
        assert before['weight']==after['weight']==weight
        assert before['pointSize']==after['pointSize']==size
        for a,b in zip(before['records'],after['records']):
            assert a['character']==b['character']
            aa=Image.open(folder/f'before-{weight}-{size}'/a['system']['file']).convert('RGB')
            bb=Image.open(folder/f'after-{weight}-{size}'/b['system']['file']).convert('RGB')
            assert ImageChops.difference(aa,bb).getbbox() is None
            rows.append({'weight':weight,'size':size,'character':b['character'],
                         'beforeInkIoU':a['inkIoU'],'afterInkIoU':b['inkIoU'],
                         'beforeAdvanceDifference':a['advanceDifference'],'advanceDifference':b['advanceDifference'],
                         'differentPixels':b['differentPixels'],'exactAdvance':b['exactAdvance'],
                         'exactPixels':b['exactMatch'],'completeMatch':b['completeMatch']})
byWeight={}
for weight in (100,400,900):
    selected=[r for r in rows if r['weight']==weight]
    byWeight[str(weight)]={'total':len(selected),'exactPixels':sum(r['exactPixels'] for r in selected),
                          'complete':sum(r['completeMatch'] for r in selected),
                          'exactAdvance':sum(r['exactAdvance'] for r in selected),
                          'beforeMeanInkIoU':sum(r['beforeInkIoU'] for r in selected)/len(selected),
                          'afterMeanInkIoU':sum(r['afterInkIoU'] for r in selected)/len(selected)}
report={'fontSHA256':sha,'scope':'3 uppercase bowl glyphs, three weights, four native sizes; no full-font or browser acceptance',
        'allReferencesIdentical':True,'byWeight':byWeight,'total':len(rows),'rows':rows}
(folder/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
sheet=Image.new('RGB',(1200,900),'white');draw=ImageDraw.Draw(sheet);label=ImageFont.load_default(size=19)
for col,title in enumerate(('BEFORE / 0.640','CURRENT / 0.650','SYSTEM REFERENCE')):
    draw.text((col*400+25,22),title,font=label,fill='#444444')
for row,weight in enumerate((100,400,900)):
    paths=[folder/f'before-{weight}-128/0420-tabuna.png',folder/f'after-{weight}-128/0420-tabuna.png',folder/f'after-{weight}-128/0420-system.png']
    images=[Image.open(p).convert('RGB') for p in paths];boxes=[ImageOps.invert(im.convert('L')).getbbox() for im in images]
    box=(min(b[0] for b in boxes)-8,min(b[1] for b in boxes)-8,max(b[2] for b in boxes)+8,max(b[3] for b in boxes)+8)
    for col,im in enumerate(images):
        crop=im.crop(box);sheet.paste(crop,(col*400+(400-crop.width)//2,65+row*265))
    draw.text((25,290+row*265),f'U+0420 / weight {weight} / 128 pt / native 2x',font=label,fill='#555555')
draw.text((25,866),'Measured geometry and spacing; remaining errors are reported separately.',font=label,fill='#444444')
sheet.save(folder/'progress.png')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
