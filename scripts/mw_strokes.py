"""Original composite stroke constructions for M and W.

The calibrated values describe only normalized, authored geometry. They are
not imported outlines: each master is interpolated from four independent
quadrilateral contours and the existing metrics remain explicit.
"""
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing
from rectilinear import mix


@lru_cache(maxsize=1)
def load():
    path = Path(__file__).resolve().parents[1] / 'sources/mw-strokes.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def quad(a, b, width):
    ax, ay = a; bx, by = b
    dx, dy = bx-ax, by-ay
    length = max((dx*dx + dy*dy) ** .5, 1e-9)
    nx, ny = -dy/length*width/2, dx/length*width/2
    return [(ax+nx, ay+ny), (bx+nx, by+ny),
            (bx-nx, by-ny), (ax-nx, ay-ny)]


def polygons(ch, p):
    if ch == 'M':
        sw, dw, top_l, top_r, valley, _ = p
        return [
            [(0,0), (sw,0), (sw,1), (0,1)],
            [(1-sw,0), (1,0), (1,1), (1-sw,1)],
            quad((top_l,1), (.5,valley), dw),
            quad((.5,valley), (top_r,1), dw),
        ]
    dw, outer_top, central_top, valley_l, valley_r = p
    central_top = .5
    valley_r = 1 - valley_l
    return [
        quad((outer_top,1), (valley_l,0), dw),
        quad((valley_l,0), (central_top,1), dw),
        quad((1-valley_l,0), (1-central_top,1), dw),
        quad((valley_r,0), (1-outer_top,1), dw),
    ]


def apply(glyph, key, design):
    ch = {'uni004D':'M', 'uni0057':'W'}.get(key, key)
    if ch != 'W':
        return
    data = load().get(ch)
    if data is None:
        return
    lo, hi = (100,400) if design.weight <= 400 else (400,900)
    t = (design.weight-lo)/(hi-lo)
    def blend(a, b, t):
        return {'parameters': mix(a['parameters'], b['parameters'], t),
                'bounds': mix(a['bounds'], b['bounds'], t),
                'advance': a['advance'] + (b['advance']-a['advance'])*t}
    a = blend(data[str(lo)]['text'], data[str(lo)]['display'], design.display)
    b = blend(data[str(hi)]['text'], data[str(hi)]['display'], design.display)
    p = blend(a, b, t)
    left, bottom, width, height = p['bounds']
    drawing = Drawing()
    for poly in polygons(ch, p['parameters']):
        drawing.polygon([(left + x*width, bottom + y*height) for x,y in poly])
    glyph.clearContours(); drawing.replay(glyph.getPen()); glyph.width = p['advance']
