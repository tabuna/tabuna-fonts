#!/usr/bin/env python3
"""Pixel audit for the complete web-font control alphabet."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLYPHS = (
    "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    "абвгдежзийклмнопрстуфхцчшщъыьэюя"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
)


def main() -> None:
    out_root = ROOT / "build" / "full-score"
    rows = []
    for size in (32, 64, 128):
        out = out_root / str(size)
        out.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [str(ROOT / "build" / "render-pairs"), str(ROOT / "dist" / "TabunaSansVariable.ttf"),
             str(out), str(size), GLYPHS, "2", "400", "axis"], check=True)
        subprocess.run(
            [str(ROOT / ".venv" / "bin" / "python"), str(ROOT / "scripts" / "compare-pixels.py"),
             str(out)], check=True)
        data = json.loads((out / "comparison.json").read_text())
        rows.append({"size": size, "total": data["total"],
                     "exactMatches": data["exactMatches"], "meanInkIoU": data["meanInkIoU"]})
    records = json.loads(((out_root / "64") / "comparison.json").read_text())["records"]
    result = {"glyphs": len(GLYPHS), "sizes": rows,
              "meanInkIoU": sum(row["meanInkIoU"] for row in rows) / len(rows),
              "worst64px": [{"character": row["character"], "inkIoU": row["inkIoU"]}
                            for row in sorted(records, key=lambda row: row["inkIoU"])[:20]]}
    (ROOT / "build" / "full-score.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
