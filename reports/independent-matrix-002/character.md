# Independent type-character review

Role: Independent brand/type-character reviewer (AI visual assessment).

Current TTF SHA-256: `3567058955eb20ebaf25ef5241a094b25d86dfd7be966f8032492dd3caa3e011`.

## Locked blind assessment

**No preference: A and B are indistinguishable in the supplied real RU/EN lines.** Confidence is high that this sheet does not show an obvious repeatable line-level change; confidence in broader brand positioning is moderate. This judgment was persisted before reading the font binary for its hash. A/B identities remain unknown.

The RU UI line, RU/EN body sentences, and RU/EN headings retain effectively the same visible width, rhythm, color, openness, and word silhouettes. B has a visibly barred capital I in the diagnostic rows at both extreme weights. That is a local identification cue, not demonstrated line-level character differentiation.

Both look compact, clean, relatively open at regular text sizes, and restrained. A moderately humanist reading is plausible. The Cyrillic Л/л and Д/д are recognizable local forms, but these few words cannot establish a distinctive, self-contained Cyrillic voice.

## Tests and verdicts

Viewed `build/matrix002/blind-pairs.png`: RU UI at 18px/400/opsz14; RU/EN body at 22px/400/opsz18; RU/EN headings at 48px/500/opsz48; diagnostic forms at 54px/100 and 900/opsz64. Verified the current TTF hash after locking the blind judgment.

| Use | Verdict | Scope |
|---|---|---|
| UI | conditional | Real labels look coherent; identification cue is only shown at large sizes. |
| Headings | pass | Shown RU/EN headings are readable and rhythmically coherent; distinctiveness is not proven. |
| Body | conditional | Single sentences look calm; paragraphs and target body sizes are absent. |
| Sustained reading | unverified | No sustained reading material or reader study. |

These visual verdicts apply to both specimens; the current-font hash does not decode their identities.

## Findings and acceptance tests

1. **No repeatable line-level A/B character change.** Avoid claiming a proven personality improvement. Acceptance: randomized, order-swapped unfamiliar RU/EN sentences with repeated changed forms and repeated preference/identification judgments.
2. **B's capital-I bars are a visible local difference.** Test them as an identification feature. Acceptance: real labels, names, and identifiers containing I/l/1 at actual UI sizes remain readily distinguishable.
3. **Headings have steady spacing and compatible Latin/Cyrillic color.** Continue this restrained direction and broaden Cyrillic coverage. Acceptance: representative Cyrillic combinations, punctuation, numbers, and mixed scripts in headings and paragraphs at regular/bold weights.
4. **Reading claims exceed current evidence.** Keep them provisional. Acceptance: multi-paragraph RU/EN proofing at intended sizes/line lengths, plus actual reader testing for reading-comfort claims.

## Limits

AI visual judgment only; no human results or named-designer impersonation. No identity key, prior/current reports, or source font outlines read. No source edits. No paragraph, timing, print, low-resolution-device, or cross-platform testing. The observed similarity does not prove technical identity.
