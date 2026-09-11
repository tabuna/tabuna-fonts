#!/usr/bin/env python3
"""Build local advance fields from native scalar measurements of our baseline."""
from pathlib import Path
import json,hashlib,math,unicodedata
from fontTools.ttLib import TTFont
from fontTools.misc.roundTools import otRound
from fontTools.varLib.models import normalizeValue,piecewiseLinearMap
from fontTools.misc.fixedTools import floatToFixedToFloat
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/optical-widths-baseline'
font=TTFont(BASE/'TabunaSans-with-hvar.ttf');cmap=font.getBestCmap();upm=font['head'].unitsPerEm
eligible=json.loads((BASE/'eligible.json').read_text())
trained=set(json.loads((ROOT/'proofs/weight-metrics/characters.json').read_text())['characters'])|{' ','\u00a0'}
boundary_measurements=[{r['text']:r for r in json.loads((BASE/f'characters-{w}-{s}.json').read_text())['records']}
                       for w in (100,400,900) for s in (16,28)]
fit_characters=[];unmodified=[]
for ch in eligible['characters']:
    decomposition=unicodedata.normalize('NFD',ch)
    inherits=(len(decomposition)>1 and decomposition[0] in trained
              and all(unicodedata.combining(c) for c in decomposition[1:])
              and all(abs(d[ch]['own']-d[decomposition[0]]['own'])<1e-9 for d in boundary_measurements))
    if ch in trained or inherits:fit_characters.append(ch)
    else:unmodified.append({'text':ch,'reason':'Separate composite proportions need geometry work; a local advance-only correction would leave oversized ink and create a width dip between unchanged endpoints.'})
axis=next(a for a in font['fvar'].axes if a.axisTag=='opsz')
def mapped(size):return piecewiseLinearMap(normalizeValue(size,(axis.minValue,axis.defaultValue,axis.maxValue)),font['avar'].segments['opsz'])
# Keep the local field wholly inside 16–28, including fixed-point rounding.
coords=[math.ceil(mapped(16)*16384)/16384]+[floatToFixedToFloat(mapped(s),14) for s in (18,20,24)]+[math.floor(mapped(28)*16384)/16384]
supports=[]
for i in range(1,4):
    optical={'opsz':tuple(coords[i-1:i+2])}
    supports.extend([optical,{**optical,'wght':(-1,-1,0)},{**optical,'wght':(0,1,1)}])
measurements={};runs=[]
for w in (100,400,900):
    for s in (18,20,24):
        path=BASE/f'characters-{w}-{s}.json';d=json.loads(path.read_text())
        assert d['referenceWeightMode']=='axis' and d['weight']==w and d['pointSize']==s
        assert d['fontSHA256']==hashlib.sha256((BASE/'TabunaSans-before.ttf').read_bytes()).hexdigest()
        measurements[(w,s)]={r['text']:r for r in d['records']}
        runs.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
glyphs={};diagnostics=[]
for ch in fit_characters:
    name=cmap[ord(ch)]
    if font['hmtx'][name][0]==0:continue
    deltas=[]
    for s in (18,20,24):
        by_weight={}
        for w in (100,400,900):
            r=measurements[(w,s)][ch];assert not r['fallback']
            own=r['own']*upm/s;target=otRound(r['system']*upm/s)
            assert abs(own-otRound(own))<1e-6,(ch,w,s,'Non-integer own scalar advance')
            by_weight[w]=target-otRound(own)
            diagnostics.append({'text':ch,'weight':w,'size':s,'ownAdvanceFU':own,'referenceAdvanceFU':r['system']*upm/s,'roundedTargetFU':target,'delta':by_weight[w]})
        deltas.extend([by_weight[400],by_weight[100]-by_weight[400],by_weight[900]-by_weight[400]])
    if any(deltas):glyphs[name]=deltas
special_diagnostics=[]
for name in ['ff.liga','fi.liga','fl.liga','ffi.liga','ffl.liga','colon.case']:
    deltas=[]
    for s in (18,20,24):
        by_weight={}
        for w in (100,400,900):
            if name.endswith('.liga'):
                text=name.removesuffix('.liga');r=measurements[(w,s)][text]
                assert not r['fallback'] and len(r['ownLayout'])==1
                assert len(r['systemLayout'])==len(text)
                own=r['own']*upm/s
                target=sum(otRound(item['advance']*upm/s) for item in r['systemLayout'])
            else:
                path=BASE/f'colon-{w}-{s}.json';d=json.loads(path.read_text());values=[]
                runs.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
                for r in d['records']:
                    assert not r['fallback'];index=r['text'].index(':')
                    a=next(item for item in r['ownUnkernedLayout'] if item['index']==index)
                    b=next(item for item in r['systemUnkernedLayout'] if item['index']==index)
                    assert font.getGlyphName(a['glyph'])==name
                    values.append((a['advance']*upm/s,otRound(b['advance']*upm/s)))
                assert len(set(values))==1,'Colon advance varies among expected case contexts'
                own,target=values[0]
            by_weight[w]=target-otRound(own)
            special_diagnostics.append({'glyph':name,'weight':w,'size':s,'ownAdvanceFU':own,'roundedTargetFU':target,'delta':by_weight[w]})
        deltas.extend([by_weight[400],by_weight[100]-by_weight[400],by_weight[900]-by_weight[400]])
    if any(deltas):glyphs[name]=deltas
data={'method':'Native per-glyph scalar advance differences, rounded at 2048 UPM; local optical supports and three weight nodes',
      'unitsPerEm':upm,'axisRange':[axis.minValue,axis.defaultValue,axis.maxValue],'supports':supports,'glyphs':glyphs,'diagnostics':diagnostics,
      'baselineSHA256':hashlib.sha256((BASE/'TabunaSans-before.ttf').read_bytes()).hexdigest(),'runs':runs,'excluded':eligible['excluded'],'unmodifiedProportions':unmodified,
      'specialDiagnostics':special_diagnostics,
      'limitations':'No outline changes. Combining/control characters and fallback cases excluded. Tabular alternates and ligature internal positions are not calibrated here.'}
data['baselineModelAdvances']=[{'weight':w,'size':s,'widths':{name:otRound(gs[name].width) for name in glyphs}}
                              for w in (100,400,900) for s in (18,20,24)
                              for gs in [font.getGlyphSet(location={'wght':w,'opsz':s})]]
(ROOT/'sources/optical-widths.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'glyphs':len(glyphs),'measurements':len(diagnostics),'regions':len(supports)}))
