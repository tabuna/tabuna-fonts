"""Sterling: an S-shaped rising ribbon, open head, foot and crossbar."""
import json
from functools import lru_cache
from pathlib import Path
from geometry import Drawing
from bezier import tangent_arc as arc,unit
from parameters import at_location


def turn(*args):
    return arc(*args,bounded=True)


def construction(p):
    o,i=p['outer'],p['inner'];d=Drawing();base=p['base']
    start=(0,0);foot=(0,o['foot_y']);bulge=(o['bulge_x'],o['bulge_y']);neck=(o['neck_x'],o['neck_y']);top=(o['top_x'],1);tip=(o['tip_x'],o['tip_y']);cut=(o['tip_x'],i['tip_y']);itop=(i['top_x'],i['top']);ineck=(i['neck_x'],i['neck_y']);ibulge=(i['bulge_x'],i['bulge_y']);ifoot=(i['foot_x'],i['foot_y'])
    h=o['handles'];k=i['handles']
    d.outline(start,[foot,turn(foot,bulge,unit(1,o['foot_slope']),(0,1),h[0]),turn(bulge,neck,(0,1),(0,1),h[1]),turn(neck,top,(0,1),(1,0),h[2]),turn(top,tip,(1,0),unit(1,-o['tip_slope']),h[3]),cut,
      turn(cut,itop,unit(-1,i['tip_slope']),(-1,0),k[3]),turn(itop,ineck,(-1,0),(0,-1),k[2]),turn(ineck,ibulge,(0,-1),(0,-1),k[1]),turn(ibulge,ifoot,(0,-1),unit(-1,-i['foot_slope']),k[0]),(i['foot_x'],base),(1,base),(1,0)])
    bar=p['bar'];d.rect(bar['left'],bar['bottom'],bar['right']-bar['left'],bar['top']-bar['bottom'])
    l,b,r,t=p['bounds'];out=Drawing();d.replay(out.pen,(r-l,0,0,t-b,l,b));return out


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/sterling-ribbon.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='sterling':return
    glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
