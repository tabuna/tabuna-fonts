"""Recover Che cup parameters from scalar cross-section moments."""
import argparse,json,sys,copy
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from che_cup import construction


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(glyphs={},measurements=[])
    for ch in 'Чч':
      for w in [100,400,900]:
       for label,opt in [('text',17),('display',28)]:
        gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);v=np.concatenate(flat.contours);lo=v.min(0);hi=v.max(0);cs=[((np.array(c)-lo)/(hi-lo)).tolist() for c in flat.contours];stems=scan(cs,.95);left,right=stems[0][1],stems[-1][0]
        ys=scan(cs,(left+right)/2,vertical=True)[0]
        p=dict(bounds=[0,0,1,1],left=left,right=right)
        for i,key in enumerate(['outer','inner']):p[key]=dict(start_y=.73,bottom_x=(left+right)/2,bottom_y=ys[i],join_y=scan(cs,right-1e-5,vertical=True)[0][i],slope=.55,handles=[[.4,.4],[.35,.35]])
        paths=[];values=[];lower=[];upper=[]
        for key in ['outer','inner']:
          q=p[key]
          for name in ['start_y','bottom_x','bottom_y','join_y','slope']:
            paths.append((key,name));values.append(q[name]);lower.append(.05 if name=='slope' else max(.01,q[name]-.2));upper.append(2 if name=='slope' else min(.99,q[name]+.2))
          for i in range(2):
           for j in range(2):paths.append((key,'handles',i,j));values.append(q['handles'][i][j]);lower.append(.1);upper.append(.8)
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
        fit=least_squares(residual,values,bounds=(lower,upper),max_nfev=120,diff_step=1e-4,ftol=1e-8,xtol=1e-8,gtol=1e-8);p=params(fit.x);p['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();name='uni%04X'%ord(ch);data['glyphs'].setdefault(name,{}).setdefault(str(w),{})[label]=p
        row=dict(character=ch,weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success));data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
