# Independent numeric UI and data review — 0.0.3

TTF SHA-256: `56cb3cbd30099ed97b0395e7eae28f9431e84ff9eede14cdfb4061f1c5873edc`  
WOFF2 SHA-256: `090801dbfa6086e63678a38df35c522f3032164b2e4bced9e692121bccef704e`

I did not read earlier reports, matrices or other reviewers’ findings. Font and source files remained read-only. The fixed 189-character repertoire was accepted.

**Numeric UI: pass with conditions.** At 400–700/opsz9–14, timers, prices and decimals look clear at 16px. Numeric headings at 32px pass within the same qualification. Inline numeric body content is supported; sustained prose reading is not assessed by this narrow review.

HarfBuzz tested nine axis locations × default/tnum/pnum × calt off/on: 54 conditions, 540 digit advances and 1,080 numeric sample shapes. Actual FreeType outlines were rendered in 108 runs at 16px and 32px, and the resulting proof was inspected. Relevant WOFF2 cmap, GSUB, GPOS, hmtx, glyf, gvar and fvar tables exactly match TTF.

All 18 tnum conditions have identical digit advances, invariant widths across six timer states, and equal decimal suffix widths for right-aligned two-decimal values. Default and pnum deliberately retain proportional widths. calt raises the colon between digits without changing width: at400/14, the numeric colon spans y101–604 versus the ordinary colon −4–500 (normalized to1000). Decimal periods remain on the baseline; currency and minus signs are recognizable.

- **P2 integration:** enable tabular-nums for changing values and right-align equal-precision amounts. Default proportional figures can shift a counter. Acceptance: cycle 00:00:00,11:11:11,88:88:88,12:34:56,09:59:59,10:00:00 without width changes; verify decimals for1.11,12.34,123.45,1234.56 align when right-aligned.
- **P2 usage limit:** weight100 at16px has faint hairlines, especially opsz128. Prefer400–700/opsz9–14 for critical data. Acceptance: inspect the target1x/2x renderer at intended contrast and confirm every digit and decimal/colon mark is readable without zoom.

Evidence: `scratchbuild/matrix003/data/proof.png`, `metrics.json`, `review.py`. Font defects requiring an outline change were not identified. The proof was rendered directly through FreeType with HarfBuzz glyph selection; this is not a browser or long-form readability study. calt-off comparisons are metric-only. tnum does not solve mixed decimal precision or inconsistent application alignment.
