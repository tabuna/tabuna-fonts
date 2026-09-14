import sys,json,numpy as np
from pathlib import Path
sys.path.insert(0,'scripts')
from z_bands import construction
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
p=Path('build/font-recovery/z-bands');f=TTFont('/System/Library/Fonts/SFNS.ttf');data=json.load(open(p/'parameters.json'));proof=[]
for ch,weights in data['glyphs'].items():
 for w,profiles in weights.items():
  for label,params in profiles.items():
   gs=f.getGlyphSet(location=dict(wght=int(w),opsz=17 if label=='text' else 28,wdth=100,GRAD=400));ref=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(ref);cs=[(np.array(c)*1000/f['head'].unitsPerEm).tolist() for c in ref.contours];own=Flatten(None);construction(params).replay(own);v=np.concatenate(cs);error=0;count=0
   for y in np.linspace(v[:,1].min()+1e-4,v[:,1].max()-1e-4,501):
    a=np.array(scan(cs,y,nonzero=True));b=np.array(scan(own.contours,y,nonzero=True))
    if a.shape!=b.shape:count+=1
    else:error=max(error,float(np.max(abs(a-b))))
   proof.append(dict(character=ch,weight=w,optical=label,max_edge_error=error,mismatch=count))
print(proof);(p/'construction-proof.json').write_text(json.dumps(dict(profiles=12,sections_per_profile=501,checks=proof),indent=2)+'\n')

assert len(proof)==12 and all(x['mismatch']==0 and x['max_edge_error']<1e-7 for x in proof), 'Z-band section mismatch'
