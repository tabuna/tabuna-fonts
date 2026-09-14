"""Tabuna Sans geometry: bowls, stems and shoulders.

Every point below is constructed from dimensions and tangent proportions.
There are no imported outlines, glyph-specific point lists or pixel corrections.
"""
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.transformPen import TransformPen


def oval(pen, bounds, kx, ky, counter=False):
    """Four cubic quarters with horizontal and vertical extrema.

kx controls the tangent along the top/bottom; ky controls the side tangent.
The inner contour uses the same rule with its own dimensions and curvature.
    """
    left, bottom, right, top = bounds
    cx, cy = (left + right) / 2, (bottom + top) / 2
    rx, ry = (right - left) / 2, (top - bottom) / 2
    path = RecordingPen()
    path.moveTo((left, cy))
    path.curveTo((left, cy + ky * ry), (cx - kx * rx, top), (cx, top))
    path.curveTo((cx + kx * rx, top), (right, cy + ky * ry), (right, cy))
    path.curveTo((right, cy - ky * ry), (cx + kx * rx, bottom), (cx, bottom))
    path.curveTo((cx - kx * rx, bottom), (left, cy - ky * ry), (left, cy))
    path.closePath()
    path.replay(ReverseContourPen(pen) if counter else pen)


def closed_bowl(pen, p, counter=False):
    """Four extremal anchors and independent tangent proportions per quarter.

    The simpler symmetric oval remains a valid special case. Independent
    quarters let a counter accommodate a neighboring stem without distortion
    of the opposite side.
    """
    if 'tangents' not in p:
        oval(pen, p['bbox'], *p['handles'], counter=counter)
        return
    left, bottom, right, top = p['bbox']
    tx, bx = p['extrema']['top_x'], p['extrema']['bottom_x']
    ly, ry = p['extrema']['left_y'], p['extrema']['right_y']
    tl, tr, br, bl = [p['tangents'][corner] for corner in
                       ('top_left', 'top_right', 'bottom_right', 'bottom_left')]
    path = RecordingPen()
    path.moveTo((left, ly))
    path.curveTo((left, ly+(top-ly)*tl[1]), (tx-(tx-left)*tl[0], top), (tx, top))
    path.curveTo((tx+(right-tx)*tr[0], top), (right, ry+(top-ry)*tr[1]), (right, ry))
    path.curveTo((right, ry-(ry-bottom)*br[1]), (bx+(right-bx)*br[0], bottom), (bx, bottom))
    path.curveTo((bx-(bx-left)*bl[0], bottom), (left, ly-(ly-bottom)*bl[1]), (left, ly))
    path.closePath()
    path.replay(ReverseContourPen(pen) if counter else pen)


def polygon(pen, points):
    """A closed clockwise boundary; callers express points through dimensions."""
    pen.moveTo(points[0])
    previous = points[0]
    for point in points[1:]:
        if point != previous:
            pen.lineTo(point)
        previous = point
    pen.closePath()


def rectangle(pen, left, bottom, right, top):
    polygon(pen, [(left, bottom), (left, top), (right, top), (right, bottom)])


def capital_h(pen, parameters):
    """Two equal stems and a crossbar, expressed as one non-overlapping contour."""
    left, bottom, right, top = parameters['bbox']
    stem = parameters['stem']
    bar_bottom, bar_top = parameters['crossbar']
    polygon(pen, [
        (left, bottom), (left, top), (left + stem, top),
        (left + stem, bar_top), (right - stem, bar_top),
        (right - stem, top), (right, top), (right, bottom),
        (right - stem, bottom), (right - stem, bar_bottom),
        (left + stem, bar_bottom), (left + stem, bottom),
    ])


def stem_and_bars(pen, p):
    """E/F/L: one spine with any number of right-facing horizontal bars."""
    left, bottom, _, top = p['bbox']
    inside = left + p['stem']
    boundary = [(left, bottom), (left, top), (inside, top)]
    for bar in sorted(p['bars'], key=lambda bar: bar['top'], reverse=True):
        boundary.extend([
            (inside, bar['top']), (bar['right'], bar['top']),
            (bar['right'], bar['bottom']), (inside, bar['bottom']),
        ])
    boundary.append((inside, bottom))
    polygon(pen, boundary)


def capital_t(pen, p):
    """A centered stem suspended from a full-width horizontal bar."""
    left, bottom, right, top = p['bbox']
    stem_left, stem_right = p['stem_interval']
    bar_bottom = p['bar_bottom']
    polygon(pen, [
        (left, top), (right, top), (right, bar_bottom),
        (stem_right, bar_bottom), (stem_right, bottom),
        (stem_left, bottom), (stem_left, bar_bottom), (left, bar_bottom),
    ])


def shoulder_n(pen, p):
    """Two stems joined by an arch, with independently shaped inside and outside.

    The left stem can rise above the arch (h). Rotating this construction gives
    u. The crown, stem junctions and tangent lengths are semantic parameters,
    rather than a list of font outline nodes.
    """
    left, bottom, right, _ = p['bbox']
    stem, top = p['stem'], p['arch_top']
    join, shoulder = p['join'], p['shoulder']
    crown, inner_crown = p['crown_x'], p['inner_crown_x']
    inner_top = p['inner_top']
    inner_left, inner_right = p['inner_join'], p['inner_shoulder']
    inside_left, inside_right = left + stem, right - stem

    # Left stem and outer shoulder: leave the stem, reach the crown, turn down.
    pen.moveTo((left, bottom))
    pen.lineTo((left, p['stem_top']))
    pen.lineTo((inside_left, p['stem_top']))
    pen.lineTo((inside_left, join))
    pen.curveTo(
        (inside_left + (crown - inside_left) * p['outer_departure_x'],
         join + (top - join) * p['outer_departure_y']),
        (crown - (crown - inside_left) * p['outer_top_left'], top),
        (crown, top),
    )
    pen.curveTo(
        (crown + (right - crown) * p['outer_top_right'], top),
        (right, shoulder + (top - shoulder) * p['outer_side_right']),
        (right, shoulder),
    )
    pen.lineTo((right, bottom))
    pen.lineTo((inside_right, bottom))
    pen.lineTo((inside_right, inner_right))

    # Return along the counter. Its crown need not align with the outer crown.
    pen.curveTo(
        (inside_right, inner_right + (inner_top - inner_right) * p['inner_side_right']),
        (inner_crown + (inside_right - inner_crown) * p['inner_top_right'], inner_top),
        (inner_crown, inner_top),
    )
    pen.curveTo(
        (inner_crown - (inner_crown - inside_left) * p['inner_top_left'], inner_top),
        (inside_left, inner_left + (inner_top - inner_left) * p['inner_side_left']),
        (inside_left, inner_left),
    )
    pen.lineTo((inside_left, bottom))
    pen.closePath()


def open_bowl(pen, p):
    """C/c: an outside and an inside arch joined by two flat terminal cuts.

    Each arch travels through bottom, left and top extrema. The terminal
    locations control the opening independently of the bowl's curvature.
    """
    def arch(path, profile, lower, upper):
        left, bottom, top = profile['left'], profile['bottom'], profile['top']
        bx, tx, cy = profile['bottom_x'], profile['top_x'], profile['axis_y']
        kx, ky, departure = profile['kx'], profile['ky'], profile['departure']
        back_x, back_y = profile.get('back_kx', kx), profile.get('back_ky', ky)
        lx, ly = lower
        ux, uy = upper
        path.curveTo((lx - (lx-bx)*departure, ly-(ly-bottom)*ky),
                     (bx+(lx-bx)*kx, bottom), (bx, bottom))
        path.curveTo((bx-(bx-left)*back_x, bottom),
                     (left, cy-(cy-bottom)*back_y), (left, cy))
        path.curveTo((left, cy+(top-cy)*back_y),
                     (tx-(tx-left)*back_x, top), (tx, top))
        path.curveTo((tx+(ux-tx)*kx, top),
                     (ux-(ux-tx)*departure, uy+(top-uy)*ky), (ux, uy))

    lower, upper = p['lower_terminal'], p['upper_terminal']
    pen.moveTo(tuple(lower['outer']))
    arch(pen, p['outer'], lower['outer'], upper['outer'])
    pen.lineTo(tuple(upper['inner']))
    inside = RecordingPen()
    inside.moveTo(tuple(lower['inner']))
    arch(inside, p['inner'], lower['inner'], upper['inner'])
    # Reverse only the open inner arch; the two terminal cuts close the ribbon.
    commands = inside.value
    starts = [commands[0][1][0]] + [args[-1] for _, args in commands[1:]]
    for index in range(len(commands)-1, 0, -1):
        control1, control2, _ = commands[index][1]
        pen.curveTo(control2, control1, starts[index-1])
    pen.closePath()


def flat_bowl(pen, p, counter=False):
    """A flat left wall, horizontal shoulders and a rounded right side."""
    left, bottom, right, top = p['bbox']
    tx, bx, cy = p['top_x'], p['bottom_x'], p['axis_y']
    kx, ky = p['kx'], p['ky']
    path = RecordingPen()
    path.moveTo((left, bottom))
    path.lineTo((left, top))
    path.lineTo((tx, top))
    path.curveTo((tx+(right-tx)*kx, top),
                 (right, cy+(top-cy)*ky), (right, cy))
    path.curveTo((right, cy-(cy-bottom)*ky),
                 (bx+(right-bx)*kx, bottom), (bx, bottom))
    path.closePath()
    path.replay(ReverseContourPen(pen) if counter else pen)


def stem_bowl(pen, p):
    """b/d/p/q: an upright with independently shaped bowl and counter."""
    left, _, right, _ = p['bbox']
    inside = left + p['stem']
    top, bottom = p['bowl_top'], p['bowl_bottom']
    tx, bx, cy = p['top_x'], p['bottom_x'], p['axis_y']
    upper, lower = p['join_top'], p['join_bottom']
    kx, ky = p['kx'], p['ky']
    pen.moveTo((left, p['stem_bottom']))
    pen.lineTo((left, p['stem_top']))
    pen.lineTo((inside, p['stem_top']))
    pen.lineTo((inside, upper))
    pen.curveTo((inside+(tx-inside)*p['departure_top_x'], upper+(top-upper)*p['departure_top_y']),
                (tx-(tx-inside)*kx, top), (tx, top))
    pen.curveTo((tx+(right-tx)*kx, top),
                (right, cy+(top-cy)*ky), (right, cy))
    pen.curveTo((right, cy-(cy-bottom)*ky),
                (bx+(right-bx)*kx, bottom), (bx, bottom))
    pen.curveTo((bx-(bx-inside)*kx, bottom),
                (inside+(bx-inside)*p['departure_bottom_x'], lower-(lower-bottom)*p['departure_bottom_y']),
                (inside, lower))
    pen.lineTo((inside, p['stem_bottom']))
    pen.closePath()
    closed_bowl(pen, p['inner'], counter=True)


def draw_template(pen, character, parameters):
    """Dispatch by construction family; never silently substitute a character."""
    kind = parameters['template']
    if kind == 'round':
        outer, inner = parameters['outer'], parameters['inner']
        closed_bowl(pen, outer)
        closed_bowl(pen, inner, counter=True)
    elif kind == 'capital_h':
        capital_h(pen, parameters)
    elif kind == 'stem_and_bars':
        stem_and_bars(pen, parameters)
    elif kind == 'rectangle':
        rectangle(pen, *parameters['bbox'])
    elif kind == 'capital_t':
        capital_t(pen, parameters)
    elif kind == 'open_bowl':
        open_bowl(pen, parameters)
    elif kind == 'flat_bowl':
        flat_bowl(pen, parameters['outer'])
        flat_bowl(pen, parameters['inner'], counter=True)
    elif kind == 'stem_bowl':
        if parameters.get('mirror'):
            left, _, right, _ = parameters['bbox']
            reflected = TransformPen(pen, (-1, 0, 0, 1, left+right, 0))
            stem_bowl(ReverseContourPen(reflected), parameters)
        else:
            stem_bowl(pen, parameters)
    elif kind == 'shoulder_n':
        shoulder_n(pen, parameters)
    elif kind == 'shoulder_u':
        left, _, right, _ = parameters['bbox']
        rotation = (-1, 0, 0, -1, left + right, parameters['x_height'])
        shoulder_n(TransformPen(pen, rotation), parameters)
    else:
        raise ValueError(f'No independent template for {character}: {kind}')
