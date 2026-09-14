"""Fit own shared open bowl and crossbars to scalar scan moments."""
import argparse,copy,json,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from euro_bowl import construction


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume',action='store_true');a=ap.parse_args()
    seed=json.loads((ROOT/'sources/open-rounds.json').read_text())['glyphs']['C'];f=TTFont('/System/Library/Fonts/SFNS.ttf');data=json.loads(a.out.read_text()) if a.resume and a.out.exists() else dict(weights={},measurements=[])
    for w in [100,400,900]:
        for label,opt in [('text',17),('display',28)]:
            if label in data['weights'].get(str(w),{}):continue
            gs=f.getGlyphSet(location={'wght':w,'opsz':opt,'wdth':100,'GRAD':400});flat=Flatten(gs);gs[f.getBestCmap()[0x20AC]].draw(flat)
            pts=np.concatenate(flat.contours);lo=pts.min(0);hi=pts.max(0);cs=[((np.array(c)-lo)/(hi-lo)).tolist() for c in flat.contours]
            p=copy.deepcopy(seed[str(w)][label]);p.pop('advance');p['bounds']=[0,0,1,1];p['left']=.22;p['parameters'].update(outerTopX=.85,outerBottomX=.85,upperTipY=.99,lowerTipY=.01,upperOuterX=1,lowerOuterX=1,upperInnerX=1,lowerInnerX=1,upperInnerY=.95,lowerInnerY=.05); p['bars']=[dict(y=y,height={100:.025,400:.07,900:.13}[w],right=.75,slant=.25) for y in [.40,.59]]
            if w==100:
                regular_path=a.out.parent/'parameters-v3.json'
                if regular_path.exists():
                    previous=json.loads(regular_path.read_text())
                    if label in previous['weights'].get('400',{}):
                        p=copy.deepcopy(previous['weights']['400'][label]);p['bounds']=[0,0,1,1]
                        span=scan(cs,.5,nonzero=True)[0]
                        p['left']=span[0]
                        p['parameters']['innerLeftX']=(span[1]-span[0])/(1-span[0])
                        vertical=scan(cs,.8,vertical=True,nonzero=True)
                        p['parameters']['innerBottomY']=vertical[0][1]
                        p['parameters']['innerTopY']=vertical[-1][0]
                        p['parameters']['lowerInnerY']=vertical[0][1]
                        p['parameters']['upperInnerY']=vertical[-1][0]
            keys=[];vals=[];low=[];high=[]
            def add(path,v,l,h):keys.append(path);vals.append(v);low.append(l);high.append(h)
            for k,v in p['parameters'].items():add(('parameters',k),v,.001,1.05)
            for i,v in enumerate(p['handles']):add(('handles',i),v,.015,.98)
            add(('left',),p['left'],.01,.3)
            spans=scan(cs,.001,vertical=True,nonzero=True)
            assert len(spans)==2,spans
            p['bars']=[dict(y=(a+b)/2,height=b-a,right=scan(cs,(a+b)/2,nonzero=True)[0][1],slant=0) for a,b in spans]
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
            fit=least_squares(residual,np.clip(vals,np.array(low)+1e-8,np.array(high)-1e-8),bounds=(low,high),max_nfev=100,diff_step=1e-3,x_scale=1,ftol=1e-8,xtol=1e-8,gtol=1e-8)
            q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();data['weights'].setdefault(str(w),{})[label]=q;row=dict(weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),converged=bool(fit.success));data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
