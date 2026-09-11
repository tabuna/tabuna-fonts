"""Apply measured pair positions to our sources and inherited accent groups."""
from pathlib import Path
from functools import lru_cache
import json,unicodedata
from fontTools.misc.roundTools import otRound

@lru_cache(maxsize=1)
def load():
    return json.loads((Path(__file__).resolve().parents[1]/'sources/kerning.json').read_text())

def apply(font,design,charset,name):
    data=load();trained=set(data['characters'])
    def base(ch):
        # Latin and Cyrillic remain separate. Measured accented characters
        # retain their own pairs; other accents inherit their canonical base.
        return ch if ch in trained else unicodedata.normalize('NFD',ch)[0]
    groups={}
    for ch in charset:
        if ch.isalpha():groups.setdefault(base(ch),[]).append(name(ch))
    for side in (1,2):
        for ch,members in groups.items():font.groups[f'public.kern{side}.{name(ch)}']=list(members)
    for text in ('ff','fi','fl','ffi','ffl'):
        for side,ch in ((1,text[-1]),(2,text[0])):
            font.groups[f'public.kern{side}.{name(ch)}'].append(text+'.liga')
    for pair,weights in data['pairs'].items():
        a,b=pair
        left=f'public.kern1.{name(base(a))}' if a.isalpha() else name(a)
        right=f'public.kern2.{name(base(b))}' if b.isalpha() else name(b)
        text,display=weights[str(design.weight)]
        value=text+(display-text)*design.display
        font.kerning[(left,right)]=otRound(value)/2.048
