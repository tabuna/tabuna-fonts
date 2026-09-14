"""Shared linear-band construction with analytic clipping at upright edges."""
import json
from functools import lru_cache
from pathlib import Path
from parameters import at_location
from math_bands import construction as bands
from geometry import Drawing


def construction(p):
 if not p['bars']:return bands(p)
 d=bands(dict(bars=p['bars'],slashes=[]))
 left=min(b['x']-b['width']/2 for b in p['bars']);right=max(b['x']+b['width']/2 for b in p['bars'])
 for band in p['slashes']:
  lo,hi=band['bottom'],band['top'];edges=[]
  for sign in [-1,1]:
   a=band['slope']+sign*band.get('width_slope',0)/2;b=band['intercept']+sign*band['width']/2
   ys=sorted([lo,hi,max(lo,min(hi,(left-b)/a)),max(lo,min(hi,(right-b)/a))])
   edges.append([(max(left,min(right,a*y+b)),y) for y in ys])
  d.polygon(edges[0]+edges[1][::-1])
 return d

@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/diagonal-family.json').read_text())['glyphs']
def apply(glyph,key,design):
 p=load().get(key)
 if p is not None:
  glyph.clearContours();glyph.clearComponents();construction(at_location(p,design)).replay(glyph.getPen())
