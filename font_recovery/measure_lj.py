"""Fit Lj's El-shaped left part and its independently proportioned right bowl."""
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
from font_recovery.measure_el import fit_profile as fit_stem
from font_recovery.fitting import shape_features


def fit_profile(font, construction, character):
    body, stem_evidence=fit_stem(font,construction,character)
    glyphs=font.getGlyphSet();flat=Flatten(glyphs)
    glyphs[font.getBestCmap()[ord(character)]].draw(flat)
    points=np.concatenate(flat.contours);low=points.min(0);high=points.max(0);span=high-low
    contours=[((np.array(c)-low)/span).tolist() for c in flat.contours]
    target=shape_features(contours,[0,0,1,1],count=101,nonzero=True)
    scale=font['head'].unitsPerEm/1000
    bounds=np.array(body['bounds'])*scale
    left,bottom=(bounds[:2]-low)/span;right,top=(bounds[2:]-low)/span
    parameters=copy.deepcopy(body);parameters['bounds']=[left,bottom,right,top]
    # Probe the bowl beyond the main stem, in its flat horizontal section.
    x=right+(1-right)*.2;vertical=scan(contours,x,True,nonzero=True)
    assert len(vertical)==2,(character,vertical)
    outer_bottom,inner_bottom=vertical[0];inner_top,outer_top=vertical[1]
    axis=(outer_top+outer_bottom)/2
    inner_right=scan(contours,axis,nonzero=True)[-1][0]
    parameters['bowl']={'left':left+body['right_inner']*(right-left),'counter_left':right,
        'right':1.,'bottom':outer_bottom,'top':outer_top,'axis':axis,
        'top_x':(right+1)/2,'bottom_x':(right+1)/2,'handles':[[.4,.4],[.4,.4]],
        'inner_right':inner_right,'inner_bottom':inner_bottom,'inner_top':inner_top,
        'inner_axis':axis,'inner_top_x':(right+inner_right)/2,
        'inner_bottom_x':(right+inner_right)/2,'inner_handles':[[.4,.4],[.4,.4]]}
    keys,values,lower,upper=[],[],[],[]
    for key in ['top_x','bottom_x','axis','inner_top_x','inner_bottom_x','inner_axis','inner_right']:
        value=parameters['bowl'][key];keys.append((key,));values.append(value)
        lower.append(value-.1);upper.append(value+.1)
    for key in ['handles','inner_handles']:
        for i in range(2):
            for j in range(2):keys.append((key,i,j));values.append(.4);lower.append(.05);upper.append(.9)
    def profile(v):
        result=copy.deepcopy(parameters)
        for path,value in zip(keys,v):
            field=result['bowl']
            for key in path[:-1]:field=field[key]
            field[path[-1]]=float(value)
        return result
    def residual(v):
        pen=Flatten(None);construction(profile(v)).replay(pen)
        return shape_features(pen.contours,[0,0,1,1],count=101,nonzero=True)-target
    fit=least_squares(residual,values,bounds=(lower,upper),max_nfev=150,diff_step=1e-5,
                      x_scale='jac',ftol=1e-9,xtol=1e-9,gtol=1e-9)
    result=profile(fit.x);result['bounds']=body['bounds']
    for key,value in result['bowl'].items():
        if 'handles' in key:continue
        axis=0 if key.endswith('_x') or 'left' in key or 'right' in key else 1
        result['bowl'][key]=float((low[axis]+value*span[axis])/scale)
    return result,{'stem':stem_evidence,'bowl_residual':float(np.linalg.norm(fit.fun)),
                   'bowl_evaluations':fit.nfev,'bowl_converged':bool(fit.success)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workspace',type=Path,required=True)
    parser.add_argument('--character',choices=['Љ','љ'],required=True);args=parser.parse_args()
    sys.path.insert(0,str(args.workspace/'scripts'))
    spec=importlib.util.spec_from_file_location('el_stem',args.workspace/'scripts/el_stem.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    font=TTFont('/System/Library/Fonts/SFNS.ttf');options=subset.Options();options.layout_features=[]
    selector=subset.Subsetter(options=options);selector.populate(text=args.character);selector.subset(font)
    data,evidence={},[];filename='lj-stem.json' if args.character=='Љ' else 'lj-stem-lower.json'
    out=args.workspace/'sources'/filename
    for weight in [100,400,900]:
        data[str(weight)]={}
        for label,optical in [('text',17),('display',28)]:
            instance=instantiateVariableFont(font,{'wght':weight,'opsz':optical,'wdth':100,'GRAD':400},inplace=False)
            shape,metrics=fit_profile(instance,module.construction,args.character)
            data[str(weight)][label]=shape;evidence.append({'weight':weight,'optical':optical,**metrics})
            out.write_text(json.dumps({'weights':data},indent=2)+'\n')
            out.with_suffix('.measurement.json').write_text(json.dumps({'method':'Nonzero scan moments; El-shaped stem and two-sided bowl; no source vertices exported','profiles':evidence},indent=2)+'\n')
            print(evidence[-1],flush=True)


if __name__=='__main__':main()
