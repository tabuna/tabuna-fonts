"""Zhe: a central stem and mirrored rising/falling bands with level joins."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from parameters import at_location


def construction(p):
    sl,sr=p['stem'];h=p['top'];upper,lower=p['upper'],p['lower']
    ul,ur=upper['left'],upper['right'];ll,lr=lower['left'],lower['right']
    jt,jb=p['join'];uc,lc=p['caps'];root=sr-(sr-sl)/8
    x=lambda line,y:line[0]*y+line[1]
    side=Drawing()
    # The horizontal inner joins are explicit design constraints. Hidden
    # outer caps extend into the stem; nonzero winding forms the union.
    side.polygon([(root,jt),(x(ul,jt),jt),(x(ul,h),h),(x(ur,h),h),
                  (x(ur,uc),uc),(root,uc)])
    side.polygon([(x(ll,0),0),(x(ll,jb),jb),(root,jb),
                  (root,lc),(x(lr,lc),lc),(x(lr,0),0)])
    # Stem edge compensation is independent of the reflected branch axis.
    left_edge, right_edge = p.get('stem_edge_compensation', (0, 0))
    d=Drawing();d.rect(sl+left_edge,0,sr-sl+right_edge-left_edge,h)
    side.replay(d.pen)
    side.replay(d.pen,(-1,0,0,1,sl+sr,0))
    return d


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/branched-stems.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    data=load().get(key)
    if data is not None:
        glyph.clearContours()
        construction(at_location(data,design)).replay(glyph.getPen())
