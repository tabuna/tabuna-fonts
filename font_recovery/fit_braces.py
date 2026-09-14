"""Fit shared tangent-arc brace topology against scalar scanline moments."""
import sys,json,copy,argparse
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from curly_braces import construction


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume',action='store_true');a=ap.parse_args();f=TTFont('/System/Library/Fonts/SFNS.ttf')
    data=json.loads(a.out.read_text()) if a.resume and a.out.exists() else dict(glyphs={},measurements=[])
    for ch,name in [('{','braceleft'),('}','braceright')]:
      for w in [100,400,900]:
        for label,opt in [('text',17),('display',28)]:
            profiles=data['glyphs'].setdefault(name,{}).setdefault(str(w),{})
            if label in profiles:continue
            gs=f.getGlyphSet(location={'wght':w,'opsz':opt,'wdth':100,'GRAD':400});flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);pts=np.concatenate(flat.contours);lo=pts.min(0);hi=pts.max(0);cs=[(np.array(c)-lo)/(hi-lo) for c in flat.contours]
            if ch=='}':
                for c in cs:c[:,0]=1-c[:,0]
            cs=[c.tolist() for c in cs]
            p=dict(bounds=[0,0,1,1],outer=dict(stem=.4,bottom_x=.9,bottom_y=.16,lower_y=.35,nose_bottom=.47,nose_top=.53,upper_y=.65,top_y=.84,top_x=.9,handles=[[.4,.4] for _ in range(4)]),inner=dict(stem=.55,bottom_x=.9,bottom=.04,bottom_y=.16,lower_y=.37,nose_x=.15,nose_bottom=.495,nose_top=.505,upper_y=.63,top_y=.84,top_x=.9,top=.96,handles=[[.4,.4] for _ in range(4)]))
            if ch=='}':p=copy.deepcopy(data['glyphs']['braceleft'][str(w)][label]);p['bounds']=[0,0,1,1]
            stem=scan(cs,.75,nonzero=True)[0]
            p['outer']['stem'],p['inner']['stem']=stem
            caps=scan(cs,.99,vertical=True,nonzero=True)
            p['inner']['bottom'],p['inner']['top']=caps[0][1],caps[-1][0]
            nose=scan(cs,.001,vertical=True,nonzero=True)[0]
            p['outer']['nose_bottom'],p['outer']['nose_top']=nose
            p['inner']['nose_x']=scan(cs,.5,nonzero=True)[0][1]
            keys=[];vals=[];lower=[];upper=[]
            for role in ['outer','inner']:
                for k,v in p[role].items():
                    if k=='stem' or (role=='inner' and k in ('top','bottom')) or (role=='outer' and k in ('nose_bottom','nose_top')):continue
                    if k=='handles':
                        for j,pair in enumerate(v):
                            for n,x in enumerate(pair):keys.append((role,k,j,n));vals.append(x);lower.append(.05);upper.append(.95)
                    else:keys.append((role,k));vals.append(v);lower.append(max(0,v-.14));upper.append(min(1,v+.14))
            def params(v):
                q=copy.deepcopy(p)
                for path,x in zip(keys,v):
                    field=q
                    for k in path[:-1]:field=field[k]
                    field[path[-1]]=float(x)
                return q
            target=shape_features(cs,[0,0,1,1],count=101,nonzero=True)
            def residual(v):
                flat=Flatten(None);construction(params(v)).replay(flat);return shape_features(flat.contours,[0,0,1,1],count=101,nonzero=True)-target
            fit=least_squares(residual,np.clip(vals,np.array(lower)+1e-8,np.array(upper)-1e-8),bounds=(lower,upper),diff_step=1e-4,max_nfev=100,ftol=1e-8,xtol=1e-8,gtol=1e-8)
            q=params(fit.x);q['bounds']=(np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist();profiles[label]=q;row=dict(character=ch,weight=w,optical=opt,residual=float(np.linalg.norm(fit.fun)),converged=bool(fit.success));data['measurements'].append(row);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
