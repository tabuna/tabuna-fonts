# Independent release review

Current binaries, public README, CSS, web build and tag v0.0.1; no other independent findings read, no rebuild, no browser cache reproduction.

Current TTF SHA256: `5888eecc912f46f14b7807906d2ffc0a42d543a3695465b76a83b699373344b9`

Current WOFF2 SHA256: `9c5c23886f3cac3acca41e9db66bdde9a69e5145453e1a84e24605bc31b43e59`

## REL-01 — Checked-in font URL still identifies the old tagged WOFF2

P2; confidence high; release packaging / web deployment.

- dist/tabuna.css:3 and index.html:8 still use ?v=59b13381af3b, exactly the v0.0.1 WOFF2 hash prefix.
- Current WOFF2 SHA256 begins 9c5c23886f3c, while the URL remains unchanged.
- docs/BUILDING.md:9 recommends scripts/build.py, which replaces dist binaries without refreshing CSS or preload URLs.

Deploying the current tree over the old demo can keep serving a cached old font to returning clients under ordinary cacheable hosting. Font design changes may appear absent or differ across clients; this is not an outline-quality defect. Actual headers and cache outcomes were not measured.

Acceptance: Make the documented web build refresh all font asset references and assert their hash matches the emitted WOFF2 before packaging. Verify an old-cache-to-new-release browser deployment.

## REL-02 — Web wrapper does not invalidate the stylesheet URL

P2; confidence high; release packaging / web deployment.

- scripts/build-web.sh:19 rewrites WOFF2 URL inside dist/tabuna.css.
- scripts/build-web.sh:24 only rewrites TabunaSansVariable.woff2 references in index.html.
- index.html:9 uses dist/tabuna.css?v=59b13381af3b; this URL is never refreshed by that wrapper.

Even after running build-web.sh, returning browsers can reuse the old CSS (and its old font URL) while the preload fetches the new font, causing old rendering and possibly an unused extra font download. This persists independently of the presently stale WOFF2 URL.

Acceptance: Update a stylesheet content hash/version after writing CSS, and verify both fresh and cached stylesheet paths select the intended font hash.

## REL-03 — Changed binaries retain the tagged release version and stale unique ID

P2; confidence high; release identification; relevant before shipping a new release.

- Current TTF SHA256 5888eecc912f46f14b7807906d2ffc0a42d543a3695465b76a83b699373344b9 differs from tag TTF 18f597e3a48133227d503eff9a297c9b9e62c646dd5cf7902dd8ed216369cf28.
- Both actual name tables report ID5 Version 0.0.1, ID3 0.900;TBNA;TabunaSans-Regular, ID6 TabunaSans-Regular; head.fontRevision is 0.001007080078125.
- scripts/build.py:111,128-129 and dist/manifest.json still identify 0.0.1; current README download links point to working-branch dist while the baseline link points to v0.0.1.
- Changed tables: head, hmtx, loca, glyf, gvar

Version labels cannot distinguish installed/current binaries from the fixed baseline. The unique identifier contains a different legacy version. This is normal only if the working tree is explicitly unreleased; do not package these changed bytes as an equivalent 0.0.1 release. Identical PostScript names alone are normal across upgrades.

Acceptance: Before publishing, assign a new release/prerelease identity consistently to manifest, name version and unique identifier, and head revision; publish checksums tied to that identity and preserve v0.0.1 immutable assets.

## UI suitability and scope

Verified current cmap has 189 entries, axes wght 100/400/900 and opsz 9/14/128, and WOFF2 is 93164 bytes (about 91 KiB); README numeric claims match.

The compact cmap excludes U+0301/U+0306 combining marks, U+2022 bullet, U+2192 arrow, U+2713 check, U+202F narrow NBSP, U+2009 thin space and U+00E9. CSS system fallback is expected for unsupported characters; accent shaping may also normalize supported decompositions. These facts constrain whole-UI typography but are not a coverage bug given the explicit 189-character scope.

README documents missing expanded scripts and no italic; default CSS font synthesis and platform fallback can change appearance for out-of-scope UI text. No cross-platform fallback rendering or small-text quality assessment performed.

## Reproducibility limits

requirements.lock pins dependency versions and build.py:573 fixes SOURCE_DATE_EPOCH. These are useful controls but not a completed independent reproducibility proof; no full rebuild was run.

This review does not establish universal UI-font suitability, visual originality, or Apple-platform equivalence.
