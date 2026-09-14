"""f/t from an independently positioned stem, crossbar, and tangent hook."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from bezier import tangent_arc,unit
from parameters import at_location


def construction(p,reverse=False):
    left,right=p['stem'];d=Drawing()
    def edge(x,q):
        a=(x,q['top']-q['rise']);b=(q['top_x'],q['top']);c=(p['tip_x'],q['top']-q['drop'])
        return a,[tangent_arc(a,b,(0,1),(1,0),q['handles'][0],bounded=True),
                  tangent_arc(b,c,(1,0),unit(1,-q['slope']),q['handles'][1],bounded=True)]
    a,outer=edge(left,p['outer']);b,inner=edge(right,p['inner'])
    # Reverse the inner edge with the same controls, keeping its tangent.
    inner_start=b;full=[]
    for segment in inner:full.append((inner_start,*segment));inner_start=segment[-1]
    returning=[(curve[2],curve[1],curve[0]) for curve in reversed(full)]
    d.outline((left,0),[a,*outer,inner[-1][-1],*returning,(right,0)])
    bar=p['bar'];d.rect(bar['left'],bar['bottom'],bar['right']-bar['left'],bar['top']-bar['bottom'])
    l,b,r,t=p['bounds'];out=Drawing()
    d.replay(out.pen,(r-l,0,0,b-t if reverse else t-b,l,t if reverse else b));return out


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/hooked-stems.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    data=load().get(key)
    if data is not None:
        glyph.clearContours();construction(at_location(data,design),reverse=key=='t').replay(glyph.getPen())
