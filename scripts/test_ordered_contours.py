"""Numerical regressions for raster coordinate and topology preservation."""
import unittest
import numpy as np
from ordered_contours import isocontours, fit_compatible_sections, bezier, contour_distances


class RasterGeometryTests(unittest.TestCase):
    def test_pixel_origin_survives_crop(self):
        ink = np.zeros((40, 60))
        ink[12:23, 31:45] = 1
        contour, = isocontours(ink)
        np.testing.assert_allclose(contour.min(axis=0), [31, 12])
        np.testing.assert_allclose(contour.max(axis=0), [45, 23])

    def test_hole_and_disconnected_shapes_stay_separate(self):
        ink = np.zeros((50, 60))
        ink[5:25, 5:25] = 1
        ink[10:20, 10:20] = 0
        ink[30:40, 40:50] = 1
        loops = isocontours(ink)
        self.assertEqual(len(loops), 3)
        self.assertTrue(all(len(c) >= 4 for c in loops))

    def test_joint_fit_preserves_correspondence_and_shape(self):
        t = np.linspace(0, np.pi/2, 150)
        a = np.c_[30*np.cos(t), 40*np.sin(t)]
        b = np.c_[20*np.cos(t), 55*np.sin(t)]
        fitted = fit_compatible_sections([(a, None, None), (b, None, None)], [.2, .2])
        self.assertEqual(len(fitted[0]), len(fitted[1]))
        for original, curves in zip((a, b), fitted):
            rendered = np.vstack([bezier(np.array(c['points']), np.linspace(0, 1, 500)) for c in curves])
            self.assertLess(contour_distances(original, rendered)['hausdorff'], .35)
            for x, y in zip(curves, curves[1:]):
                np.testing.assert_allclose(x['points'][-1], y['points'][0])


if __name__ == '__main__': unittest.main()
