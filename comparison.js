"use strict";
const el = (id) => document.getElementById(id);
let report;
let requestNumber = 0;
function show() {
  if (!report) return;
  const row = report.records.find((r) => r.character === el("character").value) || report.records[0];
  const dir = `proofs/pixel-${el("point-size").value}/`;
  for (const [id, file] of [["own",row.tabuna.file],["system",row.system.file],["diff",row.difference]]) {
    el(`${id}-image`).src = dir + file;
    el(`${id}-download`).href = dir + file;
    el(`${id}-image`).style.width = `${report.canvas[0] * Number(el("zoom").value)}px`;
    el(`${id}-image`).style.height = `${report.canvas[1] * Number(el("zoom").value)}px`;
    el(`${id}-image`).parentElement.style.height = `${Math.min(report.canvas[1] * Number(el("zoom").value),360)}px`;
  }
  const zoom=Number(el("zoom").value);
  const bounds=row.system.inkBounds;
  const centerX=report.originPixels[0]+(bounds[0]+bounds[2]/2)*report.pixelScale;
  const centerY=report.originPixels[1]-(bounds[1]+bounds[3]/2)*report.pixelScale;
  for (const panel of document.querySelectorAll('.pixel-scroll')) {
    panel.scrollLeft=Math.max(0,centerX*zoom-panel.clientWidth/2);
    panel.scrollTop=Math.max(0,centerY*zoom-panel.clientHeight/2);
  }
  el("exact").textContent = row.exactMatch ? "Да" : "Нет";
  el("pixel-count").textContent = row.differentPixels.toLocaleString("ru-RU");
  el("overlap").textContent = `${(row.inkIoU * 100).toFixed(1)}%`;
  el("advance").textContent = `${row.advanceDifference > 0 ? "+" : ""}${row.advanceDifference.toFixed(2)} pt`;
  el("comparison-status").textContent = `${row.character} · ${row.codepoint} · Пиксели: ${report.exactMatches}/${report.total}. Пиксели и ширина: ${report.completeMatches ?? 0}/${report.total}` + (row.referenceFallback || row.customFallback ? " · Внимание: использован запасной шрифт" : "");
  el("protocol").textContent = `${report.renderer}. ${report.os}. ${report.pointSize} pt, ${report.pixelScale}×, вес ${report.weight}, opsz ${report.customOpticalSize}. Эталон: ${report.systemPostScriptName}. Начало набора и базовая линия: ${report.originPixels.join(", ")} px. Сглаживание: ${report.antialias}.`;
  el("report-link").href = dir + "comparison.json";
}
async function load() {
  const request = ++requestNumber;
  const selected = el("character").value;
  const size = el("point-size").value;
  el("comparison-status").textContent = "Загрузка изображений…";
  try {
    const response = await fetch(`proofs/pixel-${size}/comparison.json`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (request !== requestNumber) return;
    report = data;
    document.querySelector('.pixel-panels').hidden=false;
    document.querySelector('.pixel-metrics').hidden=false;
    el("character").replaceChildren(...report.records.map((row) => {
      const option = document.createElement("option");
      option.value = row.character; option.textContent = `${row.character} · ${row.codepoint}`;
      return option;
    }));
    if (report.records.some((r) => r.character === selected)) el("character").value = selected;
    show();
  } catch {
    if (request !== requestNumber) return;
    report = undefined;
    document.querySelector('.pixel-panels').hidden=true;
    document.querySelector('.pixel-metrics').hidden=true;
    el("comparison-status").textContent = "Измерения этого размера пока не созданы. Выберите другой размер или запустите render-pairs.swift.";
  }
}
el("character").addEventListener("change",show);
el("zoom").addEventListener("change",show);
el("point-size").addEventListener("change",load);
for (const [id,step] of [["previous",-1],["next",1]]) el(id).addEventListener("click",() => {
  const select=el("character");if (!select.options.length) return;
  select.selectedIndex=(select.selectedIndex+step+select.options.length)%select.options.length;
  show();
});
load();
