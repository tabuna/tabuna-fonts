"""A stem and two intersecting straight bands, independent of source vertices."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from parameters import at_location


def crossing(a, b):
    """Intersect lines described as x = slope * y + intercept."""
    slope_a, offset_a = a
    slope_b, offset_b = b
    y = (offset_b - offset_a) / (slope_a - slope_b)
    return slope_a * y + offset_a, y


def construction(parameters):
    left, right = parameters['stem']
    top = parameters['top']
    upper, lower = parameters['upper'], parameters['lower']
    drawing = Drawing()
    drawing.rect(left, 0, right - left, parameters.get("stem_top", top))
    # Bury the upper band's vertical cap inside the stem. Its hidden overlap
    # is independent of the visible silhouette and avoids a hairline seam.
    root = right - (right - left) / 8
    ul, ur = upper['left'], upper['right']
    upper_points = [
        (root, (root - ul[1]) / ul[0]),
        (ul[0] * top + ul[1], top),
        (ur[0] * top + ur[1], top),
        (root, (root - ur[1]) / ur[0]),
    ]
    if 'floor' in upper:
        floor = upper['floor']
        # A horizontal junction floor prevents the rising band from intruding
        # into the lower aperture. Keep five points in every master.
        x = max(root, ul[0] * floor + ul[1])
        upper_points = [(ul[0] * top + ul[1], top),
                        (ur[0] * top + ur[1], top),
                        (ur[0] * floor + ur[1], floor), (x, floor),
                        (x, max(floor, (root - ul[1]) / ul[0]))]
    drawing.polygon(upper_points)
    # The falling band stops at the far boundary of the rising band. Their
    # nonzero union creates the junction; no separately placed notch nodes.
    ll, lr = lower['left'], lower['right']
    drawing.polygon([(ll[1], 0), crossing(ll, ul), crossing(lr, ul), (lr[1], 0)])
    return drawing


@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1] / 'sources/diagonal-bands.json').read_text())['glyphs']


def apply(glyph, key, design):
    data = load().get(key)
    if data is None:
        return
    drawing = construction(at_location(data, design))
    glyph.clearContours()
    drawing.replay(glyph.getPen())
    # Keep the existing separately calibrated advance and mark anchors.
