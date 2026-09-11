"""Ordered isocontours and bounded cubic fitting, from raster coverage only.

Pixel values live at pixel centres. Shared marching-squares edges are keyed
explicitly; row-major boundary pixels are never treated as an ordered path.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import nnls
from scipy.spatial import cKDTree


def isocontours(ink, threshold=0.5):
    yy, xx = np.where(ink >= threshold)
    if len(xx) == 0:
        return []
    x0, y0 = max(0, int(xx.min())-1), max(0, int(yy.min())-1)
    x1, y1 = min(ink.shape[1], int(xx.max())+2), min(ink.shape[0], int(yy.max())+2)
    ink = ink[y0:y1, x0:x1]
    points, adjacent = {}, {}
    height, width = ink.shape
    for y in range(height - 1):
        for x in range(width - 1):
            values = [ink[y, x], ink[y, x+1], ink[y+1, x+1], ink[y+1, x]]
            inside = [v >= threshold for v in values]
            if all(inside) or not any(inside):
                continue
            vertices = [(x+.5, y+.5), (x+1.5, y+.5),
                        (x+1.5, y+1.5), (x+.5, y+1.5)]
            keys = [('h', x, y), ('v', x+1, y), ('h', x, y+1), ('v', x, y)]
            crossed = []
            for e in range(4):
                j = (e+1) % 4
                if inside[e] == inside[j]:
                    continue
                t = (threshold-values[e])/(values[j]-values[e])
                points[keys[e]] = np.array(vertices[e])*(1-t)+np.array(vertices[j])*t
                crossed.append(e)
            if len(crossed) == 2:
                pairs = [crossed]
            else:
                # Asymptotic decider for the two possible saddle connections.
                centre_inside = np.mean(values) >= threshold
                pairs = [[(i-1) % 4, i] for i in range(4) if inside[i] != centre_inside]
            for a, b in pairs:
                a, b = keys[a], keys[b]
                adjacent.setdefault(a, []).append(b)
                adjacent.setdefault(b, []).append(a)
    assert all(len(v) == 2 for v in adjacent.values()), 'Open or branched contour'
    remaining = set(adjacent)
    loops = []
    while remaining:
        start = min(remaining)
        previous, current = None, start
        loop = []
        while True:
            loop.append(points[current])
            remaining.discard(current)
            nxt = next(p for p in adjacent[current] if p != previous)
            previous, current = current, nxt
            if current == start:
                break
        loop = np.array(loop)
        if len(loop) >= 4:
            loops.append(loop+[x0, y0])
    return sorted(loops, key=lambda p: abs(signed_area(p)), reverse=True)


def signed_area(points):
    other = np.roll(points, -1, axis=0)
    return float(np.sum(points[:, 0]*other[:, 1]-other[:, 0]*points[:, 1])/2)


def bezier(points, t):
    t = np.asarray(t)[:, None]
    return (1-t)**3*points[0]+3*t*(1-t)**2*points[1]+3*t*t*(1-t)*points[2]+t**3*points[3]


def unit(vector):
    return vector/max(np.linalg.norm(vector), 1e-10)


def tangent(points, at_start):
    pts = points if at_start else points[::-1]
    distance = np.linalg.norm(pts-pts[0], axis=1)
    selected = pts[distance <= 3.0]
    if len(selected) < 3:
        return unit(pts[min(2, len(pts)-1)]-pts[0])
    # A quadratic local regression is less biased than a long secant.
    u = np.r_[0, np.cumsum(np.linalg.norm(np.diff(selected, axis=0), axis=1))]
    c = np.linalg.lstsq(np.c_[u, u*u], selected-selected[0], rcond=None)[0]
    return unit(c[0])


def fit_cubic(points, left_tangent, right_tangent):
    lengths = np.r_[0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    u = lengths/max(lengths[-1], 1e-10)
    start, end = points[0], points[-1]
    for _ in range(8):
        b0, b1, b2, b3 = (1-u)**3, 3*u*(1-u)**2, 3*u*u*(1-u), u**3
        target = points-(b0+b1)[:, None]*start-(b2+b3)[:, None]*end
        matrix = np.stack([b1[:, None]*left_tangent, b2[:, None]*right_tangent], axis=-1)
        alpha, _ = nnls(matrix.reshape(-1, 2), target.ravel())
        alpha = np.minimum(alpha, lengths[-1])
        curve = np.array([start, start+alpha[0]*left_tangent, end+alpha[1]*right_tangent, end])
        value = bezier(curve, u)
        du = 3*((1-u)[:, None]**2*(curve[1]-curve[0])+2*(u*(1-u))[:, None]*(curve[2]-curve[1])+u[:, None]**2*(curve[3]-curve[2]))
        ddu = 6*((1-u)[:, None]*(curve[2]-2*curve[1]+curve[0])+u[:, None]*(curve[3]-2*curve[2]+curve[1]))
        numerator = np.sum((value-points)*du, axis=1)
        denominator = np.sum(du*du+(value-points)*ddu, axis=1)
        step = numerator/np.maximum(denominator, 1e-8)
        u = np.maximum.accumulate(np.clip(u-step, 0, 1))
    errors = np.linalg.norm(bezier(curve, u)-points, axis=1)
    return curve, errors


def fit_section(points, left_tangent=None, right_tangent=None, tolerance=.4, depth=0):
    left_tangent = tangent(points, True) if left_tangent is None else left_tangent
    right_tangent = tangent(points, False) if right_tangent is None else right_tangent
    chord = points[-1]-points[0]
    if np.linalg.norm(chord) > 0:
        u = np.clip(((points-points[0])@chord)/(chord@chord), 0, 1)
        line_error = np.linalg.norm(points-points[0]-u[:, None]*chord, axis=1)
        if max(line_error) <= tolerance*.5:
            return [{'kind': 'line', 'points': [points[0].tolist(), points[-1].tolist()]}]
    curve, errors = fit_cubic(points, left_tangent, right_tangent)
    if max(errors) <= tolerance or len(points) < 7 or depth >= 3:
        return [{'kind': 'cubic', 'points': curve.tolist(), 'maxFitErrorPixels': float(max(errors))}]
    # Add a node only at the largest measured contour discrepancy.
    split = int(np.argmax(errors[2:-2]))+2
    middle = unit(points[split+1]-points[split-1])
    return (fit_section(points[:split+1], left_tangent, -middle, tolerance, depth+1)
            + fit_section(points[split:], middle, right_tangent, tolerance, depth+1))


def contour_distances(reference, rendered):
    a = cKDTree(rendered).query(reference)[0]
    b = cKDTree(reference).query(rendered)[0]
    return {'referenceToRender': float(a.mean()), 'symmetricMean': float((a.mean()+b.mean())/2),
            'hausdorff': float(max(a.max(), b.max()))}


def fit_compatible_sections(sections, tolerances, depth=0):
    """Split all masters at the worst measured error in any one master.

    Each section is (ordered samples, initial tangent or None, final tangent
    or None). The result has identical cubic topology in every master.
    """
    fitted = []
    for points, lt, rt in sections:
        lt = tangent(points, True) if lt is None else lt
        rt = tangent(points, False) if rt is None else rt
        curve, errors = fit_cubic(points, lt, rt)
        fitted.append((curve, errors, lt, rt))
    worst = max(range(len(fitted)), key=lambda i: max(fitted[i][1])/tolerances[i])
    curve, errors, _, _ = fitted[worst]
    if max(errors) <= tolerances[worst] or depth >= 4 or min(len(p) for p, _, _ in sections) < 7:
        return [[{'kind': 'cubic', 'points': c.tolist(), 'maxFitErrorPixels': float(max(e))}] for c, e, _, _ in fitted]
    points = sections[worst][0]
    index = int(np.argmax(errors[2:-2]))+2
    arcs = np.r_[0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    fraction = arcs[index]/arcs[-1]
    left, right = [], []
    for (points, _, _), (_, _, lt, rt) in zip(sections, fitted):
        arcs = np.r_[0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
        index = int(np.argmin(abs(arcs/arcs[-1]-fraction)))
        index = int(np.clip(index, 2, len(points)-3))
        middle = unit(points[index+1]-points[index-1])
        left.append((points[:index+1], lt, -middle))
        right.append((points[index:], middle, rt))
    a = fit_compatible_sections(left, tolerances, depth+1)
    b = fit_compatible_sections(right, tolerances, depth+1)
    return [x+y for x, y in zip(a, b)]
