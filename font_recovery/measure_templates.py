"""Recover aggregate dimensions and moments, never source outline nodes.

Each round contour is reduced to bbox, normalized area and second moments.
An original four-cubic symmetric oval is fit to those three observations.
"""
from pathlib import Path
import argparse,json,hashlib,copy
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools import subset
from fontTools.varLib.instancer import instantiateVariableFont
from font_recovery.measure import Flatten,scan
from font_recovery.primitives import oval
ROOT=Path(__file__).resolve().parents[1]
SHARED_SHAPES={'Е':'E','Н':'H','О':'O','о':'o','Т':'T','І':'I','С':'C','с':'c'}

def shared_shape(font,character,base):
    """Share a constructed template only after verifying source equivalence.

    The comparison is read-only. Only translation and metrics are exported;
    the resulting shape is still built by our own Latin-family primitive.
    """
    names=font.getBestCmap();glyf=font['glyf']
    own_name,base_name=names[ord(character)],names[ord(base)]
    own,own_ends,own_flags=glyf[own_name].getCoordinates(glyf)
    other,other_ends,other_flags=glyf[base_name].getCoordinates(glyf)
    assert list(own_ends)==list(other_ends) and list(own_flags)==list(other_flags),character
    difference=np.asarray(own,dtype=float)-np.asarray(other,dtype=float)
    dx,dy=difference[0]
    assert np.allclose(difference,[dx,dy],atol=1e-6,rtol=0),character
    gs=font.getGlyphSet();bounds=BoundsPen(gs);gs[own_name].draw(bounds)
    advance,lsb=font['hmtx'][own_name]
    return {'template':'component','base':base,'dx':float(dx),'dy':float(dy),
            'advance':advance,'lsb':lsb,'bbox':list(bounds.bounds)}

def moments(poly):
    a=np.asarray(poly,dtype=float);b=np.roll(a,-1,axis=0);c=a[:,0]*b[:,1]-b[:,0]*a[:,1]
    area=c.sum()/2
    ix=(c*(a[:,0]**2+a[:,0]*b[:,0]+b[:,0]**2)).sum()/12
    iy=(c*(a[:,1]**2+a[:,1]*b[:,1]+b[:,1]**2)).sum()/12
    return np.array([abs(area),ix/area,iy/area])

def round_contour(poly):
    a=np.asarray(poly);lo=a.min(axis=0);hi=a.max(axis=0);mid=(lo+hi)/2;rad=(hi-lo)/2
    target=moments((a-mid)/rad)
    def generated(k):
        p=Flatten(None);oval(p,[-1,-1,1,1],*k);return moments(p.contours[0])
    fit=least_squares(lambda k:(generated(k)-target)*[1,4,4],[.6,.6],bounds=([.35,.35],[.9,.9]),xtol=1e-11,ftol=1e-11,gtol=1e-11)
    return {'bbox':[float(lo[0]),float(lo[1]),float(hi[0]),float(hi[1])],'handles':fit.x.tolist(),'observed_moments':target.tolist(),'model_moments':generated(fit.x).tolist(),'fit_residual_norm':float(np.linalg.norm(fit.fun))}

def glyph(font,ch,related=None):
    gs=font.getGlyphSet();name=font.getBestCmap()[ord(ch)];p=Flatten(gs);gs[name].draw(p);b=BoundsPen(gs);gs[name].draw(b)
    lo,bt,hi,tp=b.bounds;adv,lsb=font['hmtx'][name];d={'advance':adv,'bbox':list(b.bounds),'lsb':lsb}
    if ch in 'oO0':
        contours=sorted(p.contours,key=lambda c:abs(moments(c)[0]),reverse=True)
        assert len(contours)==2
        d.update(template='round',outer=round_contour(contours[0]),inner=round_contour(contours[1]))
    elif ch in 'Cc':
        from font_recovery.measure_bowls import measure_open_bowl
        d=measure_open_bowl(font,ch,d,p)
    elif ch=='D':
        from font_recovery.measure_bowls import measure_flat_bowl
        contours=sorted(p.contours,key=lambda c:moments(c)[0],reverse=True)
        assert len(contours)==2
        d.update(template='flat_bowl',outer=measure_flat_bowl(contours[0]),inner=measure_flat_bowl(contours[1]))
    elif ch in 'bdpq':
        from font_recovery.measure_bowls import measure_stem_bowl
        d=measure_stem_bowl(font,ch,d,p)
    elif ch=='H':
        bars=scan(p.contours,(lo+hi)/2,vertical=True);stems=scan(p.contours,tp*.2)
        assert len(bars)==1 and len(stems)==2
        d.update(template='capital_h',stem=float(np.mean([r-l for l,r in stems])),crossbar=bars[0])
    elif ch in 'EFL':
        stem_run=scan(p.contours,tp*.25)[0]
        stem=stem_run[1]-stem_run[0]
        levels=scan(p.contours,lo+stem+1,vertical=True)
        bars=[]
        for bottom,top in levels:
            runs=scan(p.contours,(bottom+top)/2)
            assert len(runs)==1
            bars.append({'bottom':bottom,'top':top,'right':runs[0][1]})
        assert len(bars)=={'E':3,'F':2,'L':1}[ch]
        d.update(template='stem_and_bars',stem=stem,bars=bars)
    elif ch=='I':
        d.update(template='rectangle')
    elif ch=='T':
        stems=scan(p.contours,tp*.2)
        bars=scan(p.contours,lo+1,vertical=True)
        assert len(stems)==len(bars)==1
        d.update(template='capital_t',stem_interval=stems[0],bar_bottom=bars[0][0])
    elif ch in 'nhu':
        H=font['OS/2'].sxHeight
        # Sample the straight part: near the foot for n/h, near the top for u.
        stems=scan(p.contours,H*(.8 if ch=='u' else .2));assert len(stems)==2
        sv=float(np.mean([r-l for l,r in stems]))
        # OS/2 stores rounded metadata. The visible baseline/flat top must use
        # the fractional geometric height of the actual varied outline.
        if ch=='n':H=scan(p.contours,lo+sv/2,vertical=True)[-1][1]
        elif ch=='u':H=tp
        elif related is not None:H=related['x_height']
        if ch=='u':
            p.contours=[[(lo+hi-x,H-y) for x,y in c] for c in p.contours]
            bt,tp=H-tp,H-bt
            d['bbox']=[lo,bt,hi,tp]
        crown_x=(lo+hi+sv)/2
        arch_top=max(y for c in p.contours for x,y in c if x>lo+sv+1)
        # The counter narrows at heavy weights. Measure inside its actual
        # opening, rather than at a crown estimate that can enter a stem.
        counter_x=(stems[0][1]+stems[1][0])/2
        if ch=='u':counter_x=lo+hi-counter_x
        top_runs=scan(p.contours,counter_x,vertical=True);inner=top_runs[-1][0]
        d.update(template='shoulder_u' if ch=='u' else 'shoulder_n',stem=sv,x_height=H,stem_top=tp if ch=='h' else H,
                 arch_top=arch_top,join=H*.8,shoulder=H*.58,inner_top=inner,crown_x=crown_x,
                 inner_crown_x=crown_x-sv*.2,inner_join=H*.6,inner_shoulder=H*.58,
                 outer_departure_x=.2,outer_departure_y=.8,outer_top_left=.6,
                 outer_top_right=.6,outer_side_right=.6,inner_top_left=.6,
                 inner_side_left=.6,inner_top_right=.6,inner_side_right=.6)
        # Fit semantic arch parameters to area, centroid-free moments and
        # occupied widths on fixed normalized scanlines (not source nodes).
        from font_recovery.primitives import shoulder_n
        levels=H*np.array([.2,.4,.5,.55,.6,.65,.7,.74,.78,.82,.86,.9,.93,.95,.97,.99,1.005,1.015])
        def features(cs):
            out=[]
            for y in levels:
                runs=scan(cs,y)
                for power in [1,2,3]:
                    out.append(sum(((r-lo)**power-(l-lo)**power)/power for l,r in runs)/(hi-lo)**power)
            return np.array(out)
        target=features(p.contours)
        keys=['join','shoulder','inner_top','crown_x','inner_crown_x','inner_join','inner_shoulder',
              'outer_departure_x','outer_departure_y','outer_top_left','outer_top_right','outer_side_right',
              'inner_top_left','inner_side_left','inner_top_right','inner_side_right']
        scales=np.array([H,H,H,hi-lo,hi-lo,H,H]+[1]*9)
        # Related letters start from the same fitted shoulder, transported by
        # height and width. This avoids an unrelated local optimum for h/u.
        if related is not None:
            old_left,_,old_right,_=related['bbox']
            for key in keys:
                if key in ['crown_x','inner_crown_x']:
                    d[key]=lo+(related[key]-old_left)*(hi-lo)/(old_right-old_left)
                elif key in ['join','shoulder','inner_top','inner_join','inner_shoulder']:
                    d[key]=related[key]*H/related['x_height']
                else:d[key]=related[key]
        def profile(v):return {**d,**dict(zip(keys,(v*scales).tolist()))}
        def residual(v):
            q=Flatten(None);shoulder_n(q,profile(v));return features(q.contours)-target
        x=np.array([d[k] for k in keys])/scales
        inner_limit=min(.9,inner/H-.02)
        lower=[.5,.25,.4,(lo+sv*.8)/(hi-lo),(lo+sv+1)/(hi-lo),.2,.2]+[.05]*9
        upper=[.98,.9,1.02,(hi-sv*.6)/(hi-lo),(hi-sv-1)/(hi-lo),inner_limit,inner_limit]+[.95]*9
        if np.any(np.asarray(lower) >= np.asarray(upper)):
            raise ValueError(f'{ch}: invalid shoulder limits: stem={sv}, width={hi-lo}, height={H}, inner={inner}; {list(zip(keys, lower, upper))}')
        x=np.clip(x,np.asarray(lower)+1e-6,np.asarray(upper)-1e-6)
        fit=least_squares(residual,x,bounds=(lower,upper),max_nfev=700,ftol=1e-10,xtol=1e-10,gtol=1e-10)
        d=profile(fit.x);d['fit_residual_norm']=float(np.linalg.norm(fit.fun));d['observed_scan_features']=target.tolist()
    if 'template' not in d:
        raise ValueError(f'No independent measurement/template for {ch}')
    return d

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--weights',default='400');ap.add_argument('--optical-sizes',default='28')
    ap.add_argument('--add-chars',help='Measure these new characters while retaining the current measured samples')
    ap.add_argument('--extend-weights', action='store_true', help='Add measured locations while preserving every existing design master')
    args=ap.parse_args()
    source=ROOT/'build/font-recovery/research-v2/scalar-measurements.json'
    chars=args.add_chars or 'oO0HnhuEFLITCcDbdpq'
    from font_recovery.model import DESIGN
    previous=json.loads(DESIGN.read_text())['samples'] if (args.add_chars or args.extend_weights) else []
    references=chars+''.join(SHARED_SHAPES)+''.join(SHARED_SHAPES.values())
    f=TTFont('/System/Library/Fonts/SFNS.ttf');opt=subset.Options();opt.layout_features=[];ss=subset.Subsetter(options=opt);ss.populate(text=references);ss.subset(f)
    rows=[]
    for weight in map(float,args.weights.split(',')):
        for optical in map(float,args.optical_sizes.split(',')):
            loc={'wght':weight,'opsz':optical,'wdth':100,'GRAD':400};inst=instantiateVariableFont(f,loc,inplace=False)
            saved=next((row for row in previous if row['location']==loc),None)
            if args.add_chars and saved is None:
                raise ValueError(f'No prior sample at {loc}; measure the base model first')
            profiles=copy.deepcopy(saved['glyphs']) if saved else {}
            for c in chars:
                profiles[c]=glyph(inst,c,profiles.get('n') if c in 'hu' else None)
            for c,base in SHARED_SHAPES.items():
                if base in profiles:
                    profiles[c]=shared_shape(inst,c,base)
            rows.append({'location':loc,'glyphs':profiles});print(loc,flush=True)
    if args.extend_weights:
        rows += [row for row in previous if not any(new['location']==row['location'] for new in rows)]
        rows.sort(key=lambda row: (row['location']['opsz'], row['location']['wght']))
    data={'format_version':1,'project_name':'Tabuna Sans','source_sha256':hashlib.sha256(Path('/System/Library/Fonts/SFNS.ttf').read_bytes()).hexdigest(),'method':'Independent cubic templates fitted to scalar dimensions, normalized moments and fixed scanline integral features; no source points exported','scope':'development; full alphabet still required','samples':rows}
    source.parent.mkdir(parents=True,exist_ok=True);source.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    from font_recovery.model import export_design
    export_design(source)
if __name__=='__main__':main()
