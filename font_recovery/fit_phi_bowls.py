"""Fit Phi's shared oval contours to scalar section moments."""
import argparse,json,copy,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from phi_bowls import construction


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seed',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();data=json.loads(a.seed.read_text());f=TTFont('/System/Library/Fonts/SFNS.ttf');evidence=[]
 for ch in 'Фф':
  key=f'uni{ord(ch):04X}'
  for w in [100,400,900]:
   for label,opt in [('text',17),('display',28)]:
    gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));z=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(z);cs=[(np.array(c)*1000/f['head'].unitsPerEm).tolist() for c in z.contours];v=np.concatenate(cs);lo=v.min(0);hi=v.max(0);bounds=np.r_[lo,hi].tolist();p=data['glyphs'][key][str(w)][label];paths=[];values=[];lower=[];upper=[]
    for role in ['outer','inner']:
     for i in range(4):
      for j in range(2):paths.append((role,'handles',i,j));values.append(p[role]['handles'][i][j]);lower.append(.15);upper.append(.9)
     for i in [1,3]:
      paths.append((role,'bounds',i));val=p[role]['bounds'][i];values.append(val);lower.append(val-(hi[1]-lo[1])*.06);upper.append(val+(hi[1]-lo[1])*.06)
    def params(values):
     q=copy.deepcopy(p)
     for path,x in zip(paths,values):
      obj=q
      for k in path[:-1]:obj=obj[k]
      obj[path[-1]]=float(x)
     return q
    target=shape_features(cs,bounds,count=101,nonzero=True)
    def residual(values):
     pen=Flatten(None);construction(params(values)).replay(pen);return shape_features(pen.contours,bounds,count=101,nonzero=True)-target
    fit=least_squares(residual,values,bounds=(lower,upper),diff_step=1e-4,max_nfev=120,ftol=1e-9,xtol=1e-9,gtol=1e-9);data['glyphs'][key][str(w)][label]=params(fit.x);row=dict(character=ch,weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success));evidence.append(row);data['fits']=evidence;a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(row,flush=True)

if __name__=='__main__':main()
