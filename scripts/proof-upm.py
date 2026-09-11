#!/usr/bin/env python3
"""Compare isolated UPM builds against unchanged native references."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'proofs/upm'
CHARACTERS = list('IPРDBВвOоnЬьПЦШ')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    reference = ROOT/'references/upm-baseline/TabunaSans-before.ttf'
    baseline_sha = digest(reference)
    output = {'baselineSHA256': baseline_sha, 'baselineUPM': 2048,
              'scope': '15 control glyphs, three weights and four native sizes; no full-font acceptance',
              'experiments': {}}
    for upm in (4096, 16384):
        font = ROOT/f'build/upm-experiment/{upm}/dist/TabunaSansVariable.ttf'
        sha = digest(font)
        rows = []
        for weight in (100, 400, 900):
            for size in (16, 32, 64, 128):
                a_folder, b_folder = FOLDER/f'2048-{weight}-{size}', FOLDER/f'{upm}-{weight}-{size}'
                a = json.loads((a_folder/'comparison.json').read_text())
                b = json.loads((b_folder/'comparison.json').read_text())
                assert a['fontSHA256'] == baseline_sha and b['fontSHA256'] == sha
                assert a['weight'] == b['weight'] == weight
                assert a['pointSize'] == b['pointSize'] == size
                assert [r['character'] for r in a['records']] == [r['character'] for r in b['records']] == CHARACTERS
                for old, new in zip(a['records'], b['records']):
                    im_a = Image.open(a_folder/old['system']['file']).convert('RGB')
                    im_b = Image.open(b_folder/new['system']['file']).convert('RGB')
                    assert im_a.size == im_b.size
                    assert ImageChops.difference(im_a, im_b).getbbox() is None
                    rows.append({'weight': weight, 'size': size, 'character': old['character'],
                                 'beforeIoU': old['inkIoU'], 'afterIoU': new['inkIoU'],
                                 'beforeExactPixels': old['exactMatch'], 'afterExactPixels': new['exactMatch'],
                                 'beforeExactAdvance': old['exactAdvance'], 'afterExactAdvance': new['exactAdvance'],
                                 'beforeAdvanceError': old['advanceDifference'], 'afterAdvanceError': new['advanceDifference'],
                                 'beforeDifferentPixels': old['differentPixels'], 'afterDifferentPixels': new['differentPixels']})
        def summary(selected):
            n = len(selected)
            return {'total': n, 'improved': sum(r['afterIoU'] > r['beforeIoU'] for r in selected),
                    'worsened': sum(r['afterIoU'] < r['beforeIoU'] for r in selected),
                    'sameIoU': sum(r['afterIoU'] == r['beforeIoU'] for r in selected),
                    'beforeMeanIoU': sum(r['beforeIoU'] for r in selected)/n,
                    'afterMeanIoU': sum(r['afterIoU'] for r in selected)/n,
                    'beforeExactPixels': sum(r['beforeExactPixels'] for r in selected),
                    'afterExactPixels': sum(r['afterExactPixels'] for r in selected),
                    'lostExactPixels': sum(r['beforeExactPixels'] and not r['afterExactPixels'] for r in selected),
                    'beforeExactAdvance': sum(r['beforeExactAdvance'] for r in selected),
                    'afterExactAdvance': sum(r['afterExactAdvance'] for r in selected),
                    'beforeMeanAbsoluteAdvanceError': sum(abs(r['beforeAdvanceError']) for r in selected)/n,
                    'afterMeanAbsoluteAdvanceError': sum(abs(r['afterAdvanceError']) for r in selected)/n}
        result = {'fontSHA256': sha, 'allReferencesIdentical': True,
                  'woff2Bytes': font.with_suffix('.woff2').stat().st_size,
                  'summary': summary(rows),
                  'byWeight': {str(w): summary([r for r in rows if r['weight'] == w]) for w in (100, 400, 900)},
                  'byCharacter': {ch: summary([r for r in rows if r['character'] == ch]) for ch in CHARACTERS},
                  'rows': rows}
        output['experiments'][str(upm)] = result
    (FOLDER/'results.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({upm: {'summary': result['summary'], 'byWeight': result['byWeight']}
                      for upm, result in output['experiments'].items()}, indent=2))


if __name__ == '__main__':
    main()
