"""Six uses the shared bowl/counter/tail equations in a rotated frame."""
import json
from pathlib import Path
from functools import lru_cache
from nine_bowl import construction
from parameters import at_location

@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/six-bowl.json').read_text())['weights']
def apply(glyph,key,design):
 if key!='six':return
 p=at_location(load(),design);l,b,r,t=p['bounds'];glyph.clearContours();construction(p).replay(glyph.getPen(),(-1,0,0,-1,l+r,b+t))
