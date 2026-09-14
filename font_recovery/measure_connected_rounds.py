"""Measure stems/bars and fit shared oval models for Yu."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.measure_rings import fit_pair


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(glyphs={},measurements=[])
    for ch,key in [('Ю','uni042E'),('ю','uni044E')]:
      for w in [100,400,900]:
       for label,opt in [('text',17),('display',28)]:
        gs=f.getGlyphSet(location={'wght':w,'opsz':opt,'wdth':100,'GRAD':400});flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);assert len(flat.contours)==3
        cs=sorted(flat.contours,key=len);stem_points=cs[0];ring,e=fit_pair(cs[1:],f['head'].unitsPerEm);scale=1000/f['head'].unitsPerEm;stem_points=(np.array(stem_points)*scale).tolist();v=np.array(stem_points);lo=v.min(0);hi=v.max(0);left,right=scan([stem_points],lo[1]+.1*(hi[1]-lo[1]),nonzero=True)[0];middle=(right+ring['bounds'][0][0])/2;bar_bottom,bar_top=scan([stem_points],middle,vertical=True,nonzero=True)[0]
        # End the bar inside the left bowl stroke, preserving a nonzero union.
        normalized_rings=[(np.array(c)*scale).tolist() for c in cs[1:]];stroke=scan(normalized_rings,(bar_bottom+bar_top)/2,nonzero=True)[0];bar_right=sum(stroke)/2
        p=dict(ring=ring,stem=dict(left=left,right=right,bottom=float(lo[1]),top=float(hi[1])),bar=dict(left=left,right=bar_right,bottom=bar_bottom,top=bar_top));data['glyphs'].setdefault(key,{}).setdefault(str(w),{})[label]=p;row=dict(character=ch,weight=w,optical=opt,ring_residuals=e);data['measurements'].append(row);print(row,flush=True)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':main()
