"""Fit scalar edge equations of folded diagonal bands from interior sections."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.measure_diagonal_family import band

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');prod=TTFont('dist/TabunaSansVariable.ttf');out=dict(glyphs={},measurements=[])
 for ch in 'VvwMМм':
  for w in [100,400,900]:
   for label,opt in [('text',17),('display',28)]:
    gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);cs=[(np.array(c)*1000/f['head'].unitsPerEm).tolist() for c in flat.contours];v=np.concatenate(cs);lo,hi=v.min(0),v.max(0);h=hi[1]-lo[1];count=2 if ch in 'Vv' else 4
    samples=[(y,scan(cs,y,nonzero=True)) for y in np.linspace(lo[1]+.1*h,lo[1]+.9*h,401)];samples=[(y,r) for y,r in samples if len(r)==count];assert len(samples)>10,(ch,w,opt)
    ys=np.array([y for y,r in samples]);runs=np.array([r for y,r in samples]);p=dict(bars=[],slashes=[],left=float(lo[0]),right=float(hi[0]));errors=[]
    for i in range(count):
     b,e=band(ys,runs[:,i,:],lo[1],hi[1]);p['slashes'].append(b);errors.append(e)
    # Fold seams come from intersections of fitted band centerlines.
    # A vertical center section measures the horizontal optical join cap.
    joins=[(0,1,'bottom')] if ch in 'Vv' else [(0,1,'bottom'),(1,2,'top'),(2,3,'bottom')] if ch=='w' else [(0,1,'top'),(1,2,'bottom'),(2,3,'top')]
    p['joins']=[]
    for i,j,end in joins:
     a,b=p['slashes'][i],p['slashes'][j];y=(b['intercept']-a['intercept'])/(a['slope']-b['slope']);x=a['slope']*y+a['intercept'];clip=not(ch in 'MМм' and end=='top')
     if not clip:
      mid=(lo[1]+hi[1])/2
      ar=(a['slope']+a['width_slope']/2)*mid+a['intercept']+a['width']/2
      bl=(b['slope']-b['width_slope']/2)*mid+b['intercept']-b['width']/2
      x=ar+1e-5 if i==0 else bl-1e-5
     segments=scan(cs,x,vertical=True,nonzero=True);segment=segments[0] if end=='bottom' else segments[-1]
     lower,upper=(float(lo[1]),float(np.median(ys))) if end=='bottom' else (float(np.median(ys)),float(hi[1]))
     for _ in range(60):
      level=(lower+upper)/2
      ar=(a['slope']+a['width_slope']/2)*level+a['intercept']+a['width']/2
      bl=(b['slope']-b['width_slope']/2)*level+b['intercept']-b['width']/2
      middle=(ar+bl)/2
      joined=ar>=bl or any(l<=middle<=r for l,r in scan(cs,level,nonzero=True))
      if joined==(end=='bottom'):lower=level
      else:upper=level
     cap=(lower+upper)/2
     if clip and ch in 'MМм':
      for part in [a,b]:part['bottom' if end=='bottom' else 'top']=float(segment[0] if end=='bottom' else segment[1])
     p['joins'].append(dict(left=i,right=j,x=float(x),seam_slope=float((a['slope']+a['width_slope']/2+b['slope']-b['width_slope']/2)/2),seam_intercept=float((a['intercept']+a['width']/2+b['intercept']-b['width']/2)/2),cap=float(cap),direction=1 if end=='bottom' else -1,clip=int(clip)))
    out['glyphs'].setdefault(prod.getBestCmap()[ord(ch)],{}).setdefault(str(w),{})[label]=p;out['measurements'].append(dict(character=ch,weight=w,optical=opt,max_line_residual=max(errors),interior_sections=len(ys)))
 args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out['measurements'],ensure_ascii=False))
if __name__=='__main__':main()
