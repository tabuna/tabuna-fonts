"""Update full coverage with measured changes and proven unchanged outlines."""
import argparse,copy,hashlib,json
from pathlib import Path
from fontTools.ttLib import TTFont


def main():
    ap=argparse.ArgumentParser()
    for name in ['base','delta','impact','comparison','out']:ap.add_argument('--'+name,type=Path,required=True)
    args=ap.parse_args();base=json.loads(args.base.read_text());delta=json.loads((args.delta/'report.json').read_text())
    impact=json.loads(args.impact.read_text());comparison=json.loads(args.comparison.read_text())
    assert base['font_sha256']==impact['before_sha256']
    assert delta['reproducible'] and comparison['repeat_verified'] and comparison['renderer_and_reference_pixels_equal']
    before=TTFont(impact['before']);after=TTFont(impact['after'])
    assert before['head'].unitsPerEm==after['head'].unitsPerEm
    assert hashlib.sha256(Path(impact['after']).read_bytes()).hexdigest()==impact['after_sha256']
    expected={chr(cp) for cp,name in after.getBestCmap().items() if name in impact['including_components']}
    assert set(delta['glyphs'])==expected,'Every changed mapped glyph must be measured'
    rows={(r['codepoint'],r['weight'],r['size']):copy.deepcopy(r) for r in base['all_cases']}
    replacements=set()
    for instance in delta['instances']:
        settings=json.loads((args.delta/f"wght-{instance['weight']}"/str(instance['size'])/'render-settings.json').read_text())
        assert settings['fontSHA256']==impact['after_sha256']
        for r in instance['records']:
            key=(r['codepoint'],instance['weight'],instance['size']);assert key in rows
            total=r['tp']+r['fp']+r['fn'];old=rows[key]
            old.update(mask_iou=r['tp']/total if total else None,ink_iou=r['iou'],advance_difference=r['advanceDifference'],
                       has_ink=r['hasInk'],custom_fallback=r['customFallback'],reference_fallback=r['referenceFallback'],fp=r['fp'],fn=r['fn'])
            replacements.add(key)
    assert replacements=={key for key,r in rows.items() if r['character'] in expected},'Missing changed weight/size cases'
    result=copy.deepcopy(base);result['all_cases']=list(rows.values());result['font_sha256']=impact['after_sha256']
    result['evidence']=dict(method='Full measured baseline plus measured delta; unchanged glyph geometry and metrics certified by impact proof',base=str(args.base),delta=str(args.delta),impact=str(args.impact),comparison=str(args.comparison),replaced_cases=len(replacements),reused_cases=len(rows)-len(replacements))
    result['worst_ink_cases']=sorted((r for r in rows.values() if r['mask_iou'] is not None),key=lambda r:r['mask_iou'])[:100]
    result['fallback_cases']=[r for r in rows.values() if r['custom_fallback'] or r['reference_fallback']]
    result['whitespace']=[r for r in rows.values() if r['codepoint'] in ['U+0020','U+00A0']]
    for item in result['per_character']:
        cases=[r for r in rows.values() if r['character']==item['character']];ink=[r for r in cases if r['mask_iou'] is not None]
        item['worst_ink_case']=min(ink,key=lambda r:r['mask_iou']) if ink else None
        item['maximum_advance_difference']=max(abs(r['advance_difference']) for r in cases)
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['evidence']))


if __name__=='__main__':main()
