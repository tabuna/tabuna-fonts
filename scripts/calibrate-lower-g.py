#!/usr/bin/env python3
"""Fit an authored g against PNG distance fields; never read reference vectors."""
from pathlib import Path
import argparse,json,hashlib,importlib.util
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,gaussian_filter,map_coordinates,label
from scipy.optimize import least_squares
from lower_g import contours,NAMES
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/lower-g-baseline'
spec=importlib.util.spec_from_file_location('rect_fit',ROOT/'scripts/calibrate-rectilinear.py');rect=importlib.util.module_from_spec(spec);spec.loader.exec_module(rect)
T=np.linspace(0,1,40);B=np.array([(1-T)**3,3*(1-T)**2*T,3*(1-T)*T*T,T**3]).T


def sample(p,k):
    result=[]
    for start,segs,_ in contours(p,k):
        current=np.array(start);pieces=[]
        for seg in [*segs,start]:
            if len(seg)==2 and isinstance(seg[0],(float,int,np.floating)):
                end=np.array(seg);piece=current[None,:]*(1-T[:,None])+end[None,:]*T[:,None]
            else:piece=B@np.array([current,*seg]);end=np.array(seg[-1])
            pieces.append(piece);current=end
        result.append(pieces)
    return result


def fit(folder,r,d):
    size,scale=d['pointSize'],d['pixelScale'];ox,oy=d['originPixels'];l,b,w,h=r['system']['inkBounds'];top=b+h
    full=np.asarray(Image.open(folder/r['system']['file']).convert('L'),dtype=float)
    x0=int(ox+l*scale)-16;y0=int(oy-top*scale)-16;x1=int(ox+(l+w)*scale)+17;y1=int(oy-b*scale)+17
    ink=1-full[y0:y1,x0:x1]/255;binary=ink>.5
    def enclosed(mask):
        labels,count=label(~mask);background=labels[0,0];holes=[i for i in range(1,count+1) if i!=background]
        assert len(holes)==1,('Expected one bounded white region',len(holes));return labels==holes[0]
    hole=enclosed(binary)
    def distance(mask):
        raw=distance_transform_edt(~mask)-distance_transform_edt(mask)
        return gaussian_filter(raw-.5*np.sign(raw),.45)
    def coordinates(mask):
        yy,xx=np.where(mask);return ((xx+.5+x0-ox)/scale-l)/w,(oy-yy-.5-y0-b*scale)/(scale*h)
    hx,hy=coordinates(hole)
    it=float(hx[hy>hy.max()-2/(scale*h)].mean());ib=float(hx[hy<hy.min()+2/(scale*h)].mean())
    il,ir,ity,iby=float(hx.min()),float(hx.max()),float(hy.max()),float(hy.min())
    ily=float(hy[hx<hx.min()+2/(scale*w)].mean());iry=float(hy[hx>hx.max()-2/(scale*w)].mean())
    stems=[]
    for y in np.linspace(.90,.97,20):
        py=round(oy-(b+h*y)*scale)-y0;edges=rect.edges(ink[py].tolist())
        if len(edges)>=4 and abs(((edges[-1]+x0-ox)/scale-l)/w-1)<.004:stems.append(((edges[-2]+x0-ox)/scale-l)/w)
    assert stems,'No exposed right stem';s=max(stems)
    px=round(ox+(l+w*(s+1)/2)*scale)-x0;ey=rect.edges(ink[:,px].tolist());st=(oy-ey[0]-y0-b*scale)/(scale*h)
    px=round(ox+(l+w*(il+ir)/2)*scale)-x0;ey=rect.edges(ink[:,px].tolist());assert len(ey)==6,('Body and tail need six scalar transitions',ey)
    yedges=[(oy-y-y0-b*scale)/(scale*h) for y in ey];bodyBottom=yedges[3];tailInnerBottom=yedges[4]
    yy,xx=np.indices(ink.shape);nx=((xx+.5+x0-ox)/scale-l)/w;ny=(oy-yy-.5-y0-b*scale)/(scale*h)
    low=binary&(ny<bodyBottom-.025)&(nx<.4);tipY=float(ny[low].max())+.5/(scale*h)
    py=round(oy-(b+h*(tipY-.003))*scale)-y0;edges=rect.edges(ink[py].tolist());assert len(edges)>=4
    to=((edges[0]+x0-ox)/scale-l)/w;ti=((edges[1]+x0-ox)/scale-l)/w
    # A temporary raster bridge identifies the open tail's inner white region.
    # It is used only by the objective; it is never added to the authored contour.
    closed=binary|hole;bridge=closed.copy();px=round(ox+(l+w*(to+ti)/2)*scale)-x0
    ya=round(oy-(b+h*.65)*scale)-y0;yb=round(oy-(b+h*(tipY-.02))*scale)-y0;bridge[ya:yb,px:px+2]=True
    tailHole=enclosed(bridge)
    bodyField=distance(closed);tailOuterField=distance(bridge|tailHole);tailInnerField=distance(tailHole)
    fields=[bodyField,tailOuterField,tailOuterField,bodyField,tailInnerField,tailInnerField]+[bodyField]*9+[distance(hole)]*5
    initial=[.28,.52,to,ti,tipY,.28,.51,tailInnerBottom,.46,bodyBottom,.63,.46,s-.015,bodyBottom+.14,s-.015,.86,il,ily,ir,iry,it,ity,ib,iby]
    limits=[(.15,.42),(.3,.7),(max(0,to-.02),to+.02),(ti-.02,ti+.02),(tipY-.002,tipY+.002),(.16,.45),(.3,.7),(tailInnerBottom-.008,tailInnerBottom+.008),
            (.25,.7),(bodyBottom-.008,bodyBottom+.008),(.45,.80),(.25,.7),(s-.08,s),(.30,.65),(s-.08,s),(.73,.98),
            (max(.001,il-.006),il+.006),(iby+.025,ity-.025),(ir-.006,min(.999,ir+.006)),(iby+.025,ity-.025),(il+.025,ir-.025),(ity-.006,ity+.006),(il+.025,ir-.025),(iby-.006,iby+.006)]
    lo=np.array([a for a,b in limits]+[.001]*28);hi=np.array([b for a,b in limits]+[1.1]*28)
    handles=[.55,.55,.55,.10,.45,.10,.45,.55,.55,.55,.25,.55,.55,.55,.55,.55,.55,.55,.25,.55]+[.55]*8
    x=np.clip(np.array(initial+handles),lo+1e-6,hi-1e-6)
    def unpack(v):return {**dict(zip(NAMES,v[:len(NAMES)])),'stem':s,'stemTop':st},v[len(NAMES):]
    def residual(v):
        p,k=unpack(v);pieces=[seg for contour in sample(p,k) for seg in contour];assert len(pieces)==len(fields)
        ds=[]
        for points,field in zip(pieces,fields):
            xx=ox+(l+points[:,0]*w)*scale-x0-.5;yy=oy-(b+points[:,1]*h)*scale-y0-.5
            ds.append(map_coordinates(field,[yy,xx],order=1,mode='nearest'))
        pairs=[(p['tipInnerX']-p['tipOuterX'],.01),(p['tipY']-p['tailInnerBottomY'],.008),
               (p['tailRightY']-p['tailInnerBottomY'],.02),(p['tailInnerRightY']-p['tailInnerBottomY'],.02),
               (p['bodyBottomY']-p['tailInnerBottomY'],.04),(p['innerBottomY']-p['bodyBottomY'],.005),
               (p['innerTopY']-p['innerLeftY'],.025),(p['innerLeftY']-p['innerBottomY'],.025),
               (p['innerTopY']-p['innerRightY'],.025),(p['innerRightY']-p['innerBottomY'],.025),
               (p['joinBottomY']-p['tailInnerRightY'],.008),(p['joinTopY']-p['joinBottomY'],.1)]
        return np.concatenate([*ds,[min(0,a-b)*5000 for a,b in pairs]])
    f1=least_squares(lambda v:residual(np.r_[v,x[len(NAMES):]]),x[:len(NAMES)],bounds=(lo[:len(NAMES)],hi[:len(NAMES)]),max_nfev=180,ftol=1e-7,xtol=1e-7,gtol=1e-7);x[:len(NAMES)]=f1.x
    f2=least_squares(residual,x,bounds=(lo,hi),max_nfev=400,ftol=1e-7,xtol=1e-7,gtol=1e-7);p,k=unpack(f2.x)
    preview=Image.new('L',(ink.shape[1],ink.shape[0]),255);draw=ImageDraw.Draw(preview)
    for pieces,counter in zip(sample(p,k),(False,True)):
        draw.polygon([(ox+(l+x*w)*scale-x0,oy-(b+y*h)*scale-y0) for x,y in np.concatenate(pieces)],fill=255 if counter else 0)
    ours=1-np.asarray(preview)/255;iou=float(np.minimum(ours,ink).sum()/np.maximum(ours,ink).sum())
    path=ROOT/'build'/f'lower-g-fit-{d["weight"]}-{size}.png';sheet=Image.new('L',(preview.width*2,preview.height),255)
    sheet.paste(preview,(0,0));sheet.paste(Image.fromarray(np.uint8((1-ink)*255)),(preview.width,0));sheet.save(path)
    result={'parameters':{key:float(v) for key,v in p.items()},'handles':[float(v) for v in k],'bounds':[v*1000/size for v in (l,b,l+w,top)]}
    diagnostic={'rmsPixels':float(np.sqrt(np.mean(residual(f2.x)**2))),'polygonPreviewInkIoU':iou,'evaluations':f1.nfev+f2.nfev,'optimizerSuccess':bool(f2.success),'preview':str(path.relative_to(ROOT))}
    print(d['weight'],size,diagnostic,flush=True);return result,diagnostic


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--one',action='store_true');args=parser.parse_args()
    result={'method':'Authored eight-exterior/four-counter cubic g; bounded fitting against separate body, tail, and counter PNG fields; no reference vectors','glyphs':{'g':{}},'runs':[],'diagnostics':[]}
    for weight in ([400] if args.one else [100,400,900]):
        for size,mode in ([(16,'text')] if args.one else [(16,'text'),(64,'display')]):
            folder=BASE/f'{weight}-{size}';path=folder/'render-settings.json';d=json.loads(path.read_text());assert d['referenceWeightMode']=='axis'
            r=d['records'][0];assert r['system']['renderedFonts']==[d['systemPostScriptName']]
            p,diag=fit(folder,r,d);result['glyphs']['g'].setdefault(str(weight),{})[mode]=p
            result['diagnostics'].append({'weight':weight,'size':size,**diag});result['runs'].append({'report':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'os':d['os']})
            (ROOT/'build/lower-g-fit-progress.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/('build/lower-g-one.json' if args.one else 'sources/lower-g.json')).write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
