"""Read-only SFNS table inventory. Never exports a font or edits source geometry."""
from pathlib import Path
import json,importlib,hashlib
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/font-recovery/sfns-analysis'
SOURCE=Path('/System/Library/Fonts/SFNS.ttf')
def simple(v):
    if isinstance(v,(str,int,float,bool)) or v is None:return v
    if isinstance(v,bytes):return {'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()}
    if isinstance(v,(list,tuple)):return [simple(x) for x in v]
    if isinstance(v,dict):return {str(k):simple(x) for k,x in v.items()}
    if hasattr(v,'__dict__'):return {k:simple(x) for k,x in vars(v).items() if not k.startswith('_')}
    return str(v)
def main():
    assert json.loads((ROOT/'build/font-recovery/baseline/summary.json').read_text())['reproducible']
    OUT.mkdir(parents=True,exist_ok=True)
    f=TTFont(SOURCE,lazy=False)
    libs={}
    for name in ['fontTools','uharfbuzz','freetype','PIL','numpy','cv2','scipy','fontmake']:
        try:
            m=importlib.import_module(name);libs[name]={'available':True,'version':getattr(m,'__version__','see baseline package inventory')}
        except ImportError as e:libs[name]={'available':False,'error':str(e)}
    tags='cmap glyf loca head hhea hmtx maxp name OS/2 post fvar gvar avar HVAR VVAR STAT kern GPOS GSUB prep fpgm cvt gasp hdmx trak opbd'.split()
    tables={}
    for requested in tags:
        tag='cvt ' if requested=='cvt' else requested
        if tag not in f:tables[requested]={'present':False};continue
        tab=f[tag];rec={'present':True,'length':f.reader.tables[tag].length,'decoded_class':type(tab).__name__}
        if tag in ['head','hhea','OS/2','maxp','post','fvar','avar','STAT','gasp','trak','opbd']:rec['data']=simple(tab)
        elif tag=='cmap':rec['subtables']=[{'format':x.format,'platformID':x.platformID,'platEncID':x.platEncID,'entries':len(getattr(x,'cmap',{}))} for x in tab.tables]
        elif tag=='glyf':rec.update(simple_count=sum(not f['glyf'][g].isComposite() for g in f.getGlyphOrder()),composite_count=sum(f['glyf'][g].isComposite() for g in f.getGlyphOrder()))
        elif tag=='loca':rec.update(entries=len(tab.locations),monotonic=all(a<=b for a,b in zip(tab.locations,tab.locations[1:])))
        elif tag=='hmtx':rec['metrics']=simple(tab.metrics)
        elif tag=='name':rec['records']=[{'id':n.nameID,'platform':n.platformID,'language':n.langID,'value':n.toUnicode(errors='replace')} for n in tab.names]
        elif tag=='gvar':rec.update(glyphs=len(tab.variations),tuples=sum(len(v) for v in tab.variations.values()))
        elif tag in ['GPOS','GSUB']:
            t=tab.table;rec['features']=[x.FeatureTag for x in t.FeatureList.FeatureRecord] if t.FeatureList else [];rec['lookup_types']=[x.LookupType for x in t.LookupList.Lookup] if t.LookupList else []
        elif tag in ['HVAR','VVAR']:rec['data']=simple(tab)
        elif tag in ['prep','fpgm']:rec['instructions']=tab.program.getAssembly()
        elif tag=='cvt ':rec['values']=list(tab.values)
        else:rec['data']=simple(tab)
        tables[requested]=rec
    result={'file':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'font_name':f['name'].getDebugName(1),'version':f['name'].getDebugName(5),'unitsPerEm':f['head'].unitsPerEm,'glyph_count':len(f.getGlyphOrder()),'table_tags':list(f.keys()),'tables':tables,'cmap':{f'U+{k:04X}':v for k,v in f.getBestCmap().items()},'variation_axes':[{'tag':a.axisTag,'name':f['name'].getDebugName(a.axisNameID),'min':a.minValue,'default':a.defaultValue,'max':a.maxValue,'semantics':'pending measured phase 4'} for a in f['fvar'].axes] if 'fvar' in f else [],'libraries':libs,'documentation':'https://developer.apple.com/fonts/TrueType-Reference-Manual/','phase':2,'completed':True}
    (OUT/'font-info.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['font_name','unitsPerEm','glyph_count','variation_axes','libraries']},ensure_ascii=False))
if __name__=='__main__':main()
