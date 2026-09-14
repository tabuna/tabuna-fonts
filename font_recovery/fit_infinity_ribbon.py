"""Fit infinity silhouette and counters separately from section moments."""
import argparse,json,copy,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from infinity_ribbon import construction


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(weights={},measurements=[])
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));z=Flatten(gs);gs[f.getBestCmap()[0x221e]].draw(z);assert len(z.contours)==3;v=np.concatenate(z.contours);lo=v.min(0);hi=v.max(0);cs=[(np.array(c)-lo)/(hi-lo) for c in z.contours];outer=cs[0];holes=sorted(cs[1:],key=lambda v:v[:,0].min());cs=[outer,*holes];waist=scan([outer.tolist()],.5,vertical=True,nonzero=True)[0]
   def profile(v):
    low,high=v.min(0),v.max(0)
    def at(axis,value,other):return float(np.mean(v[np.abs(v[:,axis]-value)<1e-6,other]))
    return dict(left=float(low[0]),axis=at(0,low[0],1),top=float(high[1]),bottom=float(low[1]),top_x=at(1,high[1],0),bottom_x=at(1,low[1],0),upper_slope=1.5,lower_slope=1.5,handles=[[.35,.35] for _ in range(4)])
   left=outer[outer[:,0]<=.5];right=outer[outer[:,0]>=.5].copy();right[:,0]=1-right[:,0];rh=holes[1].copy();rh[:,0]=1-rh[:,0];p=dict(bounds=[0,0,1,1],upper=[.5,float(waist[1])],lower=[.5,float(waist[0])],left=profile(left),right=profile(right),counters={})
   for name,v in [('left',holes[0]),('right',rh)]:
    q=profile(v);tip=v[:,0].max();q['tip_x']=float(tip);q['tip_y']=float(np.mean(v[np.abs(v[:,0]-tip)<1e-6,1]));p['counters'][name]=q
   results=[]
   for index,roles in [(0,[('left',),('right',)]),(1,[('counters','left')]),(2,[('counters','right')])]:
    paths=[];values=[];lower=[];upper=[]
    for role in roles:
     q=p
     for k in role:q=q[k]
     for k,value in q.items():
      if k in ['left','top','bottom','tip_x','tip_y']:continue
      if k=='handles':
       for i in range(4):
        for j in range(2):paths.append((*role,k,i,j));values.append(value[i][j]);lower.append(.03);upper.append(.9)
      else:
       paths.append((*role,k));values.append(value);lower.append(.05 if 'slope' in k else max(.001,value-.1));upper.append(8 if 'slope' in k else min(.999,value+.1))
    if index==0:
     for k in ['upper','lower']:
      paths.append((k,1));values.append(p[k][1]);lower.append(p[k][1]-.08);upper.append(p[k][1]+.08)
    def params(values):
     q=copy.deepcopy(p)
     for path,x in zip(paths,values):
      obj=q
      for k in path[:-1]:obj=obj[k]
      obj[path[-1]]=float(x)
     return q
    target=shape_features([cs[index].tolist()],[0,0,1,1],count=91,nonzero=True)
    def residual(values):
     pen=Flatten(None);construction(params(values)).replay(pen);return shape_features([pen.contours[index]],[0,0,1,1],count=91,nonzero=True)-target
    fit=least_squares(residual,values,bounds=(lower,upper),diff_step=1e-4,max_nfev=120,ftol=1e-9,xtol=1e-9,gtol=1e-9);p=params(fit.x);results.append(dict(part=index,residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success)))
   p['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();data['weights'].setdefault(str(w),{})[label]=p;row=dict(weight=w,optical=opt,parts=results);data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)

if __name__=='__main__':main()
