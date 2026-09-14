"""Measure J/j edge landmarks and fit tangent lengths from section moments."""
import argparse,json,copy,sys,math
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from j_hooks import construction


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=dict(glyphs={},measurements=[])
 for ch in 'Jj':
  for w in [100,400,900]:
   for label,opt in [('text',17),('display',28)]:
    gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);co=min(flat.contours,key=lambda c:min(y for x,y in c));v=np.array(co);lo=v.min(0);hi=v.max(0);v=(v-lo)/(hi-lo);cs=[v.tolist()];stem=scan(cs,.8,nonzero=True)[0];p=dict(stem=stem,bounds=[0,0,1,1]);tip=scan(cs,.000001,vertical=True,nonzero=True)[0]
    if ch=='J':
     top=tip[1];near=scan(cs,top-1e-6,nonzero=True)[0];inner_tip_x=near[1];center=scan(cs,1e-6,nonzero=True)[0];bottom_x=sum(center)/2;inner_bottom=scan(cs,bottom_x,vertical=True,nonzero=True)[0][1]
     p['outer']=dict(join_y=.3,bottom_x=bottom_x,bottom_y=0,tip_x=0,tip_y=top,tip_angle=math.pi/2,handles=[[.4,.4],[.4,.4]])
     p['inner']=dict(join_y=.3,bottom_x=bottom_x,bottom_y=inner_bottom,tip_x=inner_tip_x,tip_y=top,tip_angle=math.pi/2,handles=[[.4,.4],[.4,.4]])
    else:
     p['outer']=dict(join_y=.2,bottom_x=.15,bottom_y=0,tip_x=0,tip_y=tip[0],tip_angle=.08,handles=[[.4,.4],[.4,.4]])
     p['inner']=dict(join_y=.2,bottom_x=.04,bottom_y=tip[1],tip_x=0,tip_y=tip[1],tip_angle=0,handles=[[.4,.4],[.4,.4]])
    paths=[];values=[];lower=[];upper=[]
    for role in ['outer','inner']:
     for k,vv in p[role].items():
      if k in ['tip_x','tip_y'] or role=='outer' and k=='bottom_y' or ch=='J' and k=='tip_angle':continue
      if k=='handles':
       for i in range(2):
        for j in range(2):paths.append((role,k,i,j));values.append(vv[i][j]);lower.append(.02);upper.append(.95)
      else:
       paths.append((role,k));values.append(vv)
       bounds={'join_y':(.12,.5),'bottom_x':(.001,.7 if ch=='J' else .4),'bottom_y':(max(0,vv-.06),min(.5,vv+.06)),'tip_angle':(-.3,.5)};l,u=bounds[k];lower.append(l);upper.append(u)
    def params(values):
     q=copy.deepcopy(p)
     for path,x in zip(paths,values):
      obj=q
      for k in path[:-1]:obj=obj[k]
      obj[path[-1]]=float(x)
     return q
    target=shape_features(cs,[0,0,1,1],count=71,nonzero=True)
    def residual(values):
     z=Flatten(None);construction(params(values)).replay(z);return shape_features(z.contours,[0,0,1,1],count=71,nonzero=True)-target
    fit=least_squares(residual,values,bounds=(lower,upper),max_nfev=100,diff_step=1e-4,ftol=1e-8,xtol=1e-8,gtol=1e-8);q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();data['glyphs'].setdefault(ch,{}).setdefault(str(w),{})[label]=q;row=dict(character=ch,weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success));data['measurements'].append(row);args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)

if __name__=='__main__':main()
