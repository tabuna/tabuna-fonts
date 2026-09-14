"""Tilde ribbon: three monotone tangent cubic arcs along each edge."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from bezier import tangent_arc,unit
from parameters import at_location


def edge(q):
 points=[(0,q['start']),(q['peak_x'],q['peak_y']),(q['trough_x'],q['trough_y']),(1,q['end'])]
 tangents=[unit(1,q['start_slope']),(1,0),(1,0),unit(1,q['end_slope'])]
 return points,[tangent_arc(points[i],points[i+1],tangents[i],tangents[i+1],q['handles'][i],bounded=True) for i in range(3)]


def construction(p):
 up,u=edge(p['upper']);lp,l=edge(p['lower']);d=Drawing();d.outline(up[0],[*u,lp[-1],*[(l[i][1],l[i][0],lp[i]) for i in [2,1,0]]]);return d

@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/tilde-wave.json').read_text())['weights']
def apply(glyph,key,design):
 if key!='asciitilde':return
 p=at_location(load(),design);l,b,r,t=p['bounds'];glyph.clearContours();construction(p).replay(glyph.getPen(),(r-l,0,0,t-b,l,b))
