"""Measure four band boundaries by fixed scans; export dimensions and line equations."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools import subset
from fontTools.agl import UV2AGL
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from font_recovery.measure import Flatten,scan


def profile(font,ch):
    gs=font.getGlyphSet();p=Flatten(gs);gs[font.getBestCmap()[ord(ch)]].draw(p)
    factor=1000/font['head'].unitsPerEm
    contours=[[(x*factor,y*factor) for x,y in c] for c in p.contours]
    shape=max(contours,key=lambda c:np.ptp(np.array(c)[:,1]));left=min(x for x,y in shape);right=max(x for x,y in shape)
    if ch in '>≥':shape=[(left+right-x,y) for x,y in shape]
    xs=np.linspace(left+.7*(right-left),left+.9*(right-left),13)
    runs=[scan([shape],x,vertical=True,nonzero=True) for x in xs]
    assert all(len(r)==2 for r in runs),(ch,runs)
    values=np.array(runs).reshape(-1,4);edges=[];errors=[]
    for column in values.T:
        a,b=np.polyfit(xs,column,1);edges.append(dict(slope=float(a),intercept=float(b)))
        errors.append(float(np.max(abs(column-(a*xs+b)))))
    assert max(errors)<.01,errors
    bars=[]
    for c in contours:
        if np.ptp(np.array(c)[:,1])==np.ptp(np.array(shape)[:,1]):continue
        a=np.array(c);lo=a.min(axis=0);hi=a.max(axis=0)
        bars.append(dict(left=float(lo[0]),bottom=float(lo[1]),width=float(hi[0]-lo[0]),height=float(hi[1]-lo[1])))
    return dict(span=[left,right],edges=edges,bars=bars),max(errors)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    f=TTFont('/System/Library/Fonts/SFNS.ttf');o=subset.Options();o.layout_features=[];s=subset.Subsetter(options=o);s.populate(text='<>≤≥');s.subset(f)
    data=dict(glyphs={},measurements=[])
    for weight in [100,400,900]:
        for label,optical in [('text',17),('display',28)]:
            font=instantiateVariableFont(f,{'wght':weight,'opsz':optical,'wdth':100,'GRAD':400},inplace=False)
            for ch in '<>≤≥':
                p,error=profile(font,ch);data['glyphs'].setdefault(UV2AGL[ord(ch)],{}).setdefault(str(weight),{})[label]=p
                data['measurements'].append(dict(character=ch,weight=weight,optical=optical,max_line_error=error))
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(data,indent=2)+'\n');print(args.out)


if __name__=='__main__':main()
