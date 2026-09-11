#!/usr/bin/env python3
"""Fit fixed M/W polygon topology to native PNG ink."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,gaussian_filter,map_coordinates
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/mw-baseline'
T=np.linspace(0,1,48)
TOPO={
 'M':[(0,0),(0,1),(.16,1),(.5,.08),(.84,1),(1,1),(1,0),(.84,0),(.84,.78),(.5,.16),(.16,.78),(.16,0)],
 'W':[(0,1),(.14,1),(.25,.05),(.5,.82),(.75,.05),(.86,1),(1,1),(1,0),(.86,0),(.75,.68),(.5,.16),(.25,.68),(.14,0),(0,0)]}

def edge_samples(points):
    out=[]
    for a,b in zip(points,points[1:]+points[:1]):out.append(np.array(a)[None,:]*(1-T[:,None])+np.array(b)[None,:]*T[:,None])
    return np.concatenate(out)

def fit(folder,d,ch):
    r=next(r for r in d['records'] if r['character']==ch);size=d['pointSize'];sc=d['pixelScale'];ox,oy=d['originPixels']
    l,b,w,h=r['system']['inkBounds'];top=b+h
    full=np.asarray(Image.open(folder/r['system']['file']).convert('L'),dtype=float)
    x0=int(ox+l*sc)-14;y0=int(oy-top*sc)-14;x1=int(ox+(l+w)*sc)+15;y1=int(oy-b*sc)+15
    ink=1-full[y0:y1,x0:x1]/255;mask=ink>.5
    field=gaussian_filter(distance_transform_edt(~mask)-distance_transform_edt(mask)-.5*np.sign(distance_transform_edt(~mask)-distance_transform_edt(mask)),.45)
    initial=np.array(TOPO[ch],dtype=float)
    # Hold the extrema fixed at the measured scalar bounds; only internal
    # joins and diagonal tips are fitted.
    # The vertical roles (stem top, valley and inner return) are part of the
    # fixed topology. Fit only horizontal joins; allowing the optimizer to
    # move those y values can self-intersect the M/W polygon.
    variable=[i for i,p in enumerate(initial) if not (p[0] in (0,1) and p[1] in (0,1))]
    x=np.array([initial[i][0] for i in variable]);lo=np.array([max(0,initial[i][0]-.14) for i in variable]);hi=np.array([min(1,initial[i][0]+.14) for i in variable])
    def unpack(v):
        p=initial.copy()
        for i,value in zip(variable,v):p[i,0]=value
        return p
    def residual(v):
        p=unpack(v);pts=edge_samples(p);xx=ox+(l+pts[:,0]*w)*sc-x0-.5;yy=oy-(b+pts[:,1]*h)*sc-y0-.5
        return map_coordinates(field,[yy,xx],order=1,mode='nearest')
    f=least_squares(residual,x,bounds=(lo,hi),max_nfev=420,ftol=1e-8,xtol=1e-8,gtol=1e-8)
    p=unpack(f.x);preview=Image.new('L',(ink.shape[1],ink.shape[0]),255);draw=ImageDraw.Draw(preview)
    draw.polygon([(ox+(l+px*w)*sc-x0,oy-(b+py*h)*sc-y0) for px,py in p],fill=0)
    path=ROOT/'build'/f'mw-fit-{ch}-{d["weight"]}-{size}.png';sheet=Image.new('L',(preview.width*2,preview.height),255);sheet.paste(preview,(0,0));sheet.paste(Image.fromarray(np.uint8((1-ink)*255)),(preview.width,0));sheet.save(path)
    return {'points':[(float((l+px*w)*1000/size),float((b+py*h)*1000/size)) for px,py in p],'advance':r['system']['advance']*1000/size},{'character':ch,'weight':d['weight'],'size':size,'rmsPixels':float(np.sqrt(np.mean(residual(f.x)**2))),'evaluations':f.nfev,'optimizerSuccess':bool(f.success),'preview':str(path.relative_to(ROOT))}

def main():
    out={'method':'Fixed authored polygon topology for M/W, fitted to native PNG distance fields; no reference vectors','glyphs':{},'runs':[],'diagnostics':[]}
    for weight in (100,400,900):
        for size,mode in ((16,'text'),(64,'display')):
            folder=BASE/f'{weight}-{size}';path=folder/'render-settings.json';d=json.loads(path.read_text())
            for ch in 'MW':
                shape,diag=fit(folder,d,ch);out['glyphs'].setdefault(ch,{}).setdefault(str(weight),{})[mode]=shape;out['diagnostics'].append(diag)
            out['runs'].append({'report':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'weight':weight,'size':size,'os':d['os']})
            (ROOT/'build/mw-fit-progress.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'sources/mw.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Calibrated M/W',flush=True)
if __name__=='__main__':main()
