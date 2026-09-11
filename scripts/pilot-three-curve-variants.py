#!/usr/bin/env python3
"""Build and measure cubic-node variants for digit three.

This follows the Inter-inspired workflow used for digit five: move existing
outline nodes/handles and reject additive patching as soon as it creates large
FP regions.
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
OUT = ROOT / "build" / "pilot-three" / "curve-variants"
GLYPH = "3"
CONTROL_IOU = 0.716332
CONTROL_MEAN_64 = 0.895685
CONTROL_TOTAL = 126
PX_TO_UNITS = 1000 / (64 * 2)


BASE = {
    "start_y_h": 0.85,
    "top_c1_x_w": 0.12,
    "top_c1_y_h": 0.99,
    "top_c2_x_w": 0.29,
    "top_end_x_w": 0.49,
    "upper_right_c1_x_w": 0.80,
    "upper_right_c2_x_w": 0.98,
    "upper_right_c2_y_h": 0.91,
    "upper_right_end_x_w": 0.98,
    "upper_right_end_y_h": 0.75,
    "upper_side_c1_x_w": 0.98,
    "upper_side_c1_y_h": 0.62,
    "upper_side_c2_x_w": 0.86,
    "upper_side_c2_y_h": 0.55,
    "waist_right_x_w": 0.73,
    "waist_right_y_h": 0.51,
    "mid_c1_x_w": 0.93,
    "mid_c1_y_h": 0.47,
    "mid_c2_y_h": 0.37,
    "lower_right_end_y_h": 0.3021760221760222,
    "bottom_right_c1_y_h": 0.09,
    "bottom_c2_x_w": 0.79,
    "bottom_end_x_w": 0.5226882845188285,
    "bottom_left_c1_x_w": 0.28268828451882844,
    "bottom_left_c2_x_w": 0.08,
    "bottom_left_c2_y_h": 0.07217602217602218,
    "bottom_left_end_y_h": 0.20217602217602217,
    "left_waist_x_s": 1.015434646654159,
    "left_waist_y_h": 0.18,
    "left_waist_y_sy": 0.51,
    "lower_inner_c1_x_w": 0.25,
    "lower_inner_c2_x_w": 0.33,
    "lower_inner_end_x_w": 0.49,
    "lower_inner_right_c1_x_w": 0.72,
    "lower_inner_right_c2_x_s": 1.0,
    "lower_inner_right_c2_y_h": 0.12,
    "lower_inner_right_end_x_s": 1.0,
    "lower_inner_right_end_y_h": 0.28,
    "lower_join_c1_x_s": 1.0,
    "lower_join_c1_y_h": 0.40,
    "lower_join_c2_x_w": 0.74,
    "lower_join_end_x_w": 0.43,
    "waist_left_x_w": 0.28,
    "upper_inner_c1_x_w": 0.70,
    "upper_inner_c2_x_w": 0.98,
    "upper_inner_c2_x_s": 1.0,
    "upper_inner_c2_y_h": 0.63,
    "upper_inner_end_x_w": 0.98,
    "upper_inner_end_x_s": 1.0,
    "upper_inner_end_y_h": 0.75,
    "upper_inner_top_c1_x_w": 0.98,
    "upper_inner_top_c1_x_s": 1.0,
    "upper_inner_top_c2_x_w": 0.69,
    "upper_inner_top_end_x_w": 0.49,
    "top_return_c1_x_w": 0.34,
    "top_return_c2_x_w": 0.24,
    "top_return_c2_y_h": 0.92,
    "top_return_c2_y_sy": 0.12,
    "top_return_end_x_s": 0.77,
    "top_return_end_y_h": 0.85,
    "top_return_end_y_sy": 0.47,
}


RECONSTRUCTIONS = [
    {
        "name": "A_raise_lower_bowl",
        "reason": "Raises the lower outer bowl and left terminal as one closed contour.",
        "config": {
            **BASE,
            "lower_right_end_y_h": 0.28,
            "bottom_right_c1_y_h": 0.09,
            "bottom_left_end_y_h": 0.18,
            "left_waist_y_h": 0.18,
            "lower_inner_right_end_y_h": 0.28,
        },
    },
    {
        "name": "B_tighter_waist",
        "reason": "Tightens the middle connection without adding a waist patch.",
        "config": {
            **BASE,
            "waist_right_x_w": 0.69,
            "waist_right_y_h": 0.50,
            "mid_c1_x_w": 0.90,
            "lower_join_end_x_w": 0.40,
            "waist_left_x_w": 0.30,
            "upper_inner_c1_x_w": 0.66,
        },
    },
    {
        "name": "C_open_upper_bowl",
        "reason": "Opens the upper right bowl and shifts the return curve upward.",
        "config": {
            **BASE,
            "upper_right_end_y_h": 0.78,
            "upper_side_c2_y_h": 0.58,
            "waist_right_y_h": 0.53,
            "upper_inner_end_y_h": 0.78,
            "top_return_end_y_h": 0.87,
        },
    },
]


PARAMS = [
    "lower_right_end_y_h",
    "bottom_right_c1_y_h",
    "bottom_end_x_w",
    "bottom_left_c1_x_w",
    "bottom_left_c2_y_h",
    "bottom_left_end_y_h",
    "left_waist_x_s",
    "left_waist_y_h",
    "lower_inner_right_end_y_h",
    "lower_join_c1_y_h",
    "lower_join_end_x_w",
    "waist_left_x_w",
    "waist_right_x_w",
    "waist_right_y_h",
    "upper_right_end_y_h",
    "upper_side_c2_y_h",
    "upper_inner_end_y_h",
    "top_return_end_y_h",
]


def run(cmd: list[str], *, env: dict[str, str] | None = None) -> None:
    subprocess.run(cmd, cwd=ROOT, env=env, check=True)


def build_font(name: str, config: dict[str, float] | None) -> Path:
    env = os.environ.copy()
    if config is None:
        env.pop("TABUNA_PILOT_THREE", None)
    else:
        env["TABUNA_PILOT_THREE"] = json.dumps(config, separators=(",", ":"))
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
    regular_w = 478
    if param.endswith("_s") or param.endswith("_sy"):
        return units / regular_s
    if param.endswith("_h"):
        return units / regular_h
    if param.endswith("_w"):
        return units / regular_w
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
        if accepted["softInkIoU"] > best_iou and accepted["fp"] <= int(base_row["fp"]) + 60:
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
    selected = max(rows, key=lambda row: (
        row["softInkIoU"],
        -row["boundaryDistance"],
        -row["fn"],
        -row["fp"],
    ))
    opt_rows = optimize_points(dict(selected["config"]), selected)
    all_rows = [*rows, *opt_rows]
    best = max(all_rows, key=lambda row: row["softInkIoU"])
    summary = {
        "glyph": GLYPH,
        "control": rows[0],
        "reconstructions": rows[1:],
        "selectedForPointOptimization": selected["variant"],
        "pointOptimization": opt_rows,
        "best": best,
        "acceptedCandidate": best if best["softInkIoU"] > rows[0]["softInkIoU"] else None,
        "notes": [
            "Only digit 3 was varied.",
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
