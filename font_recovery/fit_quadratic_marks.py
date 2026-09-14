"""Fit shared G1 quadratic round model using scalar section moments only."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from quadratic_round import contour


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();data=json.loads(a.base.read_text());f=TTFont('/System/Library/Fonts/SFNS.ttf');cache={};evidence=[]
 for w in [100,400,900]:
  for label,opt in [('text',17),('display',28)]:
   gs=f.getGlyphSet(location=dict(wght=w,opsz=opt,wdth=100,GRAD=400))
   for key,source in [('colon','colon'),('divide','divide'),('ellipsis','ellipsis'),('colon.case','colon.uc')]:
    flat=Flatten(gs);gs[source].draw(flat);rounds=[c for c in flat.contours if len(c)>20];profiles=data['glyphs'][key][str(w)][label]['rounds'];assert len(rounds)==len(profiles)
    for c,p in zip(rounds,profiles):
     v=np.array(c);v=(v-v.min(0))/np.ptp(v,axis=0);cachekey=np.round(v,9).tobytes()
     if cachekey not in cache:
      target=shape_features([v.tolist()],[0,0,1,1],count=81,nonzero=True)
      def residual(x):
       q=Flatten(None);contour([0,0,1,1],np.array(x).reshape(4,3)).replay(q);return shape_features(q.contours,[0,0,1,1],count=81,nonzero=True)-target
      fit=least_squares(residual,[.414,.586,.5]*4,bounds=([.05,.05,.1]*4,[.95,.95,.9]*4),max_nfev=100,diff_step=1e-4,ftol=1e-10,xtol=1e-10,gtol=1e-10);cache[cachekey]=(fit.x.reshape(4,3).tolist(),float(np.linalg.norm(fit.fun)))
     p['quadrants'],error=cache[cachekey];p.pop('handles',None);evidence.append(dict(glyph=key,weight=w,optical=opt,residual=error))
    print(key,w,label,evidence[-1]['residual'],flush=True)
    data['quadratic_round_measurements']=evidence;a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
