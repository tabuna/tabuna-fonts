"""Fit a shared cubic wave ribbon to section moments, not source nodes."""
import argparse,json,copy,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tilde_wave import construction


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(weights={},measurements=[])
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[126]].draw(flat);assert len(flat.contours)==1;v=np.array(flat.contours[0]);lo=v.min(0);hi=v.max(0);v=(v-lo)/(hi-lo);cs=[v.tolist()];start=scan(cs,1e-7,vertical=True,nonzero=True)[0];end=scan(cs,1-1e-7,vertical=True,nonzero=True)[0];xs=np.linspace(.001,.999,401);ys=np.array([scan(cs,x,vertical=True,nonzero=True)[0] for x in xs]);p=dict(bounds=[0,0,1,1])
   for j,role in enumerate(['lower','upper']):
    peak=int(ys[:,j].argmax());trough=int(ys[:,j].argmin());p[role]=dict(start=start[j],end=end[j],peak_x=float(xs[peak]),peak_y=1 if role=='upper' else float(ys[peak,j]),trough_x=float(xs[trough]),trough_y=0 if role=='lower' else float(ys[trough,j]),start_slope=4,end_slope=4,handles=[[.35,.35] for _ in range(3)])
   paths=[];values=[];lower=[];upper=[]
   for role in ['upper','lower']:
    for k,vv in p[role].items():
     if k in ['start','end'] or role=='upper' and k=='peak_y' or role=='lower' and k=='trough_y':continue
     if k=='handles':
      for i in range(3):
       for j in range(2):paths.append((role,k,i,j));values.append(vv[i][j]);lower.append(.02);upper.append(.95)
     else:
      paths.append((role,k));values.append(vv)
      if k.endswith('slope'):lower.append(.1);upper.append(12)
      elif k=='peak_x':lower.append(.05);upper.append(.45)
      elif k=='trough_x':lower.append(.55);upper.append(.95)
      else:lower.append(max(.001,vv-.15));upper.append(min(.999,vv+.15))
   def params(values):
    q=copy.deepcopy(p)
    for path,x in zip(paths,values):
     obj=q
     for k in path[:-1]:obj=obj[k]
     obj[path[-1]]=float(x)
    return q
   target=shape_features(cs,[0,0,1,1],count=81,nonzero=True)
   def residual(values):
    z=Flatten(None);construction(params(values)).replay(z);return shape_features(z.contours,[0,0,1,1],count=81,nonzero=True)-target
   fit=least_squares(residual,values,bounds=(lower,upper),max_nfev=150,diff_step=1e-4,ftol=1e-9,xtol=1e-9,gtol=1e-9);q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();data['weights'].setdefault(str(w),{})[label]=q;row=dict(weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success));data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)

if __name__=='__main__':main()
