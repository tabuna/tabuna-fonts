"""Double quotation chevrons reuse the comparison-sign line model."""
import json
from functools import lru_cache
from pathlib import Path
from parameters import at_location
from comparison_signs import construction


@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1]/'sources/guillemets.json').read_text())['glyphs']


def apply(glyph,key,design):
    profiles=load().get(key)
    if profiles is None:return
    glyph.clearContours()
    for p in at_location(profiles,design)['parts']:
        construction(p,reverse=key=='guillemotright').replay(glyph.getPen())
