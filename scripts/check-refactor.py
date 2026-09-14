#!/usr/bin/env python3
"""Build in an isolated directory and require byte-identical release fonts."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, default=ROOT / 'dist',
                        help='Directory containing the fonts that must be preserved')
    args = parser.parse_args()
    baseline = {name: (args.baseline / name).read_bytes()
                for name in ('TabunaSansVariable.ttf', 'TabunaSansVariable.woff2')}
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='refactor-check-', dir=build))
    for directory in ('scripts', 'sources'):
        shutil.copytree(ROOT / directory, work / directory,
                        ignore=shutil.ignore_patterns('__pycache__'))
    with (work / 'build.log').open('w') as log:
        result = subprocess.run([sys.executable, str(work / 'scripts/build.py')],
                                stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise SystemExit(f'Build failed; see {work / "build.log"}')
    comparisons = []
    for name, before in baseline.items():
        after = (work / 'dist' / name).read_bytes()
        comparisons.append({'file': name, 'byte_identical': before == after,
                            'baseline_sha256': hashlib.sha256(before).hexdigest(),
                            'rebuilt_sha256': hashlib.sha256(after).hexdigest()})
    passed = all(row['byte_identical'] for row in comparisons)
    report = work / 'comparison.json'
    report.write_text(json.dumps({'passed': passed, 'files': comparisons}, indent=2) + '\n')
    print(json.dumps({'passed': passed, 'report': str(report)}, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
