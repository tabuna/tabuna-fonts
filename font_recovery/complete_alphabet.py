"""Measure scalar envelopes and ink area for the complete authored alphabet.

The reference is used only here. No reference contours enter design.json:
new letters retain the project's independently drawn skeletons. Area fitting
sets stroke color; it is deliberately not a claim of matching letter shapes.
"""
import hashlib
import argparse
import json
from pathlib import Path

import pathops
from scipy.optimize import minimize_scalar
from fontTools import subset
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from font_recovery.alphabet import draw_skeleton
from font_recovery.measure import Flatten
from font_recovery.model import DESIGN

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path('/System/Library/Fonts/SFNS.ttf')
ACCENTS = {'Ё': ('Е', 'dieresis'), 'ё': ('е', 'dieresis'),
           'Й': ('И', 'breve'), 'й': ('и', 'breve')}


def measure(font, character):
    glyph_set = font.getGlyphSet()
    name = font.getBestCmap()[ord(character)]
    bounds = BoundsPen(glyph_set)
    glyph_set[name].draw(bounds)
    path = pathops.Path()
    glyph_set[name].draw(path.getPen(glyph_set))
    path.simplify()
    return {'bbox': list(bounds.bounds), 'advance': font['hmtx'][name][0],
            'lsb': bounds.bounds[0]}, path.area


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--refit', action='store_true', help='Refit existing skeleton stroke scales after construction changes')
    args = parser.parse_args()
    design = json.loads(DESIGN.read_text())
    required = json.loads((DESIGN.parent / 'required-alphabet.json').read_text())
    characters = ''.join(row['character'] for row in required)
    font = TTFont(REFERENCE)
    options = subset.Options()
    options.layout_features = []
    selector = subset.Subsetter(options=options)
    selector.populate(text=characters)
    selector.subset(font)
    evidence = []
    for sample in design['samples']:
        location = sample['location']
        instance = instantiateVariableFont(font, location, inplace=False)
        profiles = sample['glyphs']
        for character in characters:
            if character in ACCENTS:
                continue
            if character in profiles and not (args.refit and profiles[character]['template'] == 'skeleton'):
                continue
            parameters, target_area = measure(instance, character)
            parameters.update(template='skeleton', weight=location['wght'],
                              stroke_scale=1.0, maturity='coverage; shape acceptance pending')

            def loss(strength):
                parameters['stroke_scale'] = float(strength)
                own = pathops.Path()
                draw_skeleton(own.getPen(), character, parameters)
                own.simplify()
                return ((own.area - target_area) / target_area) ** 2

            fit = minimize_scalar(loss, bounds=(.55, 1.65), method='bounded',
                                  options={'xatol': 1e-5})
            parameters['stroke_scale'] = float(fit.x)
            profiles[character] = parameters
            evidence.append({'character': character, 'location': location,
                             'reference_ink_area': target_area,
                             'relative_area_error': float(fit.fun ** .5),
                             'stroke_scale': float(fit.x)})
        for character, (base, accent) in ACCENTS.items():
            parameters, _ = measure(instance, character)
            glyph_set = instance.getGlyphSet()
            name = instance.getBestCmap()[ord(character)]
            flattened = Flatten(glyph_set)
            glyph_set[name].draw(flattened)
            base_top = profiles[base]['bbox'][3]
            accent_contours = [contour for contour in flattened.contours
                               if min(y for x, y in contour) > base_top]
            if not accent_contours:
                raise ValueError(f'Cannot isolate accent envelope for {character}')
            points = [point for contour in accent_contours for point in contour]
            accent_bounds = [min(x for x, y in points), min(y for x, y in points),
                             max(x for x, y in points), max(y for x, y in points)]
            parameters.update(template='accented', base=base, accent=accent,
                              dx=parameters['bbox'][0] - profiles[base]['bbox'][0],
                              accent_bbox=accent_bounds,
                              accent_stroke=(accent_bounds[3] - accent_bounds[1]) * .42,
                              maturity='coverage; accent shape acceptance pending')
            profiles[character] = parameters
        missing = set(characters) - profiles.keys()
        assert not missing, missing
        print(f"Weight {location['wght']:g}: {len(characters)}/{len(characters)} alphabet characters", flush=True)
    design['status'] = 'complete Latin/Russian alphabet; development geometry, full release acceptance pending'
    DESIGN.write_text(json.dumps(design, ensure_ascii=False, indent=2) + '\n')
    report = ROOT / 'build/font-recovery/reports/alphabet-construction.json'
    report.write_text(json.dumps({'reference_sha256': hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
                                  'method': 'Authored skeletons; scalar bbox, advance and nonzero ink-area fit',
                                  'shape_acceptance': False, 'fits': evidence},
                                 ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
