"""Measure rotated eight lobe and oval-counter landmarks, not outline nodes."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(weights={},measurements=[])
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));pen=Flatten(gs);gs[f.getBestCmap()[56]].draw(pen);v=np.concatenate(pen.contours);lo=v.min(0);hi=v.max(0);cs=[]
   for c in pen.contours:
    v=(np.array(c)-lo)/(hi-lo);cs.append(np.column_stack([v[:,1],1-v[:,0]]))
   outer=cs[0];waist=scan([outer.tolist()],.5,vertical=True,nonzero=True)[0]
   def profile(v):
    low,high=v.min(0),v.max(0)
    def at(axis,value,other):return float(np.mean(v[np.abs(v[:,axis]-value)<1e-6,other]))
    return dict(left=float(low[0]),axis=at(0,low[0],1),top=float(high[1]),bottom=float(low[1]),top_x=at(1,high[1],0),bottom_x=at(1,low[1],0),upper_slope=1,lower_slope=1,handles=[[.35,.35] for _ in range(4)])
   left=outer[outer[:,0]<=.5];right=outer[outer[:,0]>=.5].copy();right[:,0]=1-right[:,0];p=dict(bounds=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist(),upper=[.5,float(waist[1])],lower=[.5,float(waist[0])],left=profile(left),right=profile(right),counters=[])
   for c in sorted(cs[1:],key=lambda v:v[:,0].min()):p['counters'].append(dict(bounds=np.r_[c.min(0),c.max(0)].tolist(),handles=[[.5522847498,.5522847498] for _ in range(4)]))
   data['weights'].setdefault(str(w),{})[label]=p;data['measurements'].append(dict(weight=w,optical=opt,method='Rotated normalized scalar bounds, extrema and central section; parameters are seeds pending fitting.'))
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n')

if __name__=='__main__':main()
