"""Match normalized letter stem thickness with the existing authored C/R weight axis."""
import json
from pathlib import Path
import numpy as np
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from scipy.optimize import minimize_scalar
from font_recovery.measure import Flatten,scan
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'build/font-recovery/enclosed/parameters.json';data=json.loads(p.read_text())
system=TTFont('/System/Library/Fonts/SFNS.ttf');s=subset.Subsetter();s.populate(text='©®');s.subset(system)
own=TTFont(ROOT/'dist/TabunaSansVariable.ttf');evidence=[]
def box(c):
 a=np.array(c);return np.r_[a.min(axis=0),a.max(axis=0)]
def thickness(contours,fraction):
 a=np.concatenate(contours);lo=a.min(axis=0);hi=a.max(axis=0);runs=scan(contours,lo[1]+fraction*(hi[1]-lo[1]),nonzero=True)
 return (runs[0][1]-runs[0][0])/(hi[0]-lo[0])
for weight in [100,400,900]:
 for label,optical in [('text',17),('display',28)]:
  f=instantiateVariableFont(system,{'wght':weight,'opsz':optical,'wdth':100,'GRAD':400},inplace=False);gs=f.getGlyphSet()
  for ch,key,base,fraction in [('©','copyright','C',.5),('®','registered','R',.2)]:
   flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat)
   cs=sorted(flat.contours,key=lambda c:(box(c)[2]-box(c)[0])*(box(c)[3]-box(c)[1]),reverse=True)[2:];target=thickness(cs,fraction)
   def error(w):
    glyphs=own.getGlyphSet(location={'wght':w,'opsz':14 if label=='text' else 28});q=Flatten(glyphs);glyphs[base].draw(q);return (thickness(q.contours,fraction)-target)**2
   fit=minimize_scalar(error,bounds=(100,900),method='bounded',options={'xatol':.001});data['glyphs'][key][str(weight)][label]['letter_weight']=float(fit.x);evidence.append(dict(character=ch,weight=weight,optical=optical,letter_weight=float(fit.x),normalized_stem_error=float(fit.fun**.5)))
data['letter_weight_measurements']=evidence;p.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(evidence))
