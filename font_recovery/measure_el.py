"""Fit an authored Cyrillic stem/returning-foot model to scalar scanline moments."""
import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from font_recovery.measure import Flatten, scan
from font_recovery.fitting import shape_features


def clip_left(contour, right):
    """Analysis-only polygon clipping to isolate Lj's stem from its bowl."""
    result=[]
    for a,b in zip(contour[-1:]+contour[:-1],contour):
        inside_a,inside_b=a[0]<=right,b[0]<=right
        if inside_a!=inside_b:
            t=(right-a[0])/(b[0]-a[0]);result.append((right,a[1]+t*(b[1]-a[1])))
        if inside_b:result.append(b)
    return result


def fit_profile(font, construction, character):
    gs=font.getGlyphSet();flat=Flatten(gs);gs[font.getBestCmap()[ord(character)]].draw(flat)
    if character in 'Љљ':
        points=np.concatenate(flat.contours);low=points.min(0);high=points.max(0)
        levels=low[1]+np.array([.75,.80,.85])*(high[1]-low[1])
        edge=float(np.mean([scan(flat.contours,y,nonzero=True)[-1][1] for y in levels]))
        flat.contours=[clip_left(c,edge) for c in flat.contours]
        flat.contours=[c for c in flat.contours if c]
    points=np.concatenate(flat.contours);left,bottom=points.min(0);right,top=points.max(0)
    normalized=[((np.array(c)-[left,bottom])/[right-left,top-bottom]).tolist() for c in flat.contours]
    vertices=np.concatenate(normalized);target=shape_features(normalized,[0,0,1,1],count=101,nonzero=True)
    rows=[.60,.65,.70];runs=[scan(normalized,y,nonzero=True) for y in rows];assert all(len(r)==2 for r in runs)
    left_edges=np.array([r[0] for r in runs]);right_edges=np.array([r[1] for r in runs])
    outer=np.polyfit(rows,left_edges[:,0],1).tolist();inner=np.polyfit(rows,left_edges[:,1],1).tolist()
    gap=(left_edges[1,1]+right_edges[1,0])/2
    cap=scan(normalized,gap,True,nonzero=True)[-1][0]
    cut=vertices[np.abs(vertices[:,0])<1e-8,1];assert len(cut)>=2
    cut_bottom,cut_top=float(cut.min()),float(cut.max())
    p={'bounds':[0,0,1,1],'stem_outer':outer,'stem_inner':inner,
       'right_inner':float(right_edges[:,0].mean()),'cap_bottom':cap,'baseline':float(-bottom/(top-bottom)),
       'foot':{'cut_bottom':cut_bottom,'cut_top':cut_top,'inside_x':.05,'inside_y':cut_top-.004,
               'outside_x':.06,'up_x':.15,'up_y':cut_top+.06,'down_x':.24,'down_y':.14,
               'up_join':.38,'down_join':.37,'up_slope':1.1,'down_slope':1.2,
               'top_slope':.12,'bottom_slope':.2,'handles':[[.35,.35] for _ in range(6)]}}
    keys,values,low,high=[],[],[],[]
    for key,value in p['foot'].items():
        if key in ('cut_top','cut_bottom'):continue
        if key=='handles':
            for i,pair in enumerate(value):
                for j,v in enumerate(pair):keys.append((key,i,j));values.append(v);low.append(.05);high.append(.9)
        else:
            keys.append((key,));values.append(value)
            if 'slope' in key:low.append(.001);high.append(4)
            else:low.append(max(-.01,value-.1));high.append(value+.1)
    def profile(v):
        result=copy.deepcopy(p)
        for path,value in zip(keys,v):
            field=result['foot']
            for key in path[:-1]:field=field[key]
            field[path[-1]]=float(value)
        return result
    def residual(v):
        candidate=Flatten(None);construction(profile(v)).replay(candidate)
        return shape_features(candidate.contours,[0,0,1,1],count=101,nonzero=True)-target
    fit=least_squares(residual,values,bounds=(low,high),max_nfev=150,diff_step=1e-5,x_scale='jac',ftol=1e-9,xtol=1e-9,gtol=1e-9)
    result=profile(fit.x);result['bounds']=[float(v/font['head'].unitsPerEm*1000) for v in (left,bottom,right,top)]
    line_residual=max(np.max(abs(np.polyval(edge,rows)-left_edges[:,i])) for i,edge in enumerate([outer,inner]))
    return result,{'residual_norm':float(np.linalg.norm(fit.fun)),'evaluations':fit.nfev,'converged':bool(fit.success),'stem_line_residual':float(line_residual)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--weights', default='100,400,900')
    parser.add_argument('--character', default='Л')
    parser.add_argument('--out-name', default='el-stem.json')
    args = parser.parse_args()
    sys.path.insert(0, str(args.workspace/'scripts'))
    spec = importlib.util.spec_from_file_location('el_stem', args.workspace/'scripts/el_stem.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    font = TTFont('/System/Library/Fonts/SFNS.ttf')
    options = subset.Options(); options.layout_features = []
    selector = subset.Subsetter(options=options); selector.populate(text=args.character); selector.subset(font)
    data, evidence = {}, []
    for weight in map(int, args.weights.split(',')):
        data[str(weight)] = {}
        for label, optical in [('text', 17), ('display', 28)]:
            instance = instantiateVariableFont(font, {'wght':weight, 'opsz':optical, 'wdth':100, 'GRAD':400}, inplace=False)
            shape, result = fit_profile(instance, module.construction, args.character)
            data[str(weight)][label] = shape
            evidence.append({'weight':weight, 'optical':optical, **result})
            out = args.workspace/'sources'/args.out_name
            out.write_text(json.dumps({'weights':data}, indent=2)+'\n')
            out.with_suffix('.measurement.json').write_text(json.dumps({'method':'Nonzero scanline moments; measured straight stems and authored six-arc foot topology; no source vertices exported', 'profiles':evidence}, indent=2)+'\n')
            print(evidence[-1], flush=True)


if __name__ == '__main__':
    main()
