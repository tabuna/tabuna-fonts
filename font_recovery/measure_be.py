"""Fit a stem, bar and shared Bézier bowl to Be's scalar scan moments."""
import argparse,copy,json,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from be_bowl import construction


def fit_profile(font):
    gs=font.getGlyphSet();f=Flatten(gs);gs[font.getBestCmap()[ord('Б')]].draw(f)
    points=np.concatenate(f.contours);lo=points.min(axis=0);hi=points.max(axis=0)
    contours=[[(float((x-lo[0])/(hi[0]-lo[0])),float((y-lo[1])/(hi[1]-lo[1]))) for x,y in c] for c in f.contours]
    stem=scan(contours,.75,nonzero=True)[0][1]
    # Measure the horizontal bowl boundaries near the stem, before the
    # curved shoulder; a center scan can cut the arc instead of its flat top.
    vertical=scan(contours,stem+.02,vertical=True,nonzero=True)
    assert len(vertical)==3,vertical
    cap=dict(right=scan(contours,.995,nonzero=True)[0][1],bottom=vertical[-1][0])
    outer_top=vertical[1][1];inner_top=vertical[1][0];inner_bottom=vertical[0][1]
    def bowl():return dict(upper_x=.3,upper_y=.7,lower_x=.3,lower_y=.7,upper_slope=1,lower_slope=1,end_slope=0,handles=[[.34,.34] for _ in range(4)])
    outer=bowl();inner=bowl();axis=outer_top/2
    inside=scan(contours,(inner_top+inner_bottom)/2,nonzero=True)[-1][0]
    outer.update(top_x=.52,bottom_x=.52,top=outer_top,bottom=0,right=1,axis=axis)
    inner.update(top_x=(stem+inside)/2,bottom_x=(stem+inside)/2,top=inner_top,bottom=inner_bottom,right=inside,axis=(inner_top+inner_bottom)/2)
    p=dict(bounds=[0,0,1,1],stem=stem,cap=cap,outer=outer,inner=inner)
    keys=[];values=[];low=[];high=[]
    for role in ['outer','inner']:
        for key,val in p[role].items():
            if key in ['end_slope','top','bottom'] or (role=='outer' and key=='right'):continue
            if key=='handles':
                for i in range(4):
                    for j in range(2):keys.append((role,key,i,j));values.append(val[i][j]);low.append(.08);high.append(.8)
            else:
                keys.append((role,key));values.append(val)
                if 'slope' in key:low.append(.1);high.append(4)
                elif key in ['upper_x','upper_y','lower_x','lower_y']:low.append(.15);high.append(.85)
                else:low.append(max(.001,val-.08));high.append(min(.999,val+.08))
    def profile(values):
        q=copy.deepcopy(p)
        for path,value in zip(keys,values):
            field=q
            for key in path[:-1]:field=field[key]
            field[path[-1]]=float(value)
        return q
    target=shape_features(contours,[0,0,1,1],count=81,nonzero=True)
    def residual(v):
        f=Flatten(None);construction(profile(v)).replay(f)
        return shape_features(f.contours,[0,0,1,1],count=81,nonzero=True)-target
    fit=least_squares(residual,values,bounds=(low,high),max_nfev=120,diff_step=1e-4,x_scale='jac',ftol=1e-8,xtol=1e-8,gtol=1e-8)
    q=profile(fit.x);q['bounds']=[float(v/font['head'].unitsPerEm*1000) for v in [*lo,*hi]]
    return q,dict(residual_norm=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume',action='store_true')
    args=ap.parse_args();font=TTFont('/System/Library/Fonts/SFNS.ttf')
    options=subset.Options();options.layout_features=[];s=subset.Subsetter(options=options);s.populate(text='Б');s.subset(font)
    data=json.loads(args.out.read_text()) if args.resume and args.out.exists() else dict(weights={},measurements=[])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    for weight in [100,400,900]:
        for label,optical in [('text',17),('display',28)]:
            profiles=data['weights'].setdefault(str(weight),{})
            if args.resume and label in profiles:continue
            instance=instantiateVariableFont(font,{'wght':weight,'opsz':optical,'wdth':100,'GRAD':400},inplace=False)
            p,e=fit_profile(instance);profiles[label]=p
            row=dict(weight=weight,optical=optical,**e);data['measurements'].append(row)
            args.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
