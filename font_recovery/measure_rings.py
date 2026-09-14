"""Fit shared cubic round contours using scalar scanline moments."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from font_recovery.measure import Flatten
from font_recovery.fitting import shape_features
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from rounds import contour


def profile(font,ch):
    gs=font.getGlyphSet();f=Flatten(gs);gs[font.getBestCmap()[ord(ch)]].draw(f);assert len(f.contours)==2
    return fit_pair(f.contours,font['head'].unitsPerEm)


def fit_pair(contours,units_per_em):
    def box(c):
        a=np.array(c);return np.r_[a.min(0),a.max(0)]
    cs=sorted(contours,key=lambda c:np.prod(box(c)[2:]-box(c)[:2]),reverse=True)
    params={'bounds':[]};errors=[]
    for field,points in zip(['outerHandles','innerHandles'],cs):
        bounds=box(points);lo=bounds[:2];span=bounds[2:]-lo;normalized=((np.array(points)-lo)/span).tolist()
        target=shape_features([normalized],[0,0,1,1],count=101,nonzero=True)
        def residual(v):
            q=Flatten(None);contour([0,0,1,1],np.array(v).reshape(4,2).tolist()).replay(q)
            return shape_features(q.contours,[0,0,1,1],count=101,nonzero=True)-target
        fit=least_squares(residual,[.55]*8,bounds=([.15]*8,[.95]*8),diff_step=1e-4,max_nfev=80,x_scale='jac')
        params[field]=fit.x.reshape(4,2).tolist();params['bounds'].append((bounds*1000/units_per_em).tolist());errors.append(float(np.linalg.norm(fit.fun)))
    return params,errors


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    f=TTFont('/System/Library/Fonts/SFNS.ttf');o=subset.Options();o.layout_features=[];s=subset.Subsetter(options=o);s.populate(text='0°');s.subset(f);data=dict(glyphs={},measurements=[])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    for w in [100,400,900]:
        for label,optical in [('text',17),('display',28)]:
            font=instantiateVariableFont(f,{'wght':w,'opsz':optical,'wdth':100,'GRAD':400},inplace=False)
            for ch,key in [('0','zero'),('°','degree')]:
                p,e=profile(font,ch);data['glyphs'].setdefault(key,{}).setdefault(str(w),{})[label]=p;row=dict(character=ch,weight=w,optical=optical,residuals=e);data['measurements'].append(row);args.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
