"""Shared optical compensation for thin lower horizontal bars, in 1000-em units."""
THIN_WEIGHT = 100
REGULAR_WEIGHT = 400
LOWER_BAR_TOP_EXPANSION = .25


def lower_bar_top_expansion(weight, display_fraction):
    """Fade the same bar compensation to zero at Regular and text optical sizes."""
    thin_fraction = max(0, min(1, (REGULAR_WEIGHT-weight)/(REGULAR_WEIGHT-THIN_WEIGHT)))
    return LOWER_BAR_TOP_EXPANSION * thin_fraction * display_fraction
