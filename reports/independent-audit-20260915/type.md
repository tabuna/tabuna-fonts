# Independent typographic review — Tabuna Sans

Font SHA-256: `5888eecc912f46f14b7807906d2ffc0a42d543a3695465b76a83b699373344b9`.

**Verdict:** credible candidate for Latin/Russian UI and headings; no release-blocking core letterform defect established in the bounded specimens. This is an independent AI role review, not an Apple or human panel endorsement. Prior verdicts were not read.

- **P2, integration:** bullet/per-mille render as an oval in a font-only proof because they are absent. The approved189-character scope intentionally excludes them: preserve scope, test fallback/content policy. Normal browser fallback can resolve the issue; this reviewer did not validate it.
- **P2, usage:** w100 is visibly fragile at9–20px in1x raster. Avoid as functional UI/body default.
- **P2, usage:** forcing opsz128 into9–16px text visibly tightens strings; do not freeze display optical sizing for UI. Small confusables require human testing.

The inspected a/а, P/Р, B/В/в and Л/Д/Ж/К/Я families are coherent. Similar Latin/Cyrillic forms are expected. I/l/1 have different cues; rn/m are not proven to collapse. w900 produces dense but not demonstrably broken headings. Preference for w400 over500 in long text is not a measured reading result.

Initial scenario hypotheses: UI14–20px w400–500; body16–18px w400 (500 for added presence), line-height1.45–1.6; headings24–48px w500–700,900 for short emphasis. These are test starting points, not universal limits. Native-platform scaling, dark mode, low-vision use and sustained reading need human validation.

Evidence and per-finding conditions, confidence, recommendations and acceptance tests: `type.json`. Proofs: `build/independent-audit-20260915/type/`; see `body-native.png`, `ui-native-opsz14.png`, `ui-detail-opsz9.png`, `ui-detail-opsz128.png`, `families-24px-opsz14.png`, `heading-detail-opsz9.png`. JSON includes hashes of all proofs. Method: Pillow/FreeType1x, fontTools; not CoreText. Some contact sheets downscaled during viewing; native UI crops also inspected.
