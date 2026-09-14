"""A brace ribbon with four turns on each side, shared by mirrored braces."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from bezier import tangent_arc as arc
from parameters import at_location


def construction(p,mirror=False):
    o,i=p['outer'],p['inner'];d=Drawing()
    start=(1,0)
    d.outline(start,[(o['bottom_x'],0),arc((o['bottom_x'],0),(o['stem'],o['bottom_y']),(-1,0),(0,1),o['handles'][0]),
        (o['stem'],o['lower_y']),arc((o['stem'],o['lower_y']),(0,o['nose_bottom']),(0,1),(-1,0),o['handles'][1]),
        (0,o['nose_top']),arc((0,o['nose_top']),(o['stem'],o['upper_y']),(1,0),(0,1),o['handles'][2]),
        (o['stem'],o['top_y']),arc((o['stem'],o['top_y']),(o['top_x'],1),(0,1),(1,0),o['handles'][3]),
        (1,1),(1,i['top']),(i['top_x'],i['top']),arc((i['top_x'],i['top']),(i['stem'],i['top_y']),(-1,0),(0,-1),i['handles'][3]),
        (i['stem'],i['upper_y']),arc((i['stem'],i['upper_y']),(i['nose_x'],i['nose_top']),(0,-1),(-1,0),i['handles'][2]),
        (i['nose_x'],i['nose_bottom']),arc((i['nose_x'],i['nose_bottom']),(i['stem'],i['lower_y']),(1,0),(0,-1),i['handles'][1]),
        (i['stem'],i['bottom_y']),arc((i['stem'],i['bottom_y']),(i['bottom_x'],i['bottom']),(0,-1),(1,0),i['handles'][0]),(1,i['bottom'])])
    l,b,r,t=p['bounds'];out=Drawing();d.replay(out.pen,(-(r-l) if mirror else r-l,0,0,t-b,r if mirror else l,b));return out


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/curly-braces.json').read_text())['glyphs']


def apply(glyph,key,design):
    if key not in ('braceleft','braceright'):return
    p=at_location(load()[key],design);glyph.clearContours();construction(p,key=='braceright').replay(glyph.getPen())
