#!/usr/bin/env python3
"""Compare equal-size, equal-origin native renders without registration."""
from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image, ImageChops, ImageOps

parser=argparse.ArgumentParser()
parser.add_argument('directory',type=Path)
args=parser.parse_args();directory=args.directory
settings=json.loads((directory/'render-settings.json').read_text())
self_a,self_b=[Image.open(directory/p).convert('RGB') for p in settings['selfTest']]
assert ImageChops.difference(self_a,self_b).getbbox() is None,'Renderer self-test: identical inputs produced different pixels'
rows=[]
for record in settings['records']:
    own=Image.open(directory/record['tabuna']['file']).convert('L')
    ref=Image.open(directory/record['system']['file']).convert('L')
    assert own.size==ref.size
    difference=ImageChops.difference(own,ref)
    own_ink=ImageOps.invert(own);ref_ink=ImageOps.invert(ref)
    common=ImageChops.darker(own_ink,ref_ink)
    union_ink=ImageChops.lighter(own_ink,ref_ink)
    total=own.width*own.height
    changed=total-difference.histogram()[0]
    active_count=total-union_ink.histogram()[0]
    # Ink error is normalized by the actual union of the two ink masks,
    # not by the large white background, which would inflate similarity.
    def ink_sum(img):return sum(value*count for value,count in enumerate(img.histogram()))
    union=ink_sum(union_ink);intersection=ink_sum(common);error=ink_sum(difference)
    soft_iou=intersection/union if union else 1
    diffname=record.get('id',record['codepoint'][2:])+'-diff.png'
    own_only=ImageChops.subtract(own_ink,common);ref_only=ImageChops.subtract(ref_ink,common)
    base=ImageOps.invert(common)
    overlay=Image.merge('RGB',(
        ImageChops.subtract(base,ref_only),
        ImageChops.subtract(ImageChops.subtract(base,own_only),ref_only.point(lambda x:round(x*.3))),
        ImageChops.subtract(base,ref_only.point(lambda x:round(x*.7)))))
    overlay.save(directory/diffname)
    exact_advance=record['tabuna']['advance']==record['system']['advance']
    custom_fallback=any(n!=settings['customPostScriptName'] for n in record['tabuna']['renderedFonts'])
    reference_fallback=any(n!=settings['systemPostScriptName'] for n in record['system']['renderedFonts'])
    rows.append({**record,'difference':diffname,'exactMatch':changed==0,'differentPixels':changed,
                 'exactAdvance':exact_advance,
                 'completeMatch':changed==0 and exact_advance and not custom_fallback and not reference_fallback,
                 'customFallback':custom_fallback,
                 'inkUnionPixels':active_count,'inkIoU':round(soft_iou,6),
                 'normalizedInkError':round(error/union,6) if union else 0,
                 'advanceDifference':round(record['tabuna']['advance']-record['system']['advance'],6),
                 'referenceFallback':reference_fallback})
report={k:v for k,v in settings.items() if k!='records'}
report.update({'exactMatches':sum(r['exactMatch'] for r in rows),'total':len(rows),
               'completeMatches':sum(r['completeMatch'] for r in rows),
               'rendererSelfTest':'pass: the same system glyph rendered twice is pixel-identical',
               'meanInkIoU':round(sum(r['inkIoU'] for r in rows)/len(rows),6),
               'legend':f"Black: shared ink. Magenta: {settings['customPostScriptName']}-only ink. Green: system-only ink.",
               'records':rows})
(directory/'comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['total','exactMatches','meanInkIoU','systemPostScriptName']},ensure_ascii=False,indent=2))
