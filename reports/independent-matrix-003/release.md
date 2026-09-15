# Independent release engineering audit — Tabuna Sans 0.0.3

TTF SHA-256: `56cb3cbd30099ed97b0395e7eae28f9431e84ff9eede14cdfb4061f1c5873edc`.

Independent of prior and peer reviewer reports. Inspected current binaries, public claims, build/cache source and permitted release-gate status. No font/source edits or dist build.

## Results

- Metadata/manifest match: 311,328-byte TTF, 93,320-byte WOFF2 (91.13 KiB), 218 glyphs, exactly 189 encoded characters matching the declared charset in both formats.
- Version 0.0.3; wght 100–900 (default 400), opsz 9–128 (default 14), nine named weights. GSUB calt/liga/pnum/tnum and GPOS kern are present.
- All nine discovered versioned cache references match current asset hashes.
- Eight cache and gate tests passed after supplying `PYTHONPATH=scripts`; initial test discovery lacked that import path.
- README accurately reports packaging and explicitly limits 0.0.3 to pilot use with participant and platform evaluation incomplete.
- Main build source uses local geometry/source data; no direct SFNS/Inter read observed. Full dependency provenance and byte-reproducible rebuilding were outside this read-only audit.

## Finding P1 — authorial release readiness remains blocked

Current authorial release gate rejects this exact TTF: all D01–D06 pending and authorial deviations unverified. Technical and numeric audit failure arrays are empty; baseline criterion has 160 cases below 95% across 37 characters.

Recommendation: Retain pilot-only positioning and complete exact-hash decision evidence before promoting an authorial-ready release. Do not equate raster similarity with reading performance.

Acceptance: python -m font_recovery.design_status --require authorial exits 0 for this exact approved artifact, with complete hashed evidence and no pending decisions.

The gate currently exits 1. Its baseline checkpoint is verified; baseline readiness and authorial readiness are false. Ordinary `build-web.sh` does not invoke the authorial gate, consistent with documented separation of building from release approval.

## Scoped verdicts

UI, headings and body: **conditional pilot**, solely from packaging and release engineering. No visual or usability endorsement.

Sustained reading: **not established**. No human reading study or Apple endorsement is supplied or implied.

Evidence: `scratchbuild/matrix003/release/artifact-inspection.json`; structured tests, precise gate output, findings and limits are in `release.json`.
