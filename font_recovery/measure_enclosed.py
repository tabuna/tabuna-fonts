"""Measure enclosing ring and inner-letter dimensions, never source outline nodes."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from font_recovery.measure import Flatten


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    font=TTFont('/System/Library/Fonts/SFNS.ttf');o=subset.Options();o.layout_features=[];s=subset.Subsetter(options=o);s.populate(text='©®');s.subset(font);data=dict(glyphs={})
    for weight in [100,400,900]:
        for label,optical in [('text',17),('display',28)]:
            f=instantiateVariableFont(font,{'wght':weight,'opsz':optical,'wdth':100,'GRAD':400},inplace=False);gs=f.getGlyphSet();factor=1000/f['head'].unitsPerEm
            for ch,key in [('©','copyright'),('®','registered')]:
                name=f.getBestCmap()[ord(ch)];p=Flatten(gs);gs[name].draw(p)
                boxes=[]
                for c in p.contours:
                    a=np.array(c);boxes.append([*a.min(axis=0),*a.max(axis=0)])
                boxes=sorted(boxes,key=lambda b:(b[2]-b[0])*(b[3]-b[1]),reverse=True)
                outer,inner=boxes[:2];letters=np.array(boxes[2:]);letter=[*letters[:,:2].min(axis=0),*letters[:,2:].max(axis=0)]
                profile=dict(outer=[float(v*factor) for v in outer],inner=[float(v*factor) for v in inner],letter=[float(v*factor) for v in letter],advance=float(gs[name].width*factor))
                data['glyphs'].setdefault(key,{}).setdefault(str(weight),{})[label]=profile
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(data,indent=2)+'\n');print(args.out)


if __name__=='__main__':main()
