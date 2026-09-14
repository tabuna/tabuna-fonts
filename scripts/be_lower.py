"""Lowercase Be: an oval bowl and a rising, returning ribbon.

All segments are cubic tangent arcs; the two ribbon sides have independent
shoulders so stroke width need not be a scaled copy of the regular master.
"""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from bezier import tangent_arc as arc, unit
from parameters import at_location


def construction(p):
    o,t,b,c=(p[k] for k in ('outer','tail','bowl','counter'))
    bottom=(o['bottom_x'],0);left=(0,o['left_y'])
    shoulder=(t['shoulder_x'],t['shoulder_y']);neck=(t['neck_x'],t['neck_y'])
    tip=(t['tip_x'],1);cut=(t['tip_x'],t['cut_y'])
    inner_neck=(t['inner_neck_x'],t['inner_neck_y'])
    join=(b['join_x'],b['join_y']);top=(b['top_x'],b['top'])
    right=(1,b['right_y'])
    nodes=[bottom,left,shoulder,neck,tip,cut,inner_neck,join,top,right,bottom]
    directions=[(-1,0),(0,1),unit(1,t['shoulder_slope']),unit(1,t['neck_slope']),unit(1,t['tip_slope']),unit(-1,-t['cut_slope']),unit(-1,-t['inner_neck_slope']),unit(-b['join_slope'], -1),(1,0),(0,-1),(-1,0)]
    h=o['handles'];segments=[]
    for i in range(10):
        if i==4:segments.append(cut)
        else:
            # The bowl starts with a corner at the ribbon junction.
            start=unit(1,b['rise_slope']) if i==7 else directions[i]
            segments.append(arc(nodes[i],nodes[i+1],start,directions[i+1],h[i]))
    d=Drawing();d.outline(bottom,segments)
    top=(c['top_x'],c['top']);right=(c['right'],c['right_y']);bottom=(c['bottom_x'],c['bottom']);left=(c['left'],c['left_y'])
    h=c['handles'];d.outline(top,[arc(top,right,(1,0),(0,-1),h[0]),arc(right,bottom,(0,-1),(-1,0),h[1]),arc(bottom,left,(-1,0),(0,1),h[2]),arc(left,top,(0,1),(1,0),h[3])],counter=True)
    l,b,r,t=p['bounds'];scaled=Drawing();d.replay(scaled.pen,(r-l,0,0,t-b,l,b));return scaled


@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1]/'sources/be-lower.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='uni0431':return
    d=construction(at_location(load(),design));glyph.clearContours();d.replay(glyph.getPen())
