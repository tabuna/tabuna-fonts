"""Dollar reuses the shared twelve-cubic S and a separate vertical stem."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from s_curves import contours
from parameters import at_location


def body(p):
    d=Drawing()
    for start,segments,counter in contours(p['parameters'],p['handles']):d.outline(start,segments,counter)
    return d


def construction(p):
    l,b,r,t=p['bounds'];d=Drawing();body(p).replay(d.pen,(r-l,0,0,t-b,l,b));s=p['stem'];d.rect(s['left'],s['bottom'],s['right']-s['left'],s['top']-s['bottom']);return d


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/dollar-s.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='dollar':return
    glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
