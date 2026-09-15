# Independent Cyrillic/editorial review

Scoped pass for authored Russian UI and short editorial body text; no evidence-backed Cyrillic outline defect found. Integration conditions remain.

Font SHA-256: `5888eecc912f46f14b7807906d2ffc0a42d543a3695465b76a83b699373344b9`. WOFF2 SHA-256: `9c5c23886f3cac3acca41e9db66bdde9a69e5145453e1a84e24605bc31b43e59`. Intentional cmap: 189 characters.

No existing audit reports or verdicts read. Only current binaries, self-contained proof images and proof generators inspected. Pillow/FreeType native pixel proofs; current cmap inspected with fontTools. Own Russian accent/quote/currency proof generated. No browser/CoreText or reader study performed.

## P2 — Bullet and per-mille become misleading hollow ovals without fallback

Source proof strings contain U+2022 bullet and U+2030 per-mille. Both are absent from cmap; direct Pillow rendering shows a hollow zero-like placeholder, while ₽ € $ £ and № render normally. This is not a Cyrillic drawing defect. Define explicit approved content/fallback behavior for these characters; test actual browser fallback. Intentional 189-character scope need not expand.

Evidence: `build/independent-audit-20260915/type/heading-detail-opsz128.png`, `build/independent-audit-20260915/type/ui-native-opsz14.png`.

## P2 — Russian money grouping needs nonbreaking content

At 18 px the 400 and 500 body samples break the amount after 1, placing 250 ₽ on the next line. The proof uses ordinary spaces; this is a wrapping/content issue, not bad font spacing. U+00A0 is supported, U+202F is absent. Use supported NBSP for 1 250 ₽ or a no-wrap amount span, and verify narrow layouts.

Evidence: `build/independent-audit-20260915/type/body-native.png`.

## P3 — Precomposed Russian accents look sound; decomposed input needs policy

Ё/ё and Й/й are present with clear marks in the viewed 14–48 px proofs. Combining U+0308 and U+0306 are absent. This does not prove browser failure because shaping may normalize; raw direct renderers and fallback paths need separate verification. Normalize authored Russian copy to NFC where appropriate; test pasted decomposed е+diaeresis and и+breve in supported clients before promising unrestricted user-text support.

Evidence: `build/independent-audit-20260915/cyrillic-editor/ru-editor-proof.png`, `build/independent-audit-20260915/type/14px-detail-nearest2x.png`.

## Cyrillic assessment

Russian/Latin color and size feel compatible in 14–18 px 400/500 body samples. Russian has naturally more repeated verticals but no conspicuous patch of alien weight. Л/Д retain recognizable forms; Ж/К/Я and lowercase а/в read consistently in body and headings. No observed collision or malformed join warrants an outline change. Guillemets, nested low/high quotes, ₽ and common Western currency signs are present and coherent. Ё/й marks remain separate in inspected proofs. The restrained, upright Cyrillic texture is utilitarian rather than expressive; preference for a more humanist Л/Д is taste, not demonstrated failure.

## Scoped use and remaining verification

14–18 px, wght 400; 500 for stronger labels; start with 1.4–1.5 line height. 14–20 px, wght 400–500 with authored NFC Russian copy and explicit fallback policy. 24–48 px, wght 400–700; proof each intended optical-size setting. Do not infer unrestricted multilingual/user-input coverage or platform-wide small-text quality from these Pillow proofs.

Safari/CoreText and Chromium at 1x/2x with actual font-loading and fallback stacks.; NBSP amount wrapping, nested quotes, Ё/й clipping at actual CSS line height, decomposed pasted accents.; Confirm unsupported bullet/per-mille and narrow NBSP preserve semantics under actual fallback..
