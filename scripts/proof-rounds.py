#!/usr/bin/env python3
"""Summarize native before/after round-glyph renders without score inflation."""
from pathlib import Path
from PIL import Image,ImageOps,ImageChops,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'proofs/rounds'
font_hash=hashlib.sha256((ROOT/'dist/TabunaSansVariable.ttf').read_bytes()).hexdigest()
rows=[]
for size in (16,32,64,128):
    before=json.loads((folder/f'before-{size}/comparison.json').read_text())
    after=json.loads((folder/f'after-{size}/comparison.json').read_text())
    assert after['fontSHA256']==font_hash
    assert before['pointSize']==after['pointSize']
    for old,new in zip(before['records'],after['records']):
        assert old['character']==new['character']
        a=Image.open(folder/f'before-{size}'/old['system']['file'])
        b=Image.open(folder/f'after-{size}'/new['system']['file'])
        assert ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox() is None
        rows.append({'size':size,'character':new['character'],'beforeInkIoU':old['inkIoU'],
                     'afterInkIoU':new['inkIoU'],'differentPixels':new['differentPixels'],
                     'exactAdvance':new['exactAdvance'],'completeMatch':new['completeMatch']})
report={'fontSHA256':font_hash,'scope':'Four Regular round glyphs at four native sizes; not full-font acceptance',
        'allReferencesIdentical':True,'rows':rows,
        'improvedCount':sum(r['afterInkIoU']>r['beforeInkIoU'] for r in rows),
        'completeCount':sum(r['completeMatch'] for r in rows),'total':len(rows)}
(folder/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
# Identical cropping coordinates within each comparison row; no registration.
sheet=Image.new('RGB',(900,590),'white');draw=ImageDraw.Draw(sheet)
label=ImageFont.load_default(size=18)
for col,title in enumerate(('BEFORE / 0.600','CURRENT / 0.610','SYSTEM REFERENCE')):
    draw.text((col*300+25,22),title,font=label,fill='#444444')
for row,code in enumerate(('006F','041E')):
    paths=[folder/'before-128'/f'{code}-tabuna.png',folder/'after-128'/f'{code}-tabuna.png',folder/'after-128'/f'{code}-system.png']
    images=[Image.open(p).convert('RGB') for p in paths]
    boxes=[ImageOps.invert(im.convert('L')).getbbox() for im in images]
    box=(min(b[0] for b in boxes)-8,min(b[1] for b in boxes)-8,max(b[2] for b in boxes)+8,max(b[3] for b in boxes)+8)
    for col,im in enumerate(images):
        crop=im.crop(box);sheet.paste(crop,(col*300+int((300-crop.width)/2),65+row*245))
    draw.text((25,265+row*245),f'U+{code} / 128 pt / native 2x',font=label,fill='#555555')
draw.text((25,553),'Widths match. Nonzero pixel differences remain.',font=label,fill='#444444')
sheet.save(folder/'progress.png')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
