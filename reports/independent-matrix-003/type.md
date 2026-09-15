# Independent type designer audit — Tabuna Sans 0.0.3

SHA-256: `56cb3cbd30099ed97b0395e7eae28f9431e84ff9eede14cdfb4061f1c5873edc`

Inspected the current dist TTF and newly generated proofs only. Did not read old reports, matrices, or other reviewers’ findings. Source font was not modified.

Proofs use HarfBuzz shaping and FreeType grayscale rasterization. All three PNGs were visually inspected through view_image. RU/EN UI 14 px, body 18 px, headings 40 px; weights 100/400/900 and numerically matched opsz. Identity lines cover I/l/1, O/0, rn/m and Cyrillic distinctions.

- **ui: conditional_pass** — 400 at 14 px has legible labels, punctuation and Russian/English rhythm. 100 is visibly faint at this raster size and 900 is dense; neither extreme should be the default. Alphanumeric identifiers need extra care for O/0.
- **headings: pass** — At 40 px all three weights have coherent RU/EN proportions and clear word silhouettes; no obvious collisions or closed counters in these samples.
- **body: conditional_pass** — 400 at 18 px is convincing in the short RU/EN samples; counters and word spacing remain clear. Weight 100 is delicate and 900 emphatic, appropriate stylistic extremes rather than demonstrated drawing defects.
- **sustained_reading: unproven** — The regular short paragraphs look promising, but a few lines of visual review cannot establish comfort over sustained reading.

## P2 — Alphanumeric tokens containing O and 0 at 14 or 18 px, especially when context does not reveal which character is intended. O and zero differ mainly by width; both remain unslashed ovals.

For identifier-heavy interfaces, consider an optional differentiated zero (such as a slashed-zero feature) or choose a separate identifier treatment. This is a use-case limitation, not a general body-text defect.

Acceptance: Render random mixed O/0 identifiers at 14/18 px with the optional treatment enabled and verify that the character distinction no longer relies primarily on width; follow with real reader identification testing if this is a product requirement.

## P3 — Weight 100 at 14 px on a 1× grayscale raster loses visual strength; weight 900 makes multiline 18 px prose markedly dark.

Document regular around 400 as the initial UI/body choice and reserve these extremes for deliberate display/emphasis use. Do not change outlines based solely on their intentionally thin or heavy character.

Acceptance: Check target-platform UI/body examples at actual display scale using intended foreground/background colors and selected production weight.

## Evidence

- `scratchbuild/matrix003/type/weight-100.png`
- `scratchbuild/matrix003/type/weight-400.png`
- `scratchbuild/matrix003/type/weight-900.png`

## Limits

- One grayscale FreeType rendering environment; no browser/CoreText comparison, HiDPI comparison or low-contrast backgrounds.
- Only 14/18/40 px and weights 100/400/900, not an exhaustive variable-axis sweep.
- opsz equals numerical pixel size in these proofs; production CSS optical sizing can follow different point-size conventions.
- No human reading study, no measured reading speed or fatigue result.
- No extended paragraphs, full glyph inventory, language coverage or shaping correctness certification.
