"""R: shared full-height bowl and a separately measured diagonal leg."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from upper_bowls import drawing as bowl
from math_bands import construction as bands
from parameters import at_location


def construction(p):
 d=bowl(p);bands(dict(bars=[],slashes=[p['leg']])).replay(d.pen);l,b,r,t=p['bounds'];out=Drawing();d.replay(out.pen,(r-l,0,0,t-b,l,b));return out

@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/r-bowl.json').read_text())['weights']
def apply(glyph,key,design):
 if key!='R':return
 glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
