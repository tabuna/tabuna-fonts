import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
R=Path(__file__).resolve().parents[1]; src=R/'build/full-score/64'; out=R/'build/pilot-k'; out.mkdir(parents=True,exist_ok=True)
r=next(x for x in json.load(open(src/'comparison.json'))['records'] if x['character']=='к')
a=np.array(Image.open(src/r['system']['file']).convert('L'))/255
q=np.array(Image.open(src/r['tabuna']['file']).convert('L'))/255
rows=[]
for t in (.25,.5,.75):
 m=a<(1-t); lab,n=ndimage.label(m); c=max((lab==i for i in range(1,n+1)),key=lambda z:z.sum())
 edge=c&~ndimage.binary_erosion(c); y,x=np.where(edge)
 # retain extrema plus evenly spaced boundary samples, never alter bbox
 pts=np.column_stack([x,y]);
 if len(pts)>34: pts=pts[np.linspace(0,len(pts)-1,34).astype(int)]
 ref=c; ren=q<.5; fp=int((ren&~ref).sum());fn=int((ref&~ren).sum())
 dt=ndimage.distance_transform_edt(~ren); boundary_dist=float(dt[ref].mean())
 item={'threshold':t,'bbox':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'points':pts.tolist(),'iou':r['inkIoU'],'fp':fp,'fn':fn,'boundaryDistance':boundary_dist}
 json.dump(item,open(out/f'k-{t:.2f}.json','w'),indent=2); rows.append(item)
json.dump({'glyph':'к','bboxReference':[72,154,124,219],'variants':rows},open(out/'summary.json','w'),ensure_ascii=False,indent=2)
print(json.dumps({'glyph':'к','variants':[(x['threshold'],x['fp'],x['fn'],x['boundaryDistance']) for x in rows]},ensure_ascii=False))
