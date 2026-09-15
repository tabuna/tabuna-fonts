# Независимая оценка доступности Tabuna Sans

Conditional candidate for Regular/Medium UI and short body text; promising display hierarchy. Not enough evidence for broad accessible-font or sustained-reading certification. No blanket HIG certification.

Роль: независимый рецензент, использующий рекомендации Apple; не сотрудник Apple и не реальный приглашённый дизайнер. Предыдущие вердикты и отчёты не читались. Проверены текущие TTF, CSS, HTML, JS и продуктовые утверждения README. Исходники шрифта не изменены.

## Образец и пределы проверки

TTF SHA-256: `5888eecc912f46f14b7807906d2ffc0a42d543a3695465b76a83b699373344b9`

WOFF2 SHA-256: `9c5c23886f3cac3acca41e9db66bdde9a69e5145453e1a84e24605bc31b43e59`

macOS/web RU/EN; synthetic FreeType 1x/2x light/dark screening. No real-device browser, CoreText, VoiceOver, zoom/reflow or human reading test.

Новые изображения получены Pillow/FreeType из отдельных инстансов текущего TTF. 2x означает удвоенную плотность растра при том же логическом размере; это не тест на Retina/CoreText. Значения opsz заданы явно; точность выбора auto браузером здесь не проверена. PNG в просмотрщике может масштабироваться. Длительное чтение, удобство слабовидящих и работа VoiceOver по таким изображениям не доказуемы.

## Что уже выглядит убедительно

- Fresh 14–18 px Regular specimens have visible diacritics and readable short RU/EN strings in both high-contrast themes.
- I/l/1 use distinguishable constructions; O/0 have different widths.
- 24–48 px 500–650 headings sustain clear size/weight hierarchy in the short specimens.
- All six audited demo text/background pairs exceed 4.5:1 nominal sRGB contrast; this is not an all-page accessibility pass.
- CSS uses font-display:swap, system fallback and optical-sizing:auto; HTML has real text, headings, input labels and a status role.

Контраст в демо, рассчитанный из авторских sRGB цветов: light-text 15.06:1, light-muted 5.57:1, light-muted-surface 5.14:1, dark-text 14.73:1, dark-muted 8.28:1, dark-muted-surface 7.07:1. Это проверка сочетаний цвета, а не обещание, что тонкий штрих будет читаться.

## Замечания

### A11Y-01 · high · Thin is too fragile for small functional text

**Условие:** 12 px, wght 100, opsz 9, 1x and 2x FreeType; light #20221f/#f8f8f4 and dark #f0f2e9/#1c1f1b

**Наблюдение:** Fresh specimens show much fainter Thin strokes and diacritics than 400/500 under identical colors. Demo permits 12 px and wght 100; README lists the entire 100–900 range without role limits. Thin availability itself is valid.

**Последствие:** Reduced visibility for small labels, especially low vision and weaker displays.

**Рекомендация:** Use 400–600 as the initial functional UI range. Reserve 100–300 for large display experiments with independent reading checks. Do not market all weights as interchangeable for small UI.

**Основание:** Explicit Apple guidance generally discourages light weights and advises larger sizes for thin custom fonts. Exact Tabuna ranges are reviewer inference.

**Приёмка:** On macOS Safari and Chrome at native 1x/2x, compare 12/14/16 px, 400/500/600, automatic opsz in both themes. Recruit readers including low vision; record character/label errors against system-ui. Keep Thin out of essential-label defaults.

**Уверенность:** high for specimen; medium for real-device impact. Категория: conditional deployment risk, not a malformed font.

Источники: [Official guidance 1](https://developer.apple.com/design/human-interface-guidelines/typography).

### A11Y-02 · medium · Small-text specimen inherits display tracking and tight leading

**Условие:** Demo #sample-text and #system-sample at 12–18 px, wght 400, automatic opsz, either theme: letter-spacing -0.018em and line-height 1.17 remain fixed as size changes.

**Наблюдение:** demo.css rule and demo.js update() set font size, weight and opsz but do not change tracking/leading. Reading article separately uses 1rem/1.65 and normal inherited tracking.

**Последствие:** The live small-size sample does not represent a neutral body/UI baseline; tight multi-line specimen can bias readability comparisons.

**Рекомендация:** Offer text/UI/display presets; begin body comparisons with normal tracking and roughly 1.5–1.65 line-height, then evaluate rhythm. These are test defaults, not universal accessibility minimums.

**Основание:** Apple requires contextual legibility. WCAG text-spacing values describe supported user overrides, not required author defaults.

**Приёмка:** Compare same RU/EN passages with normal tracking versus -0.018em at 12/14/16/18 px. Apply simultaneously 1.5 line-height, 2em paragraph spacing, 0.12em tracking and 0.16em word spacing; no content/function loss. Test user overrides in a real browser.

**Уверенность:** high code evidence; untested runtime consequence. Категория: demo and integration coverage.

Источники: [Official guidance 1](https://developer.apple.com/design/human-interface-guidelines/typography), [Official guidance 2](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html).

### A11Y-03 · medium · The font package cannot establish text enlargement or native accessibility behavior

**Условие:** All sizes/weights/opsz and themes in downstream web/native integrations; demo hero uses nowrap, specimen JS uses pixel sizes and a height cap with scrolling.

**Наблюдение:** dist/tabuna.css supplies @font-face, fallback stack and optical-sizing only. README offers CSS but no native scalable text example. No native integration was supplied for this independent review.

**Последствие:** Font users could mistake variable axes or TTF installation for support of accessibility settings.

**Рекомендация:** Document application responsibility: web zoom and spacing/reflow tests; platform-appropriate adjustable text and emphasis. For future iOS apps use scalable custom font APIs and preserve Bold Text behavior. Do not transfer an iOS size table to macOS.

**Основание:** Explicit Apple custom-font accessibility guidance. Dynamic Type platform list does not include macOS in the inspected typography text. WCAG resize-text applies to web content, not a font binary.

**Приёмка:** In web deployment verify 200% text enlargement without loss; inspect 320 CSS px reflow and user-spacing overrides. In target native app test available text-size and emphasis settings. For iOS additionally test every supported Dynamic Type accessibility category. Retain hierarchy and complete labels.

**Уверенность:** high about evidence gap. Категория: release acceptance gap; not a proven conformance failure.

Источники: [Official guidance 1](https://developer.apple.com/design/human-interface-guidelines/typography), [Official guidance 2](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html), [Official guidance 3](https://developer.apple.com/documentation/uikit/scaling-fonts-automatically).

### A11Y-04 · medium · Distinct I/l/1 does not establish all-code legibility

**Условие:** 12–16 px wght 400/500 opsz 9–12, both themes, 1x/2x; tokens containing O/0, Cyrillic З/digit 3 and Latin rn/m.

**Наблюдение:** Fresh specimens show identifiable I bars, l silhouette and 1 flag; O and 0 differ in width. З and 3 remain visually close. No timed transcription, randomized string test or low-vision participant test was conducted.

**Последствие:** People reading IDs, recovery codes and mixed alphanumeric data have less context than prose readers.

**Рекомендация:** Run randomized token transcription before using the font for critical codes. Keep a user-selectable or role-specific alternative if error rates are worse than system-ui. Do not alter normal Cyrillic homographs merely to make a global distinction claim.

**Основание:** Reviewer inference from contextual legibility; Apple specifies legibility, not particular glyph constructions.

**Приёмка:** Blind randomized RU/EN task: Il1, O0, З3, В8, Б6, rn/m, cl/d embedded in tokens at 12/14/16 px and 400/500. Compare error rate and time to system-ui at equal CSS size and at matched apparent size. Pre-register acceptable non-inferiority margins.

**Уверенность:** medium. Категория: task-specific legibility risk.

Источники: [Official guidance 1](https://developer.apple.com/design/human-interface-guidelines/typography).

### A11Y-05 · medium · Short clean samples do not validate sustained body reading

**Условие:** Proposed body use 16–18 px, wght 400, text opsz/auto, 1.5–1.65 leading; headings 24–48 px 500–650; light/dark.

**Наблюдение:** Current page provides two short RU paragraphs; independent raster sheet includes short RU/EN labels, not sustained reading. cmap has 189 codepoints and no U+0300–036F combining marks, so accented/stressed or borrowed words may require fallback. No true italic is provided.

**Последствие:** Long reading comfort, mixed-font fallback rhythm, emphatic text, and language pronunciation cannot be inferred from contour checks.

**Рекомендация:** Describe body suitability as provisional. Test multi-page RU/EN text, real emphasis and fallback combinations, and allow text size/spacing/font choices. Keep text selectable with correct language/semantics for assistive readers.

**Основание:** Reviewer evidence limit; accessibility belongs to the whole reading experience. A font has no inherent VoiceOver certification.

**Приёмка:** Run 15–20 minute randomized crossover reading sessions with RU and EN readers; record comprehension, speed, discomfort and preferences. Include stress marks, decomposed/precomposed sequences, foreign names and fallback. Check VoiceOver reading order/language in the final app, not in PNGs.

**Уверенность:** high about untested scope. Категория: claim limitation.

Источники: [Official guidance 1](https://developer.apple.com/design/human-interface-guidelines/typography), [Official guidance 2](https://developer.apple.com/design/human-interface-guidelines/accessibility).

## Практическое решение

Approve only a bounded pilot: UI 14–16px/400–600, body 16–18px/400, headings 24px+/500–650, auto opsz and normal tracking as starting test presets; these are reviewer-selected starting points, not Apple mandates or proven universal safe thresholds.

Сохранить автоматический оптический размер. В отдельном стресс-примере 16px/opsz128 строка плотнее, чем 16px/opsz12; display-инстанс не следует фиксировать для мелкого текста. Это управляемое условие применения, не дефект самого диапазона оси.

## Доказательства и происхождение рекомендаций

Official Apple pages were JS-only when opened. Current search-indexed official Apple typography and scaling-fonts text retrieved on 2026-09-15, with indexed crawl age up to two months. Bundled HIG references used as routing notes. WCAG pages opened directly. No numeric Apple minimum-size table claimed.

Apple прямо рекомендует проверять читаемость нестандартных шрифтов, избегать лёгких весов для мелкого текста и реализовывать доступность в приложении. Предложенные диапазоны Tabuna, тесты ошибок и чтения — выводы рецензента. WCAG 1.4.12 не предписывает стартовый line-height 1.5: он проверяет сохранность контента при пользовательских изменениях интервалов.

- [specimen-dark-2x.png](/Users/tabuna/math-design/tabuna-fonts/build/independent-audit-20260915/accessibility/specimen-dark-2x.png)
- [specimen-light-1x.png](/Users/tabuna/math-design/tabuna-fonts/build/independent-audit-20260915/accessibility/specimen-light-1x.png)
- [specimen-light-2x.png](/Users/tabuna/math-design/tabuna-fonts/build/independent-audit-20260915/accessibility/specimen-light-2x.png)
- [specimen-dark-1x.png](/Users/tabuna/math-design/tabuna-fonts/build/independent-audit-20260915/accessibility/specimen-dark-1x.png)
