# Independent character and recognition review — matrix 003

Role: character/recognition reviewer. Evidence: direct visual inspection of `build/matrix003/blind.png` before reading any identity key, source, design documents, or other reviews. The key remains unread. This is an independent model visual assessment, not a human recognition experiment. Font/source files were not modified. The distributed TTF SHA-256 was independently checked as `56cb3cbd30099ed97b0395e7eae28f9431e84ff9eede14cdfb4061f1c5873edc`.

## Blind observations

| Pair | Preference | Observation |
|---|---|---|
| 1, Latin 16/400/14 | Indistinguishable | Same apparent width, spacing rhythm, and unobtrusive sentence color. No dependable character advantage. |
| 2, Cyrillic 16/400/14 | Indistinguishable | Both show a calm, compact Cyrillic line; no dependable difference in the recurring д/о/л forms. |
| 3, Latin 24/400/24 | Indistinguishable | Repeated a/r/e and round forms produce the same apparent rhythm; neither establishes a stronger recurring signature. |
| 4, Cyrillic 24/400/24 | Indistinguishable | Repetition of о/л/д remains coherent in both. No visible comparative preference. |
| 5, Latin repeat | Indistinguishable | Consistent with pair 1. |
| 6, Cyrillic repeat | Indistinguishable | Consistent with pair 2. |
| 7, Cyrillic 48/500/48 | Indistinguishable | Readable conventional Cyrillic construction and even word rhythm; no visible X/Y advantage. |
| 8, Latin 48/500/48 | Indistinguishable | The long line retains the same general character in both. |
| 9, mixed 48/100/48 | X, moderate confidence | X's capital I has horizontal terminals, helping separate it from lowercase l and numeral 1. Remaining glyphs appear equivalent. |
| 10, mixed 48/900/48 | X, moderate confidence | The terminal treatment again separates capital I from lowercase l. This is a local glyph distinction, not evidence of recurrent family character in prose. |

Repeat consistency: both explicit repeated sentence conditions agree (1/5 and 2/6). The preference for X in the two diagnostic groups is consistent across the two displayed weights, but these are not identical repeat trials. No claim of measured recognition accuracy follows.

## Character and application verdicts

The common visual impression is restrained, compact and suitable for a moderate UI tone. Cyrillic words look coherent on their own: л/д and the sampled б/я are recognizable Cyrillic constructions rather than a requirement to resemble Latin. This is a visual judgment on a narrow sample, not a complete Cyrillic audit. The paired prose does not establish an X/Y difference in repeated character. A distinctive capital I may help disambiguation while doing little to change the identity of ordinary lines that rarely contain it.

| Use | Verdict |
|---|---|
| UI | Conditional: displayed 16px labels look usable; diagnostic I benefit is only shown at 48px. Verify at actual UI sizes. |
| Headings | Provisional visual pass for sampled 24px and 48px lines; no comparative character winner. |
| Body | Conditional: short lines look even, but paragraph rhythm and reading comfort remain untested. |
| Sustained reading | Not established: no long passage, timed reading, comprehension, or human evidence. |

## Findings

1. **Local disambiguation benefit.** Condition: Il1 at 48px, weights 100 and 900. Recommendation: preserve/test X's capital-I distinction if UI identifiers matter. Acceptance test: render mixed Il1/O0 identifiers at 12, 14, 16, and 18px on target displays; inspect clipping and spacing, then run a blinded human transcription task to measure errors. Do not infer O/zero differentiation from this I-specific observation.
2. **Recurring character advantage not demonstrated.** Condition: all paired running-text specimens at 16, 24, and 48px. Recommendation: do not justify a choice with greater family recognition on the present evidence. If stronger signature is required, evaluate a restrained set of frequent forms and their repeated texture. Acceptance test: blinded paragraphs in each script, with diagnostic isolated letters omitted, repeated with shuffled order; require a predeclared, repeatable preference/identification result from human readers before claiming recognition gains.
3. **Cyrillic evidence is narrow but visually coherent.** Condition: displayed Russian sentences and diagnostic glyph groups. Recommendation: retain the independent Cyrillic word-shape criterion. Acceptance test: expanded Russian paragraphs and UI strings, including dense repeated л/д/п/и/ш/щ and б/в/ь/ъ sequences, reviewed by native readers at intended sizes.

Limitations: one static raster sheet; no key decoding; no source inspection; no font-table or outline audit; no human participants or recognition measurements; no mobile rendering, dark mode, paragraph reading, or complete character coverage. Indistinguishable means no reliable difference observed here, not proof of identical outlines. The verified TTF hash identifies the delivered file, but without decoding the key this report does not assign X/Y to that file.
