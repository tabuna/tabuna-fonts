"""Demonstrate continuous weight changes using one variable TTF in FreeType."""
import argparse
import hashlib
import json
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', type=Path, default=ROOT / 'build/generated-font/tabuna-sans-complete/TabunaSansVariable.ttf')
    parser.add_argument('--out', type=Path, default=ROOT / 'build/font-recovery/reports/weight-range.png')
    args = parser.parse_args()
    binary = TTFont(args.font)
    axes = binary['fvar'].axes
    weight_axis = next(axis for axis in axes if axis.axisTag == 'wght')
    assert (weight_axis.minValue, weight_axis.maxValue) == (100, 900)
    text = 'Tabuna Sans Привет'
    assert all(ord(character) in binary.getBestCmap() for character in text)
    sheet = Image.new('RGB', (1150, 980), 'white')
    draw = ImageDraw.Draw(sheet)
    label = ImageFont.load_default(size=20)
    draw.text((32, 20), 'One variable TTF | wght 100-900 | FreeType rendering', fill='#333333', font=label)
    signatures = []
    for row, weight in enumerate(range(100, 901, 100)):
        font = ImageFont.truetype(str(args.font), 66)
        font.set_variation_by_axes([weight if axis.axisTag == 'wght' else axis.defaultValue for axis in axes])
        y = 68 + row * 96
        draw.text((32, y + 24), str(weight), font=label, fill='#777777')
        draw.text((110, y), text, font=font, fill='black')
        signatures.append(hashlib.sha256(sheet.crop((110, y, 1150, y + 95)).tobytes()).hexdigest())
    assert len(set(signatures)) == 9, 'Some weight samples rendered identically'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out)
    args.out.with_suffix('.json').write_text(json.dumps({
        'font': str(args.font), 'font_sha256': hashlib.sha256(args.font.read_bytes()).hexdigest(),
        'weights': list(range(100, 901, 100)), 'distinct_rendered_samples': len(set(signatures)),
        'renderer': 'Pillow FreeType, directly from the same variable TTF',
        'purpose': 'Weight behavior demonstration; not a CoreText raster acceptance audit',
    }, indent=2) + '\n')
    print(args.out)


if __name__ == '__main__':
    main()
