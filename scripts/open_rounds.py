"""Original open-round construction: four outer and four inner cubic arcs."""
from parameters import at_location
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing

NAMES=['outerTopX','outerLeftY','outerBottomX','upperTipY','lowerTipY',
       'upperOuterX','lowerOuterX','innerLeftX','innerLeftY','innerTopX','innerTopY',
       'innerBottomX','innerBottomY','upperInnerX','lowerInnerX']


def contours(p,k):
    ot,ol,ob,uy,ly,uo,lo,il,ily,it,ity,ib,iby,ui,li=[p[n] for n in NAMES]
    iuy=p.get('upperInnerY',uy);ily_tip=p.get('lowerInnerY',ly)
    segments=[
        ((uo-(uo-ot)*k[0],uy+(1-uy)*k[1]),(ot+(uo-ot)*k[2],1),(ot,1)),
        ((ot-ot*k[3],1),(0,ol+(1-ol)*k[4]),(0,ol)),
        ((0,ol-ol*k[5]),(ob-ob*k[6],0),(ob,0)),
        ((ob+(lo-ob)*k[7],0),(lo-(lo-ob)*k[8],ly-ly*k[9]),(lo,ly)),
        (li,ily_tip),
        ((li-(li-ib)*k[10],ily_tip-(ily_tip-iby)*k[11]),(ib+(li-ib)*k[12],iby),(ib,iby)),
        ((ib-(ib-il)*k[13],iby),(il,ily-(ily-iby)*k[14]),(il,ily)),
        ((il,ily+(ity-ily)*k[15]),(it-(it-il)*k[16],ity),(it,ity)),
        ((it+(ui-it)*k[17],ity),(ui-(ui-it)*k[18],iuy+(ity-iuy)*k[19]),(ui,iuy))]
    return [((uo,uy),segments,False)]


@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1]/'sources/open-rounds.json').read_text())['glyphs']


def apply(glyph,key,design):
    ch={'uni0441':'с','uni0421':'С'}.get(key,key)
    if ch not in ('c','C','с','С'):return
    data=load()[ch]
    p=at_location(data, design);drawing=Drawing()
    for start,segments,counter in contours(p['parameters'],p['handles']):drawing.outline(start,segments,counter)
    left,bottom,right,top=p['bounds'];glyph.clearContours()
    drawing.replay(glyph.getPen(),(right-left,0,0,top-bottom,left,bottom));glyph.width=p['advance']
