"""Phi: shared four-cubic outer/counter ovals and a vertical stem."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from rounds import contour
from parameters import at_location


def construction(p):
 d=Drawing()
 contour(p['outer']['bounds'],p['outer']['handles']).replay(d.pen)
 contour(p['inner']['bounds'],p['inner']['handles'],counter=True).replay(d.pen)
 l,b,r,t=p['stem'];d.rect(l,b,r-l,t-b)
 return d

@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/phi-bowls.json').read_text())['glyphs']
def apply(glyph,key,design):
 p=load().get(key)
 if p is not None:
  glyph.clearContours();construction(at_location(p,design)).replay(glyph.getPen())
