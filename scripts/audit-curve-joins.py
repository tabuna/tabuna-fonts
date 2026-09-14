"""Audit authored cubic joins before TrueType approximation and rounding.

Corners are reported separately, never forced smooth. Curvature jump is
multiplied by the glyph bounding-box diagonal to remove scale dependence.
This is a diagnostic, not a claim that a small jump proves visual quality.
"""
import json
from math import atan2, degrees, hypot
from pathlib import Path
from types import SimpleNamespace
from bezier import curvature, derivatives
from parameters import at_location
import five_bowl, el_stem, y_tail, ya_bowl, de_stem

ROOT = Path(__file__).resolve().parents[1]


def contours(drawing):
    segments = []
    for op, args in drawing.pen.value:
        if op == 'moveTo':
            start = current = args[0]
        elif op in ('lineTo', 'curveTo'):
            end = args[-1]
            if op == 'lineTo':
                delta = tuple(end[i]-current[i] for i in (0, 1))
                curve = (current, tuple(current[i]+delta[i]/3 for i in (0, 1)),
                         tuple(current[i]+2*delta[i]/3 for i in (0, 1)), end)
            else:
                curve = (current, *args)
            if current != end or op == 'curveTo':
                segments.append((op, curve))
            current = end
        elif op == 'closePath':
            if current != start:
                delta = tuple(start[i]-current[i] for i in (0, 1))
                segments.append(('lineTo', (current,
                    tuple(current[i]+delta[i]/3 for i in (0, 1)),
                    tuple(current[i]+2*delta[i]/3 for i in (0, 1)), start)))
            yield segments
            segments = []


def audit(drawing):
    paths = list(contours(drawing))
    points = [p for path in paths for _, curve in path for p in curve]
    scale = hypot(*(max(p[i] for p in points)-min(p[i] for p in points) for i in (0, 1)))
    result = []
    for ci, path in enumerate(paths):
        for ji, ((a, left), (b, right)) in enumerate(zip(path, path[1:]+path[:1])):
            if a == b == 'lineTo':
                continue
            u, v = derivatives(left, 1)[0], derivatives(right, 0)[0]
            if min(hypot(*u), hypot(*v)) < 1e-9:
                result.append(dict(contour=ci, join=ji, kind='stationary'))
                continue
            angle = abs(degrees(atan2(u[0]*v[1]-u[1]*v[0], u[0]*v[0]+u[1]*v[1])))
            k1, k2 = curvature(left, 1), curvature(right, 0)
            result.append(dict(contour=ci, join=ji, kind='smooth' if angle < .01 else 'corner',
                               angle_degrees=angle, curvature_jump=abs(k1-k2)*scale,
                               point=left[-1]))
    return result


def main():
    families = [('five', five_bowl, five_bowl.load())]
    families += [(key, el_stem, data) for key, data in el_stem.load().items()]
    families += [(key, y_tail, data) for key, data in y_tail.load().items()]
    families += [(key, ya_bowl, data) for key, data in ya_bowl.load().items()]
    families += [(key, de_stem, data) for key, data in de_stem.load().items()]
    rows = []
    for key, module, masters in families:
        for weight in (100, 250, 400, 650, 900):
            for optical in (0, .5, 1):
                params = at_location(masters, SimpleNamespace(weight=weight, display=optical))
                for row in audit(module.construction(params)):
                    rows.append(dict(glyph=key, weight=weight, display=optical, **row))
    smooth = sorted((r for r in rows if r['kind']=='smooth'), key=lambda r:r['curvature_jump'], reverse=True)
    report = dict(scope='Source cubic joins, 15 parameter locations per family; corners classified, not repaired.',
                  locations=len(families)*15, joins=len(rows), smooth_joins=len(smooth),
                  stationary_joins=sum(r['kind']=='stationary' for r in rows),
                  worst_smooth_joins=smooth[:30], joins_detail=rows)
    path = ROOT/'proofs/curves/joins.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='joins_detail'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
