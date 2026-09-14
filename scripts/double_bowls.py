"""Original B/В/в contours with two separately parameterized bowls."""
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing
from bowls import arc
from parameters import at_location


@lru_cache(maxsize=1)
def load():
    path = Path(__file__).resolve().parents[1]/'sources/double-bowls.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def drawing(p):
    d = Drawing()
    sl, sr = p['stemLeft'], p['stemRight']
    uu, ul = arc(p['outerUpper'], True), arc(p['outerUpper'], False)
    lu, ll = arc(p['outerLower'], True), arc(p['outerLower'], False)
    d.outline((sl, p['bottom']), [
        (sl, p['top']), uu[-1], tuple(list(reversed(uu))[1:]), tuple(ul[1:]),
        lu[-1], tuple(list(reversed(lu))[1:]), tuple(ll[1:]),
    ])
    for key in ('innerUpper', 'innerLower'):
        q = p[key]
        upper, lower = arc(q, True), arc(q, False)
        d.outline((sr, q['bottom']), [lower[-1], tuple(list(reversed(lower))[1:]),
                  tuple(upper[1:]), (sr, q['top'])], counter=True)
    return d


def apply(glyph, key, design):
    ch = chr(int(key[3:], 16)) if key.startswith('uni') and len(key) == 7 else key
    data = load().get(ch)
    if data is None:
        return
    p = at_location(data, design)
    glyph.clearContours()
    drawing(p).replay(glyph.getPen())
    glyph.width = p['advance']
