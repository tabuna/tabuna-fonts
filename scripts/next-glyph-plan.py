#!/usr/bin/env python3
"""Choose the next glyph from geometry-audit.json without changing source files."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('audit', nargs='?', default='build/highlight-audit/geometry-audit.json')
    ap.add_argument('--size', default='64')
    ap.add_argument('--chars', help='optional allow-list of characters')
    ap.add_argument('--top', type=int, default=12)
    ap.add_argument('--out', default='build/highlight-audit/next-glyph-plan.json')
    args = ap.parse_args()
    data = json.loads(Path(args.audit).read_text())
    block = data['sizes'][str(args.size)]
    allow = set(args.chars) if args.chars else None
    rows = []
    for row in block['records']:
        ch = row['character']
        if allow is not None and ch not in allow:
            continue
        fn = sum(int(x['area']) for x in row.get('fnComponents', []))
        fp = sum(int(x['area']) for x in row.get('fpComponents', []))
        lf = int(row.get('fnComponents', [{}])[0].get('area', 0)) if row.get('fnComponents') else 0
        lp = int(row.get('fpComponents', [{}])[0].get('area', 0)) if row.get('fpComponents') else 0
        bbox = row.get('bboxDelta', [0, 0, 0, 0])
        td = abs(float(row.get('thickness', {}).get('deltaMean', 0)))
        boundary = row.get('boundary', {}).get('refToRender', {})
        boundary_p95 = float(boundary.get('p95', 0))
        # Large connected errors get more weight than isolated antialias pixels.
        priority = (fn + fp) * (1.0 + max(lf, lp) / max(fn + fp, 1))
        if boundary_p95 <= 1 and max(lf, lp) <= 3:
            priority *= 0.05
        if any(bbox):
            priority *= 1.1
        diagnosis = row.get('diagnosis', [])
        if any('смещение' in d or 'масштаб' in d for d in diagnosis) and any(bbox):
            group, hypothesis = 'bbox', 'локальное положение контура отличается от эталона'
        elif any('толщина' in d for d in diagnosis) and td > 0.8 and max(lf, lp) < 0.25 * max(fn + fp, 1):
            group, hypothesis = 'thickness', 'штрих систематически тоньше или толще при совпадающем BBox'
        elif lf >= lp:
            group, hypothesis = 'outer-geometry', 'крупная связная FN-компонента указывает на недостающий внешний сегмент'
        else:
            group, hypothesis = 'connection-or-inner-geometry', 'крупная FP-компонента указывает на неверное соединение или внутренний контур'
        rows.append({
            'character': ch, 'priority': round(priority, 3), 'iou': row.get('iou'),
            'fp': row.get('fp'), 'fn': row.get('fn'), 'largestFN': lf,
            'largestFP': lp, 'bboxDelta': bbox, 'boundaryP95': boundary_p95,
            'parameterGroup': group, 'hypothesis': hypothesis,
        })
    rows.sort(key=lambda x: x['priority'], reverse=True)
    result = {'size': str(args.size), 'source': str(Path(args.audit)), 'candidates': rows[:args.top]}
    if rows:
        result['selected'] = rows[0]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
