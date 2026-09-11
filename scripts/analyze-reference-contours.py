#!/usr/bin/env python3
"""Export ordered reference paths and masks, with inner and outer paths separate."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from ordered_contours import isocontours, signed_area

ROOT = Path(__file__).resolve().parents[1]


def contains(path, point):
    x, y = point
    a, b = path, np.roll(path, -1, axis=0)
    indices = np.flatnonzero((a[:, 1] > y) != (b[:, 1] > y))
    hits = a[indices, 0]+(y-a[indices, 1])*(b[indices, 0]-a[indices, 0])/(b[indices, 1]-a[indices, 1])
    return bool(np.count_nonzero(x < hits) % 2)


def simplify(points, tolerance=.6):
    """Pin extrema; add points only at the largest local contour deviation."""
    pinned = sorted(set(int(f(points[:, dim])) for dim in (0, 1) for f in (np.argmin, np.argmax)))
    chosen = set(pinned)
    closed = np.vstack([points, points])
    def split(start, end):
        part = closed[start:end+1]
        vector = part[-1]-part[0]
        fraction = np.clip((part-part[0])@vector/max(vector@vector, 1e-12), 0, 1)
        distance = np.linalg.norm(part-part[0]-fraction[:, None]*vector, axis=1)
        index = int(np.argmax(distance))
        if distance[index] > tolerance and 0 < index < len(part)-1:
            chosen.add((start+index) % len(points))
            split(start, start+index)
            split(start+index, end)
    for a, b in zip(pinned, pinned[1:]+[pinned[0]+len(points)]):
        split(a, b)
    return [{'index': i, 'point': points[i].tolist(),
             'reason': 'extremum' if i in pinned else 'maximum local contour deviation'} for i in sorted(chosen)]


def bbox(mask):
    yy, xx = np.where(mask)
    return [int(xx.min()), int(yy.min()), int(xx.max()+1), int(yy.max()+1)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT/'build/full-score/64')
    parser.add_argument('--out', type=Path, default=ROOT/'build/reference-contours')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    data = json.loads((args.source/'comparison.json').read_text())
    rows = []
    for ch in 'ЯкКзЗ53':
        r = next(r for r in data['records'] if r['character'] == ch)
        ink = 1-np.asarray(Image.open(args.source/r['system']['file']).convert('L'), dtype=float)/255
        own = 1-np.asarray(Image.open(args.source/r['tabuna']['file']).convert('L'), dtype=float)/255
        thresholds = {}
        for threshold in (.25, .5, .75):
            loops = isocontours(ink, threshold)
            maskfile = f'{ord(ch):04X}-mask-{threshold:.2f}.png'
            Image.fromarray(np.uint8(ink >= threshold)*255).save(args.out/maskfile)
            contours = []
            for i, path in enumerate(loops):
                depth = sum(contains(other, path[0]) for j, other in enumerate(loops) if i != j)
                contours.append({'role': 'inner' if depth % 2 else 'outer', 'nestingDepth': depth,
                                 'areaPixels': abs(signed_area(path)), 'orderedPoints': path.tolist(),
                                 'controlPointCandidates': simplify(path)})
            thresholds[str(threshold)] = {'maskFile': maskfile, 'bbox': bbox(ink >= threshold), 'contours': contours}
        a, b = ink >= .5, own >= .5
        rows.append({'character': ch, 'bbox': bbox(a), 'iou': r['inkIoU'],
                     'fp': int((b & ~a).sum()), 'fn': int((a & ~b).sum()),
                     'bboxDifference': [y-x for x, y in zip(bbox(a), bbox(b))], 'thresholds': thresholds})
    result = {'version': 2, 'fontSHA256': data['fontSHA256'], 'coordinateSystem': 'image pixels; pixel centres at half-integers',
              'method': 'Ordered marching-squares isocontours from grayscale coverage; nested paths distinguish external and internal contours.',
              'note': 'Replaces unordered row-major edge samples. Candidates preserve extrema and maximum local deviation; they are not fitted Bezier handles.',
              'glyphs': rows}
    (args.out/'report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'out': str(args.out/'report.json'), 'glyphs': len(rows)}))


if __name__ == '__main__': main()
