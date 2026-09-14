"""Measure the upright and rising-band edge equations of one."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(weights={},measurements=[])
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[49]].draw(flat);cs=[(np.array(c)*1000/f['head'].unitsPerEm).tolist() for c in flat.contours];v=np.concatenate(cs);lo=v.min(0);hi=v.max(0);stem=scan(cs,.1*hi[1],nonzero=True)[0][0];xs=np.linspace(lo[0]+.1*(stem-lo[0]),lo[0]+.8*(stem-lo[0]),51);edges=np.array([scan(cs,x,vertical=True,nonzero=True)[0] for x in xs]);lower=np.polyfit(xs,edges[:,0],1);upper=np.polyfit(xs,edges[:,1],1);err=max(float(max(abs(np.polyval(lower,xs)-edges[:,0]))),float(max(abs(np.polyval(upper,xs)-edges[:,1]))));assert err<1e-6
   p=dict(extent=[float(lo[0]),float(hi[0])],stem=float(stem),height=float(hi[1]),upper=upper.tolist(),lower=lower.tolist());data['weights'].setdefault(str(w),{})[label]=p;data['measurements'].append(dict(weight=w,optical=opt,line_residual=err))
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(data['measurements'])


if __name__=='__main__':main()
