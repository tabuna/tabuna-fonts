"""Encode measured tracking as OpenType HVAR advances, with no Apple tables.

Existing outline variations, kerning, mark placement, and HVAR sidebearing
maps are preserved. Only nonzero advances receive the common spacing field.
"""
from fontTools.misc.fixedTools import floatToFixedToFloat
from fontTools.misc.roundTools import otRound
from fontTools.varLib.builder import buildVarData, buildVarIdxMap, buildVarRegionList
from fontTools.varLib.models import normalizeValue, piecewiseLinearMap
from fontTools.ttLib.tables.TupleVariation import TupleVariation


def apply_tracking(font, calibration):
    axes=font['fvar'].axes
    optical=next(a for a in axes if a.axisTag=='opsz')
    axis_range=(optical.minValue,optical.defaultValue,optical.maxValue)
    points={}
    for row in calibration['records']:
        raw=normalizeValue(row['pointSize'],axis_range)
        mapped=piecewiseLinearMap(raw,font['avar'].segments['opsz'])
        coord=floatToFixedToFloat(mapped,14)
        value=row['fontUnits']
        if coord in points and points[coord]!=value:
            raise ValueError(f'Axis collapses distinct tracking requests at {coord}')
        points[coord]=value
    base=points[0]
    coords=sorted(points)
    supports=[];deltas=[]
    for i,coord in enumerate(coords):
        if coord==0:continue
        left=coords[i-1] if i else coord
        right=coords[i+1] if i+1<len(coords) else coord
        supports.append({'opsz':(left,coord,right)})
        deltas.append(otRound(points[coord]-base))
    hvar=font['HVAR'].table
    store=hvar.VarStore
    additions=buildVarRegionList(supports,[a.axisTag for a in axes])
    first_region=len(store.VarRegionList.Region)
    region_indices=list(range(first_region,first_region+len(additions.Region)))
    store.VarRegionList.Region.extend(additions.Region)
    store.VarRegionList.RegionCount=len(store.VarRegionList.Region)
    order=font.getGlyphOrder()
    old_map=hvar.AdvWidthMap.mapping if hvar.AdvWidthMap else dict(zip(order,range(len(order))))
    original_data=list(store.VarData)
    groups={};new_indices=[];adjusted=0
    for name in order:
        width,lsb=font['hmtx'][name]
        multiplier=len(name.removesuffix('.liga')) if name.endswith('.liga') else 1
        old_index=old_map[name]
        if width==0:
            new_indices.append(old_index)
            continue
        outer,inner=old_index>>16,old_index&0xffff
        if outer not in groups:
            original=original_data[outer]
            groups[outer]={'outer':len(store.VarData),'rows':{},'original':original,
                           'table':buildVarData(list(original.VarRegionIndex)+region_indices,[],optimize=False)}
            store.VarData.append(groups[outer]['table'])
        group=groups[outer]
        row_key=(inner,multiplier)
        if row_key not in group['rows']:
            group['rows'][row_key]=len(group['table'].Item)
            group['table'].Item.append(list(group['original'].Item[inner])+[d*multiplier for d in deltas])
        new_indices.append((group['outer']<<16)|group['rows'][row_key])
        font['hmtx'][name]=(width+base*multiplier,lsb)
        # TrueType instancing and renderers without HVAR use the right phantom
        # point in gvar. Keep both equivalent metric representations in sync.
        glyph=font['glyf'][name]
        if multiplier>1:
            assert glyph.isComposite() and len(glyph.components)==multiplier
            for index,component in enumerate(glyph.components):component.x+=base*index
            glyph.recalcBounds(font['glyf'])
        count=len(glyph.components) if glyph.isComposite() else len(glyph.getCoordinates(font['glyf'])[0])
        for support,delta in zip(supports,deltas):
            if delta:
                outlines=[(index*delta,0) for index in range(count)] if multiplier>1 else [None]*count
                coordinates=outlines+[(0,0),(delta*multiplier,0),(0,0),(0,0)]
                font['gvar'].variations.setdefault(name,[]).append(TupleVariation(support,coordinates))
        adjusted+=1
    for group in groups.values():
        table=group['table'];table.ItemCount=len(table.Item);table.calculateNumShorts(optimize=False)
    store.VarDataCount=len(store.VarData)
    hvar.AdvWidthMap=buildVarIdxMap(new_indices,order)
    # hmtx changed after compilation: keep derived default-instance metadata
    # consistent even when the caller disables automatic bounding-box updates.
    font['hhea'].recalc(font)
    font['OS/2'].recalcAvgCharWidth(font)
    return {'format':'OpenType HVAR','baseAdvanceAdjustment':base,'adjustedGlyphs':adjusted,
            'trackingRegions':len(supports),'axisRange':axis_range,'source':'sources/tracking.json'}
