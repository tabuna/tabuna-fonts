"""Authored open double-bowl construction, used by digit three and both Cyrillic Ze cases."""
import json
from pathlib import Path
from functools import lru_cache
from parameters import at_location
from open_double_model import contour
from geometry import Drawing
@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/open-double-bowls.json').read_text())
def apply(glyph,key,design):
 ch={'three':'3','uni0417':'З','uni0437':'з'}.get(key)
 if ch is None:return
 p=at_location(load()[ch],design);d=Drawing();arcs=contour(p['shape']);d.pen.moveTo(tuple(map(float,arcs[0][1][0])))
 for kind,points in arcs:
  if kind=='line':d.pen.lineTo(tuple(map(float,points[-1])))
  else:d.pen.curveTo(*(tuple(map(float,point)) for point in points[1:]))
 d.pen.closePath();l,b,r,t=p['bounds'];glyph.clearContours();d.replay(glyph.getPen(),(r-l,0,0,t-b,l,b))
