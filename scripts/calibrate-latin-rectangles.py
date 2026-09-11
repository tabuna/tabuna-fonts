#!/usr/bin/env python3
"""Fit scalar stroke positions to our fixed polygon constructions.

Regular retains saved own source coordinates. No reference outlines or font
binary tables are read. Raster scan edges determine extreme stroke dimensions.
"""
from pathlib import Path
from PIL import Image
import hashlib,json,importlib.util
from latin_rectangles import polygon
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rect_fit',ROOT/'scripts/calibrate-rectilinear.py')
rect_fit=importlib.util.module_from_spec(spec);spec.loader.exec_module(rect_fit)
CHARS='IHEFLЕІ'
BASE=ROOT/'references/latin-rectangles-baseline'


def measure(folder,record,data):
    im=Image.open(folder/record['system']['file']).convert('L');pix=im.load()
    ox,oy=data['originPixels'];scale=data['pixelScale'];size=data['pointSize']
    left,bottom,width,height=record['system']['inkBounds'];right=left+width;top=bottom+height
    xl=int(ox+left*scale)-3;xr=int(ox+right*scale)+4
    yt=int(oy-top*scale)-3;yb=int(oy-bottom*scale)+4
    def row(y):
        py=round(oy-y*scale)
        return [(v+xl-ox)/scale for v in rect_fit.edges([1-pix[x,py]/255 for x in range(xl,xr)])]
    def column(x):
        px=round(ox+x*scale)
        return [(oy-v-yt)/scale for v in rect_fit.edges([1-pix[px,y]/255 for y in range(yt,yb)])]
    ch={'Е':'E','І':'I'}.get(record['character'],record['character'])
    p={'left':left,'right':right,'bottom':bottom,'top':top}
    if ch!='I':
        stems=row(bottom+height*.7)
        assert len(stems)==(4 if ch=='H' else 2),(record['character'],stems)
        p['stemRight']=stems[1]
        if ch=='H':
            p['rightStemLeft']=stems[2]
            bars=column((stems[1]+stems[2])/2)
            assert len(bars)==2,(record['character'],bars)
            p['middleTop'],p['middleBottom']=bars
        else:
            bars=column(left+width*.6)
            assert len(bars)=={'E':6,'F':4,'L':2}[ch],(record['character'],bars)
            if ch=='L':p['bottomTop']=bars[0]
            else:
                p['topBottom'],p['middleTop'],p['middleBottom']=bars[1:4]
                p['middleRight']=row((bars[2]+bars[3])/2)[-1]
                if ch=='E':
                    p['bottomTop']=bars[4]
                    p['bottomRight']=row((bars[4]+bars[5])/2)[-1]
    return {k:v*1000/size for k,v in p.items()}


def main():
    regular_path=BASE/'regular-source.json';regular=json.loads(regular_path.read_text())
    output={'method':'Fixed authored polygon recipes; scalar native axis-reference raster scans for 100/900; own saved Regular source',
            'regularSource':str(regular_path.relative_to(ROOT)),
            'regularSourceSHA256':hashlib.sha256(regular_path.read_bytes()).hexdigest(),
            'weights':[100,400,900],'glyphs':{ch:{'400':regular['glyphs'][ch]} for ch in CHARS},'runs':[]}
    for weight in (100,900):
        for size,mode in [(16,'text'),(64,'display')]:
            folder=BASE/f'{weight}-{size}';path=folder/'render-settings.json';data=json.loads(path.read_text())
            assert data['weight']==weight and data['referenceWeightMode']=='axis'
            assert ''.join(r['character'] for r in data['records'])==CHARS
            for record in data['records']:
                assert record['system']['renderedFonts']==[data['systemPostScriptName']]
                ch=record['character'];p=measure(folder,record,data)
                points=polygon(ch,p)
                assert len(points)==len(regular['glyphs'][ch][mode]['points'])
                output['glyphs'][ch].setdefault(str(weight),{})[mode]={'points':points,'advance':record['system']['advance']*1000/size}
            output['runs'].append({'report':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'weight':weight,'pointSize':size,'os':data['os']})
    (ROOT/'sources/latin-rectangles.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print('Calibrated seven original polygon glyphs; saved Regular source retained.')
if __name__=='__main__':main()
