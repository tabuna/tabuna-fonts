"""Ampersand from tangent-directed cubic stroke strips.

The fitting view uses two ribbons. Production splits them at corresponding
anchors: four upper arc strips, a diagonal, four lower arc strips and a cap.
The lower straight extension is covered by the upper diagonal and omitted.
Separate same-winding pieces permit intended joins without self-crossing paths.
No G2 continuity claim is made.
"""
import json
from pathlib import Path
from functools import lru_cache
from geometry import Drawing
from bezier import tangent_arc,unit
from parameters import at_location


def arc(a,b,u,v,h):return tangent_arc(a,b,u,v,h,bounded=True)


def upper(q, pieces=False):
    d=Drawing();o,i=q['outer'],q['inner'];h=o['handles'];k=i['handles'];tail=(q['diagonal_outer'][0]*q['base']+q['diagonal_outer'][1],q['base']);join=(q['diagonal_outer'][0]*o['join_y']+q['diagonal_outer'][1],o['join_y']);left=(o['left_x'],o['left_y']);top=(o['top_x'],1);right=(o['right_x'],o['right_y']);cut=(o['cut_x'],o['cut_y']);icut=(i['cut_x'],i['cut_y']);iright=(i['right_x'],i['right_y']);itop=(i['top_x'],i['top_y']);ileft=(i['left_x'],i['left_y']);ijoin=(q['diagonal_inner'][0]*i['join_y']+q['diagonal_inner'][1],i['join_y']);itail=(q['diagonal_inner'][0]*q['base']+q['diagonal_inner'][1],q['base'])
    outer=[arc(join,left,unit(join[0]-tail[0],join[1]-tail[1]),(0,1),h[0]),arc(left,top,(0,1),(1,0),h[1]),arc(top,right,(1,0),(0,-1),h[2]),arc(right,cut,(0,-1),unit(-1,-o['cut_slope']),h[3])]
    inner=[arc(icut,iright,unit(1,i['cut_slope']),(0,1),k[3]),arc(iright,itop,(0,1),(-1,0),k[2]),arc(itop,ileft,(-1,0),(0,-1),k[1]),arc(ileft,ijoin,(0,-1),unit(itail[0]-ijoin[0],itail[1]-ijoin[1]),k[0])]
    if pieces:
        d.outline(tail,[join,ijoin,itail])
        starts=[join,left,top,right];inner_starts=[ileft,itop,iright,icut]
        for n in range(4):d.outline(starts[n],[outer[n],inner_starts[n],inner[3-n]])
    else:d.outline(tail,[join]+outer+[icut]+inner+[itail])
    return d



def lower(q, pieces=False):
    d=Drawing();o,i=q['outer'],q['inner'];h=o['handles'];k=i['handles'];bottom=(o['bottom_x'],0);left=(0,o['left_y']);join=(o['join_x'],o['join_y']);cut=(o['cut_x'],o['cut_y']);icut=(i['cut_x'],i['cut_y']);ijoin=(i['join_x'],i['join_y']);ileft=(i['left_x'],i['left_y']);ibottom=(i['bottom_x'],i['bottom_y']);ishoulder=(i['shoulder_x'],i['shoulder_y']);iright=(i['right_x'],i['right_y']);oright=(o['right_x'],o['right_y']);shoulder=(o['shoulder_x'],o['shoulder_y'])
    a=arc(bottom,left,(-1,0),(0,1),h[0]);b=arc(left,join,(0,1),unit(cut[0]-join[0],cut[1]-join[1]),h[1]);c=arc(ijoin,ileft,unit(ijoin[0]-icut[0],ijoin[1]-icut[1]),(0,-1),k[1]);e=arc(ileft,ibottom,(0,-1),(1,0),k[0]);f=arc(ibottom,ishoulder,(1,0),unit(1,i['shoulder_slope']),k[2]);g=arc(ishoulder,iright,unit(1,i['shoulder_slope']),(0,1),k[3]);j=arc(oright,shoulder,(0,-1),unit(-1,-o['shoulder_slope']),h[3]);m=arc(shoulder,bottom,unit(-1,-o['shoulder_slope']),(-1,0),h[2])
    if pieces:
        d.outline(bottom,[a,ileft,e]);d.outline(left,[b,ijoin,c]);d.outline(shoulder,[m,ibottom,f]);d.outline(oright,[j,ishoulder,g]);d.outline(iright,[(i['right_x'],q['cap']),(o['right_x'],q['cap']),oright])
    else:d.outline(bottom,[a,b,cut,icut,ijoin,c,e,f,g,(i['right_x'],q['cap']),(o['right_x'],q['cap']),oright,j,m])
    return d



def construction(p):
    d=Drawing();upper(p['upper'],pieces=True).replay(d.pen);lower(p['lower'],pieces=True).replay(d.pen);l,b,r,t=p['bounds'];out=Drawing();d.replay(out.pen,(r-l,0,0,t-b,l,b));return out


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/ampersand-ribbons.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='ampersand':return
    glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
