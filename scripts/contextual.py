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
    glyph=source.comp('colon.case',[(name(':'),tuple(transform))],blend('advance')/2.048)
    from round_band_marks import apply
    apply(glyph,'colon.case',source.d)

def position(font,design,name):
    data=load();node=data['nodes'][str(design.weight)];a,b=node['text'],node['display'];t=design.display
    for side in ('left','right'):
        for ch in data[side+'Context']:
            value=a[side][ch]+(b[side][ch]-a[side][ch])*t
            pair=(name(ch),'colon.case') if side=='left' else ('colon.case',name(ch))
            font.kerning[pair]=otRound(value)/2.048

def features(name):
    data=load();groups=data.get('contextGroups',{'latin':{'left':data['leftContext'],'right':data['rightContext']}})
    # Numeral substitutions run before calt. Keep both forms in each
    # context class so tnum/pnum do not change punctuation alignment.
    def members(characters):
        return ' '.join(glyph for ch in characters
                        for glyph in ([name(ch), name(ch)+'.tnum']
                                      if ch in '0123456789' else [name(ch)]))
    definitions=[];rules=[]
    for key,group in groups.items():
        left=members(group['left']);right=members(group['right'])
        definitions.extend([f"@ColonBefore_{key} = [{left}];",f"@ColonAfter_{key} = [{right}];"])
        rules.append(f"  sub @ColonBefore_{key} colon' @ColonAfter_{key} by colon.case;")
    return '\n'.join(definitions+['feature calt {']+rules+['} calt;',''])
