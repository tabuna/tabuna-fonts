# Independent Apple HIG / accessibility perspective — 0.0.3

Existing web demo viewed from Safari/macOS/iOS accessibility principles; no native Apple app supplied. Source inspection only.

Analytical review, not Apple employee review, certification, or human study.

WOFF2 SHA-256: `090801dbfa6086e63678a38df35c522f3032164b2e4bced9e692121bccef704e`

First review was independent: no earlier reports/matrices or other-agent conclusions read; source/font files unchanged.

## Verdicts

- **ui: conditional** — Suitable to continue limited 16px/500 interface trials. Actual checkbox/button sample uses Tabuna, but system-font page chrome does not validate broader UI deployment; adaptive native integration and runtime assistive-technology testing remain unverified.
- **headings: conditional** — Hierarchy and moderate default weights are reasonable. Large headline use remains provisional pending large-text reflow and rendered glyph/spacing review; hero nowrap is a concrete adaptation risk.
- **body: conditional** — 1rem/400 static paragraphs and 18px/400 body preset with 1.6–1.65 leading provide a reasonable starting setup; source settings alone do not establish font legibility.
- **sustained_reading: not_established** — Only two short demonstration paragraphs; no long-form task, controlled reader evidence, low-vision evaluation, or fatigue measure. Cannot approve sustained reading from HIG-oriented source inspection.

## Evidence

- **font-identity** (SHA-256 and dist/manifest.json read): Manifest version 0.0.3; axes wght 100–900 and opsz 9–128; 189 characters. No binary shaping assertion made.
- **actual-font-scope** (index.html + dist/tabuna.css + demo.css): Page chrome is system-ui; custom .tabuna used on hero, article, explicit UI sample, figures/table and weight specimens. Scoped buttons inherit custom font. This demonstrates a real but narrow UI sample.
- **role-defaults** (demo.js update() and sample-role handler): UI preset 16px/500, body 18px/400, display 64px/400; auto optical sizing enabled. UI line-height 1.45; body 1.6. Static article 1rem/400, line-height 1.65; UI 1rem/1.45 with button weight500.
- **heading-defaults** (demo.css): Hero weight450, line-height1.02, negative tracking and nowrap. Article heading weight500, clamp(2rem,3.4vw,3.5rem), line-height1.08; two intentional lines via br.
- **adaptation** (demo.css and index.html): Viewport permits zoom; rem-based static article/UI; 620px reading columns collapse; navigation wraps; focus-visible outline, labeled native controls, status regions, light/dark palettes, contrast/forced-colors handling. Specimen JavaScript writes absolute px sizes.
- **hig-reference** (Read apple-hig SKILL.md, review-workflow.md, relevant foundations and page-index entries; open official Typography/Accessibility/Layout URLs): Official pages resolved but web extraction returned JavaScript-required shells. General guidance routed by installed snapshot; no exact platform size requirements asserted.

## Findings

### HIG-003-01 — medium

Specimen update() assigns target.style.fontSize = size + px. Raising browser default font size changes rem-based article/UI but leaves preset 16/18/64px specimen sizes fixed, absent page zoom or manual slider adjustment.

**Impact:** The role specimen and production-like article respond differently to user text preferences; optical sizing auto does not itself implement text scaling.

**Recommendation:** Keep a documented distinction between exact-pixel proof mode and scalable content mode; implement role samples with relative text scaling. For native iOS integration scale custom fonts through platform text styles/Dynamic Type.

**Acceptance test:** At default browser font sizes 16px and 32px, verify scalable UI/body text increases and all labels/status/control text remains readable without overlap; separately test Safari page zoom. Native adoption must test all supported Dynamic Type sizes.

Evidence: demo.js update(), demo.css .article-sample and .ui-sample, https://developer.apple.com/design/human-interface-guidelines/typography, https://developer.apple.com/design/human-interface-guidelines/accessibility

### HIG-003-02 — medium

Hero h1 uses white-space:nowrap with a mobile minimum font-size of 2.8rem; headline cannot wrap as user text size grows.

**Impact:** Potential horizontal overflow at narrow widths and enlarged root text; source risk, not a reproduced runtime failure.

**Recommendation:** Allow an accessible wrap strategy or revise responsive headline sizing based on available width while preserving text enlargement.

**Acceptance test:** At widths320/375/768px and enlarged text or 200% zoom, verify full Tabuna Sans title remains available without clipping or page-level horizontal scrolling. Record screenshots and scrollWidth/clientWidth.

Evidence: demo.css .hero h1 and max-width620px, https://developer.apple.com/design/human-interface-guidelines/layout, https://developer.apple.com/design/human-interface-guidelines/typography

### HIG-003-03 — medium

The demo presents an interface font and a 16–18px body starting recommendation, but supplies only a short article and one checkbox/button task.

**Impact:** These samples support experimentation, not a claim of broad Apple UI readiness or sustained-reading suitability.

**Recommendation:** Keep the visible in-development qualifier and describe target use as provisional; add long-form Russian/English reading and realistic dense UI validation before stronger claims.

**Acceptance test:** Document tested device/browser, exact font hash, text-size/weight/opsz, scaling, low-vision/VoiceOver observations, and reader outcomes for long-form passages; do not equate HIG review with certification.

Evidence: index.html hero-note, caption, reading section, https://developer.apple.com/design/human-interface-guidelines/typography, https://developer.apple.com/design/human-interface-guidelines/accessibility

## Limitations

- No browser rendering, visual glyph evaluation, VoiceOver, keyboard traversal, zoom execution, native Dynamic Type test, or human readability study was performed in this bounded review.
- No previous reports, matrices, research evaluations, or other agents’ results were read.
- Official HIG live content was not extractable; general principles come from installed skill snapshot dated 2026-08-03.
- FontTools was unavailable in default python3; no outline-width measurement was used as evidence.
- Conditional verdicts concern the evidence and demo integration; they neither certify nor reject intrinsic glyph quality.
