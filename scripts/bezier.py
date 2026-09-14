"""Shared cubic Bézier geometry: endpoints, tangent directions and tensions.

B(t) = (1-t)^3 P0 + 3(1-t)^2 t P1 + 3(1-t)t^2 P2 + t^3 P3.
A common tangent direction gives G1 continuity. C1 additionally requires
matching derivative lengths; neither condition alone guarantees equal curvature.
"""
from math import hypot


def unit(x, y):
    length = hypot(x, y)
    if not length:
        raise ValueError('A tangent needs a nonzero direction')
    return x / length, y / length


def tangent_arc(start, end, departure, arrival, handles, bounded=False):
    """Return cubic controls and endpoint from two unit tangents and tensions."""
    span = hypot(end[0] - start[0], end[1] - start[1])
    a, b = [span * h for h in handles]
    if bounded:
        def reach(direction):
            return max(0, min([span] + [
                (end[i] - start[i]) / direction[i]
                for i in (0, 1) if abs(direction[i]) > 1e-10]))
        a, b = min(a, reach(departure) * .999), min(b, reach(arrival) * .999)
    return ((start[0] + departure[0] * a, start[1] + departure[1] * a),
            (end[0] - arrival[0] * b, end[1] - arrival[1] * b), end)


def point(curve, t):
    """Evaluate a cubic at 0 <= t <= 1."""
    u = 1 - t
    return tuple(u**3 * curve[0][i] + 3*u*u*t * curve[1][i]
                 + 3*u*t*t * curve[2][i] + t**3 * curve[3][i] for i in (0, 1))


def derivatives(curve, t):
    u = 1 - t
    first = tuple(3*(u*u*(curve[1][i]-curve[0][i])
                    + 2*u*t*(curve[2][i]-curve[1][i])
                    + t*t*(curve[3][i]-curve[2][i])) for i in (0, 1))
    second = tuple(6*(u*(curve[2][i]-2*curve[1][i]+curve[0][i])
                     + t*(curve[3][i]-2*curve[2][i]+curve[1][i])) for i in (0, 1))
    return first, second


def curvature(curve, t):
    velocity, acceleration = derivatives(curve, t)
    speed = hypot(*velocity)
    if speed <= 1e-12:
        raise ValueError('Curvature is undefined at a stationary point')
    return (velocity[0]*acceleration[1]-velocity[1]*acceleration[0]) / speed**3


def bowl_side(q, top, side, bottom):
    """Four cubics around a bowl side, with shared tangents and bounded handles."""
    a=(side[0]+(top[0]-side[0])*q['upper_x'],side[1]+(top[1]-side[1])*q['upper_y'])
    b=(side[0]+(bottom[0]-side[0])*q['lower_x'],side[1]+(bottom[1]-side[1])*q['lower_y'])
    sign=1 if side[0]>top[0] else -1
    u=unit(sign,-q['upper_slope']);v=unit(-sign,-q['lower_slope'])
    tangents=[(sign,0),u,(0,-1),v,unit(-sign,-q['end_slope'])]
    points=[top,a,side,b,bottom]
    return [tangent_arc(points[i],points[i+1],tangents[i],tangents[i+1],q['handles'][i],bounded=True) for i in range(4)]
