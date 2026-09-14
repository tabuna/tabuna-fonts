"""Capital Be: stem and top bar with two sides from the shared Bézier bowl."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from bezier import bowl_side
from parameters import at_location


def construction(p):
    stem=p['stem'];cap=p['cap'];outer=p['outer'];inner=p['inner']
    d=Drawing()
    def arcs(q):
        top=(q['top_x'],q['top']);side=(q['right'],q['axis']);bottom=(q['bottom_x'],q['bottom'])
        return top,bowl_side(q,top,side,bottom)
    top,curves=arcs(outer)
    d.outline((0,0),[(0,1),(cap['right'],1),(cap['right'],cap['bottom']),
                    (stem,cap['bottom']),(stem,outer['top']),top,*curves])
    top,curves=arcs(inner)
    d.outline((stem,inner['top']),[top,*curves,(stem,inner['bottom'])],counter=True)
    l,b,r,t=p['bounds'];out=Drawing();d.replay(out.pen,(r-l,0,0,t-b,l,b));return out


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/be-bowl.json'
    return json.loads(path.read_text())['weights'] if path.exists() else {}


def apply(glyph,key,design):
    if key=='uni0411' and load():
        glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
