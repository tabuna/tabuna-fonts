"""Shared interpolation of the font's measured construction parameters.

Each family describes its own shape. This module only locates that shape
between text/display endpoints and the 100/400/900 weight masters.
Keeping the arithmetic order stable preserves the compiled outlines exactly.
"""


def mix(a, b, amount):
    """Linearly blend equally structured scalar, list or dictionary data."""
    if isinstance(a, dict):
        return {key: mix(a[key], b[key], amount) for key in a}
    if isinstance(a, list):
        return [mix(x, y, amount) for x, y in zip(a, b)]
    return a + (b - a) * amount


def at_location(masters, design):
    """Blend optical endpoints first, then the enclosing weight interval."""
    lower, upper = (100, 400) if design.weight <= 400 else (400, 900)
    a = mix(masters[str(lower)]['text'], masters[str(lower)]['display'], design.display)
    b = mix(masters[str(upper)]['text'], masters[str(upper)]['display'], design.display)
    return mix(a, b, (design.weight - lower) / (upper - lower))
