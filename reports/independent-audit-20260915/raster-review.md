# Independent raster/display review #9

Font SHA-256: `5888eecc912f46f14b7807906d2ffc0a42d543a3695465b76a83b699373344b9`

Inspected four accessibility theme/scale PNGs and type/body-native.png; read generators only, no prior audit verdicts. No CoreText, DirectWrite, or browser tests performed.

## Method

- **accessibility:** Pillow ImageFont.truetype on fontTools static instances. 1x uses size pixels; 2x rerasterizes at size*2 and doubles canvas/positions. This is not a screenshot of a device/browser. opsz manually specified, typically CSS px*0.75.
- **type:** Pillow/FreeType variable font with explicitly set [wght,opsz]. body-native is 1x and opsz equals pixel size. 14px-detail-nearest2x is an enlarged 1x crop, not a 2x rasterization.
- **view_limitation:** The image tool downscaled the 2200x2240 2x proofs to 1568x1596 for display; no pixel-level 2x pass is claimed.

## R1 — observed

Scenario: 12px / wght100 / opsz9 / light and dark 1x

Thin row is visibly much fainter than 300–500; delicate stems and diacritics have little visual presence. This is a size/weight usage concern, not evidence of missing outlines.

Acceptance test: Do not extend a body-text approval to 100 weight from these plates. For any intended small thin-text use, inspect native 1:1 target-renderer captures in both themes and verify every stem, dot and breve remains visible at normal viewing size.

## R2 — observed_with_coverage_limit

Scenario: 14/16/18px / wght400 and500 / light 1x body; 14/16/18px /400 / both themes accessibility

The inspected body rows are readable, show a clear 400-to-500 weight change, and exhibit no obvious clipped lines. Ё/ё and Й/й remain visible in the 400 accessibility rows. Dark-theme 500 at 14–18px is absent from those accessibility plates; the static-instance and variable-font plates also use different opsz mappings.

Acceptance test: Capture all 14,16,18px ×400,500 ×light,dark at consistent explicit opsz and actual DPR1/DPR2. Require visible diacritics, open counters, no clipping, and unambiguous weight progression. Include Il1|, ЁёЙй, rn/m, cl/d, ЩЦ, mixed Russian/English body text.

## R3 — coverage_gap

Scenario: Actual CoreText/macOS, DirectWrite/Windows and production browser auto optical sizing

These generated PNGs establish only Pillow/FreeType rendering at chosen axis values. They cannot validate platform antialiasing, browser font selection or automatic opsz behavior.

Acceptance test: Load this exact SHA in a minimal browser specimen with font-optical-sizing:auto and a separate explicit-axis reference; verify the font really loads and compare rendered widths/shapes at 14/16/18px and 400/500. Test Safari/CoreText and Windows Edge/DirectWrite at native DPR1 andDPR2 (record OS, browser, scaling, zoom). Add a native CoreText/DirectWrite text control if native-app support is claimed. Save lossless captures; inspect at 1:1 for missing marks, closed counters, clipping and weight inconsistency, without requiring cross-renderer pixel equality.
