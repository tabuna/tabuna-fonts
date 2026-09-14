"""Scalar bounds and section measurements for a shared Phi oval/stem model."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(glyphs={},measurements=[])
 for ch in 'Фф':
  for w in [100,400,900]:
   for label,opt in [('text',17),('display',28)]:
    gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));z=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(z);assert len(z.contours)==3;cs=[np.array(c)*1000/f['head'].unitsPerEm for c in z.contours];body=max(cs,key=lambda c:np.ptp(c[:,1]));holes=[c for c in cs if c is not body];lo,hi=body.min(0),body.max(0);stem=scan([c.tolist() for c in cs],hi[1]-.001,nonzero=True)[0];inner=np.concatenate(holes);il,ih=inner.min(0),inner.max(0);outside=body[(body[:,0]<stem[0]-.001)|(body[:,0]>stem[1]+.001)];ol,oh=outside.min(0),outside.max(0)
    def oval(bounds):return dict(bounds=list(map(float,bounds)),handles=[[.5522847498,.5522847498] for _ in range(4)])
    p=dict(stem=[float(stem[0]),float(lo[1]),float(stem[1]),float(hi[1])],outer=oval([lo[0],ol[1],hi[0],oh[1]]),inner=oval([il[0],il[1],ih[0],ih[1]]));key=f'uni{ord(ch):04X}';data['glyphs'].setdefault(key,{}).setdefault(str(w),{})[label]=p;data['measurements'].append(dict(character=ch,weight=w,optical=opt,method='Measured bounds and top stem section; oval parameters are seeds awaiting section-moment fitting.'))
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
