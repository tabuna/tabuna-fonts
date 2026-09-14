"""Original G: four exterior and four interior cubics, with a level crossbar."""
from parameters import at_location
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing

NAMES=['outerTopX','outerLeftY','outerBottomX','upperTipY','upperOuterX','upperInnerX',
       'outerRightY','barTopY','barBottomY','barLeftX','innerRightX',
       'innerLeftX','innerLeftY','innerTopX','innerTopY','innerBottomX','innerBottomY']


def contours(p,k):
    ot,ol,ob,uy,uo,ui,ory,bt,bb,bl,ir,il,ily,it,ity,ib,iby=[p[n] for n in NAMES]
    segments=[
        ((uo-(uo-ot)*k[0],uy+(1-uy)*k[1]),(ot+(uo-ot)*k[2],1),(ot,1)),
        ((ot-ot*k[3],1),(0,ol+(1-ol)*k[4]),(0,ol)),
        ((0,ol-ol*k[5]),(ob-ob*k[6],0),(ob,0)),
        ((ob+(1-ob)*k[7],0),(1,ory-ory*k[8]),(1,ory)),
        (1,bt),(bl,bt),(bl,bb),(ir,bb),
        ((ir,bb-(bb-iby)*k[9]),(ib+(ir-ib)*k[10],iby),(ib,iby)),
        ((ib-(ib-il)*k[11],iby),(il,ily-(ily-iby)*k[12]),(il,ily)),
        ((il,ily+(ity-ily)*k[13]),(it-(it-il)*k[14],ity),(it,ity)),
        ((it+(ui-it)*k[15],ity),(ui-(ui-it)*k[16],uy+(ity-uy)*k[17]),(ui,uy))]
    return [((uo,uy),segments,False)]


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/upper-g.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    data=load().get(key)
    if data is None:return
    p=at_location(data, design);drawing=Drawing()
    for start,segments,counter in contours(p['parameters'],p['handles']):drawing.outline(start,segments,counter)
    left,bottom,right,top=p['bounds'];glyph.clearContours()
    drawing.replay(glyph.getPen(),(right-left,0,0,top-bottom,left,bottom))
    # Advance calibration is independent of outline fitting.
