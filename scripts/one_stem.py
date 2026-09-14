"""One: independent upright and a rising band bounded by two line equations."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from parameters import at_location


def construction(p):
    left,right=p['extent'];stem=p['stem'];height=p['height'];a,b=p['upper'];c,d=p['lower'];end=(height-b)/a
    shape=Drawing();shape.polygon([(left,c*left+d),(left,a*left+b),(end,height),(right,height),(right,min(height,c*right+d))]);shape.rect(stem,0,right-stem,height);return shape


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/one-stem.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='one':return
    glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
