"""Check sampled compiled contours for proper crossings at varied locations."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from font_recovery.measure import Flatten


def crossings(contours):
    starts = np.concatenate([np.asarray(c) for c in contours])
    ends = np.concatenate([np.roll(np.asarray(c), -1, axis=0) for c in contours])
    vectors = ends-starts
    def cross(a, b):
        return a[...,0]*b[...,1]-a[...,1]*b[...,0]
    a = cross(vectors[:,None], starts[None]-starts[:,None])
    b = cross(vectors[:,None], ends[None]-starts[:,None])
    hits = a*b < -1e-10
    return int((hits & hits.T).sum()//2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--characters', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--within-contours', action='store_true',
                        help='Check each contour separately when same-winding component overlaps are intentional')
    args = parser.parse_args()
    font = TTFont(args.font)
    failures, checked = [], 0
    for weight in [100,150,250,400,500,600,700,800,900]:
        for optical in [9,14,16,20,28,64,128]:
            glyphs = font.getGlyphSet(location={'wght':weight,'opsz':optical})
            for character in args.characters:
                pen = Flatten(glyphs)
                glyphs[font.getBestCmap()[ord(character)]].draw(pen)
                count = (sum(crossings([c]) for c in pen.contours)
                         if args.within_contours else crossings(pen.contours))
                checked += 1
                if count:
                    failures.append({'character':character, 'weight':weight,
                                     'optical':optical, 'crossings':count})
    report = {'font_sha256':hashlib.sha256(args.font.read_bytes()).hexdigest(),
              'characters':args.characters,
              'weights':[100,150,250,400,500,600,700,800,900],
              'optical_sizes':[9,14,16,20,28,64,128],
              'checked':checked, 'failures':failures,
              'between_contours_checked':not args.within_contours,
              'method':'Pairwise proper intersections of sampled compiled contours; not an exact analytic proof'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
    assert not failures


if __name__ == '__main__':
    main()
