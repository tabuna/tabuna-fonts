#!/usr/bin/env python3
"""Measure selected reconstructed glyphs, with all unrelated data frozen."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
import pathops
import uharfbuzz as hb
from fontTools.agl import UV2AGL
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bowl_fit', ROOT/'scripts/reconstruct-bowls.py')
fit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fit)
pilot = fit.pilot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('characters')
    parser.add_argument('--control', type=Path, default=fit.OUT/'control.ttf')
    args = parser.parse_args()
    assert args.characters and all(c in '2З3' for c in args.characters)
    out = fit.OUT/('proof-'+''.join(f'{ord(c):04X}' for c in args.characters))
    out.mkdir(exist_ok=True)
    current = ROOT/'dist/TabunaSansVariable.ttf'
    a, b = TTFont(args.control), TTFont(current)
    added = set(b.getGlyphOrder())-set(a.getGlyphOrder())
    assert added <= {'three.small'}, added
    assert b.getGlyphOrder()[:len(a.getGlyphOrder())] == a.getGlyphOrder(), 'Public glyph IDs changed'
    roots = {UV2AGL.get(ord(ch), f'uni{ord(ch):04X}') for ch in args.characters}
    affected = set(roots)
    while True:
        dependents = {key for key in a.getGlyphOrder() if a['glyf'][key].isComposite()
                      and any(c.glyphName in affected for c in a['glyf'][key].components)}
        if dependents <= affected: break
        affected |= dependents
    changes = []
    for key in a.getGlyphOrder():
        assert a['hmtx'][key][0] == b['hmtx'][key][0], (key, 'advance changed')
        if a['glyf'][key].compile(a['glyf']) != b['glyf'][key].compile(b['glyf']): changes.append(key)
        if key not in affected:
            assert a['gvar'].variations[key] == b['gvar'].variations[key], (key, 'unrelated variation changed')
    assert set(changes) <= affected and roots <= set(changes), (changes, affected)
    tabular_proof = []
    if '3' in args.characters:
        for weight in (100, 400, 900):
            for size in (16, 64):
                runs = []
                for path in (args.control, current):
                    font = hb.Font(hb.Face(path.read_bytes()))
                    font.set_variations({'wght': weight, 'opsz': size})
                    buffer = hb.Buffer()
                    buffer.add_str('0123456789')
                    buffer.guess_segment_properties()
                    hb.shape(font, buffer, {'tnum': True})
                    runs.append(([a.codepoint for a in buffer.glyph_infos], [p.x_advance for p in buffer.glyph_positions]))
                assert runs[0] == runs[1] and len(set(runs[1][1])) == 1, (weight, size, 'tabular shaping changed')
                tabular_proof.append({'weight': weight, 'size': size, 'advance': runs[1][1][0]})
    cases = [(w, s) for w in (100, 400, 900) for s in (9, 14, 16, 20, 32, 64, 128)]
    cases += [(w, s) for w in (250, 700) for s in (16, 64)]
    rows = []
    for weight, size in cases:
        results = {}
        for version, path in (('before', args.control), ('after', current)):
            folder = out/f'{weight}-{size}'/version
            pilot.run([ROOT/'build/render-pairs', path, folder, size, args.characters, 2, weight, 'axis'])
            settings = json.loads((folder/'render-settings.json').read_text())
            results[version] = {}
            for record in settings['records']:
                assert record['tabuna']['renderedFonts'] == [settings['customPostScriptName']]
                ref = pilot.coverage(folder/record['system']['file'])
                own = pilot.coverage(folder/record['tabuna']['file'])
                m = pilot.metrics(ref, own)
                m['advance'] = record['tabuna']['advance']
                m['referenceSHA256'] = hashlib.sha256((folder/record['system']['file']).read_bytes()).hexdigest()
                results[version][record['character']] = m
                if weight == 400 and size == 64:
                    glyph_out = out/f'{ord(record["character"]):04X}'/version
                    glyph_out.mkdir(parents=True, exist_ok=True)
                    pilot.error_image(ref, own, glyph_out/'errors.png')
        glyphset = b.getGlyphSet(location={'wght': weight, 'opsz': size})
        if 'three.small' in added:
            old_glyphset = a.getGlyphSet(location={'wght': weight, 'opsz': size})
            for key in ('uni00B3', 'threequarters'):
                pens = [DecomposingRecordingPen(gs) for gs in (old_glyphset, glyphset)]
                for gs, pen in zip((old_glyphset, glyphset), pens): gs[key].draw(pen)
                assert len(pens[0].value) == len(pens[1].value), (key, 'derived contour structure changed')
                for (op0, pts0), (op1, pts1) in zip(pens[0].value, pens[1].value):
                    assert op0 == op1
                    np.testing.assert_allclose(pts0, pts1, rtol=0, atol=1e-9, err_msg=f'{key}/{weight}/{size}: derived geometry changed')
        for character in args.characters:
            before, after = results['before'][character], results['after'][character]
            assert before['referenceSHA256'] == after['referenceSHA256']
            assert after['advance'] == before['advance']
            assert after['inkIoU'] > before['inkIoU'], (character, weight, size, before, after)
            key = UV2AGL.get(ord(character), f'uni{ord(character):04X}')
            path = pathops.Path()
            glyphset[key].draw(path.getPen())
            assert len(list(pathops.simplify(path).contours)) == 1, (character, weight, size, 'topology')
            row = {'character': character, 'weight': weight, 'size': size, 'before': before, 'after': after,
                   'deltaInkIoU': after['inkIoU']-before['inkIoU']}
            rows.append(row)
            print(json.dumps({'glyph': character, 'weight': weight, 'size': size,
                              'before': before['inkIoU'], 'after': after['inkIoU']}, ensure_ascii=False), flush=True)
    for ch in args.characters:
        r = next(r for r in rows if r['character'] == ch and r['weight'] == 400 and r['size'] == 64)
        ref = pilot.coverage(out/'400-64/after'/f'{ord(ch):04X}-system.png')
        pilot.sheet([{'name': name, **r[name]} for name in ('before', 'after')], ref, out/f'{ord(ch):04X}')
    report = {'controlSHA256': hashlib.sha256(args.control.read_bytes()).hexdigest(),
              'acceptedSHA256': hashlib.sha256(current.read_bytes()).hexdigest(),
              'changedGlyphTables': changes, 'allowedAffectedGlyphs': sorted(affected),
              'addedPrivateGlyphs': sorted(added),
              'preservedDerivedGeometry': ['³', '¾'] if 'three.small' in added else [],
              'allAdvancesUnchanged': True, 'unrelatedGeometryAndVariationsUnchanged': True,
              'tabularDigitChecks': tabular_proof,
              'allCasesImprove': True, 'vectorTopologyAllCases': 'One connected closed path without holes', 'cases': rows,
              'binaryTopologyDifferences': [{'glyph': r['character'], 'weight': r['weight'], 'size': r['size'],
                                            'reference': r['after']['referenceTopology'], 'render': r['after']['renderTopology']}
                                           for r in rows if r['after']['referenceTopology'] != r['after']['renderTopology']]}
    fit.write(out/'report.json', report)


if __name__ == '__main__': main()
