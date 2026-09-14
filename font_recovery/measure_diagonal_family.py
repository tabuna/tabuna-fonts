"""Recover upright and diagonal edge equations from silhouette sections."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan


def band(ys,edges,lo,hi):
 center=edges.mean(1);width=np.diff(edges,axis=1)[:,0]
 s,b=np.polyfit(ys,center,1);ws,wi=np.polyfit(ys,width,1)
 error=max(np.max(abs(center-(s*ys+b))),np.max(abs(width-(ws*ys+wi))))
 return dict(slope=float(s),intercept=float(b),width=float(wi),width_slope=float(ws),bottom=float(lo),top=float(hi)),float(error)


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');prod=TTFont('dist/TabunaSansVariable.ttf');out=dict(glyphs={},measurements=[])
 for ch in 'NИиXxХх^':
  key=prod.getBestCmap()[ord(ch)];out['glyphs'][key]={}
  for w in [100,400,900]:
   for label,opt in [('text',17),('display',28)]:
    gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);cs=[(np.array(c)*1000/f['head'].unitsPerEm).tolist() for c in flat.contours];v=np.concatenate(cs);lo,hi=v.min(0),v.max(0);h=hi[1]-lo[1];p=dict(bars=[],slashes=[]);errors=[]
    if ch in 'NИи':
     samples=[(y,scan(cs,y,nonzero=True)) for y in np.linspace(lo[1]+.25*h,lo[1]+.75*h,151)];samples=[(y,r) for y,r in samples if len(r)==3];assert len(samples)>10,(ch,w,opt)
     ys=np.array([y for y,r in samples]);runs=np.array([r for y,r in samples]);b,e=band(ys,runs[:,1,:],lo[1],hi[1]);p['slashes'].append(b);errors.append(e)
     for idx in [0,2]:
      edges=np.median(runs[:,idx,:],axis=0);p['bars'].append(dict(x=float(edges.mean()),y=float((lo[1]+hi[1])/2),width=float(edges[1]-edges[0]),height=float(h)))
    else:
     for low,high,start,end in ([(.05,.25,lo[1],hi[1])] if ch=='^' else [(.05,.2,lo[1],lo[1]+h/2),(.8,.95,lo[1]+h/2,hi[1])]):
      samples=[(y,scan(cs,y,nonzero=True)) for y in np.linspace(lo[1]+low*h,lo[1]+high*h,51)];samples=[(y,r) for y,r in samples if len(r)==2];assert len(samples)>10,(ch,w,opt)
      ys=np.array([y for y,r in samples]);runs=np.array([r for y,r in samples])
      for idx in [0,1]:
       b,e=band(ys,runs[:,idx,:],start,end);p['slashes'].append(b);errors.append(e)
    out['glyphs'][key].setdefault(str(w),{})[label]=p;out['measurements'].append(dict(character=ch,weight=w,optical=opt,max_line_residual=max(errors)))
 args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out['measurements']))

if __name__=='__main__':main()
