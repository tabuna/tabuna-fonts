"""Authored open double bowl: twelve tangent-constrained cubic arcs."""
import numpy as np

def contour(p):
 # Clockwise outer rim, reverse inner rim; five straight edges at terminals and the middle bar.
 points=[(p['tip_x'],p['upper_tip_y']),(p['top_x'],1),(p['upper_right'],p['upper_y']),
         (p['waist_x'],p['waist_y']),(1,p['lower_y']),(p['bottom_x'],0),(0,p['lower_tip_y']),
         (p['lower_inner_tip_x'],p['lower_tip_y']), (p['inner_bottom_x'],p['inner_bottom_y']),
         (p['inner_lower_right'],p['inner_lower_y']),(p['middle_x']+p.get('middle_extension',0),p['middle_bottom']),(p['middle_x'],p['middle_bottom']),
         (p['middle_x'],p['middle_top']),(p['middle_x']+p.get('middle_extension',0),p['middle_top']),(p['inner_upper_right'],p['inner_upper_y']),
         (p['inner_top_x'],p['inner_top_y']),(p['upper_inner_tip_x'],p['upper_tip_y'])]
 tangents=[(0,1),(1,0),(0,-1),(0,-1),(0,-1),(-1,0),(0,1),
           (0,-1),(1,0),(0,1),(-1,0),(-1,0),(1,0),(1,0),(0,1),(-1,0),(0,-1)]
 arcs=[];index=0
 for i in range(len(points)):
  j=(i+1)%len(points);a=np.array(points[i]);b=np.array(points[j])
  if i in (6,10,11,12,16):arcs.append(('line',np.array([a,b])));continue
  out_tangent=(1,0) if i==3 else tangents[i]
  in_tangent=(-1,0) if j==3 else tangents[j]
  delta=np.abs(b-a);h=p['handles'][index:index+2];index+=2
  first=delta[0] if out_tangent[0] else delta[1]
  second=delta[0] if in_tangent[0] else delta[1]
  arcs.append(('cubic',np.array([a,a+np.array(out_tangent)*first*h[0],b-np.array(in_tangent)*second*h[1],b])))
 assert index==24
 return arcs

def flattened(p):
 t=np.linspace(0,1,41);weights=np.array([(1-t)**3,3*t*(1-t)**2,3*t*t*(1-t),t**3]).T
 return [np.concatenate([weights@c if kind=='cubic' else c for kind,c in contour(p)]).tolist()]
