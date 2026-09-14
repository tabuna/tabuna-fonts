"""Fit the dollar's S separately from its overlapping vertical stem."""
import sys,json,copy,argparse
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from dollar_s import body


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume',action='store_true');a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');seed=json.loads((ROOT/'sources/s-curves.json').read_text())['glyphs']['S'];data=json.loads(a.out.read_text()) if a.resume and a.out.exists() else dict(weights={},measurements=[])
    for w in [100,400,900]:
      for label,opt in [('text',17),('display',28)]:
        profiles=data['weights'].setdefault(str(w),{})
        if label in profiles:continue
        gs=f.getGlyphSet(location={'wght':w,'opsz':opt,'wdth':100,'GRAD':400});flat=Flatten(gs);gs[f.getBestCmap()[36]].draw(flat);assert len(flat.contours)==2;s_points=max(flat.contours,key=len);stem_points=min(flat.contours,key=len);v=np.array(s_points);lo=v.min(0);hi=v.max(0);cs=[((v-lo)/(hi-lo)).tolist()];p=copy.deepcopy(seed[str(w)][label]);p['bounds']=[0,0,1,1];keys=[];vals=[];low=[];high=[]
        fixed=set()
        if w==900:
            previous=a.out.parent/'parameters.json'
            if previous.exists():p=copy.deepcopy(json.loads(previous.read_text())['weights'][str(w)][label]);p['bounds']=[0,0,1,1]
            upper_levels=np.linspace(.6,.9,801);upper_values=[scan(cs,float(y),nonzero=True)[0][1] for y in upper_levels];n=int(np.argmin(upper_values));p['parameters']['upperLeftX']=float(upper_values[n]);p['parameters']['upperLeftY']=float(upper_levels[n])
            lower_levels=np.linspace(.1,.4,801);lower_values=[scan(cs,float(y),nonzero=True)[-1][0] for y in lower_levels];n=int(np.argmax(lower_values));p['parameters']['lowerRightX']=float(lower_values[n]);p['parameters']['lowerRightY']=float(lower_levels[n]);fixed={'upperLeftX','upperLeftY','lowerRightX','lowerRightY'}
        for k,x in p['parameters'].items():
            if k in fixed:continue
            keys.append(('parameters',k));vals.append(x)
            if k.endswith('Slope'):low.append(.001);high.append(3)
            else:low.append(max(-.01,x-.2));high.append(min(1.01,x+.2))
        for i,x in enumerate(p['handles']):keys.append(('handles',i));vals.append(x);low.append(.005);high.append(.995)
        def params(v):
            q=copy.deepcopy(p)
            for (field,k),n in zip(keys,v):q[field][k]=float(n)
            return q
        target=shape_features(cs,[0,0,1,1],count=101,nonzero=True)
        def residual(v):
            flat=Flatten(None);body(params(v)).replay(flat);return shape_features(flat.contours,[0,0,1,1],count=101,nonzero=True)-target
        fit=least_squares(residual,np.clip(vals,np.array(low)+1e-8,np.array(high)-1e-8),bounds=(low,high),max_nfev=120,diff_step=1e-4,ftol=1e-8,xtol=1e-8,gtol=1e-8)
        q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();s=np.array(stem_points)*1000/f['head'].unitsPerEm;sl=s.min(0);sh=s.max(0);q['stem']=dict(left=float(sl[0]),bottom=float(sl[1]),right=float(sh[0]),top=float(sh[1]));profiles[label]=q;row=dict(weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),converged=bool(fit.success));data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
