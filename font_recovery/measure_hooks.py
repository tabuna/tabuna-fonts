"""Fit an authored hook while measuring stem and crossbar independently."""
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
from hooked_stems import construction


def fit_profile(font,ch):
    gs=font.getGlyphSet();f=Flatten(gs);gs[font.getBestCmap()[ord(ch)]].draw(f)
    points=np.concatenate(f.contours);lo=points.min(axis=0);hi=points.max(axis=0)
    contours=[[(float((x-lo[0])/(hi[0]-lo[0])),float((y-lo[1])/(hi[1]-lo[1]))) for x,y in c] for c in f.contours]
    if ch=='t':contours=[[(x,1-y) for x,y in c] for c in contours]
    stems=[scan(contours,y,nonzero=True) for y in [.015,.025,.035]]
    assert all(len(r)==1 for r in stems)
    stem=np.mean([r[0] for r in stems],axis=0).tolist()
    vertical=scan(contours,.01,vertical=True,nonzero=True);assert len(vertical)==1,vertical
    bottom,top=vertical[0];bar_run=scan(contours,(bottom+top)/2,nonzero=True);assert len(bar_run)==1
    bar=dict(left=bar_run[0][0],right=bar_run[0][1],bottom=bottom,top=top)
    tip=max(scan(contours,y,nonzero=True)[-1][1] for y in np.linspace(top+.03,.995,71))
    cut=scan(contours,tip-.001,vertical=True,nonzero=True)[-1]
    peak=scan(contours,.999,nonzero=True)[-1];peak_x=sum(peak)/2
    thick=(stem[1]-stem[0])*(hi[0]-lo[0])/(hi[1]-lo[1])
    outer=dict(join=max(top+.025,.75),top_x=peak_x,top=1,cut=cut[1],slope=.15,handles=[[.4,.4],[.34,.34]])
    inner=dict(join=max(top+.02,.73),top_x=peak_x,top=1-thick,cut=cut[0],slope=.15,handles=[[.4,.4],[.34,.34]])
    for q in [outer,inner]:
        q['rise']=max(.005,q['top']-q.pop('join'))
        q['drop']=max(.001,q['top']-q.pop('cut'))
    p=dict(bounds=[0,0,1,1],stem=stem,bar=bar,tip_x=tip,outer=outer,inner=inner)
    keys=[];values=[];low=[];high=[]
    for role in ['outer','inner']:
        for key,value in p[role].items():
            if role=='outer' and key=='top':continue
            if key=='handles':
                for i in range(2):
                    for j in range(2):keys.append((role,key,i,j));values.append(value[i][j]);low.append(.08);high.append(.85)
            else:
                keys.append((role,key));values.append(value)
                if key=='slope':low.append(.01);high.append(3)
                elif key=='rise':low.append(.003);high.append(.45)
                elif key=='drop':low.append(.0001);high.append(.25)
                elif key=='top_x':low.append(stem[1]+.001);high.append(tip-.001)
                else:low.append(max(top+.001,value-.15));high.append(min(.9999,value+.15))
    def profile(v):
        q=copy.deepcopy(p)
        for path,value in zip(keys,v):
            field=q
            for key in path[:-1]:field=field[key]
            field[path[-1]]=float(value)
        return q
    values=np.clip(values,np.array(low)+1e-7,np.array(high)-1e-7)
    target=shape_features(contours,[0,0,1,1],count=81,nonzero=True)
    def residual(v):
        f=Flatten(None);construction(profile(v)).replay(f)
        return shape_features(f.contours,[0,0,1,1],count=81,nonzero=True)-target
    fit=least_squares(residual,values,bounds=(low,high),max_nfev=120,diff_step=1e-4,x_scale='jac',ftol=1e-8,xtol=1e-8,gtol=1e-8)
    q=profile(fit.x);q['bounds']=[float(v/font['head'].unitsPerEm*1000) for v in [*lo,*hi]]
    return q,dict(residual_norm=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--weights',default='100,400,900');ap.add_argument('--resume',action='store_true');args=ap.parse_args()
    font=TTFont('/System/Library/Fonts/SFNS.ttf');o=subset.Options();o.layout_features=[];s=subset.Subsetter(options=o);s.populate(text='ft');s.subset(font)
    data=json.loads(args.out.read_text()) if args.resume and args.out.exists() else dict(glyphs={},measurements=[])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    for weight in map(int,args.weights.split(',')):
        for label,optical in [('text',17),('display',28)]:
            f=instantiateVariableFont(font,{'wght':weight,'opsz':optical,'wdth':100,'GRAD':400},inplace=False)
            for ch in 'ft':
                profiles=data['glyphs'].setdefault(ch,{}).setdefault(str(weight),{})
                if args.resume and label in profiles:continue
                p,e=fit_profile(f,ch);profiles[label]=p;row=dict(character=ch,weight=weight,optical=optical,**e);data['measurements'].append(row)
                args.out.write_text(json.dumps(data,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
