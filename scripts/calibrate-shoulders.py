#!/usr/bin/env python3
"""Fit our authored shoulder construction to scalar native raster profiles.

Fixed topology: two outer and two inner cubic segments, tangent at their
crowns. The reference supplies raster coverage, never contours or font tables.
"""
from pathlib import Path
from PIL import Image
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[1]


def edges(values):
    result=[]
    for i in range(1,len(values)):
        if (values[i-1]>=.5)!=(values[i]>=.5):
            lo=max(0,i-2);hi=min(len(values),i+2);area=sum(values[lo:hi])
            result.append(hi-area if values[i]>=.5 else lo+area)
    return result


def golden(fun,lo,hi):
    for _ in range(30):
        a=lo+(hi-lo)/3;b=hi-(hi-lo)/3
        if fun(a)<fun(b):hi=b
        else:lo=a
    return (lo+hi)/2


def fit_segment(points,side,crown,slanted=False,fixed_y=None):
    """Side-to-crown cubic. Solve endpoint height and vertical handle linearly."""
    sx=side;cx,cy=crown;data=[((x-sx)/(cx-sx),y) for x,y in points if .018<(x-sx)/(cx-sx)<.985]
    data=data[::max(1,len(data)//90)]
    assert len(data)>8
    def solve(ax,kx):
        terms=[]
        for x,y in data:
            lo,hi=0.,1.
            for _ in range(22):
                t=(lo+hi)/2;v=1-t
                xx=3*v*v*t*ax+3*v*t*t*(1-kx)+t**3
                if xx<x:lo=t
                else:hi=t
            t=(lo+hi)/2;v=1-t;a=v**3+3*v*v*t;b=3*v*v*t;z=y-cy*(3*v*t*t+t**3)
            terms.append((a,b,z))
        aa=sum(a*a for a,b,z in terms);ab=sum(a*b for a,b,z in terms);bb=sum(b*b for a,b,z in terms)
        az=sum(a*z for a,b,z in terms);bz=sum(b*z for a,b,z in terms);det=aa*bb-ab*ab
        sy=(az*bb-bz*ab)/det;handle=(bz*aa-az*ab)/det
        if fixed_y is not None:
            sy=fixed_y;handle=(bz-sy*ab)/bb
        error=sum((a*sy+b*handle-z)**2 for a,b,z in terms)/len(terms)
        ky=handle/(cy-sy) if cy!=sy else 1
        # Keep a monotone arch with interior control points.
        penalty=max(0,.15-ky)**2+max(0,ky-.95)**2
        return error+penalty*(cy-sy)**2,sy,ky
    ax=0.;kx=.6
    for _ in range(6 if slanted else 1):
        kx=golden(lambda k:solve(ax,k)[0],.25,.85)
        if slanted:ax=golden(lambda a:solve(a,kx)[0],0,.45)
    error,sy,ky=solve(ax,kx)
    return {'sideX':sx,'sideY':sy,'crownX':cx,'crownY':cy,'sideHandleX':ax,'sideHandleY':ky,'crownHandle':kx,'rms':math.sqrt(error)}


def fit(folder,rec,settings):
    im=Image.open(folder/rec['system']['file']).convert('L');pix=im.load()
    ox,oy=settings['originPixels'];scale=settings['pixelScale'];size=settings['pointSize']
    left,bottom,width,height=rec['system']['inkBounds'];right=left+width;top=bottom+height
    xl=int(ox+left*scale)-3;xr=int(ox+right*scale)+4
    yt=int(oy-top*scale)-3;yb=int(oy-bottom*scale)+4
    # Straight stems are measured well below the shoulder.
    y=round(oy-height*.22*scale)
    ee=edges([1-pix[x,y]/255 for x in range(xl,xr)])
    assert len(ee)==4
    stem=[(x+xl-ox)/scale for x in ee]
    columns=[]
    for px in range(xl,xr):
        x=(px+.5-ox)/scale
        ee=edges([1-pix[px,y]/255 for y in range(yt,yb)])
        if stem[1]+2/scale<x<stem[2]-2/scale and len(ee)==2:
            columns.append((x,(oy-yt-ee[0])/scale,(oy-yt-ee[1])/scale))
    assert len(columns)>20
    def peak(index):
        t=max(p[index] for p in columns)
        plateau=[p[0] for p in columns if p[index]>=t-.015/scale]
        return sum(plateau)/len(plateau),t
    outer=peak(1);inner=peak(2)
    # n has a short cap above the notch; h has the full ascender.
    if rec['character']=='h':capTop=top;capRight=stem[1]
    else:
        px=round(ox+(left+stem[1])/2*scale)
        ee=edges([1-pix[px,y]/255 for y in range(yt,yb)])
        capTop=(oy-yt-ee[0])/scale
        py=round(oy-(capTop-.02*height)*scale)
        ee=edges([1-pix[x,py]/255 for x in range(xl,xr)])
        capRight=(ee[1]+xl-ox)/scale if len(ee)==4 else stem[1]
    outerLeft=fit_segment([(x,y) for x,y,z in columns if x<outer[0]],capRight,outer,True)
    # Outer right includes the region occupied by the inner right stem below.
    outerRightData=[]
    for px in range(round(ox+outer[0]*scale),xr):
        ee=edges([1-pix[px,y]/255 for y in range(yt,yb)])
        if ee:outerRightData.append(((px+.5-ox)/scale,(oy-yt-ee[0])/scale))
    outerRight=fit_segment(outerRightData,right,outer)
    innerLeft=fit_segment([(x,z) for x,y,z in columns if x<inner[0]],stem[1],inner)
    innerRight=fit_segment([(x,z) for x,y,z in columns if x>inner[0]],stem[2],inner)
    result={'left':left,'right':right,'bottom':bottom,'top':top,'capTop':capTop,'capRight':capRight,
            'leftInner':stem[1],'rightInner':stem[2],
            'outerLeft':outerLeft,'outerRight':outerRight,'innerLeft':innerLeft,'innerRight':innerRight}
    # Store design-space scalar measurements (1000 units/em).
    for k,v in result.items():
        if isinstance(v,dict):
            for name in ('sideX','sideY','crownX','crownY','rms'):v[name]*=1000/size
        else:result[k]*=1000/size
    return result


def fit_m(folder,rec,settings):
    im=Image.open(folder/rec['system']['file']).convert('L');pix=im.load()
    ox,oy=settings['originPixels'];scale=settings['pixelScale'];size=settings['pointSize']
    left,bottom,width,height=rec['system']['inkBounds'];right=left+width;top=bottom+height
    xl=int(ox+left*scale)-3;xr=int(ox+right*scale)+4
    yt=int(oy-top*scale)-3;yb=int(oy-bottom*scale)+4
    py=round(oy-height*.22*scale)
    ee=edges([1-pix[x,py]/255 for x in range(xl,xr)])
    assert len(ee)==6
    stem=[(x+xl-ox)/scale for x in ee]
    columns=[]
    for px in range(xl,xr):
        x=(px+.5-ox)/scale;ee=edges([1-pix[px,y]/255 for y in range(yt,yb)])
        if len(ee)==2:columns.append((x,(oy-yt-ee[0])/scale,(oy-yt-ee[1])/scale))
    gaps=[[p for p in columns if stem[i]+2/scale<p[0]<stem[i+1]-2/scale] for i in (1,3)]
    def peak(points,index):
        y=max(p[index] for p in points);plateau=[p[0] for p in points if p[index]>=y-.015/scale]
        return sum(plateau)/len(plateau),y
    crowns=[peak(g,1) for g in gaps];inner=[peak(g,2) for g in gaps]
    between=[p for p in columns if crowns[0][0]<p[0]<crowns[1][0]]
    valley=min(p[1] for p in between);flat=[p[0] for p in between if p[1]<=valley+.015/scale]
    joint=sum(flat)/len(flat)
    px=round(ox+(left+stem[1])/2*scale);ee=edges([1-pix[px,y]/255 for y in range(yt,yb)])
    capTop=(oy-yt-ee[0])/scale
    py=round(oy-(capTop-.02*height)*scale);ee=edges([1-pix[x,py]/255 for x in range(xl,xr)])
    capRight=(ee[1]+xl-ox)/scale if len(ee)>=4 else stem[1]
    outer=[(x,y) for x,y,z in columns]
    result={'left':left,'right':right,'bottom':bottom,'top':top,'capTop':capTop,'capRight':capRight,
            'leftInner':stem[1],'middleLeft':stem[2],'middleRight':stem[3],'rightInner':stem[4],
            'outerLeft':fit_segment([(x,y) for x,y in outer if x<crowns[0][0]],capRight,crowns[0],True),
            'outerRight':fit_segment([(x,y) for x,y in outer if crowns[0][0]<x<joint],joint,crowns[0],True,valley),
            'outerLeft2':fit_segment([(x,y) for x,y in outer if joint<x<crowns[1][0]],joint,crowns[1],True,valley),
            'outerRight2':fit_segment([(x,y) for x,y in outer if x>crowns[1][0]],right,crowns[1])}
    for i,g in enumerate(gaps):
        suffix='' if i==0 else '2'
        result['innerLeft'+suffix]=fit_segment([(x,z) for x,y,z in g if x<inner[i][0]],stem[1+2*i],inner[i])
        result['innerRight'+suffix]=fit_segment([(x,z) for x,y,z in g if x>inner[i][0]],stem[2+2*i],inner[i])
    for k,v in result.items():
        if isinstance(v,dict):
            for name in ('sideX','sideY','crownX','crownY','rms'):v[name]*=1000/size
        else:result[k]*=1000/size
    return result


def main():
    out={'method':'Scalar profile fit of original fixed shoulder model; no reference outlines','weight':400,'glyphs':{},'runs':[]}
    for mode in ('text','display'):
        folder=ROOT/'references/shoulders-baseline'/mode;p=folder/'render-settings.json';d=json.loads(p.read_text())
        for r in d['records']:
            if r['character'] not in 'nhm':continue
            out['glyphs'].setdefault(r['character'],{})[mode]=(fit_m if r['character']=='m' else fit)(folder,r,d)
        out['runs'].append({'report':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    (ROOT/'sources/shoulders.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    for ch,modes in out['glyphs'].items():
        for mode,p in modes.items():print(ch,mode,{k:round(v['rms'],4) for k,v in p.items() if isinstance(v,dict)})
if __name__=='__main__':main()
