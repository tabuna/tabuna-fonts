"""Known smooth and corner constructions validate the source-join diagnostic."""
import importlib.util
from pathlib import Path
import unittest
from geometry import Drawing

spec = importlib.util.spec_from_file_location('joins', Path(__file__).with_name('audit-curve-joins.py'))
joins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(joins)


class JoinTests(unittest.TestCase):
    def test_circle_quarters_have_matching_curvature(self):
        d = Drawing()
        d.ellipse(0, 0, 200, 200)
        rows = joins.audit(d)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(r['kind']=='smooth' for r in rows))
        self.assertLess(max(r['curvature_jump'] for r in rows), 1e-12)

    def test_tangent_line_can_have_curvature_jump(self):
        d = Drawing()
        d.outline((0, 0), [((1, 0), (2, 1), (2, 2)), (2, 3), (0, 3)])
        rows = joins.audit(d)
        smooth = [r for r in rows if r['kind']=='smooth']
        self.assertEqual(len(smooth), 1)
        self.assertGreater(smooth[0]['curvature_jump'], 1)
        self.assertTrue(any(r['kind']=='corner' for r in rows))


if __name__ == '__main__':
    unittest.main()
