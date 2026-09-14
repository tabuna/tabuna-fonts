# Локальная структурная проверка системного шрифта

Проверен установленный `/System/Library/Fonts/SFNS.ttf` только для анализа
конструктивной логики. Файл не копируется в `dist` и его контуры не
подключаются к production-коду.

Команда:

```sh
./.venv/bin/python scripts/inspect-local-font.py \
  /System/Library/Fonts/SFNS.ttf --chars 'кКЯзЗ53' \
  --out build/system-font-inspection/sfns-structure.json
```

SFNS — TrueType `glyf`, 2048 UPM, с четырьмя вариационными осями: `wdth`,
`opsz`, `GRAD`, `wght`. Структура выбранных glyphs:

| glyph | contours | points | on/off | наблюдаемая логика |
|---|---:|---:|---:|---|
| `к` | 1 | 14 | 14/0 | один линейный упорядоченный контур |
| `К` | 1 | 14 | 14/0 | стержень, верхнее плечо, waist-notch, нижнее плечо |
| `Я` | 2 | 26 | 17/9 | внешний контур + отдельная внутренняя чаша |
| `з` | 1 | 55 | 26/29 | непрерывный криволинейный контур с quadratic handles |
| `З` | 1 | 58 | 26/32 | непрерывный криволинейный контур с overshoot |
| `5` | 1 | 46 | 21/25 | верхняя полка, плечо и нижняя чаша в одном контуре |
| `3` | 1 | 60 | 26/34 | две чаши, общая талия и overshoot |

Эти данные объясняют, почему для `К` перекрывающиеся полигоны давали большие
FN/FP: эталон использует один ordered contour. В production добавлена
независимая реконструкция с округлёнными относительными пропорциями; исходные
SFNS-точки не импортируются.

Для повторной проверки соседней группы на весовых мастерах используй:

```sh
./.venv/bin/python scripts/inspect-variable-neighbors.py \
  --chars 'аябвжз5З3' --weights 100,400,800 \
  --out build/system-font-inspection/variable-neighbors.json
```

Сводка нормализованных движений узлов сохранена в
`build/system-font-inspection/neighbor-variation-analysis.txt`, а полный
структурный вывод — в
`build/system-font-inspection/variable-neighbors.json`. Интерпретация
инвариантов и проверка общего параметра находятся в
`build/system-font-inspection/GEOMETRY-SYSTEM-AUDIT.md`.
