"""Replace empty-space advance models, leaving all visible glyphs untouched."""
from fontTools.varLib.builder import buildVarData,buildVarIdxMap,buildVarRegionList
from fontTools.ttLib.tables.TupleVariation import TupleVariation


def apply(font,data):
    assert data['unitsPerEm']==font['head'].unitsPerEm
    assert data['axes']=={a.axisTag:[a.minValue,a.defaultValue,a.maxValue] for a in font['fvar'].axes}
    assert {tag:{float(k):v for k,v in mapping.items()} for tag,mapping in data['avar'].items()}==font['avar'].segments
    cmap=font.getBestCmap();names=[cmap[ord(ch)] for ch in data['characters']]
    assert len(set(names))==len(names)
    for name in names:
        glyph=font['glyf'][name]
        assert not glyph.isComposite() and glyph.numberOfContours==0,'Only empty spaces may use this metric replacement'
    hvar=font['HVAR'].table;store=hvar.VarStore;order=font.getGlyphOrder()
    old_map=hvar.AdvWidthMap.mapping if hvar.AdvWidthMap else dict(zip(order,range(len(order))))
    regions=buildVarRegionList(data['supports'],[a.axisTag for a in font['fvar'].axes])
    first=len(store.VarRegionList.Region);indices=list(range(first,first+len(regions.Region)))
    store.VarRegionList.Region.extend(regions.Region);store.VarRegionList.RegionCount=len(store.VarRegionList.Region)
    table=buildVarData(indices,[data['deltas']],optimize=False);new_index=len(store.VarData)<<16
    store.VarData.append(table);store.VarDataCount=len(store.VarData)
    hvar.AdvWidthMap=buildVarIdxMap([new_index if name in names else old_map[name] for name in order],order)
    for name in names:
        font['hmtx'][name]=(data['baseAdvance'],font['hmtx'][name][1])
        font['gvar'].variations[name]=[TupleVariation(support,[(0,0),(delta,0),(0,0),(0,0)]) for support,delta in zip(data['supports'],data['deltas'])]
    font['hhea'].recalc(font);font['OS/2'].recalcAvgCharWidth(font)
    return {'glyphs':names,'baseAdvance':data['baseAdvance'],'regions':len(data['supports']),'source':'sources/space-widths.json'}
