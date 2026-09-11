"""Our upper/full-height bowl construction for P, Cyrillic Р, and D."""
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing
from bowls import arc,mix

@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/upper-bowls.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def drawing(p):
    d=Drawing();sl,sr,h,b=p['stemLeft'],p['stemRight'],p['top'],p['bottom']
    outer,inner=p['outer'],p['inner'];ou,ol=arc(outer,True),arc(outer,False)
    d.outline((sl,b),[(sl,outer['top']),ou[-1],tuple(list(reversed(ou))[1:]),tuple(ol[1:]),(sr,outer['bottom']),(sr,b)])
    iu,il=arc(inner,True),arc(inner,False)
    d.outline((sr,inner['bottom']),[il[-1],tuple(list(reversed(il))[1:]),tuple(iu[1:]),(sr,inner['top'])],counter=True)
    return d


def apply(glyph,key,design):
    ch=chr(int(key[3:],16)) if key.startswith('uni') and len(key)==7 else key
    data=load().get(ch)
    if data is None:return
    lo,hi=(100,400) if design.weight<=400 else (400,900)
    a=mix(data[str(lo)]['text'],data[str(lo)]['display'],design.display)
    b=mix(data[str(hi)]['text'],data[str(hi)]['display'],design.display)
    p=mix(a,b,(design.weight-lo)/(hi-lo))
    glyph.clearContours();drawing(p).replay(glyph.getPen());glyph.width=p['advance']
