#!/usr/bin/env python3
"""Turn red/green highlight differences into ranked repair signals.

Input is a render-pairs directory after compare-pixels.py. The script keeps the
same no-registration premise for scores, but additionally asks diagnostic
questions: would a small shift, dilation, erosion, or bbox change explain the
error better than local contour reconstruction?
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage


@dataclass
class Masks:
    ref: np.ndarray
    own: np.ndarray


def bbox(mask: np.ndarray) -> list[int] | None:
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]


def centroid(mask: np.ndarray) -> list[float] | None:
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return [round(float(xs.mean()), 3), round(float(ys.mean()), 3)]


def iou(a: np.ndarray, b: np.ndarray) -> float:
    union = int((a | b).sum())
    if union == 0:
        return 1.0
    return int((a & b).sum()) / union


def shift(mask: np.ndarray, dx: int, dy: int) -> np.ndarray:
    out = np.zeros_like(mask)
    h, w = mask.shape
    src_x0 = max(0, -dx)
    src_x1 = min(w, w - dx)
    dst_x0 = max(0, dx)
    dst_x1 = min(w, w + dx)
    src_y0 = max(0, -dy)
    src_y1 = min(h, h - dy)
    dst_y0 = max(0, dy)
    dst_y1 = min(h, h + dy)
    if src_x1 > src_x0 and src_y1 > src_y0:
        out[dst_y0:dst_y1, dst_x0:dst_x1] = mask[src_y0:src_y1, src_x0:src_x1]
    return out


def best_shift(ref: np.ndarray, own: np.ndarray, radius: int = 4) -> dict[str, object]:
    best = {"dx": 0, "dy": 0, "iou": iou(ref, own)}
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            score = iou(ref, shift(own, dx, dy))
            if score > best["iou"]:
                best = {"dx": dx, "dy": dy, "iou": score}
    return best


def edge(mask: np.ndarray) -> np.ndarray:
    if not mask.any():
        return mask
    return mask & ~ndimage.binary_erosion(mask)


def largest_components(mask: np.ndarray, count: int = 5) -> list[dict[str, object]]:
    labels, total = ndimage.label(mask)
    if total == 0:
        return []
    rows = []
    areas = ndimage.sum(mask, labels, index=range(1, total + 1))
    for label, area in sorted(enumerate(areas, 1), key=lambda item: item[1], reverse=True)[:count]:
        component = labels == label
        rows.append({"area": int(area), "bbox": bbox(component), "centroid": centroid(component)})
    return rows


def classify(row: dict[str, object]) -> list[str]:
    tags: list[str] = []
    if row["bestShiftGain"] >= 0.025:
        tags.append("смещение")
    bw, bh = row["bboxDeltaWH"]
    if abs(bw) >= 3 or abs(bh) >= 3:
        tags.append("масштаб/bbox")
    if row["dilateGain"] >= 0.015:
        tags.append("штрих тонкий")
    if row["erodeGain"] >= 0.015:
        tags.append("штрих толстый")
    if row["largestFN"] >= 80 and row["fnBoundaryShare"] < 0.7:
        tags.append("пропуск контура")
    if row["largestFP"] >= 80 and row["fpBoundaryShare"] < 0.7:
        tags.append("лишний контур")
    if not tags and (row["fnBoundaryShare"] >= 0.75 or row["fpBoundaryShare"] >= 0.75):
        tags.append("граница/AA")
    return tags or ["смешанная геометрия"]


def load_masks(directory: Path, record: dict[str, object], threshold: float) -> Masks:
    ref_img = np.array(Image.open(directory / record["system"]["file"]).convert("L")) / 255.0
    own_img = np.array(Image.open(directory / record["tabuna"]["file"]).convert("L")) / 255.0
    return Masks(ref=ref_img < (1 - threshold), own=own_img < (1 - threshold))


def analyze_record(directory: Path, record: dict[str, object]) -> dict[str, object]:
    masks = load_masks(directory, record, 0.5)
    ref, own = masks.ref, masks.own
    base = iou(ref, own)
    fp = own & ~ref
    fn = ref & ~own
    ref_box = bbox(ref)
    own_box = bbox(own)
    if ref_box and own_box:
        bbox_delta = [own_box[i] - ref_box[i] for i in range(4)]
        bbox_delta_wh = [(own_box[2] - own_box[0]) - (ref_box[2] - ref_box[0]),
                         (own_box[3] - own_box[1]) - (ref_box[3] - ref_box[1])]
    else:
        bbox_delta = [0, 0, 0, 0]
        bbox_delta_wh = [0, 0]
    own_dilated = ndimage.binary_dilation(own)
    own_eroded = ndimage.binary_erosion(own)
    shifted = best_shift(ref, own)
    ref_edge = edge(ref)
    own_edge = edge(own)
    distance_to_ref_edge = ndimage.distance_transform_edt(~ref_edge)
    distance_to_own_edge = ndimage.distance_transform_edt(~own_edge)
    fn_boundary = int((fn & (distance_to_own_edge <= 1.5)).sum())
    fp_boundary = int((fp & (distance_to_ref_edge <= 1.5)).sum())
    fn_total = int(fn.sum())
    fp_total = int(fp.sum())
    fn_components = largest_components(fn)
    fp_components = largest_components(fp)
    row = {
        "character": record["character"],
        "codepoint": record["codepoint"],
        "inkIoU": record["inkIoU"],
        "hardIoU": round(base, 6),
        "fp": fp_total,
        "fn": fn_total,
        "largestFP": fp_components[0]["area"] if fp_components else 0,
        "largestFN": fn_components[0]["area"] if fn_components else 0,
        "fpComponents": fp_components,
        "fnComponents": fn_components,
        "bboxReference": ref_box,
        "bboxRender": own_box,
        "bboxDelta": bbox_delta,
        "bboxDeltaWH": bbox_delta_wh,
        "centroidDelta": None if centroid(ref) is None or centroid(own) is None else [
            round(centroid(own)[0] - centroid(ref)[0], 3),
            round(centroid(own)[1] - centroid(ref)[1], 3),
        ],
        "bestShift": shifted,
        "bestShiftGain": round(float(shifted["iou"]) - base, 6),
        "dilateIoU": round(iou(ref, own_dilated), 6),
        "dilateGain": round(iou(ref, own_dilated) - base, 6),
        "erodeIoU": round(iou(ref, own_eroded), 6),
        "erodeGain": round(iou(ref, own_eroded) - base, 6),
        "fnBoundaryShare": round(fn_boundary / fn_total, 4) if fn_total else 0,
        "fpBoundaryShare": round(fp_boundary / fp_total, 4) if fp_total else 0,
        "diffFile": record["difference"],
    }
    row["tags"] = classify(row)
    row["priorityScore"] = round(
        (1 - float(record["inkIoU"])) * 1000
        + row["largestFN"] * 0.7
        + row["largestFP"] * 0.35
        + max(0, row["bestShiftGain"]) * 500,
        3,
    )
    return row


def make_atlas(directory: Path, rows: list[dict[str, object]], out: Path, limit: int) -> None:
    thumbs: list[tuple[dict[str, object], Image.Image]] = []
    for row in rows[:limit]:
        stem = row['codepoint'][2:]
        ref = np.asarray(Image.open(directory / f'{stem}-system.png').convert('L')) < 128
        own = np.asarray(Image.open(directory / f'{stem}-tabuna.png').convert('L')) < 128
        pixels = np.full((*ref.shape, 3), 255, dtype=np.uint8)
        pixels[ref & own] = [160, 160, 160]
        pixels[ref & ~own] = [240, 40, 40]
        pixels[own & ~ref] = [35, 95, 245]
        img = Image.fromarray(pixels)
        box = bbox(ref | own)
        box = (box[0]-5, box[1]-5, box[2]+5, box[3]+5) if box else (0, 0, img.width, img.height)
        crop = img.crop(box)
        scale = min(180/crop.width, 180/crop.height)
        crop = crop.resize((round(crop.width*scale), round(crop.height*scale)), Image.Resampling.NEAREST)
        thumbs.append((row, crop))
    cell_w, cell_h = 260, 250
    cols = 4
    rows_count = (len(thumbs) + cols - 1) // cols
    atlas = Image.new("RGB", (cols * cell_w, rows_count * cell_h+28), "white")
    draw = ImageDraw.Draw(atlas)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
    draw.text((8, 5), 'FN: красный · FP: синий · совпадение: серый · порог 0.5', fill=(20, 20, 20), font=font)
    for i, (row, img) in enumerate(thumbs):
        x = (i % cols) * cell_w
        y = (i // cols) * cell_h+28
        atlas.paste(img, (x + 8, y + 8))
        text = (
            f"{row['character']} IoU {row['inkIoU']:.3f}\n"
            f"FP/FN {row['fp']}/{row['fn']} L {row['largestFP']}/{row['largestFN']}\n"
            f"{', '.join(row['tags'][:2])}"
        )
        draw.multiline_text((x + 8, y + 192), text, fill=(20, 20, 20), font=font, spacing=2)
    atlas.save(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--limit", type=int, default=32)
    args = parser.parse_args()
    directory = args.directory
    data = json.loads((directory / "comparison.json").read_text())
    rows = [analyze_record(directory, record) for record in data["records"]]
    by_priority = sorted(rows, key=lambda row: row["priorityScore"], reverse=True)
    report = {
        "source": str(directory),
        "legend": {
            "diff": data.get("legend"),
            "classification": "Tags are diagnostics from binary masks at threshold 0.5; scores remain no-registration render scores.",
        },
        "topPriority": by_priority[: args.limit],
        "byTag": {},
    }
    for row in rows:
        for tag in row["tags"]:
            report["byTag"].setdefault(tag, []).append({
                "character": row["character"],
                "inkIoU": row["inkIoU"],
                "priorityScore": row["priorityScore"],
            })
    for tag in report["byTag"]:
        report["byTag"][tag].sort(key=lambda item: item["priorityScore"], reverse=True)
        report["byTag"][tag] = report["byTag"][tag][:20]
    out_json = directory / "highlight-analysis.json"
    out_png = directory / "highlight-atlas.png"
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    make_atlas(directory, by_priority, out_png, args.limit)
    print(json.dumps({
        "analysis": str(out_json),
        "atlas": str(out_png),
        "top": [
            {
                "character": row["character"],
                "inkIoU": row["inkIoU"],
                "tags": row["tags"],
                "fp": row["fp"],
                "fn": row["fn"],
                "largestFP": row["largestFP"],
                "largestFN": row["largestFN"],
            }
            for row in by_priority[:12]
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
