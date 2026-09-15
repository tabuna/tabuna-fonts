#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
"$ROOT/.venv/bin/python" "$ROOT/scripts/build.py"
"$ROOT/.venv/bin/python" "$ROOT/scripts/check_digits.py"
"$ROOT/.venv/bin/python" "$ROOT/scripts/check_timers.py"
"$ROOT/.venv/bin/python" "$ROOT/scripts/web_cache.py"
