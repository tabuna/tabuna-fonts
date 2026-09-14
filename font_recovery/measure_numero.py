"""Measure numero's construction dimensions and fit its shared oval."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.measure_rings import fit_pair


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(weights={},measurements=[])
    for w in [100,400,900]:
      for label,opt in [('text',17),('display',28)]:
        gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[8470]].draw(flat)
        assert len(flat.contours)==4
        cs=sorted(flat.contours,key=lambda c:np.ptp(np.array(c)[:,1]),reverse=True)
        ring,e=fit_pair(cs[1:3],f['head'].unitsPerEm);scale=1000/f['head'].unitsPerEm
        c=(np.array(cs[0])*scale).tolist();v=np.array(c);bottom=float(v[:,1].min());top=float(v[:,1].max());ys=np.linspace(bottom+.47*(top-bottom),bottom+.53*(top-bottom),51);runs=[scan([c],y,nonzero=True) for y in ys];assert all(len(r)==3 for r in runs)
        stems=[runs[25][0],runs[25][-1]];edges=np.array([r[1] for r in runs]);diagonal=[];errors=[]
        for i in [0,1]:
            slope,offset=np.polyfit(ys,edges[:,i],1);diagonal.append([float(slope),float(offset)]);errors.append(float(max(abs(edges[:,i]-(slope*ys+offset)))))
        bar=np.array(cs[3])*scale;p=dict(n=dict(stems=stems,bottom=bottom,top=top,diagonal=diagonal),ring=ring,bar=np.r_[bar.min(0),bar.max(0)].tolist());data['weights'].setdefault(str(w),{})[label]=p;row=dict(weight=w,optical=opt,ring_residuals=e,line_residuals=errors);data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
