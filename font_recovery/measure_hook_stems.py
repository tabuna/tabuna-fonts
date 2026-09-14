"""Locate the straight stems of f/t using fixed horizontal sections."""
import json
from pathlib import Path
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from font_recovery.measure import Flatten,scan


def measure(font,ch,weight,optical):
    glyphs=font.getGlyphSet(location={'wght':weight,'opsz':optical})
    name=font.getBestCmap()[ord(ch)];flat=Flatten(glyphs);bounds=BoundsPen(glyphs)
    glyphs[name].draw(flat);glyphs[name].draw(bounds)
    left,bottom,right,top=bounds.bounds;scale=1000/font['head'].unitsPerEm
    fractions=[.15,.20,.25] if ch=='f' else [.30,.35,.40]
    runs=[scan(flat.contours,bottom+(top-bottom)*v,nonzero=True) for v in fractions]
    assert all(len(r)==1 for r in runs),(ch,weight,optical,runs)
    values=np.array([r[0] for r in runs])*scale
    return dict(left=float(values[:,0].mean()),right=float(values[:,1].mean()),
                width=float((values[:,1]-values[:,0]).mean()),
                straightness_error=float(np.ptp(values,axis=0).max()),
                bounds=[v*scale for v in bounds.bounds])


def main():
    own=TTFont('dist/TabunaSansVariable.ttf');ref=TTFont('/System/Library/Fonts/SFNS.ttf')
    rows=[]
    for ch in 'ft':
        for weight in [100,400,900]:
            for label,a,b in [('text',14,17),('display',28,28)]:
                current=measure(own,ch,weight,a);target=measure(ref,ch,weight,b)
                rows.append(dict(character=ch,weight=weight,optical=label,current=current,reference=target,
                                 stem_left_error=current['left']-target['left'],stem_width_ratio=current['width']/target['width']))
    path=Path('build/font-recovery/hook-stems/measurement.json');path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(rows,indent=2)+'\n')
    for r in rows:print(r['character'],r['weight'],r['optical'],round(r['stem_left_error'],2),round(r['stem_width_ratio'],3))


if __name__=='__main__':main()
