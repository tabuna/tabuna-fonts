#!/usr/bin/env python3
"""Inspect a locally installed TrueType font without importing its outlines.

The report contains structure and metrics only: contour counts, on/off-curve
point counts, component references, bounds, advances and variation axes.  It is
intended to reveal construction logic that can be redrawn in our own source.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from fontTools.ttLib import TTFont


def name(font: TTFont, glyph_name: str) -> str:
    cmap = font.getBestCmap() or {}
    for cp, gn in cmap.items():
        if gn == glyph_name:
            return f"U+{cp:04X}"
    return glyph_name


def glyph_structure(font: TTFont, ch: str) -> dict:
    cmap = font.getBestCmap() or {}
    glyph_name = cmap.get(ord(ch))
    if not glyph_name:
        return {"character": ch, "missing": True}
    glyf = font["glyf"]
    g = glyf[glyph_name]
    advance, lsb = font["hmtx"].metrics[glyph_name]
    row = {
        "character": ch,
        "codepoint": f"U+{ord(ch):04X}",
        "glyphName": glyph_name,
        "advanceWidth": int(advance),
        "leftSideBearing": int(lsb),
        "bbox": [int(g.xMin), int(g.yMin), int(g.xMax), int(g.yMax)] if g.numberOfContours != 0 else None,
        "contourCount": int(max(0, g.numberOfContours)),
        "pointCount": 0,
        "onCurveCount": 0,
        "offCurveCount": 0,
        "components": [],
    }
    if g.isComposite():
        row["components"] = [
            {"glyphName": c.glyphName,
             "transform": [round(float(v), 6) for v in c.getComponentInfo()[1]],
             "firstReference": getattr(c, "firstPt", None),
             "firstComponent": getattr(c, "firstComponent", None)}
            for c in g.components
        ]
    elif g.numberOfContours > 0:
        coords, _, flags = g.getCoordinates(glyf)
        row["pointCount"] = len(coords)
        row["onCurveCount"] = int(sum(bool(f & 1) for f in flags))
        row["offCurveCount"] = int(len(coords) - row["onCurveCount"])
        row["contours"] = []
        start = 0
        for end in g.endPtsOfContours:
            pts = coords[start:end + 1]
            row["contours"].append({
                "pointCount": int(len(pts)),
                "onCurveCount": int(sum(bool(flags[i] & 1) for i in range(start, end + 1))),
                "bbox": [int(min(p[0] for p in pts)), int(min(p[1] for p in pts)),
                         int(max(p[0] for p in pts)), int(max(p[1] for p in pts))],
            })
            start = end + 1
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("font", type=Path)
    ap.add_argument("--chars", default="кКЯзЗ53")
    ap.add_argument("--out", type=Path, default=Path("build/system-font-inspection/structure.json"))
    args = ap.parse_args()
    font = TTFont(args.font, lazy=False)
    axes = []
    if "fvar" in font:
        axes = [{"tag": a.axisTag, "min": a.minValue, "default": a.defaultValue, "max": a.maxValue}
                for a in font["fvar"].axes]
    result = {
        "font": str(args.font),
        "family": next((n.toUnicode() for n in font["name"].names if n.nameID == 1), None),
        "unitsPerEm": int(font["head"].unitsPerEm),
        "outlineFormat": "TrueType quadratic (glyf)" if "glyf" in font else "unknown",
        "variationAxes": axes,
        "hasVariationDeltas": "gvar" in font,
        "glyphs": [glyph_structure(font, ch) for ch in args.chars],
        "note": "Structural metadata only; production outlines are not copied from the inspected font.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"out": str(args.out), "glyphs": len(result["glyphs"]), "axes": axes}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
