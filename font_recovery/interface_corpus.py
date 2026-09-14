"""Compare wrapping and clipping in the fixed interface corpus with HarfBuzz.

This checks layout and conservative outline extents. It does not replace
native/browser visual review or a readability study with people.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import uharfbuzz as hb

ROOT = Path(__file__).resolve().parents[1]


class Typesetter:
    def __init__(self, path):
        self.data = Path(path).read_bytes()
        self.face = hb.Face(self.data)
        self.upm = self.face.upem
        self.font = hb.Font(self.face)

    def location(self, weight, optical):
        self.font.set_variations({'wght': weight, 'opsz': optical})
        self.shape.cache_clear()

    @lru_cache(maxsize=4096)
    def shape(self, text, language):
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        if language != 'mixed':
            buffer.language = language
        hb.shape(self.font, buffer)
        cursor = 0
        boxes = []
        for info, position in zip(buffer.glyph_infos, buffer.glyph_positions):
            if not info.codepoint:
                raise ValueError(f'Missing glyph while shaping {text!r}')
            extent = self.font.get_glyph_extents(info.codepoint)
            if extent and (extent.width or extent.height):
                left = cursor + position.x_offset + extent.x_bearing
                top = position.y_offset + extent.y_bearing
                boxes.append((left, top + extent.height, left + extent.width, top))
            cursor += position.x_advance
        bounds = (min(x[0] for x in boxes), min(x[1] for x in boxes),
                  max(x[2] for x in boxes), max(x[3] for x in boxes)) if boxes else (0, 0, 0, 0)
        return cursor / self.upm, tuple(x / self.upm for x in bounds)

    def layout(self, fixture):
        language, width = fixture['language'], fixture['width_em']
        if 'text' in fixture:
            lines, current = [], ''
            for word in fixture['text'].split(' '):
                proposed = f'{current} {word}' if current else word
                if current and self.shape(proposed, language)[0] > width:
                    lines.append(current)
                    current = word
                else:
                    current = proposed
            if current:
                lines.append(current)
        else:
            lines = fixture['lines']
        padding = fixture['padding_em']
        rows = []
        for text in lines:
            advance, (left, bottom, right, top) = self.shape(text, language)
            rows.append(dict(text=text, advance_em=advance,
                             overflow=advance > width,
                             clipped=(left < -padding or right > width + padding
                                      or bottom < -.35-padding or top > 1+padding),
                             ink_bounds_em=[left, bottom, right, top]))
        return rows


def compare(before, after, corpus):
    fonts = [Typesetter(before), Typesetter(after)]
    failures, cases, max_advance_change = [], 0, 0
    locations = set()
    for weight in corpus['weights']:
        for size in corpus['sizes_px']:
            for optical_mode in corpus['optical_sizes']:
                optical = max(9, min(128, size)) if optical_mode == 'auto' else optical_mode
                locations.add((weight, optical))
                for font in fonts:
                    font.location(weight, optical)
                for fixture in corpus['fixtures']:
                    a, b = [font.layout(fixture) for font in fonts]
                    case = dict(fixture=fixture['id'], weight=weight,
                                size_px=size, optical_size=optical_mode)
                    cases += 1
                    if [x['text'] for x in a] != [x['text'] for x in b]:
                        failures.append(dict(**case, reason='line breaks changed', before=a, after=b))
                        continue
                    for old, new in zip(a, b):
                        max_advance_change = max(max_advance_change,
                                                 abs(new['advance_em']-old['advance_em']) * size)
                        if (new['clipped'] and not old['clipped']) or (new['overflow'] and not old['overflow']):
                            failures.append(dict(**case, reason='new clipping or overflow', before=old, after=new))
    digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    return dict(status='passed' if not failures else 'failed',
                before_sha256=digest(before), font_sha256=digest(after),
                method='HarfBuzz shaping, word wrapping, and conservative glyph extents; theme does not change layout geometry.',
                fixture_count=len(corpus['fixtures']), layout_cases=cases,
                distinct_axis_locations=len(locations), themes=corpus['themes'],
                maximum_advance_change_px=max_advance_change, failures=failures,
                visual_review_required=True, human_readability_study=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, default=ROOT/'dist/TabunaSansVariable.ttf')
    parser.add_argument('--corpus', type=Path, default=ROOT/'sources/interface-corpus.json')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    corpus = json.loads(args.corpus.read_text())
    result = compare(args.before, args.after, corpus)
    result['corpus_sha256'] = hashlib.sha256(args.corpus.read_bytes()).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'failures'}))
    if result['failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
