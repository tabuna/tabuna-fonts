# Independent release review — matrix 002

TTF SHA256: `3567058955eb20ebaf25ef5241a094b25d86dfd7be966f8032492dd3caa3e011`

WOFF2 SHA256: `d07839f04ebdbfb89fed1c4f9d5d2609197db1071251bd5cf8ab0db5f626b207`

Release packaging passes. An isolated source rebuild produced byte-identical TTF and WOFF2 in 20.9 seconds. Both binaries match version 0.0.2, 189 characters, 218 glyphs, advertised axes and manifest sizes. The documented shaping features are present. All nine fingerprint references match; preload and CSS resolve the same font. TTF/WOFF2 outline and advance comparison passes all 5,450 glyph/location cases.

UI, headings and body: **conditional for documented pilot use**, with platform/content validation remaining outside this release-only review. Sustained reading: **unverified**, accurately stated in README. No binary deployment blocker was found.

## Findings

### P2 — Authorial release gate remains closed; pilot distribution is accurately labeled

Evidence: font_recovery.design_status --require authorial returns 1; D01–D06 pending; authorial_deviations_verified=false; technical_failures=[]; audit_failures=[]; docs/BUILDING.md explicitly requires this gate for authorial release; README identifies 0.0.2 as pilot.

Recommendation: Keep pilot wording. Before calling this an accepted authorial release, close the six decisions with current-hash evidence and satisfy the project gate. This is not a finding that the pilot binaries fail to load or render.

Acceptance: .venv/bin/python -m font_recovery.design_status --require authorial exits 0 on the exact shipped TTF.

### P3 — Archive comparison navigation is incomplete in a clean static checkout

Evidence: index.html links comparison.html; comparison.html links REVIEW.md, which does not exist; comparison.js fetches proofs/pixel-${size}/comparison.json; proofs is ignored and git ls-files proofs returns no files; Archive disclaimer and fetch-error handling exist.

Recommendation: Replace the missing review link and either provide an intentional archive landing page without live proof controls or publish the required archive data alongside the page.

Acceptance: Serve only tracked site files; follow the comparison and review links and confirm no broken navigation or unavailable expected comparison data.

## Limits

No previous or current reviewer reports were read for the initial audit. Project gate was executed after independent metadata/cache/source inspection.

Only scratch build/matrix002/release and assigned reports were written; production font sources/binaries untouched.

Rebuild uses the existing pinned local Python dependencies; no clean dependency download or cross-OS build performed.

No browser renderer, participant reading study, full font visual review, remote deployment or push performed.

Legacy scripts/verify-full.py inspected but not run: it still requests out-of-repertoire marks/letters and local references; documented compact verify.py is the relevant repertoire check.

Fresh test artifacts: `build/matrix002/release/inspection.json`, `reproduction.json`, `parity.json`, `design-status.json`, `gate-exit.json`; scratch build log under `repro/build.log`.
