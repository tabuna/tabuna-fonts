#!/usr/bin/env python3
"""Measure reference dimensions; preserve every authored contour's topology.

Reads the saved native render reports and our own pre-calibration UFOs.
Reference outlines and font files are not read. Re-running requires a fresh
uncalibrated baseline, so the original measurements cannot compound silently.
"""
from pathlib import Path
import hashlib
import json
from ufoLib2 import Font
from fontTools.pens.boundsPen import BoundsPen
from build import name

ROOT=Path(__file__).resolve().parents[1]
BASELINE=ROOT/'references/metrics-baseline'
records={};provenance=[]
for label,size,optical,body in [('text',16,16,524),('display',64,28,506)]:
    path=BASELINE/f'render-{size}.json'
    report=json.loads(path.read_text())
    font=Font.open(BASELINE/f'TabunaSans-400-{optical}.ufo')
    provenance.append({'report':str(path.relative_to(ROOT)),
        'reportSHA256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'reference':report['systemPostScriptName'],'os':report['os'],
        'basisFontSHA256':report['fontSHA256'],'pointSize':size})
    for row in report['records']:
        ch=row['character'];key=name(ch)
        if ch=='I' or row['system']['renderedFonts']!=[report['systemPostScriptName']]:continue
        glyph=font[key]
        if glyph.components:continue
        pen=BoundsPen(font);glyph.draw(pen)
        if not pen.bounds:continue
        x0,y0,x1,y1=[v/2.048 for v in pen.bounds]
        rx,ry,rw,rh=[v*1000/size for v in row['system']['inkBounds']]
        if rw<=0 or rh<=0:continue
        sx=rw/(x1-x0)
        knots=[(y0,ry),(y1,ry+rh)]
        if ch.islower() and y1>=body:
            # The flat x-height is measured from the system x in the same run.
            flat=next(r for r in report['records'] if r['character']=='x')['system']['inkBounds']
            target_body=(flat[1]+flat[3])*1000/size
            if y0<0<y1:knots.append((0,0))
            if y0<body<y1:knots.append((body,target_body))
        records.setdefault(key,{})[label]={'sx':sx,'dx':rx-x0*sx,
            'y':sorted(knots),'baseAdvance':glyph.width/2.048,
            'advance':row['system']['advance']*1000/size,
            'character':ch}
records={k:v for k,v in records.items() if set(v)=={'text','display'}}
result={'method':'Native dimensions and advances; original source control points retained',
    'weight':400,'referenceRuns':provenance,'glyphs':records,
    'scope':'Endpoint calibration at Regular. Weight-dependent proportions and curves still require verification.'}
(ROOT/'sources/metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(f'Measured {len(records)} original glyphs at two optical endpoints.')
