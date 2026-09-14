"""Enclosed symbols from two cubic ellipses and the authored C/R models."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from parameters import at_location


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/enclosed-symbols.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,base,design,letter_at_weight):
    data=load().get(key)
    if data is None:return
    p=at_location(data,design);d=Drawing();d.ellipse(*p['outer']);d.ellipse(*p['inner'],reverse=True)
    if key=='registered':
        from r_bowl import construction
        parameters=json.loads((Path(__file__).resolve().parents[1]/'sources/registered-bowl.json').read_text())['weights']
        construction(at_location(parameters,design)).replay(d.pen)
        glyph.clearContours();glyph.clearComponents();d.replay(glyph.getPen());glyph.width=p['advance']
        return
    base=letter_at_weight(p['letter_weight'])
    from fontTools.pens.boundsPen import BoundsPen
    bounds=BoundsPen(None);base.draw(bounds)
    l,b,r,t=bounds.bounds;dl,db,dr,dt=p['letter'];sx=(dr-dl)/(r-l);sy=(dt-db)/(t-b)
    from fontTools.pens.transformPen import TransformPen
    base.draw(TransformPen(d.pen,(sx,0,0,sy,dl-l*sx,db-b*sy)))
    glyph.clearContours();glyph.clearComponents();d.replay(glyph.getPen());glyph.width=p['advance']
