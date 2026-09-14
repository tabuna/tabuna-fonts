"""Validate compiled geometry across the weight axis and report missing coverage."""
import argparse
import json
import hashlib
from pathlib import Path

import pathops
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]


def validate(font):
    glyph_set = font.getGlyphSet()
    results = []
    issues = []
    for name in font.getGlyphOrder():
        advance, _ = font['hmtx'][name]
        if advance < 0:
            issues.append({'glyph': name, 'problem': 'negative advance'})
        recording = RecordingPen()
        glyph_set[name].draw(recording)
        current = None
        for operation, points in recording.value:
            if operation == 'moveTo':
                current = points[0]
            elif operation in ('lineTo', 'qCurveTo', 'curveTo'):
                if not any(point != current for point in points):
                    issues.append({'glyph': name, 'problem': 'degenerate segment'})
                current = points[-1]
        path = pathops.Path()
        glyph_set[name].draw(path.getPen())
        area = path.area
        contours = len(list(path.contours))
        path.simplify()
        tolerance = max(0.001, abs(area) * 1e-6)
        if abs(path.area - area) > tolerance:
            issues.append({'glyph': name, 'problem': 'overlap/self-intersection changes fill area',
                           'area_difference': path.area - area})
        if len(list(path.contours)) != contours:
            issues.append({'glyph': name, 'problem': 'simplification changes contour topology'})
        if contours:
            if path.area <= 0:
                issues.append({'glyph': name, 'problem': 'non-positive filled area'})
        results.append({'glyph': name, 'contours': contours, 'area': area})
    return results, issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', type=Path, default=ROOT / 'build/generated-font/tabuna-sans-variable/TabunaSansVariable.ttf')
    parser.add_argument('--out', type=Path, default=ROOT / 'build/font-recovery/research-v2/validation.json')
    parser.add_argument('--development', action='store_true',
                        help='Allow incomplete alphabet for geometry experiments only.')
    args = parser.parse_args()
    font = TTFont(args.font)
    samples = []
    if 'fvar' in font:
        axis = next(axis for axis in font['fvar'].axes if axis.axisTag == 'wght')
        weights = sorted({axis.minValue, axis.maxValue, *[weight for weight in
                         [100, 175, 250, 325, 400, 500, 600, 700, 800, 850, 900]
                         if axis.minValue <= weight <= axis.maxValue]})
    else:
        weights = [None]
    for weight in weights:
        instance = instantiateVariableFont(font, {'wght': weight}, inplace=False) if weight else font
        glyphs, issues = validate(instance)
        samples.append({'weight': weight, 'glyphs': glyphs, 'issues': issues})
    geometry_passed = not any(sample['issues'] for sample in samples)
    charset = json.loads((ROOT / 'sources/charset.json').read_text())
    missing = [row for row in charset if ord(row['character']) not in font.getBestCmap()]
    alphabet = json.loads((ROOT / 'font_recovery/data/required-alphabet.json').read_text())
    missing_alphabet = [row for row in alphabet if ord(row['character']) not in font.getBestCmap()]
    result = {
        'font': str(args.font),
        'font_sha256': hashlib.sha256(args.font.read_bytes()).hexdigest(),
        'geometry_checks_passed': geometry_passed,
        'method': 'Compiled segments; Skia simplify area and topology invariance across the declared weight range',
        'samples': samples,
        'missing_required_characters': missing,
        'alphabet_required_count': len(alphabet),
        'alphabet_present_count': len(alphabet) - len(missing_alphabet),
        'missing_alphabet_characters': missing_alphabet,
        'alphabet_coverage_passed': not missing_alphabet,
        'full_release_ready': False,
        'limitations': 'Coverage, shaping, spacing, optical size and full raster acceptance still required.',
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'geometry_checks_passed': geometry_passed, 'sample_count': len(samples),
                      'missing_characters': len(missing),
                      'missing_alphabet_characters': len(missing_alphabet)}, ensure_ascii=False))
    if missing_alphabet and not args.development:
        parser.exit(1, 'Incomplete alphabet: ' + ''.join(row['character'] for row in missing_alphabet)
                    + '\nGeometry checks alone do not establish font readiness.\n')
    if not geometry_passed:
        parser.exit(1, f'Geometry acceptance failed; full diagnostics saved to {args.out}\n')


if __name__ == '__main__':
    main()
