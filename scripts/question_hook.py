"""Question mark: four tangent-directed cubic arcs per edge and an oval dot."""
import json
from pathlib import Path
from functools import lru_cache
from bezier import tangent_arc,unit
from geometry import Drawing
from parameters import at_location


def edge(q,cut,stem):
    pts=[(cut,q['cut_y']),(q['top_x'],q['top_y']),(q['right_x'],q['right_y']),(q['neck_x'],q['neck_y']),(stem,q['stem_y'])]
    tangents=[unit(q['cut_slope'],1),(1,0),(0,-1),unit(-1,-q['neck_slope']),(0,-1)]
    return pts,[tangent_arc(pts[i],pts[i+1],tangents[i],tangents[i+1],q['handles'][i]) for i in range(4)]


def construction(p):
    d=Drawing();op,oc=edge(p['outer'],0,p['stem'][1]);ip,ic=edge(p['inner'],p['cut_x'],p['stem'][0])
    rev=[(ic[i][1],ic[i][0],ip[i]) for i in reversed(range(4))]
    d.outline(op[0],[*oc,(p['stem'][1],0),(p['stem'][0],0),ip[-1],*rev])
    return d


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/question-hook.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='question':return
    p=at_location(load(),design);l,b,r,t=p['bounds'];glyph.clearContours();construction(p).replay(glyph.getPen(),(r-l,0,0,t-b,l,b));d=Drawing();d.ellipse(*p['dot']);d.replay(glyph.getPen())
