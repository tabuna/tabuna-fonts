"""Infinity: tangent lobes joined at two crossings, with teardrop counters."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from bezier import tangent_arc,unit
from parameters import at_location


def lobe(q,upper,lower,counter=False):
 points=[upper,(q['top_x'],q['top']),(q['left'],q['axis']),(q['bottom_x'],q['bottom']),lower]
 tangents=[unit(-1,q['upper_slope']),(-1,0),(0,-1),(1,0),unit(1,q['lower_slope'])]
 return points,[tangent_arc(points[i],points[i+1],tangents[i],tangents[i+1],q['handles'][i],bounded=True) for i in range(4)]


def construction(p):
 d=Drawing();u=p['upper'];b=p['lower'];lp,ls=lobe(p['left'],u,b);rp,rs=lobe(p['right'],(1-u[0],u[1]),(1-b[0],b[1]));ref=lambda v:(1-v[0],v[1]);d.outline(u,[*ls,*[tuple(ref(v) for v in (rs[i][1],rs[i][0],rp[i])) for i in [3,2,1,0]]])
 for side in ['left','right']:
  q=p['counters'][side];tip=(q['tip_x'],q['tip_y']);pts,segs=lobe(q,tip,tip);hole=Drawing();hole.outline(tip,segs,counter=True);hole.replay(d.pen,(-1,0,0,1,1,0) if side=='right' else (1,0,0,1,0,0))
 return d

@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/infinity-ribbon.json').read_text())['weights']
def apply(glyph,key,design):
 if key!='infinity':return
 p=at_location(load(),design);l,b,r,t=p['bounds'];glyph.clearContours();construction(p).replay(glyph.getPen(),(r-l,0,0,t-b,l,b))
