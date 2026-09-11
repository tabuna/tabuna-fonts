"""Our four-cubic round model, with scalar raster-calibrated proportions."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from bowls import mix

@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/round-weights.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    character={'uni043E':'о','uni041E':'О'}.get(key,key)
    data=load().get(character)
    if data is None:return
    assert len(glyph.contours)==2
    lo,hi=(100,400) if design.weight<=400 else (400,900)
    a=mix(data[str(lo)]['text'],data[str(lo)]['display'],design.display)
    b=mix(data[str(hi)]['text'],data[str(hi)]['display'],design.display)
    p=mix(a,b,(design.weight-lo)/(hi-lo))
    drawing=Drawing()
    for index,field in enumerate(('outerHandles','innerHandles')):
        handles=p[field]
        l,b,r,t=p['bounds'][index];cx=(l+r)/2;cy=(b+t)/2;rx=(r-l)/2;ry=(t-b)/2
        (ax,ay),(bx,by),(cxh,cyh),(dx,dy)=handles
        drawing.outline((l,cy),[
            ((l,cy+ry*ay),(cx-rx*ax,t),(cx,t)),
            ((cx+rx*bx,t),(r,cy+ry*by),(r,cy)),
            ((r,cy-ry*cyh),(cx+rx*cxh,b),(cx,b)),
            ((cx-rx*dx,b),(l,cy-ry*dy),(l,cy))],counter=index==1)
    glyph.clearContours();drawing.replay(glyph.getPen())
    glyph.width=p['advance']
