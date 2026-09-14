"""Fit Q with common round contours and scalar line measurements of its tail."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.measure_rings import fit_pair


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(weights={},measurements=[])
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[81]].draw(flat);assert len(flat.contours)==3;rounds=[c for c in flat.contours if len(c)>20];tail=[c for c in flat.contours if len(c)==4];assert len(rounds)==2 and len(tail)==1;bowl,errors=fit_pair(rounds,f['head'].unitsPerEm);v=np.array(tail[0])*1000/f['head'].unitsPerEm;lo=v.min(0);hi=v.max(0);ys=np.linspace(lo[1]+.1*(hi[1]-lo[1]),lo[1]+.9*(hi[1]-lo[1]),51);edges=np.array([scan([v.tolist()],y,nonzero=True)[0] for y in ys]);center=edges.mean(1);width=np.diff(edges,axis=1)[:,0];s,b=np.polyfit(ys,center,1);ws,wi=np.polyfit(ys,width,1);err=max(float(max(abs(center-(s*ys+b)))),float(max(abs(width-(ws*ys+wi)))));assert err<1e-7
   p=dict(bowl=bowl,tail=dict(slope=float(s),intercept=float(b),width=float(wi),width_slope=float(ws),bottom=float(lo[1]),top=float(hi[1])));data['weights'].setdefault(str(w),{})[label]=p;row=dict(weight=w,optical=opt,bowl_residuals=errors,line_residual=err);data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
