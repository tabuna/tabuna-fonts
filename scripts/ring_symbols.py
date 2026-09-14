"""Zero and degree use the same authored four-cubic contour as O/o."""
import json
from pathlib import Path
from functools import lru_cache
from rounds import contour
from parameters import at_location


@lru_cache(maxsize=1)
def load():
    p=Path(__file__).resolve().parents[1]/'sources/ring-symbols.json'
    return json.loads(p.read_text())['glyphs'] if p.exists() else {}


def apply(glyph,key,design):
    data=load().get(key)
    if data is None:return
    p=at_location(data,design);glyph.clearContours()
    for index,field in enumerate(['outerHandles','innerHandles']):
        contour(p['bounds'][index],p[field],index==1).replay(glyph.getPen())
