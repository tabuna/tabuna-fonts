"""Nine: a bowl, a separately sized counter and a returning lower tail."""
import json
from functools import lru_cache
from math import hypot
from pathlib import Path
from geometry import Drawing
from bezier import unit, tangent_arc as arc
from parameters import at_location


def construction(p):
    outer, tail, bowl, counter = (p[k] for k in ('outer','tail','bowl','counter'))
    d = Drawing()

    top = (outer['top_x'], 1)
    shoulder = (outer['shoulder_x'], outer['shoulder_y'])
    shoulder_tangent = unit(1,-outer['shoulder_slope'])
    right = (1, outer['axis'])
    lower_shoulder=(outer['lower_x'],outer['lower_y'])
    lower_tangent=unit(-outer['lower_slope'],-1)
    bottom = (outer['bottom_x'], 0)
    cut = (tail['outer_cut_x'], tail['cut_y'])
    inner_cut = (tail['inner_cut_x'], tail['cut_y'])
    inner_bottom = (tail['bottom_x'], tail['bottom'])
    join = (tail['join_x'], tail['join_y'])
    bowl_bottom = (bowl['bottom_x'], bowl['bottom'])
    left = (0, bowl['left_y'])
    h = outer['handles']
    segments = [arc(top,shoulder,(1,0),shoulder_tangent,h[0]),
                arc(shoulder,right,shoulder_tangent,(0,-1),h[8]),
                arc(right,lower_shoulder,(0,-1),lower_tangent,h[1]),
                arc(lower_shoulder,bottom,lower_tangent,(-1,0),h[9]),
                arc(bottom,cut,(-1,0),unit(-tail['outer_cut_slope'],1),h[2]),
                inner_cut,
                arc(inner_cut,inner_bottom,unit(tail['inner_cut_slope'],-1),(1,0),h[3]),
                arc(inner_bottom,join,(1,0),(0,1),h[4]),
                arc(join,bowl_bottom,unit(-1,-bowl['join_slope']),(-1,0),h[5]),
                arc(bowl_bottom,left,(-1,0),(0,1),h[6]),
                arc(left,top,(0,1),(1,0),h[7])]
    d.outline(top, segments)
    ct=(counter['top_x'],counter['top']);cr=(counter['right'],counter['right_y'])
    cb=(counter['bottom_x'],counter['bottom']);cl=(counter['left'],counter['left_y'])
    h=counter['handles']
    d.outline(ct,[arc(ct,cr,(1,0),(0,-1),h[0]),arc(cr,cb,(0,-1),(-1,0),h[1]),
                  arc(cb,cl,(-1,0),(0,1),h[2]),arc(cl,ct,(0,1),(1,0),h[3])],counter=True)
    l,b,r,t=p['bounds'];scaled=Drawing();d.replay(scaled.pen,(r-l,0,0,t-b,l,b))
    return scaled


@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1]/'sources/nine-bowl.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='nine':
        return
    drawing=construction(at_location(load(),design))
    glyph.clearContours();drawing.replay(glyph.getPen())
