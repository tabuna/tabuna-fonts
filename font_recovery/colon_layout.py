"""Certify the narrowly defined Cyrillic contextual-colon layout extension."""
import copy,hashlib


def verify(before,after):
    assert before.getBestCmap()==after.getBestCmap()
    cyrl={after.getBestCmap()[cp] for cp in [0x401,*range(0x410,0x430)]}
    context=cyrl|{after.getBestCmap()[cp] for cp in range(48,58)}
    expected=copy.deepcopy(before['GSUB']);features=expected.table.FeatureList.FeatureRecord
    calt=[r.Feature.LookupListIndex for r in features if r.FeatureTag=='calt'];assert len(calt)==1 and len(calt[0])==1
    lookup=expected.table.LookupList.Lookup[calt[0][0]];assert lookup.LookupType==6 and lookup.LookupFlag==0 and len(lookup.SubTable)==1
    rule=copy.deepcopy(lookup.SubTable[0]);assert rule.Format==3 and rule.BacktrackGlyphCount==rule.InputGlyphCount==rule.LookAheadGlyphCount==rule.SubstCount==1
    assert rule.InputCoverage[0].glyphs==['colon'];record=rule.SubstLookupRecord[0];assert record.SequenceIndex==0
    target=expected.table.LookupList.Lookup[record.LookupListIndex];assert target.LookupType==1 and len(target.SubTable)==1 and target.SubTable[0].mapping=={'colon':'colon.case'}
    names=sorted(context,key=after.getGlyphID);rule.BacktrackCoverage[0].glyphs=names;rule.LookAheadCoverage[0].glyphs=names;lookup.SubTable.append(rule);lookup.SubTableCount=2
    assert expected.compile(after)==after['GSUB'].compile(after),'Unexpected substitution change'
    normalized=copy.deepcopy(after['GPOS']);old=before['GPOS'].table.LookupList.Lookup[0].SubTable[0].ExtSubTable;new=normalized.table.LookupList.Lookup[0].SubTable[0].ExtSubTable
    assert old.Format==new.Format==1
    old_pairs={(left,r.SecondGlyph) for left,pairs in zip(old.Coverage.glyphs,old.PairSet) for r in pairs.PairValueRecord}
    added=[];coverage=[];pairsets=[]
    for left,pairs in zip(new.Coverage.glyphs,new.PairSet):
        kept=[]
        for record in pairs.PairValueRecord:
            pair=(left,record.SecondGlyph)
            if pair in old_pairs:kept.append(record);continue
            assert (left in cyrl and record.SecondGlyph=='colon.case') or (left=='colon.case' and record.SecondGlyph in cyrl),'Unrelated new kern pair'
            for role in ['Value1','Value2']:
                value=getattr(record,role,None)
                assert value is None or all(v==0 for v in value.__dict__.values()),'New kern pair is not constant zero'
            added.append(pair)
        if kept:
            pairs.PairValueRecord=kept;pairs.PairValueCount=len(kept);coverage.append(left);pairsets.append(pairs)
    new.Coverage.glyphs=coverage;new.PairSet=pairsets;new.PairSetCount=len(pairsets)
    assert normalized.compile(after)==before['GPOS'].compile(before),'Existing positioning changed'
    return dict(status='passed',substitution='Exactly one new Cyrillic uppercase/digit contextual colon rule; all prior GSUB behavior structurally retained',new_constant_zero_kern_pairs=added,existing_positioning_identical=True,table_hashes={tag:[hashlib.sha256(f[tag].compile(f)).hexdigest() for f in [before,after]] for tag in ['GSUB','GPOS']})
