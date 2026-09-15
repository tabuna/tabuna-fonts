#!/usr/bin/env python3
"""Certify that the numeral fix preserves every proportional glyph continuously."""
import argparse
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_scope(before, after):
    a, b = TTFont(before), TTFont(after)
    assert a.getGlyphOrder() == b.getGlyphOrder()
    assert a.getBestCmap() == b.getBestCmap()
    changed = {'glyf': [], 'gvar': [], 'hmtx': []}
    for name in a.getGlyphOrder():
        if a['glyf'][name].compile(a['glyf']) != b['glyf'][name].compile(b['glyf']):
            changed['glyf'].append(name)
        va = [(v.axes,v.coordinates) for v in a['gvar'].variations.get(name,[])]
        vb = [(v.axes,v.coordinates) for v in b['gvar'].variations.get(name,[])]
        if va != vb: changed['gvar'].append(name)
        if a['hmtx'][name] != b['hmtx'][name]: changed['hmtx'].append(name)
    allowed = {n for n in a.getGlyphOrder() if n.endswith('.tnum')}
    assert len(allowed) == 10
    assert all(set(names) <= allowed for names in changed.values()), changed
    table_changes = []
    for tag in a.keys():
        if tag == 'GlyphOrder': continue
        if a.getTableData(tag) != b.getTableData(tag): table_changes.append(tag)
    assert set(table_changes) <= {'glyf','gvar','hmtx','loca','head','name','hhea','OS/2'}, table_changes
    for tag, allowed_fields in [('head',{'checkSumAdjustment','fontRevision'}),
                               ('hhea',{'advanceWidthMax','minLeftSideBearing','minRightSideBearing','xMaxExtent'}),
                               ('OS/2',{'xAvgCharWidth'})]:
        normal = lambda v: vars(v) if hasattr(v, '__dict__') else v
        fields = {k for k in vars(a[tag]) if normal(vars(a[tag])[k]) != normal(vars(b[tag])[k])}
        assert fields <= allowed_fields, (tag,fields)
    na={(n.nameID,n.platformID,n.platEncID,n.langID):n.toUnicode() for n in a['name'].names}
    nb={(n.nameID,n.platformID,n.platEncID,n.langID):n.toUnicode() for n in b['name'].names}
    assert na.keys() == nb.keys()
    assert {k[0] for k in na if na[k]!=nb[k]} <= {3,5}
    return dict(before_sha256=digest(before), font_sha256=digest(after), passed=True,
                changed_glyphs=changed, changed_tables=table_changes,
                proportional_glyphs_and_advances_unchanged=True,
                continuous_variation_data_unchanged_outside_tabular_digits=True,
                version=b['name'].getDebugName(5),unique_id=b['name'].getDebugName(3),
                head_revision=b['head'].fontRevision)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--before',type=Path,required=True)
    parser.add_argument('--after',type=Path,default=Path('dist/TabunaSansVariable.ttf'))
    parser.add_argument('--output',type=Path,default=Path('reports/tabular-scope.json'))
    args=parser.parse_args()
    report=check_scope(args.before,args.after)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
