"""Stable quadratic spline topology for the authored dollar model.

A calibration curve asks cu2qu for exactly N segments; it is never emitted.
This keeps spline topology stable while Bezier parameters vary.
"""
from fontTools.cu2qu.cu2qu import curves_to_quadratic
from fontTools.pens.recordingPen import RecordingPen
COUNTS={'dollar':[3,3,3,4,3,3,4,3,3,5,3,3]}
CALIBRATION=[(0,0),(0,1),(1,1),(1,0)]
ERRORS={2:.1,3:.02,4:.01,5:.005}

def convert(curve,count):
 result=curves_to_quadratic([curve,CALIBRATION],[1e9,ERRORS[count]])[0]
 assert len(result)==count+2
 return result

def apply(font):
 for key,counts in COUNTS.items():
  glyph=font[key];record=RecordingPen();glyph.draw(record);glyph.clearContours();pen=glyph.getPen();index=0;current=None
  for op,points in record.value:
   if op=='curveTo':
    result=convert([current,*points],counts[index]);pen.qCurveTo(*result[1:]);index+=1
   else:getattr(pen,op)(*points)
   if points:current=points[-1]
  assert index==len(counts)
