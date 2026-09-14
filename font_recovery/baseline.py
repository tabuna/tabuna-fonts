"""Freeze and compare baseline audit runs; no production geometry mutations."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    base=ROOT/'build/font-recovery/baseline'
    a=json.loads((base/'run-1/report.json').read_text())
    b=json.loads((base/'run-2/report.json').read_text())
    equal=a==b
    # Paths in top-level font field are identical; all metrics and record order must match.
    totals={k:sum(v[k] for v in a['sizes'].values()) for k in ['tp','fp','fn']}
    t,p,n=(totals[k] for k in ['tp','fp','fn'])
    totals.update(iou=t/(t+p+n),dice=2*t/(2*t+p+n),precision=t/(t+p),recall=t/(t+n))
    report={'reproducible':equal,'aggregate_definition':'micro aggregate across all glyphs and all sizes', 'totals':totals,'sizes':{},'glyphs':a['glyphs'],'error_glyphs':{},'environment':'../reports/phase-0-inventory.json'}
    for size,v in a['sizes'].items():
        report['sizes'][size]={k:x for k,x in v.items() if k!='records'}
        report['sizes'][size]['iou']=v['tp']/(v['tp']+v['fp']+v['fn'])
        report['error_glyphs'][size]=[x['character'] for x in v['records'] if x['fp'] or x['fn']]
    (base/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report['totals']));print('reproducible:',equal)
    if not equal:raise SystemExit('Baseline runs differ; further phases forbidden')
if __name__=='__main__':main()
