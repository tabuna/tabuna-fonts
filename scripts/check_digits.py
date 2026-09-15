#!/usr/bin/env python3
"""Check shaped numeral cells and filled intersections in the compiled font."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen


def check(path):
    data = path.read_bytes()
    font = TTFont(path)
    face = hb.Face(data)
    weights = [100, 250, 350, 400, 550, 650, 725, 800, 900]
    sizes = [9, 10.5, 12, 14, 16, 18, 20, 24, 28, 32, 40, 48, 64, 72, 96, 112, 128]
    failures = []
    counts = {'tnum': 0, 'pnum': 0}
    min_gap = float('inf')
    for w, o in itertools.product(weights, sizes):
        location = {'wght': w, 'opsz': o}
        gs = font.getGlyphSet(location=location)
        hfont = hb.Font(face)
        hfont.set_variations(location)
        recordings = {}
        for feature in counts:
            advances = set()
            for a, b in itertools.product('0123456789', repeat=2):
                buffer = hb.Buffer()
                buffer.add_str(a+b)
                buffer.guess_segment_properties()
                hb.shape(hfont, buffer, {feature: True})
                paths = []
                x = 0
                for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions):
                    name = font.getGlyphName(info.codepoint)
                    if name not in recordings:
                        rec = DecomposingRecordingPen(gs)
                        gs[name].draw(rec)
                        recordings[name] = rec
                    shape = pathops.Path()
                    recordings[name].replay(TransformPen(shape.getPen(), (1,0,0,1,x+pos.x_offset,pos.y_offset)))
                    paths.append(shape)
                    x += pos.x_advance
                    advances.add(pos.x_advance)
                assert len(paths) == 2
                gap = paths[1].bounds[0] - paths[0].bounds[2]
                area = 0 if gap > 0 else abs(pathops.op(paths[0],paths[1],pathops.PathOp.INTERSECTION).area)
                if feature == 'tnum':
                    min_gap = min(min_gap, gap)
                if area > .5 or (feature == 'tnum' and gap < 100):
                    failures.append(dict(location=location, text=a+b, feature=feature, gap=gap, area=area))
                counts[feature] += 1
            if feature == 'tnum' and len(advances) != 1:
                failures.append(dict(location=location, unequal_advances=sorted(advances)))
    return dict(font_sha256=hashlib.sha256(data).hexdigest(), cases=counts,
                locations=len(weights)*len(sizes), min_tabular_gap_font_units=min_gap,
                failures=failures, passed=not failures)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--font', type=Path, default=Path('dist/TabunaSansVariable.ttf'))
    parser.add_argument('--output', type=Path, default=Path('reports/digit-verification.json'))
    args=parser.parse_args()
    report=check(args.font)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='failures'}, indent=2))
    print('Failures:', len(report['failures']))
    raise SystemExit(0 if report['passed'] else 1)
