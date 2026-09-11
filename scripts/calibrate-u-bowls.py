#!/usr/bin/env python3
"""Fit authored U/u curves to independent exterior/interior PNG fields."""
from pathlib import Path
import json,hashlib,argparse
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,gaussian_filter,map_coordinates,label
from scipy.optimize import least_squares
from u_bowls import contours,NAMES
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/u-bowls-baseline'
T=np.linspace(0,1,48);B=np.array([(1-T)**3,3*(1-T)**2*T,3*(1-T)*T*T,T**3]).T
LIMITS=[(.2,.65),(.25,.65),(.08,.65),(.005,.45),(.2,.75),(.25,.65),(.005,.45),(.55,.995),(.2,.75)]


def samples(p,k,lower):
    result=[]
    for start,segs,_ in contours(p,k,lower):
        current=np.array(start)
        for seg in [*segs,start]:
            if len(seg)==2 and isinstance(seg[0],(float,int,np.floating)):
                end=np.array(seg);piece=current[None,:]*(1-T[:,None])+end[None,:]*T[:,None]
            else:piece=B@np.array([current,*seg]);end=np.array(seg[-1])
            result.append(piece);current=end
    return result


def edges(values):
    result=[]
    for i in range(1,len(values)):
        if (values[i-1]>=.5)!=(values[i]>=.5):
            lo=max(0,i-2);hi=min(len(values),i+2);area=sum(values[lo:hi])
            result.append(hi-area if values[i]>=.5 else lo+area)
    return result


def fit(folder,r,d):
    ch=r['character'];lower=ch=='u';size=d['pointSize'];sc=d['pixelScale'];ox,oy=d['originPixels']
    l,b,w,h=r['system']['inkBounds'];top=b+h
    full=np.asarray(Image.open(folder/r['system']['file']).convert('L'),dtype=float)
    x0=int(ox+l*sc)-16;y0=int(oy-top*sc)-16;x1=int(ox+(l+w)*sc)+17;y1=int(oy-b*sc)+17
    ink=1-full[y0:y1,x0:x1]/255;binary=ink>.5
    closed=binary.copy();by=round(oy-(b+h*.96)*sc)-y0
    bx0=round(ox+(l+w*.01)*sc)-x0;bx1=round(ox+(l+w*.99)*sc)-x0
    closed[by:by+2,bx0:bx1]=True
    labels,n=label(~closed);background=labels[0,0];candidates=[i for i in range(1,n+1) if i!=background]
    assert candidates,'Temporary top bridge must enclose an interior'
    hole=labels==max(candidates,key=lambda i:np.count_nonzero(labels==i))
    def field(mask):
        raw=distance_transform_edt(~mask)-distance_transform_edt(mask)
        return gaussian_filter(raw-.5*np.sign(raw),.45)
    outer_field=field(binary|hole);inner_field=field(hole);ink_field=field(binary)
    # Stem top caps and the tiny notch use the actual ink field.
    # The temporary bridge ends below the stem tops. Use actual ink for
    # the straight inside edges so that the bridge cannot bias those stems.
    fields=([outer_field]*3+[ink_field,outer_field,ink_field,outer_field,ink_field,ink_field,inner_field,inner_field,ink_field,ink_field]) if lower else ([outer_field]*4+[ink_field,ink_field,inner_field,inner_field,ink_field,ink_field])
    py=round(oy-(b+h*.8)*sc)-y0;ee=edges(ink[py]);assert len(ee)==4,(ch,ee)
    il=((ee[1]+x0-ox)/sc-l)/w;ir=((ee[2]+x0-ox)/sc-l)/w
    yy,xx=np.where(hole);hx=(xx+.5+x0-ox)/sc;hy=(oy-yy-.5-y0)/sc
    iby=(hy.min()-b)/h;ib=(np.mean(hx[hy<hy.min()+2/sc])-l)/w
    names=NAMES+(['capLeft','joinX'] if lower else [])
    initial=[.40,.43 if lower else .50,.20 if lower else .40,il,.42,ib,iby,ir,.44]
    limits=LIMITS.copy();handle_count=9 if lower else 8
    if lower:
        capBottom=-b/h;row=round(oy-(b+h*(capBottom+.012))*sc)-y0
        cap_edges=edges(ink[row]);cap=((cap_edges[-2]+x0-ox)/sc-l)/w
        initial.extend([cap,cap-.008]);limits.extend([(.5,.995),(.5,.995)])
    lo=np.array([v[0] for v in limits]+[.001]*handle_count);hi=np.array([v[1] for v in limits]+[1.1]*handle_count)
    for key,value in {'innerLeftX':il,'innerRightX':ir,'innerBottomY':iby,**({'capLeft':cap} if lower else {})}.items():
        i=names.index(key);lo[i]=max(lo[i],value-.005);hi[i]=min(hi[i],value+.005)
    x=np.clip(initial+[.55]*8+([.1] if lower else []),lo+1e-7,hi-1e-7)
    def unpack(v):
        p=dict(zip(names,v[:len(names)]))
        if lower:p['capBottomY']=capBottom
        return p,v[len(names):]
    def residual(v):
        p,k=unpack(v);rs=[]
        pieces=samples(p,k,lower);assert len(pieces)==len(fields)
        for pts,f in zip(pieces,fields):
            xx=ox+(l+pts[:,0]*w)*sc-x0-.5;yy=oy-(b+pts[:,1]*h)*sc-y0-.5
            rs.append(map_coordinates(f,[yy,xx],order=1,mode='nearest'))
        constraints=[p['innerRightX']-p['innerLeftX']-.05,p['innerLeftY']-p['innerBottomY']-.06,p['innerRightY']-p['innerBottomY']-.06]
        if lower:constraints.extend([p['capLeft']-p['joinX'],p['outerRightY']-p['capBottomY']-.03,p['joinX']-p['outerBottomX']-.03])
        return np.concatenate([*rs,np.minimum(constraints,0)*5000])
    f1=least_squares(lambda v:residual(np.r_[v,x[len(names):]]),x[:len(names)],bounds=(lo[:len(names)],hi[:len(names)]),max_nfev=180,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    x[:len(names)]=f1.x
    f2=least_squares(residual,x,bounds=(lo,hi),max_nfev=350,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    p,k=unpack(f2.x);preview=Image.new('L',(ink.shape[1],ink.shape[0]),255);draw=ImageDraw.Draw(preview)
    pts=np.concatenate(samples(p,k,lower));draw.polygon([(ox+(l+a*w)*sc-x0,oy-(b+c*h)*sc-y0) for a,c in pts],fill=0)
    path=ROOT/'build'/f'u-bowls-fit-{ch}-{d["weight"]}-{size}.png';sheet=Image.new('L',(preview.width*2,preview.height),255);sheet.paste(preview,(0,0));sheet.paste(Image.fromarray(np.uint8((1-ink)*255)),(preview.width,0));sheet.save(path)
    shape={'parameters':{key:float(v) for key,v in p.items()},'handles':[float(v) for v in k],
           'bounds':[l*1000/size,b*1000/size,(l+w)*1000/size,top*1000/size]}
    diag={'character':ch,'weight':d['weight'],'size':size,'rmsPixels':float(np.sqrt(np.mean(residual(f2.x)**2))),
          'evaluations':f1.nfev+f2.nfev,'optimizerSuccess':bool(f2.success),'preview':str(path.relative_to(ROOT))}
    print(diag,flush=True);return shape,diag


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--one',action='store_true');args=parser.parse_args()
    result={'method':'Authored four-cubic U/u bowls and straight stems; separate PNG fields; no reference vectors','glyphs':{},'runs':[],'diagnostics':[]}
    for weight in ([400] if args.one else (100,400,900)):
        for size,mode in ([(64,'display')] if args.one else [(16,'text'),(64,'display')]):
            folder=BASE/f'{weight}-{size}';path=folder/'render-settings.json';d=json.loads(path.read_text());assert d['referenceWeightMode']=='axis'
            for r in d['records']:
                assert r['system']['renderedFonts']==[d['systemPostScriptName']]
                shape,diag=fit(folder,r,d);result['glyphs'].setdefault(r['character'],{}).setdefault(str(weight),{})[mode]=shape
                result['diagnostics'].append(diag)
            result['runs'].append({'report':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'os':d['os']})
            (ROOT/'build/u-bowls-fit-progress.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (ROOT/('build/u-bowls-one.json' if args.one else 'sources/u-bowls.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
