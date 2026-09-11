#!/usr/bin/env python3
"""Build and measure isolated Cyrillic small ze candidates."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "pilot-z" / "font-variants"
GLYPH = "з"
CONTROL_Z_IOU = 0.643550
CONTROL_MEAN_64 = 0.892104
CONTROL_TOTAL = 126
PX_TO_UNITS = 1000 / (64 * 2)


BASE = {
    "top_left_s": 0.34,
    "top_right_s": 0.50,
    "waist_left_w": 0.33,
    "waist_y_h": 0.51,
    "lower_left_s": 0.35,
    "lower_right_s": 0.50,
    "lower_y_h": 0.23,
    "width_top_s": 0.96,
    "width_bottom_s": 0.98,
}


RECONSTRUCTIONS = [
    {
        "name": "mask025_A_wide_left",
        "threshold": 0.25,
        "config": {
            **BASE,
            "top_left_s": 0.12,
            "top_right_s": 0.35,
            "waist_left_w": 0.25,
            "lower_left_s": 0.08,
            "lower_right_s": 0.36,
            "lower_y_h": 0.20,
            "width_top_s": 1.06,
            "width_bottom_s": 1.08,
            "join_fill": [
                {"x_w": 0.68, "y_h": 0.47},
                {"x_w": 0.95, "y_h": 0.40},
                {"x_w": 0.93, "y_h": 0.28},
                {"x_w": 0.67, "y_h": 0.36},
            ],
        },
    },
    {
        "name": "mask050_B_balanced",
        "threshold": 0.50,
        "config": {
            **BASE,
            "top_left_s": 0.18,
            "top_right_s": 0.42,
            "waist_left_w": 0.27,
            "lower_left_s": 0.15,
            "lower_right_s": 0.42,
            "lower_y_h": 0.21,
            "width_top_s": 1.00,
            "width_bottom_s": 1.03,
            "join_fill": [
                {"x_w": 0.68, "y_h": 0.48},
                {"x_w": 0.93, "y_h": 0.40},
                {"x_w": 0.92, "y_h": 0.30},
                {"x_w": 0.67, "y_h": 0.37},
            ],
        },
    },
    {
        "name": "mask075_C_core",
        "threshold": 0.75,
        "config": {
            **BASE,
            "top_left_s": 0.24,
            "top_right_s": 0.48,
            "waist_left_w": 0.30,
            "lower_left_s": 0.22,
            "lower_right_s": 0.46,
            "lower_y_h": 0.22,
            "width_top_s": 0.96,
            "width_bottom_s": 0.99,
            "join_fill": [
                {"x_w": 0.69, "y_h": 0.48},
                {"x_w": 0.91, "y_h": 0.40},
                {"x_w": 0.90, "y_h": 0.31},
                {"x_w": 0.68, "y_h": 0.38},
            ],
        },
    },
]


def run(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def build_font(name: str, config: dict[str, object]) -> Path:
    env = os.environ.copy()
    env["TABUNA_PILOT_Z"] = json.dumps(config, separators=(",", ":"))
    run([str(ROOT / ".venv" / "bin" / "python"), str(ROOT / "scripts" / "build.py")], env=env)
    fonts = OUT / "fonts"
    fonts.mkdir(parents=True, exist_ok=True)
    target = fonts / f"{name}.ttf"
    shutil.copy2(ROOT / "dist" / "TabunaSansVariable.ttf", target)
    return target


def render_and_compare(name: str, font: Path) -> dict[str, object]:
    directory = OUT / name
    directory.mkdir(parents=True, exist_ok=True)
    run([str(ROOT / "build" / "render-pairs"), str(font), str(directory), "64", GLYPH, "2", "400", "axis"])
    run([str(ROOT / ".venv" / "bin" / "python"), str(ROOT / "scripts" / "compare-pixels.py"), str(directory)])
    return json.loads((directory / "comparison.json").read_text())["records"][0]


def bbox(mask: np.ndarray) -> list[int] | None:
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]


def edge(mask: np.ndarray) -> np.ndarray:
    if not mask.any():
        return mask
    return mask & ~ndimage.binary_erosion(mask)


def hard_metrics(name: str, threshold: float, record: dict[str, object]) -> dict[str, object]:
    directory = OUT / name
    ref_img = np.array(Image.open(directory / record["system"]["file"]).convert("L")) / 255.0
    own_img = np.array(Image.open(directory / record["tabuna"]["file"]).convert("L")) / 255.0
    ref = ref_img < (1 - threshold)
    own = own_img < 0.5
    fp_mask = own & ~ref
    fn_mask = ref & ~own
    inter = int((ref & own).sum())
    union = int((ref | own).sum())
    ref_edge = edge(ref)
    own_edge = edge(own)
    dt_to_own_edge = ndimage.distance_transform_edt(~own_edge)
    boundary = float(dt_to_own_edge[ref_edge].mean()) if ref_edge.any() else 0.0
    overlay = np.zeros((*ref.shape, 3), dtype=np.uint8)
    overlay[ref & own] = [160, 160, 160]
    overlay[fn_mask] = [255, 0, 0]
    overlay[fp_mask] = [0, 90, 255]
    Image.fromarray(overlay).save(directory / f"{name}-errors.png")
    return {
        "maskIoU": round(inter / union, 6) if union else 1.0,
        "fp": int(fp_mask.sum()),
        "fn": int(fn_mask.sum()),
        "bboxReference": bbox(ref),
        "bboxRender": bbox(own),
        "bboxDelta": None if bbox(ref) is None or bbox(own) is None else [
            int(a - b) for a, b in zip(bbox(own), bbox(ref))
        ],
        "boundaryDistance": round(boundary, 6),
    }


def measure(name: str, threshold: float, config: dict[str, object]) -> dict[str, object]:
    font = build_font(name, config)
    record = render_and_compare(name, font)
    metrics = hard_metrics(name, threshold, record)
    soft = float(record["inkIoU"])
    row = {
        "variant": name,
        "threshold": threshold,
        "font": str(font),
        "softInkIoU": soft,
        "estimatedMean64": round(CONTROL_MEAN_64 + (soft - CONTROL_Z_IOU) / CONTROL_TOTAL, 9),
        **metrics,
        "config": config,
    }
    (OUT / name / "metrics.json").write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n")
    return row


def px_delta_for(param: str) -> float:
    units = 2 * PX_TO_UNITS
    regular_s = 78 * 1.025
    regular_h = 524
    regular_w = 416
    if param.endswith("_s") or param.startswith("width_"):
        return units / regular_s
    if param.endswith("_h"):
        return units / regular_h
    if param.endswith("_w"):
        return units / regular_w
    raise ValueError(param)


def optimize_points(start: dict[str, object], base_row: dict[str, object]) -> list[dict[str, object]]:
    params = [
        "top_left_s",
        "waist_left_w",
        "lower_left_s",
        "lower_y_h",
        "lower_right_s",
        "top_right_s",
        "width_top_s",
        "width_bottom_s",
    ]
    rows = []
    current = dict(start)
    best_iou = float(base_row["softInkIoU"])
    misses = 0
    for param in params:
        if misses >= 3:
            break
        delta = px_delta_for(param)
        trials = []
        for direction in (-1, 1):
            trial = dict(current)
            trial[param] = float(trial[param]) + direction * delta
            name = f"opt_{len(rows)+1:02d}_{param}_{'minus' if direction < 0 else 'plus'}"
            row = measure(name, 0.75, trial)
            row["changedPoint"] = {"parameter": param, "direction": direction, "deltaApproxPixels": 2}
            trials.append(row)
        accepted = max(trials, key=lambda row: row["softInkIoU"])
        if accepted["softInkIoU"] > best_iou:
            current = dict(accepted["config"])
            best_iou = float(accepted["softInkIoU"])
            accepted["accepted"] = True
            misses = 0
        else:
            accepted["accepted"] = False
            misses += 1
        rows.extend(trials)
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [measure("independent_control", 0.75, BASE)]
    for item in RECONSTRUCTIONS:
        rows.append(measure(item["name"], item["threshold"], item["config"]))
    if max(row["softInkIoU"] for row in rows) <= CONTROL_Z_IOU:
        summary = {
            "glyph": GLYPH,
            "previousDigitBasedControl": {"softInkIoU": CONTROL_Z_IOU, "mean64": CONTROL_MEAN_64},
            "reconstructions": rows,
            "selectedForPointOptimization": None,
            "pointOptimization": [],
            "best": max(rows, key=lambda row: row["softInkIoU"]),
            "accepted": False,
            "stopReason": "All independent stroke reconstructions are below the previous digit-derived control.",
        }
        (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps({
            "out": str(OUT / "summary.json"),
            "accepted": False,
            "bestSoftInkIoU": summary["best"]["softInkIoU"],
            "controlSoftInkIoU": CONTROL_Z_IOU,
        }, ensure_ascii=False))
        return
    selected = min(rows[1:], key=lambda row: (row["boundaryDistance"], row["fn"], row["fp"], -row["softInkIoU"]))
    opt_rows = optimize_points(dict(selected["config"]), selected)
    all_rows = [*rows, *opt_rows]
    summary = {
        "glyph": GLYPH,
        "previousDigitBasedControl": {"softInkIoU": CONTROL_Z_IOU, "mean64": CONTROL_MEAN_64},
        "reconstructions": rows,
        "selectedForPointOptimization": selected["variant"],
        "pointOptimization": opt_rows,
        "best": max(all_rows, key=lambda row: row["softInkIoU"]),
        "notes": [
            "Only glyph з was varied.",
            "The default source contour is independent Cyrillic and can be overwritten from the best config.",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "out": str(OUT / "summary.json"),
        "selected": selected["variant"],
        "bestSoftInkIoU": summary["best"]["softInkIoU"],
        "bestMaskIoU": summary["best"]["maskIoU"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
