"""Z/z share two rectangular bars and an affine diagonal band."""
import json
from pathlib import Path
from functools import lru_cache
from parameters import at_location
from geometry import Drawing

def construction(p):
 bottom,top=p["bars"];d=p["slashes"][0]
 bl=bottom["x"]-bottom["width"]/2;br=bottom["x"]+bottom["width"]/2;bt=bottom["y"]+bottom["height"]/2;b=bottom["y"]-bottom["height"]/2
 tl=top["x"]-top["width"]/2;tr=top["x"]+top["width"]/2;tb=top["y"]-top["height"]/2;t=top["y"]+top["height"]/2
 la=d["slope"]-d["width_slope"]/2;lb=d["intercept"]-d["width"]/2;ra=d["slope"]+d["width_slope"]/2;rb=d["intercept"]+d["width"]/2
 low,up=p["lower_tip"],p["upper_tip"]
 shape=Drawing();shape.polygon([(tl,t),(tr,t),(tr,(tr-rb)/ra),(low,(low-rb)/ra),(low,bt),(br,bt),(br,b),(bl,b),(bl,(bl-lb)/la),(up,(up-lb)/la),(up,tb),(tl,tb)]);return shape
@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/z-bands.json').read_text())['glyphs']
def apply(glyph,key,design):
 if key not in load():return
 glyph.clearContours();glyph.clearComponents();construction(at_location(load()[key],design)).replay(glyph.getPen())
