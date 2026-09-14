"""Measure Z/z as horizontal bars and one affine diagonal band."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.measure_diagonal_family import band

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');out=dict(glyphs={},measurements=[])
 for ch in 'Zz':
  for w in [100,400,900]:
   for label,opt in [('text',17),('display',28)]:
    gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);cs=[(np.array(c)*1000/f['head'].unitsPerEm).tolist() for c in flat.contours];v=np.concatenate(cs);lo,hi=v.min(0),v.max(0)
    tl,tr=scan(cs,hi[1]-1e-5,nonzero=True)[0];bl,br=scan(cs,lo[1]+1e-5,nonzero=True)[0]
    tb=scan(cs,tl+1e-5,vertical=True,nonzero=True)[-1][0];bt=scan(cs,br-1e-5,vertical=True,nonzero=True)[0][1]
    ys=np.linspace(bt+(tb-bt)*.1,tb-(tb-bt)*.1,101);runs=[scan(cs,y,nonzero=True) for y in ys];assert all(len(r)==1 for r in runs);edges=np.array([r[0] for r in runs]);diag,error=band(ys,edges,bt,tb);assert error<1e-7
    bars=[dict(x=float((bl+br)/2),y=float((lo[1]+bt)/2),width=float(br-bl),height=float(bt-lo[1])),dict(x=float((tl+tr)/2),y=float((hi[1]+tb)/2),width=float(tr-tl),height=float(hi[1]-tb))]
    out['glyphs'].setdefault(ch,{}).setdefault(str(w),{})[label]=dict(bars=bars,slashes=[diag],lower_tip=float(scan(cs,bt+1e-6,nonzero=True)[0][1]),upper_tip=float(scan(cs,tb-1e-6,nonzero=True)[0][0]));out['measurements'].append(dict(character=ch,weight=w,optical=opt,max_line_residual=error))
 args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
