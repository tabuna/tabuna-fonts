"""Measure the shaped colon variant as independent shared round contours."""
import argparse,json
from pathlib import Path
import numpy as np
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten
from font_recovery.measure_rings import fit_pair


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();data=json.loads(a.base.read_text());path=Path('/System/Library/Fonts/SFNS.ttf');f=TTFont(path);raw=path.read_bytes();profiles={};evidence=[]
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   location=dict(wght=w,opsz=opt,wdth=100,GRAD=400);font=hb.Font(hb.Face(raw));font.set_variations(location);buffer=hb.Buffer();buffer.add_str('H:H');buffer.guess_segment_properties();hb.shape(font,buffer);gid=buffer.glyph_infos[1].codepoint;name=f.getGlyphName(gid);assert name!='colon';gs=f.getGlyphSet(location=location);flat=Flatten(gs);gs[name].draw(flat);assert len(flat.contours)==2;p=dict(rounds=[],bands=[]);errors=[]
   for c in flat.contours:
    q,e=fit_pair([c,c],f['head'].unitsPerEm);p['rounds'].append(dict(bounds=q['bounds'][0],handles=q['outerHandles']));errors.append(e[0])
   profiles.setdefault(str(w),{})[label]=p;evidence.append(dict(weight=w,optical=opt,shaped_reference_name=name,reference_gid=gid,residuals=errors));print(evidence[-1],flush=True)
 data['glyphs']['colon.case']=profiles;data['context_colon_measurements']=evidence;a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
