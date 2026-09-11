# Pixel optimization log

All scores use the project's CoreText renderer, shared origin, grayscale antialiasing, and isolated glyph comparison.

| glyph | change | size | IoU |
|---|---|---:|---:|
| к | diagonal controls `0.84/0.84 → 0.80/0.80` | 32/64/128 | 0.628975 mean |
| Л | upper slant point `0.29 → 0.33` | 32 | 0.679621 |
| Л | upper slant point `0.29 → 0.33` | 64 | 0.677519 |
| Л | upper slant point `0.29 → 0.33` | 128 | 0.677377 |
| Д | indirect result from the `Л` contour change | 64 | 0.778279 |
| э | middle bar reach `0.72 → 0.80` | 64 | 0.692158 |
| Э | independent middle bar reach `0.72 → 0.84` | 64 | 0.671947 |
| з | scale and vertical transform sweeps | 64 | 0.643550 (unchanged) |
| 5 | top bar start sweep | 64 | 0.644059 (best) |

The next contour that needs a native construction is `з`: scaling Latin `3` no longer produces measurable gains.

Latest accepted refinements:

- `Д/Л`: lower slant foot point `0.09 → 0.13`; mean IoU at 64 px improved to `0.733996`, with stable results at 32/64/128 px.
- `Э`: independent uppercase bar reach `0.80 → 0.84`; IoU at 64 px improved to `0.671947`.
- Native `з` prototype was rejected (`0.577747` vs `0.643550`) and removed.

Cross-size stability check for separated `Э/э` (32/64/128 px): `Э` = `0.669843 / 0.671947 / 0.670564`; `э` = `0.699226 / 0.698119 / 0.699906`.

Control set after latest accepted changes: 64 Cyrillic glyphs at 64 px, 10 exact matches, mean inkIoU `0.873280`.

- `У`: central junction `0.54 → 0.48`; IoU improved from `0.490101` to `0.534900` at 64 px. Cross-size check: `0.537815 / 0.534900 / 0.534958` at 32/64/128 px.

- `К`: upper diagonal start `0.65 → 0.50`; IoU at 64 px improved to `0.528862`.

- `К`: lower diagonal inset `0.35 → 0.45` after upper start `0.50`; IoU at 64 px `0.539520`.

Control set after `У` and `К`: mean inkIoU `0.874384` across 32/64/128 px (per-size `0.874024 / 0.874326 / 0.874801`).

- `У`: lower bowl control `0.32 → 0.40` after junction `0.48`; IoU at 64 px improved to `0.672646`.

Control set after `У`: mean inkIoU `0.876533` across 32/64/128 px (per-size `0.876171 / 0.876478 / 0.876951`).

- `К`: upper diagonal inset `0.38 → 0.46` with prior controls; IoU at 64 px improved to `0.549687`.

Control set after `К` diagonal refinements: mean inkIoU `0.876695` across 32/64/128 px (per-size `0.876337 / 0.876637 / 0.877112`).

Cross-size check for `К` after both shoulder refinements: IoU `0.550761 / 0.549687 / 0.549557` at 32/64/128 px.

- `К`: upper diagonal inset extended `0.46 → 0.58`; IoU at 64 px improved to `0.565409`.

- `К`: upper diagonal inset extended `0.58 → 0.74`; IoU at 64 px improved to `0.585816`.

- `К`: upper diagonal inset extended `0.74 → 0.90`; IoU at 64 px improved to `0.605241`.

- `К`: upper diagonal inset extended `0.90 → 1.02`; IoU at 64 px improved to `0.618180`.

- `К`: upper diagonal inset `1.02 → 1.26`; IoU at 64 px improved to `0.634112`.

- `К`: fine sweep `1.26–1.38`; best inset `1.30`, IoU `0.634123` at 64 px.

Control set after final `К` sweep: mean inkIoU `0.878016` across 32/64/128 px (per-size `0.877663 / 0.877956 / 0.878430`).
- `5`: raised the lower bowl's left join from `1.06s` to `1.36s`, matching the system raster's straighter shoulder transition; 64 px IoU improved `0.644059 → 0.662987`.
- Full 126-glyph audit after `5` correction: mean IoU `0.887189` across 32/64/128 px; `5` improved to `0.662987` at 64 px without changing exact-match count.
- `4`: shifted the upright from `70%` to `72%` of advance width; 64 px IoU improved `0.684464 → 0.728389`.
- `У`: lowered the upper-arm junction from `0.36H` to `0.28H`; 64 px IoU improved `0.672646 → 0.695481`.
- `Э`: corrected the mirrored middle bar from left-anchored `(0,.84w)` to right-facing `(.28w,w)`, matching the system construction; 64 px IoU improved `0.671947 → 0.722576`.
- `Ю`: moved the oval's left edge from `0.30w` to `0.26w`, aligning its join with the stem; 64 px IoU improved `0.714606 → 0.834060`.
- `я`: extended the mirrored lowercase `R` vertically by `4%` around its baseline (`yy=1.04`, `dy=-0.04h`); 64 px IoU improved `0.677692 → 0.715687`.
- `к`: rebuilt the native Cyrillic join from the threshold `0.75` contour, then accepted six one-point moves (`lower_join_y`, `lower_tip_inset`, `upper_join_y`, `upper_join_x`, `upper_thick`, `upper_tip_inset`); 64 px IoU improved `0.628640 → 0.788888`, with FP/FN at threshold `0.75` improving from `164/431` to `50/249`.
- Full 126-glyph audit after the `к` reconstruction: mean IoU `0.891195` across 32/64/128 px (per-size `0.890679 / 0.891161 / 0.891745`).
- `К`: replaced the Latin-derived form with an independent Cyrillic contour, selected from the threshold `0.25` reconstruction and seven accepted point moves; 64 px IoU improved `0.634123 → 0.752930`.
- Full 126-glyph audit after the `К` reconstruction: mean IoU `0.892140` across 32/64/128 px (per-size `0.891630 / 0.892104 / 0.892685`).
- `з`: independent stroke-based reconstruction was rejected. It produced `0.571588` at best against the previous digit-derived control `0.643550`; all three threshold candidates (`0.25 / 0.50 / 0.75`) stayed below control, so the production contour remains unchanged. The error map shows the next attempt needs closed bowl-outline reconstruction rather than two centre-line strokes.
- `з`: isolated FN patching showed only the lower-left bowl segment improved the production contour; top-left, right-waist, and combined patches were rejected. The accepted lower-left segment improved 64 px IoU `0.643550 → 0.654801`.
- Full 126-glyph audit after the `з` lower-left segment: mean IoU `0.892229` across 32/64/128 px (per-size `0.891725 / 0.892193 / 0.892768`).
- `З`: isolated FN patching showed only the right waist segment improved the production contour; top, bottom, and combined top/bottom patches were rejected. The accepted waist segment improved 64 px IoU `0.703430 → 0.722331`.
- Full 126-glyph audit after the `З` waist segment: mean IoU `0.892387` across 32/64/128 px (per-size `0.891896 / 0.892343 / 0.892923`).
- `3`: isolated top, bottom, waist, and top+bottom FN patches were rejected. Top and bottom created too much FP (`0.665602` and `0.653625` vs control `0.684290`), while waist was neutral. The next attempt needs curvature changes in the original bowls rather than additive patches.
- `Я`: isolated FN patching showed only the central join segment improved the mirrored `R` construction; leg, bowl, and leg+bowl/leg+join patches were rejected. The accepted join segment improved 64 px IoU `0.702488 → 0.736946`.
- Full 126-glyph audit after the `Я` join segment: mean IoU `0.892660` across 32/64/128 px (per-size `0.892169 / 0.892617 / 0.893195`).
- `5`: isolated lower-bowl, shoulder, topbar, and lower+shoulder patches were rejected. The topbar patch was nearly neutral (`0.662821` vs control `0.662987`), while lower and shoulder patches added too much FP. The next attempt needs curvature changes to the lower bowl rather than additive patches.
- `5`: after inspecting Inter's Glyphs-package workflow, switched from additive patches to existing cubic-node/handle moves. The accepted curve reconstruction moved the shoulder, right side, lower bowl, left terminal, and return point of the existing contour; 64 px IoU improved `0.662987 → 0.725204`, hard-mask FP/FN improved `428/489 → 331/384`, and boundary distance improved `1.901323 → 1.460629`.
- Full 126-glyph audit after the `5` curve reconstruction: mean IoU `0.893158` across 32/64/128 px (per-size `0.892674 / 0.893110 / 0.893691`).
- Added highlight-driven error analysis (`scripts/analyze-highlight-errors.py`) to classify red/green overlays by shift, bbox/scale, stroke thickness, large FN/FP components, and boundary-only error. This replaces blind one-glyph sweeps with prioritized repair classes.
- `3`: promoted the highlight-confirmed curve reconstruction for the lower bowl and left waist; 64 px IoU improved `0.684290 → 0.716332`. Because `з/З` are still partially digit-derived, the same contour change also improved `з` `0.654801 → 0.657520` and `З` `0.722331 → 0.739157`.
- Full 126-glyph audit after the `3` reconstruction: mean IoU `0.893550` across 32/64/128 px (per-size `0.893055 / 0.893520 / 0.894076`).
- Highlight shift batch: applied whole-contour registration fixes from the analysis to `j` (left 2 px), `4` (up 2 px), and `7` (left 2 px). Their 64 px IoU became `0.814117`, `0.808030`, and `0.799904` respectively, with unchanged advances.
- Full 126-glyph audit after the shift batch: mean IoU `0.895711` across 32/64/128 px (per-size `0.895221 / 0.895685 / 0.896228`).
- Second highlight shift batch: applied the next high-confidence whole-contour shifts to `з` (right 1 px), `K/k` (down 2 px), and `У` (right 1 px). Their 64 px IoU became `0.682126`, `0.766412 / 0.839477`, and `0.733337` respectively, with unchanged advances.
- Full 126-glyph audit after the second shift batch: mean IoU `0.897215` across 32/64/128 px (per-size `0.896733 / 0.897188 / 0.897725`). The updated highlight atlas now ranks true contour reconstruction problems above simple registration errors.

- `з`: replaced the digit-derived contour and patch with an independent, ordered-raster cubic reconstruction. Three construction thresholds were evaluated using one fixed scoring threshold (0.5): `0.25 → 0.931580`, `0.50 → 0.971760`, `0.75 → 0.916925`, against `0.682126` control. Selected 0.5; initial pilot took about 3 seconds, without full font rebuilds.
- `з`: fitted compatible text/display drawings at weights 100/400/900 with a shared error-directed split tree (37 cubic segments). Accepted variable font at 64 pt/2×/400: `0.682126 → 0.980483`; FP `82 → 18`; FN `429 → 14`; largest FN `216 → 3`; bbox matches; symmetric contour distance `1.494357 → 0.117122` pixels. All 25 tested size/weight combinations improved, including intermediate weights 250 and 700. No other glyph geometry or variation data changed; advances are unchanged.
- Corrected reference contour export: the previous 32–35 points were sampled in row-major order, not contour order, and did not separate inner boundaries. Export now includes ordered isocontours, nested inner/outer paths, masks at three thresholds, and error-directed candidate landmarks. Highlight atlas now crops actual glyph bounds and uses red FN / blue FP / grey intersection.
- Full 126-glyph audit after independent `з`: mean IoU `0.899557` across 32/64/128 pt at 2× (per-size `0.899022 / 0.899556 / 0.900093`). Detailed results and limits: `ZE-RECONSTRUCTION-REPORT.md`. Stopped local fitting because Regular's remaining differences are boundary-only; the overall font objective is still incomplete.

- `З`: independent ordered-raster reconstruction, thresholds 0.25/0.5/0.75 measured separately; selected 0.5. Compatible six-master construction (33 cubic segments) improved 64 pt/2×/400 Ink IoU `0.739157 → 0.981768`, FP `134 → 14`, FN `491 → 24`, largest FN `207 → 2`. All 25 tested axis combinations improve. Overall mean after З alone: `0.901447`.
- `3`: independent reconstruction with its own 38 cubic segments and fixed threshold 0.5. Accepted variable result at 64 pt/2×/400: `0.716332 → 0.984307`, FP `209 → 16`, FN `483 → 25`, largest FN `301 → 3`. All 25 main axis combinations and an additional 175/16 holdout improve. Three one-handle corrections for a reported interpolation kink at point 84 were rejected because they reduced IoU; stopped searching. The remaining kink warning is documented with manual review points.
- Preserved `³/¾`: both inherit the ordinary three in the original font. One superscript holdout regressed after changing 3, so their old source drawing is retained in a private `three.small` component, appended without changing public glyph IDs. Their expanded geometry is unchanged on 25 axis combinations and 12 native raster pairs are pixel-identical. Tabular three follows the new ordinary three with unchanged tabular advances.
- Full 126-glyph audit after З and 3: mean Ink IoU `0.903532` (32/64/128 pt: `0.902875 / 0.903608 / 0.904113`). All prior advances and unrelated baseline glyph geometry/variations are preserved. Details and open interpolation limitation: `BOWL-RECONSTRUCTION-REPORT.md`.
