"""A: two tapered diagonal stems, a crossbar and a flat counter apex."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from parameters import at_location


def construction(p):
    def point(edge, y):
        slope, offset = p[edge]
        return slope * y + offset, y
    top, bar = p['top'], p['bar_bottom']
    d = Drawing()
    d.polygon([point('outer_left', 0), point('outer_left', top),
               point('outer_right', top), point('outer_right', 0),
               point('inner_right', 0), point('inner_right', bar),
               point('inner_left', bar), point('inner_left', 0)])
    bottom, apex = p['bar_top'], p['counter_top']
    d.outline(point('inner_left', bottom), [point('inner_left', apex),
              point('inner_right', apex), point('inner_right', bottom)], counter=True)
    return d


@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1] / 'sources/cap-a.json').read_text())['glyphs']


def apply(glyph, key, design):
    data = load().get(key)
    if data is not None:
        glyph.clearContours()
        construction(at_location(data, design)).replay(glyph.getPen())
