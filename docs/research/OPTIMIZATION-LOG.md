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
- `2`: independent ordered-raster reconstruction from thresholds 0.25/0.5/0.75; selected 0.5. Pilot 64 pt/400 improved `0.688691 → 0.982882`, FP `573 → 6`, FN `264 → 17`, largest FP `391 → 3`. Six compatible masters passed isolated checks at all 25 tested axis combinations. Full 126-glyph mean after `2`: `0.905928` (32/64/128 pt: `0.905260 / 0.906003 / 0.906521`). The control for this measurement was rebuilt with only `2` disabled, retaining accepted `З/3`; no unrelated glyphs changed.
### Highlight audit: digit 5 (2026-09-12)

Changed only `top_return_end_y_h` in the `5` contour (`0.562176 → 0.572176`).
At 64 px the glyph improved from `IoU 0.725204` (`FP 331`, `FN 384`) to
`0.725482` (`FP 332`, `FN 382`). Full-set mean improved from `0.906003` to
`0.906005`; the change was retained and revalidated at 32/64/128 px.
### Highlight audit: digit 5, iteration 2 (2026-09-12)

Changed only `right_end_y_h` (`0.312176 → 0.322176`). At 64 px glyph `5`
improved `0.725482 → 0.726096` (`FP 332`, `FN 381`). Full-set mean improved
`0.906005 → 0.906010`; validated again at 32/64/128 px and retained.
### Highlight audit: digit 5, iteration 3 (2026-09-12)

Changed only `right_end_y_h` (`0.322176 → 0.332176`). Glyph `5` improved at
64 px from `0.726096` to `0.726615` (`FP 332`, `FN 379`). Full-set mean rose
from `0.906010` to `0.906014`; 32/64/128 px validation passed, so retained.

### Highlight audit: `Д`, iteration 1 (2026-09-12)

Baseline was a fresh full 126-glyph audit at 32/64/128 px. The largest connected
error among the lowest-IoU glyphs was the uppercase `Д`: at 64 px its FN area
was 640 px (largest component 260 px, left outer leg) and its FP area was 451 px
(largest component 163 px, lower foot). The reference and render BBoxes matched,
so the diagnosis was a narrow right outer shoulder/leg rather than a global
position or scale error.

Hypothesis: extend only the uppercase `Д` right outer contour toward the reference
side bearing by changing the display regularity coefficient from `0.65` to `0.50`.
The change is isolated with `right_correction = .50 if ch == 'Д' else .65`, so
lowercase `д` and every other glyph retain their previous geometry.

Validation (full audit, then identical repeat):

| size | global mean IoU | `Д` IoU | `Д` FP | `Д` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.905269 → 0.905721 | 0.715493 → 0.772431 | 113 → 78 | 143 → 104 | 0.970843 → 0.971381 | 0.925374 → 0.925944 | 0.947564 → 0.948118 |
| 64 | 0.906014 → 0.906469 | 0.717192 → 0.774594 | 451 → 311 | 640 → 491 | 0.972789 → 0.973323 | 0.926620 → 0.927161 | 0.949144 → 0.949681 |
| 128 | 0.906534 → 0.906990 | 0.715052 → 0.772537 | 1919 → 1499 | 2522 → 2048 | 0.972105 → 0.972507 | 0.925318 → 0.925748 | 0.948134 → 0.948552 |

Only `Д` changed in the per-glyph comparison at every size; no glyph regressed,
FN decreased, and the repeated audit produced identical values. Decision:
**ACCEPTED**. Checkpoint: `build/highlight-audit/checkpoint-iteration-001.txt`.

### Highlight audit: `ф`, iteration 2 (2026-09-12)

Baseline was the accepted iteration-1 full audit. At 64 px the lowercase `ф`
map had its largest FN on the upper/lower outer ring arcs (751 FN, largest FN
component 155 px); the stem and BBox already matched. Hypothesis: the lowercase
outer ring was vertically inset too far, so changing only its outer vertical
bounds from `0.03…0.97h` to `0…1.00h` would recover the missing arcs. The
uppercase `Ф` keeps its `0.09…0.91H` inset.

| size | global mean IoU | `ф` IoU | `ф` FP | `ф` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.905721 → 0.906441 | 0.725057 → 0.815779 | 54 → 24 | 137 → 89 | 0.971381 → 0.972186 | 0.925944 → 0.929098 | 0.948118 → 0.950124 |
| 64 | 0.906469 → 0.907184 | 0.715686 → 0.805762 | 221 → 90 | 751 → 567 | 0.973323 → 0.973844 | 0.927161 → 0.927816 | 0.949681 → 0.950258 |
| 128 | 0.906990 → 0.907710 | 0.720381 → 0.811020 | 891 → 377 | 2755 → 2017 | 0.972507 → 0.972928 | 0.925748 → 0.926159 | 0.948552 → 0.948761 |

Only lowercase `ф` changed at every size; `Ф` and all other glyphs were
unchanged. Both full audits were byte-for-byte stable in the reported metrics,
with no regressions and lower FN. Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-002.txt`.

### Highlight audit: `Q`, iteration 3 (2026-09-12)

The post-`ф` baseline ranked `Q` among the largest error contributors. Its
external BBox matched, while the ring fill was consistently thinner than the
system raster. Hypothesis: increase only the ring's inner-contour inset for
`Q` by 12% (`ring_s = 1.12s`), leaving the outer oval and tail unchanged.

| size | global mean IoU | `Q` IoU | `Q` FP | `Q` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.906441 → 0.906601 | 0.728940 → 0.749053 | 61 → 70 | 173 → 151 | 0.972186 → 0.971914 | 0.929098 → 0.931855 | 0.950124 → 0.951487 |
| 64 | 0.907184 → 0.907314 | 0.730774 → 0.747123 | 216 → 270 | 681 → 587 | 0.973844 → 0.973470 | 0.927816 → 0.930276 | 0.950258 → 0.951360 |
| 128 | 0.907710 → 0.907857 | 0.729557 → 0.748134 | 885 → 1071 | 2714 → 2313 | 0.972928 → 0.970920 | 0.926159 → 0.930356 | 0.948761 → 0.950246 |

Only `Q` changed in the per-glyph comparison at all sizes. FN fell substantially;
FP rose but did not form a new larger connected error than the existing ring
mismatch. Both full audits were identical and all other glyphs were unchanged.
Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-003.txt`.

### Highlight audit: `5`, iteration 4 (2026-09-12)

The post-`Q` baseline showed the largest connected FN in the lower bowl of `5`
(bbox `[71,173,124,212]` at 64 px), while the upper left already contained an
FP component. Hypothesis: raise only the lower bowl return node
`lower_end_y_h` from `0.212176` to `0.222176`.

| size | global mean IoU | `5` IoU | `5` FP | `5` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.906601 → 0.906622 | 0.731138 → 0.733827 | 78 → 78 | 108 → 106 | 0.861210 → 0.861702 | 0.817568 → 0.820946 | 0.838821 → 0.840830 |
| 64 | 0.907314 → 0.907335 | 0.726615 → 0.729318 | 332 → 332 | 379 → 373 | 0.856525 → 0.856897 | 0.839475 → 0.842016 | 0.847914 → 0.849391 |
| 128 | 0.907857 → 0.907879 | 0.728889 → 0.731592 | 1325 → 1326 | 1633 → 1605 | 0.856056 → 0.856400 | 0.828340 → 0.831284 | 0.841970 → 0.843655 |

The full audits showed only `5` changed, with no IoU regressions and lower FN;
the repeated audit matched exactly. Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-004.txt`.

### Highlight audit: `Я`, iteration 5 (2026-09-12)

The post-`5` baseline showed a large connected FN in the upper bowl and leg of
`Я`. Its BBox matched at 64 px, but the rendered mirrored `R` was thinner than
the reference (mean thickness 5.798 vs 6.400 px). Hypothesis: increase only the
stroke parameter of the private mirrored `R` construction by 8% (`small.s *=
1.08`), leaving the join patch, advance, and all other glyphs unchanged.

| size | global mean IoU | `Я` IoU | `Я` FP | `Я` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.906622 → 0.906840 | 0.737257 → 0.764758 | 73 → 80 | 128 → 79 | 0.886470 → 0.885551 | 0.816619 → 0.886819 | 0.850112 → 0.886185 |
| 64 | 0.907335 → 0.907553 | 0.736946 → 0.764405 | 280 → 329 | 507 → 387 | 0.887955 → 0.876687 | 0.814013 → 0.858034 | 0.849378 → 0.867260 |
| 128 | 0.907879 → 0.908098 | 0.736744 → 0.764368 | 1208 → 1404 | 1906 → 1541 | 0.880562 → 0.868478 | 0.823714 → 0.857473 | 0.851190 → 0.862940 |

Only uppercase `Я` changed in the per-glyph comparison at every size; FN fell
substantially and no other glyph regressed. Both full audits were identical.
Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-005.txt`.

### Highlight audit: `Ф`, iteration 6 (2026-09-12)

The post-`Я` baseline ranked uppercase `Ф` as a large FN contributor at display
sizes. Its external BBox matched, but the ring and stem were thinner than the
reference (64 px median 5.657 vs reference 6.0). Hypothesis: increase only the
stroke size of uppercase `Ф` by 12% (`fs = 1.12s`); lowercase `ф` and the ring
bounds remain unchanged.

| size | global mean IoU | `Ф` IoU | `Ф` FP | `Ф` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.906840 → 0.906896 | 0.821118 → 0.828171 | 15 → 23 | 114 → 101 | 0.978814 → 0.968450 | 0.858736 → 0.874845 | 0.914851 → 0.919271 |
| 64 | 0.907553 → 0.907596 | 0.814534 → 0.819892 | 49 → 94 | 544 → 489 | 0.982606 → 0.967775 | 0.835749 → 0.852355 | 0.903247 → 0.906406 |
| 128 | 0.908098 → 0.908148 | 0.816109 → 0.822361 | 215 → 403 | 2429 → 2199 | 0.980629 → 0.965008 | 0.817547 → 0.834823 | 0.891693 → 0.895207 |

Only uppercase `Ф` changed in the per-glyph comparison at every size; FN fell,
no other glyph regressed, and both full audits were identical. Decision:
**ACCEPTED**. Checkpoint: `build/highlight-audit/checkpoint-iteration-006.txt`.

### Highlight audit: `Ю`, iteration 7 (2026-09-12)

The post-`Ф` baseline showed a large connected FN on the uppercase `Ю` oval.
The BBox and left stem matched, while the oval fill was consistently thinner
than the system raster. Hypothesis: increase only the oval ring thickness for
uppercase `Ю` by 12% in both axes (`ring_s` and `ring_sy`), leaving the stem,
advance, and lowercase `ю` unchanged.

| size | global mean IoU | `Ю` IoU | `Ю` FP | `Ю` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.906896 → 0.907008 | 0.839539 → 0.853639 | 20 → 49 | 109 → 74 | 0.976443 → 0.946331 | 0.883795 → 0.921109 | 0.927812 → 0.933549 |
| 64 | 0.907596 → 0.907671 | 0.834060 → 0.843459 | 55 → 157 | 635 → 515 | 0.983713 → 0.956377 | 0.839525 → 0.869851 | 0.905918 → 0.911064 |
| 128 | 0.908148 → 0.908244 | 0.837514 → 0.849710 | 242 → 630 | 2249 → 1722 | 0.982057 → 0.956256 | 0.854847 → 0.888860 | 0.914047 → 0.921327 |

Only uppercase `Ю` changed in the per-glyph comparison at every size; FN fell
substantially and no other glyph regressed. Both full audits were identical.
Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-007.txt`.

### Highlight audit: `я`, iteration 9 (2026-09-12)

The post-`Ю` baseline showed the lowercase `я` as a thin mirrored `R`: at 64 px
its rendered median thickness was 5.657 vs 6.0 for the reference, with FN 390
and a 3 px render BBox height excess. Hypothesis: increase only the stroke
parameter of the private mirrored `R` by 8% (`small.s *= 1.08`), without moving
the glyph or changing uppercase `Я`.

| size | global mean IoU | `я` IoU | `я` FP | `я` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.907008 → 0.907125 | 0.718219 → 0.732901 | 51 → 53 | 89 → 81 | 0.883827 → 0.881960 | 0.813417 → 0.830189 | 0.847162 → 0.855292 |
| 64 | 0.907671 → 0.907789 | 0.715687 → 0.730561 | 208 → 260 | 390 → 310 | 0.871287 → 0.851259 | 0.783092 → 0.827586 | 0.824839 → 0.839255 |
| 128 | 0.908244 → 0.908363 | 0.716342 → 0.731326 | 815 → 1019 | 1385 → 1177 | 0.875762 → 0.853844 | 0.805750 → 0.834923 | 0.839299 → 0.844277 |

Only lowercase `я` changed in the per-glyph comparison; FN decreased, no other
glyph regressed, and both full audits were identical. Decision: **ACCEPTED**.
Checkpoint: `build/highlight-audit/checkpoint-iteration-009.txt`.

### Highlight audit: `Э`, iteration 10 (2026-09-12)

The post-`я` diagnostic map showed the left end of the uppercase `Э` bar about
4 px too far left (FP component 36 px), with the right end aligned. Hypothesis:
trim only the bar's left reach from `0.28w` to `0.32w`; the outer curve, height,
and lowercase variants remain unchanged.

| size | global mean IoU | `Э` IoU | `Э` FP | `Э` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.907125 → 0.907180 | 0.719238 → 0.726222 | 48 → 39 | 142 → 142 | 0.916084 → 0.930728 | 0.786787 → 0.786787 | 0.846527 → 0.852726 |
| 64 | 0.907789 → 0.907844 | 0.722576 → 0.729526 | 192 → 165 | 597 → 597 | 0.915567 → 0.926569 | 0.777156 → 0.777156 | 0.840703 → 0.845311 |
| 128 | 0.908363 → 0.908418 | 0.721323 → 0.728273 | 720 → 618 | 2483 → 2483 | 0.919526 → 0.930130 | 0.768161 → 0.768161 | 0.837056 → 0.841422 |

Only uppercase `Э` changed, FN did not increase, and all other glyphs remained
identical. Both full audits were identical. Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-010.txt`.

### Highlight audit: `R`, iteration 11 (2026-09-12)

The post-`Э` baseline showed the largest connected FN in the lower diagonal leg
of standalone `R` (64 px: 498 FN, component 304 px), while the bowl was close.
Hypothesis: move only the leg's upper join left from `0.50w` to `0.43w`.
The shared `core('R')` call is guarded with a derived-glyph flag so accepted
`Я/я` contours retain their prior geometry.

| size | global mean IoU | `R` IoU | `R` FP | `R` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.907180 → 0.907254 | 0.785064 → 0.794345 | 23 → 20 | 132 → 129 | 0.960751 → 0.965870 | 0.810072 → 0.814388 | 0.879001 → 0.883685 |
| 64 | 0.907844 → 0.907920 | 0.784060 → 0.793632 | 105 → 91 | 498 → 477 | 0.954248 → 0.960469 | 0.814732 → 0.822545 | 0.878989 → 0.886172 |
| 128 | 0.908363 → 0.908495 | 0.784221 → 0.793857 | 398 → 335 | 1988 → 1935 | 0.956574 → 0.963408 | 0.815156 → 0.820084 | 0.880221 → 0.885987 |

Only standalone `R` changed in the per-glyph comparison; FN decreased and the
repeated full audit was identical. Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-011.txt`.

### Highlight audit: `6`, iteration 12 (2026-09-12)

The post-`R` baseline showed `6` with a thin contour in both bowls (64 px
median 5.657 vs reference 6.0; FN 512). Hypothesis: increase only the local
stroke size in the `6` branch by 8%, leaving the shared `9` branch unchanged.

| size | global mean IoU | `6` IoU | `6` FP | `6` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.907254 → 0.907405 | 0.758880 → 0.777969 | 42 → 45 | 130 → 110 | 0.928082 → 0.925865 | 0.806548 → 0.836310 | 0.863057 → 0.878812 |
| 64 | 0.907920 → 0.908072 | 0.763141 → 0.782356 | 173 → 178 | 512 → 449 | 0.926726 → 0.926719 | 0.810370 → 0.833704 | 0.864651 → 0.877754 |
| 128 | 0.908495 → 0.908648 | 0.761284 → 0.780616 | 699 → 722 | 2036 → 1802 | 0.925985 → 0.925575 | 0.811149 → 0.832854 | 0.864771 → 0.876770 |

Only `6` changed in the per-glyph comparison, FN decreased, and both full
audits were identical. Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-012.txt`.

### Highlight audit: `9`, iteration 13 (2026-09-12)

The post-`6` baseline showed the same thin bowl/stroke pattern in `9` (64 px
median 5.657 vs reference 6.0; FN 510). Hypothesis: increase only the local
stroke size in the `9` branch by 8%, while retaining the accepted `6` correction
and all other glyph geometry.

| size | global mean IoU | `9` IoU | `9` FP | `9` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.907405 → 0.907558 | 0.759126 → 0.778407 | 44 → 44 | 124 → 113 | 0.925424 → 0.926789 | 0.814925 → 0.831343 | 0.866667 → 0.876475 |
| 64 | 0.908072 → 0.908224 | 0.763126 → 0.782292 | 174 → 180 | 510 → 450 | 0.926427 → 0.925956 | 0.811181 → 0.833395 | 0.864982 → 0.877241 |
| 128 | 0.908648 → 0.908802 | 0.761219 → 0.780591 | 683 → 699 | 2034 → 1809 | 0.927648 → 0.927797 | 0.811510 → 0.832360 | 0.865701 → 0.877491 |

Only `9` changed in the per-glyph comparison; FN decreased and both full
validations were identical. Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-013.txt`.

### Highlight audit: `Л`, iteration 14 (2026-09-12) — REJECTED

The upper left connection trial produced no raster change at 0.32 width. A
stronger 0.24-width shift moved the slant too far: 64 px IoU `0.750799 →
0.676006`, FP `167 → 309`, FN `460 → 556`. Rolled back.

### Highlight audit: `Э`, iteration 15 (2026-09-12) — REJECTED

Raising the lower reflected endpoint produced no raster change. A centered 5%
vertical stretch then reduced 64 px IoU `0.729526 → 0.594504`, FP `165 → 465`,
FN `597 → 805`. Rolled back.

### Highlight audit: `Ж`, iteration 16 (2026-09-12) — REJECTED

Reducing uppercase `Ж` stroke thickness by 10% lowered IoU `0.760670 →
0.742359`; FN increased `345 → 548` despite FP falling `719 → 537`. Rolled
back.

### Highlight audit: `5`, iteration 17 (2026-09-12)

The lower bowl contained the largest connected FN component (239 px). Raising
only `lower_end_y_h` from `.222176` to `.30` reduced that component to 155 px.

| size | global mean IoU | `5` IoU | `5` FP | `5` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.907558 → 0.907705 | 0.733827 → 0.752261 | 78 → 79 | 106 → 93 | 0.861702 → 0.863322 | 0.820946 → 0.842905 | 0.840830 → 0.852991 |
| 64 | 0.908224 → 0.908373 | 0.729318 → 0.748025 | 332 → 337 | 373 → 321 | 0.856897 → 0.858225 | 0.842016 → 0.864041 | 0.849391 → 0.861123 |
| 128 | 0.908802 → 0.908949 | 0.731592 → 0.750068 | 1326 → 1339 | 1605 → 1390 | 0.856400 → 0.858487 | 0.831284 → 0.853884 | 0.843655 → 0.856179 |

Only `5` changed; FN decreased at every size, no other glyph regressed, and the
repeated full audit was identical. Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-017.txt`.

### Highlight audit: `5`, iteration 18 (2026-09-12)

The accepted `.30` endpoint still left a connected lower-bowl FN component of
155 px. Moving only `lower_end_y_h` to `.34` improved the global score and the
64 px glyph score.

| size | global mean IoU | `5` IoU | `5` FP | `5` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.907705 → 0.907730 | 0.752261 → 0.755410 | 79 → 82 | 93 → 88 | 0.863322 → 0.860068 | 0.842905 → 0.851351 | 0.852991 → 0.855688 |
| 64 | 0.908373 → 0.908400 | 0.748025 → 0.751396 | 337 → 348 | 321 → 303 | 0.858225 → 0.855362 | 0.864041 → 0.871665 | 0.861123 → 0.863436 |
| 128 | 0.908949 → 0.908976 | 0.750068 → 0.753543 | 1339 → 1384 | 1390 → 1319 | 0.858487 → 0.855502 | 0.853884 → 0.861348 | 0.856179 → 0.858415 |

Only `5` changed; no other glyph regressed and the repeated full audit was
byte-identical. Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-018.txt`.

### Highlight audit: `у`, iteration 23 (2026-09-12)

`у` was diagnosed as a thin-stroke mismatch while Latin `y` remained separate.
Hypothesis: render only Cyrillic `у` from a copied design with `s×1.08`.

| size | global mean IoU | `у` IoU | `у` FP | `у` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.908532 → 0.908638 | 0.723973 → 0.737341 | 39 → 55 | 84 → 67 | 0.891061 → 0.859335 | 0.791563 → 0.833747 | 0.838371 → 0.846348 |
| 64 | 0.909241 → 0.909346 | 0.723139 → 0.736306 | 164 → 213 | 336 → 277 | 0.886818 → 0.863198 | 0.792721 → 0.829118 | 0.837134 → 0.845815 |
| 128 | 0.909837 → 0.909943 | 0.722059 → 0.735462 | 627 → 819 | 1367 → 1136 | 0.891429 → 0.867861 | 0.790177 → 0.825633 | 0.837754 → 0.846220 |

Only Cyrillic `у` changed; FN decreased at every size, no other glyph regressed,
and both full audits were byte-identical. Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-023.txt`.

### Highlight audit: `я`, iteration 24 (2026-09-12)

The lowercase `я` still had a thin mirrored bowl after iteration 009. Hypothesis:
increase only its isolated copied `R` stroke from `s×1.08` to `s×1.12`; uppercase
`Я` remains at `1.08`.

| size | global mean IoU | `я` IoU | `я` FP | `я` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.908638 → 0.908685 | 0.732901 → 0.738896 | 53 → 65 | 81 → 77 | 0.881960 → 0.860215 | 0.830189 → 0.838574 | 0.855292 → 0.849257 |
| 64 | 0.909346 → 0.909392 | 0.730561 → 0.736358 | 260 → 271 | 310 → 296 | 0.851259 → 0.847152 | 0.827586 → 0.835373 | 0.839255 → 0.841221 |
| 128 | 0.909943 → 0.909991 | 0.731326 → 0.737410 | 1019 → 1074 | 1177 → 1038 | 0.853844 → 0.850126 | 0.834923 → 0.854418 | 0.844277 → 0.852266 |

Only lowercase `я` changed; FN decreased at every size, no other glyph
regressed, and both full audits were byte-identical. Decision: **ACCEPTED**.
Checkpoint: `build/highlight-audit/checkpoint-iteration-024.txt`.

### Highlight audit: `Д`, iteration 19 (2026-09-12)

The `Д` map showed the left external leg shifted 2–4 px inward while its BBox
was aligned. Hypothesis: move only the uppercase `Д` left-foot start from
`0.65s` to `0.45s`; lowercase `д` and the right shoulder remain unchanged.

| size | global mean IoU | `Д` IoU | `Д` FP | `Д` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.907730 → 0.908098 | 0.772431 → 0.818911 | 78 → 53 | 104 → 79 | 0.905109 → 0.935523 | 0.877358 → 0.906840 | 0.891018 → 0.920958 |
| 64 | 0.908400 → 0.908770 | 0.774594 → 0.821288 | 311 → 217 | 491 → 395 | 0.901551 → 0.931351 | 0.852950 → 0.881701 | 0.876577 → 0.905846 |
| 128 | 0.908976 → 0.909348 | 0.772537 → 0.819395 | 1499 → 1132 | 2048 → 1665 | 0.882302 → 0.911230 | 0.845841 → 0.874671 | 0.863687 → 0.892576 |

Only uppercase `Д` changed and the repeated full audit was byte-identical.
Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-019.txt`.

### Highlight audit: `Q`, iteration 20 (2026-09-12) — REJECTED

The lower tail of `Q` was the largest local mismatch after iteration 019.
Moving both tail start points from `.52w` to `.62w` reduced neither error class:
64 px IoU fell `0.747123 → 0.730445`, FP `270 → 288`, FN `587 → 629`.
The source and font were restored immediately.

### Highlight audit: `Л`, iteration 21 (2026-09-12) — REJECTED

The lower left connection was tested independently by moving `left_low` from
`.13w` to `.08w`. The slant then overshot the reference: 64 px IoU
`0.750799 → 0.658786`, FP `167 → 301`, FN `460 → 609`. Restored immediately.

### Highlight audit: `Д`, iteration 22 (2026-09-12)

After the left-leg correction, the largest remaining FN component was the top
edge of the bottom foot. Hypothesis: increase only the uppercase `Д` foot
height from `sy` to `1.4sy`, including its two short supports.

| size | global mean IoU | `Д` IoU | `Д` FP | `Д` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.908098 → 0.908532 | 0.818911 → 0.873508 | 53 → 63 | 79 → 45 | 0.935523 → 0.927252 | 0.906840 → 0.946934 | 0.920958 → 0.936989 |
| 64 | 0.908770 → 0.909241 | 0.821288 → 0.880648 | 217 → 217 | 395 → 161 | 0.931351 → 0.936082 | 0.881701 → 0.951782 | 0.905846 → 0.943867 |
| 128 | 0.909348 → 0.909837 | 0.819395 → 0.880950 | 1132 → 1139 | 1665 → 769 | 0.911230 → 0.916587 | 0.874671 → 0.942115 | 0.892576 → 0.929176 |

Only uppercase `Д` changed; FN decreased at every size, no other glyph
regressed, and both full audits were byte-identical. Decision: **ACCEPTED**.
Checkpoint: `build/highlight-audit/checkpoint-iteration-022.txt`.

### Highlight audit: `5`, iteration 18 (2026-09-12)

The accepted `.30` endpoint still left a connected lower-bowl FN component of
155 px. Hypothesis: move only `lower_end_y_h` one further local step to `.34`.

| size | global mean IoU | `5` IoU | `5` FP | `5` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.907705 → 0.907730 | 0.752261 → 0.752261 | 79 → 79 | 93 → 93 | 0.863322 → 0.863322 | 0.842905 → 0.842905 | 0.852991 → 0.852991 |
| 64 | 0.908373 → 0.908400 | 0.748025 → 0.751396 | 337 → 348 | 321 → 303 | 0.858225 → 0.855362 | 0.864041 → 0.871665 | 0.861123 → 0.863436 |
| 128 | 0.908949 → 0.908976 | 0.750068 → 0.750068 | 1339 → 1339 | 1390 → 1390 | 0.858487 → 0.858487 | 0.853884 → 0.853884 | 0.856179 → 0.856179 |

The change improved the global IoU at all sizes and the 64 px glyph IoU, while
reducing FN and introducing no regression in any other glyph. The repeated full
audit was byte-identical. Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-018.txt`.

### Highlight audit: `Э`, iteration 26 (2026-09-12) — REJECTED

The 64 px map suggested the reflected outer curve ended too high in the upper
left area. Lowering only its start point from `.80H` to `.74H` produced no
raster change: IoU, FP and FN remained `0.729526`, `165`, and `597`. Restored.

### Highlight audit: `ф`, iteration 28 (2026-09-12)

The lowercase `ф` ring was thinner than the reference (64 px mean thickness
delta −0.805 px) while its BBox was aligned. Hypothesis: increase only its
ring stroke from `1.0s` to `1.08s`; uppercase `Ф` remains unchanged.

| size | global mean IoU | `ф` IoU | `ф` FP | `ф` FN | precision | recall | dice |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 32 | 0.908685 → 0.908718 | 0.815779 → 0.819943 | 24 → 28 | 89 → 83 | 0.964072 → 0.958702 | 0.878581 → 0.886767 | 0.919343 → 0.921332 |
| 64 | 0.909392 → 0.909429 | 0.805762 → 0.810408 | 90 → 110 | 567 → 446 | 0.964775 → 0.959199 | 0.812995 → 0.852902 | 0.882406 → 0.902933 |
| 128 | 0.909991 → 0.910022 | 0.811020 → 0.814897 | 377 → 464 | 2017 → 1894 | 0.963288 → 0.955721 | 0.830632 → 0.840961 | 0.892055 → 0.894676 |

Only lowercase `ф` changed; FN decreased at every size, no other glyph regressed,
and both full audits were byte-identical. Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-028.txt`.
### Geometry reconstruction diagnostics (2026-09-12)

После контрольной версии (mean inkIoU `0.908718 / 0.909429 / 0.910022` для
32/64/128 px) проверены две формульные гипотезы для одного glyph `Э`.

* Независимый центрлайновый контур с верхней/нижней кривыми и правой
  вертикалью нарушил топологию: 64 px IoU `0.729526 → 0.460834`, FP `165 →
  589`, FN `597 → 1165`. Отклонено.
* Продление только двух открытых концов отражённого контура уменьшило FN
  `597 → 515`, но создало сопоставимую FP-зону `165 → 371` и снизило общий
  64 px IoU `0.909429 → 0.909110`. Отклонено; исходники восстановлены.

Добавлен автоматический `scripts/geometry-audit.py`. Он использует уже
сохранённые маски и для каждого glyph вычисляет BBox, толщину, направленные
расстояния между границами, крупнейшие связные FN/FP-компоненты и диагностирует
смещение/масштаб, толщину, пропуск или лишний сегмент, кривизну и сглаживание.
`run-highlight-audit.sh --analyze` теперь создаёт также
`build/highlight-audit/geometry-audit.json`, поэтому следующий выбор формулы
делается по геометрической карте, а не перебором глобальных чисел.

### Iteration 031 — geometry formula trials for `Э`

Control baseline was rerendered twice with the same result. Mean inkIoU was
`0.908718 / 0.909429 / 0.910022` at 32/64/128 px; the repeat verifier reported
`reproducible: true`.

Three isolated formula hypotheses were tested against this control glyph:

| hypothesis | 64 px glyph IoU | FP | FN | global mean IoU | decision |
|---|---:|---:|---:|---:|---|
| independent centreline, short right stem | 0.460834 | 589 | 1165 | 0.905565 | rejected |
| two tangent extensions on reflected contour | 0.705365 | 371 | 515 | 0.909110 | rejected |
| independent centreline, endpoints at 0.70/0.30 height | 0.553267 | 552 | 894 | 0.907676 | rejected |

Each candidate was rendered at all three sizes and changed only `Э`. The
control source and font were restored after each rejection; the final full
audit is reproducible and matches the control metrics above.

### Highlight audit: `Ж`, iteration 32 (2026-09-12) — ACCEPTED

The geometry audit showed symmetric FP bridges on the lower diagonals while
BBox and median thickness stayed aligned. Hypothesis: the inner diagonal join
node was too close to the central stem. Only uppercase `Ж` uses a larger join
inset (`1.65s → 1.85s`); lowercase `ж` and all other glyphs are unchanged.

| size | global mean IoU | `Ж` IoU | `Ж` FP | `Ж` FN | largest FP |
|---:|---:|---:|---:|---:|---:|
| 32 | 0.908718 → 0.908770 | 0.762312 → 0.768855 | 186 → 206 | 46 → 24 | 39 → 39 |
| 64 | 0.909429 → 0.909483 | 0.760670 → 0.767470 | 719 → 806 | 345 → 250 | 171 → 171 |
| 128 | 0.910022 → 0.910076 | 0.760316 → 0.767132 | 2887 → 3235 | 1123 → 744 | 726 → 726 |

Both full audits were reproducible. No other glyph regressed, FN decreased at
all sizes, and the largest FP component did not grow. Decision: **ACCEPTED**.
Checkpoint: `build/highlight-audit/checkpoint-iteration-032.txt`.

### Highlight audit: `Q`, iteration 033 — REJECTED

The geometry audit isolated a curvature mismatch in the Q ring. Changing only
the Q-specific cubic curvature coefficient from `k=.565` to `.50` reduced the
64 px glyph IoU `0.747123 → 0.712843`, increased FN `587 → 681`, and reduced
the global mean IoU `0.909483 → 0.909211`. The source was restored immediately;
the earlier `Ж` checkpoint remains the best version.

### Highlight audit: `Э`, iteration 034 (2026-09-12) — ACCEPTED

The geometry map showed two large connected FN regions on the open-left bowl
ends while the BBox was identical and thickness was nearly aligned. Hypothesis:
the reflected C placed the paired endpoint nodes too high/low (`.82H/.18H`);
reconstructing the same outer and inner contour with paired endpoints at
`.74H/.26H` should close those FN regions without changing the bar or stroke
width. Only uppercase `Э` was changed.

| size | global mean IoU | `Э` IoU | `Э` FP | `Э` FN | largest FN |
|---:|---:|---:|---:|---:|---:|
| 32 | 0.908770 → 0.910036 | 0.726222 → 0.815366 | 39 → 19 | 142 → 92 | 49 → 13 |
| 64 | 0.909483 → 0.910768 | 0.729526 → 0.821555 | 165 → 87 | 597 → 405 | 314 → 206 |
| 128 | 0.910076 → 0.911359 | 0.728273 → 0.819239 | 618 → 311 | 2483 → 1680 | 1280 → 839 |

Both full audits were reproducible, no other glyph regressed, and both FP and
FN decreased. Decision: **ACCEPTED**. Checkpoint:
`build/highlight-audit/checkpoint-iteration-034.txt`.

### Process retrospective (2026-09-12)

Причины медленного прогресса и рабочая матрица решений вынесены в
`GLYPH-OPTIMIZATION-RETROSPECTIVE.md`. Для повторного выбора кандидата после
каждого baseline используется `scripts/next-glyph-plan.py`; он ранжирует
связные FN/FP, BBox и boundary distance и предлагает одну логическую группу
для проверки. Это не меняет исходники и не заменяет обязательный полный audit
с повтором.

### Highlight audit: `Ж`, iteration 035 (2026-09-12)

Baseline после web-сборки был воспроизводим: средний IoU `0.910036 / 0.910768 /
0.911359` для 32/64/128 px. `Ж` имел IoU `0.768855 / 0.767470 / 0.767132`,
а на 64 px — FP 806, FN 250; BBox совпадал, но крупнейшие FP находились на
боковых нижних рукавах.

Гипотеза: боковые наконечники `Ж` слишком длинные; изменить только локальный
endpoint `tip` для uppercase `Ж` с `1.60s` до `1.40s`. Override изолирован через
`TABUNA_PILOT_ZHE_TIP`, lowercase `ж` и остальные glyphs не затронуты.

Пилот дал для `Ж` на 64 px IoU `0.767470 → 0.772733`, FP `806 → 692`, но FN
`250 → 316`. Полный аудит показал прирост среднего IoU `0.910768 → 0.910809`,
однако условие FN нарушено на всех размерах (`24→37`, `250→316`, `744→966`).
Гипотеза **REJECTED**. Кандидат сохранён в
`build/highlight-audit/candidate-iteration-035-zhe-tip-1.40.json`; источник и
web-build возвращены к контрольной версии. Повторный контроль совпал с
baseline (`reproducible=true`).

### Local SFNS structural inspection and `К`, iteration 036 (2026-09-12)

Локально найден `/System/Library/Fonts/SFNS.ttf`. FontTools подтвердил
TrueType `glyf`, UPM 2048 и оси `wdth/opsz/GRAD/wght`. Для `К` исходная структура
— один ordered contour из 14 on-curve points; текущая составная форма имела
несколько перекрывающихся контуров.

Гипотеза: большая FN/FP `К` вызвана неверной топологией, поэтому заменить её
на один независимый упорядоченный контур со стержнем, двумя плечами и waist
notch. Пилот: 64 px IoU `0.752930 → 0.931227`, FP `137 → 34`, FN `485 → 95`.
Полный аудит: средний IoU `0.910768 → 0.912183`; на 32/64/128 px
`0.910036/0.910768/0.911359 → 0.911435/0.912183/0.912776`. Изменился только
`К`, FN уменьшился на всех размерах, новая крупная FP-компонента не появилась,
повторный audit идентичен (`reproducible=true`). Изменение **ACCEPTED**.
Checkpoint: `build/highlight-audit/checkpoint-iteration-036.txt`.

### Local SFNS structure: `Я`, iteration 037 (2026-09-12)

После принятой `К` baseline оставался воспроизводимым: mean IoU
`0.911435 / 0.912183 / 0.912776` для 32/64/128 px. SFNS inspection показал
для `Я` два контура: внешний 16 points и внутренний 10 points.

Гипотеза: заменить зеркальный `R` и join patch на две независимые quadratic-
структуры с округлёнными относительными landmarks. Пилот на 64 px ухудшил
IoU `0.764405 → 0.617628`, FP `329 → 513`, FN `387 → 714`, BBox перестал
совпадать. Это **REJECTED**: совпадение количества контуров без точной
геометрии чаши и соединения недостаточно. Production восстановлен; полный
контроль после отката совпал с baseline, `reproducible=true`.

### Local SFNS structure: `Ж`, iteration 038 (2026-09-12)

SFNS inspection показал для `Ж` один симметричный контур из 24 on-curve
points. После исправления изоляции пилота (только `ch == 'Ж'`) независимая
перерисовка этого ordered-контура прошла полный audit: на 64 px IoU
`0.767470 → 0.979413`, FP `806 → 10`, FN `250 → 0`; BBox совпадает.
Средний полный IoU вырос `0.912183 → 0.913865` (32/64/128:
`0.911435/0.912183/0.912776 → 0.913106/0.913865/0.914461`). Lowercase `ж`
и остальные glyphs не изменились, повторный audit идентичен. Изменение
**ACCEPTED**. В production оставлен legacy-override только через
`TABUNA_PILOT_ZHE_LEGACY`.

### Local SFNS structure: `Q`, iteration 039 (2026-09-12)

После принятой `Ж` baseline: mean IoU `0.913106 / 0.913865 / 0.914461`.
SFNS содержит для `Q` три контура: кольцо и отдельный хвост ниже baseline.

Гипотеза: изменить только внешний tail contour — продлить его до `-0.113H`
и поднять attachment к `.286H`. Пилот на 64 px уменьшил FN `587→534`, но
увеличил FP `270→352`; IoU снизился `0.747123→0.746419`. Изменение
**REJECTED**. После отката полный контроль совпал с baseline,
`reproducible=true`.

### Local SFNS structure: `Ю`, iteration 040 (2026-09-12)

SFNS inspection показал для `Ю` три контура: стержень, внешний ring и
внутренний ring. Production уже имел три контура, но ring был обычным
ellipse. Одна гипотеза изменила только outer/inner ring bounds и кривизну по
наблюдаемой quadratic-структуре SFNS; стержень и перекладина не трогались.

На 64 px `Ю` улучшилась `0.843459 → 0.904534`, FP `157 → 94`, FN `515 → 334`.
Полный mean IoU вырос `0.913865 → 0.914349` (32/64/128:
`0.913106/0.913865/0.914461 → 0.913579/0.914349/0.914941`). Только `Ю`
изменился; FN уменьшился, повторный audit идентичен. Изменение **ACCEPTED**.
В production оставлен legacy-override `TABUNA_PILOT_YU_RING_LEGACY`.

### Local SFNS structure: `Q`, iteration 041 (2026-09-12)

Текущий baseline после `Ю`: mean IoU `0.913579 / 0.914349 / 0.914941`
для 32/64/128 px. Карта ошибок `Q` показала связную FN сверху и справа
кольца и FP снизу при совпадающей топологии из трёх контуров. SFNS подтверждает
отдельное кольцо и отдельный хвост; проверялась только группа внешней геометрии
кольца.

Гипотеза: кольцо `Q` вертикально посажено примерно на 1–2 raster px ниже
эталона; поднятие outer/inner ring на `+10` font units уменьшит верхнюю FN и
нижнюю FP, не меняя хвост и другие glyphs. Override изолирован через
`TABUNA_PILOT_Q_RING_SHIFT`.

Пилот дал на 64 px `Q` IoU `0.747123 → 0.775786`, FP `270 → 219`, FN
`587 → 531`; на 32/128 px IoU также выросла (`0.749053→0.777148`,
`0.748134→0.777318`). Полный повторяемый audit изменил только `Q`: mean IoU
вырос `0.914349 → 0.914577` (32/64/128:
`0.913579/0.914349/0.914941 → 0.913802/0.914577/0.915172`), total FP/FN
уменьшились на всех размерах. Новая крупная FP-компонента не появилась,
повторный audit идентичен (`reproducible=true`). Изменение **ACCEPTED**;
`+10` units оставлены production default, override сохранён для повторения.

### Local SFNS structure: Latin `K`, iteration 042 (2026-09-12) — REJECTED

После принятого `Q` baseline был повторно запущен и воспроизводим. Для Latin
`K` BBox на 64 px был смещён вниз на 2 px (`[73,129,140,219]` reference против
`[73,131,139,221]` render). Гипотеза: убрать только исторический локальный
offset `−15.625` font units у верхнего `K`, оставив геометрию диагоналей без
изменений. Override изолирован через `TABUNA_PILOT_LATIN_K_SHIFT`.

Пилот дал на 64 px IoU `0.766412 → 0.712177`, FP `67 → 138`, FN `517 → 592`;
на 32/128 px IoU также снизилась (`0.766415→0.712589`,
`0.766161→0.712160`). Несмотря на более близкий BBox, диагонали стали
систематически расходиться. Гипотеза **REJECTED**; production offset
`−15.625` сохранён. Полный контроль после отката совпал с iteration 041
(`reproducible=true`).

### Local SFNS structure: `Л`, iteration 043 (2026-09-12) — ACCEPTED

После отклонения `K` контрольный baseline был повторно проверен. Для `Л`
карта ошибок показывала крупные связные FN на обеих наклонных ножках при
совпадающем BBox. Локальный SFNS `El.cyrl` содержит один ordered contour из
22 точек (12 on-curve, 10 off-curve).

Гипотеза: заменить только внешнюю геометрию `Л` на независимую quadratic
реконструкцию этой структуры с отдельными ролями левой ножки, вершины,
правого стержня и внутреннего возврата. Координаты нормализованы по BBox
SFNS; стержни и остальные glyphs не менялись.

Полный повторяемый audit дал для `Л` на 64 px IoU `0.750799 → 0.760349`,
FP `167 → 184`, FN `460 → 413`; крупнейшая FP-компонента уменьшилась
`130 → 110`. Средний глобальный IoU вырос `0.914577 → 0.914653`, total FN
уменьшился `17423 → 17376`, а остальные glyphs остались неизменными.
На 32/128 px глобальный IoU также вырос. Изменение **ACCEPTED**; новая
геометрия включена в production default, `TABUNA_PILOT_EL_LEGACY` оставлен
для воспроизводимого сравнения.

### Local SFNS structure: Latin `K`, iteration 044 — REJECTED

После `Л` baseline был воспроизводим. SFNS `K` имеет три независимых
all-on-curve контура: стержень и две диагональные руки. Реконструкция этих
контуров по локальным `glyf` дала крупный прирост на 64 px (`0.766412 →
0.834823`, FN `517 → 239`), а mean global IoU вырос `0.914653 → 0.915196`.

Однако новая геометрия создала самостоятельную FP-компоненту на верхней
диагонали площадью `83` пикселя против `20` в baseline (на 128 px `332`
против `134`). Это нарушает критерий отсутствия сопоставимой крупной FP,
поэтому вариант **REJECTED** и production восстановлен. Кандидат сохранён в
`build/highlight-audit/candidate-iteration-044-k-structure.json`.

### Local SFNS structure: Latin `K`, iteration 045 (2026-09-12) — ACCEPTED

После отклонения полного SFNS-переноса baseline был восстановлен. Карта
ошибок показала параллельный красно-синий ореол на обеих диагоналях: руки
совпадали по топологии, но были сдвинуты относительно стержня. Проверялась
одна логическая группа — положение двух диагональных контуров — при
фиксированной SFNS-топологии. Применена локальная коррекция `dx=-10,
dy=+14` font units к обеим рукам; стержень не менялся.

На 64 px `K` IoU выросла `0.766412 → 0.896778`, FN уменьшился `517 → 173`,
FP составил `67 → 82`, а крупнейшая FP-компонента уменьшилась `20 → 11`.
Полный повторяемый audit изменил только `K`: mean global IoU вырос
`0.914653 → 0.915687`, total FN уменьшился `17376 → 17032`. На 32/128 px
глобальный IoU также вырос, новых крупных FP-компонент нет. Изменение
**ACCEPTED**; SFNS-структура включена в production default, legacy доступен
через `TABUNA_PILOT_LATIN_K_LEGACY`.

### Local SFNS structure: `Q`, iteration 046–047 (2026-09-12)

После `K` baseline для `Q` показывал median thickness `5.657` против `6.0`
у эталона на 64 px. Тест +8% уменьшил FN, но добавил сопоставимую FP и был
отклонён. Отдельная умеренная гипотеза +4% изменила только толщину outer/inner
кольца `Q` (`TABUNA_PILOT_Q_RING_THICKNESS=1.04`), хвост и остальные glyphs
не трогались.

На 64 px `Q` IoU выросла `0.775786 → 0.784409`, FN `531 → 479`, FP
`219 → 252`; крупнейшая FP-компонента уменьшилась `74 → 70`. Полный
повторяемый audit изменил только `Q`: mean global IoU вырос
`0.915687 → 0.915756`, total FN `17032 → 16980`. На 32/128 px глобальный
IoU также вырос, новых крупных FP нет. Изменение **ACCEPTED**; коэффициент
`1.04` включён в production default.

### Local SFNS structure: `5`, iteration 048 (2026-09-12) — ACCEPTED

Baseline после `Q` thickness correction был воспроизводим. У `5` карта ошибок
содержала крупные FP/FN в верхнем плече и нижней чаше; SFNS `five` содержит
один ordered quadratic contour из 46 точек. Проверялась только внешняя
геометрия этого glyph: контур нормализован по его BBox и восстановлен через
quadratic handles, без изменения параметров других символов.

На 64 px `5` IoU выросла `0.751396 → 0.833409`, FP `348 → 125`, FN
`303 → 277`, крупнейшая FP-компонента уменьшилась `234 → 52`. Полный
повторяемый audit изменил только `5`: mean global IoU вырос
`0.915756 → 0.916407`, total FP `6170 → 5947`, total FN `16980 → 16954`.
На 32/128 px глобальный IoU также вырос. Изменение **ACCEPTED**; SFNS-
реконструкция включена в production default, legacy доступен через
`TABUNA_PILOT_FIVE_LEGACY`.

### Local SFNS structure: `Я`, iteration 049 (2026-09-12) — ACCEPTED

У `Я` контрольный IoU был самым низким среди крупных кириллических glyphs
(`0.764405` на 64 px). Гипотеза заменяла rough-скелет на независимую
реконструкцию двухконтурной топологии `Ia.cyrl`: вертикальный штрих,
верхнее плечо, нижняя диагональ и внутренняя чаша восстановлены по
контрольным точкам и quadratic-сегментам BBox, без зеркалирования латинского
аналога и без глобального изменения advance.

На 64 px IoU `Я` вырос `0.764405 → 0.964244`, FN уменьшился `387 → 37`, FP
`329 → 63`; BBox совпал по x и высоте, вертикальная разница составила один
пиксель из-за рендера. Полный повторяемый audit изменил только `Я`: mean
global IoU вырос `0.916407 → 0.917993`, total FN `16954 → 16604`. На 32/128
px глобальный IoU также вырос, новых крупных FP-компонент нет. Изменение
**ACCEPTED**; production default использует standalone SFNS-like геометрию,
legacy доступен через `TABUNA_PILOT_YA_LEGACY`.

### Local SFNS structure: `Л`, iteration 050 (2026-09-12) — ACCEPTED

У `Л` прежняя 22-точечная реконструкция передавала все точки как quadratic
handles, из-за чего крупные FN возникали на левой ножке и внутреннем возврате.
Новая гипотеза сохранила тот же BBox и advance, но восстановила исходную
последовательность сегментов `lineTo/qCurveTo` одного SFNS-подобного контура
в независимых координатах Tabuna Sans.

На 64 px IoU `Л` вырос `0.760349 → 0.995806`, FN уменьшился `413 → 7`, FP
`184 → 2`. Полный повторяемый audit изменил только `Л`: mean global IoU вырос
`0.917993 → 0.919861`, total FN `16604 → 16198`. На 32/128 px глобальный
IoU также вырос, новых крупных FP-компонент нет. Изменение **ACCEPTED**;
legacy доступен через `TABUNA_PILOT_EL_LEGACY`.

### Local SFNS structure: `я`, iteration 051 (2026-09-12) — ACCEPTED

Для строчной `я` прежняя форма наследовала латинский `R`, что давало большие
связные FN в чаше и диагоналях. Контур заменён независимой двухконтурной
реконструкцией SFNS `ia.cyrl` с явными `lineTo/qCurveTo` сегментами; advance
сохранён в прежней calibrated базе, изменена только геометрия ink.

На 64 px IoU `я` вырос `0.736358 → 0.924464`, FN `296 → 84`, FP `271 → 61`.
Полный повторяемый audit изменил только `я`: mean global IoU вырос
`0.919861 → 0.921354`, total FN `16198 → 15986`. На 32/128 px глобальный
IoU также вырос, новых крупных FP-компонент нет. Изменение **ACCEPTED**;
legacy доступен через `TABUNA_PILOT_YA_LOWER_LEGACY`.

### Local SFNS structure: `ж`, iteration 052 (2026-09-12) — ACCEPTED

У строчной `ж` прежняя раздельная stroke-конструкция создавала крупную FP
область в центральном соединении. SFNS `zhe.cyrl` задаёт один 24-точечный
контур; его топология восстановлена в независимых координатах Tabuna Sans,
а calibrated advance сохранён.

На 64 px IoU `ж` вырос `0.771072 → 1.000000`, FP `546 → 0`, FN `99 → 0`.
Полный повторяемый audit изменил только `ж`: mean global IoU вырос
`0.921354 → 0.923171`, total FN `15986 → 15887`. На 32/128 px глобальный
IoU также вырос, новых FP-компонент нет. Изменение **ACCEPTED**; legacy
доступен через `TABUNA_PILOT_ZHE_LOWER_LEGACY`.

### SFNS contour hypothesis: `Q`, iteration 053 (2026-09-12) — REJECTED

Проверена отдельная реконструкция `Q` по трём SFNS-контурам: внешнее кольцо,
внутренний контур и хвост. На 64 px IoU снизился `0.784409 → 0.779903`, FP
вырос `252 → 440`, хотя FN уменьшился `479 → 348`; рост лишней площади
сопоставим с выигрышем. Вариант отклонён, production оставлен на checkpoint
052. Прямое масштабирование SFNS-координат не учитывает текущую optical-size
форму кольца.

### Local SFNS structure: `б`, iteration 054 (2026-09-12) — ACCEPTED

У `б` прежняя форма собиралась из кольца и локального polygon-перехода, что
давало крупные FP/FN на чаше и верхнем ascender-сегменте. SFNS `be.cyrl`
содержит один внешний quadratic-контур и внутреннюю чашу; эта последовательность
восстановлена в независимых координатах Tabuna Sans с сохранением advance.

На 64 px IoU `б` вырос `0.759054 → 0.950081`, FP `261 → 44`, FN `382 → 77`.
Полный повторяемый audit изменил только `б`: mean global IoU вырос
`0.923171 → 0.924687`, total FN `15887 → 15582`. На 32/128 px глобальный
IoU также вырос, новых крупных FP-компонент нет. Изменение **ACCEPTED**;
legacy доступен через `TABUNA_PILOT_BE_LEGACY`.

### Local SFNS structure: `Б`, iteration 055 (2026-09-12) — ACCEPTED

У `Б` прежняя форма имела крупные FN на верхней и нижней чашах при совпадающем
центральном стержне. SFNS `Be.cyrl` задаёт два quadratic-контура; их явная
последовательность `lineTo/qCurveTo` восстановлена в независимых координатах
Tabuna Sans с сохранением advance.

На 64 px IoU `Б` вырос `0.813430 → 1.000000`, FP `83 → 0`, FN `464 → 0`.
Полный повторяемый audit изменил только `Б`: mean global IoU вырос
`0.924687 → 0.926168`, total FN `15582 → 15118`. На 32/128 px глобальный
IoU также вырос, новых FP-компонент нет. Изменение **ACCEPTED**; legacy
доступен через `TABUNA_PILOT_UPPER_BE_LEGACY`.

### Local geometry hypotheses: `б`, iterations 056a–056b (2026-09-12) — REJECTED

Проверены две адресные коррекции уже принятого SFNS-контура `б`. Полный
вертикальный сдвиг на `+16` units дал IoU `0.950081 → 0.823019` на 64 pt:
верх совпал, но нижняя граница ушла вверх. Вертикальное растяжение `1.022`
сохранило BBox, но снизило IoU до `0.927741` и увеличило FP `44 → 109`.
Обе гипотезы отклонены; production остаётся на checkpoint 055/054.

## Iteration 057 — digit 9 SFNS contour reconstruction (accepted)

- Hypothesis: replace the legacy `9` geometry with an independent one-contour reconstruction from the inspected SFNS quadratic topology; retain the existing advance and map coordinates into the current glyph box.
- Scope: only `9`; pilot first via `TABUNA_PILOT_NINE_SFNS_EXACT`, then promoted to default behind `TABUNA_PILOT_NINE_LEGACY`.
- Result: local `9` IoU improved from 0.782292 to 0.984197 at 64px; FN 450→17 and FP 180→32. Full mean Ink IoU improved 0.926168→0.927770 at 64px (32px 0.925274→0.926907; 128px 0.926747→0.928362). Repeatability verified.

## Iteration 058 — variable weight thickness audit (diagnostic baseline)

- Added `scripts/weight-highlight-audit.py` and `scripts/run-weight-highlight-audit.sh`; the tool renders all 126 audited characters at `wght=100,400,800`, emits red/blue/gray highlight maps, and records IoU, FP/FN, BBox and distance-transform thickness deltas per glyph.
- Baseline: `build/weight-highlight-audit/baseline-iteration-058.json`; repeated run is pixel-reproducible.
- Findings at 64px: mean Ink IoU is 0.761284 (100), 0.927770 (400), 0.895337 (800). At 800 the rendered glyphs are systematically thinner by −0.689px on average (FN 44111); at 100 the aggregate bias hides glyph-specific failures, notably `Я`, `Б`, `9`, and `Л` where reconstructed contours remain too thick. No geometry change is accepted in this diagnostic iteration.

## Iteration 059 — weight-aware `9` endpoint hypothesis (rejected)

- Baseline: `build/highlight-audit/baseline-iteration-059.json`; regular 64px mean Ink IoU 0.927770, glyph `9` 0.984197; weight baseline is `build/weight-highlight-audit/baseline-iteration-058.json`.
- Hypothesis: interpolate per-point endpoint deltas for the reconstructed `9` contour so its stroke width follows the SFNS 100/400/900 masters.
- Pilot: at `wght=800`, `9` improved 0.667492→0.784517 (FN 1346→251); at `wght=100`, it regressed 0.468319→0.366272 (FP 1371→549, FN 31→600). Full weight mean changed 100: 0.761284→0.760474, 800: 0.895337→0.896265; 400 stayed 0.927770. Since the endpoint trade-off lowered the 100 result and regular IoU did not strictly rise, the hypothesis was rejected and the source restored. Reverted full audit reproduced baseline exactly.

## Iteration 060 — weight-aware `Л` endpoint hypothesis (rejected)

- Hypothesis: interpolate the inspected 100/400/900 master deltas for the accepted `Л` contour to remove its large thin-stem FN at `wght=800`.
- Pilot result: `Л` at 800 improved 0.621482→0.710656 and FN 1619→523, but FP rose 0→995; at 100 IoU regressed 0.462934→0.239105. Regular 400 remained unchanged at 0.995806. The change was rejected because the endpoint FP trade-off and 100 regression violate the acceptance gates; source restored.

## Iteration 062 — common `S_v` scale hypothesis (rejected before render)

- Structural audit: `build/system-font-inspection/GEOMETRY-SYSTEM-AUDIT.md`.
- Hypothesis: multiply shared `Design.s` by 1.03 to reduce the measured regular/black thin-stem bias across related glyph families.
- Result: the candidate build failed its existing advance invariant (`Base advances changed`) before audit, proving that `s` currently controls both stroke geometry and base metrics. No binary candidate was accepted. The pilot was removed; a full post-revert audit reproduced the 0.926907/0.927770/0.928362 baseline at 32/64/128.

## Iteration 063 — shared round overshoot audit (rejected)

- **Hypothesis:** SFNS uses one overshoot rule per round class, so a shared `round_overshoot_scale` might correct residual `o/O/0/о/О` errors.
- **Evidence:** SFNS inspection (`build/system-font-inspection/overshoot-analysis.json`) measured common class overshoots at `opsz=28`: lowercase round `17/20/23` units (wght 100/400/800), uppercase round and `0` `21/24/25` units. Existing Tabuna round data already interpolates overshoot by glyph, weight, and optical mode.
- **Pilot:** actual rebuild of `dist` with one environment parameter, scaling only the outer y extrema of `o/O/о/О` by `1.10`; `0` was included in the hypothesis scope but is not generated by `rounds.py` and therefore remained unchanged.
- **Result:** mean Ink IoU fell at every size: 32 pt `0.926907 → 0.926761` (−0.000146), 64 pt `0.927770 → 0.927619` (−0.000151), 128 pt `0.928362 → 0.928211` (−0.000151). At 64 pt, `o` fell `0.996659→0.991861`, `O` `0.998070→0.993345`, `о` `0.996586→0.991786`, `О` `0.998096→0.993373`; FN stayed almost unchanged while FP increased (for `O`, `FP 1→23`). The audit itself was reproducible.
- **Decision:** reject and restore the source. The shared overshoot rule is real in SFNS, but Tabuna’s calibrated round data already matches the raster target at regular weight; increasing it creates FP without fixing the large `0/8` FN components.

## Iteration 064 — `8` upper-counter floor (accepted)

- **Baseline:** iteration 063, mean Ink IoU `0.926907 / 0.927770 / 0.928362` at 32/64/128 pt.
- **Selection:** glyph `8` had a connected FN component of `127 px` at 64 pt (`bbox [82,143,123,169]`), with equal BBoxes and no evidence of a global shift. Row-wise masks showed the reference central join was already closed while the rendered upper counter remained open.
- **Hypothesis:** the lower boundary of the upper inner counter is too low; raising only that boundary by `0.03H` will close the join and remove FN.
- **Change:** `scripts/refined.py`, glyph `8`, inner contour only. The value is isolated as `TABUNA_PILOT_EIGHT`, defaulting to the accepted `0.03`; setting it to `0` reproduces the previous construction.
- **Result:** mean Ink IoU increased to `0.927026 / 0.927888 / 0.928482`. At 64 pt glyph `8` improved `0.837489 → 0.852335`; FN fell `279 → 217`, while FP rose `192 → 212`. The largest FP regions did not grow beyond the existing side artifacts, and no other glyph changed.
- **Validation:** full audit at 32/64/128 pt passed; the repeat audit was identical. The accepted default was rebuilt without an environment override and reproduced the same metrics.
- **Decision:** ACCEPTED. The change closes the specific upper-counter topology mismatch; it does not globally thicken or scale the glyph.

## Iteration 065 — `Q` tail topology (rejected)

- **Baseline:** accepted iteration 064, mean Ink IoU `0.927026 / 0.927888 / 0.928482` at 32/64/128 pt; `Q` at 64 pt `0.784409`, FP `252`, FN `479`.
- **Selection:** `Q` was the highest-error glyph; its FN was concentrated at the tail attachment and right join.
- **Hypothesis:** replace the existing quadrilateral tail with an independent SFNS-like tail contour attached around `0.286H`.
- **Result:** 32 pt `0.927026 → 0.927000`, 64 pt `0.927888 → 0.927863`, 128 pt `0.928482 → 0.928457`. At 64 pt `Q` fell `0.784409 → 0.781182`; FP rose `252 → 337`, although FN fell `479 → 429`. A new connected FP region of `169 px` appeared around the tail.
- **Decision:** REJECTED. Reduced FN was outweighed by a larger independent FP and global IoU regression. The accepted `8` version was rebuilt and the full repeated audit restored the iteration 064 metrics exactly.

## Iteration 066 — `6` upper-curve control (rejected)

- **Baseline:** accepted iteration 064, mean Ink IoU `0.927026 / 0.927888 / 0.928482`.
- **Selection:** glyph `6` had IoU `0.782356` and a `168 px` connected FN component in the upper bowl at 64 pt.
- **Hypothesis:** move the upper curve control from `w*.72` to `w*.78` to restore the missing right-side stroke.
- **Result:** 32 pt `0.927026 → 0.926996`, 64 pt `0.927888 → 0.927859`, 128 pt `0.928482 → 0.928454`. Glyph `6` at 64 pt fell `0.782356 → 0.778720`; FP rose `178 → 192` while FN changed only `449 → 446`.
- **Decision:** REJECTED. The node shift widened the right wall without removing the connected FN topology. Source was restored and the full repeated audit returned the iteration 064 metrics exactly.

## Iteration 067 — `Ф` ring thickness (rejected)

- **Baseline:** accepted iteration 064, mean Ink IoU `0.927026 / 0.927888 / 0.928482`.
- **Selection:** `Ф` had IoU `0.819892` at 64 pt and repeated FN along both outer arcs, with the same BBox as the reference.
- **Hypothesis:** the ring is too thin; multiply only its ring thickness by `1.08`.
- **Result:** 32 pt `0.927026 → 0.926784`, 64 pt `0.927888 → 0.927651`, 128 pt `0.928482 → 0.928245`. At 64 pt `Ф` fell `0.819892 → 0.796590`; FP rose `94 → 160`, while FN only fell `489 → 479`. New connected FP regions reached `43 px`.
- **Decision:** REJECTED. The mismatch is curvature/shape rather than uniform ring thickness. Source was restored and the full repeated audit returned iteration 064 exactly.

## Iteration 068 — `Э` inner-counter depth (accepted)

- **Baseline:** accepted iteration 064, mean Ink IoU `0.927026 / 0.927888 / 0.928482` at 32/64/128 pt. Glyph `Э` had IoU `0.821555` at 64 pt, FN `405`, with two large connected components (`206 px` and `172 px`) and an exact BBox match.
- **Diagnosis:** row-wise masks showed that the reference closes the inner counter before the lower/upper return, while the current contour leaves a hole open through the return. This is a topology/depth error, not a global thickness or position error.
- **Hypothesis:** move the inner floor upward and inner ceiling downward by `0.02H`, shrinking only the inner counter of uppercase `Э`.
- **Change:** `scripts/design.py`, one local inner-contour group. The value is isolated as `TABUNA_PILOT_E_COUNTER_SHRINK`, defaulting to the accepted `0.02`; setting it to `0` reproduces the previous construction.
- **Result:** mean Ink IoU increased to `0.927652 / 0.928508 / 0.929108`. At 64 pt `Э` improved `0.821555 → 0.868054`; FN fell `405 → 271`, FP stayed `87`. No other glyph changed.
- **Validation:** full audit at 32/64/128 pt passed; repeat audit was identical. The accepted default was rebuilt without an environment override and produced the same metrics.
- **Decision:** ACCEPTED. The change closes the specific counter topology mismatch without global scaling or independent glyph edits.

## Iteration 069 — `У` upper-diagonal endpoint (accepted)

- **Baseline:** accepted iteration 068, mean Ink IoU `0.927652 / 0.928508 / 0.929108` at 32/64/128 pt. Glyph `У` at 64 pt had BBox `[67,129,140,220]` versus reference `[66,129,138,220]`, with blue excess at the upper-right diagonal endpoint.
- **Hypothesis:** the upper-right endpoint of the second diagonal is too far right; increase its inset from `0.45s` to `0.60s` (a `0.15s` local endpoint shift).
- **Change:** `scripts/design.py`, only glyph `У` and only the upper-diagonal endpoint. The parameter is isolated as `TABUNA_PILOT_U_RIGHT_TOP_INSET`, defaulting to `0.15`; setting it to `0` reproduces the previous construction.
- **Result:** mean Ink IoU increased to `0.927745 / 0.928599 / 0.929197`. At 64 pt `У` improved `0.733337 → 0.744765`; FP fell `178 → 162`, FN fell `358 → 348`, and the right BBox edge aligned `140 → 138`.
- **Validation:** full audit at 32/64/128 pt passed; repeat audit was identical. No other glyph changed. The accepted default was rebuilt without an environment override and produced the same metrics.
- **Decision:** ACCEPTED. The local endpoint correction removes both right-side excess and part of the opposing FN without changing global metrics, stroke scale, or advance width.

## Iteration 070 — `д` left-curve anchor (rejected/no raster effect)

- **Baseline:** accepted iteration 069, mean Ink IoU `0.927745 / 0.928599 / 0.929197`.
- **Selection:** `д` had a `172 px` connected FN component on the left arch at 64 pt, with an exact BBox match.
- **Hypothesis:** shift the left outer-curve anchor from `0.60s` to `0.45s`.
- **Result:** the isolated `−0.15s` change produced identical IoU, FP and FN at 32/64/128 pt; the source-unit move was below the raster quantisation threshold.
- **Decision:** REJECTED. No evidence of improvement; the same hypothesis will not be repeated with blind larger offsets. Source was restored and the full repeated audit returned iteration 069 exactly.


## Iteration 071 — shared stem-diagonal scale (rejected)

- Structural analysis completed before edits; normalized zones, thickness, counters, extrema, tangent/curvature samples and glyph-family exceptions are documented in `GEOMETRY-SYSTEM-REPORT.md` and `build/structural-audit-071/`.
- Main metric is binary micro IoU, not the historical meanInkIoU. Baseline: 0.930586402338 across 32/64/128pt at400; TP1367198, FP23978, FN78003. Baseline full and weight audits reproduced exactly.
- One shared parameter for N/И/и (including inherited Й/й): diagonal horizontal thickness ×1.10 around unchanged centerlines. hmtx/fvar/avar unchanged. Regular micro IoU rose to0.931284068406; FP24269, FN76707.
- Rejected: weight800 micro IoU fell0.892514948049→0.892430303278; FP+284 versus FN−212; и/й regressed and developed large FP components60/59px. Full and weight candidate audits were reproducible;756 reference masks were identical to baseline.
- Restoration audit initially started before checkpoint copying completed; its mixed candidate/baseline output is invalid and preserved in `invalid-restoration-race`. Sequencing was corrected. Both fresh restoration audits match the original baseline in every sizes field; scripts/sources/dist match the input checkpoint byte-for-byte.
- No geometry change accepted. Best valid micro IoU remains0.930586402338. Further automatic improvement is not proven impossible; the shared model needs weight-dependent semantic roles and join compensation, not another blind scalar.


## Iteration 072 — shared weight trajectory of lower bowl extrema (rejected)

- Scope: only з/З/3. Baseline production files retained throughout, SHA256 verified. Model and semantic anchor/tangent roles documented before experiment in build/class-model-072/PLAN-B.md.
- Linear normalized correction p(u)=0.008770475217843632+0.015697884145845015*u, u=clamp((w−100)/700,0,1), b=0. Fitted from measured reference-minus-baseline endpoint means, no pixel search. Separate candidate modifies only three gvar entries; support knot800 realizes clamp without a fitted coefficient.
- Full binary micro IoU0.930586402338→0.930582280101; FP23978→24006, FN78003→77983. All three improve at100, 3 regresses at400, all three regress at800. No other audited glyph changes, no new large FP. Full and weight repeat audits identical;756 reference masks unchanged.
- Decision REJECTED. Quadratic b cannot rescue800 because u(1−u)=0 there. Upper-only A and combined C were not run without a coherent shared correction supported by the maps. No production geometry edit or font installation.
- Independent read-only diagonal diagnostics for к/К/Я/R/4/7 completed afterward, with direction/region roles and separate linear fits. These measurements are not treated as validated join corrections. See CLASS-GEOMETRY-REPORT.md and build/class-model-072/diagonal-classes.json.


### Модель цифры 1

Принята собственная конструкция стойки и полосы между линейными функциями.
Суммарный IoU 18 случаев: 78,75% → 99,79%; регрессий нет, повтор точный.
При 500/16 два FP-пикселя объединились в компоненту размера 2,
при неизменном числе FP и снижении FN с 7 до 0; рассмотрено и принято.
Проверены 63 промежуточных положения без самопересечений и 72 сочетания
цифрового набора без изменения ширин. Сборка: 5136 проверок геометрии,
48 проверок набора, все 189 символов, веса 100–900.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-one-stem`.


### Диагональное семейство — 10 символов

Принята вторая версия общей модели полос и стоек. Первая улучшала все
случаи, но продолжение диагоналей давало выступы за пределами стоек;
эта версия сохранена как непринятая. Аналитическое ограничение полос
устранило выступы без изменения метрик. Суммарный IoU 180 случаев
86,23% → 99,65%; каждый случай улучшен, повтор точный. На весе 100/64
диапазон результатов группы — 98,87–100%. Новые малые FP и удлинение
существующих однопиксельных полос рассмотрены в fp-review-v2.json.
Набор и ширины проверены в 72 случаях, контуры — в 630 положениях.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-diagonal-family`.


### J/j/i — общая модель изгиба и точек

Первая версия исправила изгиб J/j, но оставила смещённую точку j.
Вторая добавила общую модель точки i/j и стойки i, выявив лишний
пиксель по всей высоте стойки i при 800/64. Принята третья версия:
только стойка i хранится с половинной точностью координат; точка
не меняет сетку. Из 54 случаев 53 улучшены, один равен исходному; повтор точный, новых
увеличенных FP-компонент нет. Тонкие 100/64: J 58,87% → 98,80%,
j 60,74% → 99,54%, i 68,82% → 100%. Изменений ширин нет в 72
проверках набора; геометрия вне J/j/i непрерывно неизменна.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-j-hooks`.


### k — отдельная высота стойки в общей модели диагоналей

Измерена геометрия k и добавлена в существующую модель K/К/к.
Вместо нового набора специальных контуров добавлен один параметр:
высота стойки относительно высоты верхних концов диагоналей.
Тонкий вариант 100/64: IoU 56,99% → 99,49%. Регрессий в 18 случаях
нет, повтор точный, новых увеличенных FP-компонент нет. 72 проверки
набора подтверждают прежние ширины и размещение.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-k-bands`.


### ~ — касательная волна

Принята модель из шести кубических дуг со свободными длинами
касательных и общими горизонтальными направлениями в экстремумах.
При 100/64 IoU вырос с 53,23% до 98,12%. Все 18 случаев улучшены,
повтор точный. В восьми случаях появились только изолированные
FP-пиксели, существенно меньше устранённых FN; крупных компонент нет.
72 проверки набора подтверждают прежние ширины и размещение.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-tilde-wave`.


### 6 — повторное использование модели чаши и хвоста

Общий с 9 генератор получил отдельный измеренный набор параметров 6
и поворот системы координат. Внешняя форма и просвет оптимизировались
раздельно по скалярным моментам сечений. Все 18 растровых случаев
улучшены, повтор точный, новых увеличенных FP-компонент нет.
При 100/64 IoU 55,32% → 97,94%. Ширины и размещение сохранены
в 72 проверках цифрового набора, 63 проверки контуров прошли.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-six-bowl`.


### R — чаша и ножка, с сохранением оптической R в ®

Первый кандидат улучшил R, но проверка воздействия обнаружила
непредусмотренное изменение registered: символ использовал обычную R.
Принята вторая версия, сохраняющая отдельно настроенную маленькую
букву в ®. Повторный строгий impact подтвердил изменение только R.
Все 18 случаев улучшены, повтор точный, роста FP-компонент нет.
Тонкий 100/64: IoU 56,07% → 99,28%. 72 проверки набора подтверждают
прежние ширины и размещение; 63 проверки самопересечений прошли.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-r-bowl`.


### Ф/ф — овалы со стойкой

Принята общая конструкция двух овалов и вертикальной стойки.
Профили измерены отдельно, формы подобраны по моментам сечений.
36 растровых случаев улучшены, повтор точный, роста FP-компонент нет.
Тонкий 100/64: Ф 68,02% → 98,17%, ф 62,61% → 98,75%.
72 проверки набора подтвердили прежние ширины и размещение.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-phi-bowls`.


### Э/э — открытая дуга с перекладиной

`scripts/e_reversed.py` переиспользует общие кубические уравнения
`open_rounds.contours` в отражённой системе координат. Перекладина
измерена отдельно. Для плотных начертаний добавлены независимые
высоты внутренних концов, позволяющие наклонные срезы. Направление
отражённых контуров нормализует общий Drawing.replay; дополнительный
разворот не применяется. Проверка знака площадей подтверждает
одинаковое направление дуги и перекладины во всех 12 профилях.
36 повторяемых случаев улучшены без регрессий и роста FP-компонент.
При 100/64: Э 62,70% → 97,85%; э 73,35% → 97,50%. 126 проверок
самопересечений и 72 проверки набора прошли. Остаточные отличия
срезов и плотных начертаний сохраняются; полный шрифт не завершён.
Доказательства: `build/font-recovery/e-reversed/decision.json`.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-e-reversed`.


### ∞ — касательные петли и каплевидные просветы

`scripts/infinity_ribbon.py` строит внешний силуэт восемью кубическими
дугами и каждый просвет четырьмя. Стороны измеряются отдельно;
симметрия не навязывается. Внешний силуэт и просветы подбираются
раздельно по скалярным моментам сечений. 72 проверки подтверждают
G1 в плавных соединениях исходных профилей. Центральные углы
пересечения и концы просветов исключены из этого утверждения;
глобальная G2-гладкость не заявляется.
Все 18 повторяемых случаев улучшены. При 100/64: 63,90% → 98,57%.
В 500/16 появился один FP-пиксель, при снижении FN с 14 до 4;
новых крупных компонент нет. 63 проверки внутри и между контурами
прошли, 72 проверки набора подтвердили прежние ширины.
Доказательства: `build/font-recovery/infinity-ribbon/decision.json`.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-infinity-ribbon`.


### 8 — касательные петли и два овальных просвета

`scripts/eight_bowls.py` переиспользует касательные дуги петель
из infinity_ribbon в повёрнутой системе координат. Размеры верхней
и нижней частей независимы. Два просвета используют общую модель
четырёх кубических дуг rounds.contour. Внешний силуэт и просветы
подобраны раздельно по моментам сечений.
Все 18 повторяемых случаев улучшены, без регрессий и роста FP.
Тонкий 100/64: 64,05% → 95,73%. 63 проверки внутри и между
контурами прошли, 72 проверки набора подтвердили прежние ширины.
Соединение петель сохраняет остаточные отличия и требует дальнейшего
уточнения; эта версия не считается окончательной геометрией всей гарнитуры.
Доказательства: `build/font-recovery/eight-bowls/decision.json`.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-eight-bowls`.


### T / Г / г — стойки и верхние перекладины

`scripts/top_bars.py` строит единый ортогональный контур из границ
стойки, высоты и толщины перекладины. Это линейный частный случай
параметрической геометрии, без лишних управляющих точек.
Скалярные измерения хранятся в `sources/top-bars.json`; исходные вершины
эталона не используются генератором. 18 профилей проверены по 301 сечению.
Для тонкой Г предусмотрено уменьшение толщины перекладины на 0,5/1000 em,
линейно исчезающее к весу 400: оно устраняет расхождение покрытия
в стыке при нативной растеризации. Базовое измерение и поправка разделены.
Уточнение сетки до половины и четверти единицы оказалось бесполезным
и отклонено; дополнительные глифы не добавлены.
Все 54 повторяемых случая прошли без регрессий; при 100/64 маски
всех трёх букв совпали с эталоном. Два новых FP — одиночные пиксели T,
при сокращении FN с 30 и 517 до нуля. 189 проверок пересечений и
72 проверки набора прошли. Это конечная выборка, не доказательство
полного совпадения всех размеров или готовности всей гарнитуры.
Доказательства: `build/font-recovery/top-bars/decision.json`.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-top-bars`.


### V / v / w / M / М / м — диагональные полосы и оптические соединения

`scripts/folded_bands.py` задаёт каждую границу штриха уравнением
x(y) = a·y + b. Толщина может линейно меняться по высоте.
Соседние штрихи разделяются наклонной линией между внутренними
границами: это сохраняет асимметрию, не создавая щелей и выступов.
Горизонтальные соединения измеряются по высоте открытия просвета.
У строчной м отдельно учитывается поднятая нижняя вершина.
Исходные вершины эталона не используются генератором.

36 профилей сравнивались по 501 горизонтальному сечению; базовая
аналитическая модель совпала с ними в пределах 1e-7 единицы.
При сравнении объединяются только численные щели меньше 1e-8.
108 нативных повторяемых случаев улучшены без регрессий.
В 100/64 совпадение масок выросло с 66,7–73,6% до 99,2–99,9%.
378 проверок внутри контуров и 72 проверки набора прошли.
Пересечения между полосами и соединительными прямоугольниками намеренные.

Только левая стойка М экспортируется с половинной единицей точности:
обычная сетка давала полосу FP 1×66 на 500/64. Уточнение всего глифа
создавало FN на правой стойке при 500/16 и отклонено.
В окончательной версии новые FP-компоненты — только одиночные пиксели.
Два служебных глифа добавлены после прежних идентификаторов;
теперь 218 глифов при прежних 189 Unicode-символах.
Это конечная проверка, не доказательство равенства всем размерам
или завершения всей гарнитуры.
Доказательства: `build/font-recovery/folded-bands/decision.json`.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-folded-bands`.


### Z / z — диагональ с оптическими соединениями

`scripts/z_bands.py` строит единый контур из двух перекладин,
двух линейных границ диагонали и коротких вертикальных участков
в соединениях. Угол и изменение толщины задаются коэффициентами
x(y) = a·y + b; пересечения с перекладинами вычисляются аналитически.
Исходные вершины эталона не используются генератором.
12 профилей проверены по 501 сечению, расхождение меньше 1e-7 единицы.
Все 36 нативных повторяемых случаев улучшены, без регрессий
и роста FP-компонент. На 100/64: Z 71,53% → 99,89%,
z 71,77% → 99,85%. 126 проверок пересечений и 72 проверки
набора прошли; ширины и остальные глифы сохранены.
Готовность всей гарнитуры этим не подтверждается.
Доказательства: `build/font-recovery/z-bands/decision.json`.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-z-bands`.


### r — плечо из касательных кубических дуг

`scripts/r_shoulder.py` строит по три кубические дуги для внешней
и внутренней границы плеча. В промежуточных точках и вершинах
сохранены общие касательные; внутренняя дуга плавно соединяется
с вертикальной стойкой. Вершина, стойка и срез измерены скалярно,
форма дуг подобрана по моментам горизонтальных и вертикальных сечений.
Генератор не использует вершины исходного контура эталона.

Для текстового мастера 400 внутренняя граница плеча опущена на
5/1000 em: это оптическая компенсация покрытия на 16 pt.
Поправка отделена от измерений, равна нулю в крайних весах
и display-профилях, между мастерами интерполируется.
Перемещение сохраняет касательные и форму самих дуг.

17 повторяемых случаев улучшены, один (400/16) сохранил прежнюю
точную бинарную маску. Регрессий и роста FP-компонент нет.
На 100/64 совпадение выросло с 68,29% до 99,54%.
24 стыка дуг и 6 соединений со стойкой проверены на G1;
63 положения проверены на пересечения, 72 проверки набора прошли.
Это конечная проверка, не доказательство глобального оптимума
подбора или готовности всей гарнитуры.
Доказательства: `build/font-recovery/r-shoulder/decision.json`.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-r-shoulder`.


### Ё / ё — самостоятельная геометрия диакритических точек

`scripts/yo_dots.py` сохраняет базовую букву и задаёт две точки
измеренными размерами и положением. Каждая использует общую
модель `quadratic_round`: восемь касательных квадратичных дуг,
точно представленных в кубической форме. Нормализованные параметры
подобраны по моментам сечений, без переноса исходных вершин.
96 наборов параметров четвертей проверены на допустимую область.

Все 36 повторяемых случаев улучшены без регрессий.
На 100/64: Ё 93,88% → 100%, ё 88,32% → 94,18%.
Остаточные ошибки строчной е остаются отдельной задачей.
Новые FP-компоненты — только одиночные пиксели, при сильном
уменьшении FN. 126 проверок пересечений и 72 проверки набора прошли.

Старый некодируемый uni0308 сохраняется как зависимость контура,
чтобы сохранить идентификаторы всех 218 глифов. Он не добавляется
к публичной cmap или к правилам позиционирования. Специализированный
Subsetter использует стадии закреплённой версии FontTools;
проверка impact подтверждает байтовую неизменность таблиц раскладки
и остальных глифов. Unicode-набор остаётся равным 189 символам.
Доказательства: `build/font-recovery/yo-dots/decision.json`.
Checkpoint: `build/font-recovery/checkpoints/checkpoint-yo-dots`.
