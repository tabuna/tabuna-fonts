"""Four: a cubic diagonal band, a stepped upright, and a crossbar."""
import json
from pathlib import Path
from functools import lru_cache
import numpy as np
from geometry import Drawing
from parameters import at_location


def value(c,y):return float(np.polyval(c,y))


def crossing(c,x,lo,hi):
    q=list(c);q[-1]-=x
    roots=[float(r.real) for r in np.roots(q) if abs(r.imag)<1e-7 and lo-1e-6<=r.real<=hi+1e-6]
    if not roots:raise ValueError('Diagonal does not meet its construction boundary')
    return max(lo,min(hi,roots[0]))


def curve(c,a,b,top):
    x0,x1=value(c,a),value(c,b);d=np.polyder(c);h=(b-a)/3
    return ((x0+value(d,a)*h,(a+h)*top),(x1-value(d,b)*h,(b-h)*top),(x1,b*top))


def construction(p):
    d=Drawing();top=p['top'];left,bar_right,bar_bottom,bar_top=p['bar'];lower,upper=p['stems'];o,i=p['outer'],p['inner'];floor=bar_top/top
    root=max(floor,crossing(o,left,0,1));join=crossing(i,upper[0],floor,1)
    d.outline((left,bar_top),[(value(o,root),root*top),curve(o,root,1,top),(upper[0],top),(upper[0],join*top),curve(i,join,floor,top)])
    d.rect(left,bar_bottom,bar_right-left,bar_top-bar_bottom)
    d.rect(lower[0],0,lower[1]-lower[0],bar_top)
    d.rect(upper[0],bar_bottom,upper[1]-upper[0],top-bar_bottom)
    return d


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/four-frame.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='four':return
    glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
