"""Upright and top crossbar as a single analytic rectilinear boundary."""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from parameters import at_location

def construction(p,ch):
 l,r,b,t=p['left'],p['right'],p['bottom'],p['top'];sl,sr,bb=p['stem_left'],p['stem_right'],p['bar_bottom']+p.get('optical_bar_reduction',0)
 vertices=[(l,bb),(l,t),(r,t),(r,bb),(sr,bb),(sr,b),(sl,b),(sl,bb)] if ch=='T' else [(sl,b),(sl,t),(r,t),(r,bb),(sr,bb),(sr,b)]
 d=Drawing();d.polygon(vertices);return d
@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/top-bars.json').read_text())['glyphs']
def apply(glyph,key,design):
 ch=chr(int(key[3:],16)) if key.startswith('uni') and len(key)==7 else key
 if ch not in load():return
 glyph.clearContours();glyph.clearComponents();construction(at_location(load()[ch],design),ch).replay(glyph.getPen())
