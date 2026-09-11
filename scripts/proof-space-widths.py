#!/usr/bin/env python3
"""Check space-only binary changes and fresh native scalar measurements."""
from pathlib import Path
import argparse,hashlib,json,subprocess
from fontTools.ttLib import TTFont
from fontTools.misc.roundTools import otRound
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/space-widths-baseline'
parser=argparse.ArgumentParser();parser.add_argument('--font',default='dist/TabunaSansVariable.ttf');args=parser.parse_args()
path=ROOT/args.font;OUT=ROOT/'proofs/space-widths';OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=TTFont(BASE/'TabunaSans-before.ttf');after=TTFont(path)
unchanged=[]
for tag in ('glyf','hmtx','avar','GPOS','GSUB','GDEF'):
    assert before[tag].compile(before)==after[tag].compile(after),tag
    unchanged.append(tag)
spaces={after.getBestCmap()[ord(c)] for c in (' ','\u00a0')};count=0
for name in before.getGlyphOrder():
    old=before['gvar'].variations.get(name,[]);new=after['gvar'].variations.get(name,[])
    if name not in spaces:
        assert len(old)==len(new),name
        assert all(a.axes==b.axes and a.coordinates==b.coordinates for a,b in zip(old,new)),name
        count+=len(old)
    else:
        assert after['glyf'][name].numberOfContours==0
        for v in new:
            assert len(v.coordinates)==4
            left,right,top,bottom=v.coordinates
            assert left==top==bottom==(0,0) and right[1]==0
grid=json.loads((BASE/'grid.json').read_text())
holdout={'weights':[150,250,350,450,550,650,750,850],'sizes':[10.5,13.5,17.5,21,23,25,27,36,80]}
rows=[]
for group,points in [('grid',grid),('holdout',holdout)]:
    for w in points['weights']:
        for s in points['sizes']:
            oldpath=BASE/f'{w}-{s}.json';newpath=OUT/f'{w}-{s}.json'
            if not oldpath.exists():
                subprocess.run([str(ROOT/'build/measure-text'),str(BASE/'TabunaSans-before.ttf'),str(BASE/'characters.json'),str(oldpath),str(s),str(w),'axis'],check=True,stdout=subprocess.DEVNULL)
            subprocess.run([str(ROOT/'build/measure-text'),str(path),str(BASE/'characters.json'),str(newpath),str(s),str(w),'axis'],check=True,stdout=subprocess.DEVNULL)
            b=json.loads(oldpath.read_text());a=json.loads(newpath.read_text())
            assert b['fontSHA256']==sha(BASE/'TabunaSans-before.ttf') and a['fontSHA256']==sha(path)
            for r,p in zip(a['records'],b['records']):
                assert r['text']==p['text'] and r['system']==p['system'] and not r['fallback'] and not p['fallback']
                target=otRound(r['system']*2048/s)*s/2048
                rows.append({'group':group,'weight':w,'size':s,'text':r['text'],'before':p['own'],'after':r['own'],'system':r['system'],'roundedNative':target,
                             'beforeRoundedMatch':p['own']==target,'afterRoundedMatch':r['own']==target,'beforeRawExact':p['own']==p['system'],'afterRawExact':r['own']==r['system']})
    print(f'Measured {group}',flush=True)
def stats(rs):
    return {'total':len(rs),**{k:sum(r[k] for r in rs) for k in ('beforeRoundedMatch','afterRoundedMatch','beforeRawExact','afterRawExact')},
            'beforeMeanAbsoluteWidthError':sum(abs(r['before']-r['system']) for r in rs)/len(rs),
            'afterMeanAbsoluteWidthError':sum(abs(r['after']-r['system']) for r in rs)/len(rs),
            'improved':sum(abs(r['after']-r['system'])<abs(r['before']-r['system']) for r in rs),
            'regressed':sum(abs(r['after']-r['system'])>abs(r['before']-r['system']) for r in rs)}
report={'fontSHA256':sha(path),'beforeFontSHA256':sha(BASE/'TabunaSans-before.ttf'),'unchangedTables':unchanged,
        'unchangedVisibleGlyphVariationTuples':count,'modifiedGlyphs':sorted(spaces),
        'scope':'Native explicit-axis scalar layout. Rounded targets are distinguished from raw equality. Holdout values were not used in calibration.',
        'spaces':{g:stats([r for r in rows if r['group']==g and r['text'] in (' ','\u00a0')]) for g in ('grid','holdout')},
        'controlStrings':{g:stats([r for r in rows if r['group']==g and r['text'] not in (' ','\u00a0')]) for g in ('grid','holdout')},'rows':rows}
(OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
