"""Semantic search regions for independent З and 3 raster reconstruction.

These normalized seeds select measured points on each glyph's own contour.
No coordinates or fitted curves are shared between the two glyphs.
"""

LANDMARKS = {
    '2': [
        ('upper_terminal_outer', .03, .24, 'corner'), ('outer_top', .50, .00, 'horizontal'),
        ('upper_outer_right', .97, .25, 'vertical'), ('outer_curve_right', .82, .52, 'vertical'),
        ('diagonal_outer', .52, .72, 'corner'), ('lower_right_outer', .97, .91, 'horizontal'),
        ('bottom_right', .97, 1.00, 'corner'), ('bottom_left', .04, 1.00, 'horizontal'),
        ('lower_terminal_outer', .04, .84, 'corner'), ('diagonal_inner', .33, .73, 'corner'),
        ('inner_diagonal', .55, .545, 'corner'), ('inner_upper_right', .78, .327, 'vertical'),
        ('inner_top_right', .73, .174, 'corner'), ('inner_top', .54, .11, 'horizontal'),
        ('inner_top_left', .33, .137, 'horizontal'), ('upper_terminal_inner', .20, .239, 'corner'),
        ('terminal_inner_end', .01, .30, 'corner'),
    ],
    'З': [
        ('upper_terminal_outer', .04, .25, 'corner'),
        ('outer_top', .49, .00, 'horizontal'),
        ('upper_outer_right', .96, .25, 'vertical'),
        ('waist_outer', .71, .49, 'corner'),
        ('lower_outer_right', 1., .73, 'vertical'),
        ('outer_bottom', .49, 1., 'horizontal'),
        ('lower_terminal_outer', .00, .75, 'corner'),
        ('lower_terminal_inner', .18, .75, 'corner'),
        ('inner_bottom', .49, .89, 'horizontal'),
        ('lower_inner_right', .82, .73, 'vertical'),
        ('lower_join', .52, .56, 'horizontal'),
        ('middle_terminal_bottom', .30, .56, 'corner'),
        ('middle_terminal_top', .30, .445, 'corner'),
        ('upper_join', .52, .445, 'horizontal'),
        ('upper_inner_right', .78, .25, 'vertical'),
        ('inner_top', .49, .105, 'horizontal'),
        ('upper_terminal_inner', .21, .25, 'corner'),
    ],
    '3': [
        ('upper_terminal_outer', .04, .25, 'corner'),
        ('outer_top', .48, .00, 'horizontal'),
        ('upper_outer_right', .95, .25, 'vertical'),
        ('waist_outer', .67, .49, 'corner'),
        ('lower_outer_right', 1., .73, 'vertical'),
        ('outer_bottom', .48, 1., 'horizontal'),
        ('lower_terminal_outer', .00, .75, 'corner'),
        ('lower_terminal_inner', .19, .75, 'corner'),
        ('inner_bottom', .48, .89, 'horizontal'),
        ('lower_inner_right', .81, .73, 'vertical'),
        ('lower_join', .51, .55, 'horizontal'),
        ('middle_terminal_bottom', .32, .55, 'corner'),
        ('middle_terminal_top', .32, .445, 'corner'),
        ('upper_join', .51, .445, 'horizontal'),
        ('upper_inner_right', .76, .25, 'vertical'),
        ('inner_top', .48, .10, 'horizontal'),
        ('upper_terminal_inner', .22, .25, 'corner'),
    ],
}
