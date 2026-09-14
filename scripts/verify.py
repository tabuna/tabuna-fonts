"""Check compact output against the full authored font from the same build."""
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
import uharfbuzz as hb

ROOT=Path(__file__).resolve().parents[1]


def main():
    full_path=ROOT/'build/TabunaSansFull.ttf'
    paths=[full_path,ROOT/'dist/TabunaSansVariable.ttf',ROOT/'dist/TabunaSansVariable.woff2']
    fonts=[TTFont(p) for p in paths]
    full,font,web=fonts
    expected={ord(c) for c in (ROOT/'sources/compact-charset.txt').read_text() if c not in '\r\n'}
    # Explicit user-approved repertoire, independent of the subset input file.
    required = set(range(0x20, 0x7F)) | set(range(0x410, 0x450)) | {
        0xA0, 0xA3, 0xA5, 0xA9, 0xAB, 0xAE, 0xB0, 0xB1, 0xB7, 0xBB,
        0xD7, 0xF7, 0x401, 0x451, 0x2013, 0x2014, 0x2018, 0x2019,
        0x201C, 0x201D, 0x201E, 0x2026, 0x20AC, 0x20BD, 0x2116,
        0x2212, 0x221E, 0x2260, 0x2264, 0x2265,
    }
    assert len(required) == 189
    assert expected == required, 'Compact charset differs from the approved 189 characters'
    assert set(font.getBestCmap())==expected==set(web.getBestCmap())
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzЁё'+''.join(chr(c) for c in range(0x410,0x450))
    assert all(ord(c) in expected for c in alphabet)
    axes={a.axisTag:(a.minValue,a.maxValue) for a in font['fvar'].axes}
    assert axes=={'wght':(100,900),'opsz':(9,128)}
    for name in font.getGlyphOrder():
        assert full['hmtx'][name]==font['hmtx'][name]==web['hmtx'][name],name
    checked=0
    for weight in [100,250,400,600,800,900]:
        for optical in [9,14,28,128]:
            sets=[f.getGlyphSet(location={'wght':weight,'opsz':optical}) for f in fonts]
            for name in font.getGlyphOrder():
                values=[]
                for gs in sets:
                    p=RecordingPen();gs[name].draw(p);values.append(p.value)
                assert values[0]==values[1]==values[2],(name,weight,optical)
                checked+=1
    text=''.join(sorted(chr(c) for c in expected))+' AVATAR office ffi fl 1234567890 Ясность и уют'
    count=0
    for weight in [100,250,400,600,800,900]:
        for optical in [9,14,28,128]:
            for feature in ['tnum','pnum']:
                runs=[]
                for path,f in zip(paths[:2],fonts[:2]):
                    h=hb.Font(hb.Face(path.read_bytes()));h.set_variations({'wght':weight,'opsz':optical})
                    b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(h,b,{feature:True})
                    assert all(g.codepoint for g in b.glyph_infos)
                    runs.append([(f.getGlyphName(g.codepoint),p.x_advance,p.x_offset,p.y_offset) for g,p in zip(b.glyph_infos,b.glyph_positions)])
                assert runs[0]==runs[1],(weight,optical,feature)
                count+=1
    report={'status':'passed','characters':len(expected),'glyphs':len(font.getGlyphOrder()),'axes':axes,'glyph_location_comparisons':checked,'shaping_comparisons':count,'ttf_woff2_equal_geometry':True,'full_source_sha256':hashlib.sha256(full_path.read_bytes()).hexdigest(),'font_sha256':hashlib.sha256(paths[1].read_bytes()).hexdigest(),'scope':'Compaction preserves the authored model; does not prove complete provenance or SFNS equality.'}
    out=ROOT/'proofs/compact';out.mkdir(parents=True,exist_ok=True);(out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
