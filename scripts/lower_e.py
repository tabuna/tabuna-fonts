"""Original e construction: six outer arcs and two counter arcs."""
from parameters import at_location
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing

NAMES=['crossY','innerLeftX','innerBottomX','innerBottomY','tipInnerX','tipOuterX','tipY',
       'outerBottomX','outerLeftY','outerTopX','outerRightY','counterLeftX','counterRightX',
       'counterBottomY','counterTopX','counterTopY']


def contours(p,k):
    cy,il,ib,iby,ti,to,ty,ob,ly,ot,ry,cl,cr,cb,ct,cty=[p[n] for n in NAMES]
    ity=p.get('tipInnerY',ty)
    outer=[(il,cy),
        ((il,cy-(cy-iby)*k[0]),(ib-(ib-il)*k[1],iby),(ib,iby)),
        ((ib+(ti-ib)*k[2],iby),(ti-(ti-ib)*k[3],ity-(ity-iby)*k[4]),(ti,ity)),
        (to,ty),
        ((to-(to-ob)*k[5],ty-ty*k[6]),(ob+(to-ob)*k[7],0),(ob,0)),
        ((ob-ob*k[8],0),(0,ly-ly*k[9]),(0,ly)),
        ((0,ly+(1-ly)*k[10]),(ot-ot*k[11],1),(ot,1)),
        ((ot+(1-ot)*k[12],1),(1,ry+(1-ry)*k[13]),(1,ry))]
    inner=[(cr,cb),
        ((cr-(cr-ct)*k[14],cb+(cty-cb)*k[15]),(ct+(cr-ct)*k[16],cty),(ct,cty)),
        ((ct-(ct-cl)*k[17],cty),(cl+(ct-cl)*k[18],cb+(cty-cb)*k[19]),(cl,cb))]
    return [((1,cy),outer,False),((cl,cb),inner,True)]


@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1]/'sources/lower-e.json').read_text())['glyphs']


def apply(glyph,key,design):
    ch={'uni0435':'е'}.get(key,key)
    if ch not in ('e','е'):return
    data=load()[ch]
    p=at_location(data, design);drawing=Drawing()
    for start,segments,counter in contours(p['parameters'],p['handles']):drawing.outline(start,segments,counter)
    left,bottom,right,top=p['bounds'];glyph.clearContours()
    drawing.replay(glyph.getPen(),(right-left,0,0,top-bottom,left,bottom));glyph.width=p['advance']
