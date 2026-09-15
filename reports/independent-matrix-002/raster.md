# Independent raster review

Font SHA-256: `3567058955eb20ebaf25ef5241a094b25d86dfd7be966f8032492dd3caa3e011`. Font and source remained read-only.

Rendered 32 size/weight/density combinations: 12/14/16/18 px × 100/400/500/900 × 1x/2x, with opsz matched to CSS size. Six RU/EN UI/body/probe lines per combination (192 lines). Reviewed seven overviews and 14 native-resolution crops. This is FreeType/HarfBuzz raster emulation, not physical 1x/Retina hardware or OS/browser validation.

- **ui: conditional** — Core RU/EN UI samples are readable at 12–18 px at 400/500 in this rasterizer. Thin 100 is too pale for routine small UI; 900 has dense small counters and should be reserved for emphasis.
- **headings: conditional** — 18 px heading-sized labels at 400/500/900 survive. Larger display sizes were outside this review; Thin needs contrast and size appropriate to its intended role.
- **body: conditional** — Short RU/EN body strings at 14–18 px 400/500 show no visible broken strokes, mark collisions, or filled counters. 12 px is less comfortable and 100/900 are not recommended body defaults.
- **sustained_reading: unverified** — Short raster strings cannot establish sustained reading performance, comfort, line-length effects, or fatigue.

Core RU/EN: sampled 400/500 strokes and counters survive. Russian ё dots and й breve sit separately above their bases. At 900/12 px, а/е/в/8 counters are small; I did not establish a definite fully closed counter. No specific malformed-outline raster failure was established in basic RU/EN.

## P2: Thin loses practical contrast at small 1x sizes

proof-12-100-1x.png and proof-14-100-1x.png: EN/RU stems and dots are markedly pale relative to 400; contours remain recognizable. The 2x 12 px render gives more stable edges. This is an expected Thin limitation, not evidence of malformed outlines.

Recommendation: Use 400/500 for routine 12–14 px UI and body; document Thin as display/emphasis rather than small reading text. Acceptance: Compare the same strings at native 1x/2x in target OS/browser engines and confirm normal UI defaults use 400 or higher.

## P2: Supplementary accented Latin probes lack coverage

Final probe line ends in three identical oval missing-glyph forms for é ï Å at every weight. getBestCmap confirms all three absent; ё and й are mapped. This is a coverage failure, not raster mark positioning.

Recommendation: If accented Latin names or international text are promised, add these glyphs and decomposition/mark support; otherwise explicitly limit repertoire. Acceptance: HarfBuzz shaping of é ï Å must return nonzero intended glyphs and visual accents at 12–18 px in supported engines.

Proofs: `build/matrix002/raster/proof-{size}-{weight}-{scale}x.png`; generator: `build/matrix002/raster/render_audit.py`. The supplemental accented Latin failure must not be confused with ё/й mark support.

Limits: black-on-white short strings only. Large overviews were viewer-resized; individual crops informed raster judgments. No dark-mode/low-contrast/subpixel/fractional-size or sustained-reading evidence. 2x proofs show backing-store pixels and keep opsz at CSS size.
