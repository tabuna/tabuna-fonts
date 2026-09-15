# Data-interface cross-critique

**Accept ENG-001 as P2.** Independently shaped current TTF `12:34`, `00:00`, `99:59` at wght 400 / opsz 14. Default uses `colon.case` with y bounds 205..1239; `tnum` uses `colon` with bounds −10..1024, a 215-unit downward shift (1.47 px at 14 px). `a:b` keeps ordinary colon in both modes. Inspected timer-arbitration.png; the change is visible.

My initial timer **width** pass remains correct but did not test vertical alignment. Its context measurements already recorded the differing colon glyph IDs; I missed their visual consequence. The 960 passes cannot be used as a complete timer visual pass. UI remains conditional; timer headings must also be conditional until this interaction is corrected.

Acceptance: shape numeric timers with tnum on/off across representative axis locations in TTF and WOFF2. Both modes should choose colon.case; prose a:b must retain colon; tabular digit equality and stable timer widths must continue to pass.

**Revise DATA-01 to a P3 integration check.** README explicitly fixes 189 codepoints, prescribes system fallback for missing symbols, and U+00A0 for authored amounts. Missing U+202F/U+2009 is therefore not an in-scope font defect. Reject glyph expansion as a required action. Reject my original font-only “no .notdef” acceptance criterion for these out-of-scope characters.

Replacement acceptance: load actual WOFF2 in the target browser with `font-family: "Tabuna Sans", system-ui, sans-serif`. Render locale amounts with U+202F and U+2009, alongside the documented U+00A0 sample. Check no tofu, fallback rendering, U+202F nonbreaking behavior, and numeric grouping/decimal alignment with tabular-nums at narrow widths. Repeat on target platforms. This test is specified, not executed; fallback success is not claimed.

DATA-02 O/0 similarity remains an identifier-use limitation; a zero alternate is optional future work. DATA-03 weight advice already agrees with README 400–500 guidance and needs no font engineering action. Sustained reading remains unverified.

Initial data.md/json preserved. No font or source edits. The new direct reproduction is one axis location; the engineering report provides the wider grid.
