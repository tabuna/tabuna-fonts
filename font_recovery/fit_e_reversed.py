"""Fit mirrored open-round models for Э/э from scalar section moments."""
import argparse,json,copy,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from e_reversed import body


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--initial',type=Path);ap.add_argument('--only');a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');seed=json.loads(Path('sources/open-rounds.json').read_text())['glyphs'];initial=json.loads(a.initial.read_text())['glyphs'] if a.initial else None;data=dict(glyphs=copy.deepcopy(initial) if initial else {},measurements=[])
 for ch,base in [('Э','C'),('э','c')]:
  for w in [100,400,900]:
   for label,opt in [('text',17),('display',28)]:
    if a.only and a.only!=f'{ch}:{w}:{label}':continue
    gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));z=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(z);assert len(z.contours)==2;curve=max(z.contours,key=len);bar=min(z.contours,key=len);v=np.array(curve);lo=v.min(0);hi=v.max(0);v=(v-lo)/(hi-lo);v[:,0]=1-v[:,0];p=copy.deepcopy(initial[f'uni{ord(ch):04X}'][str(w)][label] if initial else seed[base][str(w)][label]);p['parameters'].setdefault('upperInnerY',p['parameters']['upperTipY']);p['parameters'].setdefault('lowerInnerY',p['parameters']['lowerTipY']);paths=[];values=[];lower=[];upper=[]
    for k,val in p['parameters'].items():paths.append(('parameters',k));values.append(val);lower.append(max(.001,val-.15));upper.append(min(.999,val+.15))
    for i,val in enumerate(p['handles']):paths.append(('handles',i));values.append(val);lower.append(.01);upper.append(.95)
    def params(values):
     q=copy.deepcopy(p)
     for (role,k),x in zip(paths,values):q[role][k]=float(x)
     return q
    target=shape_features([v.tolist()],[0,0,1,1],count=81,nonzero=True)
    def residual(values):
     pen=Flatten(None);body(params(values)).replay(pen);return shape_features(pen.contours,[0,0,1,1],count=81,nonzero=True)-target
    fit=least_squares(residual,np.clip(values,np.array(lower)+1e-8,np.array(upper)-1e-8),bounds=(lower,upper),diff_step=1e-4,max_nfev=120,ftol=1e-9,xtol=1e-9,gtol=1e-9);q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();bb=np.array(bar)*1000/f['head'].unitsPerEm;bl,bh=bb.min(0),bb.max(0);q['bar']=[float(bl[0]),float(bl[1]),float(bh[0]-bl[0]),float(bh[1]-bl[1])];q.pop('advance',None);key=f'uni{ord(ch):04X}';data['glyphs'].setdefault(key,{}).setdefault(str(w),{})[label]=q;row=dict(character=ch,weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success));data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(row,flush=True)

if __name__=='__main__':main()
