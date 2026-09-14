"""Measure the small R inside registered; fit the shared bowl to scalar sections."""
import argparse,json,copy,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from r_bowl import construction


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(weights={},measurements=[])
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[174]].draw(flat);flat.contours=sorted(flat.contours,key=lambda c:float(np.prod(np.ptp(np.array(c),axis=0))),reverse=True)[2:];assert len(flat.contours)==2;v=np.concatenate(flat.contours);lo=v.min(0);hi=v.max(0);cs=[((np.array(c)-lo)/(hi-lo)).tolist() for c in flat.contours]
   def box(c):v=np.array(c);return np.r_[v.min(0),v.max(0)]
   body=max(cs,key=lambda c:box(c)[3]-box(c)[1]);inner=next(c for c in cs if c is not body);ib=box(inner);stem=scan(cs,.05,nonzero=True)[0];bottom=scan([body],stem[1]+.01,vertical=True,nonzero=True)[0][0];right=max(x for x,y in body if y>(bottom+1)/2)
   def side(l,b,r,t):return dict(right=r,centerY=(b+t)/2,top=t,bottom=b,upper=dict(endX=(l+r)/2,kx=.55,ky=.55),lower=dict(endX=(l+r)/2,kx=.55,ky=.55))
   ys=np.linspace(.02,.2,41);runs=[scan(cs,y,nonzero=True) for y in ys];assert all(len(r)==2 for r in runs);edges=np.array(runs)[:,1,:];sl,inter=np.polyfit(ys,edges.mean(1),1);ws,wi=np.polyfit(ys,np.diff(edges,axis=1)[:,0],1);leg=dict(slope=float(sl),intercept=float(inter),width=float(wi),width_slope=float(ws),bottom=0,top=float(bottom+(ib[1]-bottom)*.8));err=float(np.max(abs(edges.mean(1)-(sl*ys+inter))))
   p=dict(bounds=[0,0,1,1],stemLeft=stem[0],stemRight=stem[1],top=1,bottom=0,outer=side(stem[1],bottom,right,1),inner=side(*ib),leg=leg);paths=[];values=[];lower=[];upper=[]
   for role in ['outer','inner']:
    q=p[role];paths.append((role,'centerY'));values.append(q['centerY']);lower.append(q['centerY']-.08);upper.append(q['centerY']+.08)
    for part in ['upper','lower']:
     for k,v in q[part].items():
      paths.append((role,part,k));values.append(v);lower.append(.15 if k!='endX' else stem[1]+.001);upper.append(.95 if k!='endX' else q['right']-.001)
   paths.append(('leg','top'));values.append(leg['top']);lower.append(bottom);upper.append(float(ib[1]))
   def params(values):
    q=copy.deepcopy(p)
    for path,x in zip(paths,values):
     obj=q
     for k in path[:-1]:obj=obj[k]
     obj[path[-1]]=float(x)
    return q
   target=shape_features(cs,[0,0,1,1],count=101,nonzero=True)
   def residual(values):
    z=Flatten(None);construction(params(values)).replay(z);return shape_features(z.contours,[0,0,1,1],count=101,nonzero=True)-target
   fit=least_squares(residual,values,bounds=(lower,upper),diff_step=1e-4,max_nfev=120,ftol=1e-9,xtol=1e-9,gtol=1e-9);q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();data['weights'].setdefault(str(w),{})[label]=q;row=dict(weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),leg_line_residual=err,evaluations=fit.nfev,converged=bool(fit.success));data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)

if __name__=='__main__':main()
