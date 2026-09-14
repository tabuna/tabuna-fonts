#!/usr/bin/env python3
"""Render the same alphabet in both fonts and export per-glyph Highlight data."""
from __future__ import annotations
import argparse, json, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
GLYPHS = ("АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
          "абвгдежзийклмнопрстуфхцчшщъыьэюя"
          "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")

def bbox(mask):
    y, x = np.where(mask)
    return [int(x.min()), int(y.min()), int(x.max()+1), int(y.max()+1)] if len(x) else None

def largest(mask, n=5):
    labels, count = ndimage.label(mask)
    rows=[]
    for i in range(1, count+1):
        ys,xs=np.where(labels==i)
        if len(xs): rows.append({"area":int(len(xs)),"bbox":[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]})
    return sorted(rows,key=lambda r:r["area"],reverse=True)[:n]

def thickness(mask):
    """Estimate local filled-stem thickness in raster pixels."""
    if not mask.any(): return {"median":0.0,"mean":0.0,"p90":0.0}
    values = 2.0 * ndimage.distance_transform_edt(mask)[mask]
    return {"median":round(float(np.median(values)),3),
            "mean":round(float(values.mean()),3),
            "p90":round(float(np.percentile(values,90)),3)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--font",type=Path,default=ROOT/"dist/TabunaSansVariable.ttf")
    ap.add_argument("--out",type=Path,default=ROOT/"build/highlight-audit")
    ap.add_argument("--sizes",default="32,64,128")
    ap.add_argument("--chars",default=None,help="Only audit these characters (default: full alphabet)")
    ap.add_argument("--analyze",action="store_true",help="Rank connected FN/FP errors and write a Highlight atlas after rendering")
    ap.add_argument("--verify-repeat",action="store_true",help="Run the same audit a second time and fail if any pixel metrics differ")
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    chars=args.chars or GLYPHS
    result={"font":str(args.font),"glyphs":chars,"sizes":{},"method":"same-origin CoreText renders; threshold 0.5; red=FN, blue=FP, gray=intersection"}
    for size in map(int,args.sizes.split(',')):
        out=args.out/str(size); out.mkdir(parents=True,exist_ok=True)
        subprocess.run([str(ROOT/"build/render-pairs"),str(args.font),str(out),str(size),chars,"2","400","axis"],check=True)
        subprocess.run([str(ROOT/".venv/bin/python"),str(ROOT/"scripts/compare-pixels.py"),str(out)],check=True,stdout=subprocess.DEVNULL)
        data=json.loads((out/"comparison.json").read_text()); rows=[]
        for rec in data["records"]:
            ref=np.asarray(Image.open(out/rec["system"]["file"]).convert("L"))/255
            own=np.asarray(Image.open(out/rec["tabuna"]["file"]).convert("L"))/255
            r=(1-ref)>=.5; o=(1-own)>=.5; fn=r&~o; fp=o&~r; common=r&o
            rgba=np.zeros((*r.shape,3),dtype=np.uint8); rgba[common]=[150,150,150]; rgba[fn]=[235,45,45]; rgba[fp]=[40,95,235]
            Image.fromarray(rgba).save(out/(rec["id"]+"-highlight.png"))
            rt, ot = thickness(r), thickness(o)
            tp=int(common.sum()); fp_n=int(fp.sum()); fn_n=int(fn.sum())
            precision=tp/(tp+fp_n) if tp+fp_n else 1.0
            recall=tp/(tp+fn_n) if tp+fn_n else 1.0
            dice=2*tp/(2*tp+fp_n+fn_n) if 2*tp+fp_n+fn_n else 1.0
            rb, ob = bbox(r), bbox(o)
            rows.append({"character":rec["character"],"codepoint":rec["codepoint"],"iou":rec["inkIoU"],"tp":tp,"fp":fp_n,"fn":fn_n,"precision":round(precision,6),"recall":round(recall,6),"dice":round(dice,6),"errorArea":fp_n+fn_n,"referenceBBox":rb,"renderBBox":ob,"bboxDelta":[ob[i]-rb[i] for i in range(4)] if rb and ob else None,"thickness":{"reference":rt,"render":ot,"deltaMedian":round(ot['median']-rt['median'],3),"deltaMean":round(ot['mean']-rt['mean'],3)},"largestFP":largest(fp),"largestFN":largest(fn),"highlight":f"{size}/{rec['id']}-highlight.png"})
        total_tp=sum(x["tp"] for x in rows); total_fp=sum(x["fp"] for x in rows); total_fn=sum(x["fn"] for x in rows)
        result["sizes"][str(size)]={"meanInkIoU":data["meanInkIoU"],"tp":total_tp,"fp":total_fp,"fn":total_fn,"precision":round(total_tp/(total_tp+total_fp),6) if total_tp+total_fp else 1.0,"recall":round(total_tp/(total_tp+total_fn),6) if total_tp+total_fn else 1.0,"dice":round(2*total_tp/(2*total_tp+total_fp+total_fn),6) if 2*total_tp+total_fp+total_fn else 1.0,"records":rows}
    (args.out/"report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    if args.verify_repeat:
        repeat_out = args.out / "_repeat"
        shutil.rmtree(repeat_out, ignore_errors=True)
        command = [str(ROOT/".venv/bin/python"), str(Path(__file__).resolve()),
                   "--font", str(args.font), "--out", str(repeat_out),
                   "--sizes", args.sizes]
        if args.chars is not None:
            command += ["--chars", args.chars]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
        repeated = json.loads((repeat_out/"report.json").read_text())
        keys = ("iou", "tp", "fp", "fn")
        reproducible = all(
            tuple(a[k] for k in keys) == tuple(b[k] for k in keys)
            for size in result["sizes"]
            for a, b in zip(result["sizes"][size]["records"], repeated["sizes"][size]["records"])
        )
        result["reproducible"] = bool(reproducible)
        (args.out/"report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
        if not reproducible:
            raise SystemExit("repeat audit differs: inspect report.json and _repeat/report.json")
    if args.analyze:
        analyzer = ROOT / "scripts" / "analyze-highlight-errors.py"
        for size in map(int, args.sizes.split(',')):
            subprocess.run([str(ROOT/".venv/bin/python"), str(analyzer), str(args.out/str(size))], check=True, stdout=subprocess.DEVNULL)
        geometry = ROOT / "scripts" / "geometry-audit.py"
        subprocess.run([str(ROOT/".venv/bin/python"), str(geometry), str(args.out)], check=True, stdout=subprocess.DEVNULL)
    summary = {"out":str(args.out/"report.json"),"glyphs":len(chars),"sizes":list(result["sizes"])}
    if args.verify_repeat:
        summary["reproducible"] = result["reproducible"]
    print(json.dumps(summary, ensure_ascii=False))
if __name__ == "__main__": main()
