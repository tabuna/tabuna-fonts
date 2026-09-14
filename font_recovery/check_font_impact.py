"""Prove the scope of a geometry change across the continuous designspace."""
import argparse
import hashlib
import json
from pathlib import Path
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont


def variations(font, name, phantom_only=False):
    result = []
    for variation in font['gvar'].variations[name]:
        coordinates = variation.coordinates[-4:] if phantom_only else variation.coordinates
        values = tuple(coordinates)
        if phantom_only and all(value in (None, (0, 0)) for value in values):
            continue
        support = tuple(sorted(variation.axes.items()))
        # Tracking can add a second tuple with the same support. Retain every
        # tuple rather than overwriting an earlier outline or metric delta.
        result.append((support, values))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    parser.add_argument('--characters', required=True)
    parser.add_argument('--colon-context-layout', action='store_true', help='Independently certify the exact Cyrillic contextual-colon GSUB rule and new zero kern pairs')
    parser.add_argument('--unit-components', default='', help='Explicit subset of appended helper names used at unit scale; all others must be half scale')
    parser.add_argument('--gsub-variants', default='', help='Explicit unencoded single-substitution derivatives of the declared characters; audit their shaping contexts separately')
    parser.add_argument('--added-components', default='', help='Comma-separated new unencoded helper glyphs appended after all existing IDs')
    parser.add_argument('--allow-bearing-changes', action='store_true',
                        help='Permit changed ink bearings only in the intended glyphs and their components; advances must remain equal')
    parser.add_argument('--allow-derived-maxp', action='store_true',
                        help='Allow outline-derived maxima only after independently recalculating them for both fonts')
    parser.add_argument('--allow-derived-hhea', action='store_true',
                        help='Allow recalculated horizontal ink extrema; all other hhea fields must remain equal')
    parser.add_argument('--allow-advance-changes', action='store_true',
                        help='Permit measured advance corrections only in the explicitly intended glyphs')
    parser.add_argument('--before-full', type=Path)
    parser.add_argument('--after-full', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    before, after = TTFont(args.before), TTFont(args.after)
    assert before.getBestCmap() == after.getBestCmap(), 'Unicode map changed'
    added = [name for name in args.added_components.split(',') if name]
    assert after.getGlyphOrder() == before.getGlyphOrder()+added, 'Existing IDs changed or unexpected helpers added'
    assert not set(added) & set(after.getBestCmap().values()), 'Helpers must be unencoded'
    assert not set(added) & set(before.getGlyphOrder())

    allowed = {before.getBestCmap()[ord(character)] for character in args.characters}
    unit_components=set(filter(None,args.unit_components.split(',')))
    assert unit_components<=set(added), 'Unit helpers must be explicitly appended'
    variants = [name for name in args.gsub_variants.split(',') if name]
    variant_links = {}
    for variant in variants:
        assert variant in before.getGlyphOrder() and variant not in before.getBestCmap().values(), 'Variant must be existing and unencoded'
        links = []
        for font in (before, after):
            parents = set()
            for lookup in font['GSUB'].table.LookupList.Lookup:
                for table in lookup.SubTable:
                    table = getattr(table, 'ExtSubTable', table)
                    parents.update(source for source, target in getattr(table, 'mapping', {}).items() if target == variant)
            assert parents and parents <= allowed, 'Variant must substitute only declared base glyphs'
            links.append(sorted(parents))
        assert links[0] == links[1], 'Variant substitution relation changed'
        variant_links[variant] = links[0]
    allowed.update(variants)
    if added:
        referenced=set()
        for name in after.getGlyphOrder():
            glyph=after['glyf'][name]
            for component in getattr(glyph,'components',[]):
                if component.glyphName in added:
                    assert name in allowed, 'New helper used outside the declared glyphs'
                    scale=1 if component.glyphName in unit_components else .5
                    assert component.getComponentInfo()[1] == (scale,0,0,scale,0,0), 'Unexpected helper transform'
                    referenced.add(component.glyphName)
        assert referenced==set(added), 'Unused or missing helper'
    affected = set(allowed)

    while True:
        previous = affected.copy()
        for name in before.getGlyphOrder():
            glyph = before['glyf'][name]
            if glyph.isComposite() and any(component.glyphName in affected for component in glyph.components):
                affected.add(name)
        if affected == previous:
            break
    bearing_changes = {}
    advance_changes = {}
    for name, (advance, bearing) in before['hmtx'].metrics.items():
        new_advance, new_bearing = after['hmtx'][name]
        if advance != new_advance:
            assert args.allow_advance_changes and name in allowed, f'Unexpected advance change: {name}'
            advance_changes[name] = [advance, new_advance]
        if bearing != new_bearing:
            assert args.allow_bearing_changes and name in affected, f'Unexpected bearing change: {name}'
            bearing_changes[name] = [bearing, new_bearing]
    assert set(before.keys()) == set(after.keys()), 'Table repertoire changed'
    tables = [tag for tag in before.keys() if tag not in
              ('GlyphOrder', 'glyf', 'gvar', 'loca', 'head')]
    if bearing_changes or advance_changes or added:
        tables.remove('hmtx')
    if added:
        # Validate the only header/storage changes caused by appended helpers.
        for font in (before,after):
            advances=[font['hmtx'][name][0] for name in font.getGlyphOrder()]
            count=len(advances)
            while count>1 and advances[count-1]==advances[count-2]:count-=1
            assert font['hhea'].numberOfHMetrics==count
            assert font['maxp'].numGlyphs==len(font.getGlyphOrder())
        count=after['hhea'].numberOfHMetrics
        after['hhea'].numberOfHMetrics=before['hhea'].numberOfHMetrics
        if not args.allow_derived_hhea:assert before['hhea'].compile(before)==after['hhea'].compile(after)
        after['hhea'].numberOfHMetrics=count
        if not args.allow_derived_hhea:tables.remove('hhea')
        for field,value in before['post'].__dict__.items():
            if field=='extraNames':
                assert after['post'].extraNames==value+added
            elif field=='glyphOrder':
                assert after['post'].glyphOrder==value+added
            else:assert after['post'].__dict__.get(field)==value, f'Unexpected post change: {field}'
        tables.remove('post')
    derived_maxp_changes = {}
    derived_average_width = None
    if before['OS/2'].xAvgCharWidth != after['OS/2'].xAvgCharWidth:
        assert (args.allow_advance_changes or added) and args.before_full and args.after_full, 'Average width change requires full-source evidence'
        averages = []
        for font, path in ((before, args.before_full), (after, args.after_full)):
            full = TTFont(path)
            assert all(full['hmtx'][name] == font['hmtx'][name] for name in font.getGlyphOrder())
            actual = font['OS/2'].xAvgCharWidth
            assert actual == full['OS/2'].xAvgCharWidth == full['OS/2'].recalcAvgCharWidth(full)
            averages.append(actual)
        # Compare every other OS/2 field as bytes, then restore the measured value.
        after['OS/2'].xAvgCharWidth = averages[0]
        assert before['OS/2'].compile(before) == after['OS/2'].compile(after), 'Other OS/2 fields changed'
        after['OS/2'].xAvgCharWidth = averages[1]
        tables.remove('OS/2')
        derived_average_width = {'values': averages, 'full_sources': [str(args.before_full), str(args.after_full)]}
    if args.allow_derived_maxp:
        derived = {'maxPoints', 'maxContours', 'maxCompositePoints',
                   'maxCompositeContours', 'maxComponentElements', 'maxComponentDepth'}
        if added:derived.add('numGlyphs')
        originals = [dict(font['maxp'].__dict__) for font in (before, after)]
        for font, original in zip((before, after), originals):
            font['maxp'].recalc(font)
            for field in derived:
                assert original[field] == getattr(font['maxp'], field), f'Incorrect derived maxp: {field}'
        for field in set(originals[0]) | set(originals[1]):
            a, b = originals[0].get(field), originals[1].get(field)
            if a != b:
                assert field in derived, f'Non-outline maxp changed: {field}'
                derived_maxp_changes[field] = [a, b]
        tables.remove('maxp')
    derived_hhea_changes = {}
    if args.allow_derived_hhea:
        derived = {'advanceWidthMax', 'minLeftSideBearing', 'minRightSideBearing', 'xMaxExtent'}
        if added:derived.add('numberOfHMetrics')  # Independently counted above.
        originals = [dict(font['hhea'].__dict__) for font in (before, after)]
        for font, original in zip((before, after), originals):
            font['hhea'].recalc(font)
            for field in derived:
                assert original[field] == getattr(font['hhea'], field), f'Incorrect derived hhea: {field}'
        for field in set(originals[0]) | set(originals[1]):
            a, b = originals[0].get(field), originals[1].get(field)
            if a != b:
                assert field in derived, f'Non-outline hhea changed: {field}'
                derived_hhea_changes[field] = [a, b]
        tables.remove('hhea')
    layout_proof=None
    if args.colon_context_layout:
        from font_recovery.colon_layout import verify
        layout_proof=verify(before,after)
        tables.remove('GSUB');tables.remove('GPOS')
    for tag in tables:
        assert before[tag].compile(before) == after[tag].compile(after), tag
    for field in ('unitsPerEm', 'flags', 'macStyle', 'lowestRecPPEM', 'fontDirectionHint'):
        assert getattr(before['head'], field) == getattr(after['head'], field), field
    changed = []
    variable_metric_changes = []
    for name in before.getGlyphOrder():
        recordings = []
        for font in (before, after):
            pen = RecordingPen()
            font['glyf'][name].draw(pen, font['glyf'])
            recordings.append(pen.value)
        same_outline = recordings[0] == recordings[1]
        same_variation = variations(before, name) == variations(after, name)
        if not (same_outline and same_variation):
            changed.append(name)
            assert name in allowed, f'Unexpected direct geometry change: {name}'
        if variations(before, name, True) != variations(after, name, True):
            assert args.allow_advance_changes and name in allowed, f'Unexpected variable phantom metrics change: {name}'
            variable_metric_changes.append(name)
    report = {
        'before': str(args.before), 'after': str(args.after),
        'before_sha256': hashlib.sha256(args.before.read_bytes()).hexdigest(),
        'after_sha256': hashlib.sha256(args.after.read_bytes()).hexdigest(),
        'directly_changed_glyphs': changed, 'including_components': sorted(affected),
        'coverage': len(before.getBestCmap()), 'glyphs': len(after.getGlyphOrder()),
        'added_unencoded_half_scale_components': added,
        'verified_gsub_variant_relations': variant_links,
        'appended_unit_scale_helpers': sorted(unit_components),
        'verified_colon_layout_extension': layout_proof,
        'identical_tables': tables, 'default_and_variable_metrics_equal': not (bearing_changes or advance_changes or variable_metric_changes),
        'default_advances_and_variable_phantom_deltas_equal': not (advance_changes or variable_metric_changes),
        'intentional_advance_changes': advance_changes,
        'intentional_variable_metric_changes': variable_metric_changes,
        'intentional_ink_bearing_changes': bearing_changes,
        'verified_derived_maxp_changes': derived_maxp_changes,
        'verified_derived_hhea_changes': derived_hhea_changes,
        'verified_derived_average_width': derived_average_width,
        'proof': 'Default drawing commands and all gvar support/delta data equal outside allowed glyphs; applies to the whole continuous designspace',
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
