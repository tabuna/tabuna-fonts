"""Ya family: upright stem, diagonal leg, and eight tangent-defined cubics."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from bezier import bowl_side
from parameters import at_location


def construction(p):
    stem=p['stem'];outer=p['outer'];inner=p['inner'];leg=p['leg']
    x=lambda edge,y:edge[0]*y+edge[1]
    d=Drawing()
    top=(outer['top_x'],1);left=(outer['left'],outer['axis'])
    shoulder=(x(leg['left'],outer['join_y']),outer['join_y'])
    base=p['bowl_bottom']
    d.outline((1,0),[(1,1),top,*bowl_side(outer,top,left,shoulder),
                    (x(leg['left'],0),0),(x(leg['right'],0),0),
                    (x(leg['right'],base),base),(stem,base),(stem,0)])
    top=(inner['top_x'],inner['top']);left=(inner['left'],inner['axis'])
    bottom=(inner['bottom_x'],inner['bottom'])
    d.outline((stem,inner['top']),[top,*bowl_side(inner,top,left,bottom),(stem,inner['bottom'])],counter=True)
    l,b,r,t=p['bounds'];out=Drawing();d.replay(out.pen,(r-l,0,0,t-b,l,b));return out


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/ya-bowl.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    data=load().get(key)
    if data is not None:
        glyph.clearContours();construction(at_location(data,design)).replay(glyph.getPen())
