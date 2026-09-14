"""Gate a full regular audit against its predecessor, preserving other glyphs."""
import argparse
import json
from pathlib import Path


def mask_iou(record):
    union = record['tp']+record['fp']+record['fn']
    return record['tp']/union if union else 1.0


def totals(report):
    counts = {key: sum(size[key] for size in report['sizes'].values())
              for key in ('tp', 'fp', 'fn')}
    tp, fp, fn = (counts[key] for key in ('tp', 'fp', 'fn'))
    return {**counts, 'iou': tp/(tp+fp+fn), 'dice': 2*tp/(2*tp+fp+fn),
            'precision': tp/(tp+fp), 'recall': tp/(tp+fn)}


def compare(before, after, characters):
    a, b = [json.loads((root/'report.json').read_text()) for root in (before, after)]
    assert a['glyphs'] == b['glyphs'], 'Audit coverage changed'
    assert set(characters) <= set(a['glyphs']), 'Changed characters absent from audit'
    assert a['sizes'].keys() == b['sizes'].keys(), 'Audit sizes changed'
    assert a['method'] == b['method'], 'Audit method changed'
    assert b['reproducible'], 'Candidate audit not verified by repetition'
    changes = []
    for size in a['sizes']:
        old, new = [json.loads((root/size/'render-settings.json').read_text())
                    for root in (before, after)]
        # All global rendering settings are equal except the actual font hash.
        old_settings = {k:v for k,v in old.items() if k not in ('fontSHA256', 'records')}
        new_settings = {k:v for k,v in new.items() if k not in ('fontSHA256', 'records')}
        assert old_settings == new_settings, f'Renderer settings changed: {size}'
        assert len(old['records']) == len(new['records']) == len(a['glyphs'])
        for record in new['records']:
            assert record['tabuna']['renderedFonts'] == ['TabunaSans-Regular'], 'Font fallback'
            kinds = ['system'] + ([] if record['character'] in characters else ['tabuna'])
            for kind in kinds:
                filename = record[kind]['file']
                assert (before/size/filename).read_bytes() == (after/size/filename).read_bytes(), filename
        for x, y in zip(a['sizes'][size]['records'], b['sizes'][size]['records']):
            assert x['character'] == y['character']
            if x['character'] not in characters:
                assert x == y, f'Unexpected character change: {x["character"]}'
            else:
                # The renderer also reports an alpha/ink IoU. The requested
                # threshold-mask gate is TP/(TP+FP+FN), kept distinct here.
                assert mask_iou(y) >= mask_iou(x), f'Character regressed: {x["character"]}'
                changes.append({'character':x['character'], 'size':int(size),
                                'before':{**{k:x[k] for k in ('tp','fp','fn')},
                                          'iou':mask_iou(x), 'ink_iou':x['iou']},
                                'after':{**{k:y[k] for k in ('tp','fp','fn')},
                                         'iou':mask_iou(y), 'ink_iou':y['iou']}})
    initial, candidate = totals(a), totals(b)
    assert candidate['iou'] > initial['iou'], 'Overall IoU did not improve'
    return {'full_regular_gate_passed':True, 'before':initial, 'after':candidate,
            'unchanged_characters':len(a['glyphs'])-len(set(characters)),
            'renderer_settings_and_reference_pixels_equal':True,
            'repeat_verified':True, 'changes':changes,
            'scope':'Regular full audit only; variable, technical and text gates are separate'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--characters', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = compare(args.before, args.after, args.characters)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
