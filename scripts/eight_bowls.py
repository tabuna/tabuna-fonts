"""Eight: shared tangent lobes in a rotated frame, with oval counters."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from infinity_ribbon import lobe
from rounds import contour
from parameters import at_location


def construction(p):
 d=Drawing();u=p['upper'];b=p['lower'];lp,ls=lobe(p['left'],u,b);rp,rs=lobe(p['right'],(1-u[0],u[1]),(1-b[0],b[1]));ref=lambda v:(1-v[0],v[1])
 d.outline(u,[*ls,*[tuple(ref(v) for v in (rs[i][1],rs[i][0],rp[i])) for i in [3,2,1,0]]])
 for q in p['counters']:contour(q['bounds'],q['handles'],counter=True).replay(d.pen)
 return d

@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/eight-bowls.json').read_text())['weights']
def apply(glyph,key,design):
 if key!='eight':return
 p=at_location(load(),design);l,b,r,t=p['bounds'];glyph.clearContours();construction(p).replay(glyph.getPen(),(0,t-b,-(r-l),0,r,b))
