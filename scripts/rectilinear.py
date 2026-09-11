"""Original polygon recipes for Cyrillic rectilinear letters."""
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing

@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/rectilinear.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def mix(a,b,t):
    if isinstance(a,dict):return {k:mix(a[k],b[k],t) for k in a}
    if isinstance(a,list):return [mix(x,y,t) for x,y in zip(a,b)]
    return a+(b-a)*t


def outline(ch,p):
    l,r,h,b=p['left'],p['right'],p['top'],p['bottom'];bt,bb=p['barTop'],p['barBottom'];st=p['stems']
    if ch=='П':
        (l,lr),(rl,r)=st
        points=[(l,b),(l,h),(r,h),(r,b),(rl,b),(rl,bb),(lr,bb),(lr,b)]
    elif ch=='Т':
        sl,sr=st[0]
        points=[(l,bb),(l,h),(r,h),(r,bb),(sr,bb),(sr,b),(sl,b),(sl,bb)]
    elif ch=='Н':
        (l,lr),(rl,r)=st
        points=[(l,b),(l,h),(lr,h),(lr,bt),(rl,bt),(rl,h),(r,h),(r,b),(rl,b),(rl,bb),(lr,bb),(lr,b)]
    else:
        b=bb
        points=[(st[0][0],b)]
        body_stems=st[:-1] if ch in 'ЦЩ' else st
        for i,(sl,sr) in enumerate(body_stems):
            points.extend([(sl,h),(sr,h),(sr,bt)])
            if i+1<len(body_stems):points.append((body_stems[i+1][0],bt))
        if ch in 'ЦЩ':
            tl,tr,tb=p['tail'];points.extend([(tr,bt),(tr,tb),(tl,tb),(tl,b)])
        else:points.append((st[-1][1],b))
    drawing=Drawing();drawing.polygon(points)
    if ch in 'ЦЩ':drawing.rect(st[-1][0],bb,st[-1][1]-st[-1][0],h-bb)
    return drawing


def apply(glyph,key,design):
    ch=chr(int(key[3:],16)) if key.startswith('uni') and len(key)==7 else key
    data=load().get(ch)
    if data is None:return
    lo,hi=(100,400) if design.weight<=400 else (400,900)
    weight=(design.weight-lo)/(hi-lo)
    a=mix(data[str(lo)]['text'],data[str(lo)]['display'],design.display)
    b=mix(data[str(hi)]['text'],data[str(hi)]['display'],design.display)
    params=mix(a,b,weight)
    glyph.clearContours();outline(ch.upper(),params).replay(glyph.getPen())
    # Both calibration sizes have zero portable tracking. Other optical sizes
    # receive the existing common HVAR/gvar tracking field during compilation.
    glyph.width=params['advance']
