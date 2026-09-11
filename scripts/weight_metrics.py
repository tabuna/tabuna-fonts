"""Scalar correction of own shapes, with explicit measured weight endpoints."""
from pathlib import Path
from functools import lru_cache
import json
from metrics import linear

@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/weight-metrics.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def coefficients(key,design):
    data=load().get(key)
    if data is None or (design.weight==400 and '400' not in data['nodes']):return None
    weight=100 if design.weight<400 else 900
    strength=(400-design.weight)/300 if weight==100 else (design.weight-400)/500
    def endpoint(w):
        if str(w) not in data['nodes']:return {'sx':1.,'dx':0.,'advanceOffset':0.,'y':lambda y:y}
        a,b=data['nodes'][str(w)]['text'],data['nodes'][str(w)]['display'];t=design.display
        def mix(k):return a[k]+(b[k]-a[k])*t
        sx=mix('sx')
        return {'sx':sx,'dx':mix('dx'),'advanceOffset':mix('advance')-mix('baseAdvance')*sx,
                'y':lambda y:linear(y,a['y'])*(1-t)+linear(y,b['y'])*t}
    regular,extreme=endpoint(400),endpoint(weight)
    out={k:regular[k]+(extreme[k]-regular[k])*strength for k in ('sx','dx','advanceOffset')}
    out['y']=lambda y:regular['y'](y)+(extreme['y'](y)-regular['y'](y))*strength
    return out


def apply(glyph,key,design):
    c=coefficients(key,design)
    if c is None:return
    for contour in glyph.contours:
        for point in contour.points:
            point.x=point.x*c['sx']+c['dx'];point.y=c['y'](point.y)
    glyph.width=glyph.width*c['sx']+c['advanceOffset']
