"""Cyrillic E: mirrored shared open-round curves and a measured crossbar."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from open_rounds import contours
from parameters import at_location


def body(p):
 d=Drawing()
 for start,segments,counter in contours(p['parameters'],p['handles']):d.outline(start,segments,counter)
 return d


def construction(p):
 l,b,r,t=p['bounds'];d=Drawing();body(p).replay(d.pen,(-(r-l),0,0,t-b,r,b));x,y,w,h=p['bar'];d.rect(x,y,w,h);return d

@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/e-reversed.json').read_text())['glyphs']
def apply(glyph,key,design):
 p=load().get(key)
 if p is not None:glyph.clearContours();construction(at_location(p,design)).replay(glyph.getPen())
