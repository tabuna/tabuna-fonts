#!/usr/bin/env python3
"""Fit our two-cubic bowl construction to scalar raster profiles.

The topology stays authored here: a straight attachment and upper/lower
quarter curves, independently drawn for outside and counter. No font paths
or control points are read from the reference.
"""
from pathlib import Path
from PIL import Image
from bisect import bisect_left
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[1]


def edges(values):
    out=[]
    for i in range(1,len(values)):
        if (values[i-1]>=.5)!=(values[i]>=.5):
            lo=max(0,i-2);hi=min(len(values),i+2);area=sum(values[lo:hi])
            out.append(hi-area if values[i]>=.5 else lo+area)
    return out


def golden(fn,lo,hi):
    for _ in range(28):
        a=lo+(hi-lo)/3;b=hi-(hi-lo)/3
        if fn(a)<fn(b):hi=b
        else:lo=a
    return (lo+hi)/2


def fit_profile(profile,lower,upper,left):
    profile=sorted(profile);ys=[p[0] for p in profile]
    right=max(p[1] for p in profile)
    plateau=[y for y,x in profile if x>=right-.015]
    center=sum(plateau)/len(plateau)
    def at(y):
        i=max(1,min(len(profile)-1,bisect_left(ys,y)))
        a,b=profile[i-1:i+1];t=(y-a[0])/(b[0]-a[0]);return a[1]+(b[1]-a[1])*t
    def quadrant(cy,tip):
        def solve(ky):
            terms=[]
            for i in range(3,96):
                t=i/100;v=1-t;f=3*v*v*t*ky+3*v*t*t+t**3;y=cy+(tip-cy)*f
                if not ys[0]+.6<y<ys[-1]-.6:continue
                a=3*v*t*t;b=t**3;z=at(y)-right*(v**3+3*v*v*t)
                terms.append((a,b,z))
            aa=sum(a*a for a,b,z in terms);ab=sum(a*b for a,b,z in terms);bb=sum(b*b for a,b,z in terms)
            az=sum(a*z for a,b,z in terms);bz=sum(b*z for a,b,z in terms);det=aa*bb-ab*ab
            control=(az*bb-bz*ab)/det;end=(bz*aa-az*ab)/det
            error=sum((a*control+b*end-z)**2 for a,b,z in terms)/len(terms)
            kx=(control-end)/(right-end)
            penalty=(max(0,left-end)**2+max(0,.2-kx)**2*(right-left)**2+max(0,kx-.98)**2*(right-left)**2)
            return error+penalty,end,kx
        ky=golden(lambda k:solve(k)[0],.3,.85);error,end,kx=solve(ky)
        return {'endX':end,'kx':kx,'ky':ky,'rms':math.sqrt(error)}
    candidates=[]
    for offset in (-3,-2,-1,0,1,2,3):
        cy=center+offset
        if not lower<cy<upper:continue
        top=quadrant(cy,upper);bottom=quadrant(cy,lower)
        candidates.append((top['rms']**2+bottom['rms']**2,cy,top,bottom))
    error,cy,top,bottom=min(candidates,key=lambda v:v[0])
    return {'right':right,'centerY':cy,'top':upper,'bottom':lower,'upper':top,'lower':bottom}


def measure(folder,rec,settings):
    im=Image.open(folder/rec['system']['file']).convert('L');pix=im.load()
    ox,oy=settings['originPixels'];scale=settings['pixelScale'];size=settings['pointSize'];unit=1000/size
    left,bottom,width,height=rec['system']['inkBounds'];right=left+width;top=bottom+height
    xl=int(ox+left*scale)-3;xr=int(ox+right*scale)+4
    yt=int(oy-top*scale)-3;yb=int(oy-bottom*scale)+4
    def row(y,end=xr):
        py=round(oy-y*scale)
        return [(v+xl-ox)/scale for v in edges([1-pix[x,py]/255 for x in range(xl,end)])]
    stem=row(top*.82);ch=rec['character'].upper()
    assert len(stem)==(4 if ch=='Ы' else 2),(rec['character'],stem)
    sl,sr=stem[:2]
    if ch=='Ъ':
        # A heavy head bar can cover the initial upper scanline. The body
        # stem's left boundary is the rightmost first edge across the height;
        # the head projects left and the bowl projects only to the right.
        sl=max(row(top*f/100)[0] for f in range(15,96,5))
    limit=round(ox+(stem[1]+stem[2])*.5*scale) if ch=='Ы' else xr
    if ch=='Ы':
        # The separating whitespace lies to the right of the bowl. Find it on
        # a low row where the counter is present, ignoring the independent post.
        low=row(top*.30)
        assert len(low)>=4
        limit=round(ox+(low[-3]+low[-2])*.5*scale)
    columns=[]
    scanTop=int(oy-top*.76*scale)
    for px in range(round(ox+sr*scale)+3,limit):
        x=(px+.5-ox)/scale;es=edges([1-pix[px,y]/255 for y in range(scanTop,yb)])
        if len(es) in (2,4):columns.append((x,[(oy-e-scanTop)/scale for e in es]))
    assert columns
    bowlTop=max(v[0] for x,v in columns)
    counter=[v for x,v in columns if len(v)==4]
    assert counter
    innerTop=max(v[1] for v in counter);innerBottom=min(v[2] for v in counter)
    outer=[];inner=[]
    for py in range(int(oy-bowlTop*scale)+1,yb):
        y=(oy-py-.5)/scale
        es=[(v+xl-ox)/scale for v in edges([1-pix[x,py]/255 for x in range(xl,limit)])]
        if len(es) not in (2,4):continue
        if bottom+.5/scale<y<bowlTop-.5/scale and es[-1]>sr+2/scale:outer.append((y*unit,es[-1]*unit))
        if len(es)==4:inner.append((y*unit,es[-2]*unit))
    result={'stemLeft':sl*unit,'stemRight':sr*unit,'top':top*unit,'bottom':bottom*unit,
            'advance':rec['system']['advance']*unit,
            'outer':fit_profile(outer,bottom*unit,bowlTop*unit,sr*unit),
            'inner':fit_profile(inner,innerBottom*unit,innerTop*unit,sr*unit)}
    if ch=='Ы':result['post']=[stem[2]*unit,stem[3]*unit,bottom*unit,top*unit]
    if ch=='Ъ':
        x=(left+sl)/2;px=round(ox+x*scale)
        es=edges([1-pix[px,y]/255 for y in range(yt,yb)]);assert len(es)==2
        result['head']=[left*unit,(oy-es[-1]-yt)/scale*unit]
    return result


def main():
    data={'method':'Fixed original two-cubic bowls fitted to scalar native profiles; no reference paths','weights':[100,400,900],'glyphs':{},'runs':[]}
    for weight in (100,400,900):
        for size,mode in [(16,'text'),(64,'display')]:
            folder=ROOT/'references/css-weights-baseline/bowls'/f'{weight}-{size}';p=folder/'render-settings.json';s=json.loads(p.read_text())
            assert s['weight']==weight
            assert s['referenceWeightMode']=='axis'
            for rec in s['records']:
                assert rec['system']['renderedFonts']==[s['systemPostScriptName']]
                result=measure(folder,rec,s);data['glyphs'].setdefault(rec['character'],{}).setdefault(str(weight),{})[mode]=result
                print(weight,mode,rec['character'],{kind:[round(result[kind][q]['rms'],3) for q in ('upper','lower')] for kind in ('outer','inner')},flush=True)
            data['runs'].append({'report':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    (ROOT/'sources/bowls.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
