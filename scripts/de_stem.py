"""Д/д: measured straight stems, tangent transitions and a shared baseline bar."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from bezier import tangent_arc,unit
from parameters import at_location


def construction(p):
    d=Drawing();base=p['bar']['top'];top=p['top'];outer=p['outer'];inner=p['inner']
    def line(edge,y):return edge[0]*y+edge[1],y
    a=(p['outer_cut'],base);b=line(outer,p['outer_join']);c=line(inner,p['inner_join']);e=(p['inner_cut'],base)
    up=tangent_arc(a,b,(1,0),unit(outer[0],1),p['outer_handles'],bounded=True)
    down=tangent_arc(c,e,unit(-inner[0],-1),(-1,0),p['inner_handles'],bounded=True)
    if p.get('g2'):
        # Three collinear controls at the straight-stem end give zero
        # endpoint curvature, matching the adjacent line exactly.
        up=(line(outer,base),up[1],b)
        down=(down[0],line(inner,base),e)
    d.outline(a,[up,
                 line(outer,top),(p['right_outer'],top),(p['right_outer'],base),
                 (p['right_inner'],base),(p['right_inner'],p['cap_bottom']),line(inner,p['cap_bottom']),c,
                 down])
    bar=p['bar'];d.rect(bar['left'],bar['bottom'],bar['right']-bar['left'],base-bar['bottom'])
    for left,right in p['legs']:d.rect(left,p['bottom'],right-left,base-p['bottom'])
    return d


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/de-stem.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    from parameters import at_location
    data=load().get(key)
    if data is not None:
        glyph.clearContours();construction(at_location(data,design)).replay(glyph.getPen())
