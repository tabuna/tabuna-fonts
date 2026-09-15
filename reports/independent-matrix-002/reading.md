# Independent reading review — matrix 002

Artifact SHA-256: `3567058955eb20ebaf25ef5241a094b25d86dfd7be966f8032492dd3caa3e011` (verified).

This is a completed model visual review, not human research. I inspected the blind paired image first, then independently rendered the actual variable font using Pillow/FreeType. I did not read prior reports or the blind key.

## Blind assessment

- UI 18px and body 22px, Russian and English: **indistinguishable**, medium confidence. No reliable difference in rhythm, word spacing, or texture in these phrases.
- Headings 48px/500: **indistinguishable**, medium confidence. Both versions maintain similar spacing and open counters.
- Confusion rows 54px/100 and 54px/900: **B preferred for capital-I distinction**. B has visible horizontal terminals on I, separating it from l. High confidence in the visible cue; low confidence in a reading-performance benefit without testing. Other glyphs provide no clear preference; O/0 remain similar oval silhouettes.

## Actual-font examination

The accompanying `reading-actual.png` shows 14/16/18px, weight 400, opsz 14 UI labels, three-line Russian and English paragraphs, and confusion strings; headings are 48px/500/opsz48. Short text has consistent word boundaries and a calm, even texture. I found no conspicuous spacing collision or counter loss in these samples. The capital I has useful crossbars. Small-size O/0, З/3, and narrow l/1 deserve transcription testing, especially in identifiers lacking word context. Similarity is a test hypothesis, not measured failure.

| Use | Verdict | Scope |
|---|---|---|
| UI | Conditional | Ordinary labels look coherent; ambiguous codes need task testing. |
| Headings | Pass | Visual pass for the two 48px/500/opsz48 samples only. |
| Body | Conditional | Short 14–18px paragraphs look balanced; broader browser/device and reading checks remain. |
| Sustained reading | Unverified | No human speed, comprehension, or fatigue data. |

No global spacing change is justified by this proof. Retain the capital-I cue. Inspect representative browser rendering at 1x/2x and 14–18px/400–600 before release, checking line clipping, collisions and word boundaries. Test I/l/1, O/0 and З/3 with context-free identifiers before deciding on further shape changes or an optional distinct-zero feature.

## Minimal human pilot

Recruit 8–12 target readers with Russian/English fluency represented. Use masked labels and counterbalanced current/incumbent font order; rotate matched passages to prevent repeated-text learning. Match x-height and line length for the main comparison, and separately check native product CSS. Per font, use two 500–700-word passages with comprehension questions, a 10-minute reading block plus comfort rating, and 24 short identifier-transcription trials distributed across 14/16/18px. Record reading time, comprehension, pair-specific substitution errors, identifier completion time, comfort, device/DPR and text-size preference.

Review paired participant outcomes for recurring confusion clusters or reduced comprehension. The pilot diagnoses problems; it cannot establish equivalence or superiority. Set an acceptable margin before a larger confirmatory study. JSON supplies condition/evidence/recommendation/acceptance-test entries.

Limitations: one model reviewer; selected axes/text only; short paragraphs; Pillow rather than target browser/OS rasterization; no pixel-diff measurement, human experiment, full accessibility determination, or sustained-reading claim.
