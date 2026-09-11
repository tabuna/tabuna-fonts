"""Add measured local advance corrections; preserve every simple outline."""
from fontTools.varLib.builder import buildVarData,buildVarIdxMap,buildVarRegionList
from fontTools.ttLib.tables.TupleVariation import TupleVariation
from fontTools.misc.roundTools import otRound


def apply(font,data):
    assert data['unitsPerEm']==font['head'].unitsPerEm
    for sample in data['baselineModelAdvances']:
        glyphs=font.getGlyphSet(location={'wght':sample['weight'],'opsz':sample['size']})
        assert all(otRound(glyphs[name].width)==width for name,width in sample['widths'].items()),'Base advances changed: remeasure and recalibrate the local optical corrections'
    supports=data['supports'];axes=font['fvar'].axes
    hvar=font['HVAR'].table;store=hvar.VarStore;order=font.getGlyphOrder()
    additions=buildVarRegionList(supports,[a.axisTag for a in axes])
    first=len(store.VarRegionList.Region)
    region_indices=list(range(first,first+len(additions.Region)))
    store.VarRegionList.Region.extend(additions.Region)
    store.VarRegionList.RegionCount=len(store.VarRegionList.Region)
    old_map=hvar.AdvWidthMap.mapping if hvar.AdvWidthMap else dict(zip(order,range(len(order))))
    original_data=list(store.VarData);groups={};indices=[];changed=[]
    for name in order:
        deltas=data['glyphs'].get(name);old_index=old_map[name]
        if not deltas or not any(deltas):indices.append(old_index);continue
        assert font['hmtx'][name][0]>0,'Do not add spacing to zero-width marks'
        outer,inner=old_index>>16,old_index&0xffff
        if outer not in groups:
            original=original_data[outer]
            table=buildVarData(list(original.VarRegionIndex)+region_indices,[],optimize=False)
            groups[outer]={'outer':len(store.VarData),'table':table,'original':original};store.VarData.append(table)
        group=groups[outer];table=group['table']
        indices.append((group['outer']<<16)|len(table.Item))
        table.Item.append(list(group['original'].Item[inner])+deltas)
        glyph=font['glyf'][name]
        count=len(glyph.components) if glyph.isComposite() else len(glyph.getCoordinates(font['glyf'])[0])
        for support,delta in zip(supports,deltas):
            if delta:font['gvar'].variations.setdefault(name,[]).append(TupleVariation(support,[None]*count+[(0,0),(delta,0),(0,0),(0,0)]))
        changed.append(name)
    for group in groups.values():
        table=group['table'];table.ItemCount=len(table.Item);table.calculateNumShorts(optimize=False)
    store.VarDataCount=len(store.VarData);hvar.AdvWidthMap=buildVarIdxMap(indices,order)
    return {'adjustedGlyphs':len(changed),'regions':len(supports),'source':'sources/optical-widths.json'}
