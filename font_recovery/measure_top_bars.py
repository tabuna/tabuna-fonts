"""Measure scalar widths and heights of upright/top-bar constructions."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();font=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(glyphs={},measurements=[])
 for ch in 'TГг':
  for weight in [100,400,900]:
   for label,optical in [('text',17),('display',28)]:
    gs=font.getGlyphSet(location=dict(wght=weight,opsz=optical,wdth=100,GRAD=400));pen=Flatten(gs);gs[font.getBestCmap()[ord(ch)]].draw(pen)
    cs=[(np.array(c)*1000/font['head'].unitsPerEm).tolist() for c in pen.contours];points=np.concatenate(cs);left,bottom=points.min(0);right,top=points.max(0)
    samples=np.array([scan(cs,y,nonzero=True)[0] for y in np.linspace(bottom+.1*(top-bottom),bottom+.7*(top-bottom),31)]);assert np.max(np.ptp(samples,axis=0))<1e-7;sl,sr=np.mean(samples,axis=0)
    x=(sr+right)/2;vertical=scan(cs,x,vertical=True,nonzero=True);assert len(vertical)==1;bar_bottom=vertical[0][0]
    p=dict(left=float(left),right=float(right),bottom=float(bottom),top=float(top),stem_left=float(sl),stem_right=float(sr),bar_bottom=float(bar_bottom))
    data['glyphs'].setdefault(ch,{}).setdefault(str(weight),{})[label]=p
    data['measurements'].append(dict(character=ch,weight=weight,optical=optical,upright_spread=float(np.max(np.ptp(samples,axis=0)))))
 args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
