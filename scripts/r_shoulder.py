"""r: upright with three tangent cubic arcs per shoulder edge."""
import json,math,copy
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from bezier import tangent_arc
from parameters import at_location

def edge(p,q):
 a=(p['stem_right'],q['join_y']);b=(q['crown_x'],q['crown_y']);c=(1,q['tip_y'])
 ta=(math.cos(q['join_angle']),math.sin(q['join_angle']));tc=(math.cos(q['tip_angle']),math.sin(q['tip_angle']))
 if 'mid_x' in q:
  m=(q['mid_x'],q['mid_y']);tm=(math.cos(q['mid_angle']),math.sin(q['mid_angle']))
  return [a,m,b,c],[tangent_arc(a,m,ta,tm,q['handles'][0],bounded=True),tangent_arc(m,b,tm,(1,0),q['handles'][1],bounded=True),tangent_arc(b,c,(1,0),tc,q['handles'][2],bounded=True)]
 return [a,b,c],[tangent_arc(a,b,ta,(1,0),q['handles'][0],bounded=True),tangent_arc(b,c,(1,0),tc,q['handles'][1],bounded=True)]

def construction(p):
 inner=copy.deepcopy(p['inner'])
 for key in ['join_y','mid_y','crown_y','tip_y']:
  if key in inner:inner[key]-=p.get('inner_optical_expansion',0)
 op,o=edge(p,p['outer']);ip,i=edge(p,inner);d=Drawing()
 reverse=[(curve[1],curve[0],ip[k]) for k,curve in reversed(list(enumerate(i)))]
 d.outline((0,0),[(0,p['stem_top']),(p['stem_right'],p['stem_top']),op[0],*o,ip[-1],*reverse,(p['stem_right'],0)])
 return d
@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/r-shoulder.json').read_text())['weights']
def apply(glyph,key,design):
 if key!='r':return
 p=at_location(load(),design);l,b,r,t=p['bounds'];glyph.clearContours();glyph.clearComponents();construction(p).replay(glyph.getPen(),(r-l,0,0,t-b,l,b))
