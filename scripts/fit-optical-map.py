#!/usr/bin/env python3
"""Fit optical-axis mapping by rendering our I, never by reading system paths.

Integer search operates on the actual F2Dot14 precision of an avar value.
The objective is exact PNG equality; a near match remains a failed match.
"""
from pathlib import Path
import json
import subprocess
from math import ceil
from PIL import Image, ImageChops, ImageOps
from fontTools.ttLib import TTFont
import optical as optics

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/optical-fit';OUT.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'build/TabunaSans-untracked.ttf'
font=TTFont(BASE,recalcTimestamp=False)
if 'trak' in font:del font['trak']

def centroid(image):
    ink=ImageOps.invert(image)
    columns=[sum(ink.crop((x,0,x+1,ink.height)).get_flattened_data()) for x in range(ink.width)]
    return sum(i*v for i,v in enumerate(columns))/sum(columns)

results=[]
shared_map=optics.initial_map()
for size in (18,20,24):
    cache={};directory=OUT/str(size);directory.mkdir(exist_ok=True)
    initial_input=ceil(optics.normalized(size)*16384)
    def evaluate(value,input_value=initial_input):
        key=(input_value,value)
        if key in cache:return cache[key]
        font['avar'].segments['opsz']={**shared_map,input_value/16384:value/16384}
        path=OUT/'candidate.ttf';font.save(path)
        subprocess.run([str(ROOT/'build/render-pairs'),str(path),str(directory),str(size),'I'],
                       stdout=subprocess.DEVNULL,check=True)
        own=Image.open(directory/'0049-tabuna.png').convert('L')
        reference=Image.open(directory/'0049-system.png').convert('L')
        diff=ImageChops.difference(own,reference);hist=diff.histogram()
        result={'value':value,'inputValue':input_value,'differentPixels':own.width*own.height-hist[0],
                'absoluteInkError':sum(i*n for i,n in enumerate(hist)),
                'centroidDifference':centroid(own)-centroid(reference)}
        cache[key]=result
        return result
    lower=round(optics.normalized(optics.TEXT_END)*16384)
    upper=round(optics.normalized(optics.DISPLAY_START)*16384)
    lo,hi=lower,upper
    while hi-lo>1:
        mid=(lo+hi)//2;r=evaluate(mid)
        if r['centroidDifference']>0:lo=mid
        else:hi=mid
    for value in range(max(lower,lo-6),min(upper,hi+6)+1):evaluate(value)
    coarse=min(cache.values(),key=lambda r:(r['absoluteInkError'],r['differentPixels']))
    # Moving a breakpoint slightly above the requested size permits finer
    # effective output coordinates than one F2Dot14 output step alone. Keep
    # every query to the left of its breakpoint so later fits cannot disturb it.
    previous=max(x for x in shared_map if x<optics.normalized(size))
    prev_output=shared_map[previous]*16384
    for input_value in range(initial_input,initial_input+17):
        predicted=prev_output+(coarse['value']-prev_output)*(input_value/16384-previous)/(initial_input/16384-previous)
        for value in range(max(lower,round(predicted)-3),min(upper,round(predicted)+3)+1):
            r=evaluate(value,input_value)
            if r['differentPixels']==0:break
        if r['differentPixels']==0:break
    best=min(cache.values(),key=lambda r:(r['absoluteInkError'],r['differentPixels']))
    results.append({'pointSize':size,'normalizedInput':best['inputValue']/16384,
                    'normalizedOutput':best['value']/16384,**best})
    # Leave a reproducible pair for the winning parameter, not the last probe.
    cache.pop((best['inputValue'],best['value']));evaluate(best['value'],best['inputValue'])
    shared_map[best['inputValue']/16384]=best['value']/16384
    print(size,best,flush=True)
result={'method':'F2Dot14 integer search on native PNGs of our I',
    'axisRange':optics.AXIS_RANGE,
    'records':results,'allPixelExact':all(r['differentPixels']==0 for r in results),
    'note':'This isolates optical mapping for I; it does not prove other glyphs or intermediate sizes match.'}
(ROOT/'sources/optical-map.json').write_text(json.dumps(result,indent=2)+'\n')
