"""Fit two independent ribbon models to scalar section moments of ampersand."""
import sys,json,copy,argparse
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from ampersand_ribbons import upper,lower


def seed(w):
    t={100:.045,400:.10,900:.20}[w];h=lambda:[[.4,.4] for _ in range(4)]
    return dict(bounds=[0,0,1,1],upper=dict(base=.015,outer=dict(tail_x=1-t*1.7,join_x=.315,join_y=.545,left_x=.13,left_y=.80,top_x=.407,right_x=.678,right_y=.805,cut_x=.38,cut_y=.535,cut_slope=.5,handles=h()),inner=dict(join_x=.315+t,join_y=.545+t*.6,left_x=.13+t,left_y=.80,top_x=.407,top_y=1-t,right_x=.678-t,right_y=.805,cut_x=.38-t,cut_y=.535+t*.65,cut_slope=.5,handles=h())),lower=dict(cap=.553,outer=dict(bottom_x=.366,left_y=.26,join_x=.226,join_y=.516,cut_x=.322,cut_y=.558,right_x=.921,right_y=.505,shoulder_x=.786,shoulder_y=.166,shoulder_slope=1.2,handles=h()),inner=dict(left_x=t,left_y=.26,bottom_x=.37,bottom_y=t,join_x=.258,join_y=.48,cut_x=.36,cut_y=.525,right_x=.921-t,right_y=.505,shoulder_x=.786-t,shoulder_y=.166+t,shoulder_slope=1.2,handles=h())))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume',action='store_true');a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=json.loads(a.out.read_text()) if a.resume and a.out.exists() else dict(weights={},measurements=[])
    for w in [100,400,900]:
      for label,opt in [('text',17),('display',28)]:
        profiles=data['weights'].setdefault(str(w),{})
        if label in profiles:continue
        gs=f.getGlyphSet(location={'wght':w,'opsz':opt,'wdth':100,'GRAD':400});flat=Flatten(gs);gs[f.getBestCmap()[38]].draw(flat);assert len(flat.contours)==2;pts=np.concatenate(flat.contours);lo=pts.min(0);hi=pts.max(0);cs=sorted([((np.array(c)-lo)/(hi-lo)).tolist() for c in flat.contours],key=lambda c:max(y for x,y in c),reverse=True);p=seed(w);e=[]
        p['upper']['base']=float(min(y for x,y in cs[0]))
        ys=np.linspace(p['upper']['base']+.025,p['upper']['base']+.12,51);sections=np.array([scan([cs[0]],float(y),nonzero=True)[0] for y in ys])
        for j,key in enumerate(['diagonal_outer','diagonal_inner']):p['upper'][key]=np.polyfit(ys,sections[:,j],1).tolist()
        xmax=max(x for x,y in cs[1]);p['lower']['cap']=scan([cs[1]],xmax-1e-5,vertical=True,nonzero=True)[-1][1]
        for side in ['outer','inner']:
            p['upper'][side].pop('join_x',None);p['upper'][side].pop('tail_x',None)
        for role,fn,c in [('upper',upper,cs[0]),('lower',lower,cs[1])]:
            q=p[role];keys=[];vals=[];lows=[];highs=[]
            for side in ['outer','inner']:
              for k,v in q[side].items():
                if k=='handles':
                    for j,pair in enumerate(v):
                        for n,x in enumerate(pair):keys.append((side,k,j,n));vals.append(x);lows.append(.04);highs.append(.95)
                else:
                    keys.append((side,k));vals.append(v)
                    if k.endswith('slope'):lows.append(.01);highs.append(3)
                    else:lows.append(max(-.005,v-.13));highs.append(min(1.005,v+.13))
            def params(v):
                result=copy.deepcopy(q)
                for path,x in zip(keys,v):
                    field=result
                    for k in path[:-1]:field=field[k]
                    field[path[-1]]=float(x)
                return result
            target=shape_features([c],[0,0,1,1],count=81,nonzero=True)
            def residual(v):
                flat=Flatten(None);fn(params(v)).replay(flat);return shape_features(flat.contours,[0,0,1,1],count=81,nonzero=True)-target
            fit=least_squares(residual,vals,bounds=(lows,highs),max_nfev=120,diff_step=1e-4,ftol=1e-8,xtol=1e-8,gtol=1e-8);p[role]=params(fit.x);e.append(dict(part=role,residual=float(np.linalg.norm(fit.fun)),converged=bool(fit.success)))
        p['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();profiles[label]=p;row=dict(weight=w,optical=opt,parts=e);data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
