"""Fit tangent shoulder parameters from scalar silhouette section moments."""
import argparse,json,copy,sys,math
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from r_shoulder import construction,edge
from bezier import point,derivatives

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--initial',type=Path);ap.add_argument('--only');args=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=json.loads(args.initial.read_text()) if args.initial else dict(weights={},measurements=[])
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   if args.only and args.only!=f'{w}:{label}':continue
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[ord('r')]].draw(flat);v=np.concatenate(flat.contours);lo=v.min(0);hi=v.max(0);cs=[((np.array(c)-lo)/(hi-lo)).tolist() for c in flat.contours];stem=scan(cs,.1,nonzero=True)[0];stem_top=scan(cs,1e-6,vertical=True,nonzero=True)[0][1];tip=scan(cs,1-1e-6,vertical=True,nonzero=True)[0]
   p=dict(stem_right=stem[1],stem_top=stem_top,bounds=[0,0,1,1],outer=dict(join_y=.72,crown_x=.8,crown_y=1,tip_y=tip[1],join_angle=1.2,tip_angle=-.1,handles=[[.4,.4],[.4,.4]]),inner=dict(join_y=.5,crown_x=.8,crown_y=tip[0]+.01,tip_y=tip[0],join_angle=math.pi/2,tip_angle=-.1,handles=[[.4,.4],[.4,.4]]))
   if args.initial:
    initial=copy.deepcopy(data['weights'][str(w)]['display' if args.only else label])
    for role in ['outer','inner']:
     tip_y=p[role]['tip_y'];p[role]=initial[role];p[role]['tip_y']=tip_y
   p['outer']['crown_x']=float(np.mean(scan(cs,1-1e-7,nonzero=True)[0]))
   for role in ['outer','inner']:
    q=p[role]
    if 'mid_x' not in q:
     pts,arcs=edge(p,q);curve=[pts[0],*arcs[0]];mid=point(curve,.5);vel,_=derivatives(curve,.5)
     q.update(mid_x=mid[0],mid_y=mid[1],mid_angle=math.atan2(vel[1],vel[0]));q['handles']=[[.35,.35],[.35,.35],q['handles'][1]]
   paths=[];values=[];lower=[];upper=[]
   for role in ['outer','inner']:
    for k,v in p[role].items():
     if k=='tip_y' or role=='outer' and k in ['crown_y','crown_x'] or role=='inner' and k=='join_angle':continue
     if k=='handles':
      for i in range(len(v)):
       for j in range(2):paths.append((role,k,i,j));values.append(v[i][j]);lower.append(.02);upper.append(.95)
     else:
      limits={'join_y':(.05,stem_top-.001),'crown_x':(max(stem[1]+.02,.4),.98),'crown_y':(tip[0],min(.999,tip[0]+.15)),'join_angle':(.05,1.55),'tip_angle':(-1.2,0),'mid_x':(max(stem[1]+.01,v-.1),min(.95,v+.1)),'mid_y':(max(.1,v-.1),min(.99,v+.1)),'mid_angle':(.05,1.55)};a,b=limits[k];paths.append((role,k));values.append(max(a+1e-5,min(b-1e-5,v)));lower.append(a);upper.append(b)
   def params(values):
    q=copy.deepcopy(p)
    for path,x in zip(paths,values):
     obj=q
     for k in path[:-1]:obj=obj[k]
     obj[path[-1]]=float(x)
    return q
   target=shape_features(cs,[0,0,1,1],count=121,nonzero=True)
   def residual(values):
    z=Flatten(None);construction(params(values)).replay(z);return shape_features(z.contours,[0,0,1,1],count=121,nonzero=True)-target
   fit=least_squares(residual,values,bounds=(lower,upper),max_nfev=220,diff_step=1e-4,ftol=1e-8,xtol=1e-8,gtol=1e-8);q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();data['weights'].setdefault(str(w),{})[label]=q;row=dict(weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success));data['measurements'].append(row);args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)
if __name__=='__main__':main()
