"""Measure k's ascender, arm height, edge equations and junction floor."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');d=dict(glyphs={'k':{}},measurements=[])
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));z=Flatten(gs);gs[f.getBestCmap()[ord('k')]].draw(z);cs=[(np.array(c)*1000/f['head'].unitsPerEm).tolist() for c in z.contours];v=np.concatenate(cs);h=v[:,1].max();stem=scan(cs,h*.99,nonzero=True)[0];arm=max(y for x,y in v if x>stem[1]+1);p=dict(stem=stem,stem_top=float(h),top=float(arm));errors={}
   for role,fractions in [('upper',np.linspace(.82,.98,31)),('lower',np.linspace(.02,.18,31))]:
    ys=fractions*arm;runs=[scan(cs,y,nonzero=True) for y in ys];assert all(len(r)==2 for r in runs);edges=np.array(runs)[:,1,:];p[role]={}
    for j,side in enumerate(['left','right']):
     line=np.polyfit(ys,edges[:,j],1);p[role][side]=line.tolist();errors[role+'_'+side]=float(max(abs(np.polyval(line,ys)-edges[:,j])))
   floors=[scan(cs,stem[1]+(stem[1]-stem[0])*t,vertical=True,nonzero=True)[0][0] for t in [.01,.02,.03]]
   if np.ptp(floors)<.01:p['upper']['floor']=float(np.mean(floors))
   d['glyphs']['k'].setdefault(str(w),{})[label]=p;d['measurements'].append(dict(weight=w,optical=opt,line_residuals=errors,floor_spread=float(np.ptp(floors))))
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(d,indent=2)+'\n');print(d['measurements'])

if __name__=='__main__':main()
