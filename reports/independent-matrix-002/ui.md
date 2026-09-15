# Independent product UI review — matrix 002

TTF SHA-256: `3567058955eb20ebaf25ef5241a094b25d86dfd7be966f8032492dd3caa3e011`. Read-only review of current demo/font; prior reports were not read.

- **ui — conditional**: Readable actual 16px UI label/button and 13px status at inspected desktop size; broader form/dialog and enlargement coverage missing.
- **headings — pass**: Current desktop hero and two-line Russian article heading show clean hierarchy and no clipping; pass limited to inspected size/weights.
- **body — conditional**: Current 16px/1.65 w400 Russian paragraphs visually readable; English paragraphs and longer text not exercised.
- **sustained_reading — unverified**: Brief visual inspection is not prolonged reading or human research; existing specimen is too short.

## Evidence

**source-scope** — Read current index.html, demo.css, demo.js, dist/tabuna.css without reports. Actual Tabuna classes on heading, intro, editable sample, article, UI demo and table; outer labels/navigation use system-ui.

**browser-desktop** — Isolated localhost tab, 1280x720 screenshot; no shared viewport changes. Hero and article hierarchy clear, 16px Russian body and checkbox/button visually legible without clipping. Save action changed the live status text.

**font-loaded** — HTTP server log, rendered status and computed styles. WOFF2 d07839f04ebdbfb89fed1c4f9d5d2609197db1071251bd5cf8ab0db5f626b207 returned HTTP 200; page says Tabuna Sans loaded. Target computed families select Tabuna Sans. Read-only browser document.fonts enumeration returned empty, so this is not per-glyph renderer identification.

**sizing** — Computed CSS and source. Hero 149.76/152.755px w450; article heading 43.52/47.002px w500; body 16/26.4px w400; UI label 16/23.2px w400; button 16/23.2px w500; status 13/18.85px w400. Body preset is 18px w400/1.6, UI preset 16px w500/1.45.

**enlargement** — Source inspection only. Rem-based body/UI typography and responsive grids present. Hero nowrap/clamp and fixed-pixel interactive sample require actual 200%/400% checks; no such visual validation performed.

## Findings

**UI-01 / P2 / demo_coverage_limitation**

Condition: Approving UI use beyond the current checkbox/save sample. Evidence: Demo has one 16px checkbox label, one 16px medium button, one 13px status; the main controls and labels are system-ui. No dialog, input placeholder, error state or dense navigation in Tabuna. Recommendation: Add a scoped Tabuna form and dialog sample with long Russian labels, help/error text and 12–14px dense controls. Acceptance: Verify actual font on each field/button; inspect 12/13/14/16px, weights 400/500/600, long labels, disabled/error states and 200%/400% enlargement without clipping.

**UI-02 / P2 / demo_coverage_limitation**

Condition: Claiming sustained reading suitability. Evidence: Only two short Russian paragraphs in the article, with default 16px/1.65; no extended bilingual prose, semantic emphasis or long reading exercise. Recommendation: Add several screenfuls of English and Russian prose at 16–18px with realistic headings, lists and emphasized spans. Acceptance: Render at intended widths and sizes, inspect paragraph rhythm and line endings; obtain actual reading feedback before any fatigue/comprehension claim.

**UI-03 / P2 / validation_gap**

Condition: Shipping responsive/enlarged heading and form layouts. Evidence: Hero has white-space:nowrap and viewport/rem clamp; editable sample receives inline px sizes; source breakpoint rules alone do not prove enlarged reflow. Recommendation: Run isolated 320px and 200%/400% zoom or text-enlargement validation. Attribute any container overflow to layout first. Acceptance: All essential labels/buttons reachable, no clipped accent/descender, heading readable and no page-level horizontal scrolling at the tested enlargement settings.

## Limitations

- Initial bounded independent review; no prior/current audit reports read.
- No human participants, reading-speed, comprehension or fatigue measurements.
- No pixel-level per-glyph font tracing; WOFF2 successful load and scoped styles corroborate use.
- No small-screen, browser-zoom, dark-mode, Windows rasterization or native dialog rendering validated.
- No confirmed font-outline defect found in this UI review; findings above concern evidence and demo coverage.
- Automatic approval initially rejected broadly bound local server; corrected safer localhost-only bind was approved and used.
