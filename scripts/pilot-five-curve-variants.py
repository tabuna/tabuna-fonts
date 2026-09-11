#!/usr/bin/env python3
"""Build and measure Inter-style cubic-node variants for digit five.

The default glyph is left unchanged unless one measured configuration is
manually promoted into refined.py. Variants move existing contour nodes/handles
instead of adding patch polygons.
"""
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
OUT = ROOT / "build" / "pilot-five" / "curve-variants"
GLYPH = "5"
CONTROL_IOU = 0.725204
CONTROL_MEAN_64 = 0.893110
CONTROL_TOTAL = 126
PX_TO_UNITS = 1000 / (64 * 2)


BASE = {
    "top_left_x_s": 0.18,
    "left_wall_y_h": 0.43,
    "upper_left_x_s": 0.82,
    "upper_left_y_h": 0.38,
    "shoulder_c1_x_w": 0.26,
    "shoulder_c1_y_h": 0.48,
    "shoulder_c2_x_w": 0.38,
    "shoulder_c2_y_h": 0.51,
    "shoulder_end_x_w": 0.5266844349680171,
    "shoulder_end_y_h": 0.5571760221760222,
    "right_c1_x_w": 0.82,
    "right_c1_y_h": 0.51,
    "right_c2_x_s": 1.0,
    "right_c2_y_h": 0.43,
    "right_end_x_s": 1.0,
    "right_end_y_h": 0.31217602217602214,
    "lower_top_c1_x_s": 1.0,
    "lower_top_c2_x_w": 0.67,
    "lower_top_end_x_w": 0.45668443496801703,
    "lower_c1_x_w": 0.313315565031983,
    "lower_c2_x_s": 1.1954346466541588,
    "lower_end_x_s": 0.9954346466541589,
    "lower_end_y_h": 0.2121760221760222,
    "left_corner_y_h": 0.17217602217602218,
    "bottom_left_x_w": 0.10331556503198294,
    "bottom_left_y_h": 0.05217602217602217,
    "bottom_c1_x_w": 0.28331556503198296,
    "bottom_c2_x_w": 0.49,
    "bottom_right_c1_x_w": 0.79,
    "bottom_right_c1_y": -10.0,
    "bottom_right_c2_y_h": 0.08,
    "bottom_right_end_y_h": 0.27,
    "outer_c1_y_h": 0.48,
    "outer_c2_x_w": 0.85,
    "outer_c2_y_h": 0.62,
    "outer_end_x_w": 0.6133155650319829,
    "outer_end_y_h": 0.6621760221760222,
    "top_return_c1_x_w": 0.36,
    "top_return_c1_y_h": 0.62,
    "top_return_c2_x_w": 0.23,
    "top_return_c2_y_h": 0.57,
    "top_return_end_x_s": 1.0,
    "top_return_end_y_h": 0.5621760221760222,
}


RECONSTRUCTIONS = [
    {
        "name": "A_lower_bowl_left",
        "reason": "Wider lower-left bowl to reduce the large lower FN island seen in previous maps.",
        "config": {
            **BASE,
            "lower_c1_x_w": 0.22,
            "lower_c2_x_s": 0.72,
            "lower_end_x_s": 0.62,
            "lower_end_y_h": 0.205,
            "left_corner_y_h": 0.18,
            "bottom_left_x_w": 0.03,
            "bottom_left_y_h": 0.04,
            "bottom_c1_x_w": 0.20,
        },
    },
    {
        "name": "B_open_shoulder",
        "reason": "Moves the shoulder and right side as one cubic contour rather than adding a shoulder patch.",
        "config": {
            **BASE,
            "shoulder_end_x_w": 0.56,
            "shoulder_end_y_h": 0.535,
            "right_c1_x_w": 0.82,
            "right_c2_y_h": 0.43,
            "right_end_y_h": 0.29,
            "outer_end_x_w": 0.58,
            "outer_end_y_h": 0.64,
            "top_return_end_y_h": 0.54,
        },
    },
    {
        "name": "C_compact_top_wide_bottom",
        "reason": "Keeps the top compact while widening the bottom curve and lowering the left terminal.",
        "config": {
            **BASE,
            "left_wall_y_h": 0.405,
            "upper_left_y_h": 0.365,
            "lower_top_end_x_w": 0.45,
            "lower_c1_x_w": 0.20,
            "lower_end_x_s": 0.58,
            "left_corner_y_h": 0.17,
            "bottom_right_end_y_h": 0.255,
        },
    },
]


PARAMS = [
    "lower_c1_x_w",
    "lower_c2_x_s",
    "lower_end_x_s",
    "lower_end_y_h",
    "left_corner_y_h",
    "bottom_left_x_w",
    "bottom_left_y_h",
    "bottom_c1_x_w",
    "lower_top_end_x_w",
    "right_end_y_h",
    "shoulder_end_x_w",
    "shoulder_end_y_h",
    "outer_end_x_w",
    "outer_end_y_h",
    "top_return_end_y_h",
]


def run(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def build_font(name: str, config: dict[str, float] | None) -> Path:
    env = os.environ.copy()
    if config is None:
        env.pop("TABUNA_PILOT_FIVE", None)
    else:
        env["TABUNA_PILOT_FIVE"] = json.dumps(config, separators=(",", ":"))
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


def hard_metrics(name: str, record: dict[str, object], threshold: float = 0.5) -> dict[str, object]:
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


def measure(name: str, config: dict[str, float] | None, reason: str = "") -> dict[str, object]:
    font = build_font(name, config)
    record = render_and_compare(name, font)
    soft = float(record["inkIoU"])
    row = {
        "variant": name,
        "font": str(font),
        "softInkIoU": soft,
        "estimatedMean64": round(CONTROL_MEAN_64 + (soft - CONTROL_IOU) / CONTROL_TOTAL, 9),
        "reason": reason,
        **hard_metrics(name, record),
        "config": config or BASE,
    }
    (OUT / name / "metrics.json").write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n")
    return row


def px_delta_for(param: str) -> float:
    units = 2 * PX_TO_UNITS
    regular_s = 78 * 1.025
    regular_h = 1443 / 2.048
    regular_w = 469
    if param.endswith("_s"):
        return units / regular_s
    if param.endswith("_h"):
        return units / regular_h
    if param.endswith("_w"):
        return units / regular_w
    if param.endswith("_y"):
        return units
    raise ValueError(param)


def optimize_points(start: dict[str, float], base_row: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    current = dict(start)
    best_iou = float(base_row["softInkIoU"])
    misses = 0
    for param in PARAMS:
        if misses >= 3:
            break
        delta = px_delta_for(param)
        trials = []
        for direction in (-1, 1):
            trial = dict(current)
            trial[param] = float(trial[param]) + direction * delta
            name = f"opt_{len(rows)+1:02d}_{param}_{'minus' if direction < 0 else 'plus'}"
            row = measure(name, trial, f"Move {param} by {'-' if direction < 0 else '+'}2px equivalent.")
            row["changedPoint"] = {
                "parameter": param,
                "direction": direction,
                "deltaApproxPixels": 2,
            }
            trials.append(row)
        accepted = max(trials, key=lambda row: row["softInkIoU"])
        if accepted["softInkIoU"] > best_iou and accepted["fn"] <= int(base_row["fn"]) + 35:
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
    rows = [measure("control", None, "Default production contour.")]
    for item in RECONSTRUCTIONS:
        rows.append(measure(item["name"], item["config"], item["reason"]))
    selected = max(rows[1:], key=lambda row: (
        row["softInkIoU"],
        -row["boundaryDistance"],
        -row["fn"],
        -row["fp"],
    ))
    if selected["softInkIoU"] <= rows[0]["softInkIoU"]:
        opt_rows: list[dict[str, object]] = []
        selected_for_opt = rows[0]
    else:
        opt_rows = optimize_points(dict(selected["config"]), selected)
        selected_for_opt = selected
    all_rows = [*rows, *opt_rows]
    best = max(all_rows, key=lambda row: row["softInkIoU"])
    summary = {
        "glyph": GLYPH,
        "control": rows[0],
        "reconstructions": rows[1:],
        "selectedForPointOptimization": selected_for_opt["variant"],
        "pointOptimization": opt_rows,
        "best": best,
        "acceptedCandidate": best if best["softInkIoU"] > rows[0]["softInkIoU"] else None,
        "notes": [
            "Only digit 5 was varied.",
            "Variants move existing cubic contour nodes/handles; no patch polygons are added.",
            "The final default build is restored after the pilot run.",
        ],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    build_font("restored-control", None)
    print(json.dumps({
        "out": str(OUT / "summary.json"),
        "controlSoftInkIoU": rows[0]["softInkIoU"],
        "bestVariant": best["variant"],
        "bestSoftInkIoU": best["softInkIoU"],
        "bestMaskIoU": best["maskIoU"],
        "accepted": summary["acceptedCandidate"] is not None,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
