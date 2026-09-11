"""Original oval constructions for Cyrillic Ф/ф.

The system raster is used only as a measurement target by the calibration
script.  The production glyphs remain authored here as one ellipse, one
counter and a centered vertical stroke, with values interpolated over both
variation axes.
"""
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing
from rectilinear import mix


@lru_cache(maxsize=1)
def load():
    path = Path(__file__).resolve().parents[1] / 'sources/phi.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def _blend(a, b, t):
    return {
        'parameters': mix(a['parameters'], b['parameters'], t),
        'bounds': mix(a['bounds'], b['bounds'], t),
        'advance': a['advance'] + (b['advance'] - a['advance']) * t,
    }


def _master(data, weight, display):
    lo, hi = (100, 400) if weight <= 400 else (400, 900)
    t = (weight - lo) / (hi - lo)
    a = _blend(data[str(lo)]['text'], data[str(lo)]['display'], display)
    b = _blend(data[str(hi)]['text'], data[str(hi)]['display'], display)
    return _blend(a, b, t)


def apply(glyph, key, design):
    ch = {'uni0424': 'Ф', 'uni0444': 'ф'}.get(key, key)
    data = load().get(ch)
    if data is None:
        return
    p = _master(data, design.weight, design.display)
    left, bottom, width, height = p['bounds']
    outer_x, outer_y, inner_x, inner_y, stem_w, stem_bottom, stem_top = p['parameters']
    d = Drawing()
    # Coordinates are normalized to the measured ink bounds.  The tiny outer
    # inset is kept explicit so the interpolation never grows past the metric
    # box at an extreme weight.
    ol = left + outer_x * width
    ob = bottom + outer_y * height
    oright = left + (1 - outer_x) * width
    ot = bottom + (1 - outer_y) * height
    d.ring(ol, ob, oright, ot, inner_x * width, inner_y * height)
    sx = left + (0.5 - stem_w / 2) * width
    d.rect(sx, bottom + stem_bottom * height, stem_w * width,
           (stem_top - stem_bottom) * height)
    glyph.clearContours()
    d.replay(glyph.getPen())
    glyph.width = p['advance']
