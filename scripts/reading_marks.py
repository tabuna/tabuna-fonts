"""Authored reading diacritics shared by case/script profiles, with scalar placement."""
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing
from rectilinear import mix

DEFAULTS={'\u0302':'circumflex','\u0306':'breve','\u0307':'dotabove'}
PROFILE_NAMES={'circumflex':'uni0302','breve':'uni0306','dotabove':'uni0307',
    'circumflex.cap':'uni0302.cap','circumflex.ascender':'uni0302.ascender','breve.cap':'uni0306.cap',
    'breve.cyrl':'uni0306.cyrl','breve.cyrl.cap':'uni0306.cyrl.cap','dotabove.cap':'uni0307.cap','commaabove.g':'commaabove.g'}


def contours(kind,p):
    if kind=='circumflex':
        return [((0,0),[(p['topLeft'],1),(p['topRight'],1),(1,0),(p['innerRight'],0),(p['innerX'],p['innerY']),(p['innerLeft'],0)])]
    if kind=='commaabove':return [((0,0),[(p['topLeft'],1),(1,1),(p['bottomRight'],0)])]
    if kind=='dotabove':
        k=p['k'];return [((0,.5),[((0,.5+k/2),(.5-k/2,1),(.5,1)),((.5+k/2,1),(1,.5+k/2),(1,.5)),((1,.5-k/2),(.5+k/2,0),(.5,0)),((.5-k/2,0),(0,.5-k/2),(0,.5))])]
    if kind=='breve':
        ox,ix,iy,il,ir=p['outerX'],p['innerX'],p['innerY'],p['innerLeft'],p['innerRight'];k=p['handles']
        return [((0,1),[((ox*k[0],1-k[1]),(ox-ox*k[2],0),(ox,0)),
            ((ox+(1-ox)*k[3],0),(1-(1-ox)*k[4],1-k[5]),(1,1)),(ir,1),
            ((ir-(ir-ix)*k[6],1-(1-iy)*k[7]),(ix+(ir-ix)*k[8],iy),(ix,iy)),
            ((ix-(ix-il)*k[9],iy),(il+(ix-il)*k[10],1-(1-iy)*k[11]),(il,1))])]
    raise ValueError(kind)


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/reading-marks.json'
    return json.loads(path.read_text()) if path.exists() else {}


def interpolate(data,design):
    lo,hi=(100,400) if design.weight<=400 else (400,900)
    a=mix(data[str(lo)]['text'],data[str(lo)]['display'],design.display)
    b=mix(data[str(hi)]['text'],data[str(hi)]['display'],design.display)
    return mix(a,b,(design.weight-lo)/(hi-lo))


def draw_profile(glyph,profile,design):
    data=load();record=data['profiles'][profile];p=interpolate(record['masters'],design)
    drawing=Drawing()
    for start,segments in contours(record['kind'],p['parameters']):drawing.outline(start,segments)
    w,h=p['dimensions'];dx,dy=p['defaultOffset'];glyph.clearContours()
    drawing.replay(glyph.getPen(),(w,0,0,h,dx-w/2,dy));glyph.width=0


def apply_mark(glyph,ch,design):
    if ch in DEFAULTS and load():draw_profile(glyph,DEFAULTS[ch],design)


def attach(source,ch,glyph):
    data=load();record=data.get('placements',{}).get(ch)
    if record is None:return
    from ufoLib2.objects import Component,Anchor
    profile=record['profile'];key=PROFILE_NAMES[profile]
    if key not in source.f:
        mark=source.f.newGlyph(key);draw_profile(mark,profile,source.d)
        mark.anchors.extend([Anchor(name='_top',x=0,y=0),Anchor(name='top',x=0,y=190)])
    pos=interpolate(record['masters'],source.d)
    shape=interpolate(data['profiles'][profile]['masters'],source.d)
    dx,dy=shape['defaultOffset']
    assert len(glyph.components)==2 and not len(glyph.contours),(ch,'Expected base and one canonical mark')
    glyph.components[1]=Component(key,(1,0,0,1,pos['x']-dx,pos['y']-dy))


def features(font):
    if not load():return ''
    cap=[];cyrlcap=[];cyrllower=[]
    for glyph in font:
        if not glyph.unicodes:continue
        ch=chr(glyph.unicodes[0])
        if ch.isalpha() and ch.isupper():cap.append(glyph.name)
        if 0x400<=ord(ch)<=0x491 and ch.isalpha():
            (cyrlcap if ch.isupper() else cyrllower).append(glyph.name)
    result='@ReadingCaps = ['+' '.join(sorted(cap))+'];\n'
    result+='@ReadingCyrlCaps = ['+' '.join(sorted(cyrlcap))+'];\n'
    result+='@ReadingCyrlLower = ['+' '.join(sorted(cyrllower))+'];\n'
    result+='feature ccmp {\n'
    result+="  sub @ReadingCyrlCaps uni0306' by uni0306.cyrl.cap;\n"
    result+="  sub @ReadingCyrlLower uni0306' by uni0306.cyrl;\n"
    result+="  sub @ReadingCaps uni0302' by uni0302.cap;\n"
    result+="  sub @ReadingCaps uni0306' by uni0306.cap;\n"
    result+="  sub @ReadingCaps uni0307' by uni0307.cap;\n"
    result+="  sub h uni0302' by uni0302.ascender;\n"
    result+="  sub g uni0327' by commaabove.g;\n"
    return result+'} ccmp;\n'
