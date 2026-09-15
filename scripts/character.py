"""Opt-in authored character, applied to our cubic model before compilation.

Positive handle scaling preserves endpoint tangent directions. Each family
has its own amplitude; optical size and weight attenuate decorative tension.
The baseline configuration is an exact no-op.
"""
import copy
import json
from math import log, tanh
from pathlib import Path

from fontTools.pens.recordingPen import RecordingPen
from geometry import Drawing
from parameters import at_location
import open_rounds
import lower_e
import e_reversed
import el_stem
import de_stem
import branched_stems
import diagonal_bands
import ya_bowl

INTENSITIES = {'baseline': 0.0, 'subtle': .45, 'moderate': 1.0, 'strong': 1.75}
# Independent optical families, including matching Cyrillic constructions.
ROUND_FAMILIES = {
    'round': ('o O о О 0', 1.0),
    'open': ('c C с С e е э Э', .8),
    'shoulder': ('b d p q б р ф Ф', .65),
    'double': ('B В в 8 3 З з', .5),
    'joined': ('a а g G D Q R P Р Б Ь ь Ы ы Ю ю Я я', .55),
}


def load():
    path = Path(__file__).resolve().parents[1]/'sources/character.json'
    data = json.loads(path.read_text()) if path.exists() else {'intensity': 'baseline'}
    if data['intensity'] not in INTENSITIES:
        raise ValueError('Unknown character intensity')
    return data


def replace(glyph, drawing):
    glyph.clearContours()
    glyph.clearComponents()
    drawing.replay(glyph.getPen())


def open_drawing(profile, construction):
    drawing = Drawing()
    for start, segments, counter in construction(profile['parameters'], profile['handles']):
        drawing.outline(start, segments, counter)
    l, b, r, t = profile['bounds']
    result = Drawing()
    drawing.replay(result.pen, (r-l, 0, 0, t-b, l, b))
    return result


def open_tips(parameters, amount):
    for outer, inner, delta in [('upperTipY', 'upperInnerY', amount),
                                 ('lowerTipY', 'lowerInnerY', -amount)]:
        parameters[inner] = parameters.get(inner, parameters[outer]) + delta
        parameters[outer] += delta


def tension(glyph, font, amount, right_relief=0):
    """Direct upper poles and handle lengths while retaining tangent directions."""
    bounds = glyph.getBounds(font)
    if bounds is None or not len(glyph):
        return 0
    l, b, r, t = bounds
    if r <= l or t <= b:
        return 0
    pen = RecordingPen(); glyph.draw(pen)
    # Move an upper horizontal pole and both adjacent handles together.
    # Side and lower poles remain fixed; both tangent directions are retained.
    # Apply the same displacement to outer and counter poles to protect weight.
    start = None; segments = []
    for index, (op, points) in enumerate(pen.value):
        if op == 'moveTo':
            start = index; segments = []
        elif op in ('lineTo', 'curveTo'):
            segments.append(index)
        elif op == 'closePath' and segments:
            for previous, following in zip(segments, segments[1:]+segments[:1]):
                po, pp = pen.value[previous]; no, np = pen.value[following]
                if po != 'curveTo' or no != 'curveTo': continue
                pole = pp[-1]
                wrap = following == segments[0]
                if wrap and pole != pen.value[start][1][0]: continue
                if pole[1] <= (b+t)/2: continue
                if abs(pp[-2][1]-pole[1]) > 1e-7 or abs(np[0][1]-pole[1]) > 1e-7: continue
                shift = lambda point: (point[0]+amount*.08*(r-l),point[1])
                pen.value[previous] = (po,(pp[0],shift(pp[1]),shift(pole)))
                pen.value[following] = (no,(shift(np[0]),np[1],np[2]))
                if wrap: pen.value[start] = ('moveTo',(shift(pole),))
    current = None; result = RecordingPen(); changed = 0
    for op, points in pen.value:
        if op == 'curveTo':
            assert len(points) == 3, 'Only cubic source geometry is supported'
            c1, c2, end = points
            x = ((current[0]+end[0])/2-l)/(r-l)
            y = ((current[1]+end[1])/2-b)/(t-b)
            upper = max(0, min(1, (y-.35)/.4))
            side = tanh(3*(x-.5))
            if side > 0:
                side *= 1-right_relief
            factor = 1 - amount * side * upper
            assert factor > 0
            c1 = tuple(a+(c-a)*factor for a, c in zip(current, c1))
            c2 = tuple(a+(c-a)*factor for a, c in zip(end, c2))
            result.curveTo(c1, c2, end); current = end
            changed += factor != 1
        else:
            getattr(result, op)(*points)
            if op in ('moveTo', 'lineTo'):
                current = points[-1]
    glyph.clearContours(); glyph.clearComponents(); result.replay(glyph.getPen())
    return changed


def silhouettes(font, strength):
    g = font['I']; l, b, r, t = g.getBounds(font); stem = r-l
    extension = min(45*strength, .82*min(l, g.width-r))
    thick = min(stem*.8, (t-b)*.13)
    d = Drawing()
    d.polygon([(l-extension,b),(l-extension,b+thick),(l,b+thick),
               (l,t-thick),(l-extension,t-thick),(l-extension,t),
               (r+extension,t),(r+extension,t-thick),(r,t-thick),
               (r,b+thick),(r+extension,b+thick),(r+extension,b)])
    replace(g,d)
    g = font['l']; l,b,r,t = g.getBounds(font); stem=r-l
    extension = min(43*strength, (g.width-r)*.80)
    thickness = stem*.88; radius = min(extension*.45, stem*.4)
    foot = r+extension; k=.5522847498307936
    d=Drawing()
    d.outline((l,t),[(r,t),(r,b+thickness+radius),
        ((r,b+thickness+radius*(1-k)),(r+radius*(1-k),b+thickness),(r+radius,b+thickness)),
        (foot,b+thickness),(foot,b),(l+radius,b),
        ((l+radius*(1-k),b),(l,b+radius*(1-k)),(l,b+radius))])
    replace(g,d)


def apply(font, design, config):
    strength = INTENSITIES[config['intensity']]
    if not strength:
        return
    cmap = {cp: g.name for g in font for cp in g.unicodes}
    weight, optical = design.weight, design.optical
    display = max(0, min(1, log(max(9,optical)/9)/log(128/9)))
    heavy = max(0, min(1, (weight-400)/500))
    amount = strength*.40*(.42+.58*display)*(1-.45*heavy)
    opening = strength*.014*(1.25-.25*display)
    for char, profiles in open_rounds.load().items():
        key = cmap.get(ord(char))
        if key is None: continue
        p=copy.deepcopy(at_location(profiles,design));open_tips(p['parameters'],opening)
        replace(font[key],open_drawing(p,open_rounds.contours))
    for char, profiles in lower_e.load().items():
        key = cmap.get(ord(char))
        if key is None: continue
        p=copy.deepcopy(at_location(profiles,design));q=p['parameters']
        release=opening*.8*(1+.5*heavy)
        q['tipInnerY']=q.get('tipInnerY',q['tipY'])-release;q['tipY']-=release
        q['crossY']+=(q['counterBottomY']-q['crossY'])*.08*strength*heavy
        replace(font[key],open_drawing(p,lower_e.contours))
    for key,profiles in e_reversed.load().items():
        if key not in font: continue
        p=copy.deepcopy(at_location(profiles,design));open_tips(p['parameters'],opening)
        replace(font[key],e_reversed.construction(p))
    silhouettes(font,strength)
    for key in ('uni041B','uni043B'):
        p=copy.deepcopy(at_location(el_stem.load()[key],design));foot=p['foot']
        foot['cut_x']=min(foot['inside_x']*.45, .023*strength)
        replace(font[key],el_stem.construction(p))
    for key in ('uni0414','uni0434'):
        p=copy.deepcopy(at_location(de_stem.load()[key],design))
        p['outer_cut']+=(p['inner_cut']-p['outer_cut'])*.06*strength
        replace(font[key],de_stem.construction(p))
    for key in ('uni0416','uni0436'):
        p=copy.deepcopy(at_location(branched_stems.load()[key],design))
        for i in range(2):p['caps'][i]+=(p['join'][i]-p['caps'][i])*.10*strength*heavy
        replace(font[key],branched_stems.construction(p))
    for key in ('uni041A','uni043A'):
        p=copy.deepcopy(at_location(diagonal_bands.load()[key],design))
        if 'floor' in p['upper']:
            p['upper']['floor']+=p['top']*.012*strength*heavy
        replace(font[key],diagonal_bands.construction(p))
    for key in ('uni042F','uni044F'):
        p=copy.deepcopy(at_location(ya_bowl.load()[key],design))
        p['inner']['bottom']-=(p['inner']['bottom']-p['bowl_bottom'])*.08*strength*heavy
        replace(font[key],ya_bowl.construction(p))
    for family,(chars,multiplier) in ROUND_FAMILIES.items():
        codepoints=set(map(ord,chars.replace(' ','')))
        for glyph in font:
            if codepoints.intersection(glyph.unicodes):
                relief=.22*max(0,min(1,(400-weight)/300)) if family=='round' else 0
                tension(glyph,font,amount*multiplier,right_relief=relief)
