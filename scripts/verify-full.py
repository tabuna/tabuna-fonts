#!/usr/bin/env python3
"""Actual binary checks: Unicode, shaping, variations, geometry and web parity."""
from pathlib import Path
import hashlib
import io
import json
import sys
import uharfbuzz as hb
import pathops
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont,AxisLimits
from fontTools.varLib.varStore import VarStoreInstancer
from fontTools.varLib.models import normalizeLocation,piecewiseLinearMap
from fontTools.misc.roundTools import otRound
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.varLib.interpolatable import test as test_interpolatable
from ufoLib2 import Font

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build import CHARSET,name
import optical as optics

fontpath=ROOT/'dist/TabunaSansVariable.ttf'
binary=fontpath.read_bytes();font=TTFont(io.BytesIO(binary));cmap=font.getBestCmap()
em_scale=font['head'].unitsPerEm/1000
errors=[];checks=[]
def check(condition,message):
    (checks if condition else errors).append(message)

missing=[f'U+{ord(c):04X}' for c in CHARSET if ord(c) not in cmap]
check(not missing,f'Unicode coverage: {len(CHARSET)} required characters; missing {missing}')
for table in ['fvar','gvar','STAT','GDEF','GPOS','GSUB']:
    check(table in font,f'OpenType table {table}')
axes={a.axisTag:(a.minValue,a.defaultValue,a.maxValue) for a in font['fvar'].axes}
check(axes=={'wght':(100,400,900),'opsz':tuple(optics.AXIS_RANGE)},f'Axis ranges: {axes}')
check(len(font['fvar'].instances)==9,'Nine named weight instances')
check(font['name'].getDebugName(1)=='Tabuna Sans','Family identity')
check(font['name'].getDebugName(2)=='Regular','Default style is Regular')

# Source outlines are already clockwise. A compiler's unconditional reversal
# changes CoreText edge coverage by one grayscale level even for a rectangle.
from fontTools.pens.areaPen import AreaPen
directions=[]
default_glyphs=font.getGlyphSet()
for ch in 'IHaоЖ1':
    pen=AreaPen(default_glyphs);default_glyphs[cmap[ord(ch)]].draw(pen)
    directions.append(pen.value < 0)
check(all(directions),'Clockwise TrueType outer contours survive compilation')

face=hb.Face(binary)
def shape(text,features=None,weight=400,optical=14):
    f=hb.Font(face);f.set_variations({'wght':weight,'opsz':optical})
    b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(f,b,features or {})
    return b.glyph_infos,b.glyph_positions

for text in ['Ясность в каждой букве.','Съешь ещё этих мягких французских булок.','Ångström naïve français Știință','ІЇЄҐ іїєґ ЉЊЂЋЏ','123 456,78 ₽ € £ ₴ ¥','− × ÷ ± ≠ ≤ ≥ ≈ ∞ √']:
    info,pos=shape(text);check(all(i.codepoint!=0 for i in info),f'Shaping without .notdef: {text}')
check(len(shape('ffi',{'liga':True})[0])==1,'ffi ligature substitutes three glyphs')
check(len(shape('ffi',{'liga':False})[0])==3,'Ligatures can be disabled')
case_id=font.getGlyphID('colon.case');colon_id=font.getGlyphID('colon')
check(shape('1:4')[0][1].codepoint==case_id and shape('a:4')[0][1].codepoint==colon_id,
      'Contextual colon follows the measured numeric versus lowercase contexts')
check(shape('1:4',{'calt':False})[0][1].codepoint==colon_id,'Contextual alternates can be disabled')
check(sum(p.x_advance for p in shape('AV')[1])<sum(p.x_advance for p in shape('AV',{'kern':False})[1]),'AV kerning reduces advance')
check(sum(p.x_advance for p in shape('То')[1])<sum(p.x_advance for p in shape('То',{'kern':False})[1]),'Cyrillic То kerning reduces advance')
info,pos=shape('x\u0301');check(len(info)==2 and pos[-1].x_advance==0 and pos[-1].x_offset!=0,'Combining mark positioning on x')
import unicodedata
reading_characters=json.loads((ROOT/'references/reading-marks-baseline/validation.json').read_text())['composed']
canonical_errors=[];mark_errors=[]
for weight in range(100,901,100):
    for optical in (9,14,16,24,28,48,72,128):
        for text in reading_characters:
            signatures=[]
            for form in (text,unicodedata.normalize('NFD',text)):
                infos,positions=shape(form,weight=weight,optical=optical)
                signatures.append([(i.codepoint,p.x_advance,p.y_advance,p.x_offset,p.y_offset) for i,p in zip(infos,positions)])
            if signatures[0]!=signatures[1]:canonical_errors.append((text,weight,optical))
        gs=font.getGlyphSet(location={'wght':weight,'opsz':optical})
        for mark in '\u0302\u0306\u0307':
            infos,positions=shape('б'+mark,weight=weight,optical=optical)
            boxes=[];x=y=0
            for info,pos in zip(infos,positions):
                pen=BoundsPen(gs);gs[font.getGlyphName(info.codepoint)].draw(pen)
                if pen.bounds:boxes.append((pen.bounds[1]+y+pos.y_offset,pen.bounds[3]+y+pos.y_offset))
                x+=pos.x_advance;y+=pos.y_advance
            if len(boxes)!=2 or boxes[1][0]<=boxes[0][1] or positions[-1].x_advance!=0:
                mark_errors.append((mark,weight,optical))
check(not canonical_errors,f'50 reading-diacritic letters shape identically in NFC and NFD at 72 locations; {len(canonical_errors)} issues')
check(not mark_errors,f'Above marks clear the Cyrillic be ascender with zero advance at 72 locations; {len(mark_errors)} issues')
for weight in [100,400,900]:
    widths=[sum(p.x_advance for p in shape(str(i),{'tnum':True},weight)[1]) for i in range(10)]
    check(len(set(widths))==1,f'Tabular figures have equal advances at weight {weight}')

# Check both axis endpoints and intermediate instances, every glyph.
optical_checks=(9,14,16,24,28,48,72,128)
location_count=9*len(optical_checks)
extent=[0,0,0,0];geometry_errors=[]
for weight in range(100,901,100):
    for optical in optical_checks:
        gs=font.getGlyphSet(location={'wght':weight,'opsz':optical})
        for gname in font.getGlyphOrder():
            pen=BoundsPen(gs);gs[gname].draw(pen)
            if not pen.bounds:continue
            x0,y0,x1,y1=[v/em_scale for v in pen.bounds]
            extent=[min(extent[0],x0),min(extent[1],y0),max(extent[2],x1),max(extent[3],y1)]
            if y0 < -300 or y1 >1030:geometry_errors.append((gname,weight,optical,[round(v,2) for v in pen.bounds]))
            if x1-x0<.1 or y1-y0<.1:geometry_errors.append((gname,weight,optical,'degenerate'))
check(not geometry_errors,f'{location_count} instances × {len(font.getGlyphOrder())} glyphs fit vertical metrics; {len(geometry_errors)} issues')

counter_errors=[]
expected_counters={'S':0,'s':0,'Ѕ':0,'ѕ':0,'U':0,'u':0,'G':0,'c':0,'C':0,'с':0,'С':0,'a':1,'а':1,'b':1,'d':1,'р':1,'e':1,'е':1,'g':1,'o':1,'p':1,'q':1,'B':2,'D':1,'O':1,'P':1,'R':1,
                   '0':1,'6':1,'8':2,'9':1,'Б':1,'В':2,'в':2,'Д':1,'д':1,'Ъ':1,'ъ':1,'Ы':1,'ы':1,'Ь':1,'ь':1,'Ф':2,'ф':2,'Ю':1,'ю':1,'Я':1,'я':1}
for weight in range(100,901,100):
    for optical in optical_checks:
        gs=font.getGlyphSet(location={'wght':weight,'opsz':optical})
        for ch,count in expected_counters.items():
            path=pathops.Path();gs[cmap[ord(ch)]].draw(path.getPen())
            contours=list(pathops.simplify(path).contours)
            holes=[c.area for c in contours if c.clockwise]
            if len(holes)!=count or (count and min(holes,default=0)<600*em_scale**2) or (ch in 'SsЅѕ' and len(contours)!=1):
                counter_errors.append({'glyph':ch,'weight':weight,'optical':optical,'areas':holes,'expected':count})
check(not counter_errors,f'Counter topology remains correct in {len(expected_counters)} key glyphs across {location_count} locations; {len(counter_errors)} issues')

woff=TTFont(ROOT/'dist/TabunaSansVariable.woff2')
check(woff.getBestCmap()==cmap,'WOFF2 retains complete Unicode map')
check(woff['gvar'].compile(woff)==font['gvar'].compile(font),'WOFF2 retains variation data')
check('trak' not in font,'Web font contains no AAT tracking table')
check('HVAR' not in font and 'HVAR' not in woff,'Variable advances use gvar phantom points, without fractional HVAR overrides')
metrics_control=TTFont(ROOT/'build/TabunaSans-with-hvar.ttf')
check(metrics_control['gvar'].compile(metrics_control)==font['gvar'].compile(font)
      and metrics_control['hmtx'].metrics==font['hmtx'].metrics,
      'Build-only HVAR control has identical gvar and default metrics')
instance_errors=[]
master_geometry_errors=[]
metric_locations=[(w,o) for w in (100,400,900) for o in (16,18,20,24,28,64,128)]+[(w,o) for w in (200,300,500,600,700,800) for o in (16,64)]
for weight,optical in metric_locations:
    # The instancer quantizes post-avar coordinates to F2Dot14. Compare HVAR
    # at the same coordinates, rather than at an unquantized nearby location.
    location=AxisLimits({'wght':weight,'opsz':optical}).limitAxesAndPopulateDefaults(font).normalize(font).defaultLocation()
    store=VarStoreInstancer(metrics_control['HVAR'].table.VarStore,font['fvar'].axes,location)
    instance=instantiateVariableFont(font,{'wght':weight,'opsz':optical},inplace=False)
    # Check the actual pre-rounding interpolated geometry against the UFO
    # master input. Lossy IUP optimization previously moved integer vertices
    # by ~0.36 FU. The epsilon here only absorbs floating-point arithmetic;
    # native pixel acceptance remains strict equality with no tolerance.
    if weight in (100,400,900) and optical in (16,64,128):
        source=Font.open(ROOT/'sources'/f'TabunaSans-{weight}-{16 if optical==16 else 28}.ufo')
        for ch in 'ПпШшЦцЩщТтНнIHEFLЕІ':
            key=cmap[ord(ch)];pen=TTGlyphPen(None);source[key].draw(pen);expected_glyph=pen.glyph()
            actual=instance['glyf'][key]
            if actual.endPtsOfContours!=expected_glyph.endPtsOfContours:
                master_geometry_errors.append((weight,optical,ch,'topology'));continue
            delta=max(abs(a-b) for p,q in zip(actual.coordinates,expected_glyph.coordinates) for a,b in zip(p,q))
            if delta>1e-7:master_geometry_errors.append((weight,optical,ch,delta))
    for glyph in font.getGlyphOrder():
        delta=store[metrics_control['HVAR'].table.AdvWidthMap.mapping[glyph]]
        expected=otRound(font['hmtx'][glyph][0]+delta)
        if instance['hmtx'][glyph][0]!=expected:instance_errors.append((weight,optical,glyph))
check(not instance_errors,f'Static instancing preserves rounded HVAR-control advances across {len(metric_locations)} locations; {len(instance_errors)} issues')
check(not master_geometry_errors,f'19 rectilinear glyphs preserve UFO master vertices at 9 locations; {len(master_geometry_errors)} issues')
font_widths=[]
for optical in (9,72):
    font_widths.append(sum(p.x_advance for p in shape('Hamburgefontsiv',optical=optical)[1]))
check(font_widths[0]!=font_widths[1],'Optical axis changes actual font metrics')

report={'font_sha256':hashlib.sha256(binary).hexdigest(),'passed':len(checks),'failed':len(errors),
        'checks':checks,'errors':errors,'global_bounds':extent,'geometry_issues':geometry_errors,'counter_issues':counter_errors,'instance_issues':instance_errors,
        'master_geometry_issues':master_geometry_errors}
(ROOT/'proofs').mkdir(exist_ok=True)
(ROOT/'proofs/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['passed','failed','errors','global_bounds']},ensure_ascii=False,indent=2))
sys.exit(bool(errors))
