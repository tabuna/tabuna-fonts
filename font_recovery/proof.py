"""Make a specimen from the actual CoreText audit images, without rerendering."""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--audit', type=Path, default=ROOT / 'build/font-recovery/research-v2/audit-shared-cyrillic')
    parser.add_argument('--out', type=Path, default=ROOT / 'build/font-recovery/research-v2/specimen.png')
    args = parser.parse_args()
    report = json.loads((args.audit / 'report.json').read_text())
    characters, weights = report['glyphs'], [100, 400, 800]
    images = {}
    boxes = []
    for weight in weights:
        folder = args.audit / f'wght-{weight}/64'
        settings = json.loads((folder / 'render-settings.json').read_text())
        for row in settings['records']:
            picture = Image.open(folder / row['tabuna']['file']).convert('RGB')
            images[weight, row['character']] = picture
            boxes.append(ImageChops.invert(picture).getbbox())
    crop = (min(b[0] for b in boxes) - 10, min(b[1] for b in boxes) - 10,
            max(b[2] for b in boxes) + 10, max(b[3] for b in boxes) + 10)
    cell_width, cell_height = crop[2] - crop[0], crop[3] - crop[1]
    sheet = Image.new('RGB', (90 + cell_width * len(characters), 95 + (cell_height + 30) * len(weights)), 'white')
    draw = ImageDraw.Draw(sheet)
    label_font = ImageFont.load_default(size=17)
    draw.text((20, 15), 'Tabuna Sans Development - independent parametric templates', fill='black', font=label_font)
    draw.text((20, 42), 'CoreText audit images, 64 pt at 2x. Incomplete character set.', fill='#666666', font=label_font)
    for row, weight in enumerate(weights):
        y = 80 + row * (cell_height + 30)
        draw.text((20, y + cell_height // 2), str(weight), fill='#666666', font=label_font)
        for column, character in enumerate(characters):
            x = 90 + column * cell_width
            sheet.paste(images[weight, character].crop(crop), (x, y))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out)
    print(args.out)


if __name__ == '__main__':
    main()
