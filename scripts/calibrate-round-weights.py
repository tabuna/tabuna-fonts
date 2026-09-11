#!/usr/bin/env python3
"""Extend our round construction to extreme weights; retain Regular sources."""
from pathlib import Path
import hashlib, importlib.util, json

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('round_fit',ROOT/'scripts/calibrate-rounds.py')
shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)


def main():
    data={'method':'Original four-cubic round model; extreme weights fitted from scalar raster profiles; Regular retained from our own UFO masters',
          'weights':[100,400,900],'glyphs':{},'runs':[]}
    legacy=json.loads((ROOT/'references/round-weights-baseline/rounds-regular.json').read_text())['glyphs']
    regular=json.loads((ROOT/'references/round-weights-baseline/regular-master-geometry.json').read_text())['glyphs']
    for size,mode in ((16,'text'),(28,'display')):
        for ch,key in [('o','o'),('O','O'),('о','uni043E'),('О','uni041E')]:
            p={**regular[ch][mode],
               'outerHandles':legacy[ch][mode]['outerHandles'],'innerHandles':legacy[ch][mode]['innerHandles']}
            data['glyphs'].setdefault(ch,{}).setdefault('400',{})[mode]=p
    for weight in (100,900):
        for size,mode in ((16,'text'),(64,'display')):
            folder=ROOT/f'references/css-weights-baseline/round-weights/{weight}-{size}'
            path=folder/'render-settings.json';settings=json.loads(path.read_text());errors={}
            assert settings['weight']==weight
            assert settings['referenceWeightMode']=='axis'
            for rec in settings['records']:
                assert rec['system']['renderedFonts']==[settings['systemPostScriptName']]
                result,error=shared.fit(folder/rec['system']['file'],rec,settings)
                l,b,w,h=rec['system']['inkBounds'];unit=1000/size
                il,ib,ir,it=result['inner']
                p={'bounds':[[l*unit,b*unit,(l+w)*unit,(b+h)*unit],
                             [(l+il*w)*unit,(b+ib*h)*unit,(l+ir*w)*unit,(b+it*h)*unit]],
                   'advance':rec['system']['advance']*unit,
                   'outerHandles':result['outerHandles'],'innerHandles':result['innerHandles']}
                data['glyphs'].setdefault(rec['character'],{}).setdefault(str(weight),{})[mode]=p
                errors[rec['character']]=error
            data['runs'].append({'report':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'fitNormalizedRMS':errors})
            print(weight,mode,'measured',flush=True)
    (ROOT/'sources/round-weights.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
