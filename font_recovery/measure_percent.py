"""Measure two oval pairs and fit the slash's scalar center-line equation."""
import argparse,json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.measure_rings import fit_pair


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(weights={},measurements=[])
    for weight in [100,400,900]:
        for label,opt in [('text',17),('display',28)]:
            gs=f.getGlyphSet(location={'wght':weight,'opsz':opt,'wdth':100,'GRAD':400});flat=Flatten(gs);gs[f.getBestCmap()[37]].draw(flat);assert len(flat.contours)==5
            def box(c):
                v=np.array(c);return np.r_[v.min(0),v.max(0)]
            cs=sorted(flat.contours,key=lambda c:box(c)[3]-box(c)[1],reverse=True);diagonal=cs[0];ovals=sorted(cs[1:],key=lambda c:(box(c)[1]+box(c)[3])/2);rings=[];errors=[]
            for pair in [ovals[:2],ovals[2:]]:
                p,e=fit_pair(pair,f['head'].unitsPerEm);rings.append(p);errors.append(e)
            scale=1000/f['head'].unitsPerEm;dc=(np.array(diagonal)*scale).tolist();b=box(dc);ys=np.linspace(b[1]+.01,b[3]-.01,51);runs=[scan([dc],y,nonzero=True)[0] for y in ys];centers=np.mean(runs,axis=1);slope,intercept=np.polyfit(ys,centers,1);width=float(np.mean([hi-lo for lo,hi in runs]));slash=dict(slope=float(slope),intercept=float(intercept),width=width,bottom=float(b[1]),top=float(b[3]));data['weights'].setdefault(str(weight),{})[label]=dict(rings=rings,slash=slash);row=dict(weight=weight,optical=opt,ring_residuals=errors,slash_center_residual=float(np.max(abs(centers-(slope*ys+intercept)))));data['measurements'].append(row);print(row,flush=True)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':main()
