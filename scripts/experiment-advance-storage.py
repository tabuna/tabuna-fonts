#!/usr/bin/env python3
"""Reproduce the isolated 0.690 HVAR-versus-phantom browser experiment."""
from pathlib import Path
from fontTools.ttLib import TTFont
import subprocess,hashlib,json
import ots
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'references/weight-interpolation-baseline/TabunaSans-before.ttf'
folder=ROOT/'build/weight-interpolation';folder.mkdir(exist_ok=True)
f=TTFont(base,recalcTimestamp=False);assert 'HVAR' in f
before={tag:f[tag].compile(f) for tag in ('glyf','gvar','hmtx','avar','GDEF','GPOS','GSUB')}
del f['HVAR']
f.save(folder/'TabunaSans-no-hvar.ttf')
f.flavor='woff2';f.save(folder/'TabunaSans-no-hvar.woff2')
assert all(f[tag].compile(f)==value for tag,value in before.items())
subprocess.run([str(Path(ots.__file__).with_name('ots-sanitize')),str(folder/'TabunaSans-no-hvar.ttf'),str(folder/'TabunaSans-no-hvar-sanitized.ttf')],check=True)
s=(ROOT/'weight-calibration.html').read_text().replace("new Worker('scripts/canvas-worker.js')","new Worker('/scripts/canvas-worker.js')").replace('`dist/TabunaSansVariable.woff2?v=${Date.now()}`','`/build/weight-interpolation/TabunaSans-no-hvar.woff2?v=${Date.now()}`').replace("'proofs/reference-weight-selection.json'","'/proofs/reference-weight-selection.json'")
(folder/'no-hvar.html').write_text(s)
(folder/'with-hvar.html').write_text(s.replace('/build/weight-interpolation/TabunaSans-no-hvar.woff2','/references/weight-interpolation-baseline/TabunaSans-before.woff2'))
s=(ROOT/'web-calibration.html').read_text().replace('dist/TabunaSansVariable.woff2','/build/weight-interpolation/TabunaSans-no-hvar.woff2').replace('build/TabunaSans-sanitized.ttf','/build/weight-interpolation/TabunaSans-no-hvar-sanitized.ttf').replace("new Worker('scripts/canvas-worker.js')","new Worker('/scripts/canvas-worker.js')").replace("'sources/text-validation.json'","'/sources/text-validation.json'")
(folder/'no-hvar-layout.html').write_text(s)
print(json.dumps({'beforeSHA256':hashlib.sha256(base.read_bytes()).hexdigest(),'candidateWOFF2SHA256':hashlib.sha256((folder/'TabunaSans-no-hvar.woff2').read_bytes()).hexdigest(),'currentDistUnchanged':True},indent=2))
