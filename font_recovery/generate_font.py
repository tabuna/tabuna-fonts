"""Compile Tabuna Sans from its own parameter model.

The compiler imports no reference font or legacy glyph code. Measurements and
font generation are separate so the checked-in design is sufficient to build.
"""
import argparse
import hashlib
import json
from pathlib import Path

from fontTools.agl import UV2AGL
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.filterPen import FilterPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps

from font_recovery.model import FontModel, DESIGN, require_alphabet
from font_recovery.primitives import rectangle, oval

ROOT = Path(__file__).resolve().parents[1]
FIXED_TIMESTAMP = 3850070400
CURVE_ERROR = 0.5  # Maximum cubic-to-quadratic conversion error, in font units.


class RemoveDegeneratePen(FilterPen):
    """Drop zero-length segments introduced by integer-rounded boolean joins."""
    def moveTo(self, point):
        self.current = point
        super().moveTo(point)

    def lineTo(self, point):
        if point != self.current:
            super().lineTo(point)
        self.current = point

    def qCurveTo(self, *points):
        if any(point != self.current for point in points):
            super().qCurveTo(*points)
        self.current = points[-1]


def clean_static_outlines(font):
    """Reach a stable integer outline after boolean union and quantization.

    Rounding a newly intersected curve can collapse a tiny contour. A second
    union then removes that artifact; stop as soon as coordinates stabilize.
    Compatible variable masters deliberately use a separate construction.
    """
    def signature():
        return [(name, glyph.numberOfContours, tuple(glyph.getCoordinates(font['glyf'])[0]),
                 tuple(glyph.endPtsOfContours) if glyph.numberOfContours > 0 else (),
                 tuple(glyph.flags) if glyph.numberOfContours > 0 else ())
                for name in font.getGlyphOrder() for glyph in [font['glyf'][name]]]

    for _ in range(8):
        previous = signature()
        removeOverlaps(font, removeHinting=True)
        glyph_set = font.getGlyphSet()
        clean = {}
        for name in font.getGlyphOrder():
            pen = TTGlyphPen(glyph_set)
            glyph_set[name].draw(RemoveDegeneratePen(pen))
            clean[name] = pen.glyph()
        for name, glyph in clean.items():
            font['glyf'][name] = glyph
        if signature() == previous:
            return
    raise ValueError('Static outline union did not stabilize after integer quantization')


def missing_glyph():
    pen = TTGlyphPen(None)
    rectangle(pen, 80, 0, 900, 1443)
    oval(Cu2QuPen(pen, max_err=CURVE_ERROR), [260, 220, 720, 1223], .55, .55, True)
    return pen.glyph()


def validate_compilation(path, names):
    """Check reopened binary tables, not just the drawing commands."""
    font = TTFont(path)
    glyph_set = font.getGlyphSet()
    records = []
    for character, name in names.items():
        assert font.getBestCmap()[ord(character)] == name
        glyph = font['glyf'][name]
        area, bounds = AreaPen(glyph_set), BoundsPen(glyph_set)
        glyph_set[name].draw(area)
        glyph_set[name].draw(bounds)
        assert bounds.bounds and area.value < 0, (character, area.value, bounds.bounds)
        assert font['hmtx'][name][0] > 0 and glyph.numberOfContours > 0
        coordinates, _, _ = glyph.getCoordinates(font['glyf'])
        assert all(-32768 <= value <= 32767 for point in coordinates for value in point)
        records.append({
            'glyph': character,
            'contours': glyph.numberOfContours,
            'points': len(coordinates),
            'bbox': bounds.bounds,
            'signed_area': area.value,
            'advance': font['hmtx'][name][0],
        })
    return list(font.keys()), records


def compile_sample(sample, out, compatible_glyphs=None):
    """Compile one measured location; optionally use jointly subdivided masters."""
    model = FontModel(**sample)
    names = {character: UV2AGL.get(ord(character), f'uni{ord(character):04X}')
             for character in model.glyphs}
    glyphs = {'.notdef': missing_glyph()}
    metrics = {'.notdef': (980, 80)}
    for character, parameters in model.glyphs.items():
        pen = TTGlyphPen(None)
        model.draw(character, Cu2QuPen(pen, max_err=CURVE_ERROR))
        name = names[character]
        glyphs[name] = pen.glyph() if compatible_glyphs is None else compatible_glyphs[character]
        if compatible_glyphs is not None and parameters['template'] in ('skeleton', 'accented'):
            # The compatible ribbon construction contains deliberate unions.
            # Signal nonzero overlap handling to TrueType rasterizers.
            glyphs[name].flags[0] |= 0x40  # OVERLAP_SIMPLE
        metrics[name] = model.advance(character), round(parameters['bbox'][0])
    glyphs['space'] = TTGlyphPen(None).glyph()
    metrics['space'] = 512, 0

    builder = FontBuilder(model.units_per_em, isTTF=True)
    builder.setupGlyphOrder(['.notdef', 'space'] + list(names.values()))
    builder.setupCharacterMap({32: 'space', **{ord(c): name for c, name in names.items()}})
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(ascent=1980, descent=-432, lineGap=0)

    weight = round(model.location['wght'])
    optical = model.location['opsz']
    style = f'W{weight} O{optical:g}'
    builder.setupNameTable({
        'familyName': 'Tabuna Sans Development',
        'styleName': style,
        'uniqueFontIdentifier': f'TabunaSansDevelopment-{weight}-{optical:g}-v1',
        'fullName': f'Tabuna Sans Development {style}',
        'psName': f'TabunaSansDevelopment-W{weight}-O{optical:g}',
        'version': 'Version 0.001',
        'manufacturer': 'Tabuna Sans Project',
        'description': 'Independent parametric construction; incomplete development font.',
    })
    builder.setupOS2(
        sTypoAscender=1980, sTypoDescender=-432, sTypoLineGap=0,
        usWinAscent=1980, usWinDescent=432,
        sxHeight=round(model.glyphs['n']['x_height']), sCapHeight=1443,
        usWeightClass=weight, fsType=0, achVendID='TBNA',
    )
    builder.setupPost()
    builder.setupMaxp()
    font = builder.font
    if compatible_glyphs is None:
        clean_static_outlines(font)
    font['head'].created = font['head'].modified = FIXED_TIMESTAMP
    font.recalcTimestamp = False
    out.parent.mkdir(parents=True, exist_ok=True)
    font.save(out)

    tables, records = validate_compilation(out, names)
    return {
        'font': str(out),
        'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
        'location': model.location,
        'tables': tables,
        'glyphs': records,
        'status': 'compiled and reopened; raster and full coverage checks separate',
        'overlap_handling': 'fontTools.removeOverlaps / skia-pathops for static builds; separate validation for compatible masters',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--design', type=Path, default=DESIGN)
    parser.add_argument('--out', type=Path, default=ROOT / 'build/generated-font/tabuna-sans')
    parser.add_argument('--development', action='store_true', help='Explicitly allow partial-alphabet experiments')
    args = parser.parse_args()
    data = json.loads(args.design.read_text())
    if not args.development:
        require_alphabet([FontModel(**sample) for sample in data['samples']])
    reports = []
    for sample in data['samples']:
        weight, optical = sample['location']['wght'], sample['location']['opsz']
        path = args.out / f'TabunaSans-W{weight:g}-O{optical:g}.ttf'
        reports.append(compile_sample(sample, path))
    (args.out / 'build-report.json').write_text(json.dumps(
        {'scope': data['status'], 'fonts': reports}, ensure_ascii=False, indent=2,
    ) + '\n')
    print(json.dumps({'fonts': len(reports), 'output': str(args.out)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
