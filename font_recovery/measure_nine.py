"""Fit an authored bowl/counter/tail model to scalar scanline moments."""
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


def fit_profile(font, construction, initial=None):
    gs = font.getGlyphSet(); flat = Flatten(gs)
    gs[font.getBestCmap()[ord('9')]].draw(flat)
    points = np.concatenate(flat.contours)
    left, bottom = points.min(axis=0); right, top = points.max(axis=0)
    normalized = [[((x-left)/(right-left), (y-bottom)/(top-bottom)) for x,y in c] for c in flat.contours]
    target = shape_features(normalized, [0,0,1,1], count=161,nonzero=True)
    vertices = np.concatenate(normalized)
    vertical = scan(normalized,.5,True); horizontal = scan(normalized,.68)
    assert len(vertical)==3 and len(horizontal)==2
    caps=[]
    for c in normalized:
        for a,b in zip(c,c[1:]+c[:1]):
            if abs(a[1]-b[1])<1e-8 and a[1]<.4 and abs(a[0]-b[0])>.05:
                caps.append((min(a[0],b[0]),max(a[0],b[0]),a[1]))
    assert len(caps)==1,caps
    cut_left,cut_right,cut_y=caps[0]
    p={'bounds':[0,0,1,1],
       'outer':{'top_x':.48,'axis':float(vertices[np.argmax(vertices[:,0]),1]),'bottom_x':.47,
                'handles':[[.4,.4] for _ in range(8)]},
       'tail':{'outer_cut_x':cut_left,'inner_cut_x':cut_right,'cut_y':cut_y,
               'outer_cut_slope':.2,'inner_cut_slope':.4,'bottom_x':.47,'bottom':vertical[0][1],
               'join_x':1-horizontal[0][1],'join_y':.51},
       'bowl':{'bottom_x':.45,'bottom':vertical[1][0],'left_y':float(vertices[np.argmin(vertices[:,0]),1]),'join_slope':1.3},
       'counter':{'left':horizontal[0][1],'right':horizontal[1][0],
                  'top_x':.48,'bottom_x':.48,'top':vertical[2][0],'bottom':vertical[1][1],
                  'left_y':.67,'right_y':.67,'handles':[[.4,.4] for _ in range(4)]}}
    if initial is not None:
        p=copy.deepcopy(initial);p['bounds']=[0,0,1,1]
    if 'shoulder_x' not in p['outer']:
        # Split the existing upper-right arc at its midpoint, exactly. The
        # extra shoulder has one shared tangent, so the join remains smooth.
        from math import dist
        o=p['outer'];a=np.array([o['top_x'],1.]);d=np.array([1.,o['axis']]);span=dist(a,d)
        b=a+[span*o['handles'][0][0],0];c=d+[0,span*o['handles'][0][1]]
        e=(a+b)/2;f=(b+c)/2;g=(c+d)/2;h=(e+f)/2;i=(f+g)/2;j=(h+i)/2
        o['shoulder_x'],o['shoulder_y']=map(float,j)
        o['shoulder_slope']=float(-(i[1]-h[1])/(i[0]-h[0]))
        o['handles'][0]=[dist(a,e)/dist(a,j),dist(h,j)/dist(a,j)]
        o['handles'].append([dist(j,i)/dist(j,d),dist(g,d)/dist(j,d)])
    keys,values,low,high=[],[],[],[]
    for role in ('outer','tail','bowl','counter'):
        for key,value in p[role].items():
            if key=='handles':
                for i,pair in enumerate(value):
                    for j,v in enumerate(pair):
                        keys.append((role,key,i,j));values.append(v);low.append(.08);high.append(.9)
            else:
                keys.append((role,key));values.append(value)
                if 'slope' in key:low.append(.01);high.append(4)
                else:low.append(max(-.02,value-.15));high.append(min(1.02,value+.15))
    def profile(v):
        result=copy.deepcopy(p)
        for path,value in zip(keys,v):
            field=result
            for key in path[:-1]:field=field[key]
            field[path[-1]]=float(value)
        return result
    def residual(v):
        candidate=Flatten(None);construction(profile(v)).replay(candidate)
        return shape_features(candidate.contours,[0,0,1,1],count=161,nonzero=True)-target
    fit=least_squares(residual,values,bounds=(low,high),max_nfev=300,diff_step=1e-4,x_scale='jac',ftol=1e-10,xtol=1e-10,gtol=1e-10)
    result=profile(fit.x);result['bounds']=[float(v/font['head'].unitsPerEm*1000) for v in (left,bottom,right,top)]
    return result,{'residual_norm':float(np.linalg.norm(fit.fun)),'evaluations':fit.nfev,'converged':bool(fit.success)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--weights', default='100,400,900')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    sys.path.insert(0, str(args.workspace/'scripts'))
    spec = importlib.util.spec_from_file_location('nine_bowl', args.workspace/'scripts/nine_bowl.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    font = TTFont('/System/Library/Fonts/SFNS.ttf')
    options = subset.Options(); options.layout_features = []
    selector = subset.Subsetter(options=options); selector.populate(text='9'); selector.subset(font)
    out = args.workspace/'sources/nine-bowl.json'
    data = json.loads(out.read_text())['weights'] if args.resume else {}
    metadata = out.with_suffix('.measurement.json')
    evidence = json.loads(metadata.read_text())['profiles'] if args.resume and metadata.exists() else []
    for weight in map(int, args.weights.split(',')):
        data.setdefault(str(weight), {})
        for label, optical in [('text', 17), ('display', 28)]:
            instance = instantiateVariableFont(font, {'wght':weight, 'opsz':optical, 'wdth':100, 'GRAD':400}, inplace=False)
            shape, result = fit_profile(instance, module.construction, data[str(weight)].get(label) if args.resume else None)
            data[str(weight)][label] = shape
            evidence = [entry for entry in evidence if (entry['weight'],entry['optical']) != (weight,optical)]
            evidence.append({'weight':weight, 'optical':optical, **result})
            out = args.workspace/'sources/nine-bowl.json'
            out.write_text(json.dumps({'weights':data}, indent=2)+'\n')
            out.with_suffix('.measurement.json').write_text(json.dumps({'method':'Nonzero-winding scalar scanline moments; authored bowl/counter/tail topology; no source vertices exported', 'profiles':evidence}, indent=2)+'\n')
            print(evidence[-1], flush=True)


if __name__ == '__main__':
    main()
