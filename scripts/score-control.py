#!/usr/bin/env python3
import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]
GLYPHS='АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюя'
out=R/'build/control-score'; out.mkdir(parents=True,exist_ok=True); rows=[]
for size in (32,64,128):
 d=out/str(size); subprocess.run([str(R/'build/render-pairs'),str(R/'dist/TabunaSansVariable.ttf'),str(d),str(size),GLYPHS,'2','400','axis'],check=True,stdout=subprocess.DEVNULL)
 subprocess.run([str(R/'.venv/bin/python'),str(R/'scripts/compare-pixels.py'),str(d)],check=True,stdout=subprocess.DEVNULL)
 data=json.loads((d/'comparison.json').read_text()); rows.append({'size':size,'total':data['total'],'exactMatches':data['exactMatches'],'meanInkIoU':data['meanInkIoU']})
records=json.loads(((out/'64')/'comparison.json').read_text())['records']
worst=[{'character':r['character'],'inkIoU':r['inkIoU']} for r in sorted(records,key=lambda x:x['inkIoU'])[:8]]
result={'glyphs':len(GLYPHS),'sizes':rows,'meanInkIoU':sum(x['meanInkIoU'] for x in rows)/len(rows),'worst64px':worst}
(R/'build/control-score.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False))
