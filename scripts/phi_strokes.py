"""Weight-aware original oval strokes for Cyrillic Ф/ф."""
from geometry import Drawing


def _factor(weight, display):
    if weight <= 400:
        t = (weight - 100) / 300
        f = 1.28 + (1.12 - 1.28) * t
    else:
        t = (weight - 400) / 500
        f = 1.12 + (1.07 - 1.12) * t
    return f * (1 - .06 * display)


def apply(glyph, key, design):
    ch = {'uni0424': 'Ф', 'uni0444': 'ф'}.get(key, key)
    if ch not in ('Ф', 'ф'):
        return
    low = ch == 'ф'
    w = 635 if low else 697
    H = design.h if low else design.cap
    s = design.s * _factor(design.weight, design.display)
    d = Drawing()
    d.ring(0, H * .09, w, H * .91, s, s * .91)
    d.rect((w - s) / 2, -210 if low else -12, s,
           950 if low else H + 24)
    glyph.clearContours()
    d.replay(glyph.getPen(), (design.xscale, 0, 0, 1, design.space, 0))
