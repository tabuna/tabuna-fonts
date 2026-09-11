"""Independent Cyrillic з geometry, with matching cubic topology in all masters."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from rectilinear import mix


@lru_cache(maxsize=1)
def load():
    path = Path(__file__).resolve().parents[1]/'sources/ze-curves.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph, key, design):
    if key != 'uni0437': return
    data = load().get('з')
    if data is None: return
    lo, hi = (100, 400) if design.weight <= 400 else (400, 900)
    a = mix(data[str(lo)]['text'], data[str(lo)]['display'], design.display)
    b = mix(data[str(hi)]['text'], data[str(hi)]['display'], design.display)
    shape = mix(a, b, (design.weight-lo)/(hi-lo))
    curves = shape['curves']
    drawing = Drawing()
    drawing.outline(tuple(curves[0][0]), [[tuple(p) for p in c[1:]] for c in curves])
    glyph.clearContours()
    drawing.replay(glyph.getPen())
    # Advance and anchors remain the independently calibrated metrics.
