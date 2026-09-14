"""Six symmetric tapered rays, described by lengths, angle and widths."""
import json
from functools import lru_cache
from math import cos,sin,pi
from pathlib import Path
from geometry import Drawing
from parameters import at_location


def polygons(p):
    rays=[]
    for angle,role in [(pi/2,'vertical'),(-pi/2,'vertical'),(p['angle'],'diagonal'),(-p['angle'],'diagonal'),(pi-p['angle'],'diagonal'),(pi+p['angle'],'diagonal')]:
        q=p[role];u=(cos(angle),sin(angle));n=(-u[1],u[0]);cx,cy=p['x'],p['y']
        rays.append([(cx+u[0]*l+n[0]*w,cy+u[1]*l+n[1]*w) for l,w in [(0,-q['inner']/2),(q['length'],-q['outer']/2),(q['length'],q['outer']/2),(0,q['inner']/2)]])
    return rays


def construction(p):
    d=Drawing()
    for points in polygons(p):d.polygon(points)
    return d


@lru_cache(maxsize=1)
def load():return json.loads((Path(__file__).resolve().parents[1]/'sources/asterisk-rays.json').read_text())['weights']


def apply(glyph,key,design):
    if key!='asterisk':return
    glyph.clearContours();construction(at_location(load(),design)).replay(glyph.getPen())
