#!/usr/bin/env python3
"""Fingerprint the font, then CSS/JS, so cached HTML dependencies stay coherent."""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def refresh(root=ROOT):
    font_hash = digest(root/'dist/TabunaSansVariable.woff2')
    css_path = root/'dist/tabuna.css'
    css, count = re.subn(r'(TabunaSansVariable\.woff2)(?:\?v=[^"\s)]+)?',
                         rf'\1?v={font_hash}', css_path.read_text())
    if count != 1:
        raise ValueError(f'Expected one font source, found {count}')
    css_path.write_text(css)
    assets = ['dist/TabunaSansVariable.woff2', 'dist/tabuna.css', 'demo.css', 'demo.js', 'sources/charset.js']
    for page in root.glob('*.html'):
        text = page.read_text()
        for asset in assets:
            token = digest(root/asset)
            text = re.sub(r'((?:href|src)="'+re.escape(asset)+r')(?:\?v=[^" ]+)?(")',
                          rf'\1?v={token}\2', text)
        page.write_text(text)
    print('Web font fingerprint:', font_hash)


if __name__ == '__main__':
    refresh()
