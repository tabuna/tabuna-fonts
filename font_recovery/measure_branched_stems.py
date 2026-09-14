"""Measure Zhe band equations and level joins from fixed scan intervals.

No source vertices are exported. Left/right reflection residuals are retained
as evidence, so imposing symmetry cannot silently discard asymmetry.
"""
import argparse,json
from fractions import Fraction
from pathlib import Path
import numpy as np
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.boundsPen import BoundsPen
from font_recovery.measure import Flatten,scan


def grid_cap(line, origin_y, low, high, fallback):
    """Choose an exact lattice point on a measured line, if one lies in the join.

    This avoids changing a long straight edge when TrueType rounds an arbitrary
    clipping intersection. Non-integral profiles use the ordinary overlap cap.
    """
    slope,offset=line
    x=(slope*origin_y+offset)*2.048
    y=origin_y*2.048
    step=Fraction(slope).limit_denominator(4096)
    if abs(float(step)-slope)>1e-10 or max(abs(x-round(x)),abs(y-round(y)))>1e-6:
        return fallback
    period=step.denominator
    target=fallback*2.048
    level=(y+round((target-y)/period)*period)/2.048
    return level if low < level < high else fallback


def profile(font,ch):
    gs=font.getGlyphSet();name=font.getBestCmap()[ord(ch)]
    flat,bounds=Flatten(gs),BoundsPen(gs);gs[name].draw(flat);gs[name].draw(bounds)
    left,bottom,right,top=bounds.bounds
    assert bottom==0
    stems=[];result={'top':top/2.048};residuals={};reflection=[]
    for band,fractions in [('upper',[.82,.86,.90,.94,.98]),('lower',[.02,.06,.10,.14,.18])]:
        levels=np.array(fractions)*top;edges=[]
        for level in levels:
            runs=scan(flat.contours,level,nonzero=True)
            assert len(runs)==3,(ch,level,runs)
            stems.append(runs[1]);edges.append(runs[2])
            axis=sum(runs[1])/2
            reflection.extend(abs(a-(2*axis-b)) for a,b in zip(runs[0],reversed(runs[2])))
        result[band]={}
        for i,side in enumerate(['left','right']):
            observed=np.array(edges)[:,i];slope,intercept=np.polyfit(levels,observed,1)
            result[band][side]=[float(slope),float(intercept/2.048)]
            residuals[band+'_'+side]=float(np.max(np.abs(observed-(slope*levels+intercept))))
    stem=np.mean(stems,axis=0);result['stem']=(stem/2.048).tolist()
    joins=[]
    for fraction in [.025,.05,.075]:
        x=stem[1]+(stem[1]-stem[0])*fraction
        runs=scan(flat.contours,x,vertical=True,nonzero=True)
        assert len(runs)==1,(ch,x,runs)
        joins.append(runs[0])
    result['join']=(np.mean(joins,axis=0)[::-1]/2.048).tolist()
    jt,jb=result['join'];ur=result['upper']['right'];lr=result['lower']['right']
    notch=(lr[1]-ur[1])/(ur[0]-lr[0])
    assert jb<notch<jt,(ch,jb,notch,jt)
    uc=grid_cap(ur,result['top'],jb,notch,(jb+notch)/2)
    lc=grid_cap(lr,0,notch,jt,(notch+jt)/2)
    result['caps']=[uc,lc]
    return result,dict(max_line_residual=residuals,max_reflection_residual=max(reflection),
                      join_spread=np.ptp(joins,axis=0).tolist())


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();font=TTFont('/System/Library/Fonts/SFNS.ttf')
    options=subset.Options();options.layout_features=[]
    selector=subset.Subsetter(options=options);selector.populate(text='Жж');selector.subset(font)
    data={f'uni{ord(ch):04X}':{} for ch in 'Жж'};evidence=[]
    for weight in [100,400,900]:
        for label,optical in [('text',17),('display',28)]:
            instance=instantiateVariableFont(font,{'wght':weight,'opsz':optical,'wdth':100,'GRAD':400},inplace=False)
            for ch in 'Жж':
                p,measurements=profile(instance,ch)
                data[f'uni{ord(ch):04X}'].setdefault(str(weight),{})[label]=p
                evidence.append(dict(character=ch,weight=weight,optical=optical,**measurements))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps({'glyphs':data},indent=2)+'\n')
    args.out.with_suffix('.measurement.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    print(args.out)


if __name__=='__main__':main()
