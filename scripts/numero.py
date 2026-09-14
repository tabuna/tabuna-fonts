"""Numero from two stems, measured diagonal equations, a shared oval and a bar."""
import json
from pathlib import Path
from functools import lru_cache
from parameters import at_location
from geometry import Drawing
from rounds import contour


def construction(p):
    d=Drawing();n=p['n'];bottom,top=n['bottom'],n['top']
    for left,right in n['stems']:d.rect(left,bottom,right-left,top-bottom)
    a,b=n['diagonal']
    left,right=[sum(stem)/2 for stem in n['stems']]
    def endpoint(edge,x):
        y=min(top,max(bottom,(x-edge[1])/edge[0]))
        return edge[0]*y+edge[1],y
    # End the diagonal inside each stem; keep hidden caps inside the N box.
    d.polygon([endpoint(a,left),endpoint(a,right),endpoint(b,right),endpoint(b,left)])
    ring=p['ring']
    for index,key in enumerate(['outerHandles','innerHandles']):
        contour(ring['bounds'][index],ring[key],index==1).replay(d.pen)
    l,b,r,t=p['bar'];d.rect(l,b,r-l,t-b)
    return d


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/numero.json').read_text())['weights']


def apply(glyph,design):
    glyph.clearContours();glyph.components.clear()
    construction(at_location(load(),design)).replay(glyph.getPen())
