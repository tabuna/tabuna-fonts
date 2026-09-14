"""Comparison signs from four line equations, a clipped tip and an optional bar."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from parameters import at_location


def construction(p, reverse=False):
    left,right=p['span'];lo,li,ui,uo=p['edges']
    def y(edge,x):return edge['slope']*x+edge['intercept']
    join=(li['intercept']-ui['intercept'])/(ui['slope']-li['slope'])
    points=[(right,y(uo,right)),(left,y(uo,left)),(left,y(lo,left)),
                           (right,y(lo,right)),(right,y(li,right)),(join,y(li,join)),(right,y(ui,right))]
    if 'vertical_clip' in p:
        bottom,top=p['vertical_clip']
        def x(edge,level):return (level-edge['intercept'])/edge['slope']
        # Fixed seven-point topology at every weight: both band ends are
        # horizontal cuts, computed analytically rather than polygon clipping.
        points=[(x(uo,top),top),(left,y(uo,left)),(left,y(lo,left)),
                (x(lo,bottom),bottom),(x(li,bottom),bottom),
                (join,y(li,join)),(x(ui,top),top)]
    d=Drawing();d.polygon(points)
    for bar in p['bars']:
        d.rect(bar['left'],bar['bottom'],bar['width'],bar['height']+bar.get('optical_top_expansion',0))
    out=Drawing();d.replay(out.pen,(-1,0,0,1,left+right,0) if reverse else (1,0,0,1,0,0));return out


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/comparison-signs.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    data=load().get(key)
    if data is not None:
        glyph.clearContours();construction(at_location(data,design),key in ('greater','greaterequal')).replay(glyph.getPen())
