#!/usr/bin/env python3
"""Fit authored diacritic recipes to isolated reference PNG ink and scalar placement."""
from pathlib import Path
import json,hashlib,unicodedata as ud,argparse
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label,find_objects,distance_transform_edt,gaussian_filter,map_coordinates,binary_dilation
from scipy.optimize import least_squares
from reading_marks import contours
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/reading-marks-baseline'
DONORS={'circumflex':'ĝ','circumflex.cap':'Ĝ','circumflex.ascender':'ĥ','breve':'ğ','breve.cap':'Ğ',
        'breve.cyrl':'й','breve.cyrl.cap':'Й','dotabove':'ġ','dotabove.cap':'Ġ','commaabove.g':'ģ'}
T=np.linspace(0,1,36);B=np.array([(1-T)**3,3*(1-T)**2*T,3*(1-T)*T*T,T**3]).T


def samples(kind,p):
    result=[]
    for start,segs in contours(kind,p):
        current=np.array(start)
        for seg in [*segs,start]:
            if len(seg)==2 and isinstance(seg[0],(float,int,np.floating)):
                end=np.array(seg);piece=current[None,:]*(1-T[:,None])+end[None,:]*T[:,None]
            else:piece=B@np.array([current,*seg]);end=np.array(seg[-1])
            result.append(piece);current=end
    return np.concatenate(result)


def extract(folder,r,d):
    size,scale=d['pointSize'],d['pixelScale'];ox,oy=d['originPixels'];l,b,w,h=r['system']['inkBounds']
    full=np.asarray(Image.open(folder/r['system']['file']).convert('L'))
    x0=int(ox+l*scale)-12;x1=int(ox+(l+w)*scale)+13;y0=int(oy-(b+h)*scale)-12;y1=int(oy-b*scale)+13
    raw=1-full[y0:y1,x0:x1]/255;labels,n=label(raw>.5);objects=find_objects(labels)
    parts=[(i+1,box) for i,box in enumerate(objects) if box]
    assert len(parts)>=2,(r['character'],'No detached reference diacritic')
    chosen,box=min(parts,key=lambda pair:pair[1][0].start)
    mask=labels==chosen;ys,xs=box
    area=raw*binary_dilation(mask,iterations=2)
    crop=area[max(0,ys.start-8):ys.stop+8,max(0,xs.start-8):xs.stop+8]
    cx=x0+max(0,xs.start-8);cy=y0+max(0,ys.start-8)
    top=b+h;bottom=(oy-(y0+ys.stop))/scale;left=(x0+xs.start-ox)/scale;right=(x0+xs.stop-ox)/scale
    binary=crop>.5;distance=distance_transform_edt(~binary)-distance_transform_edt(binary)
    field=gaussian_filter(distance-.5*np.sign(distance),.45)
    return {'ink':crop,'field':field,'origin':[ox-cx,oy-cy],'size':size,'scale':scale,'bounds':[left,bottom,right,top]}


def fit_shape(kind,e):
    l,b,r,t=e['bounds'];w=r-l;h=t-b;ox,oy=e['origin'];sc=e['scale']
    if kind=='circumflex':
        initial=[.4,.6,.31,.69,.5,.75];limits=[(.05,.49),(.51,.95),(.02,.48),(.52,.98),(.3,.7),(.1,.97)];names=['topLeft','topRight','innerLeft','innerRight','innerX','innerY']
    elif kind=='commaabove':initial=[.35,.65];limits=[(.0,.75),(.25,1.)];names=['topLeft','bottomRight']
    elif kind=='dotabove':initial=[.55228475];limits=[(.45,.68)];names=['k']
    else:
        initial=[.5,.5,.4,.18,.82]+[0,.55,.55,.55,0,.55,0,.55,.55,.55,0,.55]
        limits=[(.3,.7),(.3,.7),(.02,.85),(.01,.48),(.52,.99)]+[(0,1.1)]*12;names=['outerX','innerX','innerY','innerLeft','innerRight']
    lo=np.array([v[0] for v in limits]+[-.03,-.03,-.03,-.03]);hi=np.array([v[1] for v in limits]+[.03,.03,.03,.03])
    x=np.array(initial+[0,0,0,0])
    def unpack(v):
        p=dict(zip(names,v[:len(names)]))
        if kind=='breve':p['handles']=list(v[5:17])
        dl,db,dr,dt=v[-4:];return p,(l+dl*w,b+db*h,r+dr*w,t+dt*h)
    def residual(v):
        p,(ll,bb,rr,tt)=unpack(v);pts=samples(kind,p)
        xx=ox+(ll+pts[:,0]*(rr-ll))*sc-.5;yy=oy-(bb+pts[:,1]*(tt-bb))*sc-.5
        ds=map_coordinates(e['field'],[yy,xx],order=1,mode='nearest')
        # The topmost scalar image bound is known independently of raster fitting.
        return np.r_[ds,(tt-t)*sc*2]
    fit=least_squares(residual,x,bounds=(lo,hi),max_nfev=300,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    p,(ll,bb,rr,tt)=unpack(fit.x);factor=1000/e['size']
    shape={'parameters':{k:[float(x) for x in v] if isinstance(v,list) else float(v) for k,v in p.items()},'dimensions':[(rr-ll)*factor,(tt-bb)*factor],'defaultOffset':[0.,0.]}
    placement={'x':(ll+rr)/2*factor,'y':bb*factor}
    return shape,placement,{'rmsPixels':float(np.sqrt(np.mean(residual(fit.x)**2))),'evaluations':fit.nfev,'optimizerSuccess':bool(fit.success)}


def fit_position(kind,shape,e):
    pts=samples(kind,shape['parameters']);w,h=shape['dimensions'];size=e['size'];sc=e['scale'];ox,oy=e['origin'];l,b,r,t=e['bounds']
    factor=size/1000;points=(pts*np.array([w,h])-np.array([w/2,0]))*factor
    def residual(v):
        xx=ox+(points[:,0]+v[0])*sc-.5;yy=oy-(points[:,1]+v[1])*sc-.5
        return map_coordinates(e['field'],[yy,xx],order=1,mode='nearest')
    seed=np.array([(l+r)/2,b]);fit=least_squares(residual,seed,bounds=(seed-.08*size,seed+.08*size),max_nfev=80,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    return {'x':float(fit.x[0]/factor),'y':float(fit.x[1]/factor)},{'rmsPixels':float(np.sqrt(np.mean(residual(fit.x)**2))),'evaluations':fit.nfev,'optimizerSuccess':bool(fit.success)}


def profile_for(ch):
    if ch=='ģ':return 'commaabove.g'
    if ch=='ĥ':return 'circumflex.ascender'
    mark=ud.normalize('NFD',ch)[1];base={'\u0302':'circumflex','\u0306':'breve','\u0307':'dotabove'}[mark]
    if ch in 'ЙйЎў':base+='.cyrl'
    return base+('.cap' if ch.isupper() else '')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--one',action='store_true');args=parser.parse_args()
    cfg=json.loads((BASE/'characters.json').read_text());result={'method':'Ten shared authored diacritic profiles; PNG-isolated ink, bounded shape fitting and scalar translations, no reference vectors','profiles':{},'placements':{},'runs':[],'diagnostics':[]}
    # Only our source anchors are read to preserve default combining placement on g.
    from build import Source
    for weight in ([400] if args.one else [100,400,900]):
        for size,mode in ([(16,'text')] if args.one else [(16,'text'),(64,'display')]):
            folder=BASE/f'{weight}-{size}';path=folder/'render-settings.json';d=json.loads(path.read_text());records={r['character']:r for r in d['records']}
            assert d['referenceWeightMode']=='axis'
            extracted={}
            for ch in cfg['affected']:
                assert records[ch]['system']['renderedFonts']==[d['systemPostScriptName']]
                extracted[ch]=extract(folder,records[ch],d)
            shapes={};source=Source(weight,size)
            for profile,donor in DONORS.items():
                kind=profile.split('.')[0];shape,pos,diag=fit_shape(kind,extracted[donor]);shapes[profile]=shape
                base=source.ensure(ud.normalize('NFD',donor)[0]);anchor=next(a for a in base.anchors if a.name=='top')
                shape['defaultOffset']=[pos['x']-anchor.x,pos['y']-anchor.y]
                result['profiles'].setdefault(profile,{'kind':kind,'donor':donor,'masters':{}})['masters'].setdefault(str(weight),{})[mode]=shape
                result['diagnostics'].append({'profile':profile,'weight':weight,'size':size,**diag});print('Shape',profile,weight,size,diag,flush=True)
            for ch in cfg['affected']:
                profile=profile_for(ch);kind=profile.split('.')[0];pos,diag=fit_position(kind,shapes[profile],extracted[ch])
                result['placements'].setdefault(ch,{'profile':profile,'masters':{}})['masters'].setdefault(str(weight),{})[mode]=pos
                result['diagnostics'].append({'character':ch,'profile':profile,'weight':weight,'size':size,**diag})
            result['runs'].append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'os':d['os']})
            (ROOT/'build/reading-marks-fit-progress.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('Placed',weight,size,flush=True)
    (ROOT/('build/reading-marks-one.json' if args.one else 'sources/reading-marks.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
