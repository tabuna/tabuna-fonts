"""At sign: tangent-directed spiral ribbon and a shared four-arc inner bowl."""
from geometry import Drawing
from bezier import tangent_arc,unit
from rounds import contour


def spiral(p, pieces=False):
    def path(q,inside):
        stem_x=p['stem_left']+(p['stem_width'] if inside else 0)
        points=[(q['tip_x'],q['tip_y']),(q['bottom_x'],q['bottom_y']),
                (q['left_x'],q['left_y']),(q['top_x'],q['top_y']),
                (q['right_x'],q['right_y']),(q['hook_x'],q['hook_y']),
                (stem_x,q['hook_y']+(p['cap']-q['hook_y'])*q['stem_fraction'])]
        tangents=[unit(-1,-q.get('tip_slope',p['tip_slope'])),(-1,0),(0,1),(1,0),(0,-1),(-1,0),(0,1)]
        curves=[tangent_arc(a,b,u,v,h,bounded=True) for a,b,u,v,h in zip(points,points[1:],tangents,tangents[1:],q['handles'])]
        return points,curves
    outer,oc=path(p['outer'],False);inner,ic=path(p['inner'],True)
    reverse=[(curve[1],curve[0],start) for start,curve in reversed(list(zip(inner,ic)))]
    d=Drawing()
    if pieces:
        for n in range(len(oc)):
            d.outline(outer[n],[oc[n],inner[n+1],(ic[n][1],ic[n][0],inner[n])])
        d.outline(outer[-1],[(outer[-1][0],p['cap']),(inner[-1][0],p['cap']),inner[-1]])
    else:d.outline(outer[0],oc+[(outer[-1][0],p['cap']),(inner[-1][0],p['cap']),inner[-1]]+reverse)
    return d


def asymmetric_bowl(bounds, handles, extrema, counter=False):
    l,b,r,t=bounds
    ly,tx,ry,bx=extrema
    ly=b+(t-b)*ly;ry=b+(t-b)*ry;tx=l+(r-l)*tx;bx=l+(r-l)*bx
    (ax,ay),(cx,cy),(ex,ey),(gx,gy)=handles
    d=Drawing();d.outline((l,ly),[
        ((l,ly+(t-ly)*ay),(tx-(tx-l)*ax,t),(tx,t)),
        ((tx+(r-tx)*cx,t),(r,ry+(t-ry)*cy),(r,ry)),
        ((r,ry-(ry-b)*ey),(bx+(r-bx)*ex,b),(bx,b)),
        ((bx-(bx-l)*gx,b),(l,ly-(ly-b)*gy),(l,ly))],counter)
    return d


def construction(p):
    d=Drawing();spiral(p['spiral'],pieces=True).replay(d.pen)
    asymmetric_bowl(p['bowl_bounds'],p['bowl_handles'],p.get('bowl_extrema',[.5]*4)).replay(d.pen)
    asymmetric_bowl(p['counter_bounds'],p['counter_handles'],p.get('counter_extrema',[.5]*4),True).replay(d.pen)
    l,b,r,t=p['bounds'];out=Drawing();d.replay(out.pen,(r-l,0,0,t-b,l,b));return out


from functools import lru_cache
from pathlib import Path
import json
from parameters import at_location


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/at-spiral.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='at':return
    glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
