"""Reading/math marks composed from shared round contours and oriented bands."""
import json
from pathlib import Path
from functools import lru_cache
from rounds import contour
from quadratic_round import contour as quadratic_contour
from geometry import Drawing
from math_bands import construction
from parameters import at_location


def drawing(p):
    d=Drawing()
    for q in p['rounds']:
        shape=quadratic_contour(q['bounds'],q['quadrants']) if 'quadrants' in q else contour(q['bounds'],q['handles'])
        shape.replay(d.pen)
    for q in p['bands']:
        x,y=q['direction'];construction(dict(bars=[],slashes=[q['profile']])).replay(d.pen,(y,-x,x,y,0,0))
    return d


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/round-band-marks.json').read_text())['glyphs']


def apply(glyph,key,design):
    data=load().get(key)
    if data is None:return
    glyph.clearContours();glyph.clearComponents();drawing(at_location(data,design)).replay(glyph.getPen())
