#!/usr/bin/env python3
"""Regression test for contextual punctuation under numeral feature substitution."""
import argparse
import hashlib
import io
import itertools
import json
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont


def check(paths, weights, sizes):
    fonts=[TTFont(p) for p in paths]
    hbfonts=[]
    for font in fonts:
        buffer=io.BytesIO();font.flavor=None;font.save(buffer)
        hbfonts.append(hb.Font(hb.Face(buffer.getvalue())))
    def shape(index,text,features):
        buffer=hb.Buffer();buffer.add_str(text);buffer.guess_segment_properties()
        hb.shape(hbfonts[index],buffer,features)
        return [(fonts[index].getGlyphName(i.codepoint),p.x_advance,p.x_offset,p.y_offset)
                for i,p in zip(buffer.glyph_infos,buffer.glyph_positions)]
    numeric=[a+':'+b for a,b in itertools.product('0123456789',repeat=2)]
    upper=['A:B','А:Я','1:A','A:1','1:Я','Я:1','Ё:0','0:Ё','12:34:56']
    lower=['a:b','а:б','a:1','1:a','A:Я','Я:A','12: 34','12:',':']
    modes=[{}, {'tnum':True}, {'pnum':True}, {'tnum':True,'pnum':True}]
    failures=[];checks=0;parity=0;width_groups=0
    for w,o in itertools.product(weights,sizes):
        for h in hbfonts:h.set_variations({'wght':w,'opsz':o})
        for mode,calt in itertools.product(modes,[True,False]):
            features=dict(mode,calt=calt,kern=True)
            for text in numeric+upper+lower:
                expected='colon.case' if calt and text not in lower else 'colon'
                runs=[shape(i,text,features) for i in range(len(fonts))]
                if any(run != runs[0] for run in runs[1:]):
                    failures.append({'text':text,'location':[w,o],'features':features,'reason':'format mismatch'})
                parity+=len(fonts)-1
                for i,run in enumerate(runs):
                    colons=[g for g in run if g[0].startswith('colon')]
                    if not colons or any(g[0]!=expected or g[3]!=0 for g in colons):
                        failures.append({'format':str(paths[i]),'text':text,'location':[w,o],
                                         'features':features,'expected':expected,'actual':colons})
                    checks+=1
        for i in range(len(fonts)):
            widths={sum(g[1] for g in shape(i,d*2+':'+d*2+':'+d*2,{'tnum':True,'kern':True})) for d in '0123456789'}
            if len(widths)!=1:failures.append({'location':[w,o],'reason':'timer width jitter','widths':sorted(widths)})
            width_groups+=1
    return {'font_sha256':hashlib.sha256(paths[0].read_bytes()).hexdigest(),
            'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'axis_locations':len(weights)*len(sizes),'context_checks':checks,'format_comparisons':parity,
            'equal_width_timer_groups':width_groups,'failure_count':len(failures),'failures':failures[:20],
            'passed':not failures}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--fonts',type=Path,nargs='+',default=[Path('dist/TabunaSansVariable.ttf'),Path('dist/TabunaSansVariable.woff2')])
    parser.add_argument('--out',type=Path,default=Path('reports/timer-verification.json'))
    parser.add_argument('--quick',action='store_true')
    args=parser.parse_args()
    report=check(args.fonts,[400] if args.quick else [100,250,350,400,550,650,725,800,900],
                 [14] if args.quick else [9,12,14,16,18,24,28,32,48,64,72,96,128])
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='failures'},indent=2))
    raise SystemExit(0 if report['passed'] else 1)
