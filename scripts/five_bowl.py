"""Five: a flat cap, slanted stem and open bowl with independent inner arcs."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from bezier import tangent_arc
from parameters import at_location


def construction(p):
    """Quarter arcs have tangent lengths relative to their endpoint distance."""
    from math import hypot
    cap, stem, outer, inner = (p[k] for k in ('cap', 'stem', 'outer', 'inner'))
    d = Drawing()
    segments = []

    def arc(start, end, departure, arrival, handles):
        segments.append(tangent_arc(start, end, departure, arrival, handles))

    def direction(slope):
        length = hypot(1, slope)
        return (1 / length, slope / length)

    start = (cap['left'], 1)
    shoulder = (stem['inner_bottom'], outer['shoulder_y'])
    segments.extend([(cap['right'], 1), (cap['right'], cap['bottom']),
                     (stem['inner_top'], cap['bottom']), shoulder])
    ot, oright, ob = ((outer['top_x'], outer['top']),
                      (1, outer['axis']), (outer['bottom_x'], 0))
    cut = (0, outer['cut'])
    arc(shoulder, ot, direction(outer['shoulder_slope']), (1, 0), outer['handles'][0])
    arc(ot, oright, (1, 0), (0, -1), outer['handles'][1])
    arc(oright, ob, (0, -1), (-1, 0), outer['handles'][2])
    arc(ob, cut, (-1, 0), (0, 1), outer['handles'][3])
    icut = (inner['cut_x'], outer['cut'])
    segments.append(icut)
    ib, iright, it = ((inner['bottom_x'], inner['bottom']),
                      (inner['right'], inner['axis']), (inner['top_x'], inner['top']))
    join = (stem['join_x'], stem['bottom'])
    arc(icut, ib, (0, -1), (1, 0), inner['handles'][0])
    arc(ib, iright, (1, 0), (0, 1), inner['handles'][1])
    arc(iright, it, (0, 1), (-1, 0), inner['handles'][2])
    arrival = tuple(-v for v in direction(inner['join_slope']))
    arc(it, join, (-1, 0), arrival, inner['handles'][3])
    segments.append((stem['outer_bottom'], stem['bottom']))
    d.outline(start, segments)
    l, b, r, t = p['bounds']
    scaled = Drawing()
    d.replay(scaled.pen, (r-l, 0, 0, t-b, l, b))
    return scaled


@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1] / 'sources/five-bowl.json').read_text())['weights']


def apply(glyph, key, design):
    if key != 'five':
        return
    drawing = construction(at_location(load(), design))
    glyph.clearContours()
    drawing.replay(glyph.getPen())
