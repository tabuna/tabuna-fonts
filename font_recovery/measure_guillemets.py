"""Measure each chevron's four edge equations; no source vertices exported."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.agl import UV2AGL
from font_recovery.measure import Flatten,scan


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    font=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(glyphs={},measurements=[])
    for w in [100,400,900]:
      for label,opt in [('text',17),('display',28)]:
        gs=font.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400))
        for ch in '«»':
            flat=Flatten(gs);gs[font.getBestCmap()[ord(ch)]].draw(flat)
            assert len(flat.contours)==2
            parts=[];errors=[]
            for contour in flat.contours:
                c=np.array(contour)*1000/font['head'].unitsPerEm;left=float(c[:,0].min());right=float(c[:,0].max())
                if ch=='»':c[:,0]=left+right-c[:,0]
                shape=c.tolist();edges=[]
                for edge_index in range(4):
                    outer=edge_index in (0,3)
                    xs=np.linspace(left+(.15 if outer else .70)*(right-left),left+(.35 if outer else .90)*(right-left),51)
                    runs=[scan([shape],x,vertical=True,nonzero=True) for x in xs]
                    if not outer:assert all(len(r)==2 for r in runs)
                    column=np.array([r[0][0] if edge_index==0 else r[-1][1] if edge_index==3 else r[0][1] if edge_index==1 else r[-1][0] for r in runs])
                    a,b=np.polyfit(xs,column,1);edges.append(dict(slope=float(a),intercept=float(b)));errors.append(float(max(abs(column-(a*xs+b)))))
                parts.append(dict(span=[left,right],edges=edges,bars=[],vertical_clip=[float(c[:,1].min()),float(c[:,1].max())]))
            parts.sort(key=lambda p:p['span'][0]);data['glyphs'].setdefault(UV2AGL[ord(ch)],{}).setdefault(str(w),{})[label]=dict(parts=parts)
            data['measurements'].append(dict(character=ch,weight=w,optical=opt,max_line_error=max(errors)))
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data['measurements']))


if __name__=='__main__':main()
