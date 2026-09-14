"""Check tangent continuity of the authored spiral and asymmetric bowl pieces."""
import argparse,json,sys,math
from pathlib import Path
from fontTools.pens.recordingPen import RecordingPen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from at_spiral import spiral,asymmetric_bowl

def check(d,closed):
 p=RecordingPen();d.replay(p);start=current=None;curves=[];pairs=[];previous=None
 for op,args in p.value:
  if op=='moveTo':current=start=args[0];previous=None
  elif op=='curveTo':
   curve=[current,*args]
   if previous is not None:pairs.append((previous,curve))
   curves.append(curve);previous=curve;current=args[-1]
  elif op=='lineTo':current=args[-1];previous=None
 if closed:pairs.append((curves[-1],curves[0]))
 for a,b in pairs:
  u=[a[3][i]-a[2][i] for i in [0,1]];v=[b[1][i]-b[0][i] for i in [0,1]]
  n=math.hypot(*u)*math.hypot(*v);assert n>1e-14
  assert abs(u[0]*v[1]-u[1]*v[0])/n<1e-9
  assert sum(x*y for x,y in zip(u,v))>0
 return len(pairs)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--parameters',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();d=json.loads(a.parameters.read_text());rows=[]
 for w,profiles in d['weights'].items():
  for optical,p in profiles.items():
   n=check(spiral(p['spiral']),False)
   for role in ['bowl','counter']:n+=check(asymmetric_bowl(p[role+'_bounds'],p[role+'_handles'],p[role+'_extrema']),True)
   rows.append(dict(weight=int(w),optical=optical,tangent_joins=n))
 result=dict(status='passed',profiles=rows,total_joins=sum(r['tangent_joins'] for r in rows),scope='Cubic source G1 tangent continuity; intentional terminal corners excluded; no G2 or global curvature claim.')
 a.out.write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
