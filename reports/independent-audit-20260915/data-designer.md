# Independent numeric/data UI visual review

Heavy tabular numerals visibly crowd and join, making them unsuitable for approval as large KPI or emphasized-total numerals at the demonstrated settings. Normal 400/500 text numerals look materially more readable; that is not a completed tabular table test.

TTF SHA-256: `5888eecc912f46f14b7807906d2ffc0a42d543a3695465b76a83b699373344b9`
WOFF2 SHA-256: `9c5c23886f3cac3acca41e9db66bdde9a69e5145453e1a84e24605bc31b43e59`

## P1 — Heavy tabular digits lose visible separation

**Conditions:** tnum, wght=900/opsz=128/100px and wght=725/opsz=48/100px; also visibly compressed at wght=900/opsz=24/48px and wght=900/opsz=18/18px. Exact text 0044886699.

The left-column repeated 0/4/8/6/9 sequence reads as connected or near-connected black masses, most clearly at the first two settings. The matched proportional sequence has appreciably clearer spacing. This affects counting and scanning digits in large KPIs and emphasized totals even if every digit receives an equal advance. At 18px the string remains decipherable but looks substantially tighter; exact contour contact cannot be established from that small raster alone.

**Confidence:** High for the visual separation failure at large sizes; medium for resulting reading-performance impact and 18px severity.

**Acceptance:** At each demonstrated setting, preserve equal digit advances while producing visibly separate adjacent digits in 0044886699 and all 100 digit pairs. Verify contour clearance independently and inspect realistic 18px totals and 48–100px KPI values at native 1x/2x. No apparent joining in representative dark/light browser renders. Do not infer an exact axis-wide failure threshold from four examples.

## P2 — Tabular pricing guidance lacks a demonstrated table-and-punctuation acceptance case

**Conditions:** README applies tabular-nums to price and counter without a weight qualification; existing viewed normal-text punctuation fixture is 14px/opsz14, weights400/500, default features.

At normal 400/500, 1,234.56 and 1 250 ₽ have recognizable separators and sensible visible spacing; isolated currency signs remain distinct. No decimal/currency defect is established here. However those samples are neither stacked decimal columns nor explicit tnum proofs. Equal-width digits alone cannot establish alignment of signs, variable fractional lengths or mixed currency placements, and the heavy proof establishes a separate ink-spacing problem.

**Confidence:** High that the current viewed evidence does not demonstrate table alignment; medium that the unqualified README example encourages affected heavy-price usage.

**Acceptance:** Add a right-aligned table with 400/500 body values and 700/900 totals at14/16/18px, plus KPI values at32/48/72px. Exercise 0.00, 11.11, 88.88, −1,234.56, 1 234,56 ₽, $1,234.56, 1.234,56 €, repeated zeros and changing counters under explicit tnum. Verify stable digit advances separately from visible gaps and decimal alignment; use consistent formatting or layout for currencies and decimals. Check ordinary/NBSP spacing. Qualify heavy-use guidance if DD-1 remains unresolved.

## Evidence and limits

- README.md:77-92
- build/independent-audit-20260915/engineering/digit-proof.png
- build/independent-audit-20260915/type/ui-native-opsz14.png
- build/independent-audit-20260915/type/14px-detail-nearest2x.png
- Proof generation scripts read only to establish text/settings/rendering provenance; no engineering conclusions or prior reviewer verdicts read.

Image-based visual assessment, not a user reading study or browser acceptance run. Did not infer normal400/500 tnum quality from default-feature body samples. Did not inspect engineering numeric results. SHA identifies current distribution bytes; proof-generation scripts reference the current TTF but images were not independently regenerated in this short review.

Independent numeric/data UI visual reviewer; not a named external designer or Apple representative
