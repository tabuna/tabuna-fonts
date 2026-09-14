"""A forked stem from four line equations, with optional horizontal bars."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from diagonal_bands import crossing
from parameters import at_location


def construction(p):
    l,r=p['stem'];top,bottom,floor=p['top'],p['bottom'],p['floor'];lo,li,ri,ro=(p[k] for k in ['left_outer','left_inner','right_inner','right_outer'])
    def at(line,y):return (line[0]*y+line[1],y)
    d=Drawing();d.polygon([(l,bottom),crossing((0,l),lo),at(lo,top),at(li,top),at(li,floor),at(ri,floor),at(ri,top),at(ro,top),crossing((0,r),ro),(r,bottom)])
    for b in p['bars']:d.rect(b['left'],b['bottom'],b['right']-b['left'],b['top']-b['bottom'])
    return d


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/forked-bands.json').read_text())['glyphs']


def apply(glyph,key,design):
    data=load().get(key)
    if data is None:return
    glyph.clearContours();construction(at_location(data,design)).replay(glyph.getPen())
