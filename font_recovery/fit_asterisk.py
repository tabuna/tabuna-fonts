"""Recover scalar parameters of a six-ray construction from scan moments."""
import sys,json,argparse,copy
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from asterisk_rays import polygons


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(weights={},measurements=[])
    for w in [100,400,900]:
        for label,opt in [('text',17),('display',28)]:
            gs=f.getGlyphSet(location={'wght':w,'opsz':opt,'wdth':100,'GRAD':400});flat=Flatten(gs);gs[f.getBestCmap()[42]].draw(flat)
            cs=[(np.array(c)*1000/f['head'].unitsPerEm).tolist() for c in flat.contours];pts=np.concatenate(cs);lo=pts.min(0);hi=pts.max(0);bounds=[*lo,*hi];cx,cy=(lo+hi)/2;rx,ry=(hi-lo)/2
            seed=[cx,cy,.5,ry,rx/np.cos(.5),20,25,20,25]
            def params(v):return dict(x=v[0],y=v[1],angle=v[2],vertical=dict(length=v[3],inner=v[5],outer=v[6]),diagonal=dict(length=v[4],inner=v[7],outer=v[8]))
            target=shape_features(cs,bounds,count=161,nonzero=True)
            def residual(v):return shape_features(polygons(params(v)),bounds,count=161,nonzero=True)-target
            fit=least_squares(residual,seed,bounds=([cx-10,cy-10,.25,ry*.7,rx*.7,1,1,1,1],[cx+10,cy+10,.8,ry*1.2,rx*1.4,180,180,180,180]),max_nfev=200,diff_step=1e-4,ftol=1e-11,xtol=1e-11,gtol=1e-11)
            data['weights'].setdefault(str(w),{})[label]=params(fit.x);row=dict(weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),converged=bool(fit.success));data['measurements'].append(row);print(row,flush=True)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':main()
