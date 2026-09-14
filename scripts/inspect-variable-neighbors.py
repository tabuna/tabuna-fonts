#!/usr/bin/env python3
"""Read-only structural inspection of local variable-font neighbors.

This extracts contour metadata at requested axis locations. It never writes
the inspected outlines into the production font; the output is a measurement
artifact for choosing a fresh reconstruction hypothesis.
"""
from pathlib import Path
import argparse, json
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[1]

def inspect(font, ch):
    cmap = font.getBestCmap() or {}
    name = cmap.get(ord(ch))
    if not name or name not in font["glyf"]:
        return {"character": ch, "missing": True}
    g = font["glyf"][name]
    row = {"character": ch, "glyphName": name,
           "advanceWidth": int(font["hmtx"].metrics[name][0]),
           "bbox": [int(g.xMin), int(g.yMin), int(g.xMax), int(g.yMax)] if g.numberOfContours else None,
           "contourCount": int(max(0, g.numberOfContours)), "pointCount": 0,
           "onCurveCount": 0, "offCurveCount": 0, "contours": []}
    if g.numberOfContours > 0 and not g.isComposite():
        coords, _, flags = g.getCoordinates(font["glyf"])
        row["pointCount"] = len(coords)
        row["onCurveCount"] = int(sum(bool(f & 1) for f in flags))
        row["offCurveCount"] = len(coords) - row["onCurveCount"]
        start = 0
        for end in g.endPtsOfContours:
            pts = coords[start:end + 1]
            row["contours"].append({
                "pointCount": len(pts),
                "onCurveCount": int(sum(bool(flags[i] & 1) for i in range(start, end + 1))),
                "bbox": [int(min(p[0] for p in pts)), int(min(p[1] for p in pts)),
                         int(max(p[0] for p in pts)), int(max(p[1] for p in pts))],
            })
            start = end + 1
    elif g.isComposite():
        row["components"] = [c.glyphName for c in g.components]
    return row

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("font", type=Path, nargs="?", default=Path("/System/Library/Fonts/SFNS.ttf"))
    ap.add_argument("--chars", default="аябвжз5З3")
    ap.add_argument("--weights", default="100,400,800")
    ap.add_argument("--out", type=Path, default=ROOT / "build/system-font-inspection/variable-neighbors.json")
    args = ap.parse_args()
    weights = [int(x) for x in args.weights.split(",")]
    runs = []
    for weight in weights:
        f = instantiateVariableFont(TTFont(str(args.font)),
                                     {"wght": weight, "wdth": 100, "opsz": 28, "GRAD": 400},
                                     inplace=False)
        runs.append({"weight": weight, "glyphs": [inspect(f, ch) for ch in args.chars]})
    result = {"font": str(args.font), "chars": args.chars, "weights": weights,
              "axisDefaults": {"wdth": 100, "opsz": 28, "GRAD": 400},
              "runs": runs,
              "note": "Metadata only; no inspected outline is embedded in production sources."}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"out": str(args.out), "weights": weights, "glyphs": len(args.chars)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
