"""Measure four hash bands away from intersection compensation notches."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(glyphs={'numbersign':{}},measurements=[])
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[35]].draw(flat);assert len(flat.contours)==4;p=dict(bars=[],slashes=[]);errors=[]
   for contour in flat.contours:
    v=np.array(contour)*1000/f['head'].unitsPerEm;lo=v.min(0);hi=v.max(0);vertical=np.ptp(v[:,1])>np.ptp(v[:,0]);fractions=np.r_[np.linspace(.03,.15,21),np.linspace(.85,.97,21)] if vertical else np.linspace(.2,.8,51);ys=lo[1]+fractions*(hi[1]-lo[1]);runs=[scan([v.tolist()],y,nonzero=True) for y in ys];assert all(len(r)==1 for r in runs);edges=np.array(runs)[:,0,:];center=edges.mean(1);width=edges[:,1]-edges[:,0];s,b=np.polyfit(ys,center,1);ws,wi=np.polyfit(ys,width,1);errors.append(float(max(max(abs(center-(s*ys+b))),max(abs(width-(ws*ys+wi))))));p['slashes'].append(dict(slope=float(s),intercept=float(b),width=float(wi),width_slope=float(ws),bottom=float(lo[1]),top=float(hi[1])))
   data['glyphs']['numbersign'].setdefault(str(w),{})[label]=p;data['measurements'].append(dict(weight=w,optical=opt,max_line_residual=max(errors)))
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(data['measurements'])


if __name__=='__main__':main()
