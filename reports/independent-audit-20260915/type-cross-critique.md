# Type review: cross-critique of engineering evidence

Date: 2026-09-15. This addendum does not modify the independent initial verdict or its evidence. It revises scenario conclusions after newly supplied evidence. AI role reviewer; no human or Apple endorsement.

## Confirmed P1: tabular digits collide in the heavy/display region

The engineering method is substantially sound. `digit_collisions.py` obtains outlines at the same wght/opsz coordinates used by HarfBuzz, decomposes components, applies HarfBuzz advances/offsets, and computes the actual filled-path INTERSECTION with pathops. This is **not a bounding-box-only test**. No extra negative tracking is applied. I independently checked the HarfBuzz scale:2048 units, equal to the font UPM2048. Horizontal LTR digit pairs make omission of accumulated y advance immaterial here.

Independent shape-position checks: `44` at w725/opsz24 uses tnum glyph68, two advances1198; pnum uses glyph67, two advances1355. At w900/opsz128, tnum advances1162 versus pnum1385. The script correctly tests the feature-selected glyphs, not merely the default digit outlines at hypothetical widths.

The JSON contains217 positive-area cases among4800 sampled pair/location combinations. These cluster at725/24(1),725/48(3),725/96(14),725/128(14),900/18(8),900/24(35),900/48(45),900/96(49),900/128(48). The count is not a percentage of all continuous axis positions or all application text.

I inspected `digit-proof.png` and its renderer. It renders actual HarfBuzz feature selection through FreeType and compares tnum/pnum at identical size/axis settings, without added tracking. At100px/w900/opsz128 and100px/w725/opsz48, neighboring tnum digits visibly join, especially44 and the rounded families; pnum stays separated in the same proof. The48px/w900/opsz24 row also looks materially congested. This is a genuine spacing/outline interaction failure for ordinary tabular numbers, not merely a preference for generous spacing.

**Severity calibration:** the217 cases are not equally visible. The earliest725/24 `44` intersection is only about2.42 font units wide (about0.057px at48px). Some findings are subpixel slivers; do not illustrate every result as a gross collision. Conversely900/128 `44` has94 units of overlapping width, about4.59px at100px, and27918 square units of intersection. That case is visually significant. Near-zero tolerance should still be checked for numeric robustness, but is not needed to establish the large defects.

**Revised scenario recommendation:** block a release claim of reliable full-range tnum until fixed, or explicitly constrain that feature's permitted region. The initial UI400/500 hypothesis is not contradicted by this heavy-region finding. Numeric headings, large counters, scoreboards and bold table totals using tnum must not inherit my initial broad heading recommendation without this exception. pnum can be an interim option for standalone numeric headings only when tabular alignment is unnecessary and its spacing has been separately verified. Do not fix one sample with arbitrary CSS tracking and call the font repaired.

**Acceptance test:** after correction, shape all100 digit pairs at default tracking with tnum across the advertised axes, including sampled725/24,725/48,900/18,900/24,900/48,900/128 and nearby interpolation positions. Require absence of positive filled-outline intersections above a documented numerical tolerance, equal digit advances for tnum, and visible separation in actual target rendering at18/24/48/100px and DPR1/2. Verify default/pnum did not regress. Human recognition of totals and identifiers remains a separate test.

**Important scope correction:** initial type proofs used Pillow BASIC; libraqm is unavailable in this environment. Thus they demonstrate default unshaped font raster, not tnum/GSUB/GPOS correctness. My initial report already described the bounded specimen method, but this newly established limitation must accompany any combined verdict. The original 'no release-blocking core letterform defect established' is not a claim that tnum was tested or sound.

## P2: distinguish release versions before public distribution

I independently read current and control metadata. Both have head.fontRevision0.001007080078125, nameID5`Version 0.0.1`, nameID3`0.900;TBNA;TabunaSans-Regular`, and identical family/style/full/PostScript names. Their SHA values differ:

- Current: `5888eecc912f46f14b7807906d2ffc0a42d543a3695465b76a83b699373344b9`.
- Control0.0.1: `18f597e3a48133227d503eff9a297c9b9e62c646dd5cf7902dd8ed216369cf28`.

**Opinion:** yes, fix release-version identity before distributing this changed build as a distinct release. Different public builds with the same displayed version/unique identifier undermine bug reproduction, installed-font identification and update/cache diagnosis. This is release hygiene, not proof that the glyphs fail to render. Internal iterative builds can remain on the same provisional version if their hashes are recorded and they are not represented as distinguishable public releases.

Do not infer that all name IDs must change. Stable family/style and ordinarily PostScript names can be appropriate for an upgrade; avoid accidentally making another installed family. Update the chosen release-version fields and unique build identification consistently, document the version policy, and publish/check hashes. Check that installed current/control can be distinguished using the intended upgrade workflow. The difference between nameID3's0.900 prefix and nameID5's0.0.1 deserves a deliberate policy decision; this reviewer does not claim those strings violate a particular standard.

## Evidence integrity

- Engineering collision data: `/Users/tabuna/math-design/tabuna-fonts/build/independent-audit-20260915/engineering/digit-collisions.json`, SHA256`48c40136dfc83356d69170708250411f1451af86e6d3f2edd7983643f8fcb92c`.
- Visual proof: `/Users/tabuna/math-design/tabuna-fonts/build/independent-audit-20260915/engineering/digit-proof.png`, SHA256`6dae99e6ecb6d9a88e916264f6763fe7b646d84bef1ae8f6a9b1d4e10abf8d50`.
- Method inspected: `/Users/tabuna/math-design/tabuna-fonts/build/independent-audit-20260915/engineering/digit_collisions.py` and `/Users/tabuna/math-design/tabuna-fonts/build/independent-audit-20260915/engineering/render_digits.py`.

No source or font was modified. I inspected the method and visible evidence and independently verified shaping/metadata examples; I did not independently reimplement the entire4800-case path-intersection scan or validate CoreText/DirectWrite.
