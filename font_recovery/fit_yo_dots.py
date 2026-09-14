"""Fit paired diaeresis dots from normalized scalar section moments."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from quadratic_round import contour

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();data=dict(glyphs={},measurements=[]);f=TTFont('/System/Library/Fonts/SFNS.ttf');cache={}
 for ch in 'Ёё':
  for w in [100,400,900]:
   for label,opt in [('text',17),('display',28)]:
    gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);dots=sorted(sorted(flat.contours,key=lambda c:min(y for x,y in c),reverse=True)[:2],key=lambda c:min(x for x,y in c));params=[]
    for dot in dots:
     v=np.array(dot);lo=v.min(0);hi=v.max(0);v=(v-lo)/(hi-lo);key=np.round(v,9).tobytes()
     if key not in cache:
      target=shape_features([v.tolist()],[0,0,1,1],count=81,nonzero=True)
      def residual(x):
       q=Flatten(None);contour([0,0,1,1],np.array(x).reshape(4,3)).replay(q);return shape_features(q.contours,[0,0,1,1],count=81,nonzero=True)-target
      fit=least_squares(residual,[.414,.586,.5]*4,bounds=([.05,.05,.1]*4,[.95,.95,.9]*4),max_nfev=100,diff_step=1e-4,ftol=1e-10,xtol=1e-10,gtol=1e-10);cache[key]=(fit.x.reshape(4,3).tolist(),float(np.linalg.norm(fit.fun)))
     quadrants,error=cache[key];params.append(dict(bounds=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist(),quadrants=quadrants));data['measurements'].append(dict(character=ch,weight=w,optical=opt,dot=len(params)-1,residual=error))
    data['glyphs'].setdefault(ch,{}).setdefault(str(w),{})[label]=params;a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(ch,w,opt,flush=True)
if __name__=='__main__':main()
