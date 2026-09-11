"""Original polygon constructions for M and W."""
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing
from rectilinear import mix

@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/mw.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}

def apply(glyph,key,design):
    ch={'uni004D':'M','uni0057':'W'}.get(key,key);data=load().get(ch)
    if data is None:return
    lo,hi=(100,400) if design.weight<=400 else (400,900)
    a=mix(data[str(lo)]['text'],data[str(lo)]['display'],design.display)
    b=mix(data[str(hi)]['text'],data[str(hi)]['display'],design.display)
    p=mix(a,b,(design.weight-lo)/(hi-lo));drawing=Drawing();drawing.polygon(p['points'])
    glyph.clearContours();drawing.replay(glyph.getPen());glyph.width=p['advance']
