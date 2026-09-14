"""J/j: two tangent cubic arcs per ribbon edge and an independent upright."""
import json,math
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from bezier import tangent_arc
from parameters import at_location
from quadratic_round import contour as round_contour


def edge(q,x):
 a=(x,q['join_y']);b=(q['bottom_x'],q['bottom_y']);c=(q['tip_x'],q['tip_y'])
 tangent=(-math.cos(q['tip_angle']),math.sin(q['tip_angle']))
 return [a,b,c],[tangent_arc(a,b,(0,-1),(-1,0),q['handles'][0],bounded=True),tangent_arc(b,c,(-1,0),tangent,q['handles'][1],bounded=True)]


def construction(p):
 left,right=p['stem'];op,o=edge(p['outer'],right);ip,i=edge(p['inner'],left);d=Drawing()
 d.outline((right,1),[op[0],*o,ip[-1],(i[1][1],i[1][0],ip[1]),(i[0][1],i[0][0],ip[0]),(left,1)])
 return d

@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/j-hooks.json').read_text())['glyphs']

def apply(glyph,key,design):
 if key not in ('J','j','i'):return
 p=at_location(load()[key],design);glyph.clearContours()
 if key=='i':
  l,b,r,t=p['upright'];d=Drawing();d.rect(l,b,r-l,t-b);d.replay(glyph.getPen())
 else:
  l,b,r,t=p['bounds'];construction(p).replay(glyph.getPen(),(r-l,0,0,t-b,l,b))
 if 'dot' in p:round_contour(p['dot']['bounds'],p['dot']['quadrants']).replay(glyph.getPen())
