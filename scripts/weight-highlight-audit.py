#!/usr/bin/env python3
"""Audit variable-font weight instances against the native system reference.

Renders the same glyph set at several ``wght`` values and reports mask error
and filled-stem thickness separately.  This is intentionally independent of
the regular 400-point audit so weight failures cannot hide in a mean IoU.
"""
from pathlib import Path
import argparse, json, shutil, subprocess
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHARS = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

def bbox(mask):
    ys, xs = np.where(mask)
    return [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)] if len(xs) else None

def thickness(mask):
    from scipy import ndimage
    if not mask.any():
        return {"median": 0.0, "mean": 0.0, "p90": 0.0}
    values = 2.0 * ndimage.distance_transform_edt(mask)[mask]
    return {"median": round(float(np.median(values)), 3),
            "mean": round(float(values.mean()), 3),
            "p90": round(float(np.percentile(values, 90)), 3)}

def connected(mask):
    from scipy import ndimage
    labels, count = ndimage.label(mask)
    areas = []
    for i in range(1, count + 1):
        ys, xs = np.where(labels == i)
        if len(xs):
            areas.append({"area": int(len(xs)), "bbox": [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)]})
    return sorted(areas, key=lambda x: x["area"], reverse=True)[:5]

def audit_instance(directory, weight, size):
    data = json.loads((directory / "comparison.json").read_text())
    rows = []
    for rec in data["records"]:
        ref = np.asarray(Image.open(directory / rec["system"]["file"]).convert("L")) / 255.0
        own = np.asarray(Image.open(directory / rec["tabuna"]["file"]).convert("L")) / 255.0
        r = (1 - ref) >= 0.5
        o = (1 - own) >= 0.5
        common, fp, fn = r & o, o & ~r, r & ~o
        # Same visual convention as highlight-audit.py: shared ink is gray,
        # false negatives red, and false positives blue.
        highlight = np.zeros((*r.shape, 3), dtype=np.uint8)
        highlight[common] = [150, 150, 150]
        highlight[fn] = [235, 45, 45]
        highlight[fp] = [40, 95, 235]
        Image.fromarray(highlight).save(directory / (rec["id"] + "-highlight.png"))
        rt, ot = thickness(r), thickness(o)
        rb, ob = bbox(r), bbox(o)
        rows.append({
            "character": rec["character"], "codepoint": rec["codepoint"],
            "iou": rec["inkIoU"],
            "advanceDifference": rec["advanceDifference"],
            "customFallback": rec["customFallback"],
            "referenceFallback": rec["referenceFallback"],
            "hasInk": bool(r.any() or o.any()),
            "tp": int(common.sum()), "fp": int(fp.sum()), "fn": int(fn.sum()),
            "referenceBBox": rb, "renderBBox": ob,
            "bboxDelta": [ob[i]-rb[i] for i in range(4)] if rb and ob else None,
            "thickness": {"reference": rt, "render": ot,
                          "deltaMedian": round(ot["median"]-rt["median"], 3),
                          "deltaMean": round(ot["mean"]-rt["mean"], 3),
                          "deltaP90": round(ot["p90"]-rt["p90"], 3)},
            "largestFP": connected(fp), "largestFN": connected(fn),
            "highlight": f"wght-{weight}/{size}/{rec['id']}-highlight.png",
        })
    return {"weight": weight, "size": size, "meanInkIoU": data["meanInkIoU"],
            "tp": sum(x["tp"] for x in rows), "fp": sum(x["fp"] for x in rows),
            "fn": sum(x["fn"] for x in rows), "records": rows}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", type=Path, default=ROOT / "dist/TabunaSansVariable.ttf")
    ap.add_argument("--out", type=Path, default=ROOT / "build/weight-highlight-audit")
    ap.add_argument("--weights", default="100,400,800")
    ap.add_argument("--sizes", default="64")
    ap.add_argument("--chars", default=None)
    ap.add_argument("--verify-repeat", action="store_true")
    args = ap.parse_args()
    chars = args.chars or DEFAULT_CHARS
    weights = [int(x) for x in args.weights.split(",")]
    sizes = [int(x) for x in args.sizes.split(",")]
    args.out.mkdir(parents=True, exist_ok=True)
    instances = []
    for weight in weights:
        for size in sizes:
            folder = args.out / f"wght-{weight}" / str(size)
            shutil.rmtree(folder, ignore_errors=True)
            folder.mkdir(parents=True, exist_ok=True)
            subprocess.run([str(ROOT / "build/render-pairs"), str(args.font), str(folder),
                            str(size), chars, "2", str(weight), "axis"], check=True)
            subprocess.run([str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/compare-pixels.py"),
                            str(folder)], check=True, stdout=subprocess.DEVNULL)
            instances.append(audit_instance(folder, weight, size))
    by_weight = {}
    for w in weights:
        group = [x for x in instances if x["weight"] == w]
        by_weight[str(w)] = {
            "meanInkIoU": round(float(np.mean([x["meanInkIoU"] for x in group])), 6),
            "fp": sum(x["fp"] for x in group), "fn": sum(x["fn"] for x in group),
            "thicknessDeltaMean": round(float(np.mean([r["thickness"]["deltaMean"] for x in group for r in x["records"]])), 3),
            "thicknessDeltaMedian": round(float(np.median([r["thickness"]["deltaMedian"] for x in group for r in x["records"]])), 3),
            "thicknessDiagnosis": (
                "rendered glyphs are systematically thicker than reference"
                if float(np.mean([r["thickness"]["deltaMean"] for x in group for r in x["records"]])) > 0.25
                else "rendered glyphs are systematically thinner than reference"
                if float(np.mean([r["thickness"]["deltaMean"] for x in group for r in x["records"]])) < -0.25
                else "no systematic thickness bias; inspect glyph-specific errors"
            ),
            "largestThicknessMismatches": sorted([
                {"character": r["character"], "deltaMean": r["thickness"]["deltaMean"],
                 "deltaMedian": r["thickness"]["deltaMedian"], "iou": r["iou"], "fp": r["fp"], "fn": r["fn"]}
                for x in group for r in x["records"]
            ], key=lambda r: abs(r["deltaMean"]), reverse=True)[:20],
            "largestMaskErrors": sorted([
                {"character": r["character"], "iou": r["iou"], "fp": r["fp"], "fn": r["fn"],
                 "errorArea": r["fp"] + r["fn"]}
                for x in group for r in x["records"]
            ], key=lambda r: r["errorArea"], reverse=True)[:20],
        }
    result = {"font": str(args.font), "glyphs": chars, "weights": weights, "sizes": sizes,
              "method": "CoreText axis reference; threshold 0.5; thickness=2×distance-transform radius",
              "byWeight": by_weight, "instances": instances}
    (args.out / "report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    if args.verify_repeat:
        repeat = args.out / "_repeat"
        cmd = [str(ROOT / ".venv/bin/python"), str(Path(__file__).resolve()), "--font", str(args.font),
               "--out", str(repeat), "--weights", args.weights, "--sizes", args.sizes, "--chars", chars]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        a = json.loads((args.out / "report.json").read_text())
        b = json.loads((repeat / "report.json").read_text())
        keys = [(inst["weight"], inst["size"], rec["character"], rec["iou"], rec["fp"], rec["fn"])
                for inst in a["instances"] for rec in inst["records"]]
        keys2 = [(inst["weight"], inst["size"], rec["character"], rec["iou"], rec["fp"], rec["fn"])
                 for inst in b["instances"] for rec in inst["records"]]
        result["reproducible"] = keys == keys2
        (args.out / "report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        if not result["reproducible"]:
            raise SystemExit("weight audit differs on repeat")
    print(json.dumps({"out": str(args.out / "report.json"), "weights": weights,
                      "sizes": sizes, "glyphs": len(chars),
                      "reproducible": result.get("reproducible")}, ensure_ascii=False))

if __name__ == "__main__":
    main()
