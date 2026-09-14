"""Fit quotation/commas as line-defined bands and a measured detached oval."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.agl import UV2AGL
from font_recovery.measure import Flatten,scan


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--chars',default=',;‘’“”„');a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(glyphs={},measurements=[])
    for w in [100,400,900]:
      for label,opt in [('text',17),('display',28)]:
        gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400))
        for ch in a.chars:
            flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);p=dict(bars=[],slashes=[],ovals=[]);errors=[]
            for raw in flat.contours:
                c=(np.array(raw)*1000/f['head'].unitsPerEm).tolist();v=np.array(c);lo=v.min(0);hi=v.max(0)
                if len(raw)>20:
                    assert ch in ';!';p['ovals'].append(np.r_[lo,hi].tolist());continue
                ys=np.linspace(lo[1]+.1*(hi[1]-lo[1]),lo[1]+.9*(hi[1]-lo[1]),51);runs=[scan([c],y,nonzero=True) for y in ys];assert all(len(r)==1 for r in runs);edges=np.array(runs)[:,0,:];center=edges.mean(1);width=edges[:,1]-edges[:,0];slope,offset=np.polyfit(ys,center,1);ws,wi=np.polyfit(ys,width,1);error=max(float(max(abs(center-(slope*ys+offset)))),float(max(abs(width-(ws*ys+wi)))));assert error<1e-7
                p['slashes'].append(dict(slope=float(slope),intercept=float(offset),width=float(wi),width_slope=float(ws),bottom=float(lo[1]),top=float(hi[1])));errors.append(error)
            p['slashes'].sort(key=lambda b:b['intercept']);data['glyphs'].setdefault(UV2AGL[ord(ch)],{}).setdefault(str(w),{})[label]=p;data['measurements'].append(dict(character=ch,weight=w,optical=opt,line_residual=max(errors)))
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('Measured',len(data['glyphs']),'characters')


if __name__=='__main__':main()
