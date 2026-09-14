"""Folded strokes: independent line-bounded bands, clipped to the glyph frame."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from parameters import at_location

def construction(p):
 d=Drawing();left,right=p['left'],p['right']
 for index,band in enumerate(p['slashes']):
  left,right=(0,p['left']),(0,p['right'])
  for join in p.get('joins',[]):
   if not join.get('clip',1):continue
   if index==join['left']:right=(join['seam_slope'],join['seam_intercept'])
   if index==join['right']:left=(join['seam_slope'],join['seam_intercept'])
  lo,hi=band['bottom'],band['top'];edges=[]
  for sign in [-1,1]:
   a=band['slope']+sign*band.get('width_slope',0)/2;b=band['intercept']+sign*band['width']/2
   crossings=[(edge[1]-b)/(a-edge[0]) if abs(a-edge[0])>1e-12 else lo for edge in [left,right]]
   ys=sorted([lo,hi,*[max(lo,min(hi,y)) for y in crossings]])
   edges.append([(max(left[0]*y+left[1],min(right[0]*y+right[1],a*y+b)),y) for y in ys])
  d.polygon(edges[0]+edges[1][::-1])
 for join in p.get('joins',[]):
  a=p['slashes'][int(join['left'])];b=p['slashes'][int(join['right'])];y=join['cap']
  inner_left=(a['slope']+a.get('width_slope',0)/2)*y+a['intercept']+a['width']/2
  inner_right=(b['slope']-b.get('width_slope',0)/2)*y+b['intercept']-b['width']/2
  bottom=a['bottom'] if join['direction']>0 else y;top=y if join['direction']>0 else a['top']
  d.rect(min(inner_left,inner_right),bottom,abs(inner_right-inner_left),top-bottom)
 return d
@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/folded-bands.json').read_text())['glyphs']
def apply(glyph,key,design):
 if key not in load():return
 glyph.clearContours();glyph.clearComponents();construction(at_location(load()[key],design)).replay(glyph.getPen())
