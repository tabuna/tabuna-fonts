#!/usr/bin/env python3
"""Recompile our floating-point UFO sources at higher precision in isolation.

No deployed font or canonical source master is overwritten. Measured tracking
and existing rounded kerning scale exactly; this experiment isolates outline
and advance quantization rather than refitting either spacing field.
"""
import argparse
import json
from pathlib import Path
import build

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('upm', type=int, choices=(4096, 8192, 16384))
    parser.add_argument('--compile-only', action='store_true')
    args = parser.parse_args()
    folder = ROOT/'build/upm-experiment'/str(args.upm)
    source = folder/'sources'
    source.mkdir(parents=True, exist_ok=True)
    factor = args.upm//2048
    data = json.loads((ROOT/'sources/tracking.json').read_text())
    assert data['unitsPerEm'] == 2048
    data['experiment'] = {'originalUnitsPerEm': 2048, 'scale': factor,
                          'scope': 'Exact rescaling of existing integer tracking; no refit'}
    data['unitsPerEm'] = args.upm
    for row in data['records']:
        for key in ('fontUnits', 'measuredFontUnits', 'roundingErrorFontUnits'):
            row[key] *= factor
    (source/'tracking.json').write_text(json.dumps(data, indent=2)+'\n')
    (source/'optical-map.json').write_bytes((ROOT/'sources/optical-map.json').read_bytes())
    original_scale = build.scale_source

    def scale(font):
        original_scale(font)
        for glyph in font:
            glyph.width *= factor
            for contour in glyph.contours:
                for point in contour.points:
                    point.x *= factor
                    point.y *= factor
            for component in glyph.components:
                a, b, c, d, e, f = component.transformation
                component.transformation = a, b, c, d, e*factor, f*factor
            for anchor in glyph.anchors:
                anchor.x *= factor
                anchor.y *= factor
        for pair, value in list(font.kerning.items()):
            font.kerning[pair] = value*factor
        for key in ('unitsPerEm', 'ascender', 'descender', 'capHeight', 'xHeight',
                    'openTypeOS2TypoAscender', 'openTypeOS2TypoDescender', 'openTypeOS2TypoLineGap',
                    'openTypeOS2WinAscent', 'openTypeOS2WinDescent', 'openTypeHheaAscender',
                    'openTypeHheaDescender', 'openTypeHheaLineGap', 'postscriptUnderlinePosition',
                    'postscriptUnderlineThickness'):
            value = getattr(font.info, key)
            if value is not None:
                setattr(font.info, key, round(value*factor))

    build.ROOT, build.SOURCES, build.DIST = folder, source, folder/'dist'
    build.scale_source = scale
    if not args.compile_only:
        build.generate()
    build.compile_font()


if __name__ == '__main__':
    main()
