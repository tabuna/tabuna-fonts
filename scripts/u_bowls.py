"""Original U/u: independent outer and inner lower bowls and straight stems."""
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing
from rectilinear import mix

NAMES=['outerLeftY','outerBottomX','outerRightY','innerLeftX','innerLeftY',
       'innerBottomX','innerBottomY','innerRightX','innerRightY']


def contours(p,k,lower=False):
    ol,ob,ory,il,ily,ib,iby,ir,iry=[p[n] for n in NAMES]
    jr=p['joinX'] if lower else 1
    segments=[(0,ol),((0,ol*(1-k[0])),(ob*(1-k[1]),0),(ob,0)),
        ((ob+(jr-ob)*k[2],0),(jr-(jr-ob)*k[8] if lower else 1,ory*(1-k[3])),(jr,ory))]
    if lower:segments.extend([(p['capLeft'],ory),(p['capLeft'],p['capBottomY']),(1,p['capBottomY'])])
    segments.extend([(1,1),(ir,1),(ir,iry),
        ((ir,iry-(iry-iby)*k[4]),(ib+(ir-ib)*k[5],iby),(ib,iby)),
        ((ib-(ib-il)*k[6],iby),(il,ily-(ily-iby)*k[7]),(il,ily)),(il,1)])
    return [((0,1),segments,False)]


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/u-bowls.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    data=load().get(key)
    if data is None:return
    lo,hi=(100,400) if design.weight<=400 else (400,900)
    a=mix(data[str(lo)]['text'],data[str(lo)]['display'],design.display)
    b=mix(data[str(hi)]['text'],data[str(hi)]['display'],design.display)
    p=mix(a,b,(design.weight-lo)/(hi-lo));drawing=Drawing()
    for start,segments,counter in contours(p['parameters'],p['handles'],key=='u'):drawing.outline(start,segments,counter)
    left,bottom,right,top=p['bounds'];glyph.clearContours()
    drawing.replay(glyph.getPen(),(right-left,0,0,top-bottom,left,bottom))
    # Preserve the existing, independently calibrated advance.
