import sys,json,copy
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
sys.path.insert(0,str(Path.cwd()/'scripts'))
from at_spiral import construction
from font_recovery.measure import Flatten,scan
p=Path('build/font-recovery/at-refinement');d=json.loads((p/'parameters.json').read_text());f=TTFont('/System/Library/Fonts/SFNS.ttf');rows=[]
for w in [100,400]:
 q=d['weights'][str(w)]['text'];gs=f.getGlyphSet(location=dict(wght=w,opsz=17,wdth=100,GRAD=400));pen=Flatten(gs);gs[f.getBestCmap()[64]].draw(pen);pts=np.concatenate(pen.contours);lo=pts.min(0);hi=pts.max(0);ref=[((np.array(c)-lo)/(hi-lo)).tolist() for c in pen.contours]
 sp=q['spiral'];xs=np.linspace(max(q['bowl_bounds'][2],sp['stem_left']+sp['stem_width'],sp['outer']['tip_x'])+.012,sp['outer']['hook_x']-.004,31);target=np.array([scan(ref,x,vertical=True,nonzero=True)[0][0] for x in xs]);seed=sp['outer']['handles'][5][0]
 def residual(v):
  temp=copy.deepcopy(q);temp['bounds']=[0,0,1,1];temp['spiral']['outer']['handles'][5][0]=float(v[0]);flat=Flatten(None);construction(temp).replay(flat)
  return np.array([scan(flat.contours,x,vertical=True,nonzero=True)[0][0] for x in xs])-target
 old=float(np.linalg.norm(residual([seed])));fit=least_squares(residual,[seed],bounds=([.1],[.9]),diff_step=1e-4,max_nfev=50);sp['outer']['handles'][5][0]=float(fit.x[0]);rows.append(dict(weight=w,optical=17,handle_before=seed,handle_after=float(fit.x[0]),error_before=old,error_after=float(np.linalg.norm(fit.fun)),samples=len(xs)))
(p/'hook-parameters.json').write_text(json.dumps(d,indent=2)+'\n');(p/'hook-fit.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)
