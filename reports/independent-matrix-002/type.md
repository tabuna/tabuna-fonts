# Independent construction review — Tabuna Sans 0.0.2

Independent type designer perspective: humanist UI sans construction review; not impersonation or attributed expert opinion.

SHA-256: `3567058955eb20ebaf25ef5241a094b25d86dfd7be966f8032492dd3caa3e011`

No previous audit, report, or other reviewer output read before writing this report. Font and source unchanged.

## Verdicts

- **ui: conditional** — Regular at14–20px is visually serviceable for ordinary RU/EN labels. Identifier differentiation and small thin/heavy text need usage restrictions and target-device verification.
- **headings: pass** — Inspected36–72px samples have coherent shapes at100,400,900, including Cyrillic. Pass is visual construction judgment for this sample, not universal kerning or glyph coverage certification.
- **body: conditional** — Regular16–20px paragraphs show stable texture in both scripts. 14px is serviceable in these proofs but platform validation remains; 100/900 are not approved as paragraph defaults.
- **sustained_reading: unverified** — Short static proof inspection cannot establish fatigue, comprehension, or sustained reading performance.

## Method

Created independent RU/EN proofs at weights100/400/900. Pillow/FreeType BASIC at12/14/16/20/36/64px with matching opsz, plus72px construction panels atopsz14. Separate HarfBuzz+FreeType proof at14/48px and optical endpoints9/128. Inspected all six generated images with view_image. Font metadata reports189 cmap entries.

## Findings

### T01 — l I 1 O 0

**Condition:** UI identifiers, wght100/400/900, 12–16px; verified construction at 48/72px. **Severity:** medium.

Capital I has short bars and 1 an angled flag, but lowercase l is a plain stem; O/0 distinction relies chiefly on proportion. At small sizes the diagnostic group needs context, especially in thin weight. This is a limited differentiation vocabulary, not proof that ordinary prose is unreadable.

**Attribution:** construction with size-dependent raster amplification.

**Recommendation:** Consider optional hooked l and slashed/dotted zero for identifier-heavy UI; preserve current prose defaults until comparison.

**Acceptance test:** Blind transcription of randomized I/l/1 and O/0 codes at 12/14/16px, several rasterizers, compare current vs alternate; report error counts before choosing a change.

Evidence: [constructions.png](../../build/matrix002/type/constructions.png), [proof-400.png](../../build/matrix002/type/proof-400.png), [hb-optical-extremes.png](../../build/matrix002/type/hb-optical-extremes.png).

### T02 — a e s c; RU/EN entire text

**Condition:** wght100 at 12–16px, correctly matched opsz12–16. **Severity:** medium.

Thin strokes render pale and weak beside regular even on black-on-white. Shapes remain coherent at 36–72px. Thin is unsuitable as the default small essential text in this proof.

**Attribution:** intended thin construction interacting with grayscale rasterization; no isolated broken contour demonstrated.

**Recommendation:** Keep 100 for sufficiently large display text; select regular for body and essential UI. Do not thicken every master on this evidence.

**Acceptance test:** At target-device native size, thin labels must meet the same measured transcription accuracy as regular before approving essential small-text usage.

Evidence: [proof-100.png](../../build/matrix002/type/proof-100.png), [constructions.png](../../build/matrix002/type/constructions.png).

### T03 — e a g; в е ы ь; word spaces

**Condition:** wght900 12–16px, strongest when opsz128 is forced at 14px. **Severity:** medium.

Heavy small text has compact counters and a dense texture. At opsz128, spaces and sidebearings visibly contract; RU/EN words in the 14px line approach a continuous dark band. At opsz9 these lines have substantially clearer separation. Large heavy headings remain clear.

**Attribution:** weight and optical-size construction, not a shaping failure; opsz128 at14px is intentionally a mismatch stress test.

**Recommendation:** Use matched/automatic optical sizing and avoid heavy for paragraphs. Verify low-opsz counter openness before changing the heavy master.

**Acceptance test:** Render 900 at 12/14/16px with opsz9/14/16 on CoreText and FreeType; retain discernible counters and word boundaries; compare only matched opsz for product approval.

Evidence: [proof-900.png](../../build/matrix002/type/proof-900.png), [hb-optical-extremes.png](../../build/matrix002/type/hb-optical-extremes.png).

### T04 — д л м н п и ш щ; a g r n m

**Condition:** wght400, 14–20px paragraphs and 72px construction proof. **Severity:** low.

Latin double-storey a and single-storey g are familiar; Cyrillic has conventional upright constructions and broadly comparable color. Rectilinear Cyrillic runs produce more repeated verticals than Latin, but no individual malformed letter or strong cross-script size mismatch was evident. Overall character reads closer to a neutral grotesque than a strongly calligraphic humanist sans.

**Attribution:** design character; not a defect by itself.

**Recommendation:** Preserve script coherence; if stronger humanist character is a goal, trial localized terminal/shoulder and l differentiation rather than changing Cyrillic to unfamiliar forms.

**Acceptance test:** Compare mixed-script paragraphs and ш/щ/и/п runs at16px and headings at48px; changes should improve identification without a new script-color imbalance.

Evidence: [reading.png](../../build/matrix002/type/reading.png), [constructions.png](../../build/matrix002/type/constructions.png).

## Limits

- AI visual inspection, not human reading study or an actual named type designer review.
- Pillow lacks RAQM; base proof uses BASIC layout. Separate HarfBuzz+FreeType proof checks shaped examples, not the entire corpus.
- Only 3 weight instances and sampled optical sizes, not interpolation sweep.
- No browser/CoreText/DirectWrite or high-DPI comparison.
- 64px long lines clip at right canvas edge; judgments restricted to visible segments; full shorter48px headings are provided in hb-optical-extremes.png.
- No exhaustive189-character, kerning-pair, contour topology, or accessibility certification.
