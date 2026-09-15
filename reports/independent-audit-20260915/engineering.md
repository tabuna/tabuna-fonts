# Independent engineering audit — 2026-09-15

TTF SHA-256: `5888eecc912f46f14b7807906d2ffc0a42d543a3695465b76a83b699373344b9`
WOFF2 SHA-256: `9c5c23886f3cac3acca41e9db66bdde9a69e5145453e1a84e24605bc31b43e59`

Direct inspection and new HarfBuzz/fontTools/pathops/FreeType probes; no previous pass report or design verdict used as proof. Font and generator not changed.

## P1 · ENG-01 · Tabular digits collide at heavy optical instances despite equal advances

**font defect · confidence high**

217 filled-outline intersections among 4800 digit-pair/location cases with tnum; identical pnum grid has zero. At wght900/opsz128, 00 advances1162 each and filled intersection area39403.88 units². At900/24,00 area20571.62. First sampled lower case725/24,44 area601.87. 900/18 has8 collisions, some below a pixel at UI raster sizes. Rendering confirms strongly fused 900/128 numbers; all tnum advances nevertheless pass equality.

Affected: Heavy counters, large totals, numeric headings, tabular prices; wght725 at sampled opsz24+ and wght900 at sampled opsz18+. Not a claim that every weight/size or every pair fails.

Recommendation: Recompute tnum phantom-point advances and component placement from final digit outlines at every master; preserve sufficient digit-pair ink clearance through interpolation. Do not mask in CSS tracking. Until repaired avoid heavy tabular instances; use tested lower weights or proportional figures where alignment is unnecessary.

Acceptance: Assert equal tnum advances AND zero filled-outline intersections for all100 digit pairs at masters and intermediate wght/opsz, including725/24,900/18,900/24,900/128. Raster-test minimum gap and numeric strings in target browser engines at18/24/32/48px with auto opsz; check decimals, separators and signs.

## P2 · ENG-02 · Web cache URLs still identify the tagged control, not current WOFF2

**release/integration defect · confidence high**

dist/tabuna.css line3 and index.html lines8–9 use59b13381af3b, also present in v0.0.1 CSS. Current WOFF2 hash prefix is9c5c23886f3c. scripts/build-web.sh defines URL suffix as WOFF2 SHA256[:12], but docs main build runs scripts/build.py.

Affected: Returning browser users/deployments reusing cached control at unchanged URL. Actual stale delivery depends on HTTP cache policy; not asserted observed.

Recommendation: Make one documented build command produce synchronized TTF/WOFF2/CSS/preload and check cache token in release validation.

Acceptance: Assert CSS font URL and HTML preload token equal actual WOFF2 SHA prefix; simulate old cached asset and deploy new build, confirming new bytes load.

## P2 · ENG-03 · Changed font is indistinguishable from control0.0.1 in installation metadata

**release metadata defect · confidence high**

Current TTF5888eecc912f46f14b7807906d2ffc0a42d543a3695465b76a83b699373344b9 differs from local v0.0.1-tag TTF18f597e3a48133227d503eff9a297c9b9e62c646dd5cf7902dd8ed216369cf28. Name IDs1,2,3,4,5,6,16,17 and head.fontRevision are identical. Both name5 Version0.0.1; name3 0.900;TBNA;TabunaSans-Regular; manifest0.0.1.

Affected: Desktop replacement, font menus/caches, user bug reports and reproducibility. Same-family replacement is expected, but version and unique ID cannot identify build.

Recommendation: Assign a coherent new version and unique build identity before distributing; synchronize name3/name5/head/manifest and publish immutable hashes.

Acceptance: Current release differs from control by version/unique ID as well as bytes; clean install/update smoke test in supported native app.

Comparison uses local git tagv0.0.1 (commit1dd23282...), not independently downloaded remote release-asset bytes.

## P2 · ENG-04 · 189-character EN/RU subset needs explicit fallback policy for real content

**product integration scope / documented coverage limit · confidence high**

Missing José/Müller accents, Ukrainian їєіґ, Belarusianў, combining acute, bullet•, nonbreaking hyphen, arrows and√≈∑∫. Russian за́мок produces.notdef for acute in direct HarfBuzz. Decomposed Й/Ё compose successfully in HarfBuzz even though marks absent in cmap; U+202F/U+2009 are synthesized spaces by HarfBuzz.

Affected: Names, user input, pasted editorial text, educational stress marks and math text. Existing README correctly discloses limited Latin/Cyrillic; this is not evidence that promised189 glyphs are missing.

Recommendation: Keep current font scoped to controlled EN/RU content; test fallback for user text and editorial symbols or expand repertoire according to product needs. Provide italic policy because only upright exists.

Acceptance: Browser/native corpus with accented names, decomposed Russian, acute stress, bullets, thin spaces, hyphens and math shows no tofu, broken cluster positioning, baseline discontinuity or clipping. Validate intended emphasis with synthetic italic disabled/enabled per product policy.

## Independent positive checks

{
  "cmap": 189,
  "axes": "wght100–900 default400;opsz9–128 default14",
  "ttf_vs_decoded_woff2_shaping_comparisons": 1680,
  "ttf_vs_decoded_woff2_mismatches": 0,
  "locations": 48,
  "tnum_equal_advance_locations": 48,
  "pnum_digit_collision_cases": 0,
  "mapped_glyphs_outside_default_hhea_in_sampled_locations": 0,
  "features": "kern changes Latin/Cyrillic probe; liga produces ffi/ffl/ff/fi/fl glyphs; calt present; pnum/tnum toggles working. Feature presence/equality not typographic-quality proof."
}

## Suitability

- **ui**: Conditional for controlled EN/RU labels with regular/moderate weights; block unrestricted heavy tnum deployment until ENG-01 fixed. Test actual browser/native fallback and auto sizing.
- **headings**: Conditional, with strongest reservation for heavy numeric headings; proportional pair sample has no collisions. No aesthetic verdict inferred.
- **body**: Technically usable for constrained EN/RU upright text with tested fallback/emphasis and paragraph settings; engineering tests do not establish comfortable reading.
- **long_screen_reading**: Not approved by this engineering audit: no sustained reader test, cross-engine long-form proof or fallback/emphasis validation. This is missing evidence, not a measured failure of reading comprehension.

## Limits

- No clean rebuild or installation performed; would mutate font deliverables.
- No browser auto-opsz mapping, WebKit/Chromium rendering, or Windows native rendering independently executed here. Repro includes auto18/24/32/48px rows for follow-up.
- Raster proof is HarfBuzz positioned glyphs rendered by FreeType; not a browser screenshot.
- No Apple involvement, human readability study or accessibility certification claimed.

## Reproduction

```sh
.venv/bin/python build/independent-audit-20260915/engineering/check.py
.venv/bin/python build/independent-audit-20260915/engineering/digit_collisions.py
.venv/bin/python build/independent-audit-20260915/engineering/digit_collisions.py pnum
.venv/bin/python build/independent-audit-20260915/engineering/render_digits.py
```

Serve repository root; open /build/independent-audit-20260915/engineering/repro.html

Evidence JSON, collision lists, reproducible scripts, HTML and raster proof are under `build/independent-audit-20260915/engineering/`. The tracked report deliberately does not embed the large raw run arrays.
