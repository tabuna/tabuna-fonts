"""Measure square brackets as three bars for the existing math-bands model."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.agl import UV2AGL
from font_recovery.measure import Flatten,scan


def rectangle(left,bottom,right,top):
    return dict(x=(left+right)/2,y=(bottom+top)/2,width=right-left,height=top-bottom)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(glyphs={},measurements=[])
    for w in [100,400,900]:
      for label,opt in [('text',17),('display',28)]:
        gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400))
        for ch in '[]':
            flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);cs=[(np.array(c)*1000/f['head'].unitsPerEm).tolist() for c in flat.contours];points=np.concatenate(cs);left,bottom=points.min(0);right,top=points.max(0)
            stems=[scan(cs,y,nonzero=True) for y in np.linspace(bottom+.3*(top-bottom),bottom+.7*(top-bottom),51)];assert all(len(r)==1 for r in stems);stem=np.mean(np.array(stems)[:,0,:],axis=0);assert np.max(abs(np.array(stems)[:,0,:]-stem))<1e-6
            x=left+.9*(right-left) if ch=='[' else left+.1*(right-left);ends=scan(cs,x,vertical=True,nonzero=True);assert len(ends)==2
            bars=[rectangle(float(stem[0]),float(bottom),float(stem[1]),float(top))]+[rectangle(float(left),b,float(right),t) for b,t in ends]
            data['glyphs'].setdefault(UV2AGL[ord(ch)],{}).setdefault(str(w),{})[label]=dict(bars=bars,slashes=[],bracket_direction=1 if ch=='[' else -1);data['measurements'].append(dict(character=ch,weight=w,optical=opt,stem_scan_count=51))
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(a.out)


if __name__=='__main__':main()
