"""Fit parenthesis arc parameters from scalar section moments."""
import argparse,json,copy,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from parenthesis_arcs import construction


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(glyphs={},measurements=[])
 for ch,name in [('(','parenleft'),(')','parenright')]:
  for w in [100,400,900]:
   for label,opt in [('text',17),('display',28)]:
    gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);assert len(flat.contours)==1;v=np.array(flat.contours[0]);lo=v.min(0);hi=v.max(0);v=(v-lo)/(hi-lo)
    if ch==')':v[:,0]=1-v[:,0]
    cs=[v.tolist()];bottom=scan(cs,.000001)[0];top=scan(cs,.999999)[0];middle=scan(cs,.5)[0];p=dict(bounds=[0,0,1,1])
    for j,role in enumerate(['outer','inner']):p[role]=dict(top_x=float(top[j]),bottom_x=float(bottom[j]),middle_x=0 if j==0 else float(middle[j]),middle_y=.5,top_slope=3,bottom_slope=3,handles=[[.35,.35],[.35,.35]])
    paths=[];values=[];lower=[];upper=[]
    for role in ['outer','inner']:
     for k,v in p[role].items():
      if k in ['top_x','bottom_x'] or role=='outer' and k=='middle_x':continue
      if k=='handles':
       for i in range(2):
        for j in range(2):paths.append((role,k,i,j));values.append(v[i][j]);lower.append(.05);upper.append(.9)
      else:
       paths.append((role,k));values.append(v)
       if k.endswith('slope'):lower.append(.1);upper.append(8)
       else:lower.append(max(.001,v-.15));upper.append(min(.99,v+.15))
    def params(v):
     q=copy.deepcopy(p)
     for path,x in zip(paths,v):
      obj=q
      for k in path[:-1]:obj=obj[k]
      obj[path[-1]]=float(x)
     return q
    target=shape_features(cs,[0,0,1,1],count=61,nonzero=True)
    def residual(v):
     z=Flatten(None);construction(params(v)).replay(z);return shape_features(z.contours,[0,0,1,1],count=61,nonzero=True)-target
    fit=least_squares(residual,values,bounds=(lower,upper),max_nfev=100,diff_step=1e-4,ftol=1e-8,xtol=1e-8,gtol=1e-8);q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();data['glyphs'].setdefault(name,{}).setdefault(str(w),{})[label]=q;row=dict(character=ch,weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success));data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
