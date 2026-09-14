"""Fit question-hook scalar section moments to a shared tangent model."""
import argparse,json,sys,copy
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from question_hook import construction


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume',action='store_true');a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=json.loads(a.out.read_text()) if a.resume and a.out.exists() else dict(weights={},measurements=[])
    for w in [100,400,900]:
     for label,opt in [('text',17),('display',28)]:
      if label in data['weights'].get(str(w),{}):continue
      gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[63]].draw(flat);assert len(flat.contours)==2;hook=max(flat.contours,key=lambda c:np.ptp(np.array(c)[:,1]));dot=np.array(min(flat.contours,key=lambda c:np.ptp(np.array(c)[:,1])));v=np.array(hook);lo=v.min(0);hi=v.max(0);v=(v-lo)/(hi-lo);cs=[v.tolist()];cut_y=float(v[np.argmin(v[:,0]),1]);cut=scan(cs,cut_y+.005)[0][1];stem=scan(cs,.001)[0];thick=stem[1]-stem[0]
      p=dict(bounds=[0,0,1,1],cut_x=cut,stem=stem)
      for role in ['outer','inner']:
       inside=role=='inner';p[role]=dict(cut_y=cut_y,cut_slope=.08,top_x=.5,top_y=1-thick*.65 if inside else 1,right_x=1-thick if inside else 1,right_y=.65,neck_x=.66-thick*.4 if inside else .66,neck_y=.35,neck_slope=.75,stem_y=.09,handles=[[.38,.38] for _ in range(4)])
      paths=[];values=[];lower=[];upper=[]
      for role in ['outer','inner']:
       for name,val in p[role].items():
        if name=='cut_y' or role=='outer' and name in ['top_y','right_x']:continue
        if name=='handles':
         for i in range(4):
          for j in range(2):paths.append((role,name,i,j));values.append(val[i][j]);lower.append(.06);upper.append(.85)
        else:
         paths.append((role,name));values.append(val)
         if name in ['cut_slope','neck_slope']:lower.append(.001);upper.append(2)
         elif name=='stem_y':lower.append(.015);upper.append(.2)
         else:lower.append(max(.01,val-.17));upper.append(min(.99,val+.17))
      def params(v):
       q=copy.deepcopy(p)
       for path,x in zip(paths,v):
        obj=q
        for k in path[:-1]:obj=obj[k]
        obj[path[-1]]=float(x)
       return q
      target=shape_features(cs,[0,0,1,1],count=81,nonzero=True)
      def residual(v):
       z=Flatten(None);construction(params(v)).replay(z);return shape_features(z.contours,[0,0,1,1],count=81,nonzero=True)-target
      fit=least_squares(residual,values,bounds=(lower,upper),max_nfev=120,diff_step=1e-4,ftol=1e-8,xtol=1e-8,gtol=1e-8);q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();q['dot']=(np.r_[dot.min(0),dot.max(0)]*1000/f['head'].unitsPerEm).tolist();data['weights'].setdefault(str(w),{})[label]=q
      row=dict(weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success));data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
