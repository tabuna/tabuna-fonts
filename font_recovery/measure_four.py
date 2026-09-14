"""Fit cubic edge functions to four's scalar scan intervals."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(weights={},measurements=[])
    for w in [100,400,900]:
      for label,opt in [('text',17),('display',28)]:
        gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[52]].draw(flat);assert len(flat.contours)==2;cs=[(np.array(c)*1000/f['head'].unitsPerEm).tolist() for c in flat.contours];pts=np.concatenate(cs);left=float(pts[:,0].min());right=float(pts[:,0].max());top=float(pts[:,1].max());bb,bt=scan(cs,right-.01*(right-left),vertical=True,nonzero=True)[0];lower=scan(cs,top*.1,nonzero=True)[0];upper=scan(cs,top*.6,nonzero=True)[-1];hole=min(cs,key=lambda c:np.ptp(np.array(c)[:,1]));hole_top=max(y for x,y in hole);p=dict(top=top,bar=[left,right,bb,bt],stems=[lower,upper]);errors=[]
        for field,high,side in [('outer',top*.98,0),('inner',hole_top-top*.04,1)]:
            ys=np.linspace(bt+top*.04,high,81);runs=[scan(cs,y,nonzero=True) for y in ys]
            if side:assert all(len(r)==2 for r in runs)
            xs=np.array([r[0][side] for r in runs]);c=np.polyfit(ys/top,xs,3);p[field]=c.tolist();errors.append(float(max(abs(np.polyval(c,ys/top)-xs))))
        data['weights'].setdefault(str(w),{})[label]=p;data['measurements'].append(dict(weight=w,optical=opt,max_edge_errors=errors))
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(data['measurements'])


if __name__=='__main__':main()
