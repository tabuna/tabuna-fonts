#!/usr/bin/env python3
"""Measure geometric differences in a Highlight audit.

This is deliberately diagnostic: it never edits the font or searches a
parameter space.  It turns the already rendered reference/Tabuna masks into
contour, bounding-box, thickness and connected-error measurements so a human
can choose one authored geometry change.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


def box(mask: np.ndarray):
    ys, xs = np.where(mask)
    return [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)] if len(xs) else None


def components(mask: np.ndarray, limit: int = 10):
    labels, count = ndimage.label(mask, structure=np.ones((3, 3), dtype=np.uint8))
    rows = []
    for label in range(1, count + 1):
        ys, xs = np.where(labels == label)
        if len(xs):
            rows.append({"area": int(len(xs)), "bbox": [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]})
    return sorted(rows, key=lambda row: row["area"], reverse=True)[:limit]


def boundary(mask: np.ndarray) -> np.ndarray:
    return mask & ~ndimage.binary_erosion(mask, structure=np.ones((3, 3), dtype=bool), border_value=0)


def directed_distance(source: np.ndarray, target: np.ndarray):
    if not source.any():
        return {"mean": 0.0, "p95": 0.0, "max": 0.0, "count": 0}
    # distance_transform_edt gives distance to the nearest zero pixel; invert
    # the target boundary so boundary pixels query the nearest boundary pixel.
    distance = ndimage.distance_transform_edt(~target)
    values = distance[source]
    return {"mean": round(float(values.mean()), 3),
            "p95": round(float(np.percentile(values, 95)), 3),
            "max": round(float(values.max()), 3),
            "count": int(values.size)}


def classify(row, ref, own, fn_parts, fp_parts):
    tags = []
    dx0, dy0, dx1, dy1 = row["bboxDelta"] or (0, 0, 0, 0)
    if abs(dx0) >= 2 or abs(dx1) >= 2 or abs(dy0) >= 2 or abs(dy1) >= 2:
        tags.append("смещение/масштаб")
    thickness_delta = row["thickness"]["deltaMedian"]
    if abs(thickness_delta) >= 0.75:
        tags.append("толщина штриха")
    fn_area = row["fn"]
    fp_area = row["fp"]
    largest_fn = fn_parts[0]["area"] if fn_parts else 0
    largest_fp = fp_parts[0]["area"] if fp_parts else 0
    if largest_fn >= 25 and largest_fn >= max(1.5 * largest_fp, 1.5 * fp_area / 4):
        tags.append("пропуск/недостаточный сегмент")
    elif largest_fp >= 25 and largest_fp >= max(1.5 * largest_fn, 1.5 * fn_area / 4):
        tags.append("лишний сегмент")
    if row["boundary"]["refToRender"]["p95"] >= 2.0 or row["boundary"]["renderToRef"]["p95"] >= 2.0:
        tags.append("кривизна/контур")
    elif row["errorArea"] and not tags:
        tags.append("сглаживание/граница")
    if not tags:
        tags.append("совпадает")
    return tags


def audit_size(audit_dir: Path, size: str, records):
    out = []
    for row in records:
        ident = row["highlight"].split("/")[-1].removesuffix("-highlight.png")
        ref_path = audit_dir / size / f"{ident}-system.png"
        own_path = audit_dir / size / f"{ident}-tabuna.png"
        if not ref_path.exists() or not own_path.exists():
            continue
        ref = np.asarray(Image.open(ref_path).convert("L")) < 128
        own = np.asarray(Image.open(own_path).convert("L")) < 128
        ref_edge, own_edge = boundary(ref), boundary(own)
        enriched = dict(row)
        enriched["boundary"] = {
            "refToRender": directed_distance(ref_edge, own_edge),
            "renderToRef": directed_distance(own_edge, ref_edge),
        }
        enriched["fnComponents"] = components(ref & ~own)
        enriched["fpComponents"] = components(own & ~ref)
        enriched["diagnosis"] = classify(enriched, ref, own, enriched["fnComponents"], enriched["fpComponents"])
        out.append(enriched)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("audit_dir", type=Path, help="directory containing report.json and size folders")
    ap.add_argument("--sizes", default=None, help="comma-separated sizes; defaults to report.json")
    ap.add_argument("--top", type=int, default=20, help="number of priority glyphs per size")
    args = ap.parse_args()
    report_path = args.audit_dir / "report.json"
    report = json.loads(report_path.read_text())
    sizes = args.sizes.split(",") if args.sizes else list(report["sizes"])
    result = {"sourceReport": str(report_path), "method": "binary mask contours; 8-connected components; directed boundary distance", "sizes": {}}
    for size in sizes:
        records = audit_size(args.audit_dir, size, report["sizes"][size]["records"])
        priority = sorted(records, key=lambda row: (row["errorArea"], row["boundary"]["refToRender"]["p95"]), reverse=True)
        result["sizes"][size] = {
            "topPriority": [{"character": row["character"], "iou": row["iou"], "fp": row["fp"], "fn": row["fn"], "diagnosis": row["diagnosis"], "highlight": row["highlight"]} for row in priority[:args.top]],
            "records": records,
        }
    output = args.audit_dir / "geometry-audit.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"out": str(output), "sizes": sizes, "glyphs": sum(len(v["records"]) for v in result["sizes"].values())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
