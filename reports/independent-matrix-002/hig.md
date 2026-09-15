# Independent HIG typography and accessibility review

Independent Apple HIG typography/accessibility reviewer; not Apple affiliation or certification.

Current web specimen on desktop, with conditional integration guidance for macOS/iOS/iPadOS. No other Apple platforms assumed.

Initial report independently inspected current source and rendered demo; no previous reports consulted.

## Identity

- `TabunaSansVariable.woff2`: `d07839f04ebdbfb89fed1c4f9d5d2609197db1071251bd5cf8ab0db5f626b207`
- `TabunaSansVariable.ttf`: `3567058955eb20ebaf25ef5241a094b25d86dfd7be966f8032492dd3caa3e011`

## Verdicts

- **ui: conditional** — Real 16px Tabuna UI label/checkbox and 500 button are demonstrated; keyboard action updates status. Target-device small-type rasterization and native larger text/Bold Text integration remain unverified.
- **headings: conditional** — Rendered 43.52px/500 heading is clear and unclipped at the observed desktop viewport. No full size/weight, narrow-window, or text enlargement sweep performed.
- **body: conditional** — 16px/400 article with 1.65 line height and 18px/400 body preset with 1.6 line height provide practical starting settings. Only a short sample and one rendered desktop context were assessed.
- **sustained_reading: unverified** — No human timed reading, comprehension, or fatigue data collected.

## Verified evidence

At 1280×720 the reading section visually showed coherent heading/body/UI hierarchy without clipping or page horizontal overflow. Loaded-font status reported Tabuna Sans; computed families match the custom face. Article: 16px/400, line-height 26.4px. Heading: 43.52px/500. UI: 16px/400, button 500. Body preset: 18px/400, 28.8px line-height, normal tracking, automatic optical sizing. Keyboard Enter on Save updated the status message.

Palette contrast ratios (CSS arithmetic): {"20221f/f8f8f4": 15.06, "62655d/f8f8f4": 5.57, "62655d/efefea": 5.14, "f0f2e9/1c1f1b": 14.73, "b3b9ab/1c1f1b": 8.28, "b3b9ab/282c25": 7.07}. These are palette results, not thin-stroke perceptual guarantees.

## HIG-002-01 — Using this web demo as proof of native Apple UI readiness

Priority: medium.

**Evidence:** Distribution provides CSS @font-face and opt-in .tabuna; no native Dynamic Type or Bold Text integration is demonstrated. Browser UI controls really use Tabuna at 16px/400 and button at 500.

**Recommendation:** Keep UI readiness conditional; for each intended Apple native target map custom fonts to semantic text styles and test larger accessibility sizes and Bold Text.

**Acceptance test:** In a native sample, exercise all supported Dynamic Type categories and Bold Text with Russian/English labels, values, and actions; verify text remains readable and actions reachable without clipping.

**Basis:** Apple guidance requires accessible custom-font integration; missing native sample is an evidence limit, not proof that this font cannot support it. [Apple source](https://developer.apple.com/design/human-interface-guidelines/typography).

## HIG-002-02 — Text-size enlargement or narrow windows in the demo

Priority: medium.

**Evidence:** demo.js update() writes inline pixel sizes to #sample-text; hero h1 has white-space:nowrap; only 1280x720 default size was rendered in this bounded review. Body article itself uses 1rem and unitless 1.65.

**Recommendation:** Validate browser text enlargement separately from specimen size control, including narrow windows; use adaptive wrapping and relative type integration if any clipping occurs.

**Acceptance test:** At 320 CSS px and text enlargement through 200%, all control labels and reading content remain usable without loss; document any intentional horizontal scrolling inside code/specimen only.

**Basis:** Product acceptance test derived from HIG adaptation principles; 320/200% are review test conditions, not claimed Apple numeric mandates. [Apple source](https://developer.apple.com/design/human-interface-guidelines/layout).

## HIG-002-03 — Claiming suitability for sustained reading from this specimen

Priority: medium.

**Evidence:** The reading sample has two short Russian paragraphs at 16px/400 with 26.4px line height; body preset is 18px/400 with 28.8px line height. No timed reader study was performed.

**Recommendation:** Run sustained Russian and English reading sessions across target displays and accessibility needs before claiming comfort, comprehension, or parity with the system font.

**Acceptance test:** Record corpus, duration, device, viewing scale, participant characteristics, comprehension/error measures, and fatigue responses under a predeclared protocol; do not substitute outline metrics for reader results.

**Basis:** Review evidence requirement informed by Apple instruction to test legibility in context; study design is reviewer recommendation. [Apple source](https://developer.apple.com/design/human-interface-guidelines/typography).

## HIG-002-04 — Integrators choose Thin/ExtraLight for small functional text because the full axis is advertised

Priority: polish.

**Evidence:** Weight axis permits 100–900 and the demo offers every weight; UI/body presets appropriately use 500/400 and introductory body guidance recommends 400.

**Recommendation:** Preserve the current regular/medium defaults and add an explicit small-UI caution around thin weights in integration guidance.

**Acceptance test:** Document a recommended 400–600 starting range for small UI, subject to device testing; if lighter weights are used, verify intended size/contrast with readers.

**Basis:** Apple cautions that thin custom-font weights may require larger sizes; 400–600 is a local starting recommendation rather than a HIG rule. [Apple source](https://developer.apple.com/design/human-interface-guidelines/accessibility).

## Limits

- Bounded initial review; no font/source edits.
- Official HIG page direct opens returned JavaScript shells; live official search-index excerpts and bundled HIG routing references supplied contextual guidance.
- No font outline/hinting audit, native application test, VoiceOver session, mobile/zoom or dark-mode screenshot run.
- Browser AX exposure is not equivalent to an assistive-technology user test.
- No claim of human study, HIG certification, or long-reading fitness.
