"""Inspect source derivatives at brace curve/line joins, including interpolation."""
import sys,json,argparse,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from curly_braces import construction
from parameters import mix


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--parameters',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();data=json.loads(a.parameters.read_text())['glyphs'];rows=[]
    for glyph,masters in data.items():
      for weight in [100,250,400,650,900]:
       for optical_mix in [0,.5,1]:
        low,high=(100,400) if weight<=400 else (400,900)
        p=mix(mix(masters[str(low)]['text'],masters[str(low)]['display'],optical_mix),mix(masters[str(high)]['text'],masters[str(high)]['display'],optical_mix),(weight-low)/(high-low))
        segs=[];start=None;current=None
        def sub(a,b):return (a[0]-b[0],a[1]-b[1])
        for op,args in construction(p,glyph=='braceright').pen.value:
            if op=='moveTo':start=current=args[0]
            elif op=='lineTo':end=args[0];v=sub(end,current);segs.append(('line',v,v));current=end
            elif op=='curveTo':c1,c2,end=args;segs.append(('curve',sub(c1,current),sub(end,c2)));current=end
            elif op=='closePath' and current!=start:v=sub(start,current);segs.append(('line',v,v))
        smooth=corners=0
        for x,y in zip(segs,segs[1:]+segs[:1]):
            if x[0]==y[0]:continue
            u,v=x[2],y[1];scale=math.hypot(*u)*math.hypot(*v);assert scale>0
            cross=abs(u[0]*v[1]-u[1]*v[0])/scale;dot=(u[0]*v[0]+u[1]*v[1])/scale
            if cross<1e-9 and dot>0:smooth+=1
            else:assert abs(dot)<1e-9;corners+=1
        assert (smooth,corners)==(12,4),(glyph,weight,optical_mix,smooth,corners)
        rows.append(dict(glyph=glyph,weight=weight,optical_mix=optical_mix,smooth_tangent_joins=smooth,intentional_nose_corners=corners))
    a.out.write_text(json.dumps(dict(scope='Source cubic tangent continuity, not G2 or exact compiled TrueType continuity',locations=len(rows),smooth_joins=sum(r['smooth_tangent_joins'] for r in rows),rows=rows),indent=2)+'\n');print(len(rows))


if __name__=='__main__':main()
