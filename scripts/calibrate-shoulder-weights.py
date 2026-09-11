#!/usr/bin/env python3
"""Fit original n/h/m shoulder recipes at CSS weights 100/900."""
from pathlib import Path
import json,hashlib,importlib.util
from shoulders import construction
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'references/shoulder-weights-baseline'
spec=importlib.util.spec_from_file_location('shoulder_fit',ROOT/'scripts/calibrate-shoulders.py')
fitter=importlib.util.module_from_spec(spec);spec.loader.exec_module(fitter)
regular_path=BASE/'regular-source.json';regular=json.loads(regular_path.read_text())
result={'method':'Own fixed shoulder recipes fitted to scalar axis-reference raster profiles; own Regular cubic coordinates retained',
        'weights':[100,400,900],'regularSource':str(regular_path.relative_to(ROOT)),
        'regularSourceSHA256':hashlib.sha256(regular_path.read_bytes()).hexdigest(),
        'glyphs':{ch:{'400':regular['glyphs'][ch]} for ch in 'nhm'},'runs':[],'fitParameters':{}}
for weight in (100,900):
    for size,mode in [(16,'text'),(64,'display')]:
        folder=BASE/f'{weight}-{size}';path=folder/'render-settings.json';data=json.loads(path.read_text())
        assert data['weight']==weight and data['referenceWeightMode']=='axis'
        assert ''.join(r['character'] for r in data['records'])=='nhm'
        for r in data['records']:
            assert r['system']['renderedFonts']==[data['systemPostScriptName']]
            ch=r['character'];p=(fitter.fit_m if ch=='m' else fitter.fit)(folder,r,data)
            pen=construction(p)
            assert [op for op,_ in pen.value]==[op for op,_ in regular['glyphs'][ch][mode]['commands']]
            result['glyphs'][ch].setdefault(str(weight),{})[mode]={'commands':pen.value,'advance':r['system']['advance']*1000/size}
            result['fitParameters'].setdefault(ch,{}).setdefault(str(weight),{})[mode]=p
            print(ch,weight,mode,{k:round(v['rms'],4) for k,v in p.items() if isinstance(v,dict)},flush=True)
        result['runs'].append({'report':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'weight':weight,'size':size,'os':data['os']})
(ROOT/'sources/shoulder-weights.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
