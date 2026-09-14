"""Fit existing El-family tensions to reduce curvature jumps within a small envelope.

Only tangent handle lengths vary. Endpoints, directions, metrics, topology and
stem edges stay fixed. This is an offline candidate generator, never a build hook.
"""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from bezier import point
import el_stem
spec = importlib.util.spec_from_file_location('joins', ROOT/'scripts/audit-curve-joins.py')
joins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(joins)


def sample(drawing):
    return np.array([point(curve,t) for path in joins.contours(drawing)
                     for kind,curve in path if kind=='curveTo'
                     for t in np.linspace(0,1,17)])


def displacement_bound(before, after):
    """Convex-hull bound on |B_new(t)-B_old(t)|, for every t in [0,1]."""
    a = [curve for path in joins.contours(before) for _,curve in path]
    b = [curve for path in joins.contours(after) for _,curve in path]
    assert len(a)==len(b), 'Fairing must preserve topology'
    return float(np.linalg.norm(np.array(a)-np.array(b),axis=2).max())


def fit(p, strength, fraction):
    seed = np.array(p['foot']['handles']).ravel()
    initial = el_stem.construction(p)
    old_points = sample(initial)
    old_joins = joins.audit(initial)
    indices = [i for i,r in enumerate(old_joins) if r['kind']=='smooth']
    def shape(values):
        candidate=copy.deepcopy(p)
        candidate['foot']['handles']=values.reshape(-1,2).tolist()
        return candidate,el_stem.construction(candidate)
    def residual(values):
        _, drawing=shape(values)
        rows=joins.audit(drawing)
        # Smooth robust penalty limits domination by a single tiny radius.
        curvature=np.array([np.log1p(rows[i]['curvature_jump']) for i in indices])
        return np.concatenate(((sample(drawing)-old_points).ravel(), strength*curvature))
    result=least_squares(residual,seed,bounds=(seed*(1-fraction),seed*(1+fraction)),
                         max_nfev=120,ftol=1e-9,xtol=1e-9,gtol=1e-9)
    candidate,drawing=shape(result.x)
    new_joins=joins.audit(drawing)
    return candidate,dict(success=bool(result.success),
        max_sample_displacement=float(np.linalg.norm(sample(drawing)-old_points,axis=1).max()),
        displacement_bound=displacement_bound(initial, drawing),
        max_curvature_jump_before=max(old_joins[i]['curvature_jump'] for i in indices),
        max_curvature_jump_after=max(new_joins[i]['curvature_jump'] for i in indices))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--source',type=Path,default=ROOT/'sources')
    ap.add_argument('--strength',type=float,default=.2)
    ap.add_argument('--fraction',type=float,default=.12)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    report=[]
    for filename in ['el-stem.json','el-stem-lower.json','lj-stem.json','lj-stem-lower.json']:
        data=json.loads((args.source/filename).read_text())
        for weight,profiles in data['weights'].items():
            for optical,p in profiles.items():
                candidate,row=fit(p,args.strength,args.fraction)
                data['weights'][weight][optical]=candidate
                report.append(dict(file=filename,weight=weight,optical=optical,**row))
        (args.out/filename).write_text(json.dumps(data,indent=2)+'\n')
    (args.out/'fairing-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
