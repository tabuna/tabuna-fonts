#!/usr/bin/env python3
"""Fit our upper/full-height bowl recipe using native scalar profiles."""
from pathlib import Path
from PIL import Image
import hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bowl_fit',ROOT/'scripts/calibrate-bowls.py')
shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
edges=shared.edges;fit_profile=shared.fit_profile


def measure(folder,rec,s):
    im=Image.open(folder/rec['system']['file']).convert('L');pix=im.load()
    ox,oy=s['originPixels'];scale=s['pixelScale'];size=s['pointSize'];unit=1000/size
    left,bottom,width,height=rec['system']['inkBounds'];right=left+width;top=bottom+height
    xl=int(ox+left*scale)-3;xr=int(ox+right*scale)+4
    yt=int(oy-top*scale)-3;yb=int(oy-bottom*scale)+4
    def row(y):
        py=round(oy-y*scale)
        return [(v+xl-ox)/scale for v in edges([1-pix[x,py]/255 for x in range(xl,xr)])]
    # Inside-counter scans isolate the straight side of the stem, including D.
    samples=[row(top*f/100) for f in range(20,91,5)]
    samples=[r for r in samples if len(r)==4];assert samples,rec['character']
    sl=sum(r[0] for r in samples)/len(samples);sr=sum(r[1] for r in samples)/len(samples)
    columns=[]
    for px in range(round(ox+sr*scale)+3,xr):
        es=edges([1-pix[px,y]/255 for y in range(yt,yb)])
        if len(es) in (2,4):columns.append([(oy-e-yt)/scale for e in es])
    counters=[v for v in columns if len(v)==4];assert counters
    bowlTop=max(v[0] for v in columns);bowlBottom=min(v[-1] for v in columns)
    innerTop=max(v[1] for v in counters);innerBottom=min(v[2] for v in counters)
    outer=[];inner=[]
    for py in range(yt,yb):
        y=(oy-py-.5)/scale
        es=[(v+xl-ox)/scale for v in edges([1-pix[x,py]/255 for x in range(xl,xr)])]
        if len(es) not in (2,4):continue
        if bowlBottom+.5/scale<y<bowlTop-.5/scale and es[-1]>sr+2/scale:outer.append((y*unit,es[-1]*unit))
        if len(es)==4:inner.append((y*unit,es[-2]*unit))
    return {'stemLeft':sl*unit,'stemRight':sr*unit,'top':top*unit,'bottom':bottom*unit,
            'advance':rec['system']['advance']*unit,
            'outer':fit_profile(outer,bowlBottom*unit,bowlTop*unit,sr*unit),
            'inner':fit_profile(inner,innerBottom*unit,innerTop*unit,sr*unit)}


def main():
    data={'method':'Scalar raster fitting of an authored upper/full-height two-cubic bowl model; no reference paths','weights':[100,400,900],'glyphs':{},'runs':[]}
    for weight in (100,400,900):
        for size,mode in [(16,'text'),(64,'display')]:
            folder=ROOT/'references/css-weights-baseline/upper-bowls'/f'{weight}-{size}';p=folder/'render-settings.json';s=json.loads(p.read_text())
            assert s['weight']==weight
            assert s['referenceWeightMode']=='axis'
            for rec in s['records']:
                assert rec['system']['renderedFonts']==[s['systemPostScriptName']]
                result=measure(folder,rec,s);data['glyphs'].setdefault(rec['character'],{}).setdefault(str(weight),{})[mode]=result
                print(weight,mode,rec['character'],{k:[round(result[k][q]['rms'],3) for q in ('upper','lower')] for k in ('outer','inner')},flush=True)
            data['runs'].append({'report':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    (ROOT/'sources/upper-bowls.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
