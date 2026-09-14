"""Fit shared display e/е geometry against scalar filled-silhouette moments."""
import argparse,copy,json,sys
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten
from font_recovery.fitting import shape_features
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from lower_e import contours,NAMES
from geometry import Drawing
from fixed_e_quadratics import convert,COUNTS
from fontTools.pens.recordingPen import RecordingPen
FIT_NAMES=NAMES+["tipInnerY"]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--thin-only',action='store_true');a=ap.parse_args();data=json.load(open('build/font-recovery/shared-e/display-parameters.json'));f=TTFont('/System/Library/Fonts/SFNS.ttf');evidence=[]
 for w in ([100] if a.thin_only else [100,400,900]):
  gs=f.getGlyphSet(location=dict(wght=w,opsz=28,wdth=100,GRAD=400));ref=Flatten(gs);gs[f.getBestCmap()[ord('e')]].draw(ref);v=np.concatenate(ref.contours);lo=v.min(0);hi=v.max(0);cs=[((np.array(c)-lo)/(hi-lo)).tolist() for c in ref.contours]
  seed=copy.deepcopy(data['glyphs']['e'][str(w)]['display']);p0=seed['parameters'];p0.setdefault('tipInnerY',p0['tipY']);v0=[p0[k] for k in FIT_NAMES]+seed['handles'];lower=[max(.001,x-.06) for x in v0[:17]]+[.02]*20;upper=[min(.999,x+.06) for x in v0[:17]]+[.98]*20;v0=np.clip(v0,np.array(lower)+1e-6,np.array(upper)-1e-6)
  target=shape_features(cs,[0,0,1,1],count=91,nonzero=True)
  def params(v):return dict(zip(FIT_NAMES,map(float,v[:17]))),list(map(float,v[17:]))
  def residual(v):
   p,k=params(v);d=Drawing()
   for start,segments,counter in contours(p,k):d.outline(start,segments,counter)
   record=RecordingPen();d.replay(record);features=[]
   for counts in COUNTS.values():
    flat=Flatten(None);current=None;index=0
    for op,points in record.value:
     if op=='curveTo':flat.qCurveTo(*convert([current,*points],counts[index])[1:]);index+=1
     else:getattr(flat,op)(*points)
     if points:current=points[-1]
    features.append(shape_features(flat.contours,[0,0,1,1],count=91,nonzero=True)-target)
   return np.concatenate(features)
  fit=least_squares(residual,v0,bounds=(lower,upper),max_nfev=180,diff_step=1e-4,ftol=1e-9,xtol=1e-9,gtol=1e-9);p,k=params(fit.x)
  for ch in 'eе':
   flat=Flatten(gs);gs[f.getBestCmap()[ord(ch)]].draw(flat);v=np.concatenate(flat.contours);bounds=(np.r_[v.min(0),v.max(0)]*1000/f['head'].unitsPerEm).tolist();q=data['glyphs'][ch][str(w)]['display'];q.update(parameters=p,handles=k,bounds=bounds)
   text=data['glyphs'][ch][str(w)]['text']['parameters'];text['tipInnerY']=text['tipY']
  row=dict(weight=w,optical=28,residual=float(np.linalg.norm(fit.fun)),evaluations=fit.nfev,converged=bool(fit.success));evidence.append(row);data['display_fit']=evidence;a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(row,flush=True)
 if a.thin_only:
  original=json.loads(Path('sources/lower-e.json').read_text())
  for ch in 'eе':
   for w in ['400','900']:
    data['glyphs'][ch][w]=original['glyphs'][ch][w]
    for optical in ['text','display']:
     p=data['glyphs'][ch][w][optical]['parameters'];p['tipInnerY']=p['tipY']
  data['display_fit_scope']='Shared thin master only; independently calibrated regular and heavy masters preserved.'
  a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
