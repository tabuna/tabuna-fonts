"""A compact full-alphabet proof assembled from audited CoreText bitmaps."""
import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit', type=Path, default=ROOT / 'build/font-recovery/research-v2/audit-complete-alphabet')
    parser.add_argument('--weight', type=int, default=400)
    args = parser.parse_args()
    folder = args.audit / f'wght-{args.weight}/64'
    settings = json.loads((folder / 'render-settings.json').read_text())
    required = json.loads((ROOT / 'font_recovery/data/required-alphabet.json').read_text())
    records = {row['character']: row for row in settings['records']}
    assert all(row['character'] in records for row in required)
    columns, cell_width, cell_height = 13, 132, 190
    margin, heading = 24, 92
    sheet = Image.new('RGB', (margin * 2 + columns * cell_width,
                             heading + math.ceil(len(required) / columns) * cell_height), 'white')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=16)
    title = ImageFont.load_default(size=24)
    draw.text((margin, 18), f'Tabuna Sans Development - weight {args.weight}', font=title, fill='black')
    draw.text((margin, 53), '118 Latin/Russian letters | CoreText 64 pt, 2x | Full coverage; shape quality under review', font=font, fill='#555555')
    for index, row in enumerate(required):
        record = records[row['character']]
        picture = Image.open(folder / record['tabuna']['file']).convert('RGB')
        bounds = ImageChops.invert(picture).getbbox()
        assert bounds, row['character']
        picture = picture.crop(bounds)
        # Same scale for every character; preserve widths and relative sizes.
        picture = picture.resize((round(picture.width * .75), round(picture.height * .75)), Image.Resampling.LANCZOS)
        x = margin + (index % columns) * cell_width
        y = heading + (index // columns) * cell_height
        sheet.paste(picture, (x + (cell_width - picture.width) // 2, y + 12))
        draw.text((x + 25, y + 151), row['codepoint'], font=font, fill='#777777')
    out = args.audit / f'alphabet-wght-{args.weight}.png'
    sheet.save(out)
    print(out)


if __name__ == '__main__':
    main()
