# Independent OpenType engineering audit — 0.0.3

This is a fresh automated engineering review, not a human reading study or Apple review. No previous reports, matrices, existing test results or other reviewers’ findings were read. Font/source files were read only. Script: `scratchbuild/matrix003/engineering/audit.py`.

TTF SHA-256: `56cb3cbd30099ed97b0395e7eae28f9431e84ff9eede14cdfb4061f1c5873edc`  
WOFF2 SHA-256: `090801dbfa6086e63678a38df35c522f3032164b2e4bced9e692121bccef704e`

## Fresh evidence

- 31,588 HarfBuzz shaping calls across a 25-position grid: wght 100/250/400/650/900 × opsz 9/14/32/72/128.
- 4,050 TTF-versus-decoded-WOFF2 comparisons across 18 strings and nine feature configurations: identical glyph IDs, clusters, advances and offsets.
- 450 default-versus-pnum comparisons: identical.
- 25 equal-width digit checks: passed.
- 225 exhaustive separator sets × 100 digit combinations: constant total width with tnum for colon, period, comma, slash, hyphen, plus, minus, percent and space.
- 5,450 glyph bounds checks: finite and correctly ordered at every sampled location. This does not prove that outlines have no intersections.
- Zero failed assertions. JSON contains exact feature-range and punctuation shaping evidence.

At wght=400, opsz=14, default `1:2` uses one=928, colon.case=596, two=1214. With tnum it uses one.tnum=1286, colon.case=586, two.tnum=1286. Disabling calt selects colon without changing advances. Both Latin and Cyrillic uppercase contexts select colon.case; lowercase contexts and spaced `1 : 2` retain colon. Mixed numeral feature ranges retain the contextual colon choice.

## Integration observation (P3)

Explicit pnum=1 plus tnum=1 resolves to proportional numerals. This is not an observed font defect, but inherited raw feature settings can defeat a caller’s intended tabular alignment. Document mutually exclusive choices, and use pnum=0 when explicitly forcing tnum. Acceptance: tnum=1,pnum=0 gives every digit advance 1286 at 400/14; application controls avoid conflicting settings.

## Scope verdicts

- UI: **conditional pass** for tested numeric and punctuation mechanics; native rendering untested.
- Headings: **conditional pass** for sampled variable-font mechanics; visual quality requires separate assessment.
- Body: **unproven**; technical success does not establish legibility or text rhythm.
- Sustained reading: **unproven**; no reader study or fatigue assessment.

HarfBuzz/fontTools only. No CoreText/browser rendering, pixel inspection, continuous-axis proof, intersection analysis, actual reader or Apple approval. No blocking engineering defect found within this bounded test scope.
