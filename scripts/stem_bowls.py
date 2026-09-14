"""Authored lower-case stem and bowl construction: b/d/p/q/Cyrillic р."""
from parameters import at_location
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing

NAMES=['joinTopX','joinTopY','joinBottomX','joinBottomY','outerTopX','outerTopY','outerBottomX','outerBottomY','outerRightY',
       'innerLeftX','innerLeftY','innerRightX','innerRightY','innerTopX','innerTopY','innerBottomX','innerBottomY']


def contours(p,k):
    s,st,sb=p['stem'],p['stemTop'],p['stemBottom']
    jtx,jty,jbx,jby,tx,ty,bx,by,ry,il,ily,ir,iry,it,ity,ib,iby=[p[n] for n in NAMES]
    outer=[(0,st),(s,st),(s,jty),(jtx,jty),
        ((jtx+(tx-jtx)*k[0],jty+(ty-jty)*k[1]),(tx-(tx-jtx)*k[2],ty),(tx,ty)),
        ((tx+(1-tx)*k[3],ty),(1,ry+(ty-ry)*k[4]),(1,ry)),
        ((1,ry-(ry-by)*k[5]),(bx+(1-bx)*k[6],by),(bx,by)),
        ((bx-(bx-jbx)*k[7],by),(jbx+(bx-jbx)*k[8],jby-(jby-by)*k[9]),(jbx,jby)),
        (s,jby),(s,sb)]
    inner=[
        ((il,ily+(ity-ily)*k[10]),(it-(it-il)*k[11],ity),(it,ity)),
        ((it+(ir-it)*k[12],ity),(ir,iry+(ity-iry)*k[13]),(ir,iry)),
        ((ir,iry-(iry-iby)*k[14]),(ib+(ir-ib)*k[15],iby),(ib,iby)),
        ((ib-(ib-il)*k[16],iby),(il,ily-(ily-iby)*k[17]),(il,ily))]
    return [((0,sb),outer,False),((il,ily),inner,True)]


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/stem-bowls.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    ch=chr(int(key[3:],16)) if key.startswith('uni') and len(key)==7 else key
    data=load().get(ch)
    if data is None:return
    p=at_location(data, design);drawing=Drawing()
    for start,segments,counter in contours(p['parameters'],p['handles']):drawing.outline(start,segments,counter)
    left,bottom,right,top=p['bounds'];glyph.clearContours()
    transform=(-(right-left),0,0,top-bottom,right,bottom) if ch in 'dq' else (right-left,0,0,top-bottom,left,bottom)
    drawing.replay(glyph.getPen(),transform)
    # Advances already have separate validated models. This module edits outlines only.
