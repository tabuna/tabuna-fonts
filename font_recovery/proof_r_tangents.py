"""Check positive aligned tangents at r shoulder joins in each source profile."""
import sys,json
import numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from r_shoulder import edge
p=Path('build/font-recovery/r-shoulder');data=json.load(open(p/'parameters-v6.json'));rows=[]
for weight,profiles in data['weights'].items():
 for label,q in profiles.items():
  for role in ['outer','inner']:
   points,curves=edge(q,q[role])
   for k in range(len(curves)-1):
    left=np.array(points[k+1])-np.array(curves[k][1]);right=np.array(curves[k+1][0])-np.array(points[k+1]);cross=abs(float(left[0]*right[1]-left[1]*right[0]));dot=float(np.dot(left,right));assert cross<1e-12 and dot>0
    rows.append(dict(weight=weight,optical=label,edge=role,join=k,cross=cross,dot=dot))
  points,curves=edge(q,q['inner']);t=np.array(curves[0][0])-np.array(points[0]);assert abs(t[0])<1e-12 and t[1]>0
(p/'tangent-proof-v6.json').write_text(json.dumps(dict(shoulder_checks=len(rows),inner_stem_checks=6,checks=rows,scope='G1 at shoulder joins and inner upright; terminal and cap corners are intentional.'),indent=2)+'\n')
