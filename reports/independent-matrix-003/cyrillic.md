# Independent Cyrillic/editorial review — 0.0.3

Font SHA-256: `56cb3cbd30099ed97b0395e7eae28f9431e84ff9eede14cdfb4061f1c5873edc`

Read font manifest and generated my own HarfBuzz/FreeType Russian proofs. Did not read prior reports, matrices, other reviewer reports, or their proof images/scripts. Source/font were not modified.

## Evidence

Viewed all 3 independently rendered proof PNGs using view_image. 54 shaped lines; weights 100/400/900; 12–96 px, opsz matched numerically to size. Text includes Russian UI labels, headings, four-line paragraphs at 14/18 px, and ДЛдлбвжкяЁй.

## Verdicts

- **ui: conditional_pass** — Regular 400 Russian labels at 12–20 px remain legible with matched opsz. Thin 100 at 12–16 px has very low stroke coverage; heavy 900 is usable for short emphasis, not a default text weight.
- **headings: pass** — At 24–96 px the tested Cyrillic constructions and diacritics remain recognizable at 100, 400 and 900; no visible broken joins or counter collapse in the inspected samples.
- **body: conditional_pass** — Russian paragraphs at 14 and 18 px / weight 400 are readable and have coherent texture. This is a short visual inspection, not a reading study.
- **sustained_reading: not_established** — Four-line paragraphs do not establish long-session readability or fatigue; no human reading test was performed.

## Findings

No reproducible construction defect found in the requested Cyrillic letters. Д/д feet, Л/л shoulders, б flag, в counters, ж/к joins, я bowl and Ё/й marks remain intelligible in the inspected instances. Flat tops and angular diagonals are design choices, not objective failures.

### CYR-01 — P2 (coverage_defect)

U+2022 BULLET in the heading test shapes to glyph 0 at all three weights. Rendered as an outlined oval unrelated to surrounding weight. All requested Cyrillic letters shape to nonzero glyph IDs.

Add U+2022 with an appropriate bullet drawing/advance, or require an explicit fallback before claiming general editorial punctuation coverage.

Acceptance: Shape RU text containing U+2022 at 100/400/900 and opsz 14/48; require nonzero glyph ID and visually appropriate bullet at each instance.

### CYR-02 — P3 (usage_limit_not_construction_defect)

At 12–16 px, weight 100 renders Russian UI strokes very faint; at weight 900 the same sizes produce dense counters. No Cyrillic-specific failure isolated.

Use weight 400 for default UI/body; reserve extremes for large display or deliberate emphasis. Do not redesign Cyrillic solely from the extreme samples.

Acceptance: Check 12/14/16 px Russian labels at the intended default weight in target native/browser rasterizers on actual displays.

## Limitations

- Single renderer, grayscale rasterization; no CoreText/browser screenshot comparison.
- Three weights and sampled optical sizes, not exhaustive continuous-axis testing.
- Short excerpts only, no controlled human sustained-reading study.
- No Latin benchmark or competitor comparison used.
- Visual taste is not treated as a construction failure: flat-top Д/Л and angular ж/к are stylistic choices.

Proofs: `scratchbuild/matrix003/cyrillic/ru-{100,400,900}.png`; exact test strings and missing-glyph counts in `evidence.json`.
