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


def tapered(a, b, start_width, end_width):
    first, last = quad(a, b, start_width), quad(a, b, end_width)
    return [first[0], last[1], last[2], first[3]]


def polygons(ch, p):
    if ch == 'M':
        sw, dw, top_l, top_r, valley, _ = p
        return [
            [(0,0), (sw,0), (sw,1), (0,1)],
            [(1-sw,0), (1,0), (1,1), (1-sw,1)],
            quad((top_l,1), (.5,valley), dw),
            quad((.5,valley), (top_r,1), dw),
        ]
    dw, outer_top, central_top, valley_l, valley_r = p[:5]
    inner_dw = p[5] if len(p) > 5 else dw
    inner_bottom = p[6] if len(p) > 6 else inner_dw
    central_top = .5
    valley_r = 1 - valley_l
    return [
        quad((outer_top,1), (valley_l,0), dw),
        tapered((valley_l,0), (central_top,1), inner_bottom, inner_dw),
        tapered((1-valley_l,0), (1-central_top,1), inner_bottom, inner_dw),
        quad((valley_r,0), (1-outer_top,1), dw),
    ]


def construction(p):
    left, bottom, width, height = p['bounds']
    drawing = Drawing()
    for i, poly in enumerate(polygons('W', p['parameters'])):
        feet = ((1, 0), (2, 3)) if i == 0 else ((0, 1), (3, 2))
        original = list(poly)
        for level, field, pairs in ((0, 'foot_flatness', feet),
                                    (1, 'head_flatness', [(b, a) for a, b in feet])):
            flatness = p.get(field, 0)
            if not flatness:
                continue
            # Slide the foot along its existing sides toward a level terminal.
            # Four vertices remain four vertices throughout the designspace.
            for foot, opposite in pairs:
                x, y = original[foot]; ox, oy = original[opposite]
                poly[foot] = (x+(level-y)*(ox-x)/(oy-y)*flatness, y+(level-y)*flatness)
        drawing.polygon([(left + x*width, bottom + y*height) for x,y in poly])
    return drawing


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
                'foot_flatness': mix(a.get('foot_flatness', 0), b.get('foot_flatness', 0), t),
                'head_flatness': mix(a.get('head_flatness', 0), b.get('head_flatness', 0), t),
                'advance': a['advance'] + (b['advance']-a['advance'])*t}
    a = blend(data[str(lo)]['text'], data[str(lo)]['display'], design.display)
    b = blend(data[str(hi)]['text'], data[str(hi)]['display'], design.display)
    p = blend(a, b, t)
    glyph.clearContours(); construction(p).replay(glyph.getPen()); glyph.width = p['advance']
