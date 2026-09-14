"""Ruble reuses the authored full-height bowl, with two measured crossbars."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from upper_bowls import drawing as bowl
from parameters import at_location


def construction(p):
    d=bowl(p)
    for b in p['bars']:d.rect(b['left'],b['bottom'],b['right']-b['left'],b['top']-b['bottom'])
    l,b,r,t=p['bounds'];out=Drawing();d.replay(out.pen,(r-l,0,0,t-b,l,b));return out


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/ruble-bowl.json').read_text())['weights']


def apply(glyph,key,design):
    if key not in ('uni20BD','ruble'):return
    glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
