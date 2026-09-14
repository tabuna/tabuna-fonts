"""Cyrillic El: two measured stem edges, a cap and a curved returning foot."""
import json
from functools import lru_cache
from bezier import unit, tangent_arc as arc
from pathlib import Path
from geometry import Drawing
from parameters import at_location


def construction(p):
    foot=p['foot']; outer,inner=p['stem_outer'],p['stem_inner']
    line=lambda edge,y:(edge[0]*y+edge[1],y)
    low=(0,foot['cut_bottom']);high=(0,foot['cut_top'])
    inside=(foot['inside_x'],foot['inside_y']);outside=(foot['outside_x'],0)
    up_bend=(foot['up_x'],foot['up_y']);down_bend=(foot['down_x'],foot['down_y'])
    up_join=line(outer,foot['up_join']);down_join=line(inner,foot['down_join'])
    up_tangent=unit(1,foot['up_slope']);down_tangent=unit(-1,-foot['down_slope'])
    tip, rise_low, rise_high, fall_high, fall_low, heel = foot['handles']
    baseline=p['baseline'];cap=p['cap_bottom']
    d=Drawing();d.outline(low,[high,
        arc(high,inside,unit(1,-foot['top_slope']),(1,0),tip),
        arc(inside,up_bend,(1,0),up_tangent,rise_low),
        arc(up_bend,up_join,up_tangent,unit(outer[0],1),rise_high),
        line(outer,1),(1,1),(1,baseline),(p['right_inner'],baseline),
        (p['right_inner'],cap),line(inner,cap),down_join,
        arc(down_join,down_bend,unit(-inner[0],-1),down_tangent,fall_high),
        arc(down_bend,outside,down_tangent,(-1,0),fall_low),
        arc(outside,low,(-1,0),unit(-1,foot['bottom_slope']),heel)])
    l,b,r,t=p['bounds'];scaled=Drawing();d.replay(scaled.pen,(r-l,0,0,t-b,l,b))
    if 'bowl' in p:
        q=p['bowl']
        for prefix,counter in [('',False),('inner_',True)]:
            left=q['counter_left'] if counter else q['left']
            top=(q[prefix+'top_x'],q[prefix+'top'])
            right=(q[prefix+'right'],q[prefix+'axis'])
            bottom=(q[prefix+'bottom_x'],q[prefix+'bottom'])
            a,b=q[prefix+'handles']
            scaled.outline((left,top[1]),[top,arc(top,right,(1,0),(0,-1),a),
                           arc(right,bottom,(0,-1),(-1,0),b),(left,bottom[1])],counter=counter)
    return scaled


@lru_cache(maxsize=1)
def load():
    root=Path(__file__).resolve().parents[1]/'sources'
    return {key:json.loads((root/file).read_text())['weights']
            for key,file in [('uni041B','el-stem.json'),('uni043B','el-stem-lower.json'),
                             ('uni0409','lj-stem.json'),('uni0459','lj-stem-lower.json')]
            if (root/file).exists()}


def apply(glyph,key,design):
    data=load().get(key)
    if data is None:return
    drawing=construction(at_location(data,design));glyph.clearContours();drawing.replay(glyph.getPen())
