"""Bounded native screening of scalar parameters in an authored glyph family.

Writes candidates and measurements under build/. Never promotes a candidate
to sources/ or dist/: ordinary builds and independent audits do that separately.
"""
import argparse
import copy
import importlib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from font_recovery.native_refinement import AuthoredPreview, replace_masters
from font_recovery.scratch import require_free_space, retain_trial_artifacts
from font_recovery.native_batch import renderer


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--font', type=Path, default=ROOT/'dist/TabunaSansVariable.ttf')
    ap.add_argument('--module', required=True)
    ap.add_argument('--normalized', action='store_true', help='Map a normalized construction through its bounds')
    ap.add_argument('--reverse-construction', action='store_true', help='Use the mirrored form of a shared construction')
    ap.add_argument('--ellipse-dot', action='store_true', help='Append the separate authored elliptical dot')
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--profile', required=True, help='Dot-separated path to the weight profiles')
    ap.add_argument('--character', required=True)
    ap.add_argument('--weight', type=int, choices=[100, 400, 900], required=True)
    ap.add_argument('--all-weights', action='store_true', help='Screen all nine weights during joint-master refinement')
    ap.add_argument('--optical', choices=['text', 'display'], required=True)
    ap.add_argument('--baseline', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--parameters', default='.*', help='Regex selecting semantic parameter paths')
    ap.add_argument('--unit-parameters', default=r'(^|\.)bounds\.',
                    help='Regex for coordinates on the 1000-unit design grid; other parameters are dimensionless')
    ap.add_argument('--steps', default='.001,.0005,.00025')
    ap.add_argument('--gray-tolerance', type=float, default=.003,
                    help='Secondary grayscale decrease allowed in screening; any decrease still requires visual review')
    ap.add_argument('--resume', type=Path, help='Continue from the best parameters of an earlier screening')
    ap.add_argument('--preserve-passed', action='store_true',
                    help='Keep resumed cases that reached 95% above that target')
    ap.add_argument('--coupled', type=json.loads, help='JSON list of {weight,path,scale} for a coordinated semantic change; requires --all-weights')
    args = ap.parse_args()
    assert args.out.resolve().is_relative_to((ROOT/'build/font-recovery').resolve())
    assert not (args.out/'result.json').exists(), 'Use a new output directory; preserve existing evidence'
    args.out.mkdir(parents=True, exist_ok=True)
    require_free_space(ROOT)
    native_renderer = renderer()
    font_sha = hashlib.sha256(args.font.read_bytes()).hexdigest()
    source_sha = hashlib.sha256(args.source.read_bytes()).hexdigest()
    font = TTFont(args.font, recalcTimestamp=False)
    key = font.getBestCmap()[ord(args.character)]
    profiles = json.loads(args.source.read_text())
    for name in args.profile.split('.'):
        profiles = profiles[name]
    model = importlib.import_module(args.module)
    def construction(profile):
        drawing = model.construction(profile, reverse=True) if args.reverse_construction else model.construction(profile)
        if args.normalized:
            from geometry import Drawing
            left, bottom, right, top = profile['bounds']
            full = Drawing()
            drawing.replay(full.pen, (right-left, 0, 0, top-bottom, left, bottom))
            drawing = full
        if args.ellipse_dot:
            drawing.ellipse(*profile['dot'])
        return drawing
    preview = AuthoredPreview(font, key, construction)
    original = preview.masters(profiles)
    replace_masters(font, key, original, original)
    weights = list(range(100, 901, 100) if args.all_weights else
                   range(100, 400, 100) if args.weight == 100 else
                   range(500, 901, 100) if args.weight == 900 else range(100, 901, 100))
    size = 16 if args.optical == 'text' else 64
    references = {}
    for w in weights:
        folder = args.baseline/f'wght-{w}'/str(size)
        settings = json.loads((folder/'render-settings.json').read_text())
        assert settings['fontSHA256'] == font_sha
        references[w] = np.array(Image.open(folder/f'{ord(args.character):04X}-system.png').convert('L'))
    paths = []

    def walk(value, path=()):
        if isinstance(value, dict):
            for k, v in value.items():
                if k != 'advance':
                    walk(v, path+(k,))
        elif isinstance(value, list):
            for k, v in enumerate(value):
                walk(v, path+(k,))
        elif re.search(args.parameters, '.'.join(map(str, path))):
            paths.append(path)

    walk(profiles[str(args.weight)][args.optical])
    if args.coupled:
        assert args.all_weights
        paths = [None]
    assert paths, 'No parameter selected'
    trials = []

    def evaluate(p, change=None):
        require_free_space(ROOT)
        number = len(trials)
        folder = args.out/f'trial-{number:04d}'
        folder.mkdir(exist_ok=True)
        masters = preview.masters(p)
        candidate = replace_masters(font, key, original, masters)
        candidate.save(folder/'font.ttf')
        candidate.close()
        del candidate
        # FontTools tables can form cycles; release discarded trial fonts
        # before rendering so long searches do not grow memory and swap.
        import gc
        gc.collect()
        jobs = [['render-pairs', str((folder/'font.ttf').resolve()), str((folder/str(w)).resolve()),
                 str(size), args.character, '2', str(w), 'axis'] for w in weights]
        (folder/'jobs.json').write_text(json.dumps(jobs))
        subprocess.run([str(native_renderer), str(folder/'jobs.json')],
                       check=True, stdout=subprocess.DEVNULL)
        cases = []
        for w, ref in references.items():
            own = np.array(Image.open(folder/str(w)/f'{ord(args.character):04X}-tabuna.png').convert('L'))
            assert np.array_equal(np.array(Image.open(folder/str(w)/f'{ord(args.character):04X}-system.png').convert('L')), ref)
            a, b = own < 128, ref < 128
            ink, reference_ink = 255-own.astype(float), 255-ref.astype(float)
            cases.append(dict(weight=w, size=size, mask_iou=float((a & b).sum()/(a | b).sum()),
                              ink_iou=float(np.minimum(ink, reference_ink).sum()/np.maximum(ink, reference_ink).sum()),
                              fp=int((a & ~b).sum()), fn=int((~a & b).sum())))
        row = dict(trial=number, cases=cases, profiles=copy.deepcopy(p), change=change)
        trials.append(row)
        return row

    baseline = best = evaluate(profiles)
    floors = {c['weight']: c['mask_iou'] for c in baseline['cases']}
    assert 0 <= args.gray_tolerance <= .005
    gray_floors = {c['weight']: c['ink_iou']-args.gray_tolerance for c in baseline['cases']}

    def valid(row):
        return all(c['mask_iou'] >= floors[c['weight']] and c['ink_iou'] >= gray_floors[c['weight']]
                   for c in row['cases'])

    def score(row):
        return (-sum(max(0, .95-c['mask_iou']) for c in row['cases']),
                sum(c['mask_iou'] for c in row['cases']), sum(c['ink_iou'] for c in row['cases']))

    if args.resume:
        resumed = json.loads(args.resume.read_text())['best']['profiles']
        # Cross-weight continuation must screen the whole weight interval.
        if args.weight != 400 and not args.all_weights:
            assert all(resumed[str(w)] == profiles[str(w)] for w in (100, 400, 900)
                       if w != args.weight), 'Cross-weight continuation requires --weight 400'
        other_optical = 'display' if args.optical == 'text' else 'text'
        assert all(resumed[str(w)][other_optical] == profiles[str(w)][other_optical]
                   for w in (100, 400, 900)), 'Opposite optical endpoints require a separate audit'
        trial = evaluate(resumed, 'resume')
        assert valid(trial)
        best = trial
        if args.preserve_passed:
            for case in trial['cases']:
                if case['mask_iou'] >= .95:
                    floors[case['weight']] = max(floors[case['weight']], .95)
    print('baseline', key, baseline['cases'], 'parameters', len(paths), flush=True)

    def save():
        (args.out/'result.json').write_text(json.dumps(dict(screening_only=True, source=str(args.source),
            source_sha256=source_sha, font_sha256=font_sha,
            character=args.character, quadratic_counts=preview.counts, gray_tolerance=args.gray_tolerance,
            baseline=baseline, best=best, trials=trials), ensure_ascii=False, indent=2)+'\n')
        retain_trial_artifacts(args.out, {0, best['trial']})

    for step in map(float, args.steps.split(',')):
        for path in paths:
            current = best
            for direction in (-1, 1):
                p = copy.deepcopy(current['profiles'])
                edits = args.coupled or [dict(weight=args.weight, path=path, scale=1)]
                # Bounds and explicit stem rectangles use the 1000-unit design
                # grid; normalized radii/handles/positions remain dimensionless.
                for edit in edits:
                    target_path = edit['path']
                    v = p[str(edit['weight'])][args.optical]
                    for field in target_path[:-1]:
                        v = v[field]
                    units = 1000 if re.search(args.unit_parameters, '.'.join(map(str, target_path))) else 1
                    v[target_path[-1]] += direction*step*units*edit['scale']
                candidate = evaluate(p, dict(edits=edits, step=direction*step))
                if valid(candidate) and score(candidate) > score(best):
                    best = candidate
                    print('best', key, best['change'], score(best), flush=True)
            save()
            if score(best)[0] == 0:
                print('target reached in screening', key, best['cases'], flush=True)
                return
        print('sweep', key, step, score(best), flush=True)
    save()


if __name__ == '__main__':
    main()
