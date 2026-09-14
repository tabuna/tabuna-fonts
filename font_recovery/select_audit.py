"""Select verified cases from a completed full audit without rendering again."""
import argparse,copy,hashlib,json,shutil
from pathlib import Path


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--chars',required=True)
    ap.add_argument('--sizes',help='Optional comma-separated subset of measured sizes');args=ap.parse_args()
    raw=(args.source/'report.json').read_bytes();d=json.loads(raw)
    assert d.get('reproducible'), 'Only a completed repeat-verified audit can be reused'
    chars=args.chars;assert set(chars)<=set(d['glyphs'])
    result=copy.deepcopy(d);result['glyphs']=chars;result['instances']=[];result.pop('byWeight',None)
    if args.sizes:
        result['sizes']=list(map(int,args.sizes.split(',')))
        assert set(result['sizes'])<=set(d['sizes'])
    for instance in d['instances']:
        if instance['size'] not in result['sizes']:continue
        folder=Path(f"wght-{instance['weight']}")/str(instance['size'])
        target=args.out/folder;target.mkdir(parents=True,exist_ok=True)
        item=copy.deepcopy(instance);bychar={r['character']:r for r in item['records']}
        item['records']=[bychar[c] for c in chars]
        for k in ['tp','fp','fn']:item[k]=sum(r[k] for r in item['records'])
        item['meanInkIoU']=sum(r['iou'] for r in item['records'])/len(chars)
        result['instances'].append(item)
        settings=json.loads((args.source/folder/'render-settings.json').read_text())
        bychar={r['character']:r for r in settings['records']};settings['records']=[bychar[c] for c in chars]
        for r in settings['records']:
            for role in ['system','tabuna']:
                filename=r[role]['file'];shutil.copy2(args.source/folder/filename,target/filename)
        for r in item['records']:
            path=Path(r['highlight']);shutil.copy2(args.source/path,args.out/path)
        (target/'render-settings.json').write_text(json.dumps(settings,ensure_ascii=False,indent=2)+'\n')
    result['selection_source']=dict(path=str(args.source),report_sha256=hashlib.sha256(raw).hexdigest(),method='Exact subset of completed repeat-verified records and their original native PNGs')
    (args.out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(cases=len(chars)*len(result['instances']),characters=len(chars))))


if __name__=='__main__':main()
