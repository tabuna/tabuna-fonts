#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
FONT="$ROOT/dist/TabunaSansVariable.ttf"
RENDER="$ROOT/build/render-pairs"
# Keep the web proof set aligned with the full Highlight audit, including
# uppercase Cyrillic glyphs that are otherwise absent from render-pairs' demo
# default (for example the reconstructed `Я`).
CHARS='АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
if [ ! -x "$RENDER" ]; then
  swiftc "$ROOT/scripts/render-pairs.swift" -o "$RENDER"
fi
for size in 16 32 64 128; do
  out="$ROOT/proofs/pixel-$size"
  mkdir -p "$out"
  "$RENDER" "$FONT" "$out" "$size" "$CHARS"
  "$ROOT/.venv/bin/python" "$ROOT/scripts/compare-pixels.py" "$out"
done
