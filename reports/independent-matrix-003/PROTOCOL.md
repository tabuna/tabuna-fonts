# Protocol — independent matrix 003

Frozen local distribution: Tabuna Sans 0.0.3. Exact source/demo/font hashes are in `snapshot.json`. Font or demo changes are outside this audit. The GitHub 0.0.1 control release is a separate artifact.

Ten first-review roles: OpenType engineering, type design, Apple HIG/accessibility perspective, Cyrillic editorial design, numeric UI/data, screen reading, application UI, rasterization, character, release engineering. Each received a fresh context, was told not to read other/previous reviews, and produced its own first report. These are agent roles from one model family, not ten people, Apple employees or an endorsement by Apple/Steve Matteson. Shared tools and common model biases limit independence.

First reports are SHA-256 locked in `initial-locks.json` before cross-critique. Critiques are separate artifacts; initial findings and mistakes remain visible. The coordinating agent may read all evidence and adjudicates recommendations against the explicit 189-character contract. Passes apply only to the tested conditions.

Two reviewers inspect `build/matrix003/blind.png` before the identity key or others' reviews. X/Y row order alternates across pairs; pairs 1/5 and 2/6 repeat the same UI text in the same per-pair order. This is a repeat consistency check, not full randomized counterbalancing. Identities are revealed only after both blind first reports are locked. Two labels, one supplied rasterizer and a few strings cannot establish human recognition or reading performance. The coordinator knows the key and is not counted as a blind assessor.

Root checks supplement the ten reports: partial OpenType feature ranges, exact Unicode coverage, and narrow-viewport enlarged-text reflow. No aggregated percentage of suitability or statistically independent vote count is calculated.

Final adjudication separates: reproduced font defects; demo/integration failures; intended repertoire limits; aesthetic observations; evidence required before stronger product claims. Long-session reading requires real participants; agent impressions cannot close that requirement. Native Apple behavior must be tested separately from FreeType rendering or a CSS root-size simulation.
