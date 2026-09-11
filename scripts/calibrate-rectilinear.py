#!/usr/bin/env python3
"""Measure scalar rectangles of our explicit Cyrillic stroke constructions.

No vector paths or reference font tables are read. Rows and columns through
straight strokes determine dimensions; the authored polygon recipes are fixed.
"""
from pathlib import Path
from PIL import Image
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
CHARS='ПпШшЦцЩщТтНн'


def edges(values):
    out=[]
    for i in range(1,len(values)):
        if (values[i-1]>=.5)!=(values[i]>=.5):
            lo=max(0,i-2);hi=min(len(values),i+2);area=sum(values[lo:hi])
            out.append(hi-area if values[i]>=.5 else lo+area)
    return out


def measure(folder,record,settings):
    im=Image.open(folder/record['system']['file']).convert('L');pix=im.load()
    ox,oy=settings['originPixels'];scale=settings['pixelScale'];size=settings['pointSize']
    left,bottom,width,height=record['system']['inkBounds'];right=left+width;top=bottom+height
    xl=int(ox+left*scale)-3;xr=int(ox+right*scale)+4
    yt=int(oy-top*scale)-3;yb=int(oy-bottom*scale)+4
    ch=record['character'].upper()
    def row(y):
        py=round(oy-y*scale)
        return [(v+xl-ox)/scale for v in edges([1-pix[x,py]/255 for x in range(xl,xr)])]
    stem=row(top*.7);count=1 if ch=='Т' else 3 if ch in 'ШЩ' else 2
    assert len(stem)==count*2,(record['character'],settings['weight'],stem)
    x=(left+stem[0])/2 if ch=='Т' else (stem[1]+stem[2])/2
    px=round(ox+x*scale)
    vertical=edges([1-pix[px,y]/255 for y in range(yt,yb)])
    assert len(vertical)==2,(record['character'],vertical)
    barTop,barBottom=[(oy-v-yt)/scale for v in vertical]
    result={'left':left,'right':right,'top':top,'bottom':0.,'barBottom':barBottom,'barTop':barTop,
            'stems':[[a,b] for a,b in zip(stem[::2],stem[1::2])],
            'advance':record['system']['advance']}
    if ch in 'ЦЩ':
        tail=row(bottom*.5);assert len(tail)==2
        result['tail']=[tail[0],tail[1],bottom]
    def units(v):return [units(x) for x in v] if isinstance(v,list) else v*1000/size
    return {k:units(v) for k,v in result.items()}


def main():
    output={'method':'Scalar stroke dimensions from native raster rows/columns; fixed original polygon recipes',
            'weights':[100,400,900],'glyphs':{},'runs':[]}
    for weight in (100,400,900):
        for size,mode in [(16,'text'),(64,'display')]:
            folder=ROOT/'references/css-weights-baseline/rectilinear'/f'{weight}-{size}'
            report=folder/'render-settings.json';data=json.loads(report.read_text())
            assert data['weight']==weight
            assert data['referenceWeightMode']=='axis'
            for record in data['records']:
                assert record['system']['renderedFonts']==[data['systemPostScriptName']]
                params=measure(folder,record,data)
                output['glyphs'].setdefault(record['character'],{}).setdefault(str(weight),{})[mode]=params
            output['runs'].append({'report':str(report.relative_to(ROOT)),'sha256':hashlib.sha256(report.read_bytes()).hexdigest(),
                                   'system':data['systemPostScriptName'],'weight':weight,'pointSize':size,'os':data['os']})
    (ROOT/'sources/rectilinear.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(f'Measured {len(output["glyphs"])} glyphs at three weights and two optical sizes.')
if __name__=='__main__':main()
