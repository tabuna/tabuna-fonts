#!/usr/bin/env python3
"""Fit the authored G construction to raster fields, without reference paths."""
from pathlib import Path
import json,hashlib,argparse
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,gaussian_filter,map_coordinates,label
from scipy.optimize import least_squares
from upper_g import contours,NAMES
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/upper-g-baseline'
T=np.linspace(0,1,48);B=np.array([(1-T)**3,3*(1-T)**2*T,3*(1-T)*T*T,T**3]).T
LIMITS=[(.3,.7),(.35,.65),(.3,.7),(.58,.80),(.90,1.002),(.5,.995),
        (.25,.55),(.38,.65),(.25,.55),(.4,.7),(.55,.995),(.005,.45),(.35,.65),(.3,.7),(.65,.999),(.3,.7),(.005,.35)]


def sample(p,k):
    result=[]
    for start,segs,_ in contours(p,k):
        current=np.array(start)
        for seg in [*segs,start]:
            if len(seg)==2 and isinstance(seg[0],(float,int,np.floating)):
                end=np.array(seg);piece=current[None,:]*(1-T[:,None])+end[None,:]*T[:,None]
            else:piece=B@np.array([current,*seg]);end=np.array(seg[-1])
            result.append(piece);current=end
    return result


def fit(folder,d):
    r=d['records'][0];size=d['pointSize'];sc=d['pixelScale'];ox,oy=d['originPixels']
    l,b,w,h=r['system']['inkBounds'];top=b+h
    full=np.asarray(Image.open(folder/r['system']['file']).convert('L'),dtype=float)
    x0=int(ox+l*sc)-16;y0=int(oy-top*sc)-16;x1=int(ox+(l+w)*sc)+17;y1=int(oy-b*sc)+17
    ink=1-full[y0:y1,x0:x1]/255;binary=ink>.5
    closed=binary.copy();bx=round(ox+(l+w*.98)*sc)-x0
    by0=round(oy-(b+h*.90)*sc)-y0;by1=round(oy-(b+h*.15)*sc)-y0
    closed[by0:by1,bx:bx+2]=True
    labels,n=label(~closed);background=labels[0,0];candidates=[i for i in range(1,n+1) if i!=background]
    assert candidates,'Temporary bridge must isolate the interior'
    hole=labels==max(candidates,key=lambda i:np.count_nonzero(labels==i))
    def field(mask):
        raw=distance_transform_edt(~mask)-distance_transform_edt(mask)
        return gaussian_filter(raw-.5*np.sign(raw),.45)
    outer_field=field(binary|hole);inner_field=field(hole);ink_field=field(binary)
    fields=[outer_field]*4+[ink_field]*4+[inner_field]*4+[ink_field]
    yy,xx=np.where(hole);hx=(xx+.5+x0-ox)/sc;hy=(oy-yy-.5-y0)/sc
    il=(hx.min()-l)/w;iby=(hy.min()-b)/h;ity=(hy.max()-b)/h
    it=(np.mean(hx[hy>hy.max()-2/sc])-l)/w;ib=(np.mean(hx[hy<hy.min()+2/sc])-l)/w
    # Locate the horizontal bar in an interior vertical raster slice.
    cx=round(ox+(l+w*.65)*sc)-x0
    row_y=(oy-np.arange(ink.shape[0])-.5-y0)/sc
    band=np.flatnonzero(binary[:,cx]&((row_y-b)/h>.25)&((row_y-b)/h<.65))
    assert len(band)>1
    bt=((oy-y0-band.min())/sc-b)/h;bb=((oy-y0-band.max()-1)/sc-b)/h
    center=int((band.min()+band.max())/2)
    col_x=((np.arange(ink.shape[1])+.5+x0-ox)/sc-l)/w
    cols=np.flatnonzero(binary[center]& (col_x>.4))
    bl=((cols.min()+x0-ox)/sc-l)/w
    initial=[.51,.50,.51,.69,.993,1-il,.41,bt,bb,bl,1-il,il,.50,it,ity,ib,iby]
    handles=[.10,.48,.55,.55,.55,.55,.55,.55,.55,.55,.55,.55,.55,.55,.55,.55,.1,.5]
    lo=np.array([v[0] for v in LIMITS]+[.001]*18);hi=np.array([v[1] for v in LIMITS]+[1.1]*18)
    for key,value in {'innerLeftX':il,'innerBottomY':iby,'innerTopY':ity,'barTopY':bt,'barBottomY':bb,'barLeftX':bl}.items():
        i=NAMES.index(key);lo[i]=max(lo[i],value-.006);hi[i]=min(hi[i],value+.006)
    x=np.clip(initial+handles,lo+1e-7,hi-1e-7)
    def unpack(v):return dict(zip(NAMES,v[:len(NAMES)])),v[len(NAMES):]
    def residual(v):
        p,k=unpack(v);rs=[]
        for pts,f in zip(sample(p,k),fields):
            xx=ox+(l+pts[:,0]*w)*sc-x0-.5;yy=oy-(b+pts[:,1]*h)*sc-y0-.5
            rs.append(map_coordinates(f,[yy,xx],order=1,mode='nearest'))
        constraints=[p['barTopY']-p['outerRightY'],p['barTopY']-p['barBottomY']-.015,
            p['innerRightX']-p['barLeftX']-.02,p['innerTopY']-p['upperTipY']-.01,
            p['upperTipY']-p['barTopY']-.05,p['barBottomY']-p['innerBottomY']-.05,
            p['upperOuterX']-p['upperInnerX']-.015]
        return np.concatenate([*rs,np.minimum(constraints,0)*5000])
    f1=least_squares(lambda v:residual(np.r_[v,x[len(NAMES):]]),x[:len(NAMES)],bounds=(lo[:len(NAMES)],hi[:len(NAMES)]),max_nfev=180,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    x[:len(NAMES)]=f1.x
    f2=least_squares(residual,x,bounds=(lo,hi),max_nfev=450,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    p,k=unpack(f2.x);preview=Image.new('L',(ink.shape[1],ink.shape[0]),255);draw=ImageDraw.Draw(preview)
    pts=np.concatenate(sample(p,k));draw.polygon([(ox+(l+a*w)*sc-x0,oy-(b+c*h)*sc-y0) for a,c in pts],fill=0)
    path=ROOT/'build'/f'upper-g-fit-{d["weight"]}-{size}.png';sheet=Image.new('L',(preview.width*2,preview.height),255);sheet.paste(preview,(0,0));sheet.paste(Image.fromarray(np.uint8((1-ink)*255)),(preview.width,0));sheet.save(path)
    shape={'parameters':{key:float(v) for key,v in p.items()},'handles':[float(v) for v in k],
           'bounds':[l*1000/size,b*1000/size,(l+w)*1000/size,top*1000/size]}
    diag={'weight':d['weight'],'size':size,'rmsPixels':float(np.sqrt(np.mean(residual(f2.x)**2))),
          'evaluations':f1.nfev+f2.nfev,'optimizerSuccess':bool(f2.success),'preview':str(path.relative_to(ROOT))}
    print(diag,flush=True);return shape,diag


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--one',action='store_true');args=parser.parse_args()
    result={'method':'Authored eight-cubic G with a level crossbar; separate PNG exterior/interior fields; no reference vectors','glyphs':{'G':{}},'runs':[],'diagnostics':[]}
    for weight in ([400] if args.one else (100,400,900)):
        for size,mode in ([(64,'display')] if args.one else [(16,'text'),(64,'display')]):
            folder=BASE/f'{weight}-{size}';path=folder/'render-settings.json';d=json.loads(path.read_text())
            assert d['referenceWeightMode']=='axis' and d['records'][0]['system']['renderedFonts']==[d['systemPostScriptName']]
            shape,diag=fit(folder,d);result['glyphs']['G'].setdefault(str(weight),{})[mode]=shape
            result['diagnostics'].append(diag);result['runs'].append({'report':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'os':d['os']})
            (ROOT/'build/upper-g-fit-progress.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (ROOT/('build/upper-g-one.json' if args.one else 'sources/upper-g.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
