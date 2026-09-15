# Independent data-interface review — matrix 002

Reviewed only current dist artifacts, without consulting reviewer reports. No font or source changes.

- ui: **conditional** — Tabular timers and fixed-format decimal amounts pass across the sampled axis grid; use explicit tnum, suitable weights, and resolve locale-space/identifier requirements.
- headings: **pass** — Sampled numeric/currency headings at 28–32 raster pixels are coherent across the tested weights; scoped to these data headings.
- body: **conditional** — Short labels and numeric content are readable in the 400–500 native samples; locale coverage and alphanumeric ambiguity remain conditional.
- sustained_reading: **unverified** — No long-form reading task or user study performed; a numerical proof does not validate sustained reading.

960 automated checks passed: 900 TTF/decoded-WOFF2 shaping and missing-glyph checks, 20 tabular digit checks, and 40 timer/decimal-width checks, across wght 100/400/500/700/900 and opsz 9/14/48/128. Both rendered proof panels were inspected.

Explicit tnum is necessary for stable timers; it works. At 400/14 default 00:00:00, 11:11:11, 88:88:88 measure 8780, 6740, 8888 font units. Prose punctuation and spaces in tested contexts remain unchanged by tnum.

## P2 DATA-01: Locale grouping-space coverage is incomplete

Actual TTF cmap contains U+00A0 but lacks U+202F narrow no-break space and U+2009 thin space. Numeric locale strings using these characters require fallback; the tested ordinary U+0020 grouping works.

Recommendation: Add U+202F and U+2009 with deliberate numeric grouping advances, or explicitly document and test fallback behavior for supported locales.

Acceptance: Shape 1\u202f234,56 € and 1\u2009234.56 with actual TTF and WOFF2; require no .notdef and verify stable grouping under tnum at wght 100/400/900 and opsz 9/14/128.

## P2 DATA-02: Alphanumeric zero remains close to capital O

Inspected native 12/14/16px O0 samples show similar unmarked oval forms, particularly at 12px; GSUB feature tags are calt/liga/pnum/tnum with no zero feature. This is a visual ambiguity observation, not a measured reading-error rate.

Recommendation: For identifiers, provide a distinguishable zero alternate or avoid relying on O/0 discrimination. Keep the ordinary zero for financial amounts if desired.

Acceptance: Review randomized O/0 identifiers at 12/14/16px on target rasterizers and validate a distinguishable optional zero with actual shaping.

## P3 DATA-03: Small data typography needs a weight policy

Native 12/14/16px proof shows wght 100 markedly faint; 900/opsz 128 is markedly dense at these small sizes. wght 400–500/opsz 9–14 gives visibly more even numeric and currency reading in these samples.

Recommendation: Use 400–500 with text optical sizes for dense dashboards; reserve extremes for intentional display treatment.

Acceptance: Inspect realistic data tables at 12/14/16px and target DPRs, including hover/disabled states, before adopting weight extremes.

## Evidence and limits

- [Large numerical proof](../../build/matrix002/data/numeric-proof.png)
- [Native 12/14/16px proof](../../build/matrix002/data/native-numeric.png)
- [Measurements](../../build/matrix002/data/measurements.json)

- No prior/current reviewer reports were consulted. No font/source changes made.
- WOFF2 tested after decoding with fontTools, not browser network loading; no CoreText or DirectWrite validation.
- FreeType grayscale rendering at native 12/14/16px plus 28–32px representative numerical proof; no user reading-error study.
- Coverage probe also found ₹ ₩ ₴ ₸ ₿ and ≈ absent; relevance depends on intended product languages and markets.
- No continuous variable-axis sweep or full glyph-outline/collision audit.

Font SHA-256:

- `dist/TabunaSansVariable.ttf`: `3567058955eb20ebaf25ef5241a094b25d86dfd7be966f8032492dd3caa3e011`
- `dist/TabunaSansVariable.woff2`: `d07839f04ebdbfb89fed1c4f9d5d2609197db1071251bd5cf8ab0db5f626b207`
