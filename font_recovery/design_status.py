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


def deviations_valid(root, decisions, quality, font_sha):
    """Recompute raster scope; a declaration cannot hide an unrelated change."""
    evidence = decisions.get('authorial_deviations')
    if not evidence or not evidence_valid(root, evidence, font_sha):
        return False
    report = json.loads((root/evidence['path']).read_text())
    checkpoint = decisions.get('baseline_checkpoint') or {}
    baseline_ref = report.get('baseline_quality') or {}
    if (report.get('font_sha256') != font_sha
            or report.get('reviewed') is not True
            or not baseline_ref.get('path')
            or not evidence_valid(root, baseline_ref, checkpoint.get('font_sha256'))):
        return False
    baseline = json.loads((root/baseline_ref['path']).read_text())
    if (baseline.get('font_sha256') != checkpoint.get('font_sha256')
            or not baseline.get('repeat_verified')):
        return False
    key = lambda r: (r['codepoint'], r['weight'], r['size'])
    before = {key(r): r for r in baseline['all_cases']}
    current = {key(r): r for r in quality['all_cases']}
    if (len(before) != len(baseline['all_cases']) or before.keys() != current.keys()
            or any(r['mask_iou'] is not None and r['mask_iou'] < .95
                   for r in before.values())):
        return False
    accepted = {d['id'] for d in decisions['decisions'] if d['status'] == 'accepted'}
    scope = report.get('glyph_decisions', {})
    if any(not ids or not set(ids) <= accepted for ids in scope.values()):
        return False
    fields = ('mask_iou', 'fp', 'fn', 'custom_fallback', 'reference_fallback')
    for case, row in current.items():
        if any(row[field] != before[case][field] for field in fields):
            if row['codepoint'] not in scope:
                return False
    return True


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
    deviations_verified = deviations_valid(root, decisions, quality, digest)
    audit_failures = []
    digit_path = root/'reports/digit-verification.json'
    digit_check = json.loads(digit_path.read_text()) if digit_path.exists() else {}
    if (digit_check.get('font_sha256') != digest or digit_check.get('passed') is not True
            or digit_check.get('failures') != []
            or digit_check.get('cases', {}).get('tnum', 0) < 15300):
        audit_failures.append('tabular collision and equal-width verification is missing, stale or failed')
    timer_path = root/'reports/timer-verification.json'
    timer_check = json.loads(timer_path.read_text()) if timer_path.exists() else {}
    if (timer_check.get('font_sha256') != digest or timer_check.get('passed') is not True
            or timer_check.get('failure_count') != 0
            or timer_check.get('axis_locations', 0) < 117
            or timer_check.get('context_checks', 0) < 220896):
        audit_failures.append('contextual timer verification is missing, stale or failed')
    return dict(font_sha256=digest, phase=decisions['phase'], baseline_ready=not failures and not below,
                author_release_ready=(not failures and not pending and not audit_failures and checkpoint_valid
                    and deviations_verified
                    and decisions['phase'] == 'authorial'
                    and decisions.get('selected_intensity') in ('subtle', 'moderate', 'strong')),
                technical_failures=failures, audit_failures=audit_failures, below_95_cases=len(below),
                below_95_characters=len({r['character'] for r in below}), remaining_cases=below,
                pending_decisions=pending, baseline_checkpoint_verified=checkpoint_valid,
                authorial_deviations_verified=deviations_verified)


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
