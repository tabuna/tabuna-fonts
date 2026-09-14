"""Verify literal coordinate reuse in the existing baseline without modifying it."""
import ast,json
from pathlib import Path
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
f=TTFont('/System/Library/Fonts/SFNS.ttf');out=[]
for file,var,ch in [('scripts/refined.py','sfns_points','5'),('scripts/design.py','sfns_contours','K')]:
    tree=ast.parse((ROOT/file).read_text())
    n=next((n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==var for t in n.targets)), None)
    if n is None:
        out.append({'file':file,'glyph':ch,'literal_present':False,'interpretation':'Previously identified literal removed; absence alone does not prove independent construction.'})
        continue
    pts=ast.literal_eval(n.value)
    if var=='sfns_contours':pts=[p for c in pts for p in c]
    coords,ends,flags=f['glyf'][f.getBestCmap()[ord(ch)]].getCoordinates(f['glyf'])
    raw=[tuple(p) for p in coords]
    out.append({'file':file,'line':n.lineno,'glyph':ch,'literal_point_count':len(pts),'source_point_count':len(raw),'points_equal_in_order':pts==raw,'matching_point_multiset':sorted(pts)==sorted(raw),'matching_points':sum(p in raw for p in pts),'interpretation':'Exact font-unit tuple equality before normalization; transforming coordinates does not establish an independent construction.'})
p=ROOT/'build/font-recovery/project-analysis/provenance.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
