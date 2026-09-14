"""Find retained reference-coordinate literals in the current core sources.

This read-only source comparison is incomplete: a match flags reuse, while
an absence of matches does not prove independent construction.
"""
import ast,json
from pathlib import Path
from fontTools.ttLib import TTFont
font=TTFont('/System/Library/Fonts/SFNS.ttf');cmap=font.getBestCmap();results=[];normalized_calls={}
def character(test):
 for node in ast.walk(test):
  if isinstance(node,ast.Compare) and isinstance(node.left,ast.Name) and node.left.id=='ch' and len(node.ops)==1 and isinstance(node.ops[0],ast.Eq) and isinstance(node.comparators[0],ast.Constant):
   value=node.comparators[0].value
   if isinstance(value,str) and len(value)==1:return value
 return None
def pairs(value):
 if isinstance(value,(list,tuple)):
  if len(value)==2 and all(isinstance(x,(int,float)) for x in value):return [tuple(value)]
  return [point for item in value for point in pairs(item)]
 return []
def walk(node,ch,path):
 if isinstance(node,ast.If):
  for item in node.body:walk(item,character(node.test) or ch,path)
  for item in node.orelse:walk(item,ch,path)
  return
 if ch and ord(ch) in cmap:
  if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='norm' and node.args:
   try:points=pairs(ast.literal_eval(node.args[0]))
   except (ValueError,TypeError):points=[]
   normalized_calls.setdefault((path,ch),[]).extend((node.lineno,p) for p in points)
  candidate=None
  if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):candidate=node.value
  elif isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in ('contour','qcontour') and node.args:candidate=node.args[0]
  if candidate is not None:
   try:points=pairs(ast.literal_eval(candidate))
   except (ValueError,TypeError):points=[]
   if len(points)>=8:
    source=list(map(tuple,font['glyf'][cmap[ord(ch)]].getCoordinates(font['glyf'])[0]));matches=sum(p in source for p in points)
    if matches/len(points)>.95:
     results.append({'file':path,'line':node.lineno,'glyph':ch,'literal_points':len(points),'reference_matches':matches,'reference_point_count':len(source),'interpretation':'Strong evidence of retained reference-coordinate literals; needs independent construction review'})
 for child in ast.iter_child_nodes(node):walk(child,ch,path)
for path in ['scripts/design.py','scripts/refined.py']:walk(ast.parse(Path(path).read_text()),None,path)
for (path,ch),calls in normalized_calls.items():
 source=list(map(tuple,font['glyf'][cmap[ord(ch)]].getCoordinates(font['glyf'])[0]));matches=sum(p in source for _,p in calls)
 if len(calls)>=8 and matches/len(calls)>.95:
  results.append({'file':path,'line':min(line for line,_ in calls),'glyph':ch,'literal_points':len(calls),'reference_matches':matches,'reference_point_count':len(source),'interpretation':'Reference coordinates passed through norm(); affine normalization does not establish independent construction'})
out=Path('build/font-recovery/reports/legacy-coordinate-usage.json');out.write_text(json.dumps({'status':'Incomplete provenance audit; detection is evidence of reuse, absence is not proof of independence','findings':results},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
