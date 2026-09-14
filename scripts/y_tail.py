"""Descending fork: two diagonal arms and a curved, returning lower terminal."""
import json
from functools import lru_cache
from bezier import unit, tangent_arc
from pathlib import Path
from geometry import Drawing
from parameters import at_location


def construction(p):
    def point(edge,y):
        a,b=p[edge];return a*y+b,y
    def arc(a,b,u,v,handles):
        return tangent_arc(a,b,u,v,handles,bounded=True)
    f=p['foot'];join=f['inner_y']+f['inner_rise']
    lo=point('outer_left',join);ro=point('outer_right',f['outer_join'])
    outer=(f['outer_x'],0);inner=(f['inner_x'],f['inner_y'])
    heel=(f['cut_x'],f['cut_bottom']);tip=(f['cut_x'],f['cut_top'])
    outer_bend=(f['outer_bend_x'],f['outer_bend_y'])
    inner_bend=(inner[0]+(lo[0]-inner[0])*f['inner_progress_x'],
                inner[1]+(join-inner[1])*f['inner_progress_y'])
    od=unit(-p['outer_right'][0],-1);id=unit(f['inner_slope'],1)
    ob=unit(-f['outer_bend_slope'],-1);ib=unit(f['inner_bend_slope'],1)
    h=f['handles'];q=p['counter_bottom'];d=Drawing()
    d.outline(point('outer_left',1),[point('inner_left',1),point('inner_left',q),
        point('inner_right',q),point('inner_right',1),point('outer_right',1),ro,
        arc(ro,outer_bend,od,ob,h[0]),arc(outer_bend,outer,ob,(-1,0),h[1]),
        arc(outer,heel,(-1,0),unit(-1,f['heel_slope']),h[2]),tip,
        arc(tip,inner,unit(1,-f['tip_slope']),(1,0),h[3]),
        arc(inner,inner_bend,(1,0),ib,h[4]),arc(inner_bend,lo,ib,id,h[5])])
    l,b,r,t=p['bounds'];out=Drawing();d.replay(out.pen,(r-l,0,0,t-b,l,b));return out


@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1]/'sources/y-tail.json').read_text())['glyphs']


def apply(glyph,key,design):
    data=load().get(key)
    if data is not None:
        glyph.clearContours();construction(at_location(data,design)).replay(glyph.getPen())
