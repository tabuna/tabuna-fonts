"""Measure compact symbols as scalar round profiles and oriented bands."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.agl import UV2AGL
from font_recovery.measure import Flatten,scan
from font_recovery.measure_rings import fit_pair


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(glyphs={},measurements=[])
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400))
   for ch in ':÷…`×':
    flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);p=dict(rounds=[],bands=[]);errors=[]
    for c in flat.contours:
     if len(c)>20:
      q,e=fit_pair([c,c],f['head'].unitsPerEm);p['rounds'].append(dict(bounds=q['bounds'][0],handles=q['outerHandles']));errors.append(e[0]);continue
     assert len(c)==4;v=np.array(c)*1000/f['head'].unitsPerEm;_,vectors=np.linalg.eigh(np.cov(v.T));direction=vectors[:,-1];direction*=1 if direction[1]>=0 else -1;direction=direction if ch=='×' else np.array([0.,1.]);normal=np.array([direction[1],-direction[0]]);u=np.stack([v@normal,v@direction],1);lo=u.min(0);hi=u.max(0);ys=np.linspace(lo[1]+.1*(hi[1]-lo[1]),lo[1]+.9*(hi[1]-lo[1]),51);edges=np.array([scan([u.tolist()],y,nonzero=True)[0] for y in ys]);center=edges.mean(1);width=edges[:,1]-edges[:,0];s,b=np.polyfit(ys,center,1);ws,wi=np.polyfit(ys,width,1);error=max(float(max(abs(center-(s*ys+b)))),float(max(abs(width-(ws*ys+wi)))));errors.append(error);p['bands'].append(dict(direction=direction.tolist(),profile=dict(slope=float(s),intercept=float(b),width=float(wi),width_slope=float(ws),bottom=float(lo[1]),top=float(hi[1]))))
    data['glyphs'].setdefault(UV2AGL[ord(ch)],{}).setdefault(str(w),{})[label]=p;row=dict(character=ch,weight=w,optical=opt,fit_residuals=errors);data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
