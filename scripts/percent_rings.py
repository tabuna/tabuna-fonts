"""Percent reuses the oval-ring and clipped diagonal-band constructions."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from rounds import contour
from math_bands import construction as bands
from parameters import at_location


def construction(p):
    d=Drawing()
    for ring in p['rings']:
        for index,field in enumerate(['outerHandles','innerHandles']):contour(ring['bounds'][index],ring[field],index==1).replay(d.pen)
    bands(dict(bars=[],slashes=[p['slash']])).replay(d.pen)
    return d


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/percent-rings.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='percent':return
    glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
