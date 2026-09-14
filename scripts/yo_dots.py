"""Precomposed Ё/ё retain their base and use independently measured round dots."""
import json
from pathlib import Path
from functools import lru_cache
from parameters import at_location
from quadratic_round import contour
@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/yo-dots.json').read_text())['glyphs']
def apply(glyph,ch,design):
 if ch not in load():return
 assert len(glyph.components)==2 and not glyph.contours
 del glyph.components[1:]
 for p in at_location(load()[ch],design):contour(p['bounds'],p['quadrants']).replay(glyph.getPen())
