"""Measured proportions applied to our original source contours.

The data contains scalar dimensions and spacing, never reference paths.
Vertical zones preserve the baseline and lowercase body while correcting
ascenders and descenders independently.
"""
import json
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/'sources/metrics.json'


def load():
    return json.loads(PATH.read_text())['glyphs'] if PATH.exists() else {}


def linear(value,knots):
    for i in range(len(knots)-1):
        a,b=knots[i:i+2]
        if value<=b[0] or i==len(knots)-2:
            return a[1]+(value-a[0])*(b[1]-a[1])/(b[0]-a[0])
    return value


def coefficients(data,key,display):
    if key not in data:key={'dotlessi':'i','dotlessj':'j'}.get(key,key)
    if key not in data:return None
    a,b=data[key]['text'],data[key]['display']
    def blend(field):return a[field]+display*(b[field]-a[field])
    return {'sx':blend('sx'),'dx':blend('dx'),
            'baseAdvance':blend('baseAdvance'),'advance':blend('advance'),
            'y':lambda y:linear(y,a['y'])*(1-display)+linear(y,b['y'])*display}


def apply(glyph,transform):
    if not transform:return
    for contour in glyph.contours:
        for point in contour.points:
            point.x=point.x*transform['sx']+transform['dx']
            point.y=transform['y'](point.y)
    glyph.width=transform['advance']+(glyph.width-transform['baseAdvance'])*transform['sx']
