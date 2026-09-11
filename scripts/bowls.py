"""Our authored Cyrillic bowl construction with scalar native calibration."""
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing

@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/bowls.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def mix(a,b,t):
    if isinstance(a,dict):return {k:mix(a[k],b[k],t) for k in a}
    if isinstance(a,list):return [mix(x,y,t) for x,y in zip(a,b)]
    return a+(b-a)*t


def arc(p,upper):
    q=p['upper' if upper else 'lower'];r,cy,y=p['right'],p['centerY'],p['top' if upper else 'bottom'];end=q['endX']
    return [(r,cy),(r,cy+(y-cy)*q['ky']),(end+(r-end)*q['kx'],y),(end,y)]


def drawing(p):
    d=Drawing();sl,sr,h,b=p['stemLeft'],p['stemRight'],p['top'],p['bottom']
    outer,inner=p['outer'],p['inner'];ou,ol=arc(outer,True),arc(outer,False)
    if 'head' in p:
        hl,hb=p['head'];prefix=[(sl,hb),(hl,hb),(hl,h),(sr,h)]
    else:prefix=[(sl,h),(sr,h)]
    d.outline((sl,b),prefix+[(sr,outer['top']),ou[-1],tuple(list(reversed(ou))[1:]),tuple(ol[1:])])
    iu,il=arc(inner,True),arc(inner,False)
    d.outline((sr,inner['bottom']),[il[-1],tuple(list(reversed(il))[1:]),tuple(iu[1:]),(sr,inner['top'])],counter=True)
    if 'post' in p:
        l,r,b,t=p['post'];d.rect(l,b,r-l,t-b)
    return d


def apply(glyph,key,design):
    ch=chr(int(key[3:],16)) if key.startswith('uni') and len(key)==7 else key
    data=load().get(ch)
    if data is None:return
    lo,hi=(100,400) if design.weight<=400 else (400,900)
    a=mix(data[str(lo)]['text'],data[str(lo)]['display'],design.display)
    b=mix(data[str(hi)]['text'],data[str(hi)]['display'],design.display)
    params=mix(a,b,(design.weight-lo)/(hi-lo))
    glyph.clearContours();drawing(params).replay(glyph.getPen());glyph.width=params['advance']
