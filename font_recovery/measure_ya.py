"""Fit the Ya stem/leg/bowl model from scalar scanline observations."""
import argparse,copy,json,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from ya_bowl import construction


def fit_profile(font,ch):
    gs=font.getGlyphSet();flat=Flatten(gs);gs[font.getBestCmap()[ord(ch)]].draw(flat)
    points=np.concatenate(flat.contours);lo=points.min(axis=0);hi=points.max(axis=0)
    contours=[[(float((x-lo[0])/(hi[0]-lo[0])),float((y-lo[1])/(hi[1]-lo[1]))) for x,y in c] for c in flat.contours]
    levels=np.array([.025,.065,.105,.145,.185]);runs=[scan(contours,y,nonzero=True) for y in levels]
    assert all(len(r)==2 for r in runs)
    stem=float(np.mean([r[-1][0] for r in runs]))
    leg={side:np.polyfit(levels,[r[0][i] for r in runs],1).tolist() for i,side in enumerate(['left','right'])}
    vertical=scan(contours,stem-.025,vertical=True,nonzero=True)
    assert len(vertical)>=2,(ch,vertical)
    bottom=vertical[-2][0];ib=vertical[-2][1];it=vertical[-1][0]
    def bowl():
        return dict(upper_x=.3,upper_y=.7,lower_x=.3,lower_y=.7,
                    upper_slope=1,lower_slope=1,end_slope=0,
                    handles=[[.34,.34] for _ in range(4)])
    outer=bowl();inner=bowl()
    levels=np.linspace(bottom+.035,.97,61)
    edges=[scan(contours,y,nonzero=True)[0][0] for y in levels]
    k=int(np.argmin(edges));axis=float(levels[k]);left=float(edges[k])
    inner_axis=(ib+it)/2;inside=scan(contours,inner_axis,nonzero=True)[0][1]
    outer.update(top_x=.52,left=left,axis=axis,join_y=bottom+.025,end_slope=.3)
    inner.update(top_x=.53,bottom_x=.53,left=inside,axis=inner_axis,top=it,bottom=ib)
    p=dict(bounds=[0,0,1,1],stem=stem,leg=leg,bowl_bottom=bottom,outer=outer,inner=inner)
    keys=[];values=[];low=[];high=[]
    for role in ['outer','inner']:
        for key,val in p[role].items():
            if key=='end_slope' and role=='inner':continue
            if key=='handles':
                for i in range(4):
                    for j in range(2):
                        keys.append((role,key,i,j));values.append(val[i][j]);low.append(.08);high.append(.8)
            else:
                keys.append((role,key));values.append(val)
                if 'slope' in key:low.append(0 if key=='end_slope' else .1);high.append(4)
                elif key in ['upper_x','upper_y','lower_x','lower_y']:low.append(.15);high.append(.85)
                else:low.append(max(.001,val-.10));high.append(min(.999,val+.10))
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
    fit=least_squares(residual,values,bounds=(low,high),max_nfev=140,diff_step=1e-4,x_scale='jac',ftol=1e-8,xtol=1e-8,gtol=1e-8)
    q=profile(fit.x);q['bounds']=[float(v/font['head'].unitsPerEm*1000) for v in [*lo,*hi]]
    return q,dict(residual_norm=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--weights',default='100,400,900');ap.add_argument('--resume',action='store_true')
    args=ap.parse_args();font=TTFont('/System/Library/Fonts/SFNS.ttf')
    options=subset.Options();options.layout_features=[];s=subset.Subsetter(options=options);s.populate(text='Яя');s.subset(font)
    data=json.loads(args.out.read_text()) if args.resume and args.out.exists() else {'glyphs':{},'measurements':[]}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    for weight in map(int,args.weights.split(',')):
        for label,optical in [('text',17),('display',28)]:
            instance=instantiateVariableFont(font,{'wght':weight,'opsz':optical,'wdth':100,'GRAD':400},inplace=False)
            for ch in 'Яя':
                key=f'uni{ord(ch):04X}';profiles=data['glyphs'].setdefault(key,{}).setdefault(str(weight),{})
                if args.resume and label in profiles:continue
                p,e=fit_profile(instance,ch);profiles[label]=p
                row=dict(character=ch,weight=weight,optical=optical,**e);data['measurements'].append(row)
                args.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
