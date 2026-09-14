"""Check that a replacement retains the original font's public capabilities.

This is a necessary release gate, not proof of visual quality. Missing axes,
characters and shaping features are reported together, rather than accepting
an attractive subset as a replacement for the user's existing font.
"""
import argparse
import hashlib
import json
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]


def capabilities(path):
    font = TTFont(path)
    axes = {axis.axisTag: [axis.minValue, axis.defaultValue, axis.maxValue]
            for axis in font['fvar'].axes} if 'fvar' in font else {}
    features = {}
    for tag in ('GSUB', 'GPOS'):
        features[tag] = sorted({record.FeatureTag for record in font[tag].table.FeatureList.FeatureRecord}) if tag in font and font[tag].table.FeatureList else []
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'coverage': sorted(font.getBestCmap()), 'axes': axes, 'features': features}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', type=Path, default=ROOT / 'build/generated-font/tabuna-sans-complete/TabunaSansVariable.ttf')
    parser.add_argument('--baseline', type=Path, default=ROOT / 'build/font-recovery/checkpoints/checkpoint-000/dist/TabunaSansVariable.ttf')
    parser.add_argument('--out', type=Path, default=ROOT / 'build/font-recovery/reports/compatibility.json')
    args = parser.parse_args()
    before, after = capabilities(args.baseline), capabilities(args.font)
    missing = sorted(set(before['coverage']) - set(after['coverage']))
    issues = []
    if missing:
        issues.append(f'Missing {len(missing)} of {len(before["coverage"])} baseline characters')
    for tag, limits in before['axes'].items():
        if after['axes'].get(tag) != limits:
            issues.append(f'Axis {tag}: expected {limits}, found {after["axes"].get(tag)}')
    for table, tags in before['features'].items():
        absent = sorted(set(tags) - set(after['features'][table]))
        if absent:
            issues.append(f'{table}: missing {", ".join(absent)}')
    report = {'baseline': before, 'candidate': after,
              'missing_characters': [f'U+{codepoint:04X}' for codepoint in missing],
              'capability_parity_passed': not issues, 'issues': issues,
              'visual_acceptance': 'Separate full raster and text audits required'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'capability_parity_passed': not issues, 'issues': issues}, ensure_ascii=False))
    if issues:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
