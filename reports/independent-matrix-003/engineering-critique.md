# Release engineering cross-critique

The initial independent release report is unchanged. This second phase reads engineering.md, data.md, feature-ranges.json and permitted historical timer documentation.

**Timer closure is supported** for TTF `56cb3cbd30099ed97b0395e7eae28f9431e84ff9eede14cdfb4061f1c5873edc`. A fresh full `check_timers.py` rerun passed 220,896 context checks at 117 axis locations, 110,448 format comparisons and 234 equal-width timer groups. This corroborates the independent shaping and numeric-data reports. The root partial-range report adds 11,760 passing checks at 24 locations; that harness was reviewed, not independently rerun here.

**Simultaneous pnum/tnum is an integration condition (P3), not an observed font defect.** Direct HarfBuzz checks at400/14 reproduce proportional precedence with both features on. Explicit tnum=1,pnum=0 produces ten identical 1286-unit advances. Engineering's restrained wording is justified; conflicting callers should be corrected, rather than reopening timer closure. Acceptance: verify equal digit advances and invariant timer-cycle widths in the actual application's renderer under exclusive tabular settings. No cross-engine universal precedence claim is warranted.

**Authorial readiness is still blocked (P1), while binary checks pass.** Pending D01–D06 and unverified deviations are release-evidence gaps. They do not imply corrupt fonts or a failed timer repair; passing binary checks do not close them. Keep pilot positioning until `design_status --require authorial` succeeds for complete exact-hash evidence.

Retain the full timer regression in build-web and its current-hash, minimum-coverage, zero-failure release gate. Separately require actual browser/native numeric rendering, fallback and real-content checks before wider product deployment. The data review supports numeric UI in its scoped weights/sizes; it cannot establish general prose or sustained-reading performance.

Fresh evidence is in `scratchbuild/matrix003/release/timer-rerun.json`. This cross-critique did not repeat historical0.0.2 failures, inspect historical raster images, run CoreText/browser rendering or perform reader studies. All axis tests are discrete samples. No Apple or human endorsement is asserted.
