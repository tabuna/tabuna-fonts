# Independent raster review — Tabuna Sans 0.0.3

Font SHA-256: `56cb3cbd30099ed97b0395e7eae28f9431e84ff9eede14cdfb4061f1c5873edc`.

Fresh actual-font HarfBuzz/FreeType rendering and direct inspection of eight new proof images; only task instructions and applicable AGENTS were read. No other audit/reviewer report was opened. Font and source remained read-only.

## Method and evidence

32 configurations: weights100/400/500/900 ×12/14/16/18px ×1x/2x; each on light and separately composited dark backgrounds, three RU/EN/punctuation lines per configuration. HarfBuzz positions actual variable-font glyphs; FreeType rasterizes grayscale with default loading. opsz is explicitly matched numerically to CSS pixel size. 2x previews are BOX-downsampled, not hardware or browser captures.

- `build/matrix003/raster/weight-100.png`
- `build/matrix003/raster/weight-400.png`
- `build/matrix003/raster/weight-500.png`
- `build/matrix003/raster/weight-900.png`
- `build/matrix003/raster/dark-weight-100.png`
- `build/matrix003/raster/dark-weight-400.png`
- `build/matrix003/raster/dark-weight-500.png`
- `build/matrix003/raster/dark-weight-900.png`

## Verdicts

- **ui**: Conditional pass for 400/500 at 14–18px; 12px recognizable but less robust. Do not use 100 for essential small UI. 900 only brief emphasis. Platform validation outstanding.
- **headings**: Small headings at 16–18px 400/500/900 readable. Larger heading sizes not tested; Thin heading approval outside scope.
- **body**: Conditional pass for short RU/EN text at 16–18px 400/500. Thin and 900 unsuitable as default body in this matrix.
- **sustained_reading**: Not established: short isolated lines only; no extended reading or participant test.

## Findings

**P1 — wght100, 12–18px, native1x and synthetic2x, both backgrounds**. Thin strokes and punctuation have very low apparent coverage; 12–14px text is substantially weaker than regular, and 2x does not restore regular-like robustness. Restrict Thin to decorative text after size-specific evaluation; default essential UI/body to 400 or 500. This is a usage constraint, not proof of a malformed font. Acceptance: Inspect RU/EN controls and punctuation at real 1x/2x on target platforms; all essential labels use a weight maintaining clear strokes under normal viewing.

**P2 — wght900, 12–14px, both backgrounds**. Dense Cyrillic combinations and English e/a counters become cramped. Text remains decipherable, but word silhouettes are markedly heavier and apertures less robust than at 400/500. Use 900 for short emphasis rather than dense small text; prefer 400/500 for controls and paragraphs. Acceptance: At 12/14px, verify counters in е/а/e/a and dense ш/щ/ы clusters stay visibly open on each target platform; use a lower weight where they do not.

**P2 — 400/500 at12px native1x, punctuation and isolated identifiers**. Periods, comma tails and fine distinctions among Il1/O0 require more attention than 16–18px. No wholesale punctuation disappearance was seen in regular/medium. Prefer 14px or larger for essential text and 16–18px for body; evaluate identifier-heavy UI separately. Acceptance: Native display checks at12/14px must permit reliable distinction of comma/period, quotes, Il1 and O0 in task-realistic strings.

Regular/medium RU and EN lines remain legible through the tested range. At16–18px the normal text has visibly more comfortable counters and punctuation than the12px lines. Cyrillic ё dots remain visible at400/500; dense Cyrillic stems need more attention at extreme weights. No general clipping or missing-glyph boxes appeared in the sampled strings.

## Limits

- FreeType grayscale FT_LOAD_DEFAULT with HarfBuzz positioning; this is a synthetic renderer, not CoreText, browser, DirectWrite or hardware evidence.
- 2x is rendered at twice the pixel size while keeping opsz at CSS size, then BOX-downsampled for comparative display. Dark raw2x images are retained. These previews are not measurements of a physical Retina panel.
- Only eight composite proof images were visually inspected; screenshot presentation can itself rescale images.
- opsz matched numerically to pixel size by explicit design-coordinate setting; CSS optical-sizing behavior was not tested.
- No long paragraphs, human reading-speed/comfort study, fallback, browser shaping, contrast accessibility certification or broad script coverage.


Fixture correction: initial sheets advanced 27px for 40px image strips and overwrote descenders. Root flagged the overlap; row spacing was corrected to40px, all eight sheets regenerated and re-inspected. Final findings use corrected proofs only. This was a harness defect, not a font defect.
