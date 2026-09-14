"""Measure rectangle dimensions and band slopes; never export outline nodes."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools import subset
from fontTools.agl import UV2AGL
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from font_recovery.measure import Flatten,scan


def profile(font,ch):
    gs=font.getGlyphSet();flat=Flatten(gs);gs[font.getBestCmap()[ord(ch)]].draw(flat)
    scale=1000/font['head'].unitsPerEm;bars=[];slashes=[];errors=[]
    for contour in flat.contours:
        points=np.array(contour);lo=points.min(axis=0);hi=points.max(axis=0)
        levels=np.linspace(lo[1]+(hi[1]-lo[1])*.1,hi[1]-(hi[1]-lo[1])*.1,9)
        intervals=[scan([contour],y,nonzero=True) for y in levels]
        assert all(len(r)==1 for r in intervals)
        intervals=np.array([r[0] for r in intervals]);centers=intervals.mean(axis=1)
        widths=intervals[:,1]-intervals[:,0];a,b=np.polyfit(levels,centers,1)
        error=float(max(np.max(abs(centers-(a*levels+b))),np.ptp(widths)))
        assert error<1e-5,'Expected a constant-width straight band'
        errors.append(error)
        if abs(a)<1e-10:
            bars.append(dict(x=float((lo[0]+hi[0])/2*scale),y=float((lo[1]+hi[1])/2*scale),
                             width=float((hi[0]-lo[0])*scale),height=float((hi[1]-lo[1])*scale)))
        else:
            slashes.append(dict(slope=float(a),intercept=float(b*scale),width=float(np.mean(widths)*scale),bottom=float(lo[1]*scale),top=float(hi[1]*scale)))
    return dict(bars=bars,slashes=slashes),errors


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--chars',default='+=±≠');args=ap.parse_args()
    font=TTFont('/System/Library/Fonts/SFNS.ttf');o=subset.Options();o.layout_features=[]
    s=subset.Subsetter(options=o);s.populate(text=args.chars);s.subset(font)
    data={};evidence=[]
    for weight in [100,400,900]:
        for label,optical in [('text',17),('display',28)]:
            f=instantiateVariableFont(font,{'wght':weight,'opsz':optical,'wdth':100,'GRAD':400},inplace=False)
            for ch in args.chars:
                p,errors=profile(f,ch);key=UV2AGL[ord(ch)]
                data.setdefault(key,{}).setdefault(str(weight),{})[label]=p
                evidence.append(dict(character=ch,weight=weight,optical=optical,max_line_error=max(errors)))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(dict(glyphs=data,measurements=evidence),ensure_ascii=False,indent=2)+'\n');print(args.out)


if __name__=='__main__':main()
