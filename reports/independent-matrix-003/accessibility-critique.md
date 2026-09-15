# Accessibility cross-critique — discussion phase

The initial raster reports remain unchanged. This follow-up intentionally reads `hig.md`, `ui.md` and `enlargement.json`; it is no longer an independent first-pass opinion. No new browser tests were performed.

## Narrow enlarged reflow

Confirmed integration defect under the tested CSS-root enlargement simulation. UI and root agree on document width517px at viewport320px, versus320px normally. HIG source-risk wording is accurate for its original evidence but can now be updated in synthesis to reproduced under this condition.

**Severity:** P1 for shipping the demo as robust accessible integration; not P1 against the font binary or a reason to redraw glyphs.

**Required action:** Fix hero wrapping and control/grid intrinsic sizing. Accommodate enlarged numeric tables with accessible localized overflow or responsive structure if their two-dimensional task requires it; avoid page-wide overflow.

**Acceptance:** At320px and root32px, document scrollWidth<=clientWidth+1, title and controls fully available, no overlap/clipping. Check normal320px and desktop afterward. Separately test real browser zoom and target text preferences before claiming those modes pass.

## Absolute-pixel live specimen

Intentional exact-size proofs are legitimate and necessary for font inspection. Fixed px alone does not establish an accessibility failure when labeled and adjustable and when a separate reading sample scales. These reports correctly recommend distinguishing modes; synthesis should not treat all px sizes as prohibited.

**Severity:** P2 clarification/preview improvement, conditional on whether a role preview is presented as production-like scalable content; not a demonstrated font defect.

**Required action:** Label exact-pixel proof mode and preserve its measurement accuracy. Provide or clearly identify a scalable reading/UI preview; do not silently scale the exact-pixel specimen while retaining a false px label.

**Acceptance:** A user can distinguish the measured pixel specimen from scalable content. At doubled root size the designated scalable preview enlarges without losing text/actions, and the exact-pixel specimen continues matching its displayed numeric size.

## Thin100 at12–18px

Independent raster evidence supports a usage restriction: low coverage and weak punctuation in these small sizes on light/dark synthetic renders. It does not prove malformed outlines or require changing the100 master. No actual browser Thin trial was supplied by these inputs.

**Severity:** P1 only if Thin is selected for essential small UI/body; otherwise document as a usage limit, with no mandatory font redraw.

**Required action:** Default essential small text to400/500 and reserve100 for size-specific display experiments. Validate a proposed Thin use on target renderers before relaxing that restriction.

**Acceptance:** Essential labels and body use the tested robust weights; any exception has native-size target-platform proof of distinguishable strokes/punctuation in light and dark contexts. Existing font design can satisfy this without outline edits.

## Body and sustained-reading claims

UI short-body pass and HIG conditional body verdict concern different evidence levels and are compatible. Neither short paragraphs nor synthetic isolated lines establish prolonged comfort, comprehension, or fatigue. Lack of evidence is not evidence of font failure.

**Severity:** P2 validation/claim-scope gap before strong long-form or broad accessibility-readiness claims; not a release-blocking defect for a clearly provisional font.

**Required action:** Retain provisional scope, add realistic extended RU/EN reading fixtures and dense controls, then conduct the needed reader/platform evaluation before stronger claims.

**Acceptance:** Release language names tested roles/platforms and does not promise sustained readability from these checks. Stronger future claims are backed by documented task and reader outcomes, not screenshots alone.

## Limits

- Cross-critique evaluates reported evidence; no fresh runtime reproduction.
- Root font-size doubling is distinct from browser page zoom and Apple Dynamic Type.
- WOFF2 browser evidence and TTF synthetic evidence are separately identified; this review does not establish binary equivalence.
- No formal WCAG conformance or Apple endorsement inferred.
