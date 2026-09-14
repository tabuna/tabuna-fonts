#!/usr/bin/env python3
"""Infer editable construction logic from reference masks.

This does not recover Apple's original Bézier data.  It emits a compact,
deterministic description of the observable topology, centreline landmarks,
stroke-width profile and likely segment roles so a new contour can be authored
from structure instead of blind scalar sweeps.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]


def bbox(mask: np.ndarray) -> list[int] | None:
    yy, xx = np.where(mask)
    if not len(xx):
        return None
    return [int(xx.min()), int(yy.min()), int(xx.max() + 1), int(yy.max() + 1)]


def holes(mask: np.ndarray) -> int:
    """Count enclosed background components inside the glyph bounding box."""
    box = bbox(mask)
    if box is None:
        return 0
    l, t, r, b = box
    crop = mask[t:b, l:r]
    background = ~crop
    labels, count = ndimage.label(background)
    edge = set(np.unique(np.r_[labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    return sum(1 for i in range(1, count + 1) if i not in edge)


def separated_peaks(distance: np.ndarray, mask: np.ndarray, limit: int = 16) -> list[dict]:
    """Return medial landmarks as separated local maxima of the distance field."""
    local = distance == ndimage.maximum_filter(distance, size=5, mode="constant")
    ys, xs = np.where(local & mask & (distance > 0))
    order = sorted(zip(ys, xs), key=lambda p: float(distance[p]), reverse=True)
    chosen: list[tuple[int, int]] = []
    for y, x in order:
        if all((x - px) ** 2 + (y - py) ** 2 >= 25 for py, px in chosen):
            chosen.append((y, x))
        if len(chosen) >= limit:
            break
    return [
        {"x": int(x), "y": int(y), "halfWidth": round(float(distance[y, x]), 3)}
        for y, x in sorted(chosen)
    ]


def extrema(mask: np.ndarray) -> list[dict]:
    box = bbox(mask)
    if box is None:
        return []
    l, t, r, b = box
    ys, xs = np.where(mask)
    out = []
    for name, idx in (("left", np.argmin(xs)), ("right", np.argmax(xs)),
                      ("top", np.argmin(ys)), ("bottom", np.argmax(ys))):
        out.append({"role": name, "x": int(xs[idx]), "y": int(ys[idx])})
    return out


def symmetry(mask: np.ndarray) -> dict:
    """Measure horizontal mirror agreement; useful, but not a copying command."""
    box = bbox(mask)
    if box is None:
        return {"verticalAxis": None, "horizontalMirrorIoU": 1.0}
    l, t, r, b = box
    crop = mask[t:b, l:r]
    flipped = np.fliplr(crop)
    union = np.count_nonzero(crop | flipped)
    score = np.count_nonzero(crop & flipped) / union if union else 1.0
    axis = round((box[0] + box[2] - 1) / 2, 3) if box else None
    return {"verticalAxis": axis, "horizontalMirrorIoU": round(float(score), 6)}


def segment_hint(mask: np.ndarray, landmark_count: int, hole_count: int) -> dict:
    """Give conservative construction hints, never pretend these are originals."""
    components = int(ndimage.label(mask)[1])
    if components > 1:
        kind = "multiple-components"
    elif hole_count:
        kind = "closed-bowl-or-ring"
    elif landmark_count <= 3:
        kind = "mostly-rectilinear-stroke"
    else:
        kind = "open-stroke-with-curves"
    return {
        "constructionClass": kind,
        "suggestedNodes": max(4, min(20, landmark_count + hole_count * 2)),
        "confidence": "structural-only",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", type=Path, default=ROOT / "build/reference-contours/report.json")
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--out", type=Path, default=ROOT / "build/reference-contours/logic.json")
    args = ap.parse_args()
    report = json.loads(args.report.read_text())
    # Historical reports used both `0.5` and `0.50`; accept either form.
    key = str(args.threshold)
    key_alt = f"{args.threshold:.2f}"
    result = {
        "version": 1,
        "source": str(args.report),
        "threshold": args.threshold,
        "method": "topology + distance-transform medial landmarks + mirror diagnostic",
        "note": "Inferred construction logic; it is not Apple's original Bézier source.",
        "glyphs": [],
    }
    for row in report["glyphs"]:
        entry = row["thresholds"].get(key) or row["thresholds"][key_alt]
        mask = np.asarray(Image.open(args.report.parent / entry["maskFile"]).convert("L")) >= 128
        distance = ndimage.distance_transform_edt(mask)
        labels, components = ndimage.label(mask)
        peaks = separated_peaks(distance, mask)
        widths = 2 * distance[mask]
        contours = entry.get("contours", [])
        outer = sum(c.get("role") == "outer" for c in contours)
        inner = sum(c.get("role") == "inner" for c in contours)
        entry_out = {
            "character": row["character"],
            "bbox": bbox(mask),
            "topology": {"components": int(components), "outerContours": outer,
                         "innerContours": inner, "holes": holes(mask)},
            "symmetry": symmetry(mask),
            "stroke": {"median": round(float(np.median(widths)), 3),
                       "mean": round(float(widths.mean()), 3),
                       "p90": round(float(np.percentile(widths, 90)), 3)},
            "landmarks": extrema(mask) + peaks,
        }
        entry_out["construction"] = segment_hint(
            mask, len(peaks), entry_out["topology"]["holes"]
        )
        result["glyphs"].append(entry_out)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"out": str(args.out), "glyphs": len(result["glyphs"]), "threshold": args.threshold}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
