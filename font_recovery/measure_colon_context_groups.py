"""Measure contextual colon membership separately for Latin and Cyrillic."""
import argparse,json
from pathlib import Path
import uharfbuzz as hb


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();d=json.loads(a.base.read_text());raw=Path('/System/Library/Fonts/SFNS.ttf').read_bytes();chars=[chr(int(x[2:],16)) for x in json.loads(Path('sources/quality-scope.json').read_text())['codepoints']];evidence=[]
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   f=hb.Font(hb.Face(raw));f.set_variations(dict(wght=w,opsz=opt,wdth=100,GRAD=400));groups={}
   for script,anchor in [('latin','H'),('cyrillic','А')]:
    groups[script]={}
    for side in ['left','right']:
     found={}
     for ch in chars:
      text=ch+':'+anchor if side=='left' else anchor+':'+ch;runs=[]
      for kern in [False,True]:
       b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(f,b,{'kern':kern});runs.append((b.glyph_infos,b.glyph_positions))
      if next((g.codepoint for g in runs[1][0] if g.cluster==1),None)!=1776:continue
      idx=0 if side=='left' else 1
      advance=lambda run:sum(p.x_advance for g,p in zip(*run) if g.cluster==idx)
      found[ch]=advance(runs[1])-advance(runs[0])
     groups[script][side]=sorted(found)
     for ch,kern in found.items():d['nodes'][str(w)][label][side].setdefault(ch,kern)
   evidence.append(groups)
 assert all(g==evidence[0] for g in evidence)
 d['contextGroups']=evidence[0]
 for side in ['left','right']:d[side+'Context']=sorted(set().union(*(set(g[side]) for g in evidence[0].values())))
 d['full_scope_measurement']='Separate Latin/Cyrillic anchor probes for every required character at six source locations; existing calibrated kern values preserved.';a.out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
