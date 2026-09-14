"""Filled outlines for the core reading alphabet.

Outer edges, counters, joins and terminals have separate construction roles.
Production defaults are explicit. Legacy coordinate-based shapes remain
tracked in FONT-MODEL.md; their provenance is not resolved by this cleanup.
"""
from geometry import Drawing

def core(design, ch):
    d = Drawing()
    s = design.s
    sy = s * 0.89
    H = design.cap
    h = design.h
    heavy = max(0, (design.weight - 400) / 500)
    low = ch.islower()
    y = h if low else H
    o = 10
    widths = {'a': 454, 'b': 471, 'c': 430, 'd': 471, 'e': 464, 'f': 278, 'g': 471, 'h': 451, 'm': 728,
        'n': 451, 'o': 480, 'p': 471, 'q': 471, 'r': 274, 's': 401, 't': 280, 'u': 451, 'B': 507,
        'P': 496, 'R': 533, 'D': 567, 'C': 562, 'G': 597, 'S': 504, 'O': 615, 'Q': 615, '0': 505,
        '1': 298, '2': 477, '3': 478, '4': 513, '5': 469, '6': 494, '7': 472, '8': 496, '9': 494,
        'I': 87.890625}
    if ch not in widths:
        return None
    w = widths[ch] + heavy * (35 if ch in 'abdegopqBPR' else 18 if ch not in 'frt' else 8)
    if ch in 'ft':
        w += heavy * 72
    if ch.isupper() and H < 650:
        w *= 0.87
    p = d.outline
    if ch == 'I':
        raw = 26 + (design.weight - 100) * 52 / 300 if design.weight <= 400 else 78 + (design.weight - 400) * 64 / 500
        w = 180 / 2.048 * raw / 78
        d.rect(0, 0, w, 1443 / 2.048)
    elif ch == '0':
        return d,w  # ring_symbols supplies the two final contours.
    elif ch in 'oOQ':
        q_thickness = 1.04 if ch == 'Q' else 1.0
        ring_s = s * (1.12 if ch == 'Q' else 1.0) * q_thickness

        def oval(l, b, r, t, counter=False):
            cx = (l + r) / 2
            cy = (b + t) / 2
            rx = (r - l) / 2
            ry = (t - b) / 2
            k = 0.565
            d.outline((l, cy), [((l, cy + ry * k), (cx - rx * k, t), (cx, t)), ((cx + rx * k, t), (r,
                cy + ry * k), (r, cy)), ((r, cy - ry * k), (cx + rx * k, b), (cx, b)), ((cx - rx * k,
                b), (l, cy - ry * k), (l, cy))], counter=counter)
        q_shift = 10.0 if ch == 'Q' else 0.0
        oval(0, -o + q_shift, w, y + o + q_shift)
        oval(ring_s, sy * q_thickness - o + q_shift, w - ring_s, y + o - sy * q_thickness + q_shift,
            True)
        if ch == 'Q':
            d.polygon([(w * 0.52, y * 0.2), (w * 0.52 + s * 0.8, y * 0.25), (w + 10, -48), (w - s * 0.87,
                -48)])
    elif ch in 'n hm'.replace(' ', ''):
        top = 740 if ch == 'h' else h
        if ch == 'm':
            mid = w * 0.5
            p((0, 0), [(0, h), (s, h), (s, h * 0.86), ((w * 0.19, h + o), (w * 0.36, h + o),
                (mid - s * 0.27, h * 0.81)), ((w * 0.68, h + o), (w, h + o), (w, h * 0.62)), (w, 0),
                (w - s, 0), (w - s, h * 0.59), ((w - s, h - sy + o), (mid + s * 0.3, h - sy + o),
                (mid + s * 0.3, h * 0.55)), (mid + s * 0.3, 0), (mid - s * 0.7, 0), (mid - s * 0.7,
                h * 0.6), ((mid - s * 0.7, h - sy + o), (s, h - sy + o), (s, h * 0.55)), (s, 0)])
        else:
            p((0, 0), [(0, top), (s, top), (s, h * 0.84), ((s * 1.55, h + o), (w * 0.5, h + o),
                (w * 0.55, h + o)), ((w * 0.86, h + o), (w, h * 0.87), (w, h * 0.62)), (w, 0), (w - s,
                0), (w - s, h * 0.59), ((w - s, h - sy + o), (s, h - sy + o), (s, h * 0.55)), (s, 0)])
    elif ch == 'u':
        b, bw = core(design, 'n')
        b.replay(d.pen, (-1, 0, 0, -1, bw, h))
        w = bw
    elif ch == 'r':
        p((0, 0), [(0, h), (s, h), (s, h * 0.82), ((s * 1.42, h + o), (w * 0.77, h + o), (w, h - 2)), (w,
            h - sy - 5), ((w * 0.54, h - sy + 7), (s, h * 0.91 - sy), (s, h * 0.53)), (s, 0)])
    elif ch in 'bdpqg':
        top = 740 if ch in 'bd' else h
        bottom = -210 if ch in 'pq' else 0
        bowl = Drawing()
        bowl.outline((0, bottom), [(0, top), (s, top), (s, h * 0.84), ((w * 0.28, h + o), (w * 0.42,
            h + o), (w * 0.53, h + o)), ((w * 0.86, h + o), (w, h * 0.79), (w, h * 0.5)), ((w, h * 0.2),
            (w * 0.86, -o), (w * 0.53, -o)), ((w * 0.4, -o), (w * 0.23, 15), (s, h * 0.14)), (s,
            bottom)])
        bowl.outline((s, h * 0.5), [((s, h * 0.29), (w * 0.25, sy - o), (w * 0.5, sy - o)), ((w * 0.76,
            sy - o), (w - s, h * 0.29), (w - s, h * 0.5)), ((w - s, h * 0.71), (w * 0.76, h + o - sy),
            (w * 0.5, h + o - sy)), ((w * 0.25, h + o - sy), (s, h * 0.71), (s, h * 0.5))],
            counter=True)
        if ch in 'dq':
            bowl.replay(d.pen, (-1, 0, 0, 1, w, 0))
        elif ch == 'g':
            p((w, h), [(w, -30), ((w, -178), (w * 0.79, -220), (w * 0.48, -220)), ((w * 0.25, -220),
                (w * 0.1, -183), (0, -130)), (s * 0.63, -75), ((w * 0.23, -133), (w * 0.33, -220 + sy),
                (w * 0.49, -220 + sy)), ((w * 0.76, -220 + sy), (w - s, -110), (w - s, -24)), (w - s,
                h * 0.12), ((w * 0.72, -o), (w * 0.56, -o), (w * 0.46, -o)), ((w * 0.15, -o), (0,
                h * 0.2), (0, h * 0.49)), ((0, h * 0.8), (w * 0.16, h + o), (w * 0.46, h + o)),
                ((w * 0.6, h + o), (w * 0.76, h * 0.95), (w - s, h * 0.84)), (w - s, h)])
            p((s, h * 0.49), [((s, h * 0.28), (w * 0.26, sy - o), (w * 0.5, sy - o)), ((w * 0.75,
                sy - o), (w - s, h * 0.29), (w - s, h * 0.49)), ((w - s, h * 0.71), (w * 0.76,
                h + o - sy), (w * 0.5, h + o - sy)), ((w * 0.26, h + o - sy), (s, h * 0.71), (s,
                h * 0.49))], counter=True)
        else:
            bowl.replay(d.pen)
    elif ch in 'cCG':
        p((w, y * 0.82), [((w * 0.89, y * 0.96), (w * 0.74, y + o), (w * 0.52, y + o)), ((w * 0.18,
            y + o), (0, y * 0.81), (0, y * 0.5)), ((0, y * 0.19), (w * 0.17, -o), (w * 0.51, -o)),
            ((w * 0.74, -o), (w * 0.9, y * 0.07), (w, y * 0.18)), (w - s * 0.66, y * 0.18 + sy * 0.53),
            ((w * 0.8, sy + 13), (w * 0.67, sy - o), (w * 0.52, sy - o)), ((w * 0.25, sy - o), (s,
            y * 0.24), (s, y * 0.5)), ((s, y * 0.76), (w * 0.25, y + o - sy), (w * 0.52, y + o - sy)),
            ((w * 0.67, y + o - sy), (w * 0.8, y * 0.9 - sy * 0.12), (w - s * 0.66,
            y * 0.82 - sy * 0.53))])
        if ch == 'G':
            d.rect(w - s, y * 0.11, s, y * 0.36)
            d.rect(w * 0.56, y * 0.43, w * 0.44, sy)
    elif ch == 'e':
        p((w, h * 0.46), [(s, h * 0.46), ((s, h * 0.23), (w * 0.26, sy - o), (w * 0.52, sy - o)),
            ((w * 0.69, sy - o), (w * 0.8, h * 0.11), (w * 0.88, h * 0.21)), (w, h * 0.12), ((w * 0.89,
            h * 0.03), (w * 0.73, -o), (w * 0.51, -o)), ((w * 0.18, -o), (0, h * 0.19), (0, h * 0.5)),
            ((0, h * 0.79), (w * 0.17, h + o), (w * 0.5, h + o)), ((w * 0.83, h + o), (w, h * 0.79), (w,
            h * 0.53))])
        p((s, h * 0.46 + sy * 0.88), [(w - s, h * 0.46 + sy * 0.88), ((w - s, h * 0.79), (w * 0.73,
            h + o - sy), (w * 0.5, h + o - sy)), ((w * 0.28, h + o - sy), (s, h * 0.77), (s,
            h * 0.46 + sy * 0.88))], counter=True)
    elif ch == 'a':
        p((w, 0), [(w - s, 0), (w - s, h * 0.1), ((w * 0.73, h * 0.03), (w * 0.57, -o), (w * 0.4, -o)),
            ((w * 0.14, -o), (0, h * 0.11), (0, h * 0.28)), ((0, h * 0.45), (w * 0.17, h * 0.49),
            (w * 0.44, h * 0.53)), (w - s, h * 0.58), (w - s, h * 0.67), ((w - s, h + o - sy),
            (w * 0.29, h + o - sy), (s * 0.8, h * 0.76)), (s * 0.1, h * 0.81), ((w * 0.17, h * 0.97),
            (w * 0.32, h + o), (w * 0.51, h + o)), ((w * 0.84, h + o), (w, h * 0.84), (w, h * 0.64))])
        p((w - s, h * 0.46), [(w * 0.46, h * 0.41), ((s * 1.35, h * 0.37), (s, h * 0.36), (s, h * 0.26)),
            ((s, sy - o), (w * 0.34, sy - o), (w * 0.43, sy - o)), ((w * 0.67, sy - o), (w - s,
            h * 0.19), (w - s, h * 0.34))], counter=True)
    elif ch in 'sS':
        p((w, y * 0.82), [((w * 0.91, y * 0.95), (w * 0.73, y + o), (w * 0.5, y + o)), ((w * 0.21,
            y + o), (0, y * 0.88), (0, y * 0.7)), ((0, y * 0.52), (w * 0.18, y * 0.47), (w * 0.45,
            y * 0.4)), ((w * 0.72, y * 0.33), (w - s, y * 0.31), (w - s, y * 0.21)), ((w - s, sy - o),
            (w * 0.67, sy - o), (w * 0.49, sy - o)), ((w * 0.28, sy - o), (s * 1.03, y * 0.11),
            (s * 0.82, y * 0.22)), (0, y * 0.17), ((w * 0.1, y * 0.03), (w * 0.27, -o), (w * 0.49, -o)),
            ((w * 0.79, -o), (w, y * 0.1), (w, y * 0.23)), ((w, y * 0.43), (w * 0.81, y * 0.48),
            (w * 0.53, y * 0.55)), ((w * 0.24, y * 0.62), (s, y * 0.62), (s, y * 0.73)), ((s,
            y + o - sy), (w * 0.33, y + o - sy), (w * 0.5, y + o - sy)), ((w * 0.68, y + o - sy),
            (w * 0.78, y * 0.89), (w - s * 0.78, y * 0.78 - sy * 0.3))])
    elif ch in 'ft':
        # The positioned stem and tangent hook are built by hooked_stems.
        return d, w
    elif ch in 'BPR':
        mid = H * 0.47 if ch == 'B' else H * 0.43
        right = w - (25 if ch == 'R' else 0)
        p((0, 0), [(0, H), (right * 0.53, H), ((right * 0.88, H), (right, H * 0.88), (right, H * 0.73)),
            ((right, H * 0.6), (right * 0.89, mid + sy * 0.35), (right * 0.75, mid + sy * 0.2)), *([((w,
            H * 0.43), (w, H * 0.31), (w, H * 0.23)), ((w, H * 0.07), (w * 0.85, 0), (w * 0.55,
            0))] if ch == 'B' else [(s, mid)]), (s, 0)])
        counter_top = H - sy
        counter_bottom = mid + sy
        center = (counter_top + counter_bottom) / 2
        p((s, counter_top), [(right * 0.52, counter_top), ((right * 0.76, counter_top), (right - s,
            center + (counter_top - center) * 0.55), (right - s, center)), ((right - s,
            center - (center - counter_bottom) * 0.55), (right * 0.7, counter_bottom), (right * 0.49,
            counter_bottom)), (s, counter_bottom)], counter=True)
        if ch == 'B':
            center = (mid + sy) / 2
            p((s, mid), [(w * 0.53, mid), ((w * 0.8, mid), (w - s, center + (mid - center) * 0.55),
                (w - s, center)), ((w - s, center - (center - sy) * 0.55), (w * 0.74, sy), (w * 0.53,
                sy)), (s, sy)], counter=True)
        if ch == 'R':
            leg_x = w * (0.5 if getattr(design, 'derived_cyr_r', False) else 0.43)
            d.polygon([(leg_x, mid + sy * 0.6), (leg_x + s, mid + sy * 0.6), (w, 0), (w - s * 1.15, 0)])
    elif ch == 'D':
        p((0, 0), [(0, H), (w * 0.35, H), ((w * 0.79, H), (w, H * 0.79), (w, H * 0.5)), ((w, H * 0.2),
            (w * 0.79, 0), (w * 0.35, 0))])
        p((s, sy), [(w * 0.34, sy), ((w * 0.69, sy), (w - s, H * 0.23), (w - s, H * 0.5)), ((w - s,
            H * 0.77), (w * 0.69, H - sy), (w * 0.34, H - sy)), (s, H - sy)], counter=True)
    elif ch == '1':
        p((w - s, 0), [(w - s, H - sy * 1.06), (s * 0.34, H * 0.74), (0, H * 0.74 + sy * 0.92),
            (w - s * 0.93, H), (w, H), (w, 0)])
    elif ch == '2':
        p((0, 0), [(0, sy * 0.99), ((0, H * 0.18), (w * 0.23, H * 0.36), (w * 0.45, H * 0.5)), ((w * 0.7,
            H * 0.66), (w - s, H * 0.69), (w - s, H * 0.77)), ((w - s, H + 10 - sy), (s * 1.31,
            H + 10 - sy), (s * 0.85, H * 0.78)), (0, H * 0.81), ((w * 0.05, H * 0.98), (w * 0.32,
            H + 10), (w * 0.51, H + 10)), ((w * 0.83, H + 10), (w, H * 0.92), (w, H * 0.75)), ((w,
            H * 0.56), (w * 0.83, H * 0.49), (w * 0.57, H * 0.32)), ((w * 0.36, H * 0.18), (s * 1.25,
            sy * 1.26), (s * 1.18, sy)), (w, sy), (w, 0)])
    elif ch == '3':
        start_y_h = 0.85
        top_c1_x_w = 0.12
        top_c1_y_h = 0.99
        top_c2_x_w = 0.29
        top_end_x_w = 0.49
        upper_right_c1_x_w = 0.8
        upper_right_c2_x_w = 0.98
        upper_right_c2_y_h = 0.91
        upper_right_end_x_w = 0.98
        upper_right_end_y_h = 0.75
        upper_side_c1_x_w = 0.98
        upper_side_c1_y_h = 0.62
        upper_side_c2_x_w = 0.86
        upper_side_c2_y_h = 0.55
        waist_right_x_w = 0.73
        waist_right_y_h = 0.51
        mid_c1_x_w = 0.93
        mid_c1_y_h = 0.47
        mid_c2_y_h = 0.37
        lower_right_end_y_h = 0.3021760221760222
        bottom_right_c1_y_h = 0.09
        bottom_c2_x_w = 0.79
        bottom_end_x_w = 0.5226882845188285
        bottom_left_c1_x_w = 0.28268828451882844
        bottom_left_c2_x_w = 0.08
        bottom_left_c2_y_h = 0.07217602217602218
        bottom_left_end_y_h = 0.20217602217602218
        left_waist_x_s = 1.015434646654159
        left_waist_y_h = 0.18
        left_waist_y_sy = 0.51
        lower_inner_c1_x_w = 0.25
        lower_inner_c2_x_w = 0.33
        lower_inner_end_x_w = 0.49
        lower_inner_right_c1_x_w = 0.72
        lower_inner_right_c2_x_s = 1.0
        lower_inner_right_c2_y_h = 0.12
        lower_inner_right_end_x_s = 1.0
        lower_inner_right_end_y_h = 0.28
        lower_join_c1_x_s = 1.0
        lower_join_c1_y_h = 0.4
        lower_join_c2_x_w = 0.74
        lower_join_end_x_w = 0.43
        waist_left_x_w = 0.28
        upper_inner_c1_x_w = 0.7
        upper_inner_c2_x_w = 0.98
        upper_inner_c2_x_s = 1.0
        upper_inner_c2_y_h = 0.63
        upper_inner_end_x_w = 0.98
        upper_inner_end_x_s = 1.0
        upper_inner_end_y_h = 0.75
        upper_inner_top_c1_x_w = 0.98
        upper_inner_top_c1_x_s = 1.0
        upper_inner_top_c2_x_w = 0.69
        upper_inner_top_end_x_w = 0.49
        top_return_c1_x_w = 0.34
        top_return_c2_x_w = 0.24
        top_return_c2_y_h = 0.92
        top_return_c2_y_sy = 0.12
        top_return_end_x_s = 0.77
        top_return_end_y_h = 0.85
        top_return_end_y_sy = 0.47
        p((0, H * start_y_h), [((w * top_c1_x_w, H * top_c1_y_h), (w * top_c2_x_w, H + 10),
            (w * top_end_x_w, H + 10)), ((w * upper_right_c1_x_w, H + 10), (w * upper_right_c2_x_w,
            H * upper_right_c2_y_h), (w * upper_right_end_x_w, H * upper_right_end_y_h)),
            ((w * upper_side_c1_x_w, H * upper_side_c1_y_h), (w * upper_side_c2_x_w,
            H * upper_side_c2_y_h), (w * waist_right_x_w, H * waist_right_y_h)), ((w * mid_c1_x_w,
            H * mid_c1_y_h), (w, H * mid_c2_y_h), (w, H * lower_right_end_y_h)), ((w,
            H * bottom_right_c1_y_h), (w * bottom_c2_x_w, -10), (w * bottom_end_x_w, -10)),
            ((w * bottom_left_c1_x_w, -10), (w * bottom_left_c2_x_w, H * bottom_left_c2_y_h), (0,
            H * bottom_left_end_y_h)), (s * left_waist_x_s, H * left_waist_y_h + sy * left_waist_y_sy),
            ((w * lower_inner_c1_x_w, sy + 3), (w * lower_inner_c2_x_w, sy - 10),
            (w * lower_inner_end_x_w, sy - 10)), ((w * lower_inner_right_c1_x_w, sy - 10),
            (w - s * lower_inner_right_c2_x_s, H * lower_inner_right_c2_y_h),
            (w - s * lower_inner_right_end_x_s, H * lower_inner_right_end_y_h)),
            ((w - s * lower_join_c1_x_s, H * lower_join_c1_y_h), (w * lower_join_c2_x_w, H * 0.46),
            (w * lower_join_end_x_w, H * 0.46)), (w * waist_left_x_w, H * 0.46), (w * waist_left_x_w,
            H * 0.46 + sy), (w * lower_join_end_x_w, H * 0.46 + sy), ((w * upper_inner_c1_x_w,
            H * 0.46 + sy), (w * upper_inner_c2_x_w - s * upper_inner_c2_x_s, H * upper_inner_c2_y_h),
            (w * upper_inner_end_x_w - s * upper_inner_end_x_s, H * upper_inner_end_y_h)),
            ((w * upper_inner_top_c1_x_w - s * upper_inner_top_c1_x_s, H + 10 - sy),
            (w * upper_inner_top_c2_x_w, H + 10 - sy), (w * upper_inner_top_end_x_w, H + 10 - sy)),
            ((w * top_return_c1_x_w, H + 10 - sy), (w * top_return_c2_x_w,
            H * top_return_c2_y_h - sy * top_return_c2_y_sy), (s * top_return_end_x_s,
            H * top_return_end_y_h - sy * top_return_end_y_sy))])
    elif ch == '4':
        upright = w * 0.72
        d.rect(upright - s / 2, 0, s, H)
        d.polygon([(upright - s * 0.55, H), (upright + s * 0.45, H), (s * 1.13, H * 0.29), (w, H * 0.29),
            (w, H * 0.29 - sy), (0, H * 0.29 - sy), (0, H * 0.29)])
    elif ch == '5':
        # The final cap/stem/bowl pass owns the outline; retain the advance basis.
        return (d, w)
    elif ch == '9':
        return d,w  # nine_bowl owns the independent bowl/counter/tail model.
    elif ch == '6':
        s *= 1.08
        p((w, H * 0.85), [((w * 0.85, H * 0.98), (w * 0.66, H + 10), (w * 0.48, H + 10)), ((w * 0.15,
            H + 10), (0, H * 0.78), (0, H * 0.36)), ((0, H * 0.13), (w * 0.15, -10), (w * 0.49, -10)),
            ((w * 0.81, -10), (w, H * 0.13), (w, H * 0.31)), ((w, H * 0.51), (w * 0.8, H * 0.63),
            (w * 0.51, H * 0.63)), ((w * 0.32, H * 0.63), (s * 1.24, H * 0.54), (s, H * 0.48)), ((s,
            H * 0.8), (w * 0.28, H + 10 - sy), (w * 0.48, H + 10 - sy)), ((w * 0.64, H + 10 - sy),
            (w * 0.78, H * 0.91), (w - s * 0.67, H * 0.85 - sy * 0.57))])
        d.ellipse(s, sy - 10, w - s, H * 0.63 - sy, reverse=True)
    elif ch == '7':
        d.polygon([(0, H), (w, H), (w, H - sy), (w * 0.39, 0), (w * 0.39 - s * 1.08, 0), (w - s * 1.08,
            H - sy), (0, H - sy)])
    elif ch == '8':
        inner_top_floor_shift = 0.03 * H
        p((w * 0.5, H + 10), [((w * 0.81, H + 10), (w * 0.96, H * 0.9), (w * 0.96, H * 0.76)),
            ((w * 0.96, H * 0.64), (w * 0.87, H * 0.57), (w * 0.76, H * 0.52)), ((w * 0.93, H * 0.46),
            (w, H * 0.36), (w, H * 0.24)), ((w, H * 0.08), (w * 0.82, -10), (w * 0.5, -10)), ((w * 0.18,
            -10), (0, H * 0.08), (0, H * 0.24)), ((0, H * 0.36), (w * 0.07, H * 0.46), (w * 0.24,
            H * 0.52)), ((w * 0.13, H * 0.57), (w * 0.04, H * 0.64), (w * 0.04, H * 0.76)), ((w * 0.04,
            H * 0.9), (w * 0.19, H + 10), (w * 0.5, H + 10))])
        d.ellipse(s + w * 0.04, H * 0.51 + sy * 0.49 + inner_top_floor_shift, w - s - w * 0.04,
            H + 10 - sy, reverse=True)
        d.ellipse(s, sy - 10, w - s, H * 0.51 - sy * 0.49, reverse=True)
    if ch == '4':
        out = Drawing()
        d.replay(out.pen, (1, 0, 0, 1, 0, 15.625))
        d = out
    elif ch == '7':
        out = Drawing()
        d.replay(out.pen, (1, 0, 0, 1, -15.625, 0))
        d = out
    return (d, w)

def cyrillic_core(design, ch):
    """Upright Cyrillic has its own proportions, joins and stroke weights."""
    from copy import copy
    d = Drawing()
    s = design.s
    sy = s * 0.89
    low = ch.islower()
    h = design.h if low else design.cap
    heavy = max(0, (design.weight - 400) / 500)
    p = d.outline
    if ch == 'Я':
        return d, 523  # ya_bowl owns the complete outline.
    if ch == 'К':
        w = 529
        stem = s * 1.2
        d.polygon([(stem, 0), (0, 0), (0, h), (stem, h), (stem, h * 0.561), (w * 0.22, h * 0.561),
            (w * 0.732, h), (w * 0.94, h), (w * 0.338, h * 0.506), (w * 0.339, h * 0.537), (w, 0),
            (w * 0.779, 0), (w * 0.22, h * 0.461), (stem, h * 0.461)])
        return (d, w)
    if ch == 'З':
        w = 480
        base, bw = core(design, '3')
        base.replay(d.pen, (w / bw * 0.96, 0, 0, h / 710, 0, 0))
        d.polygon([(w * 0.66, h * 0.52), (w * 0.96, h * 0.47), (w * 0.94, h * 0.35), (w * 0.66,
            h * 0.41)])
        return (d, w)
    if ch == 'з':
        w = 416
        base, bw = core(design, '3')
        base.replay(d.pen, (w / bw * 0.96, 0, 0, h / 710, 0, 0))
        d.polygon([(s * 0.02, h * 0.18), (w * 0.42, h * 0.18), (w * 0.38, h * 0.05), (s * 0.1,
            h * 0.04)])
        out = Drawing()
        d.replay(out.pen, (1, 0, 0, 1, 7.8125, 0))
        d = out
        return (d, w)
    if ch == 'я':
        return d, 463.71 + heavy * 30.45  # Preserve the calibrated advance basis.
    if ch == 'в':
        small = copy(design)
        small.cap = h
        return core(small, 'B')
    if ch in 'кмнт':
        w = {'к': 440, 'м': 588, 'н': 457, 'т': 433}[ch] + heavy * 20
        if ch == 'н':
            d.rect(0, 0, s, h)
            d.rect(w - s, 0, s, h)
            d.rect(0, h * 0.46, w, sy)
        elif ch == 'т':
            d.rect(0, h - sy, w, sy)
            d.rect((w - s) / 2, 0, s, h)
        elif ch == 'к':
            return d,w  # diagonal_bands owns the complete contour.
        else:
            d.rect(0, 0, s, h)
            d.rect(w - s, 0, s, h)
            d.polygon([(s * 0.38, h), (s * 1.39, h), (w * 0.5, s * 1.24), (w - s * 1.39, h),
                (w - s * 0.38, h), (w * 0.5 + s * 0.45, 0), (w * 0.5 - s * 0.45, 0)])
        return (d, w)
    if ch.upper() in ('Д', 'Л'):
        de = ch.upper() == 'Д'
        w = (526 if low else 589) if de else 468 if low else 554
        w += heavy * (90 if de else 30)
        # Shared El/De models supply the final outlines; retain advance basis.
        return d,w
    if ch.upper() == 'Ж':
        # Only the scalar advance basis remains; branched_stems owns contours.
        return d, (710 if low else 892) + heavy * 26
    if ch.upper() in ('Ь', 'Ъ', 'Ы', 'Б') and ch != 'б':
        c = ch.upper()
        w = ({'Ь': 378, 'Ъ': 461, 'Ы': 598, 'Б': 464} if low else {'Ь': 458, 'Ъ': 566, 'Ы': 685,
            'Б': 509})[c] + heavy * 30
        if ch == 'Б':
            # The parametric be_bowl model supplies the final contours.
            return d, w
        offset = (83 if low else 108) if c == 'Ъ' else 0
        r = w * (0.65 if low else 0.7) if c == 'Ы' else w
        top = h * (0.58 if c == 'Б' else 0.63 if low else 0.62)
        center = (offset + r) / 2
        p((offset, 0), [(offset, h), (offset + s, h), (offset + s, top), (center, top), ((r * 0.85, top),
            (r, top * 0.81), (r, top * 0.5)), ((r, top * 0.18), (r * 0.82, 0), (r * 0.54, 0))])
        p((offset + s, sy), [(center, sy), ((r * 0.75, sy), (r - s, top * 0.29), (r - s, top * 0.5)),
            ((r - s, top * 0.73), (r * 0.74, top - sy), (center, top - sy)), (offset + s, top - sy)],
            counter=True)
        if c == 'Б':
            d.rect(0, h - sy, w * 0.96, sy)
        if c == 'Ъ':
            d.rect(0, h - sy, offset + s * 1.45, sy)
        if c == 'Ы':
            d.rect(w - s, 0, s, h)
        return (d, w)
    if ch == 'б':
        # Keep the advance basis; be_lower constructs both contours.
        _, w = core(design, 'o')
        return d, w
    if ch.upper() == 'Ч':
        w = (434 if low else 513) + heavy * 25
        p((0, h), [(s, h), (s, h * 0.68), ((s, h * 0.46), (w * 0.38, h * 0.46), (w - s, h * 0.61)),
            (w - s, h), (w, h), (w, 0), (w - s, 0), (w - s, h * 0.44), ((w * 0.38, h * 0.3), (0,
            h * 0.32), (0, h * 0.63))])
        return (d, w)
    if ch in 'ЋЂћђ':
        desc = ch in 'Ђђ'
        w = (451 if low else 550) + heavy * 24
        top = h if low else h * 0.64
        asc = 740 if low else h
        x = 42
        p((x, 0), [(x, asc), (x + s, asc), (x + s, top * 0.84), ((x + s * 1.5, top + 10), (w * 0.57,
            top + 10), (w * 0.6, top + 10)), ((w * 0.88, top + 10), (w, top * 0.85), (w, top * 0.61)),
            (w, 0), (w - s, 0), (w - s, top * 0.58), ((w - s, top - sy + 10), (x + s, top - sy + 10),
            (x + s, top * 0.54)), (x + s, 0)])
        d.rect(0, asc - (sy * 1.7 if low else sy), w * 0.81, sy)
        if desc:
            p((w - s, 6), [(w, 6), (w, -78), ((w, -206), (w * 0.73, -231), (w * 0.47, -199)), (w * 0.47,
                -199 + sy), ((w * 0.73, -210 + sy), (w - s, -163), (w - s, -76))])
        return (d, w)
    if ch in 'Љљ':
        # Preserve the advance basis; the shared model owns the whole outline.
        bw = (468 if low else 554) + heavy * 30
        return (d, bw + (270 if low else 320) + heavy * 20)
    if ch in 'Њњ':
        if low:
            left, bw = cyrillic_core(design, 'н')
        else:
            left, bw = design.latin('H')
        left.replay(d.pen)
        w = bw + (270 if low else 320) + heavy * 20
        top = h * 0.58
        cx = (bw + w - s) / 2
        p((bw - s * 0.5, 0), [(bw - s * 0.5, top), (cx, top), ((w * 0.95, top), (w, top * 0.77), (w,
            top * 0.5)), ((w, top * 0.22), (w * 0.95, 0), (cx, 0))])
        p((bw, sy), [(cx, sy), ((w - s, sy), (w - s, top * 0.35), (w - s, top * 0.5)), ((w - s,
            top - sy), (w * 0.95 - s, top - sy), (cx, top - sy)), (bw, top - sy)], counter=True)
        return (d, w)
    return None
