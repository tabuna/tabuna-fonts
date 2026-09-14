"""Che: two tangent-controlled cup edges and an independent upright."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from bezier import tangent_arc,unit
from parameters import at_location


def edge(q,left,right):
    a=(left,q['start_y']);b=(q['bottom_x'],q['bottom_y']);c=(right,q['join_y'])
    return a,[tangent_arc(a,b,(0,-1),(1,0),q['handles'][0]),tangent_arc(b,c,(1,0),unit(1,q['slope']),q['handles'][1])]


def construction(p):
    d=Drawing();right=p['right'];outer,arcs=edge(p['outer'],0,right);inner,backs=edge(p['inner'],p['left'],right)
    end=backs[-1][-1]
    # Reverse cubic traversal while preserving the shared cup tangent.
    reverse=[(backs[1][1],backs[1][0],backs[0][-1]),(backs[0][1],backs[0][0],inner)]
    d.outline((0,1),[outer,*arcs,end,*reverse,(p['left'],1)])
    d.rect(right,0,1-right,1)
    return d


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/che-cup.json').read_text())['glyphs']


def apply(glyph,key,design):
    data=load().get(key)
    if data is None:return
    p=at_location(data,design);l,b,r,t=p['bounds'];glyph.clearContours();construction(p).replay(glyph.getPen(),(r-l,0,0,t-b,l,b))
