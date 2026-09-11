"""Original single-storey g: eight exterior arcs and four counter arcs."""
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing
from rectilinear import mix

NAMES=['tailRightY','tailBottomX','tipOuterX','tipInnerX','tipY','tailInnerRightY','tailInnerBottomX','tailInnerBottomY',
       'bodyBottomX','bodyBottomY','bodyLeftY','bodyTopX','joinBottomX','joinBottomY','joinTopX','joinTopY',
       'innerLeftX','innerLeftY','innerRightX','innerRightY','innerTopX','innerTopY','innerBottomX','innerBottomY']


def contours(p,k):
    s,st=p['stem'],p['stemTop']
    ry,bx,to,ti,ty,iry,ibx,iby,bbx,bby,bly,btx,jbx,jby,jtx,jty,il,ily,ir,icy,it,ity,ib,icyb=[p[n] for n in NAMES]
    outer=[(1,ry),
        ((1,ry-ry*k[0]),(bx+(1-bx)*k[1],0),(bx,0)),
        ((bx-(bx-to)*k[2],0),(to+(bx-to)*k[3],ty-ty*k[4]),(to,ty)),
        (ti,ty),
        ((ti+(ibx-ti)*k[5],ty-(ty-iby)*k[6]),(ibx-(ibx-ti)*k[7],iby),(ibx,iby)),
        ((ibx+(s-ibx)*k[8],iby),(s,iry-(iry-iby)*k[9]),(s,iry)),
        (s,jby),(jbx,jby),
        ((jbx-(jbx-bbx)*k[10],jby-(jby-bby)*k[11]),(bbx+(jbx-bbx)*k[12],bby),(bbx,bby)),
        ((bbx-bbx*k[13],bby),(0,bly-(bly-bby)*k[14]),(0,bly)),
        ((0,bly+(1-bly)*k[15]),(btx-btx*k[16],1),(btx,1)),
        ((btx+(jtx-btx)*k[17],1),(jtx-(jtx-btx)*k[18],jty+(1-jty)*k[19]),(jtx,jty)),
        (s,jty),(s,st)]
    inner=[
        ((il,ily+(ity-ily)*k[20]),(it-(it-il)*k[21],ity),(it,ity)),
        ((it+(ir-it)*k[22],ity),(ir,icy+(ity-icy)*k[23]),(ir,icy)),
        ((ir,icy-(icy-icyb)*k[24]),(ib+(ir-ib)*k[25],icyb),(ib,icyb)),
        ((ib-(ib-il)*k[26],icyb),(il,ily-(ily-icyb)*k[27]),(il,ily))]
    return [((1,st),outer,False),((il,ily),inner,True)]


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/lower-g.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    data=load().get(key)
    if data is None:return
    lo,hi=(100,400) if design.weight<=400 else (400,900)
    a=mix(data[str(lo)]['text'],data[str(lo)]['display'],design.display)
    b=mix(data[str(hi)]['text'],data[str(hi)]['display'],design.display)
    p=mix(a,b,(design.weight-lo)/(hi-lo));drawing=Drawing()
    for start,segments,counter in contours(p['parameters'],p['handles']):drawing.outline(start,segments,counter)
    left,bottom,right,top=p['bounds'];glyph.clearContours()
    drawing.replay(glyph.getPen(),(right-left,0,0,top-bottom,left,bottom))
    # Keep the separately validated advance model.
