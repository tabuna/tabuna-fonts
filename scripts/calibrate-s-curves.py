#!/usr/bin/env python3
"""Fit an authored twelve-cubic S to two independent open-counter PNG fields."""
from pathlib import Path
import json,hashlib,argparse
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,gaussian_filter,map_coordinates,label
from scipy.optimize import least_squares
from s_curves import contours,NAMES
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/s-curves-baseline'
T=np.linspace(0,1,48);B=np.array([(1-T)**3,3*(1-T)**2*T,3*(1-T)*T*T,T**3]).T
LIMITS=[(.85,1.002),(.60,.82),(.35,.65),(0,.12),(.6,.85),
        (.25,.55),(.03,.8),(.55,.995),(.15,.38),(.35,.65),(.005,.36),(.005,.4),(.16,.35),
        (.35,.65),(.15,.4),(.45,.75),(.03,.8),(.005,.45),(.60,.85),(.35,.65),(.65,.995),(.5,.995)]


def samples(p,k):
    result=[]
    for start,segs,_ in contours(p,k):
        current=np.array(start)
        for seg in [*segs,start]:
            if len(seg)==2 and isinstance(seg[0],(float,int,np.floating)):
                end=np.array(seg);piece=current[None,:]*(1-T[:,None])+end[None,:]*T[:,None]
            else:piece=B@np.array([current,*seg]);end=np.array(seg[-1])
            result.append(piece);current=end
    return result


def fit(folder,r,d):
    ch=r['character'];size=d['pointSize'];sc=d['pixelScale'];ox,oy=d['originPixels']
    l,b,w,h=r['system']['inkBounds'];top=b+h
    full=np.asarray(Image.open(folder/r['system']['file']).convert('L'),dtype=float)
    x0=int(ox+l*sc)-16;y0=int(oy-top*sc)-16;x1=int(ox+(l+w)*sc)+17;y1=int(oy-b*sc)+17
    ink=1-full[y0:y1,x0:x1]/255;binary=ink>.5
    def pixel(x,y):return round(ox+(l+x*w)*sc)-x0,round(oy-(b+y*h)*sc)-y0
    closed=binary.copy()
    for x,ylo,yhi in ((.90,.40,.94),(.10,.06,.80)):
        px,py0=pixel(x,yhi);_,py1=pixel(x,ylo);closed[py0:py1,px:px+2]=True
    labels,n=label(~closed);bg=labels[0,0]
    holes=[]
    for seed in ((.5,.77),(.5,.23)):
        px,py=pixel(*seed);lab=labels[py,px];assert lab and lab!=bg,(ch,seed,'Open-counter mask was not isolated')
        holes.append(labels==lab)
    upper,lower=holes;assert not np.array_equal(upper,lower)
    def field(mask):
        raw=distance_transform_edt(~mask)-distance_transform_edt(mask)
        return gaussian_filter(raw-.5*np.sign(raw),.45)
    upper_field,lower_field,ink_field=field(upper),field(lower),field(binary)
    fields=[ink_field,ink_field,lower_field,lower_field,lower_field,ink_field,ink_field,
            ink_field,ink_field,upper_field,upper_field,upper_field,ink_field,ink_field]
    def coords(mask):
        yy,xx=np.where(mask);return ((xx+.5+x0-ox)/sc-l)/w,((oy-yy-.5-y0)/sc-b)/h
    ux,uyy=coords(upper);lx,lyy=coords(lower)
    uty=uyy.max();lby=lyy.min();ul=ux.min();lr=lx.max()
    ut=float(np.mean(ux[uyy>uty-2/(h*sc)]));lb=float(np.mean(lx[lyy<lby+2/(h*sc)]))
    col,_=pixel(.5,.5);hits=np.flatnonzero(binary[:,col]);parts=np.split(hits,np.flatnonzero(np.diff(hits)>1)+1);assert len(parts)==3,(ch,'Expected three central ink bands')
    middle=parts[1];umy=((oy-y0-middle.min())/sc-b)/h;lmy=((oy-y0-middle.max()-1)/sc-b)/h
    row_y=((oy-np.arange(binary.shape[0])-.5-y0)/sc-b)/h
    col,_=pixel(.94,.7);ys=np.flatnonzero(binary[:,col]&(row_y>.55)&(row_y<.95));assert len(ys)
    tip_up=((oy-y0-ys.max()-1)/sc-b)/h
    col,_=pixel(.03,.2);ys=np.flatnonzero(binary[:,col]&(row_y>.02)&(row_y<.4));assert len(ys)
    tip_low=((oy-y0-ys.min())/sc-b)/h
    px,py=np.meshgrid(np.arange(binary.shape[1]),row_y)
    top_ink=binary&(py>.6);yy,xx=np.where(top_ink);ol=((xx.min()+x0-ox)/sc-l)/w
    initial=[.97,tip_up,.5,ol,.74,lmy,.25,lr,.25,lb,lby,max(.04,1-lr),tip_low,
             .51,.25,umy,.25,ul,.74,ut,uty,min(.97,1-ul+ol)]
    handles=[.08,.55,.55,.55,.55,.55,.6,.6,.55,.55,.55,.55,.08,.55,
             .08,.55,.55,.55,.55,.55,.6,.6,.55,.55,.55,.55,.08,.55]
    lo=np.array([v[0] for v in LIMITS]+[.001]*28);hi=np.array([v[1] for v in LIMITS]+[1.15]*28)
    for key,value in {'upperTopY':uty,'lowerBottomY':lby,'upperLeftX':ul,'lowerRightX':lr,
                      'lowerMidY':lmy,'upperMidY':umy,'upperTipY':tip_up,'lowerTipY':tip_low,'outerLeftX':ol}.items():
        i=NAMES.index(key);lo[i]=max(lo[i],value-.006);hi[i]=min(hi[i],value+.006)
    x=np.clip(initial+handles,lo+1e-7,hi-1e-7)
    def unpack(v):return dict(zip(NAMES,v[:len(NAMES)])),v[len(NAMES):]
    def residual(v):
        p,k=unpack(v);rs=[]
        for index,(pts,f) in enumerate(zip(samples(p,k),fields)):
            xx=ox+(l+pts[:,0]*w)*sc-x0-.5;yy=oy-(b+pts[:,1]*h)*sc-y0-.5
            value=map_coordinates(f,[yy,xx],order=1,mode='nearest')
            # Do not let either temporary closing line act as a contour.
            if index in (2,9):
                near_bridge=pts[:,0]<.15 if index==2 else pts[:,0]>.85
                raw=map_coordinates(ink_field,[yy,xx],order=1,mode='nearest');value=np.where(near_bridge,raw,value)
            rs.append(value)
        constraints=[p['upperMidY']-p['lowerMidY']-.012,p['upperTipY']-p['upperMidY']-.01,
            p['lowerMidY']-p['lowerTipY']-.01,p['upperTopY']-p['upperTipY']-.01,p['lowerTipY']-p['lowerBottomY']-.01,
            p['upperOuterX']-p['upperTipX']-.01,p['upperLeftY']-p['upperMidY']-.01,p['lowerMidY']-p['lowerRightY']-.01]
        return np.concatenate([*rs,np.minimum(constraints,0)*5000])
    f1=least_squares(lambda v:residual(np.r_[v,x[len(NAMES):]]),x[:len(NAMES)],bounds=(lo[:len(NAMES)],hi[:len(NAMES)]),max_nfev=200,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    x[:len(NAMES)]=f1.x
    f2=least_squares(residual,x,bounds=(lo,hi),max_nfev=500,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    p,k=unpack(f2.x);preview=Image.new('L',(ink.shape[1],ink.shape[0]),255);draw=ImageDraw.Draw(preview)
    pts=np.concatenate(samples(p,k));draw.polygon([(ox+(l+a*w)*sc-x0,oy-(b+c*h)*sc-y0) for a,c in pts],fill=0)
    path=ROOT/'build'/f's-curves-fit-{ord(ch):04X}-{d["weight"]}-{size}.png';sheet=Image.new('L',(preview.width*2,preview.height),255);sheet.paste(preview,(0,0));sheet.paste(Image.fromarray(np.uint8((1-ink)*255)),(preview.width,0));sheet.save(path)
    shape={'parameters':{key:float(v) for key,v in p.items()},'handles':[float(v) for v in k],
           'bounds':[l*1000/size,b*1000/size,(l+w)*1000/size,top*1000/size]}
    diag={'character':ch,'weight':d['weight'],'size':size,'rmsPixels':float(np.sqrt(np.mean(residual(f2.x)**2))),
          'evaluations':f1.nfev+f2.nfev,'optimizerSuccess':bool(f2.success),'preview':str(path.relative_to(ROOT))}
    print(diag,flush=True);return shape,diag


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--one',action='store_true');args=parser.parse_args()
    result={'method':'Authored twelve-cubic S with collinear center tangents; two PNG open-counter fields; no reference vectors','glyphs':{},'runs':[],'diagnostics':[]}
    for weight in ([400] if args.one else (100,400,900)):
        for size,mode in ([(64,'display')] if args.one else [(16,'text'),(64,'display')]):
            folder=BASE/f'{weight}-{size}';path=folder/'render-settings.json';d=json.loads(path.read_text());assert d['referenceWeightMode']=='axis'
            for r in d['records']:
                if args.one and r['character'] not in 'Ss':continue
                assert r['system']['renderedFonts']==[d['systemPostScriptName']]
                shape,diag=fit(folder,r,d);result['glyphs'].setdefault(r['character'],{}).setdefault(str(weight),{})[mode]=shape
                result['diagnostics'].append(diag)
                (ROOT/'build/s-curves-fit-progress.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
            result['runs'].append({'report':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'os':d['os']})
    (ROOT/('build/s-curves-one.json' if args.one else 'sources/s-curves.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
