#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
"$ROOT/.venv/bin/python" "$ROOT/scripts/build.py"

# Keep the CSS font URL in lockstep with the generated manifest. Without this
# cache-buster, browsers can keep an older WOFF2 even after a fresh build.
ROOT="$ROOT" "$ROOT/.venv/bin/python" - <<'PY'
import hashlib
import os
from pathlib import Path

root = Path(os.environ["ROOT"])
version = hashlib.sha256((root / "dist" / "TabunaSansVariable.woff2").read_bytes()).hexdigest()[:12]
css_path = root / "dist" / "tabuna.css"
css = css_path.read_text()
import re
updated, count = re.subn(r"(TabunaSansVariable\.woff2\?v=)[^\"') ]+", rf"\g<1>{version}", css)
if count != 1:
    raise SystemExit(f"expected one font URL in {css_path}, found {count}")
css_path.write_text(updated)
index_path = root / "index.html"
index_path.write_text(re.sub(r"(TabunaSansVariable\.woff2\?v=)[a-f0-9]+", rf"\g<1>{version}", index_path.read_text()))
print(f"web cache-buster: {version}")
PY
