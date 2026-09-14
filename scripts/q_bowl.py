"""Q combines the shared four-arc round model with a measured diagonal band."""
import json
from functools import lru_cache
from pathlib import Path
from rounds import contour
from math_bands import construction
from parameters import at_location


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/q-bowl.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='Q':return
    p=at_location(load(),design);glyph.clearContours()
    for i,name in enumerate(['outerHandles','innerHandles']):contour(p['bowl']['bounds'][i],p['bowl'][name],i==1).replay(glyph.getPen())
    construction(dict(bars=[],slashes=[p['tail']])).replay(glyph.getPen())
