"""Check the baseline milestone and evidence required for an authorial release."""
import argparse
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_valid(root, evidence, font_sha):
    path = (root/evidence['path']).resolve()
    return (path.is_relative_to(root.resolve()) and path.is_file()
            and evidence.get('font_sha256') == font_sha
            and sha(path) == evidence.get('sha256'))


def inspect(root=ROOT):
    decisions = json.loads((root/'sources/design-decisions.json').read_text())
    quality = json.loads((root/'reports/current-quality.json').read_text())
    verification = json.loads((root/'reports/verification.json').read_text())
    font_path = root/'dist/TabunaSansVariable.ttf'
    digest = sha(font_path)
    font = TTFont(font_path)
    constraints = decisions['constraints']
    failures = []
    if quality['font_sha256'] != digest:
        failures.append('quality report does not describe the current TTF')
    if verification.get('font_sha256') != digest or verification.get('status') != 'passed':
        failures.append('font verification is missing or stale')
    if not quality.get('repeat_verified'):
        failures.append('raster reproducibility is not verified')
    expected = {(cp, w, size) for cp in font.getBestCmap()
                for w in range(100, 901, 100) for size in (16, 64)}
    actual = [(int(r['codepoint'][2:], 16), r['weight'], r['size']) for r in quality['all_cases']]
    if len(actual) != len(expected) or set(actual) != expected:
        failures.append('quality matrix must contain each required case exactly once')
    if any((r['mask_iou'] is None and int(r['codepoint'][2:], 16) not in (0x20, 0xA0))
           or (r['mask_iou'] is not None and not 0 <= r['mask_iou'] <= 1)
           for r in quality['all_cases']):
        failures.append('visible glyph measurements are missing or invalid')
    if len(font.getBestCmap()) != constraints['characters']:
        failures.append('character coverage differs from the design contract')
    axes = {a.axisTag: [a.minValue, a.maxValue] for a in font['fvar'].axes}
    if axes != {tag: constraints[tag] for tag in ('wght', 'opsz')}:
        failures.append('variation axes differ from the design contract')
    if any(r['custom_fallback'] or r['reference_fallback'] for r in quality['all_cases']):
        failures.append('font fallback occurred')
    if (root/'dist/TabunaSansVariable.woff2').stat().st_size > constraints['woff2_max_bytes']:
        failures.append('WOFF2 exceeds the size budget')
    below = sorted((r for r in quality['all_cases']
                    if r['mask_iou'] is not None and r['mask_iou'] < constraints['baseline_minimum_mask_iou']),
                   key=lambda r: r['mask_iou'])
    pending = []
    assert {d['id'] for d in decisions['decisions']} == {f'D0{i}' for i in range(1, 7)}
    assert len(decisions['decisions']) == 6
    for d in decisions['decisions']:
        evidence_ok = bool(d['evidence']) and all(evidence_valid(root, e, digest) for e in d['evidence'])
        verdict = d.get('verdict') or {}
        if (d['status'] != 'accepted' or not d['change'] or not evidence_ok
                or verdict.get('decision') != 'accept' or not verdict.get('reason')):
            pending.append(d['id'])
    checkpoint = decisions.get('baseline_checkpoint')
    checkpoint_valid = False
    if checkpoint and evidence_valid(root, checkpoint, checkpoint['font_sha256']):
        proof = json.loads((root/checkpoint['path']).read_text())
        checkpoint_valid = (proof.get('baseline_ready') is True
                            and proof.get('font_sha256') == checkpoint['font_sha256'])
    return dict(font_sha256=digest, phase=decisions['phase'], baseline_ready=not failures and not below,
                author_release_ready=(not failures and not pending and checkpoint_valid
                    and decisions['phase'] == 'authorial'
                    and decisions.get('selected_intensity') in ('subtle', 'moderate', 'strong')),
                technical_failures=failures, below_95_cases=len(below),
                below_95_characters=len({r['character'] for r in below}), remaining_cases=below,
                pending_decisions=pending, baseline_checkpoint_verified=checkpoint_valid)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--require', choices=['baseline', 'authorial'])
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    result = inspect()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'remaining_cases'}, ensure_ascii=False))
    if args.require and not result['baseline_ready' if args.require == 'baseline' else 'author_release_ready']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
