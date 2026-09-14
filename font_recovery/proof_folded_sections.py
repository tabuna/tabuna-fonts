import sys,json,numpy as np
sys.path.insert(0,'scripts')
from folded_bands import construction
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten,scan
def merged(runs):
 out=[]
 for a,b in runs:
  if out and a-out[-1][1]<1e-8:out[-1][1]=max(out[-1][1],b)
  else:out.append([a,b])
 return np.array(out)
f=TTFont('/System/Library/Fonts/SFNS.ttf');prod=TTFont('dist/TabunaSansVariable.ttf');d=json.load(open('build/font-recovery/folded-bands/parameters.json'));errs=[]
for ch in 'VvwMМм':
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400));ref=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(ref);cs=[(np.array(c)*1000/f['head'].unitsPerEm).tolist() for c in ref.contours];p=d['glyphs'][prod.getBestCmap()[ord(ch)]][str(w)][label];own=Flatten(None);construction(p).replay(own);count=0;err=0
   for y in np.linspace(.001,p['slashes'][0]['top']-.001,501):
    a=merged(scan(cs,y,nonzero=True));b=merged(scan(own.contours,y,nonzero=True))
    if a.shape!=b.shape:count+=1
    else:err=max(err,float(np.max(abs(a-b))))
   errs.append(dict(character=ch,weight=w,optical=opt,mismatched_sections=count,max_edge_error=err))
print(json.dumps(errs,ensure_ascii=False));open('build/font-recovery/folded-bands/join-section-proof.json','w').write(json.dumps(errs,indent=2))

assert len(errs)==36 and all(x['mismatched_sections']==0 and x['max_edge_error']<1e-7 for x in errs), 'Folded-band section mismatch'
