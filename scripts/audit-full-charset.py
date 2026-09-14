"""Audit every required compact character, including punctuation and spaces."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--weights',default='100,200,300,400,500,600,700,800,900')
    ap.add_argument('--sizes',default='16,64');ap.add_argument('--out',type=Path,default=ROOT/'build/font-recovery/full-charset-audit')
    ap.add_argument('--summarize-only',action='store_true')
    ap.add_argument('--font',type=Path,default=ROOT/'dist/TabunaSansVariable.ttf')
    args=ap.parse_args()
    chars=''.join(sorted(set((ROOT/'sources/compact-charset.txt').read_text().replace('\n','').replace('\r','')),key=ord))
    font=TTFont(args.font)
    assert set(map(ord,chars))==set(font.getBestCmap()), 'Audit scope must equal the shipped cmap'
    required=json.loads((ROOT/'sources/quality-scope.json').read_text())['codepoints']
    assert {f'U+{ord(c):04X}' for c in chars}==set(required), 'Must cover the complete explicit user list'
    if not args.summarize_only:
        subprocess.run([sys.executable,str(ROOT/'scripts/weight-highlight-audit.py'),
                        '--font',str(args.font),'--out',str(args.out),
                        '--weights',args.weights,'--sizes',args.sizes,'--chars',chars,'--verify-repeat'],check=True)
    d=json.loads((args.out/'report.json').read_text())
    repeat=json.loads((args.out/'_repeat/report.json').read_text())
    assert d['instances']==repeat['instances'], 'Full geometry, spacing and fallback records must reproduce'
    assert d['reproducible'] and len(d['instances'])==len(args.weights.split(','))*len(args.sizes.split(','))
    rows=[]
    font_hashes=set()
    for instance in d['instances']:
        folder=args.out/f"wght-{instance['weight']}"/str(instance['size'])
        font_hashes.add(json.loads((folder/'render-settings.json').read_text())['fontSHA256'])
        assert {r['codepoint'] for r in instance['records']}=={f'U+{ord(c):04X}' for c in chars}
        for row in instance['records']:
            union=row['tp']+row['fp']+row['fn']
            rows.append(dict(character=row['character'],codepoint=row['codepoint'],
                             weight=instance['weight'],size=instance['size'],
                             mask_iou=row['tp']/union if union else None,ink_iou=row['iou'],
                             advance_difference=row['advanceDifference'],has_ink=row['hasInk'],
                             custom_fallback=row['customFallback'],reference_fallback=row['referenceFallback'],
                             fp=row['fp'],fn=row['fn']))
    assert len(font_hashes)==1, 'A full audit cannot mix different font builds'
    assert font_hashes=={hashlib.sha256(args.font.read_bytes()).hexdigest()}, 'Audit does not describe the selected font'
    per_character=[]
    for c in chars:
        cases=[r for r in rows if r['character']==c]
        ink=[r for r in cases if r['mask_iou'] is not None]
        per_character.append(dict(character=c,codepoint=f'U+{ord(c):04X}',cases=len(cases),
            worst_ink_case=min(ink,key=lambda r:r['mask_iou']) if ink else None,
            maximum_advance_difference=max(abs(r['advance_difference']) for r in cases)))
    summary=dict(characters=len(chars),cases=len(rows),repeat_verified=True,
                 font_sha256=next(iter(font_hashes)),per_character=per_character,
                 whitespace=[r for r in rows if r['codepoint'] in ['U+0020','U+00A0']],
                 worst_ink_cases=sorted((r for r in rows if r['mask_iou'] is not None),key=lambda r:r['mask_iou'])[:100],
                 fallback_cases=[r for r in rows if r['custom_fallback'] or r['reference_fallback']],
                 all_cases=rows)
    (args.out/'quality-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['all_cases','worst_ink_cases','whitespace','fallback_cases','per_character']}))


if __name__=='__main__':main()
