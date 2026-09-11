#!/usr/bin/env python3
"""Prove that the metric-storage change preserves shaping/outline tables."""
from pathlib import Path
from fontTools.ttLib import TTFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
before_path=ROOT/'references/weight-interpolation-baseline/TabunaSans-before.ttf'
after_path=ROOT/'dist/TabunaSansVariable.ttf'
a=TTFont(before_path);b=TTFont(after_path)
tags=('glyf','gvar','hmtx','avar','GDEF','GPOS','GSUB','cmap','prep','gasp')
parity={tag:a[tag].compile(a)==b[tag].compile(b) for tag in tags}
assert all(parity.values()),parity
assert 'HVAR' in a and 'HVAR' not in b
report={'beforeFontSHA256':hashlib.sha256(before_path.read_bytes()).hexdigest(),
'fontSHA256':hashlib.sha256(after_path.read_bytes()).hexdigest(),
'scope':'Binary equality of outline, variation, metrics, mapping and shaping tables; browser metrics validated separately',
'unchangedTables':parity,'beforeHasHVAR':True,'afterHasHVAR':False}
(ROOT/'proofs/advance-storage-parity.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
