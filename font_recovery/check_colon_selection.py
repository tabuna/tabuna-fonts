"""Check contextual colon selection over every pair in the required charset."""
import argparse,hashlib,json
from pathlib import Path
import uharfbuzz as hb
from fontTools.ttLib import TTFont


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--font',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();raw=a.font.read_bytes();reference=Path('/System/Library/Fonts/SFNS.ttf').read_bytes();own=hb.Font(hb.Face(raw));ref=hb.Font(hb.Face(reference));tt=TTFont(a.font);case=tt.getGlyphID('colon.case');chars=[chr(int(x[2:],16)) for x in json.loads(Path('sources/quality-scope.json').read_text())['codepoints']];failures=[];count=0
 def selected(font,text,target):
  b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(font,b);return next((g.codepoint for g in b.glyph_infos if g.cluster==1),None)==target
 for w in [100,400,900]:
  for size,opt in [(16,17),(64,28)]:
   own.set_variations(dict(wght=w,opsz=size));ref.set_variations(dict(wght=w,opsz=opt,wdth=100,GRAD=400))
   for left in chars:
    for right in chars:
     text=left+':'+right;expected=selected(ref,text,1776);actual=selected(own,text,case);count+=1
     if expected!=actual:failures.append(dict(text=text,weight=w,size=size,expected=expected,actual=actual))
 d=dict(font_sha256=hashlib.sha256(raw).hexdigest(),reference_sha256=hashlib.sha256(reference).hexdigest(),checked=count,failures=failures,scope='HarfBuzz glyph selection for every required pair; native raster and metric checks are separate.');a.out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(dict(checked=count,failures=len(failures)));assert not failures


if __name__=='__main__':main()
