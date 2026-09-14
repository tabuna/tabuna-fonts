"""Fit an authored sterling ribbon; measure foot and crossbar separately."""
import sys,json,copy,argparse
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from sterling_ribbon import construction


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume',action='store_true');a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=json.loads(a.out.read_text()) if a.resume and a.out.exists() else dict(weights={},measurements=[])
    for w in [100,400,900]:
      for label,opt in [('text',17),('display',28)]:
        profiles=data['weights'].setdefault(str(w),{})
        if label in profiles:continue
        gs=f.getGlyphSet(location={'wght':w,'opsz':opt,'wdth':100,'GRAD':400});flat=Flatten(gs);gs[f.getBestCmap()[163]].draw(flat);assert len(flat.contours)==2
        pts=np.array(max(flat.contours,key=len));lo=pts.min(0);hi=pts.max(0);cs=[((np.array(c)-lo)/(hi-lo)).tolist() for c in flat.contours];bar=min(cs,key=len);v=np.array(bar);bl=v.min(0);bh=v.max(0);base=scan(cs,.99,vertical=True,nonzero=True)[0][1];th={100:.07,400:.16,900:.31}[w]
        p=dict(bounds=[0,0,1,1],base=base,bar=dict(left=float(bl[0]),bottom=float(bl[1]),right=float(bh[0]),top=float(bh[1])),outer=dict(foot_y=.05,foot_slope=.3,bulge_x=.3,bulge_y=.3,neck_x=.19,neck_y=.71,top_x=.65,tip_x=.93,tip_y=.95,tip_slope=.5,handles=[[.4,.4] for _ in range(4)]),inner=dict(foot_x=.14,foot_y=base+.01,foot_slope=.3,bulge_x=.3+th,bulge_y=.3,neck_x=.19+th,neck_y=.71,top_x=.65,top=1-th*.7,tip_y=.95-th*.7,tip_slope=.5,handles=[[.4,.4] for _ in range(4)]))
        if w==900 and label=='display' and 'text' in profiles:
            p=copy.deepcopy(profiles['text']);p['bounds']=[0,0,1,1];p['base']=base;p['bar']=dict(left=float(bl[0]),bottom=float(bl[1]),right=float(bh[0]),top=float(bh[1]))
        levels=np.linspace(base+.02,bl[1]-.005,501)
        runs=[scan(cs,y,nonzero=True)[0] for y in levels]
        for role,index in [('outer',0),('inner',1)]:
            n=int(np.argmax([r[index] for r in runs]));p[role]['bulge_x']=runs[n][index];p[role]['bulge_y']=float(levels[n])
        p['outer']['foot_y']=scan(cs,.001,vertical=True,nonzero=True)[0][1]
        p['inner']['foot_x']=scan(cs,base+.01,nonzero=True)[0][1]
        p['inner']['foot_y']=base+.005
        keys=[];vals=[];low=[];high=[]
        for role in ['outer','inner']:
            for k,v in p[role].items():
                if role=='outer' and k=='foot_y':continue
                if k=='handles':
                    for j,pair in enumerate(v):
                        for n,x in enumerate(pair):keys.append((role,k,j,n));vals.append(x);low.append(.05);high.append(.95)
                else:
                    keys.append((role,k));vals.append(v)
                    if k=='bulge_y':low.append(max(base+.01,v-.025));high.append(v+.025)
                    elif role=='inner' and k=='foot_y':low.append(base+.0001);high.append(base+.025)
                    elif 'slope' in k:low.append(.001);high.append(2)
                    else:low.append(max(.001,v-.16));high.append(min(.999,v+.16))
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
        fit=least_squares(residual,np.clip(vals,np.array(low)+1e-8,np.array(high)-1e-8),bounds=(low,high),diff_step=1e-4,max_nfev=120,ftol=1e-8,xtol=1e-8,gtol=1e-8)
        q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();profiles[label]=q;row=dict(weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),converged=bool(fit.success));data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
