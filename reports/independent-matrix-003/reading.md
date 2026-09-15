# Independent reading assessment — matrix 003

Actual image inspection completed blind-first. I did not read the identity key or other reports, and did not modify fonts or sources. X/Y identities remain unknown. This is agent visual assessment, not a human reading study.

Font SHA-256: `56cb3cbd30099ed97b0395e7eae28f9431e84ff9eede14cdfb4061f1c5873edc`.

## Blind observations

Pairs 1–8: **indistinguishable for a robust reading preference** at the supplied viewing scale. English UI repeats 1/5 and Russian UI repeats 2/6 give the same result. No demonstrated difference in prose/UI/headings should be inferred from this inspection.

Pairs 9 and 10: **X preferred, moderate confidence**, specifically for the capital I horizontal terminals and resulting I/l/1 differentiation at 48px thin and black. This is a diagnostic glyph preference, not a general reading preference.

Evidence: `build/matrix003/blind.png` (actually viewed).

## Independent current-font proof

Rendered actual `dist/TabunaSansVariable.ttf` through Pillow/FreeType, then viewed `scratchbuild/matrix003/reading/proof.png`. Proof includes Russian and English 16px/400 UI, dates/currency, five-line body paragraphs at opsz16, 36px/500 headings at opsz36 and 24px diagnostic characters.

UI: **provisional pass**. Labels and numerals remain readable, without conspicuous spacing failures. Headings: **provisional pass**. Both scripts show coherent rhythm and open counters. Body: **provisional pass** for the short passages inspected; color is even and words remain easy to parse. Sustained reading: **unproven**; fatigue, speed and comprehension require human measurements.

## Recommendations and acceptance tests

- **P2:** Evaluate capital-I differentiation in realistic 12–16px identifiers across weights 400/500/700 and opsz9/14/16. Acceptance evidence should include randomized human transcription of I/l/1 strings.
- **P2:** Keep sustained-reading claims provisional. Run counterbalanced 10–15 minute Russian and English reading sessions, measuring comprehension, errors, preference and discomfort against a named reference at matched apparent size.

## Limits

One supplied raster and one independent Pillow rendering. No browser/device coverage, small 12px UI, dark mode, low contrast, or real application tested. Independent 16px proof uses opsz16, while blind UI uses opsz14. Parent identifies artifact as 0.0.3; hash above identifies the exact file. No blind identities decoded.
