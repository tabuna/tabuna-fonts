"""Double quotation chevrons reuse the comparison-sign line model."""
import json
from functools import lru_cache
from pathlib import Path
from parameters import at_location
from comparison_signs import construction as chevron
from geometry import Drawing


def construction(profile, reverse=False):
    drawing = Drawing()
    for part in profile['parts']:
        chevron(part, reverse=reverse).replay(drawing.pen)
    return drawing


@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1]/'sources/guillemets.json').read_text())['glyphs']


def apply(glyph,key,design):
    profiles=load().get(key)
    if profiles is None:return
    glyph.clearContours()
    construction(at_location(profiles,design), reverse=key=='guillemotright').replay(glyph.getPen())
