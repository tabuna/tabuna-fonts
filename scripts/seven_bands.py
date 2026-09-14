"""Seven from a horizontal cap and two independently measured diagonal lines."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from parameters import at_location


def construction(p):
    left, right = p['left'], p['right']
    top, floor, bottom = p['top'], p['floor'], p['bottom']
    a, b = p['diagonal_left'], p['diagonal_right']
    # The exterior diagonal meets the vertical cap; the interior meets its floor.
    junction_y = (right - b[1]) / b[0]
    d = Drawing()
    d.polygon([(left, top), (right, top), (right, junction_y),
               (b[0]*bottom+b[1], bottom), (a[0]*bottom+a[1], bottom),
               (a[0]*floor+a[1], floor), (left, floor)])
    return d


@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1]/'sources/seven-bands.json').read_text())['weights']


def apply(glyph, key, design):
    if key != 'seven':
        return
    glyph.clearContours()
    construction(at_location(load(), design)).replay(glyph.getPen())
