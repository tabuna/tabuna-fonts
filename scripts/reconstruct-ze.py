#!/usr/bin/env python3
"""Independent Cyrillic з: ordered raster boundary -> cubic bowls -> CoreText.

Three independent construction thresholds; evaluation always uses 0.5 for both
binary masks, plus the unchanged coverage IoU. No production font is mutated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from fontTools.fontBuilder import FontBuilder
from fontTools.agl import UV2AGL
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen

from ordered_contours import isocontours, signed_area, fit_section, contour_distances, unit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT/'build'/'ze-reconstruction'
# Semantic locations identify corresponding sections, not outline coordinates.
# Actual knots are selected on the ordered measured contour.
LANDMARKS = [
    ('upper_terminal_outer', .03, .25, 'corner'),
    ('outer_top', .48, .00, 'horizontal'),
    ('upper_outer_right', .96, .25, 'vertical'),
    ('waist_outer', .73, .49, 'corner'),
    ('lower_outer_right', 1., .73, 'vertical'),
    ('outer_bottom', .50, 1., 'horizontal'),
    ('lower_terminal_outer', .00, .78, 'corner'),
    ('lower_terminal_inner', .22, .78, 'corner'),
    ('inner_bottom', .50, .87, 'horizontal'),
    ('lower_inner_right', .79, .73, 'vertical'),
    ('lower_join', .51, .575, 'horizontal'),
    ('middle_terminal_bottom', .29, .575, 'corner'),
    ('middle_terminal_top', .29, .44, 'corner'),
    ('upper_join', .51, .44, 'horizontal'),
    ('upper_inner_right', .76, .25, 'vertical'),
    ('inner_top', .48, .13, 'horizontal'),
    ('upper_terminal_inner', .24, .25, 'corner'),
]


def run(args):
    subprocess.run([str(a) for a in args], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


def coverage(path):
    return 1-np.asarray(Image.open(path).convert('L'), dtype=float)/255


def bbox(mask):
    yy, xx = np.where(mask)
    return [int(xx.min()), int(yy.min()), int(xx.max()+1), int(yy.max()+1)] if len(xx) else None


def largest(mask):
    labels, n = ndimage.label(mask)
    return int(max(ndimage.sum(mask, labels, range(1, n+1)), default=0))


def topology(mask):
    return {'components': ndimage.label(mask)[1], 'holes': ndimage.label(ndimage.binary_fill_holes(mask) & ~mask)[1]}


def metrics(ref, own):
    a, b = ref >= .5, own >= .5
    fp, fn = b & ~a, a & ~b
    ae, be = a & ~ndimage.binary_erosion(a), b & ~ndimage.binary_erosion(b)
    da, db = ndimage.distance_transform_edt(~ae), ndimage.distance_transform_edt(~be)
    union = int((a | b).sum())
    contour = contour_distances(np.vstack(isocontours(ref)), np.vstack(isocontours(own)))
    boxa, boxb = bbox(a), bbox(b)
    diagonal = np.hypot(boxa[2]-boxa[0], boxa[3]-boxa[1])
    boxdiff = [b-a for a, b in zip(boxa, boxb)]
    iou = float(np.minimum(ref, own).sum()/np.maximum(ref, own).sum())
    result = {
        'inkIoU': iou, 'maskIoU': int((a & b).sum())/union,
        'fp': int(fp.sum()), 'fn': int(fn.sum()),
        'largestFP': largest(fp), 'largestFN': largest(fn),
        'bboxReference': boxa, 'bboxRender': boxb, 'bboxDelta': boxdiff,
        'boundaryDistance': float(db[ae].mean()),
        'symmetricBoundaryDistance': float((db[ae].mean()+da[be].mean())/2),
        'contourDistance': contour,
        'referenceTopology': topology(a), 'renderTopology': topology(b),
        'fnBeyond1_5px': int((fn & (db > 1.5)).sum()),
    }
    n = int(a.sum())
    result['loss'] = 1-iou+2*result['fn']/n+result['fp']/n+4*contour['symmetricMean']/diagonal+2*sum(abs(x) for x in boxdiff)/(4*diagonal)
    return result


def sections(ink, threshold, landmarks=LANDMARKS):
    loops = isocontours(ink, threshold)
    assert len(loops) == 1, 'Expected one connected, closed contour and no counter'
    loop = loops[0]
    # In image coordinates, top -> right -> bottom is positive winding.
    if signed_area(loop) < 0:
        loop = loop[::-1]
    lo, hi = loop.min(axis=0), loop.max(axis=0)
    normalized = (loop-lo)/(hi-lo)
    indices = [int(np.argmin(np.linalg.norm(normalized-[x, y], axis=1))) for _, x, y, _ in landmarks]
    start = indices[0]
    loop = np.roll(loop, -start, axis=0)
    indices = [(i-start) % len(loop) for i in indices]
    assert all(a < b for a, b in zip(indices, indices[1:])), ('Landmark order changed', indices)
    closed = np.vstack([loop, loop[0]])
    knots = [{'name': row[0], 'point': loop[i].tolist(), 'tangent': row[3]} for row, i in zip(landmarks, indices)]
    sections = []
    for section, (a, b) in enumerate(zip(indices, indices[1:]+[len(loop)])):
        points = closed[a:b+1]
        def endpoint_tangent(i, at_start):
            kind = landmarks[i % len(landmarks)][3]
            if kind == 'corner':
                return None
            axis = np.array([1., 0.] if kind == 'horizontal' else [0., 1.])
            direction = points[min(3, len(points)-1)]-points[0] if at_start else points[max(0, len(points)-4)]-points[-1]
            return axis*(1 if direction@axis >= 0 else -1)
        sections.append((points, endpoint_tangent(section, True), endpoint_tangent(section+1, False)))
    return loop, knots, sections


def reconstruct(ink, threshold, landmarks=LANDMARKS):
    loop, knots, parts = sections(ink, threshold, landmarks)
    pieces = []
    for section, (points, start_tangent, end_tangent) in enumerate(parts):
        fitted = fit_section(points, start_tangent, end_tangent)
        for item in fitted:
            item['section'] = landmarks[section][0]+' -> '+landmarks[(section+1) % len(landmarks)][0]
        pieces.extend(fitted)
    return {'threshold': threshold, 'landmarks': knots, 'segments': pieces, 'orderedContour': loop.tolist()}


def make_font(shape, settings, advance, path, character='з'):
    units = 2048/(settings['pointSize']*settings['pixelScale'])
    ox, oy = settings['originPixels']
    recording = RecordingPen()
    recording.moveTo(shape['segments'][0]['points'][0])
    for seg in shape['segments']:
        pts = [tuple(p) for p in seg['points']]
        if seg['kind'] == 'line': recording.lineTo(pts[-1])
        else: recording.curveTo(*pts[1:])
    recording.closePath()
    pen = TTGlyphPen(None)
    # Positive image winding becomes clockwise after the y-axis inversion.
    recording.replay(TransformPen(Cu2QuPen(pen, max_err=.5), (units, 0, 0, -units, -ox*units, oy*units)))
    glyph = pen.glyph()
    glyph.recalcBounds(None)
    empty = TTGlyphPen(None).glyph()
    key = UV2AGL.get(ord(character), f'uni{ord(character):04X}')
    fb = FontBuilder(2048, isTTF=True)
    fb.setupGlyphOrder(['.notdef', key])
    fb.setupCharacterMap({ord(character): key})
    fb.setupGlyf({'.notdef': empty, key: glyph})
    fb.setupHorizontalMetrics({'.notdef': (1024, 0), key: (round(advance*2048/settings['pointSize']), glyph.xMin)})
    fb.setupHorizontalHeader(ascent=2110, descent=-615)
    fb.setupNameTable({'familyName': 'Tabuna Ze Pilot', 'styleName': 'Regular', 'psName': 'TabunaZePilot-Regular', 'uniqueFontIdentifier': 'TabunaZePilot-'+str(shape['threshold'])})
    fb.setupOS2(sTypoAscender=2110, sTypoDescender=-615, usWinAscent=2110, usWinDescent=615)
    fb.setupPost()
    fb.save(path)


def error_image(ref, own, path):
    a, b = ref >= .5, own >= .5
    overlay = np.full((*ref.shape, 3), 255, dtype=np.uint8)
    overlay[a & b] = [160, 160, 160]
    overlay[a & ~b] = [240, 40, 40]
    overlay[b & ~a] = [35, 95, 245]
    Image.fromarray(overlay).save(path)


def sheet(rows, ref, out):
    box = bbox(ref >= .25)
    crop = (box[0]-8, box[1]-8, box[2]+8, box[3]+8)
    scale = 4
    w, h = (crop[2]-crop[0])*scale, (crop[3]-crop[1])*scale
    canvas = Image.new('RGB', (w*len(rows), h+100), 'white')
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 13)
    for i, row in enumerate(rows):
        im = Image.open(out/row['name']/'errors.png').crop(crop).resize((w, h), Image.Resampling.NEAREST)
        canvas.paste(im, (w*i, 0))
        label = f"{row['name']}\nIoU {row['inkIoU']:.6f}\nFP {row['fp']} / FN {row['fn']}\nmax FN {row['largestFN']}"
        draw.multiline_text((w*i+8, h+5), label, fill='black', font=font, spacing=3)
    canvas.save(out/'comparison.png')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT/'build/full-score/64')
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--threshold', type=float, choices=[.25, .5, .75])
    args = parser.parse_args()
    started = time.monotonic()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    settings = json.loads((args.source/'render-settings.json').read_text())
    record = next(r for r in settings['records'] if r['character'] == 'з')
    ref = coverage(args.source/record['system']['file'])
    own = coverage(args.source/record['tabuna']['file'])
    rows = []
    (out/'control').mkdir(exist_ok=True)
    error_image(ref, own, out/'control/errors.png')
    rows.append({'name': 'control', **metrics(ref, own)})
    for threshold in ([args.threshold] if args.threshold else (.25, .5, .75)):
        name = f'contour-{threshold:.2f}'
        folder = out/name
        folder.mkdir(exist_ok=True)
        Image.fromarray(np.uint8(ref >= threshold)*255).save(folder/'reference-mask.png')
        shape = reconstruct(ref, threshold)
        (folder/'geometry.json').write_text(json.dumps(shape, ensure_ascii=False, indent=2)+'\n')
        font = folder/'pilot.ttf'
        make_font(shape, settings, record['tabuna']['advance'], font)
        run([ROOT/'build/render-pairs', font, folder, settings['pointSize'], 'з', settings['pixelScale'], settings['weight'], 'axis'])
        generated = json.loads((folder/'render-settings.json').read_text())
        assert generated['originPixels'] == settings['originPixels']
        assert generated['canvas'] == settings['canvas']
        assert np.array_equal(ref, coverage(folder/'0437-system.png'))
        assert generated['records'][0]['tabuna']['renderedFonts'] == [generated['customPostScriptName']]
        own = coverage(folder/'0437-tabuna.png')
        error_image(ref, own, folder/'errors.png')
        row = {'name': name, 'constructionThreshold': threshold, 'evaluationThreshold': .5,
               'segments': len(shape['segments']), 'landmarks': len(shape['landmarks']), **metrics(ref, own)}
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    eligible = [r for r in rows[1:] if r['referenceTopology'] == r['renderTopology']
                and r['largestFN'] < rows[0]['largestFN'] and r['largestFP'] <= rows[0]['largestFP']
                and r['inkIoU'] > rows[0]['inkIoU']]
    selected = min(eligible, key=lambda r: r['loss']) if eligible else None
    report = {'glyph': 'з', 'controlFontSHA256': settings['fontSHA256'],
              'referenceSHA256': hashlib.sha256((args.source/record['system']['file']).read_bytes()).hexdigest(),
              'evaluation': 'Shared CoreText origin, grayscale AA; fixed 0.5 mask threshold; no image alignment.',
              'lossWeights': [1, 2, 1, 4, 2], 'rows': rows, 'selected': selected,
              'elapsedSeconds': time.monotonic()-started,
              'limitation': 'Raster isocontours are estimates; the unknown source vector cannot be recovered uniquely.'}
    (out/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    sheet(rows, ref, out)
    print(json.dumps({'selected': selected['name'] if selected else None, 'seconds': report['elapsedSeconds']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
