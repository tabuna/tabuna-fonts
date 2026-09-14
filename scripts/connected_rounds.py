"""Connected round letters: shared oval contours, a stem and a crossbar."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from rounds import contour
from parameters import at_location


def construction(p):
    d=Drawing();ring=p['ring']
    for index,field in enumerate(['outerHandles','innerHandles']):contour(ring['bounds'][index],ring[field],index==1).replay(d.pen)
    for b in [p['stem'],p['bar']]:d.rect(b['left'],b['bottom'],b['right']-b['left'],b['top']-b['bottom'])
    return d


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/connected-rounds.json').read_text())['glyphs']


def apply(glyph,key,design):
    p=load().get(key)
    if p is None:return
    glyph.clearContours();construction(at_location(p,design)).replay(glyph.getPen())
