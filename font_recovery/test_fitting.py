"""Analytic checks for winding-aware measurements of overlapping outlines."""
import unittest
import numpy as np
from font_recovery.fitting import scan_moments
from font_recovery.measure import scan


def rectangle(left, right):
    return [(left,0),(left,1),(right,1),(right,0)]


class WindingMeasurements(unittest.TestCase):
    def test_overlap_is_filled(self):
        contours = [rectangle(0,2), rectangle(1,3)]
        # Union is [0,3]: integrals of 1, x and x².
        expected = [3, 9/2, 9]
        np.testing.assert_allclose(scan_moments(contours,[.5],0,1,nonzero=True),expected)
        np.testing.assert_allclose(scan_moments([c[::-1] for c in contours],[.5],0,1,nonzero=True),expected)
        # Parity intentionally preserves its old, different interpretation.
        np.testing.assert_allclose(scan_moments(contours,[.5],0,1),[2,3,20/3])
        self.assertEqual(scan(contours,.5,nonzero=True),[[0.,3.]])

    def test_reversed_counter_removes_ink(self):
        contours = [rectangle(0,3), rectangle(1,2)[::-1]]
        np.testing.assert_allclose(scan_moments(contours,[.5],0,1,nonzero=True),[2,3,20/3])
        self.assertEqual(scan(contours,.5,nonzero=True),[[0.,1.],[2.,3.]])

    def test_vertical_scan_and_empty_levels(self):
        contours = [rectangle(0,2), rectangle(1,3)]
        np.testing.assert_allclose(scan_moments(contours,[1.5,4],0,1,vertical=True,nonzero=True),
                                   [1,.5,1/3,0,0,0])


if __name__ == '__main__':
    unittest.main()
