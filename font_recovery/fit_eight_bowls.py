"""Fit eight's rotated tangent silhouette and oval counters separately."""
import argparse,json,copy,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from eight_bowls import construction


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seed',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();data=json.loads(a.seed.read_text());f=TTFont('/System/Library/Fonts/SFNS.ttf');evidence=[]
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));z=Flatten(gs);gs[f.getBestCmap()[56]].draw(z);v=np.concatenate(z.contours);lo=v.min(0);hi=v.max(0);cs=[]
   for co in z.contours:
    v=(np.array(co)-lo)/(hi-lo);cs.append(np.column_stack([v[:,1],1-v[:,0]]).tolist())
   cs=[cs[0],*sorted(cs[1:],key=lambda c:min(x for x,y in c))];p=copy.deepcopy(data['weights'][str(w)][label]);results=[]
   for index in [0,1,2]:
    paths=[];values=[];lower=[];upper=[]
    if index==0:
     for role in ['left','right']:
      for k,val in p[role].items():
       if k in ['left','top','bottom']:continue
       if k=='handles':
        for i in range(4):
         for j in range(2):paths.append((role,k,i,j));values.append(val[i][j]);lower.append(.02);upper.append(.9)
       else:paths.append((role,k));values.append(val);lower.append(.001 if 'slope' in k else max(.001,val-.12));upper.append(8 if 'slope' in k else min(.999,val+.12))
     for role in ['upper','lower']:
      for i in [0,1]:paths.append((role,i));values.append(p[role][i]);lower.append(p[role][i]-.08);upper.append(p[role][i]+.08)
    else:
     for i in range(4):
      for j in range(2):paths.append(('counters',index-1,'handles',i,j));values.append(.5522847498);lower.append(.15);upper.append(.9)
    def params(values):
     q=copy.deepcopy(p)
     for path,x in zip(paths,values):
      obj=q
      for k in path[:-1]:obj=obj[k]
      obj[path[-1]]=float(x)
     return q
    target=shape_features([cs[index]],[0,0,1,1],count=91,nonzero=True)
    def residual(values):
     pen=Flatten(None);construction(params(values)).replay(pen);return shape_features([pen.contours[index]],[0,0,1,1],count=91,nonzero=True)-target
    fit=least_squares(residual,values,bounds=(lower,upper),diff_step=1e-4,max_nfev=120,ftol=1e-9,xtol=1e-9,gtol=1e-9);p=params(fit.x);results.append(dict(part=index,residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success)))
   data['weights'][str(w)][label]=p;row=dict(weight=w,optical=opt,parts=results);evidence.append(row);data['fits']=evidence;a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)

if __name__=='__main__':main()
