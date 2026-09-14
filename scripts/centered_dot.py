"""Middle dot as an independently controlled ellipse on the design grid."""
from functools import lru_cache
import json
from pathlib import Path
from geometry import Drawing
from parameters import at_location

def construction(p):
    d=Drawing();d.ellipse(*p['bounds']);return d

@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1]/'sources/centered-dot.json').read_text())['weights']

def apply(glyph,key,design):
    if key!='periodcentered':return
    glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
