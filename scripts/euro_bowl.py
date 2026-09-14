"""Euro from the shared open-round bowl and two tapered crossbars."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from open_rounds import contours
from parameters import at_location


def construction(p):
    d=Drawing();bowl=Drawing()
    for start,segments,counter in contours(p['parameters'],p['handles']):bowl.outline(start,segments,counter)
    bowl.replay(d.pen,(1-p['left'],0,0,1,p['left'],0))
    for bar in p['bars']:
        y,h,r,slant=(bar[k] for k in ['y','height','right','slant'])
        d.polygon([(0,y-h/2),(r-slant*h/2,y-h/2),(r+slant*h/2,y+h/2),(0,y+h/2)])
    l,b,r,t=p['bounds'];out=Drawing();d.replay(out.pen,(r-l,0,0,t-b,l,b));return out


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/euro-bowl.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='Euro' and key!='uni20AC':return
    glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
