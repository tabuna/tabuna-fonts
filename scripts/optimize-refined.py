#!/usr/bin/env python3
"""Small, reproducible coordinate search for refined glyph parameters.

The optimizer intentionally edits only a marked parameter block in refined.py,
renders isolated glyphs with the project's existing CoreText renderer, and
scores the resulting pixel proofs. It never imports contours from another font.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFINED = ROOT / "scripts" / "refined.py"
BUILD = ROOT / "build" / "optimizer"

def render_and_score(font: Path, out: Path, glyph: str, weight: int, sizes: list[int]) -> float:
    out.mkdir(parents=True, exist_ok=True)
    scores = []
    for size in sizes:
        run = out / str(size)
        subprocess.run([str(ROOT / "build" / "render-pairs"), str(font), str(run), str(size), glyph, "2", str(weight), "axis"], check=True, stdout=subprocess.DEVNULL)
        subprocess.run([str(ROOT / ".venv" / "bin" / "python"), str(ROOT / "scripts" / "compare-pixels.py"), str(run)], check=True, stdout=subprocess.DEVNULL)
        data = json.loads((run / "comparison.json").read_text())
        scores.append(float(data["records"][0]["inkIoU"]))
    return sum(scores) / len(scores)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("font", type=Path)
    ap.add_argument("--glyph", default="к")
    ap.add_argument("--weight", type=int, default=400)
    ap.add_argument("--sizes", default="32,64,128", help="comma-separated pixel sizes")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if not args.font.is_absolute(): args.font = ROOT / args.font
    source = REFINED.read_text()
    if "# OPTIMIZER-REFINED-BEGIN" not in source:
        raise SystemExit("refined.py needs an OPTIMIZER-REFINED-BEGIN marker before optimization")
    if args.dry_run:
        print(json.dumps({"glyph": args.glyph, "weight": args.weight, "sizes": args.sizes, "status": "ready"}, ensure_ascii=False))
        return
    if not args.run:
        raise SystemExit("use --run to execute the build/render sweep")
    if args.glyph != "к":
        raise SystemExit("initial optimizer supports only к")
    marker = re.compile(r"d\.polygon\(\[\(s\*\.50,h\*\.41\),\(s\*\.50,h\*\.41\+s\*\.([0-9.]+)\)")
    lower = re.compile(r"d\.polygon\(\[\(w\*\.37,h\*\.57\),\(w\*\.37\+s\*\.([0-9.]+),h\*\.57\)")
    sizes = [int(x) for x in args.sizes.split(",") if x.strip()]
    best = (-1.0, source)
    for u in (0.80, 0.84, 0.88):
        for l in (0.80, 0.84, 0.88):
            candidate = marker.sub(lambda m: m.group(0).replace(f"s*.{m.group(1)}", "s*" + f"{u:.2f}"[1:]), source, count=1)
            candidate = lower.sub(lambda m: m.group(0).replace(f"s*.{m.group(1)}", "s*" + f"{l:.2f}"[1:]), candidate, count=1)
            REFINED.write_text(candidate)
            subprocess.run([str(ROOT / ".venv" / "bin" / "python"), str(ROOT / "scripts" / "build.py")], check=True, stdout=subprocess.DEVNULL)
            score = render_and_score(ROOT / "dist" / "TabunaSansVariable.ttf", BUILD / f"{u:.2f}-{l:.2f}", args.glyph, args.weight, sizes)
            if score > best[0]: best = (score, candidate)
    REFINED.write_text(best[1])
    subprocess.run([str(ROOT / ".venv" / "bin" / "python"), str(ROOT / "scripts" / "build.py")], check=True, stdout=subprocess.DEVNULL)
    um = marker.search(best[1])
    lm = lower.search(best[1])
    print(json.dumps({"glyph": args.glyph, "bestIoU": best[0], "status": "accepted",
                      "parameters": {"upper": float(um.group(1)), "lower": float(lm.group(1))}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
