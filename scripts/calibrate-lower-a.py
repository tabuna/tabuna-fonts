#!/usr/bin/env python3
"""Fit an authored a construction against a raster distance field.

The number and roles of arcs are fixed in lower_a.py. The input is a PNG;
no reference font tables, vector paths, or reference point topology are read.
Acceptance remains a separate real-font pixel comparison.
"""
from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,gaussian_filter,map_coordinates,label
from scipy.optimize import least_squares
from lower_a import contours,NAMES
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/lower-a-baseline'
spec=importlib.util.spec_from_file_location('rect_fit',ROOT/'scripts/calibrate-rectilinear.py');rect=importlib.util.module_from_spec(spec);spec.loader.exec_module(rect)
T=np.linspace(0,1,36);B=np.array([(1-T)**3,3*(1-T)**2*T,3*(1-T)*T*T,T**3]).T
LIMITS=[(.02,.42),(.15,.8),(.10,.45),(.15,.8),(.35,.75),(.4,.75),(.55,.86),(.25,.8),(.60,.985),(.6,.90),(0,.25),(.05,.55),(.25,.8),(.45,.80),(.01,.55),(.08,.45),(.15,.8),(-.005,.35),(.12,.5),(.15,.8),(.2,.65),(.25,.7)]


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
    stems=[]
    for frac in np.linspace(.02,.65,35):
        py=round(oy-top*frac*scale)-y0
        edges=rect.edges(ink[py].tolist())
        if len(edges)>=2 and abs((edges[-1]+x0-ox)/scale-(l+w))<2/scale:
            stems.append(((edges[-2]+x0-ox)/scale-l)/w)
    s=max(stems);sx=1-s;sy=sx*w/top*.87;bottom=b/top
    initial=[.10+sx*.15,.44,.24,.44,.55,.60,.70,.53,1-sy,.78,.045,.045+sx,.50,.64,sx,.25,.43,bottom+sy,.31,.46,.55-sy,.60-sy]
    lo=np.array([v[0] for v in LIMITS]+[.05]*24);hi=np.array([v[1] for v in LIMITS]+[1.1]*24)
    # Scalar extents of the closed white counter initialize its own model;
    # its distance field cannot attract our counter to the external outline.
    yy,xx=np.where(hole)
    hx=(xx+.5+x0-ox)/scale;hy=(oy-yy-.5-y0)/scale
    cl=(hx.min()-l)/w;cby=hy.min()/top;ctry=hy.max()/top
    cly=float(np.mean(hy[hx<hx.min()+2/scale]))/top
    cbx=(float(np.mean(hx[hy<hy.min()+2/scale]))-l)/w
    cry=float(np.min(hy[hx>hx.max()-2/scale]))/top
    measured={'counterLeftX':cl,'counterBottomY':cby,'counterTopRightY':ctry,
              'counterLeftY':cly,'counterBottomX':cbx,'counterRightY':cry}
    for key,value in measured.items():
        i=NAMES.index(key);initial[i]=value
        radius=.006 if key in ('counterLeftX','counterBottomY','counterTopRightY') else .065
        lo[i]=max(lo[i],value-radius);hi[i]=min(hi[i],value+radius)
    initial[NAMES.index('counterTopX')]=(cl+s)/2
    initial[NAMES.index('counterTopY')]=ctry-.02
    start=initial+[.55]*24 if seed is None else [seed['parameters'][n] for n in NAMES]+seed['handles']
    x=np.clip(np.array(start),lo+1e-6,hi-1e-6)
    def unpack(v):return {**dict(zip(NAMES,v[:len(NAMES)])),'stem':s,'bottom':bottom},v[len(NAMES):]
    def penalty(p):
        pairs=[(p['tipInnerX']-p['tipOuterX'],sx*.35),(s-p['counterLeftX'],.06),
            (s-p['neckX'],.015),(p['counterTopX']-p['counterLeftX'],.02),(s-p['counterTopX'],.02),
            (p['counterBottomX']-p['counterLeftX'],.02),(s-p['counterBottomX'],.02),
            (p['counterLeftY']-p['counterBottomY'],.025),(p['counterTopY']-p['counterLeftY'],.025),
            (p['counterRightY']-p['counterBottomY'],.02),(p['counterTopRightY']-p['counterRightY'],.02),
            (p['neckY']-p['counterTopY'],.01),(p['bowlRightY']-p['counterTopRightY'],.01),
            (p['counterRightY']-p['notchY'],.005),(p['hookRightY']-p['bowlRightY'],.005),
            (p['innerTopY']-p['hookRightY'],.02),(p['innerTopY']-p['tipY'],.02),(1-p['innerTopY'],.015)]
        return np.array([min(0,a-b)*5000 for a,b in pairs])
    def residual(v):
        p,k=unpack(v);distances=[]
        for points,field in zip(sample(p,k),fields):
            xx=ox+(l+points[:,0]*w)*scale-x0-.5;yy=oy-points[:,1]*top*scale-y0-.5
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
            vertices.extend([(ox+(l+xx*w)*scale-x0,oy-yy*top*scale-y0) for xx,yy in pts]);current=end
        draw.polygon(vertices,fill=255 if counter else 0)
    ours=1-np.asarray(preview)/255
    iou=float(np.minimum(ours,ink).sum()/np.maximum(ours,ink).sum())
    path=ROOT/'build'/f'a-fit-{d["weight"]}-{size}-{ord(r["character"]):04X}.png'
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
        ch=diagnostic['character'];twin='а' if ch=='a' else 'a';weight=diagnostic['weight'];size=diagnostic['size'];mode='text' if size==16 else 'display'
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
    result={'method':'Authored eight-outer/four-inner cubic construction; bounded scalar fitting against PNG distance field; no reference paths','glyphs':{},'runs':[],'diagnostics':[]}
    for weight in (100,400,900):
        for size,mode in [(16,'text'),(64,'display')]:
            folder=BASE/f'{weight}-{size}';path=folder/'render-settings.json';d=json.loads(path.read_text())
            assert d['weight']==weight and d['referenceWeightMode']=='axis'
            for r in d['records']:
                assert r['system']['renderedFonts']==[d['systemPostScriptName']]
                p,diagnostic=fit(folder,r,d)
                result['glyphs'].setdefault(r['character'],{}).setdefault(str(weight),{})[mode]=p
                result['diagnostics'].append({'character':r['character'],'weight':weight,'size':size,**diagnostic})
                (ROOT/'build/lower-a-fit-progress.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
            result['runs'].append({'report':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'weight':weight,'size':size,'os':d['os']})
    refine(result)
    (ROOT/'sources/lower-a.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
