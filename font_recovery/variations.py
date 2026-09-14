"""Independent axis sweeps using fontTools' avar-aware instancer."""
import json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from measure import CHARS,measure
OUT=Path('build/font-recovery/sfns-analysis')
FIELDS=['advance_width','left_sidebearing','right_sidebearing','bbox','counter_width','counter_height','stem_vertical','stem_horizontal','stem_diagonal','mean_handle_length','contour_area','overshoot_top','optical_center','point_count','contour_count']
def main():
    assert json.loads((OUT/'glyph-outlines.json').read_text())['completed']
    src=TTFont('/System/Library/Fonts/SFNS.ttf');axes=src['fvar'].axes
    all_rows={};deltas={};summary={}
    for axis in axes:
        lo,hi,default=axis.minValue,axis.maxValue,axis.defaultValue
        values=sorted(set([lo,lo+.25*(hi-lo),default,lo+.75*(hi-lo),hi]))
        # Distinct five samples even when default=min (GRAD).
        if len(values)<5:values=sorted(set(values+[lo+.5*(hi-lo)]))
        samples=[]
        for v in values:
            loc={a.axisTag:a.defaultValue for a in axes};loc[axis.axisTag]=v
            instance=instantiateVariableFont(src,loc,inplace=False)
            rows=[measure(instance,c) for c in CHARS]
            samples.append({'location':loc,'glyphs':rows});print(axis.axisTag,v,flush=True)
        all_rows[axis.axisTag]=samples;deltas[axis.axisTag]={};summary[axis.axisTag]={}
        baseline=next(s for s in samples if s['location'][axis.axisTag]==default)
        for i,ch in enumerate(CHARS):
            if baseline['glyphs'][i].get('missing'):continue
            curves={}
            for k in FIELDS:
                b=baseline['glyphs'][i][k]
                if b is None:continue
                vals=np.array([s['glyphs'][i][k] for s in samples],dtype=float)
                delta=vals-np.array(b);changes=np.diff(vals,axis=0)
                linear=np.array(vals[0])+np.array([(v-lo)/(hi-lo) for v in values]).reshape((-1,)+(1,)*(vals.ndim-1))*(vals[-1]-vals[0])
                curves[k]={'delta_from_default':delta.tolist(),'monotonic':bool(np.all(changes>=-1e-6) or np.all(changes<=1e-6)),'range':(vals.max(axis=0)-vals.min(axis=0)).tolist(),'max_linear_residual':float(abs(vals-linear).max()),'unchanged':bool(abs(delta).max()<1e-6)}
            deltas[axis.axisTag][ch]=curves
        summary[axis.axisTag]={'sample_values':values,'changed_fields':sorted({k for d in deltas[axis.axisTag].values() for k,v in d.items() if not v['unchanged']}),'unchanged_fields':sorted({k for d in deltas[axis.axisTag].values() for k in d if all(k not in x or x[k]['unchanged'] for x in deltas[axis.axisTag].values())}),'topology_changes':[c for c,d in deltas[axis.axisTag].items() if any(not d[k]['unchanged'] for k in ['point_count','contour_count'])]}
        (OUT/'variation-metrics.partial.json').write_text(json.dumps(all_rows,ensure_ascii=False))
    (OUT/'variation-metrics.json').write_text(json.dumps({'phase':4,'completed':True,'method':'avar-aware full instancing; one axis varies, other axes at defaults; no interactions inferred','axes':all_rows},ensure_ascii=False,indent=2))
    (OUT/'variation-deltas.json').write_text(json.dumps({'axes':deltas,'summary':summary,'gvar_usage':'Measured resultant instances; no gvar bytes copied.','missing_axes':[k for k in ['wght','wdth','opsz','GRAD'] if k not in all_rows]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
