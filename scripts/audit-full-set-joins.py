"""Audit source curve joins across the compact character set, before TTF rounding.

Reports intentional corners separately. Sampling is not a proof over the entire
variation domain; tangent continuity alone does not establish visual quality.
"""
import argparse
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from build import Source
from design import Design
from geometry import Drawing

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('curve_join_audit', ROOT/'scripts/audit-curve-joins.py')
join_audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(join_audit)


class CubicCollector(BasePen):
    """Decompose components and elevate each quadratic exactly to a cubic."""
    def __init__(self, glyphs):
        super().__init__(glyphs)
        self.drawing = Drawing()

    def _moveTo(self, point):
        self.drawing.pen.moveTo(point)

    def _lineTo(self, point):
        self.drawing.pen.lineTo(point)

    def _curveToOne(self, first, second, end):
        self.drawing.pen.curveTo(first, second, end)

    def _qCurveToOne(self, control, end):
        start = self._getCurrentPoint()
        first = tuple(start[i]+2*(control[i]-start[i])/3 for i in (0, 1))
        second = tuple(end[i]+2*(control[i]-end[i])/3 for i in (0, 1))
        self.drawing.pen.curveTo(first, second, end)

    def _closePath(self):
        self.drawing.pen.closePath()

    def _endPath(self):
        self.drawing.pen.endPath()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    font = TTFont(ROOT/'dist/TabunaSansVariable.ttf')
    characters = sorted(font.getBestCmap())
    rows, empty = [], []
    for weight in (100, 250, 400, 650, 900):
        for optical in (16, 22, 28):
            source = Source(400, optical)
            source.d = Design(weight, optical)
            glyphs = [(cp, source.ensure(chr(cp))) for cp in characters]
            for cp, glyph in glyphs:
                pen = CubicCollector(source.f)
                glyph.draw(pen)
                paths = list(join_audit.contours(pen.drawing))
                if not any(paths):
                    empty.append(dict(codepoint=f'U+{cp:04X}', weight=weight, optical=optical))
                    continue
                for item in join_audit.audit(pen.drawing):
                    path = paths[item['contour']]
                    left = path[item['join']][0]
                    right = path[(item['join']+1) % len(path)][0]
                    rows.append(dict(character=chr(cp), codepoint=f'U+{cp:04X}',
                                     weight=weight, optical=optical,
                                     curve_to_curve=left == right == 'curveTo', **item))
            print(f'{weight}/{optical}: {len(glyphs)} characters', flush=True)
    curves = [r for r in rows if r['curve_to_curve']]
    findings = [r for r in curves if r['kind'] != 'smooth']
    report = dict(characters=len(characters), locations_per_character=15,
                  glyph_locations=len(characters)*15, empty_locations=empty,
                  joins=len(rows), curve_to_curve_joins=len(curves),
                  non_smooth_curve_joins=findings,
                  worst_curvature_jumps=sorted((r for r in curves if r['kind']=='smooth'),
                    key=lambda r:r['curvature_jump'], reverse=True)[:100],
                  scope='Own source geometry at five weights and three optical sizes. Components decomposed; quadratics exactly elevated. Intentional corners and degenerate compatibility nodes need interpretation. No whole-domain smoothness or visual-quality claim.',
                  joins_detail=rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('characters','glyph_locations','joins','curve_to_curve_joins')}))
    print(f'Non-smooth curve-to-curve joins: {len(findings)}')


if __name__ == '__main__':
    main()
