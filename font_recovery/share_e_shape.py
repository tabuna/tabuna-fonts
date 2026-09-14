"""Verify normalized reference equivalence and share the authored e geometry."""
from pathlib import Path
import json,copy
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten
p=Path('build/font-recovery/shared-e');p.mkdir(parents=True,exist_ok=True)
f=TTFont('/System/Library/Fonts/SFNS.ttf');data=json.load(open('sources/lower-e.json'));proof=[]
data['glyphs']['е']['shape_from']='e'
for weight in [100,400,900]:
 for label,opt in [('text',17),('display',28)]:
  gs=f.getGlyphSet(location=dict(wght=weight,opsz=opt,wdth=100,GRAD=400));samples=[];bounds=[]
  for ch in 'eе':
   pen=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(pen);v=np.concatenate(pen.contours);lo=v.min(0);hi=v.max(0);samples.append((v-lo)/(hi-lo));bounds.append((np.r_[lo,hi]*1000/f['head'].unitsPerEm).tolist())
  assert samples[0].shape==samples[1].shape;error=float(np.max(abs(samples[0]-samples[1])));assert error<1e-12
  old=data['glyphs']['е'][str(weight)][label];data['glyphs']['е'][str(weight)][label]=dict(bounds=bounds[1],advance=old['advance']);proof.append(dict(weight=weight,optical=opt,normalized_difference=error))
(p/'parameters.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');(p/'equivalence-proof.json').write_text(json.dumps(dict(profiles=6,measurements=proof,scope='Normalized reference geometry is compared for equality; no reference vertices are exported to construction parameters.'),indent=2)+'\n')
