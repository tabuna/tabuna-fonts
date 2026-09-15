# Independent engineering review 002

Font SHA-256: `3567058955eb20ebaf25ef5241a094b25d86dfd7be966f8032492dd3caa3e011`  
WOFF2 SHA-256: `d07839f04ebdbfb89fed1c4f9d5d2609197db1071251bd5cf8ab0db5f626b207`

Independent OpenType/variation engineering inspection, performed without reading prior reviews. No font or source edits. Scope: 189 Unicode mappings, 218 glyphs, wght 100–900 / opsz 9–128. Defaults 400/14; nine named weight instances; version 0.0.2; OFL name/license metadata present. GSUB and GPOS advertise DFLT, cyrl, latn; numeric features are pnum/tnum, not oldstyle/slashed-zero.

| Use | Verdict | Reason |
|---|---|---|
| ui | conditional | All encoded glyphs rasterize at tested UI sizes, but tnum breaks contextual timer-colon alignment. Restrict text to scoped coverage and visually verify target platform. |
| headings | pass | Engineering pass within 189-codepoint scope: extremes and interior axes draw, Latin/Cyrillic kerning and ligatures function, no encoded line-metric overrun. Does not certify visual taste. |
| body | conditional | In-scope shaping and rasterization work, including decomposed Russian Ё/Й normalization. Accented Latin and general combining marks are outside coverage; platform/readability validation remains. |
| sustained_reading | unverified | No timed reader study or long-form visual evaluation was performed; successful rendering cannot establish fatigue or reading speed. |

## Observed tests

- **axis/coverage inventory**: pass, 2 checks. {'cmap': 189, 'glyphs': 218, 'axes': [['wght', 100.0, 400.0, 900.0], ['opsz', 9.0, 14.0, 128.0]]}
- **outline interpolation**: pass, 21582 checks. All 218 glyphs drawn with BoundsPen at 9 weights × 11 optical sizes; no exceptions/nonfinite bounds/unexpected empty glyphs.
- **encoded line-metric containment**: pass, 18711 checks. Zero encoded outlines exceed hhea/Typo ascent2109 descent-614. 372 exceedances belong exclusively to unencoded fractional construction components scaled by parent composites, so they are not encoded clipping defects. MVAR only changes stro/xhgt; line metrics invariant.
- **tabular numerals**: pass, 990 checks. All ten tnum advances equal at every location with kern disabled; pnum produces varied widths. At default tabular advance1286.
- **FreeType grayscale rasterization**: pass, 5292 checks. 189 codepoints × weights100/400/700/900 × pixel sizes9/11/14/18/32/72/128 with matching opsz: zero load errors or unexpectedly empty rasters.
- **shaping probes**: conditional, 18 checks. 9 strings with default versus kern/liga/calt disabled. Latin and Cyrillic kerning, five f ligatures and canonical Russian decomposition work. Out-of-scope e+acute, é, ï yield .notdef as expected for scope.
- **tnum/calt interaction**: fail, 32 checks. 16 locations × tnum off/on. All 16 tnum-on cases lose colon.case.
- **WOFF2 decoded table equivalence**: pass, 18 checks. All 18 compared tables byte-identical after WOFF2 decoding; head/loca excluded for checksum/storage representation and GlyphOrder is pseudo-table.

## Actionable finding

**ENG-001 / P2 — tabular timer colon drops.** `12:34` selects `colon.case` normally, but `colon` when `tnum` is enabled. At default axes their vertical bounds are 205–1239 versus −10–1024: a 215-unit (1.47px at 14px) change. All 16 sampled axis locations reproduce it. The numeral substitution runs before the contextual rule, whose digit coverage excludes tabular alternates. Add those alternates to the numeric context. Acceptance: both numeral modes select `colon.case` in `12:34`, `00:00`, `99:59` across the 16 locations, retain lowercase `a:b` behavior, and retain equal tabular advances.

## Interpretation and limits

The font passed the bounded engineering grid, except the numeric contextual interaction. Construction glyphs with unusually large bounds are scaled components, not observed clipping of displayed characters. Do not inflate line metrics solely to contain those component sources. The font has no per-glyph hint programs; 5,292 nonempty FreeType rasters demonstrate usable outline execution, not quality equivalence across native renderers.

- Independent engineering inspection; no prior reports or other reviewers read before this report. No font/source modifications.
- Finite axis grid does not prove absence of every contour crossing or intermediate visual defect.
- FreeType rendering success is not a visual quality score; no CoreText, DirectWrite, Safari/Chrome installation, OTS sanitizer, or sustained-reading experiment performed.
- Coverage intentionally limited to 189 codepoints. General accented Latin, combining marks, italic/oblique and broader multilingual support not promised or verified.
- No actual human, Apple employee or Apple affiliation claimed.
- Full static instancing sweep was abandoned as too expensive; direct variable glyph-set evaluation used instead. hhea/Typo containment is valid because MVAR has only stro/xhgt.

Raw evidence and reproducible outline/shaping probe: `build/matrix002/engineering/`.
