#!/usr/bin/env python3
"""Fit fixed authored bowl arcs to separate outer/counter PNG distance fields.

Reference input is raster ink plus scalar extents. No reference vector paths,
font tables or point topology are read. Binary raster acceptance is separate.
"""
from pathlib import Path
import argparse,json,hashlib,importlib.util
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,gaussian_filter,map_coordinates,label
from scipy.optimize import least_squares
from stem_bowls import contours,NAMES
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/stem-bowls-baseline'
spec=importlib.util.spec_from_file_location('rect_fit',ROOT/'scripts/calibrate-rectilinear.py');rect=importlib.util.module_from_spec(spec);spec.loader.exec_module(rect)
T=np.linspace(0,1,40);B=np.array([(1-T)**3,3*(1-T)**2*T,3*(1-T)*T*T,T**3]).T


def sample(p,k):
    result=[]
    for start,segs,_ in contours(p,k):
        pieces=[];current=np.array(start)
        for seg in [*segs,start]:
            if len(seg)==2 and isinstance(seg[0],(float,int,np.floating)):
                end=np.array(seg);piece=current[None,:]*(1-T[:,None])+end[None,:]*T[:,None]
            else:piece=B@np.array([current,*seg]);end=np.array(seg[-1])
            pieces.append(piece);current=end
        result.append(np.concatenate(pieces))
    return result


def fit(folder,r,d,seed=None):
    size,scale=d['pointSize'],d['pixelScale'];ox,oy=d['originPixels'];ch=r['character'];mirror=ch in 'dq'
    l,b,w,h=r['system']['inkBounds'];top=b+h
    full=np.asarray(Image.open(folder/r['system']['file']).convert('L'),dtype=float)
    x0=int(ox+l*scale)-16;y0=int(oy-top*scale)-16;x1=int(ox+(l+w)*scale)+17;y1=int(oy-b*scale)+17
    ink=1-full[y0:y1,x0:x1]/255;binary=ink>.5
    labels,count=label(~binary);background=labels[0,0];holes=[i for i in range(1,count+1) if i!=background]
    assert len(holes)==1, 'Reference must have exactly one closed counter'
    hole=labels==holes[0]
    def distance(mask):
        raw=distance_transform_edt(~mask)-distance_transform_edt(mask)
        return gaussian_filter(raw-.5*np.sign(raw),.45)
    fields=[distance(binary|hole),distance(hole)]
    def coordinates(mask):
        yy,xx=np.where(mask);xs=((xx+.5+x0-ox)/scale-l)/w
        return (1-xs if mirror else xs),(oy-yy-.5-y0-b*scale)/(scale*h)
    hx,hy=coordinates(hole);xx,yy=coordinates(binary)
    # Exposed part of the stem supplies three scalar edges, independently of the bowl.
    py=round(oy-(b+h*(.9 if ch in 'bd' else .1))*scale)-y0
    edges=rect.edges(ink[py].tolist());assert len(edges)==2
    ex=[((e+x0-ox)/scale-l)/w for e in edges];s=1-ex[0] if mirror else ex[1]
    px=round(ox+(l+w*(1-s/2 if mirror else s/2))*scale)-x0
    ey=rect.edges(ink[:,px].tolist());assert len(ey)==2
    st=(oy-ey[0]-y0-b*scale)/(scale*h);sb=(oy-ey[1]-y0-b*scale)/(scale*h)
    bowl=xx>s+.04;ty=float(yy[bowl].max());by=float(yy[bowl].min())
    it=float(hx[hy>hy.max()-2/(scale*h)].mean());ib=float(hx[hy<hy.min()+2/(scale*h)].mean())
    il,ir,ity,iby=float(hx.min()),float(hx.max()),float(hy.max()),float(hy.min())
    ily=float(hy[hx<hx.min()+2/(scale*w)].mean());iry=float(hy[hx>hx.max()-2/(scale*w)].mean())
    span=ty-by
    initial=[s+.015,ty-span*.18,s+.015,by+span*.18,.55,ty,.55,by,(ty+by)/2,il,ily,ir,iry,it,ity,ib,iby]
    limits=[(s,s+.08),(by+span*.55,ty-.005),(s,s+.08),(by+.005,by+span*.45),(.30,.80),(ty-.006,ty+.006),(.30,.80),(by-.006,by+.006),(by+span*.3,by+span*.7),
            (max(.001,il-.006),il+.006),(iby+.03,ity-.03),(ir-.006,min(.999,ir+.006)),(iby+.03,ity-.03),(il+.03,ir-.03),(ity-.006,ity+.006),(il+.03,ir-.03),(iby-.006,iby+.006)]
    lo=np.array([a for a,b in limits]+[.001]*18);hi=np.array([b for a,b in limits]+[1.1]*18)
    k=[.25,.55,.55,.55,.55,.55,.55,.55,.25,.55]+[.55]*8
    x=np.clip(np.array(initial+k if seed is None else [seed['parameters'][n] for n in NAMES]+seed['handles']),lo+1e-6,hi-1e-6)
    def unpack(v):return {**dict(zip(NAMES,v[:len(NAMES)])),'stem':s,'stemTop':st,'stemBottom':sb},v[len(NAMES):]
    def residual(v):
        p,k=unpack(v);distances=[]
        for points,field in zip(sample(p,k),fields):
            xs=1-points[:,0] if mirror else points[:,0]
            px=ox+(l+xs*w)*scale-x0-.5;py=oy-(b+points[:,1]*h)*scale-y0-.5
            distances.append(map_coordinates(field,[py,px],order=1,mode='nearest'))
        pairs=[(p['outerTopY']-p['innerTopY'],.004),(p['innerBottomY']-p['outerBottomY'],.004),
               (p['innerTopY']-p['innerLeftY'],.025),(p['innerLeftY']-p['innerBottomY'],.025),
               (p['innerTopY']-p['innerRightY'],.025),(p['innerRightY']-p['innerBottomY'],.025),
               (p['joinTopY']-p['joinBottomY'],.1)]
        return np.concatenate([*distances,[min(0,a-b)*5000 for a,b in pairs]])
    f1=least_squares(lambda v:residual(np.r_[v,x[len(NAMES):]]),x[:len(NAMES)],bounds=(lo[:len(NAMES)],hi[:len(NAMES)]),max_nfev=180,ftol=1e-7,xtol=1e-7,gtol=1e-7)
    x[:len(NAMES)]=f1.x
    f2=least_squares(residual,x,bounds=(lo,hi),max_nfev=350,ftol=1e-7,xtol=1e-7,gtol=1e-7)
    p,k=unpack(f2.x);preview=Image.new('L',(ink.shape[1],ink.shape[0]),255);draw=ImageDraw.Draw(preview)
    for points,counter in zip(sample(p,k),(False,True)):
        draw.polygon([(ox+(l+(1-x if mirror else x)*w)*scale-x0,oy-(b+y*h)*scale-y0) for x,y in points],fill=255 if counter else 0)
    ours=1-np.asarray(preview)/255;iou=float(np.minimum(ours,ink).sum()/np.maximum(ours,ink).sum())
    path=ROOT/'build'/f'stem-bowl-fit-{d["weight"]}-{size}-{ord(ch):04X}.png';sheet=Image.new('L',(preview.width*2,preview.height),255)
    sheet.paste(preview,(0,0));sheet.paste(Image.fromarray(np.uint8((1-ink)*255)),(preview.width,0));sheet.save(path)
    result={'parameters':{key:float(v) for key,v in p.items()},'handles':[float(v) for v in k],
            'bounds':[v*1000/size for v in (l,b,l+w,top)],'measuredAdvance':r['system']['advance']*1000/size}
    diagnostic={'rmsPixels':float(np.sqrt(np.mean(residual(f2.x)**2))),'polygonPreviewInkIoU':iou,'evaluations':f1.nfev+f2.nfev,'optimizerSuccess':bool(f2.success),'preview':str(path.relative_to(ROOT))}
    print(ch,d['weight'],size,diagnostic,flush=True);return result,diagnostic


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--one',action='store_true');args=parser.parse_args()
    result={'method':'Authored stem with four outer bowl arcs and four counter arcs; independent PNG distance fields, no reference vectors','glyphs':{},'runs':[],'diagnostics':[]}
    for weight in ([400] if args.one else [100,400,900]):
        for size,mode in ([(16,'text')] if args.one else [(16,'text'),(64,'display')]):
            folder=BASE/f'{weight}-{size}';path=folder/'render-settings.json';d=json.loads(path.read_text());assert d['referenceWeightMode']=='axis'
            for r in (d['records'][:1] if args.one else d['records']):
                assert r['system']['renderedFonts']==[d['systemPostScriptName']]
                p,diag=fit(folder,r,d);result['glyphs'].setdefault(r['character'],{}).setdefault(str(weight),{})[mode]=p
                result['diagnostics'].append({'character':r['character'],'weight':weight,'size':size,**diag})
                (ROOT/'build/stem-bowls-fit-progress.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
            result['runs'].append({'report':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'weight':weight,'size':size,'os':d['os']})
    (ROOT/('build/stem-bowls-one.json' if args.one else 'sources/stem-bowls.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
