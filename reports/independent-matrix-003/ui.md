# Independent UI integration review — Tabuna Sans 0.0.3

TTF SHA256: `56cb3cbd30099ed97b0395e7eae28f9431e84ff9eede14cdfb4061f1c5873edc`

Fresh agent review; no earlier or current audit/reviewer reports read. Font and product sources remained read-only. Independent headless Chrome contexts; shared browser viewport untouched.

## Actual tests and evidence

- Read applicable ancestor AGENTS.md, index.html, demo.css, demo.js, dist/tabuna.css; verified TTF SHA256.
- Loaded http://localhost:4173 in isolated Chrome at 1280x1000 and 320x1000, plus 320x1000 with root font size 32px (200% text-size simulation).
- Awaited document.fonts.ready; all contexts reported Tabuna Sans loaded. Inspected computed font families, weights, optical sizing, dimensions.
- Body preset, save feedback, system comparison toggle executed successfully in all three contexts.
- Visually inspected desktop and mobile reading-grid screenshots, plus full enlarged screenshot (latter limited by thumbnail scaling).

Evidence: `build/matrix003/ui/check.cjs`, `build/matrix003/ui/evidence.json`, `build/matrix003/ui/desktop-reading.png`, `build/matrix003/ui/mobile-reading.png`, `build/matrix003/ui/mobile-enlarged.png`.

## Verdicts

- **ui**: Conditional pass: legible short controls at 16px/500; enlarged narrow layout fails.
- **headings**: Pass at normal desktop/mobile sizes: clear hierarchy and open forms; enlarged hero fails reflow.
- **body**: Pass for the two supplied short Russian paragraphs at 16px/1.65 and body preset 18px/1.6.
- **sustained_reading**: Not established: supplied article is too short for fatigue or long-form evaluation.
- **tables**: Pass at ordinary tested size: 14.4px figures align, four weight rows remain readable.
- **release**: Suitable for continued prototype use; resolve enlarged narrow layout before treating demo as robust accessible integration.

## Findings

### P1

320px viewport with html font-size 32px produces document scrollWidth 517px; controls extend to x516.9, hero period to x500.5; normal 320px document width is exactly 320px.

Recommendation: Allow hero wrapping; use minmax(0,1fr)/min-width:0 and narrow single-column controls/facts with wrapping labels. Preserve readable text rather than shrinking it.

Acceptance: At 320 CSS px with 200% root text size, document scrollWidth <= clientWidth+1; all labels/actions available without horizontal page scrolling; test normal 320 and desktop for regressions.

### P2

Live body preset remains 18px after root text size grows from 16px to 32px; live sample size is assigned fixed px by JS while surrounding article doubles.

Recommendation: Clarify specimen slider uses absolute px; provide a separate scalable text preview or scale preset defaults with user text settings.

Acceptance: 200% text preference enlarges an explicit reading preview to the expected size without clipping; absolute-size specimen remains accurately labeled.

### P2

Only two short paragraphs represent body reading, and only four rows represent tabular tasks.

Recommendation: Add a dedicated extended reading/real task fixture before claiming sustained-reading readiness; include mixed Russian/English and identifiers at actual UI sizes.

Acceptance: Review several screenfuls of continuous text and dense labels/numeric tables at 14,16,18px, including 200% text, across target rendering platforms.

## Limits

- Agent assessment, not real human user testing and no Apple endorsement.
- No fatigue, comprehension, or reading-speed measurements.
- Chrome/macOS only; no Safari, Windows, Android, or physical device coverage.
- 200% root CSS font size is a text enlargement simulation, not OS Dynamic Type or browser zoom certification.
- Default light mode screenshots; keyboard focus styling inspected in source, full keyboard/screen-reader behavior not tested.
- Browser loaded WOFF2 linked by current demo; supplied TTF hash verified independently, binary equivalence not proven in this review.
