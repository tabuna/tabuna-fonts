"""Geometric invariants of the shared cubic model."""
import unittest
from math import sqrt
from bezier import point, derivatives, curvature, tangent_arc


class BezierTests(unittest.TestCase):
    def test_endpoints_and_tangent_derivatives(self):
        curve=((0,0),)+tangent_arc((0,0),(1,1),(1,0),(0,1),(.3,.4))
        self.assertEqual(point(curve,0),curve[0])
        self.assertEqual(point(curve,1),curve[3])
        self.assertEqual(derivatives(curve,0)[0][1],0)
        self.assertEqual(derivatives(curve,1)[0][0],0)

    def test_quarter_circle_curvature(self):
        k=4*(sqrt(2)-1)/3
        curve=((1,0),(1,k),(k,1),(0,1))
        for t in [0,.25,.5,.75,1]:
            self.assertLess(abs(curvature(curve,t)-1),.025)

    def test_bounded_controls_stay_inside(self):
        for end in [(1,2),(-2,-1)]:
            sign=1 if end[0]>0 else -1
            controls=tangent_arc((0,0),end,(sign,0),(0,sign),(8,8),bounded=True)
            for p in controls:
                for i in [0,1]:self.assertTrue(min(0,end[i])<=p[i]<=max(0,end[i]))


if __name__=='__main__':unittest.main()
