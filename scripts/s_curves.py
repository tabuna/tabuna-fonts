"""Original S/s construction: twelve cubics with smooth central joins."""
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing
from rectilinear import mix

NAMES=['upperOuterX','upperTipY','outerTopX','outerLeftX','outerLeftY',
       'lowerMidY','lowerSlope','lowerRightX','lowerRightY','lowerBottomX','lowerBottomY',
       'lowerTipX','lowerTipY','outerBottomX','outerRightY','upperMidY','upperSlope',
       'upperLeftX','upperLeftY','upperTopX','upperTopY','upperTipX']


def contours(p,k):
    uo,uy,ot,ol,oly,lmy,ls,lr,lry,lb,lby,li,ly,ob,ory,umy,us,ul,uly,ut,uty,ui=[p[n] for n in NAMES]
    segments=[
        ((uo-(uo-ot)*k[0],uy+(1-uy)*k[1]),(ot+(uo-ot)*k[2],1),(ot,1)),
        ((ot-(ot-ol)*k[3],1),(ol,oly+(1-oly)*k[4]),(ol,oly)),
        ((ol,oly-(oly-lmy)*k[5]),(.5-(.5-ol)*k[6],lmy+(.5-ol)*k[6]*ls),(.5,lmy)),
        ((.5+(lr-.5)*k[7],lmy-(lr-.5)*k[7]*ls),(lr,lry+(lmy-lry)*k[8]),(lr,lry)),
        ((lr,lry-(lry-lby)*k[9]),(lb+(lr-lb)*k[10],lby),(lb,lby)),
        ((lb-(lb-li)*k[11],lby),(li+(lb-li)*k[12],ly-(ly-lby)*k[13]),(li,ly)),
        (0,ly),
        ((ob*k[14],ly-ly*k[15]),(ob-ob*k[16],0),(ob,0)),
        ((ob+(1-ob)*k[17],0),(1,ory-ory*k[18]),(1,ory)),
        ((1,ory+(umy-ory)*k[19]),(.5+.5*k[20],umy-.5*k[20]*us),(.5,umy)),
        ((.5-(.5-ul)*k[21],umy+(.5-ul)*k[21]*us),(ul,uly-(uly-umy)*k[22]),(ul,uly)),
        ((ul,uly+(uty-uly)*k[23]),(ut-(ut-ul)*k[24],uty),(ut,uty)),
        ((ut+(ui-ut)*k[25],uty),(ui-(ui-ut)*k[26],uy+(uty-uy)*k[27]),(ui,uy))]
    return [((uo,uy),segments,False)]


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/s-curves.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    ch={'uni0405':'Ѕ','uni0455':'ѕ'}.get(key,key);data=load().get(ch)
    if data is None:return
    lo,hi=(100,400) if design.weight<=400 else (400,900)
    a=mix(data[str(lo)]['text'],data[str(lo)]['display'],design.display)
    b=mix(data[str(hi)]['text'],data[str(hi)]['display'],design.display)
    p=mix(a,b,(design.weight-lo)/(hi-lo));drawing=Drawing()
    for start,segments,counter in contours(p['parameters'],p['handles']):drawing.outline(start,segments,counter)
    left,bottom,right,top=p['bounds'];glyph.clearContours()
    drawing.replay(glyph.getPen(),(right-left,0,0,top-bottom,left,bottom))
    # Retain the already calibrated advances for each script independently.
