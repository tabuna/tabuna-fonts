"""Fit tangent transitions against scanline moments; export construction dimensions."""
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
from de_stem import construction


def profile(font,ch,g2=False):
    gs=font.getGlyphSet();flat=Flatten(gs);gs[font.getBestCmap()[ord(ch)]].draw(flat)
    cs=[[(x/font['head'].unitsPerEm,y/font['head'].unitsPerEm) for x,y in c] for c in flat.contours]
    pts=np.concatenate(cs);lo=pts.min(0);hi=pts.max(0);top=float(hi[1]);bottom=float(lo[1])
    levels=np.array([.55,.6,.65,.7])*top;runs=[scan(cs,y,nonzero=True) for y in levels];assert all(len(r)==2 for r in runs)
    edges=np.array(runs);outer=np.polyfit(levels,edges[:,0,0],1);inner=np.polyfit(levels,edges[:,0,1],1)
    x=(edges[1,0,1]+edges[1,1,0])/2;vertical=scan(cs,x,vertical=True,nonzero=True);assert len(vertical)==2
    barbottom,bartop=vertical[0];cap=vertical[1][0];legs=scan(cs,bottom/2,nonzero=True);assert len(legs)==2
    near=scan(cs,bartop+.0001,nonzero=True);assert len(near)==2
    p=dict(top=top,bottom=bottom,outer=outer.tolist(),inner=inner.tolist(),right_outer=float(edges[:,1,1].mean()),right_inner=float(edges[:,1,0].mean()),cap_bottom=cap,
           bar=dict(left=float(lo[0]),right=float(hi[0]),bottom=barbottom,top=bartop),legs=legs,
           outer_cut=near[0][0],inner_cut=near[0][1],outer_join=top*.4,inner_join=top*.4,outer_handles=[.35,.35],inner_handles=[.35,.35])
    if g2:p['g2']=1
    keys=['outer_cut','inner_cut','outer_join','inner_join'];values=[p[k] for k in keys]+[.35]*4
    low=[float(lo[0]),float(lo[0]),bartop+.005,bartop+.005]+[.05]*4
    high=[float(edges[0,0,0]),float(edges[0,0,1]),top*.52,top*.52]+[.9]*4
    if g2:
        values=values[:4]+[.35,.35];low=low[:4]+[.05,.05];high=high[:4]+[.9,.9]
        high[0]=float(np.polyval(outer,bartop))-.0001
        high[1]=float(np.polyval(inner,bartop))-.0001
    def params(v):
        q=copy.deepcopy(p)
        for k,n in zip(keys,v):q[k]=float(n)
        q['outer_handles']=list(map(float,v[4:6]));q['inner_handles']=list(map(float,v[6:8]))
        if g2:q['outer_handles']=[.35,float(v[4])];q['inner_handles']=[float(v[5]),.35]
        return q
    bounds=[*lo,*hi];target=shape_features(cs,bounds,count=81,nonzero=True)
    def residual(v):
        f=Flatten(None);construction(params(v)).replay(f)
        return shape_features(f.contours,bounds,count=81,nonzero=True)-target
    fit=least_squares(residual,np.clip(values,np.array(low)+1e-8,np.array(high)-1e-8),bounds=(low,high),max_nfev=100,diff_step=1e-4,x_scale='jac')
    q=params(fit.x)
    for k in ['top','bottom','right_outer','right_inner','cap_bottom','outer_cut','inner_cut','outer_join','inner_join']:q[k]*=1000
    for k in ['outer','inner']:q[k][1]*=1000
    q['bar']={k:v*1000 for k,v in q['bar'].items()};q['legs']=[[v*1000 for v in leg] for leg in q['legs']]
    return q,dict(residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--resume',action='store_true');ap.add_argument('--g2',action='store_true');args=ap.parse_args()
    f=TTFont('/System/Library/Fonts/SFNS.ttf');o=subset.Options();o.layout_features=[];s=subset.Subsetter(options=o);s.populate(text='Дд');s.subset(f)
    d=json.loads(args.out.read_text()) if args.resume and args.out.exists() else dict(glyphs={},measurements=[])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    for w in [100,400,900]:
        for label,optical in [('text',17),('display',28)]:
            font=instantiateVariableFont(f,{'wght':w,'opsz':optical,'wdth':100,'GRAD':400},inplace=False)
            for ch in 'Дд':
                entries=d['glyphs'].setdefault(f'uni{ord(ch):04X}',{}).setdefault(str(w),{})
                if label in entries:continue
                p,e=profile(font,ch,args.g2);entries[label]=p;row=dict(character=ch,weight=w,optical=optical,**e);d['measurements'].append(row);args.out.write_text(json.dumps(d,indent=2)+'\n');print(row,flush=True)


if __name__=='__main__':main()
