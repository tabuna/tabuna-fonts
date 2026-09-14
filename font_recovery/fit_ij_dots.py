"""Measure i upright and fit shared round i/j dots from section moments."""
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
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();data=json.loads(a.base.read_text());f=TTFont('/System/Library/Fonts/SFNS.ttf');cache={};evidence=[]
 for ch in 'ij':
  for w in [100,400,900]:
   for label,opt in [('text',17),('display',28)]:
    gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);assert len(flat.contours)==2;body,dot=sorted(flat.contours,key=lambda c:min(y for x,y in c));v=np.array(dot);lo=v.min(0);hi=v.max(0);v=(v-lo)/(hi-lo);key=np.round(v,9).tobytes()
    if key not in cache:
     target=shape_features([v.tolist()],[0,0,1,1],count=81,nonzero=True)
     def residual(x):
      q=Flatten(None);contour([0,0,1,1],np.array(x).reshape(4,3)).replay(q);return shape_features(q.contours,[0,0,1,1],count=81,nonzero=True)-target
     fit=least_squares(residual,[.414,.586,.5]*4,bounds=([.05,.05,.1]*4,[.95,.95,.9]*4),max_nfev=100,diff_step=1e-4,ftol=1e-10,xtol=1e-10,gtol=1e-10);cache[key]=(fit.x.reshape(4,3).tolist(),float(np.linalg.norm(fit.fun)))
    quadrants,error=cache[key];p=data['glyphs'].setdefault(ch,{}).setdefault(str(w),{}).setdefault(label,{})
    p['dot']=dict(bounds=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist(),quadrants=quadrants)
    if ch=='i':
     b=np.array(body);p['upright']=(np.r_[b.min(0),b.max(0)]*1000/f['head'].unitsPerEm).tolist()
    evidence.append(dict(character=ch,weight=w,optical=opt,residual=error));data['dot_measurements']=evidence;a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(evidence[-1],flush=True)

if __name__=='__main__':main()
