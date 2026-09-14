#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ ! -x build/render-pairs ]]; then
  mkdir -p build
  swiftc scripts/render-pairs.swift -o build/render-pairs
fi
exec .venv/bin/python scripts/weight-highlight-audit.py "$@"
