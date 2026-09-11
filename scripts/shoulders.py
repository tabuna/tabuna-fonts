"""Original shoulder model: measured scalar stems, crowns and tangent lengths."""
from pathlib import Path
from functools import lru_cache
import json
from fontTools.pens.recordingPen import RecordingPen

@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/shoulders.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


@lru_cache(maxsize=1)
def weight_masters():
    path=Path(__file__).resolve().parents[1]/'sources/shoulder-weights.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def mix_commands(a,b,t):
    if t==0:return a
    if t==1:return b
    assert [op for op,_ in a['commands']]==[op for op,_ in b['commands']]
    return {'advance':a['advance']+(b['advance']-a['advance'])*t,
            'commands':[(op,tuple(tuple(x+(y-x)*t for x,y in zip(p,q)) for p,q in zip(old,new)))
                        for (op,old),(_,new) in zip(a['commands'],b['commands'])]}


def blend(a,b,t):
    if isinstance(a,dict):return {k:blend(a[k],b[k],t) for k in a}
    return a+(b-a)*t


def curve(p):
    sx,sy,cx,cy=(p[k] for k in ('sideX','sideY','crownX','crownY'))
    return [(sx,sy),(sx+(cx-sx)*p['sideHandleX'],sy+(cy-sy)*p['sideHandleY']),
            (cx-(cx-sx)*p['crownHandle'],cy),(cx,cy)]


def construction(p):
    pen=RecordingPen();l,r,b=p['left'],p['right'],p['bottom']
    ol,orr,il,ir=[curve(p[k]) for k in ('outerLeft','outerRight','innerLeft','innerRight')]
    pen.moveTo((l,b));pen.lineTo((l,p['capTop']));pen.lineTo((p['capRight'],p['capTop']));pen.lineTo(ol[0])
    pen.curveTo(*ol[1:]);pen.curveTo(*list(reversed(orr))[1:])
    if 'middleLeft' in p:
        ol2,or2,il2,ir2=[curve(p[k]) for k in ('outerLeft2','outerRight2','innerLeft2','innerRight2')]
        assert abs(orr[0][0]-ol2[0][0])<1e-6 and abs(orr[0][1]-ol2[0][1])<1e-6
        pen.curveTo(*ol2[1:]);pen.curveTo(*list(reversed(or2))[1:])
        pen.lineTo((r,b));pen.lineTo((p['rightInner'],b));pen.lineTo(ir2[0])
        pen.curveTo(*ir2[1:]);pen.curveTo(*list(reversed(il2))[1:])
        pen.lineTo((p['middleRight'],b));pen.lineTo((p['middleLeft'],b));pen.lineTo(ir[0])
        pen.curveTo(*ir[1:]);pen.curveTo(*list(reversed(il))[1:]);pen.lineTo((p['leftInner'],b));pen.closePath()
        return pen
    pen.lineTo((r,b));pen.lineTo((p['rightInner'],b));pen.lineTo(ir[0])
    pen.curveTo(*ir[1:]);pen.curveTo(*list(reversed(il))[1:]);pen.lineTo((p['leftInner'],b));pen.closePath()
    return pen


def split_inner(pen,all_curves=False):
    # Exact de Casteljau subdivision retains the original extreme-weight shape.
    def mid(a,b):return tuple((x+y)/2 for x,y in zip(a,b))
    commands=pen.value;indices=[i for i,(op,_) in enumerate(commands) if op=='curveTo']
    if not all_curves:indices=indices[-1:]
    for index in reversed(indices):
        p0=commands[index-1][1][-1];p1,p2,p3=commands[index][1]
        a,b,c=mid(p0,p1),mid(p1,p2),mid(p2,p3);d,e=mid(a,b),mid(b,c);f=mid(d,e)
        commands[index:index+1]=[('curveTo',(a,d,f)),('curveTo',(e,c,p3))]


def apply(glyph,key,design):
    masters=weight_masters().get(key)
    if masters:
        lo,hi=(100,400) if design.weight<=400 else (400,900)
        a=mix_commands(masters[str(lo)]['text'],masters[str(lo)]['display'],design.display)
        b=mix_commands(masters[str(hi)]['text'],masters[str(hi)]['display'],design.display)
        p=mix_commands(a,b,(design.weight-lo)/(hi-lo))
        pen=RecordingPen();pen.value=p['commands']
        glyph.clearContours();pen.replay(glyph.getPen());glyph.width=p['advance']
        return
    data=load().get(key)
    if data is None:return
    original=RecordingPen();glyph.draw(original);split_inner(original,key=='m')
    target=construction(blend(data['text'],data['display'],design.display))
    assert [op for op,_ in original.value]==[op for op,_ in target.value],key
    strength=(design.weight-100)/300 if design.weight<=400 else (900-design.weight)/500
    strength=max(0,min(1,strength));result=RecordingPen()
    for (op,old),(_,new) in zip(original.value,target.value):
        result.value.append((op,tuple(tuple(blend(a,b,strength) for a,b in zip(x,y)) for x,y in zip(old,new))))
    glyph.clearContours();result.replay(glyph.getPen())
