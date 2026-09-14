"""Separate outer silhouette and hole measurements before fitting the authored lowercase Be."""
import argparse,copy,importlib.util,json,sys
from pathlib import Path
import numpy as np
import pathops
from scipy.optimize import least_squares
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from font_recovery.measure import Flatten
from font_recovery.fitting import shape_features
ROOT=Path(__file__).resolve().parents[1]


def fit(font,construction,initial):
    gs=font.getGlyphSet();path=pathops.Path();gs[font.getBestCmap()[ord("б")]].draw(path.getPen())
    # Analysis-only nonzero union. The resulting nodes are never exported.
    simple=pathops.simplify(path);flat=Flatten(None);simple.draw(flat)
    points=np.concatenate(flat.contours);lo=points.min(0);hi=points.max(0)
    cs=[((np.array(c)-lo)/(hi-lo)).tolist() for c in flat.contours]
    def area(c):
        a=np.array(c);b=np.roll(a,-1,axis=0);return float(np.sum(a[:,0]*b[:,1]-a[:,1]*b[:,0])/2)
    cs.sort(key=lambda c:abs(area(c)),reverse=True);assert len(cs)==2
    p=copy.deepcopy(initial);p['bounds']=[0,0,1,1];evidence=[]
    for index,roles in [(0,['outer','tail','bowl']),(1,['counter'])]:
        target=shape_features([cs[index]],[0,0,1,1],count=121,nonzero=True)
        keys=[];values=[];low=[];high=[]
        for role in roles:
            for key,v in p[role].items():
                if key=='handles':
                    for i,pair in enumerate(v):
                        for j,n in enumerate(pair):keys.append((role,key,i,j));values.append(n);low.append(.04);high.append(.96)
                else:
                    keys.append((role,key));values.append(v)
                    if 'slope' in key:low.append(.005);high.append(5)
                    else:low.append(max(-.01,v-.18));high.append(min(1.01,v+.18))
        def params(v):
            q=copy.deepcopy(p)
            for path,n in zip(keys,v):
                field=q
                for k in path[:-1]:field=field[k]
                field[path[-1]]=float(n)
            return q
        def residual(v):
            f=Flatten(None);construction(params(v)).replay(f)
            return shape_features([f.contours[index]],[0,0,1,1],count=121,nonzero=True)-target
        fit=least_squares(residual,np.clip(values,np.array(low)+1e-8,np.array(high)-1e-8),bounds=(low,high),max_nfev=120,diff_step=1e-4,x_scale='jac',ftol=1e-9,xtol=1e-9,gtol=1e-9)
        p=params(fit.x);evidence.append(dict(part=index,residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success)))
    p['bounds']=(np.r_[lo,hi]*1000/font['head'].unitsPerEm).tolist();return p,evidence


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--workspace',type=Path,required=True);ap.add_argument('--seed',type=Path,required=True);ap.add_argument('--resume',action='store_true');args=ap.parse_args()
    sys.path.insert(0,str(args.workspace/'scripts'));spec=importlib.util.spec_from_file_location('be_lower',args.workspace/'scripts/be_lower.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    f=TTFont('/System/Library/Fonts/SFNS.ttf');o=subset.Options();o.layout_features=[];s=subset.Subsetter(options=o);s.populate(text='б');s.subset(f)
    out=args.workspace/'sources/be-lower.json';seed=json.loads(args.seed.read_text())['weights'];d=json.loads(out.read_text()) if args.resume and out.exists() else dict(weights={},measurements=[])
    for w in [100,400,900]:
        for label,optical in [('text',17),('display',28)]:
            entries=d['weights'].setdefault(str(w),{})
            if label in entries:continue
            font=instantiateVariableFont(f,{'wght':w,'opsz':optical,'wdth':100,'GRAD':400},inplace=False)
            p,e=fit(font,m.construction,seed[str(w)][label]);entries[label]=p;row=dict(weight=w,optical=optical,parts=e);d['measurements'].append(row);out.write_text(json.dumps(d,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
