"""Center digits in a shared cell sized from final master ink, at 2048 UPM."""
import math
from fontTools.pens.boundsPen import BoundsPen


def apply(font):
    names = ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine')
    bounds = {}
    for name in names:
        pen = BoundsPen(font)
        font[name].draw(pen)
        bounds[name] = pen.bounds
    # Reserve 1/16 em of separation plus the worst common negative tracking.
    # Master interpolation preserves the enclosure; the final-font test also
    # exercises axis knots and intermediate positions after all metric deltas.
    width = max(font['zero.tnum'].width,
                math.ceil(max(b[2] - b[0] for b in bounds.values()) + 128 + 17))
    for name, (left, _, right, _) in bounds.items():
        glyph = font[name + '.tnum']
        glyph.width = width
        glyph.components[0].transformation = (1, 0, 0, 1, (width - right - left) / 2, 0)
    if 'uni2007' in font:
        font['uni2007'].width = width
