"""Summarize the current compiled prototype without claiming release readiness."""
import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
RECOVERY = ROOT / 'build/font-recovery'


def metrics(records):
    tp = sum(row['tp'] for row in records)
    fp = sum(row['fp'] for row in records)
    fn = sum(row['fn'] for row in records)
    return {'tp': tp, 'fp': fp, 'fn': fn, 'iou': tp / (tp + fp + fn),
            'dice': 2 * tp / (2 * tp + fp + fn),
            'precision': tp / (tp + fp), 'recall': tp / (tp + fn)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit', type=Path, default=RECOVERY / 'research-v2/audit-shared-cyrillic')
    args = parser.parse_args()
    audit = json.loads((args.audit / 'report.json').read_text())
    assert audit['reproducible']
    font_path = ROOT / audit['font']
    font_hash = hashlib.sha256(font_path.read_bytes()).hexdigest()
    font = TTFont(font_path)
    comparisons = []
    by_weight = {}
    baseline = json.loads((RECOVERY / 'baseline/run-1/report.json').read_text())
    for weight in audit['weights']:
        records = []
        for instance in audit['instances']:
            if instance['weight'] != weight:
                continue
            size = instance['size']
            folder = args.audit / f'wght-{weight}' / str(size)
            settings = json.loads((folder / 'render-settings.json').read_text())
            repeated = json.loads((args.audit / '_repeat' / f'wght-{weight}' / str(size) / 'render-settings.json').read_text())
            assert settings['fontSHA256'] == repeated['fontSHA256'] == font_hash
            original = json.loads((RECOVERY / f'baseline/run-1/{size}/render-settings.json').read_text())
            for key in ['renderer', 'pixelScale', 'canvas', 'originPixels', 'antialias']:
                assert settings[key] == original[key], (weight, size, key)
            for row in settings['records']:
                assert all(name.startswith('TabunaSansDevelopment-Variable') for name in row['tabuna']['renderedFonts'])
            records.extend(instance['records'])
        by_weight[str(weight)] = metrics(records)
        if weight == 400:
            for character in audit['glyphs']:
                previous = [row for size in baseline['sizes'].values()
                            for row in size['records'] if row['character'] == character]
                before = metrics(previous) if previous else None
                after = metrics([row for row in records if row['character'] == character])
                comparisons.append({'character': character, 'baseline_iou': before['iou'] if before else None,
                                    'new_iou': after['iou'],
                                    'delta_iou': after['iou'] - before['iou'] if before else None})
    inventory = json.loads((RECOVERY / 'reports/phase-0-inventory.json').read_text())
    unchanged = all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == value
                    for path, value in inventory['sha256'].items())
    assert unchanged
    validation = json.loads((RECOVERY / 'research-v2/validation.json').read_text())
    assert validation['geometry_checks_passed']
    assert validation['font_sha256'] == font_hash, 'Geometry validation is stale'
    result = {
        'objective': 'Ready Tabuna Sans with concise, understandable construction code',
        'status': 'active development; not release-ready',
        'font': str(font_path), 'font_sha256': font_hash,
        'glyphs_audited': audit['glyphs'], 'unicode_coverage': len(font.getBestCmap()),
        'required_baseline_coverage': 469, 'full_new_audit_iou': None,
        'baseline_full_iou': json.loads((RECOVERY / 'baseline/summary.json').read_text())['totals']['iou'],
        'weights': by_weight, 'per_glyph_regular': comparisons,
        'repeat_audit_identical': True, 'font_fallback_used': False,
        'renderer_settings_preserved': True, 'original_files_unchanged': unchanged,
        'full_release_ready': False,
        'remaining': ['Full 469-character coverage and independent complex templates',
                      'Optical axis and complete weight range', 'Shaping, spacing, kerning and text proofs',
                      'Full 126-character baseline acceptance', 'Final metadata and release packaging'],
    }
    reports = RECOVERY / 'reports'
    (reports / 'progress.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    with (reports / 'progress-per-glyph.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(comparisons[0]))
        writer.writeheader()
        writer.writerows(comparisons)
    lines = ['# Tabuna Sans: текущий прогресс', '',
             '**Работа продолжается; шрифт ещё не готов к выпуску.**', '',
             f"Проверено {len(audit['glyphs'])} символов: `{audit['glyphs']}`. Новый TTF содержит {len(font.getBestCmap())} Unicode-кодов со знаком пробела; исходный продукт — 469.", '',
             '## Проверенный переменный прототип', '',
             '| Вес | IoU набора | TP | FP | FN |', '|---|---:|---:|---:|---:|']
    for weight, row in by_weight.items():
        lines.append(f"| {weight} | {row['iou']:.6f} | {row['tp']} | {row['fp']} | {row['fn']} |")
    lines += ['', 'Все значения суммируют пиксели по размерам 32/64/128. Они относятся только к указанному набору; сравнивать их напрямую с общим baseline 0,930586 нельзя.', '',
              'Два запуска аудита совпали. Проверены хеш фактически отрендеренного TTF, отсутствие fallback и неизменность renderer/canvas/baseline/antialias. Геометрия проверена в девяти весах. Повторные сборки побайтово совпали; WOFF2 проверен после распаковки.', '',
              '## Устройство кода', '',
              '`font_recovery/primitives.py`: чаши, стержни, перекладины, плечи. Все точки выводятся из размеров и отношений касательных.', '',
              '`font_recovery/model.py` и `data/design.json`: модель и параметры, отдельно от измерительного кода.', '',
              '`generate_font.py` и `build_variable.py`: компиляция и совместимое разбиение кривых между мастерами. SFNS и старая геометрия не импортируются.', '',
              'Принципы и команды: `font_recovery/README.md`. Растровая проба: `build/font-recovery/research-v2/specimen.png`.', '',
              '## До выпуска', '']
    lines += [f'- {item}.' for item in result['remaining']]
    lines += ['', 'Рабочий `dist/` не заменён. Сохранён исходный checkpoint-000; новый прототип хранится как эксперимент, не как принятая замена полного шрифта.']
    (reports / 'progress.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'report': str(reports / 'progress.md'), 'audited_glyphs': len(audit['glyphs']),
                      'original_files_unchanged': unchanged}, ensure_ascii=False))


if __name__ == '__main__':
    main()
