"use strict";
const $ = (id) => document.getElementById(id);
const initialText = $("sample-text").value;
const controls = ["size", "weight", "optical", "auto-optical", "compare"];
function update() {
  const size = $("size").value;
  const weight = $("weight").value;
  const optical = $("optical").value;
  const auto = $("auto-optical").checked;
  $("size-value").textContent = `${size} px`;
  $("weight-value").textContent = weight;
  $("optical-value").textContent = auto ? "Авто" : `${optical} pt`;
  $("optical").disabled = auto;
  $("comparison").hidden = !$("compare").checked;
  for (const target of [$("sample-text"), $("system-sample")]) {
    target.style.fontSize = `${size}px`;
    const body = $("sample-role").value === "body";
    target.style.lineHeight = body ? "1.6" : Number(size) < 24 ? "1.45" : "1.17";
    target.style.letterSpacing = Number(size) < 24 || body ? "0" : "-.018em";
    target.style.fontWeight = weight;
    target.style.fontOpticalSizing = auto ? "auto" : "none";
    target.style.fontVariationSettings = auto ? "normal" : `"opsz" ${optical}`;
  }
  $("system-sample").textContent = $("sample-text").value;
  $("sample-text").style.height = "auto";
  $("sample-text").style.height = `${Math.min($("sample-text").scrollHeight, Number(size) * 14)}px`;
}
$("sample-role").addEventListener("change", () => {
  const preset = {ui: [16, 500], body: [18, 400], display: [64, 400]}[$("sample-role").value];
  $("size").value = preset[0];
  $("weight").value = preset[1];
  $("auto-optical").checked = true;
  update();
});
$("ui-save").addEventListener("click", () => {
  $("ui-feedback").textContent = "Настройки образца сохранены.";
});
controls.forEach((id) => $(id).addEventListener("input", update));
$("sample-text").addEventListener("input", update);
$("reset").addEventListener("click", () => {
  $("sample-role").value = "display";
  $("size").value = matchMedia("(max-width:620px)").matches ? "40" : "64";
  $("weight").value = "400";
  $("optical").value = "14";
  $("auto-optical").checked = true;
  $("compare").checked = false;
  $("sample-text").value = initialText;
  update();
});
if (matchMedia("(max-width:620px)").matches) $("size").value = "40";
update();
document.fonts.load('400 24px "Tabuna Sans"', "Ясность").then((faces) => {
  $("font-status").textContent = faces.length ? "Tabuna Sans загружен" : "Шрифт недоступен: показан системный";
}).catch(() => { $("font-status").textContent = "Шрифт недоступен: показан системный"; });

const charset = window.TABUNA_CHARSET || [];
function drawGlyphs() {
  const mode = $("glyph-filter").value;
  const chars = charset.filter(({character: c}) => {
    const n = c.codePointAt(0);
    if (mode === "basic") return /[A-Za-zА-Яа-яЁё]/u.test(c);
    if (mode === "latin") return /[A-Za-z]/u.test(c);
    if (mode === "cyrillic") return n >= 0x400 && n <= 0x45F;
    if (mode === "signs") return !/\p{Letter}|\p{Mark}|\p{Separator}|\p{Other}/u.test(c);
    return true;
  });
  const fragment = document.createDocumentFragment();
  for (const {character, codepoint, name} of chars) {
    const cell = document.createElement("div");
    cell.className = "glyph";
    cell.title = `${codepoint} ${name}`;
    const letter = document.createElement("b");
    // A system dotted circle would hide which font draws a combining mark.
    letter.textContent = /\p{Mark}/u.test(character) ? `a${character}` : character;
    const code = document.createElement("small");
    code.textContent = codepoint;
    cell.append(letter, code);
    fragment.append(cell);
  }
  $("glyph-grid").replaceChildren(fragment);
  $("glyph-count").textContent = `${chars.length} символов в разделе`;
}
$("glyph-filter").addEventListener("change", drawGlyphs);
if (charset.length) {
  drawGlyphs();
} else {
  $("glyph-filter").disabled = true;
  $("glyph-count").textContent = "Не удалось загрузить набор символов. Обновите страницу.";
}

function updateGlyphWeight() {
  const weight = $("glyph-weight").value;
  $("glyph-weight-value").textContent = weight;
  $("glyph-grid").style.setProperty("--glyph-weight", weight);
}
$("glyph-weight").addEventListener("input", updateGlyphWeight);
updateGlyphWeight();
