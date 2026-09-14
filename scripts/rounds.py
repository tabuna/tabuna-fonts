"""Our four-cubic round model, with scalar raster-calibrated proportions."""
from parameters import at_location
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing

@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/round-weights.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def contour(bounds, handles, counter=False):
    drawing=Drawing()
    l,b,r,t=bounds;cx=(l+r)/2;cy=(b+t)/2;rx=(r-l)/2;ry=(t-b)/2
    (ax,ay),(bx,by),(cxh,cyh),(dx,dy)=handles
    drawing.outline((l,cy),[
        ((l,cy+ry*ay),(cx-rx*ax,t),(cx,t)),
        ((cx+rx*bx,t),(r,cy+ry*by),(r,cy)),
        ((r,cy-ry*cyh),(cx+rx*cxh,b),(cx,b)),
        ((cx-rx*dx,b),(l,cy-ry*dy),(l,cy))],counter=counter)
    return drawing


def apply(glyph,key,design):
    character={'uni043E':'о','uni041E':'О'}.get(key,key)
    data=load().get(character)
    if data is None:return
    assert len(glyph.contours)==2
    p=at_location(data, design)
    drawing=Drawing()
    for index,field in enumerate(('outerHandles','innerHandles')):
        contour(p['bounds'][index],p[field],index==1).replay(drawing.pen)
    glyph.clearContours();drawing.replay(glyph.getPen())
    glyph.width=p['advance']
