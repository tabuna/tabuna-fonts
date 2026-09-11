"""Accepted independent closed outlines; each glyph owns all of its master data."""
import json
from functools import lru_cache
from pathlib import Path
from fontTools.agl import UV2AGL
from geometry import Drawing
from rectilinear import mix


@lru_cache(maxsize=1)
def load():
    path = Path(__file__).resolve().parents[1]/'sources/reconstructed-bowls.json'
    if not path.exists(): return {}
    glyphs = json.loads(path.read_text())['glyphs']
    return {UV2AGL.get(ord(ch), f'uni{ord(ch):04X}'): data for ch, data in glyphs.items()}


def raw(design, character):
    key = UV2AGL.get(ord(character), f'uni{ord(character):04X}')
    if key not in load(): return None
    # The scalar advance basis is retained; no old outline is constructed.
    width, heavy_delta = {'uni0417': (480, 0), 'three': (478, 18), 'two': (477, 0)}[key]
    return Drawing(), width+max(0, (design.weight-400)/500)*heavy_delta


def apply(glyph, key, design):
    entry = load().get(key)
    if entry is None: return
    data = entry['weights']
    lo, hi = (100, 400) if design.weight <= 400 else (400, 900)
    a = mix(data[str(lo)]['text'], data[str(lo)]['display'], design.display)
    b = mix(data[str(hi)]['text'], data[str(hi)]['display'], design.display)
    shape = mix(a, b, (design.weight-lo)/(hi-lo))
    curves = shape['curves']
    drawing = Drawing()
    drawing.outline(tuple(curves[0][0]), [[tuple(p) for p in c[1:]] for c in curves])
    glyph.clearContours()
    drawing.replay(glyph.getPen())
