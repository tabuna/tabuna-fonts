"""Fit scalar section moments of a spiral/bowl model, not source control nodes."""
import argparse,json,copy,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.measure_rings import fit_pair
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from at_spiral import construction


def seed(w):
    t={100:.035,400:.07,900:.13}[w]
    outer=dict(tip_x=.71,tip_y=.025,bottom_x=.51,bottom_y=0,left_x=0,left_y=.49,top_x=.5,top_y=1,right_x=1,right_y=.54,hook_x=.83,hook_y=.24,stem_x=.70,stem_y=.35)
    inner=dict(tip_x=.71,tip_y=.025+t,bottom_x=.51,bottom_y=t,left_x=t,left_y=.49,top_x=.5,top_y=1-t,right_x=1-t,right_y=.54,hook_x=.83,hook_y=.24+t,stem_x=.70-t,stem_y=.35)
    return dict(bounds=[0,0,1,1],spiral=dict(outer=outer,inner=inner,cap=.75,tip_slope=.25,handles=[[.4,.4] for _ in range(6)]),bowl_bounds=[.27,.24,.70,.76],bowl_handles=[[.55,.55] for _ in range(4)])


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume',action='store_true');ap.add_argument('--seed',type=Path);a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf');data=json.load(open(a.out)) if a.resume and a.out.exists() else dict(weights={},measurements=[])
    for w in [100,400,900]:
      for label,opt in [('text',17),('display',28)]:
        profiles=data['weights'].setdefault(str(w),{})
        if label in profiles:continue
        gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));flat=Flatten(gs);gs[f.getBestCmap()[64]].draw(flat);assert len(flat.contours)==2;allpts=np.concatenate(flat.contours);lo=allpts.min(0);hi=allpts.max(0);cs=[((np.array(c)-lo)/(hi-lo)).tolist() for c in flat.contours];hole=min(cs,key=lambda c:np.prod(np.ptp(np.array(c),axis=0)));counter,e=fit_pair([hole,hole],1000);p=copy.deepcopy(json.load(open(a.seed))['weights'][str(w)][label]) if a.seed else seed(w);p['bounds']=[0,0,1,1];p['counter_bounds']=counter['bounds'][0];p['counter_handles']=counter['outerHandles'];t={100:.035,400:.07,900:.13}[w];cb=p['counter_bounds'];p['bowl_bounds']=p.get('bowl_bounds',[cb[0]-t,cb[1]-t,cb[2]+t*.5,cb[3]+t])
        terminal_x=max(x for x,y in cs[0] if y<.12);terminal=scan(cs,terminal_x-1e-5,vertical=True,nonzero=True)[0]
        for role,y in zip(['outer','inner'],terminal):p['spiral'][role]['tip_x']=terminal_x;p['spiral'][role]['tip_y']=y
        for role in ['outer','inner']:
            q=p['spiral'][role]
            if 'handles' not in q:q['handles']=copy.deepcopy(p['spiral']['handles'])
            if 'stem_fraction' not in q:q['stem_fraction']=min(.9,max(.15,(q.pop('stem_y',q['hook_y']+.1)-q['hook_y'])/(p['spiral']['cap']-q['hook_y'])))
        p['spiral'].pop('handles',None)
        sp=p['spiral']
        if 'stem_x' in sp['outer']:
            a_x=sp['outer'].pop('stem_x');b_x=sp['inner'].pop('stem_x');sp['stem_left']=min(a_x,b_x);sp['stem_width']=abs(a_x-b_x)
        keys=[];vals=[];lows=[];highs=[]
        def visit(obj,path=()):
            if isinstance(obj,dict):
                for k,v in obj.items():
                    if not path and k in ['bounds','counter_bounds','counter_handles']:continue
                    if path in [('spiral','outer'),('spiral','inner')] and k in ['tip_x','tip_y']:continue
                    if path==('spiral','outer') and k in ['bottom_y','left_x','top_y','right_x']:continue
                    visit(v,path+(k,))
            elif isinstance(obj,list):
                for i,v in enumerate(obj):visit(v,path+(i,))
            else:
                keys.append(path);vals.append(obj)
                if 'handles' in path or 'bowl_handles' in path:lows.append(.1);highs.append(.9)
                elif path[-1]=='stem_width':lows.append(.005);highs.append(.25)
                elif path[-1]=='stem_fraction':lows.append(.02);highs.append(.95)
                elif path[-1]=='tip_slope':lows.append(.01);highs.append(1)
                else:lows.append(max(-.03,obj-.085));highs.append(min(1.03,obj+.085))
        visit(p)
        def params(v):
            q=copy.deepcopy(p)
            for path,x in zip(keys,v):
                obj=q
                for k in path[:-1]:obj=obj[k]
                obj[path[-1]]=float(x)
            return q
        target=shape_features(cs,[0,0,1,1],count=61,nonzero=True)
        def residual(v):
            q=Flatten(None);construction(params(v)).replay(q);return shape_features(q.contours,[0,0,1,1],count=61,nonzero=True)-target
        fit=least_squares(residual,vals,bounds=(lows,highs),max_nfev=100,diff_step=1e-4,ftol=1e-7,xtol=1e-7,gtol=1e-7);q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();profiles[label]=q;row=dict(weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),converged=bool(fit.success),evaluations=fit.nfev,counter_residual=e[0]);data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
