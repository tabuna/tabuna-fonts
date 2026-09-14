"""Compare matched variable-font raster audits using threshold-mask counts."""
import argparse
import json
from pathlib import Path
from font_recovery.compare_audits import mask_iou


def compare(before,after):
    a,b=[json.loads((root/'report.json').read_text()) for root in (before,after)]
    for key in ['glyphs','weights','sizes','method']:
        assert a[key]==b[key],f'Audit scope changed: {key}'
    assert a['reproducible'] and b['reproducible']
    assert len(a['instances'])==len(b['instances'])
    rows,regressions,growth=[],[],[]
    for old,new in zip(a['instances'],b['instances']):
        assert (old['weight'],old['size'])==(new['weight'],new['size'])
        folder=Path(f"wght-{old['weight']}")/str(old['size'])
        settings=[json.loads((root/folder/'render-settings.json').read_text()) for root in (before,after)]
        clean=lambda value:{k:v for k,v in value.items() if k not in ('fontSHA256','records')}
        assert clean(settings[0])==clean(settings[1]),'Renderer settings changed'
        for record in settings[1]['records']:
            assert all(name.startswith('TabunaSans-') for name in record['tabuna']['renderedFonts'])
            filename=record['system']['file']
            assert (before/folder/filename).read_bytes()==(after/folder/filename).read_bytes()
        expected = ([r['character'] for r in a['instances'][0]['records']]
                    if settings[0].get('textMode') else list(a['glyphs']))
        assert expected and len(expected)==len(set(expected)), 'Empty or duplicate audit entries'
        for records in (old['records'],new['records'],settings[0]['records'],settings[1]['records']):
            assert [r['character'] for r in records]==expected, 'Audit entries changed'
        for x,y in zip(old['records'],new['records']):
            assert x['character']==y['character']
            largest=lambda r:max([c['area'] for c in r['largestFP']]+[0])
            row={'weight':old['weight'],'size':old['size'],'character':x['character'],
                 'before':{**{k:x[k] for k in ('tp','fp','fn')},'mask_iou':mask_iou(x),'ink_iou':x['iou']},
                 'after':{**{k:y[k] for k in ('tp','fp','fn')},'mask_iou':mask_iou(y),'ink_iou':y['iou']},
                 'largest_fp_component':[largest(x),largest(y)]}
            rows.append(row)
            if mask_iou(y)<mask_iou(x):regressions.append(row)
            if largest(y)>largest(x):growth.append(row)
    return {'matched_cases':len(rows),'repeat_verified':True,
            'renderer_and_reference_pixels_equal':True,'mask_regressions':regressions,
            'fp_component_growth_requiring_review':growth,'results':rows}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--before',type=Path,required=True)
    parser.add_argument('--after',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();report=compare(args.before,args.after)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False))
    assert not report['mask_regressions'],'Threshold-mask regression'


if __name__=='__main__':main()
