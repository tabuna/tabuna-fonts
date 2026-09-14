"""Original single-polygon recipes for I/H/E/F/L and Cyrillic Е/І."""
from parameters import at_location
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing

@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/latin-rectangles.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def polygon(ch,p):
    ch={'Е':'E','І':'I'}.get(ch,ch)
    l,r,b,h=p['left'],p['right'],p['bottom'],p['top']
    if ch=='I':return [(l,b),(l,h),(r,h),(r,b)]
    s=p['stemRight']
    if ch=='H':
        rs=p['rightStemLeft'];bb,bt=p['middleBottom'],p['middleTop']
        return [(l,b),(l,h),(s,h),(s,bt),(rs,bt),(rs,h),(r,h),(r,b),(rs,b),(rs,bb),(s,bb),(s,b)]
    if ch=='L':return [(l,b),(l,h),(s,h),(s,p['bottomTop']),(r,p['bottomTop']),(r,b)]
    mb,mt,mr=p['middleBottom'],p['middleTop'],p['middleRight']
    points=[(l,b),(l,h),(r,h),(r,p['topBottom']),(s,p['topBottom']),(s,mt),(mr,mt),(mr,mb),(s,mb)]
    return points+([(s,p['bottomTop']),(p['bottomRight'],p['bottomTop']),(p['bottomRight'],b)] if ch=='E' else [(s,b)])


def apply(glyph,key,design):
    ch=chr(int(key[3:],16)) if key.startswith('uni') and len(key)==7 else key
    data=load().get(ch)
    if data is None:return
    params=at_location(data, design)
    drawing=Drawing();drawing.polygon(params['points'])
    glyph.clearContours();drawing.replay(glyph.getPen());glyph.width=params['advance']
