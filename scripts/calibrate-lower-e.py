#!/usr/bin/env python3
"""Fit an authored e construction against a raster distance field.

The number and roles of arcs are fixed in lower_e.py. The input is a PNG;
no reference font tables, vector paths, or reference point topology are read.
Acceptance remains a separate real-font pixel comparison.
"""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,gaussian_filter,map_coordinates,label
from scipy.optimize import least_squares
from lower_e import contours,NAMES
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/lower-e-baseline'
T=np.linspace(0,1,36);B=np.array([(1-T)**3,3*(1-T)**2*T,3*(1-T)*T*T,T**3]).T
LIMITS=[(.32,.62),(.01,.5),(.3,.7),(.01,.4),(.5,.999),(.8,1.0),(.16,.4),(.3,.7),(.35,.65),(.3,.7),(.4,.65),(.01,.5),(.5,.999),(.4,.72),(.3,.7),(.6,.995)]


def sample(p,k):
    result=[]
    for start,segs,_ in contours(p,k):
        pieces=[]
        current=np.array(start)
        for seg in [*segs,start]:
            if len(seg)==2 and isinstance(seg[0],(float,int,np.floating)):
                end=np.array(seg);piece=current[None,:]*(1-T[:,None])+end[None,:]*T[:,None]
            else:
                piece=B@np.array([current,*seg]);end=np.array(seg[-1])
            pieces.append(piece);current=end
        result.append(np.concatenate(pieces))
    return result


def fit(folder,r,d,seed=None):
    size=d['pointSize'];scale=d['pixelScale'];ox,oy=d['originPixels']
    l,b,w,h=r['system']['inkBounds'];top=b+h
    full=np.asarray(Image.open(folder/r['system']['file']).convert('L'),dtype=float)
    x0=int(ox+l*scale)-16;y0=int(oy-top*scale)-16
    x1=int(ox+(l+w)*scale)+17;y1=int(oy-b*scale)+17
    ink=1-full[y0:y1,x0:x1]/255;binary=ink>.5
    labels,count=label(~binary)
    background=labels[0,0]
    candidates=[i for i in range(1,count+1) if i!=background]
    assert candidates, 'The reference must have one closed counter'
    hole=labels==max(candidates,key=lambda i:np.count_nonzero(labels==i))
    def distance(mask):
        raw=distance_transform_edt(~mask)-distance_transform_edt(mask)
        return gaussian_filter(raw-.5*np.sign(raw),.45)
    fields=[distance(binary|hole),distance(hole)]
    yy,xx=np.where(hole)
    hx=(xx+.5+x0-ox)/scale;hy=(oy-yy-.5-y0)/scale
    cl=(hx.min()-l)/w;cr=(hx.max()-l)/w;cb=(hy.min()-b)/h;cty=(hy.max()-b)/h
    ct=(float(np.mean(hx[hy>hy.max()-2/scale]))-l)/w
    sy=1-cty
    initial=[cb-sy*.85,cl,.51,sy,.99-cl,.99,.29,.50,.49,.50,.53,cl,cr,cb,ct,cty]
    initial_handles=[.55,.55,.55,.15,.40,.15,.45,.55,.55,.55,.55,.55,.55,.55,.10,.5,.55,.55,.10,.5]
    lo=np.array([v[0] for v in LIMITS]+[.001]*20);hi=np.array([v[1] for v in LIMITS]+[1.1]*20)
    for key,value in {'counterLeftX':cl,'counterRightX':cr,'counterBottomY':cb,'counterTopY':cty}.items():
        i=NAMES.index(key);initial[i]=value;lo[i]=max(lo[i],value-.006);hi[i]=min(hi[i],value+.006)
    start=initial+initial_handles if seed is None else [seed['parameters'][n] for n in NAMES]+seed['handles']
    x=np.clip(np.array(start),lo+1e-6,hi-1e-6)
    def unpack(v):return dict(zip(NAMES,v[:len(NAMES)])),v[len(NAMES):]
    def penalty(p):
        pairs=[(p['counterBottomY']-p['crossY'],.015),(p['crossY']-p['tipY'],.04),
            (p['tipY']-p['innerBottomY'],.03),(p['tipOuterX']-p['tipInnerX'],.02),
            (p['innerBottomX']-p['innerLeftX'],.04),(p['tipInnerX']-p['innerBottomX'],.03),
            (p['counterTopX']-p['counterLeftX'],.025),(p['counterRightX']-p['counterTopX'],.025),
            (p['counterTopY']-p['counterBottomY'],.04),(p['outerRightY']-p['crossY'],.005)]
        return np.array([min(0,a-b)*5000 for a,b in pairs])
    def residual(v):
        p,k=unpack(v);distances=[]
        for points,field in zip(sample(p,k),fields):
            xx=ox+(l+points[:,0]*w)*scale-x0-.5;yy=oy-(b+points[:,1]*h)*scale-y0-.5
            distances.append(map_coordinates(field,[yy,xx],order=1,mode='nearest'))
        return np.concatenate([*distances,penalty(p)])
    # Position landmarks first, then release the bounded tangent lengths.
    f1=least_squares(lambda v:residual(np.r_[v,x[len(NAMES):]]),x[:len(NAMES)],bounds=(lo[:len(NAMES)],hi[:len(NAMES)]),max_nfev=180,ftol=1e-7,xtol=1e-7,gtol=1e-7)
    x[:len(NAMES)]=f1.x
    f2=least_squares(residual,x,bounds=(lo,hi),max_nfev=350,ftol=1e-7,xtol=1e-7,gtol=1e-7)
    p,k=unpack(f2.x)
    preview=Image.new('L',(ink.shape[1],ink.shape[0]),255);draw=ImageDraw.Draw(preview)
    for start,segs,counter in contours(p,k):
        current=np.array(start);vertices=[]
        for seg in [*segs,start]:
            if len(seg)==2 and isinstance(seg[0],(float,int,np.floating)):
                end=np.array(seg);pts=current[None,:]*(1-T[:,None])+end[None,:]*T[:,None]
            else:pts=B@np.array([current,*seg]);end=np.array(seg[-1])
            vertices.extend([(ox+(l+xx*w)*scale-x0,oy-(b+yy*h)*scale-y0) for xx,yy in pts]);current=end
        draw.polygon(vertices,fill=255 if counter else 0)
    ours=1-np.asarray(preview)/255
    iou=float(np.minimum(ours,ink).sum()/np.maximum(ours,ink).sum())
    path=ROOT/'build'/f'e-fit-{d["weight"]}-{size}-{ord(r["character"]):04X}.png'
    sheet=Image.new('L',(preview.width*2,preview.height),255);sheet.paste(preview,(0,0));sheet.paste(Image.fromarray(np.uint8((1-ink)*255)),(preview.width,0));sheet.save(path)
    result={'parameters':{key:float(v) for key,v in p.items()},'handles':[float(v) for v in k],
        'bounds':[l*1000/size,b*1000/size,(l+w)*1000/size,top*1000/size],
        'advance':r['system']['advance']*1000/size}
    diagnostic={'rmsPixels':float(np.sqrt(np.mean(residual(f2.x)**2))),'polygonPreviewInkIoU':iou,'evaluations':f1.nfev+f2.nfev,'optimizerSuccess':bool(f2.success),'initialization':'manual' if seed is None else 'another fitted own glyph','preview':str(path.relative_to(ROOT))}
    print(r['character'],d['weight'],size,diagnostic,flush=True)
    return result,diagnostic


def refine(result):
    result['seedRefinements']=[]
    for i,diagnostic in enumerate(list(result['diagnostics'])):
        if diagnostic['rmsPixels']<=1:continue
        ch=diagnostic['character'];twin='е' if ch=='e' else 'e';weight=diagnostic['weight'];size=diagnostic['size'];mode='text' if size==16 else 'display'
        folder=BASE/f'{weight}-{size}';d=json.loads((folder/'render-settings.json').read_text())
        r=next(r for r in d['records'] if r['character']==ch)
        seed=result['glyphs'][twin][str(weight)][mode]
        p,trial=fit(folder,r,d,seed)
        accepted=trial['rmsPixels']<diagnostic['rmsPixels']
        result['seedRefinements'].append({'character':ch,'weight':weight,'size':size,'beforeRMS':diagnostic['rmsPixels'],'afterRMS':trial['rmsPixels'],'accepted':accepted})
        if accepted:
            result['glyphs'][ch][str(weight)][mode]=p
            result['diagnostics'][i]={'character':ch,'weight':weight,'size':size,**trial}
    return result


def main():
    result={'method':'Authored six-outer/two-inner cubic construction; bounded scalar fitting against PNG distance field; no reference paths','glyphs':{},'runs':[],'diagnostics':[]}
    for weight in (100,400,900):
        for size,mode in [(16,'text'),(64,'display')]:
            folder=BASE/f'{weight}-{size}';path=folder/'render-settings.json';d=json.loads(path.read_text())
            assert d['weight']==weight and d['referenceWeightMode']=='axis'
            for r in d['records']:
                assert r['system']['renderedFonts']==[d['systemPostScriptName']]
                p,diagnostic=fit(folder,r,d)
                result['glyphs'].setdefault(r['character'],{}).setdefault(str(weight),{})[mode]=p
                result['diagnostics'].append({'character':r['character'],'weight':weight,'size':size,**diagnostic})
                (ROOT/'build/lower-e-fit-progress.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
            result['runs'].append({'report':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'weight':weight,'size':size,'os':d['os']})
    refine(result)
    (ROOT/'sources/lower-e.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
