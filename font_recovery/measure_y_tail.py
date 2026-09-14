"""Measure diagonal fork geometry and fit independent tail tangent parameters."""
import argparse
import copy
import json
import sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from font_recovery.measure import Flatten,scan
from font_recovery.fitting import shape_features


def profile(font, character, construction, seed=None):
    gs=font.getGlyphSet();flat=Flatten(gs);gs[font.getBestCmap()[ord(character)]].draw(flat)
    points=np.concatenate(flat.contours);left,bottom=points.min(0);right,top=points.max(0)
    contours=[((np.array(c)-[left,bottom])/[right-left,top-bottom]).tolist() for c in flat.contours]
    points=np.concatenate(contours);p={'bounds':[0,0,1,1]};residuals={}
    levels=np.array([.82,.86,.90,.94,.98]);edges=[]
    for y in levels:
        runs=scan(contours,y,nonzero=True);assert len(runs)==2,(character,y,runs)
        edges.append([*runs[0],*runs[1]])
    for j,key in enumerate(['outer_left','inner_left','inner_right','outer_right']):
        values=np.array(edges)[:,j];a,b=np.polyfit(levels,values,1);p[key]=[float(a),float(b)]
        residuals[key]=float(max(abs(values-(a*levels+b))))
    a,b=p['inner_left'];c,d=p['inner_right'];y=(d-b)/(a-c);x=a*y+b
    vertical=scan(contours,x,vertical=True,nonzero=True);p['counter_bottom']=max(r[1] for r in vertical)
    assert p['counter_bottom']<.82
    cut_x=float(points[points[:,1]<.15,0].min())
    cut=scan(contours,cut_x+1e-7,vertical=True,nonzero=True)[0]
    outer_x=float(points[abs(points[:,1])<1e-8,0].mean())
    p['foot']={'cut_x':cut_x,'cut_bottom':cut[0],'cut_top':cut[1],
        'outer_x':outer_x,'inner_x':outer_x-.025,'inner_y':cut[1]-.008,
        'inner_rise':.1,'outer_join':.27,'inner_slope':.45,
        'outer_bend_x':outer_x+.12,'outer_bend_y':.075,'outer_bend_slope':.9,
        'inner_progress_x':.6,'inner_progress_y':.45,'inner_bend_slope':1.,
        'heel_slope':.1,'tip_slope':.1,'handles':[[.35,.35] for _ in range(6)]}
    if seed is not None:
        for k in p['foot']:
            if k in seed['foot'] and k not in ['cut_x','cut_bottom','cut_top','outer_x']:
                p['foot'][k]=copy.deepcopy(seed['foot'][k])
        old=seed['foot'];foot=p['foot']
        if 'inner_join' in old:
            join=max(old['inner_join'],old['inner_bend_y']+.02)
            foot['inner_rise']=join-foot['inner_y']
            lo=p['outer_left'][0]*join+p['outer_left'][1]
            foot['inner_progress_x']=float(np.clip((old['inner_bend_x']-foot['inner_x'])/(lo-foot['inner_x']),.11,.89))
            foot['inner_progress_y']=float(np.clip((old['inner_bend_y']-foot['inner_y'])/foot['inner_rise'],.11,.89))
    keys=[];values=[];low=[];high=[]
    for key,v in p['foot'].items():
        if key in ['cut_x','cut_bottom','cut_top','outer_x']:continue
        if key=='handles':
            for i,pair in enumerate(v):
                for j,value in enumerate(pair):keys.append((key,i,j));values.append(value);low.append(.05);high.append(.8)
        else:
            keys.append((key,));values.append(v)
            if 'progress' in key:low.append(.1);high.append(.9)
            elif key=='inner_rise':low.append(.015);high.append(.3)
            elif 'slope' in key:low.append(.001);high.append(3.)
            elif 'join' in key:low.append(.12);high.append(.5)
            else:low.append(max(.001,v-.10));high.append(v+.12)
    def result(v):
        q=copy.deepcopy(p)
        for path,value in zip(keys,v):
            field=q['foot']
            for key in path[:-1]:field=field[key]
            field[path[-1]]=float(value)
        return q
    target=shape_features(contours,[0,0,1,1],count=81,nonzero=True)
    def residual(v):
        f=Flatten(None);construction(result(v)).replay(f)
        return shape_features(f.contours,[0,0,1,1],count=81,nonzero=True)-target
    fit=least_squares(residual,values,bounds=(low,high),max_nfev=350,ftol=1e-9,xtol=1e-9,gtol=1e-9)
    q=result(fit.x);q['bounds']=[float(v/2.048) for v in [left,bottom,right,top]]
    return q,{'edge_residual':residuals,'tail_fit_norm':float(np.linalg.norm(fit.fun)),
              'evaluations':fit.nfev,'converged':bool(fit.success)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workspace',type=Path,required=True);parser.add_argument('--resume',action='store_true');parser.add_argument('--weights',default='100,400,900');args=parser.parse_args()
    sys.path.insert(0,str(args.workspace/'scripts'))
    from y_tail import construction
    font=TTFont('/System/Library/Fonts/SFNS.ttf');s=subset.Subsetter();s.populate(text='yуУ');s.subset(font)
    seeds=json.loads((args.workspace/'sources/y-tail.json').read_text())['glyphs'] if args.resume else {}
    data=copy.deepcopy(seeds) if seeds else {'y':{},'uni0443':{},'uni0423':{}}
    weights=[int(w) for w in args.weights.split(',')]
    evidence=[]
    previous=args.workspace/'sources/y-tail.measurement.json'
    if args.resume and previous.exists():
        evidence=[p for p in json.loads(previous.read_text())['profiles'] if p['weight'] not in weights]
    for weight in weights:
        for k in data:data[k][str(weight)]={}
        for label,optical in [('text',17),('display',28)]:
            f=instantiateVariableFont(font,{'wght':weight,'opsz':optical,'wdth':100,'GRAD':400})
            for character,key in [('y','y'),('У','uni0423')]:
                q,e=profile(f,character,construction,seeds.get(key,{}).get(str(weight),{}).get(label))
                if label=='display' and e['tail_fit_norm']>.005:
                    alternative,measurement=profile(f,character,construction,data[key][str(weight)]['text'])
                    if measurement['tail_fit_norm']<e['tail_fit_norm']:
                        q,e=alternative,{**measurement,'initialization':'same-weight text profile'}
                data[key][str(weight)][label]=q
                evidence.append({'character':character,'weight':weight,'opsz':optical,**e});print(evidence[-1],flush=True)
            # The lowercase Cyrillic form is a translated component in the reference.
            gs=f.getGlyphSet();a=Flatten(gs);b=Flatten(gs)
            gs[f.getBestCmap()[ord('y')]].draw(a);gs[f.getBestCmap()[ord('у')]].draw(b)
            aa=np.concatenate(a.contours);bb=np.concatenate(b.contours);delta=bb-aa
            assert np.max(abs(delta-delta[0]))<1e-8 and abs(delta[0,1])<1e-8
            q=copy.deepcopy(data['y'][str(weight)][label]);q['bounds'][0]+=float(delta[0,0]/2.048);q['bounds'][2]+=float(delta[0,0]/2.048)
            data['uni0443'][str(weight)][label]=q
            path=args.workspace/'sources/y-tail.json';path.write_text(json.dumps({'glyphs':data},indent=2)+'\n')
            path.with_suffix('.measurement.json').write_text(json.dumps({'method':__doc__,'profiles':evidence},ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
