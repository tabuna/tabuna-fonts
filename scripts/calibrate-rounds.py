#!/usr/bin/env python3
"""Fit scalar proportions and handles of our four-cubic round construction.

Input is native raster coverage, not font paths. Each quadrant keeps the
original two tangent handles. The fit cannot add reference contour points.
"""
from pathlib import Path
from PIL import Image
import json, math, hashlib
ROOT=Path(__file__).resolve().parents[1]


def transitions(values):
    result=[]
    for i in range(1,len(values)):
        if (values[i-1]>=.5)!=(values[i]>=.5):
            # A grayscale edge pixel encodes the covered fraction of its cell.
            rising=values[i]>=.5
            lo=max(0,i-2);hi=min(len(values),i+2)
            area=sum(values[lo:hi])
            result.append(hi-area if rising else lo+area)
    return result


def fit_quadrant(points):
    # Unit quadrant from (0,0) to (1,1), controls (0,ky),(1-kx,1).
    def score(ky):
        terms=[]
        for x,y in points:
            lo,hi=0.,1.
            for _ in range(24):
                t=(lo+hi)/2;v=1-t
                value=3*v*v*t*ky+3*v*t*t+t*t*t
                if value<y:lo=t
                else:hi=t
            t=(lo+hi)/2;v=1-t;a=3*v*t*t
            terms.append((a,a+t*t*t-x))
        kx=sum(a*b for a,b in terms)/sum(a*a for a,b in terms)
        return sum((a*kx-b)**2 for a,b in terms),kx
    lo,hi=.35,.85
    for _ in range(40):
        a=lo+(hi-lo)/3;b=hi-(hi-lo)/3
        if score(a)[0]<score(b)[0]:hi=b
        else:lo=a
    ky=(lo+hi)/2;error,kx=score(ky)
    return [kx,ky],math.sqrt(error/len(points))


def fit(path,record,settings):
    im=Image.open(path).convert('L');pix=im.load()
    ox,oy=settings['originPixels'];scale=settings['pixelScale']
    left,bottom,width,height=record['system']['inkBounds']
    right=left+width;top=bottom+height
    xl=int(ox+left*scale)-3;xr=int(ox+right*scale)+4
    yt=int(oy-top*scale)-3;yb=int(oy-bottom*scale)+4
    rows=[]
    for py in range(yt,yb):
        edges=transitions([1-pix[x,py]/255 for x in range(xl,xr)])
        if len(edges) in (2,4):
            rows.append(((oy-py-.5)/scale,[(x+xl-ox)/scale for x in edges]))
    # Counter extrema from central row and central column coverage.
    mid=min((r for r in rows if len(r[1])==4),key=lambda r:abs(r[0]-(bottom+top)/2))
    il,ir=mid[1][1:3]
    px=round(ox+(left+right)/2*scale)
    e=transitions([1-pix[px,y]/255 for y in range(yt,yb)])
    assert len(e)==4
    it,ib=[(oy-(z+yt))/scale for z in e[1:3]]
    output={'inner':[(il-left)/width,(ib-bottom)/height,(ir-left)/width,(it-bottom)/height]}
    errors={}
    for contour,bounds in [('outer',(left,bottom,right,top)),('inner',(il,ib,ir,it))]:
        l,b,r,t=bounds;cx=(l+r)/2;cy=(b+t)/2
        quadrants=[[] for _ in range(4)] # left-top,right-top,right-bottom,left-bottom
        for y,edges in rows:
            if contour=='inner' and len(edges)!=4:continue
            le,re=(edges[0],edges[-1]) if contour=='outer' else edges[1:3]
            if not b<y<t:continue
            top_half=y>=cy;ny=(y-cy)/(t-cy) if top_half else (cy-y)/(cy-b)
            if not .02<ny<.985:continue
            for x,isleft in [(le,True),(re,False)]:
                nx=(x-l)/(cx-l) if isleft else (r-x)/(r-cx)
                quadrant=(0 if isleft else 1) if top_half else (3 if isleft else 2)
                quadrants[quadrant].append((nx,ny))
        fitted=[fit_quadrant(p[::max(1,len(p)//100)]) for p in quadrants]
        output[contour+'Handles']=[p[0] for p in fitted]
        errors[contour]=[p[1] for p in fitted]
    return output,errors


def main():
    data={'method':'Fit scalar handles of original four-cubic round model to magnified native grayscale coverage; no outline import','weight':400,'glyphs':{},'runs':[]}
    for mode in ('text','display'):
        folder=ROOT/'references/rounds-baseline'/mode
        report=folder/'render-settings.json';settings=json.loads(report.read_text())
        errors={}
        for record in settings['records']:
            ch=record['character']
            result,error=fit(folder/record['system']['file'],record,settings)
            data['glyphs'].setdefault(ch,{})[mode]=result;errors[ch]=error
        data['runs'].append({'report':str(report.relative_to(ROOT)),'reportSHA256':hashlib.sha256(report.read_bytes()).hexdigest(),'fitNormalizedRMS':errors})
    (ROOT/'sources/rounds.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(data['runs'],ensure_ascii=False,indent=2))

if __name__=='__main__':main()
