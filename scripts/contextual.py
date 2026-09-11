"""Original punctuation variants selected by measured shaping context."""
from pathlib import Path
from functools import lru_cache
import json
from fontTools.misc.roundTools import otRound

@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/colon-context.json').read_text())

def build(source,name):
    data=load();node=data['nodes'][str(source.d.weight)];a,b=node['text'],node['display'];t=source.d.display
    def blend(key):return a[key]+(b[key]-a[key])*t
    transform=[x+(y-x)*t for x,y in zip(a['transform'],b['transform'])]
    transform[4]/=2.048;transform[5]/=2.048
    source.comp('colon.case',[(name(':'),tuple(transform))],blend('advance')/2.048)

def position(font,design,name):
    data=load();node=data['nodes'][str(design.weight)];a,b=node['text'],node['display'];t=design.display
    for side in ('left','right'):
        for ch in data[side+'Context']:
            value=a[side][ch]+(b[side][ch]-a[side][ch])*t
            pair=(name(ch),'colon.case') if side=='left' else ('colon.case',name(ch))
            font.kerning[pair]=otRound(value)/2.048

def features(name):
    data=load()
    left=' '.join(name(c) for c in data['leftContext']);right=' '.join(name(c) for c in data['rightContext'])
    return f"@ColonBefore = [{left}];\n@ColonAfter = [{right}];\nfeature calt {{\n  sub @ColonBefore colon' @ColonAfter by colon.case;\n}} calt;\n"
