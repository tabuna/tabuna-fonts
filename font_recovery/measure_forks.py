"""Fit straight branch equations to section endpoints, without exporting vertices."""
import json,argparse
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(glyphs={},measurements=[])
    for ch,key,bar_count in [('Y','Y',0),('¥','yen',2)]:
        for w in [100,400,900]:
          for label,opt in [('text',17),('display',28)]:
            gs=f.getGlyphSet(location={'wght':w,'opsz':opt,'wdth':100,'GRAD':400});flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);cs=[(np.array(c)*1000/f['head'].unitsPerEm).tolist() for c in flat.contours];cs.sort(key=lambda c:np.ptp(np.array(c)[:,1]),reverse=True);body=cs[0];v=np.array(body);bottom,top=v[:,1].min(),v[:,1].max();height=top-bottom;stem=scan([body],bottom+.1*height,nonzero=True)[0];center=sum(stem)/2;floor=scan([body],center,vertical=True,nonzero=True)[0][1]
            ys=np.linspace(bottom+.8*height,bottom+.98*height,51);runs=[scan([body],y,nonzero=True) for y in ys];assert all(len(r)==2 for r in runs);edges=np.array(runs).reshape(-1,4);p=dict(stem=stem,top=float(top),bottom=float(bottom),floor=float(floor),bars=[]);errors=[]
            for i,edge_key in enumerate(['left_outer','left_inner','right_inner','right_outer']):
                slope,intercept=np.polyfit(ys,edges[:,i],1);p[edge_key]=[float(slope),float(intercept)];errors.append(float(max(abs(edges[:,i]-(slope*ys+intercept)))))
            for c in cs[1:]:
                v=np.array(c);lo=v.min(0);hi=v.max(0);p['bars'].append(dict(left=float(lo[0]),bottom=float(lo[1]),right=float(hi[0]),top=float(hi[1])))
            p['bars'].sort(key=lambda b:b['bottom']);assert len(p['bars'])==bar_count;data['glyphs'].setdefault(key,{}).setdefault(str(w),{})[label]=p;row=dict(character=ch,weight=w,optical=opt,line_residuals=errors);data['measurements'].append(row);print(row,flush=True)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':main()
