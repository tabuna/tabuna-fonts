"""Measure ruble stem/bars and fit shared bowl handles to scan moments."""
import sys,json,copy,argparse
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from ruble_bowl import construction


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(weights={},measurements=[])
    for w in [100,400,900]:
      for label,opt in [('text',17),('display',28)]:
        gs=f.getGlyphSet(location={'wght':w,'opsz':opt,'wdth':100,'GRAD':400});flat=Flatten(gs);gs[f.getBestCmap()[0x20BD]].draw(flat);assert len(flat.contours)==3;pts=np.concatenate(flat.contours);lo=pts.min(0);hi=pts.max(0);cs=[((np.array(c)-lo)/(hi-lo)).tolist() for c in flat.contours]
        def box(c):v=np.array(c);return np.r_[v.min(0),v.max(0)]
        body=max(cs,key=lambda c:box(c)[3]-box(c)[1]);others=[c for c in cs if c is not body];bar=min(others,key=len);inner=next(c for c in others if c is not bar);ib=box(inner);bb=box(bar);sl,sr=scan([body],.1,nonzero=True)[0];bt,bh=scan([body],sl/2,vertical=True,nonzero=True)[0];bottom=scan([body],sr+.015,vertical=True,nonzero=True)[0][0]
        def side(l,b,r,t):return dict(right=r,centerY=(b+t)/2,top=t,bottom=b,upper=dict(endX=(l+r)/2,kx=.55,ky=.55),lower=dict(endX=(l+r)/2,kx=.55,ky=.55))
        p=dict(bounds=[0,0,1,1],stemLeft=sl,stemRight=sr,top=1,bottom=0,outer=side(sr,bottom,1,1),inner=side(*ib),bars=[dict(left=0,right=sr,bottom=bt,top=bh),dict(left=float(bb[0]),right=float(bb[2]),bottom=float(bb[1]),top=float(bb[3]))])
        keys=[];vals=[];lower=[];upper=[]
        for role in ['outer','inner']:
            q=p[role];keys.append((role,'centerY'));vals.append(q['centerY']);lower.append(q['centerY']-.06);upper.append(q['centerY']+.06)
            for part in ['upper','lower']:
                for k,v in q[part].items():
                    keys.append((role,part,k));vals.append(v);lower.append(.15 if k!='endX' else sr+.01);upper.append(.95 if k!='endX' else q['right']-.01)
        def params(v):
            q=copy.deepcopy(p)
            for path,n in zip(keys,v):
                field=q
                for k in path[:-1]:field=field[k]
                field[path[-1]]=float(n)
            return q
        target=shape_features(cs,[0,0,1,1],count=101,nonzero=True)
        def residual(v):
            flat=Flatten(None);construction(params(v)).replay(flat);return shape_features(flat.contours,[0,0,1,1],count=101,nonzero=True)-target
        fit=least_squares(residual,vals,bounds=(lower,upper),diff_step=1e-4,max_nfev=120,ftol=1e-9,xtol=1e-9,gtol=1e-9)
        q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();data['weights'].setdefault(str(w),{})[label]=q;row=dict(weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),converged=bool(fit.success));data['measurements'].append(row);print(row,flush=True)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':main()
