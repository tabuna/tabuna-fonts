"""Build weight variation from our compatible cubic template masters.

Cubic-to-quadratic subdivision is chosen for all masters together. Thus each
point has the same geometric role across weights, without copying source gvar.
"""
import json
import argparse
import hashlib
from pathlib import Path

from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuMultiPen
from fontTools.ttLib import TTFont
from fontTools.varLib import build
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.otlLib.builder import buildStatTable

from font_recovery.model import FontModel, DESIGN, require_alphabet
from font_recovery.generate_font import compile_sample, FIXED_TIMESTAMP

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/generated-font/tabuna-sans-variable'


def compatible_outlines(models):
    """Convert corresponding curves with a shared subdivision schedule."""
    results = [{} for _ in models]
    for character in models[0].glyphs:
        recordings = []
        for model in models:
            recording = RecordingPen()
            model.draw(character, recording)
            recordings.append(recording.value)
        signatures = [[operation for operation, _ in r] for r in recordings]
        assert all(s == signatures[0] for s in signatures), character
        pens = [TTGlyphPen(None) for _ in models]
        converter = Cu2QuMultiPen(pens, max_err=0.5)
        for commands in zip(*recordings):
            operation = commands[0][0]
            if operation in ('closePath', 'endPath'):
                getattr(converter, operation)()
            else:
                getattr(converter, operation)([arguments for _, arguments in commands])
        for result, pen in zip(results, pens):
            result[character] = pen.glyph()
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--development', action='store_true', help='Explicitly allow partial-alphabet experiments')
    parser.add_argument('--out', type=Path, default=OUT)
    args = parser.parse_args()
    out = args.out
    models = FontModel.load_all()
    if not args.development:
        require_alphabet(models)
    assert len(models) >= 3
    assert {m.location['opsz'] for m in models} == {28}
    assert {m.location['wdth'] for m in models} == {100}
    assert {m.location['GRAD'] for m in models} == {400}
    models.sort(key=lambda m: m.location['wght'])
    weights = [m.location['wght'] for m in models]
    assert weights == [100, 400, 800, 900], 'Full weight range requires measured masters through 900.'
    outlines = compatible_outlines(models)
    out.mkdir(parents=True, exist_ok=True)
    designspace = DesignSpaceDocument()
    axis = AxisDescriptor()
    axis.name, axis.tag = 'Weight', 'wght'
    axis.minimum, axis.default, axis.maximum = 100, 400, 900
    designspace.addAxis(axis)
    styles = {100: 'Thin', 400: 'Regular', 800: 'ExtraBold', 900: 'Black'}
    reports = []
    for model, glyphs in zip(models, outlines):
        weight = model.location['wght']
        path = out / 'masters' / f'W{weight:g}.ttf'
        reports.append(compile_sample({'location': model.location, 'glyphs': model.glyphs}, path, glyphs))
        source = SourceDescriptor()
        source.path = str(path)
        source.name = f'weight-{weight:g}'
        source.familyName = 'Tabuna Sans Development'
        source.styleName = styles[weight]
        source.location = {'Weight': weight}
        if weight == 400:
            source.copyInfo = source.copyLib = source.copyFeatures = True
        designspace.addSource(source)
        instance = InstanceDescriptor()
        instance.familyName = source.familyName
        instance.styleName = source.styleName
        instance.location = source.location
        designspace.addInstance(instance)
    designspace.write(out / 'TabunaSans.designspace')
    font, _, _ = build(designspace)
    names = {1: 'Tabuna Sans Development', 2: 'Regular',
             3: 'TabunaSansDevelopment-Variable-0.001',
             4: 'Tabuna Sans Development', 6: 'TabunaSansDevelopment-Variable',
             16: 'Tabuna Sans Development', 17: 'Regular'}
    for identifier, value in names.items():
        font['name'].setName(value, identifier, 3, 1, 0x409)
        font['name'].setName(value, identifier, 1, 0, 0)
    font['OS/2'].fsSelection = 64
    font['OS/2'].usWeightClass = 400
    font['head'].macStyle = 0
    buildStatTable(font, [{'tag': 'wght', 'name': 'Weight', 'values': [
        {'value': weight, 'name': styles[weight], 'flags': 2 if weight == 400 else 0}
        for weight in weights
    ]}])
    font['head'].created = font['head'].modified = FIXED_TIMESTAMP
    font.recalcTimestamp = False
    path = out / 'TabunaSansVariable.ttf'
    font.save(path)
    reopened = TTFont(path)
    assert all(tag in reopened for tag in ['fvar', 'gvar', 'STAT', 'HVAR'])
    for weight in [100, 250, 400, 600, 800, 850, 900]:
        instance = instantiateVariableFont(reopened, {'wght': weight}, inplace=False)
        assert len(instance.getBestCmap()) == len(models[0].glyphs) + 1
        assert all(advance > 0 for advance, _ in instance['hmtx'].metrics.values())
    webfont = TTFont(path, recalcTimestamp=False)
    webfont.flavor = 'woff2'
    web_path = path.with_suffix('.woff2')
    webfont.save(web_path)
    decoded = TTFont(web_path)
    assert decoded.getBestCmap() == reopened.getBestCmap()
    for name in reopened.getGlyphOrder():
        assert decoded['glyf'][name].getCoordinates(decoded['glyf']) == reopened['glyf'][name].getCoordinates(reopened['glyf'])
    (out / 'build-report.json').write_text(json.dumps({
        'status': f'development font; {len(models[0].glyphs)} glyphs, weight axis only',
        'font': str(path), 'masters': reports,
        'woff2': str(web_path),
        'source_model_sha256': hashlib.sha256(DESIGN.read_bytes()).hexdigest(),
        'font_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'instantiated_weights': [100, 250, 400, 600, 800, 850, 900],
        'source_gvar_copied': False,
    }, ensure_ascii=False, indent=2) + '\n')
    print(path)


if __name__ == '__main__':
    main()
