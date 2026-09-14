"""Render numerical text and compare ordinary/tabular shaping across axes."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from render import draw_text


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--before',type=Path,required=True)
    parser.add_argument('--after',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--text',nargs=3,help='Optional three specimen lines for another glyph family')
    parser.add_argument('--small-text',default='Мелкий текст: 19 999,99 ₽ и 99%')
    parser.add_argument('--allow-context-colon',action='store_true',help='Permit only colon to colon.case glyph selection; all advances and offsets must still match')
    parser.add_argument('--allow-advance-characters',default='',help='Explicit characters whose measured spacing is intentionally corrected')
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    paths=[args.before,args.after]
    image=Image.new('RGB',(1260,780),'#fafafa');labels=ImageDraw.Draw(image)
    for x,label in [(25,'Before'),(660,'Candidate')]:labels.text((x,15),label,fill='black')
    strings=args.text or ['0123456789  1555  9999  98765','Цена 19 999,90 ₽ — 29 сентября','9/19  99%  9.0  2029–2099']
    for row,weight in enumerate([100,400,900]):
        for column,path in enumerate(paths):
            for line,text in enumerate(strings):
                draw_text(image,path,text,25+column*635,45+row*240+line*58,32,weight,14)
            draw_text(image,path,args.small_text,25+column*635,230+row*240,16,weight,14)
    checked=0;advance_changes=0;colon_substitutions=0
    nominal=hb.Font(hb.Face(paths[0].read_bytes()))
    allowed={nominal.get_nominal_glyph(ord(ch)) for ch in args.allow_advance_characters}
    from fontTools.ttLib import TTFont
    colon_pair=(TTFont(paths[0]).getGlyphID('colon'),TTFont(paths[1]).getGlyphID('colon.case'))
    for weight in [100,250,400,600,800,900]:
        for optical in [9,14,20,28,64,128]:
            for feature in ['tnum','pnum']:
                runs=[]
                for path in paths:
                    font=hb.Font(hb.Face(path.read_bytes()))
                    font.set_variations({'wght':weight,'opsz':optical})
                    buffer=hb.Buffer();buffer.add_str(' '.join(strings));buffer.guess_segment_properties()
                    hb.shape(font,buffer,{feature:True})
                    assert all(g.codepoint for g in buffer.glyph_infos),'Missing glyph'
                    runs.append([(g.codepoint,p.x_advance,p.x_offset,p.y_offset)
                                 for g,p in zip(buffer.glyph_infos,buffer.glyph_positions)])
                assert len(runs[0])==len(runs[1])
                for a,b in zip(*runs):
                    if a[0]!=b[0]:
                        assert args.allow_context_colon and (a[0],b[0])==colon_pair,(weight,optical,feature,a,b)
                        colon_substitutions+=1
                    assert a[2:]==b[2:],(weight,optical,feature,a,b)
                    if a[1]!=b[1]:
                        assert a[0] in allowed,(weight,optical,feature,a,b)
                        advance_changes+=1
                checked+=1
    image.save(args.out/'numbers.png')
    report={'shaping_comparisons':checked,'features':['tnum','pnum'],
            'glyph_ids_advances_and_offsets_equal':advance_changes==0 and colon_substitutions==0,
            'advances_and_offsets_equal':advance_changes==0,
            'intentional_context_colon_substitutions':colon_substitutions,
            'intentional_advance_characters':args.allow_advance_characters,
            'intentional_advance_change_cases':advance_changes,'image':str(args.out/'numbers.png'),
            'fonts':[{'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]}
    (args.out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':
    main()
