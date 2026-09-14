"""Arithmetic signs as axis-aligned rectangles and a slanted band."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from parameters import at_location


def construction(p):
    d=Drawing()
    if 'bracket_direction' in p:
        stem,lower,upper=p['bars']
        left=lower['x']-lower['width']/2;right=lower['x']+lower['width']/2
        bottom=lower['y']-lower['height']/2;floor=lower['y']+lower['height']/2
        top=upper['y']+upper['height']/2;ceiling=upper['y']-upper['height']/2
        inner=left+stem['width']
        points=[(left,bottom),(left,top),(right,top),(right,ceiling),
                (inner,ceiling),(inner,floor),(right,floor),(right,bottom)]
        if p['bracket_direction']<0:points=[(left+right-x,y) for x,y in points]
        d.polygon(points)
        return d
    for bar in p['bars']:
        x,y,w,h=(bar[k] for k in ['x','y','width','height'])
        d.rect(x-w/2,y-h/2,w,h)
    for band in p['slashes']:
        a,b,w,lo,hi=(band[k] for k in ['slope','intercept','width','bottom','top'])
        wl=w+band.get('width_slope',0)*lo;wh=w+band.get('width_slope',0)*hi
        d.polygon([(a*lo+b-wl/2,lo),(a*hi+b-wh/2,hi),
                   (a*hi+b+wh/2,hi),(a*lo+b+wl/2,lo)])
    for bounds in p.get('ovals',[]):d.ellipse(*bounds)
    return d


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/math-bands.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    data=load().get(key)
    if data is not None:
        glyph.clearContours();construction(at_location(data,design)).replay(glyph.getPen())
