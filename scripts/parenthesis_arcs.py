"""Parenthesis ribbon: two cubic arcs per edge with a common vertical tangent."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from bezier import tangent_arc,unit
from parameters import at_location


def edge(q):
    a=(q['top_x'],1);b=(q['middle_x'],q['middle_y']);c=(q['bottom_x'],0)
    return [a,b,c],[tangent_arc(a,b,unit(-q['top_slope'],-1),(0,-1),q['handles'][0]),tangent_arc(b,c,(0,-1),unit(q['bottom_slope'],-1),q['handles'][1])]


def construction(p):
    d=Drawing();op,o=edge(p['outer']);ip,i=edge(p['inner']);d.outline(op[0],[*o,ip[-1],(i[1][1],i[1][0],ip[1]),(i[0][1],i[0][0],ip[0])]);return d


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/parenthesis-arcs.json').read_text())['glyphs']


def apply(glyph,key,design):
    if key not in ('parenleft','parenright'):return
    p=at_location(load()[key],design);l,b,r,t=p['bounds'];glyph.clearContours();mirror=key=='parenright';construction(p).replay(glyph.getPen(),(-(r-l) if mirror else r-l,0,0,t-b,r if mirror else l,b))
