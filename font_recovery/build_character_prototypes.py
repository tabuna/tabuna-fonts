"""Build and verify isolated character variants without replacing dist/."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ('subtle', 'moderate', 'strong')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--jobs', type=int, choices=(1, 2, 3), default=1)
    args = parser.parse_args()
    out = args.out.resolve()
    allowed = (ROOT/'build/character-prototypes').resolve()
    if not out.is_relative_to(allowed) or out == allowed or out.exists():
        parser.error('--out must be a new directory inside build/character-prototypes')
    if shutil.disk_usage(ROOT).free < 2.5*2**30:
        parser.error('At least 2.5 GiB free space is required')
    decisions = json.loads((ROOT/'sources/design-decisions.json').read_text())
    checkpoint = decisions.get('baseline_checkpoint')
    if not checkpoint:
        parser.error('Preserve the 95% baseline before building authorial variants')
    proof_path = (ROOT/checkpoint['path']).resolve()
    if not proof_path.is_relative_to(ROOT):
        parser.error('Checkpoint must belong to this project')
    proof_bytes = proof_path.read_bytes()
    proof = json.loads(proof_bytes)
    if (hashlib.sha256(proof_bytes).hexdigest() != checkpoint['sha256']
            or not proof.get('baseline_ready')
            or proof['font_sha256'] != checkpoint['font_sha256']):
        parser.error('Baseline checkpoint is invalid')
    out.mkdir(parents=True)
    for variant in VARIANTS:
        destination = out/variant
        destination.mkdir()
        for folder in ('scripts', 'sources', 'font_recovery'):
            shutil.copytree(ROOT/folder, destination/folder,
                ignore=shutil.ignore_patterns('*.ufo', '*.designspace', '__pycache__', '*.pyc'))
        for name in ('requirements.lock', 'OFL.txt'):
            shutil.copy2(ROOT/name, destination/name)
        path = destination/'sources/character.json'
        config = json.loads(path.read_text()); config['intensity'] = variant
        path.write_text(json.dumps(config, ensure_ascii=False, indent=2)+'\n')

    model_hashes = {hashlib.sha256((out/v/'scripts/character.py').read_bytes()).hexdigest()
                    for v in VARIANTS}
    if len(model_hashes) != 1:
        raise RuntimeError('Model changed during prototype export; restart with a new output directory')

    def build(variant):
        directory = out/variant
        for script, log in [('build.py', 'build.log'), ('verify.py', 'verification.json')]:
            with (directory/log).open('w') as stream:
                subprocess.run([sys.executable, str(directory/'scripts'/script)],
                               cwd=directory, stdout=stream, stderr=subprocess.STDOUT, check=True)
        hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (directory/'dist').glob('*') if p.suffix in ('.ttf', '.woff2')}
        print(f'{variant}: built and verified', flush=True)
        return variant, hashes

    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        results = dict(executor.map(build, VARIANTS))
    manifest = dict(baseline_font_sha256=checkpoint['font_sha256'],
                    model_sha256=next(iter(model_hashes)),
                    variants=results, status='built-and-verified', selection=None)
    (out/'prototypes.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()
