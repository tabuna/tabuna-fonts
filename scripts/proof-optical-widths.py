#!/usr/bin/env python3
"""Prove advance-only changes and measure the resulting native scalar widths."""
from pathlib import Path
import hashlib,json,subprocess
from fontTools.ttLib import TTFont
from fontTools.misc.roundTools import otRound
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/optical-widths-baseline';OUT=ROOT/'proofs/optical-widths';OUT.mkdir(exist_ok=True)
before=TTFont(BASE/'TabunaSans-before.ttf');after=TTFont(ROOT/'dist/TabunaSansVariable.ttf')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
unchanged_tables=[]
for table in ('glyf','hmtx','avar','GPOS','GSUB','GDEF'):
    assert before[table].compile(before)==after[table].compile(after),table
    unchanged_tables.append(table)
original_tuples=added=0
for name in before.getGlyphOrder():
    old=before['gvar'].variations.get(name,[]);new=after['gvar'].variations.get(name,[])
    assert len(new)>=len(old)
    for a,b in zip(old,new):
        assert a.axes==b.axes and a.coordinates==b.coordinates,name
    original_tuples+=len(old)
    for variation in new[len(old):]:
        assert all(p is None for p in variation.coordinates[:-4]),name
        left,right,top,bottom=variation.coordinates[-4:]
        assert left==top==bottom==(0,0) and right[1]==0,name
        added+=1
eligible=set(json.loads((BASE/'eligible.json').read_text())['characters'])
calibration=json.loads((ROOT/'sources/optical-widths.json').read_text())
unmodified={r['text'] for r in calibration['unmodifiedProportions']}
rows=[]
for w in (100,400,900):
    for s in (16,18,20,24,28):
        out=OUT/f'characters-{w}-{s}.json'
        subprocess.run([str(ROOT/'build/measure-text'),str(ROOT/'dist/TabunaSansVariable.ttf'),str(BASE/'characters.json'),str(out),str(s),str(w),'axis'],check=True,stdout=subprocess.DEVNULL)
        old={r['text']:r for r in json.loads((BASE/f'characters-{w}-{s}.json').read_text())['records']}
        data=json.loads(out.read_text());assert data['fontSHA256']==sha(ROOT/'dist/TabunaSansVariable.ttf')
        for r in data['records']:
            ch=r['text']
            if ch not in eligible:continue
            b=old[ch];assert r['system']==b['system'] and not r['fallback']
            if s in (16,28):assert r['own']==b['own'],(ch,w,s,'Boundary advance changed')
            target=otRound(r['system']*2048/s)*s/2048
            rows.append({'text':ch,'weight':w,'size':s,'beforeAdvance':b['own'],'afterAdvance':r['own'],'systemAdvance':r['system'],
                         'roundedSystemAdvance':target,'beforeRoundedMatch':b['own']==target,'afterRoundedMatch':r['own']==target,'rawExact':r['own']==r['system'],
                         'unmodifiedProportion':ch in unmodified})
def stats(rs):return {'total':len(rs),'beforeRoundedMatch':sum(r['beforeRoundedMatch'] for r in rs),'afterRoundedMatch':sum(r['afterRoundedMatch'] for r in rs),'rawExact':sum(r['rawExact'] for r in rs)}
report={'beforeFontSHA256':sha(BASE/'TabunaSans-before.ttf'),'fontSHA256':sha(ROOT/'dist/TabunaSansVariable.ttf'),
        'scope':'Native scalar advances, explicit axes, 449 characters × 3 weights × 5 sizes; rounded targets are not raw native equality',
        'unchangedTables':unchanged_tables,'originalVariationTuplesUnchanged':original_tuples,'addedRightPhantomOnlyTuples':added,
        'allReferenceAdvancesUnchanged':True,'boundaryAdvancesUnchanged':True,
        'intermediate':stats([r for r in rows if r['size'] in (18,20,24)]),
        'calibratedIntermediate':stats([r for r in rows if r['size'] in (18,20,24) and not r['unmodifiedProportion']]),
        'rows':rows}
(OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
