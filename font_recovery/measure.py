"""Measurements only; outline records are not generation templates."""
import math
import numpy as np
from fontTools.pens.basePen import BasePen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
CHARS='oO0cCGsSb dpqnhmuae2358ЯRкKзЗК'.replace(' ','')
CHARS=''.join(dict.fromkeys(CHARS))
class Flatten(BasePen):
    def __init__(self,gs):super().__init__(gs);self.contours=[];self.handles=[];self.segments=[]
    def _moveTo(self,p):self.contours.append([p])
    def _lineTo(self,p):self.contours[-1].append(p);self.segments.append('line')
    def _qCurveToOne(self,c,p):
        a=self._getCurrentPoint();self.handles.append([math.dist(a,c),math.dist(c,p)]);self.segments.append('quadratic')
        self.contours[-1].extend([tuple((1-t)**2*a[i]+2*(1-t)*t*c[i]+t*t*p[i] for i in (0,1)) for t in np.linspace(0,1,33)[1:]])
    def _curveToOne(self,c,d,p):
        a=self._getCurrentPoint();self.segments.append('cubic');self.contours[-1].extend([tuple((1-t)**3*a[i]+3*(1-t)**2*t*c[i]+3*(1-t)*t*t*d[i]+t**3*p[i] for i in (0,1)) for t in np.linspace(0,1,49)[1:]])
    def _closePath(self):pass
    def _endPath(self):pass

def scan(contours,level,vertical=False,nonzero=False):
    xs=[];events=[]
    for c in contours:
        for a,b in zip(c,c[1:]+c[:1]):
            if vertical:a=a[::-1];b=b[::-1]
            if (a[1]<=level<b[1]) or (b[1]<=level<a[1]):
                x=a[0]+(level-a[1])*(b[0]-a[0])/(b[1]-a[1])
                xs.append(x);events.append((x,1 if b[1]>a[1] else -1))
    if nonzero:
        winding=0;start=None;runs=[]
        grouped={}
        for x,sign in events:grouped[x]=grouped.get(x,0)+sign
        for x,sign in sorted(grouped.items()):
            previous=winding;winding+=sign
            if previous==0 and winding!=0:start=x
            elif previous!=0 and winding==0 and x-start>1e-10:runs.append([start,x])
        return runs
    xs.sort();return [[a,b] for a,b in zip(xs[::2],xs[1::2])]

def measure(f,ch,coordinates=False):
    name=f.getBestCmap().get(ord(ch))
    if name is None:return {'character':ch,'missing':True}
    gs=f.getGlyphSet();g=f['glyf'][name];coords,ends,flags=g.getCoordinates(f['glyf']);p=Flatten(gs);gs[name].draw(p)
    bp=BoundsPen(gs);gs[name].draw(bp);bounds=bp.bounds
    ap=AreaPen(gs);gs[name].draw(ap)
    adv,lsb=f['hmtx'][name];xmin,ymin,xmax,ymax=bounds;upm=f['head'].unitsPerEm
    contours=[];start=0
    for end,c in zip(ends,p.contours):
        arr=np.array(c);cross=arr[:,0]*np.roll(arr[:,1],-1)-np.roll(arr[:,0],-1)*arr[:,1];area=float(cross.sum()/2)
        contours.append({'point_range':[start,int(end)],'point_count':int(end-start+1),'direction':'CCW' if area>0 else 'CW','sampled_signed_area':area,'bbox':[float(arr[:,0].min()),float(arr[:,1].min()),float(arr[:,0].max()),float(arr[:,1].max())]});start=end+1
    inner=[c['bbox'] for c in contours if c['direction']=='CCW']
    center=((xmin+xmax)/2,(ymin+ymax)/2)
    horizontal=scan(p.contours,center[1]);vertical=scan(p.contours,center[0],True)
    rotated=[[((x+y)/math.sqrt(2),(y-x)/math.sqrt(2)) for x,y in c] for c in p.contours]
    diagonal=scan(rotated,(center[1]-center[0])/math.sqrt(2))
    height=f['OS/2'].sxHeight if ch.islower() else f['OS/2'].sCapHeight
    lengths=[v for pair in p.handles for v in pair]
    # Area-weighted polygon centroid, holes have opposite sign.
    sums=np.zeros(3)
    for c in p.contours:
        a=np.array(c);b=np.roll(a,-1,axis=0);cr=a[:,0]*b[:,1]-b[:,0]*a[:,1];sums += [cr.sum(),((a[:,0]+b[:,0])*cr).sum(),((a[:,1]+b[:,1])*cr).sum()]
    optical=[float(sums[1]/(3*sums[0])),float(sums[2]/(3*sums[0]))] if sums[0] else list(center)
    row={'character':ch,'unicode':f'U+{ord(ch):04X}','glyph_name':name,'glyph_id':f.getGlyphID(name),'type':'composite' if g.isComposite() else 'simple','contour_count':len(ends),'point_count':len(coords),'on_curve_count':sum(bool(x&1) for x in flags),'off_curve_count':sum(not x&1 for x in flags),'segment_types':p.segments,'contours':contours,'components':[{'name':c.getComponentInfo()[0],'transform':c.getComponentInfo()[1]} for c in getattr(g,'components',[])],'bbox':list(bounds),'advance_width':adv,'left_sidebearing':lsb,'right_sidebearing':adv-lsb-(xmax-xmin),'contour_area':abs(ap.value),'signed_area':ap.value,'stem_vertical':min((b-a for a,b in horizontal),default=None),'stem_horizontal':min((b-a for a,b in vertical),default=None),'stem_diagonal':min((b-a for a,b in diagonal),default=None),'counter_width':max((b[2]-b[0] for b in inner),default=0),'counter_height':max((b[3]-b[1] for b in inner),default=0),'counter_bboxes':inner,'quadratic_handle_lengths':p.handles,'mean_handle_length':float(np.mean(lengths)) if lengths else 0,'overshoot_top':max(0,ymax-height),'overshoot_bottom':max(0,-ymin) if ch not in 'gpqy' else None,'optical_center':optical,'extrema':{'xMin':xmin,'yMin':ymin,'xMax':xmax,'yMax':ymax},'overlap_flag':any(x&64 for x in flags),'overlap_geometry':'not determined by flag; no overlap inferred','bowl_dimensions':[xmax-xmin,ymax-ymin] if ch in 'oO0' else None,'bowl_radius':None,'aperture':None,'measurement_limitations':['Stem = shortest center scan interval, a proxy unreliable for branched/diagonal glyphs.','Counter = bbox of CCW contour; open counters not measured.','No circular bowl radius assumed; aperture needs class-specific terminal landmarks.','Contour direction and centroid from quadratic sampling at 32 subdivisions.','Overshoot excludes known descenders; other structural protrusions require class labels.']}
    if coordinates:
        row['coordinates']={'font_units':[list(x) for x in coords],'baseline_relative':[list(x) for x in coords],'em':[[x/upm,y/upm] for x,y in coords],'x_height':[[x/f['OS/2'].sxHeight,y/f['OS/2'].sxHeight] for x,y in coords],'cap_height':[[x/f['OS/2'].sCapHeight,y/f['OS/2'].sCapHeight] for x,y in coords]};row['flags']=list(flags);row['end_points']=list(ends)
    return row
if __name__=='__main__':
    from fontTools.ttLib import TTFont
    from pathlib import Path
    import json
    out=Path('build/font-recovery/sfns-analysis');assert json.loads((out/'font-info.json').read_text())['completed']
    f=TTFont('/System/Library/Fonts/SFNS.ttf');data={'phase':3,'completed':True,'location':'fvar defaults','glyphs':[measure(f,c,True) for c in CHARS],'limitations':'Unidentifiable semantic measures are null, never fabricated. Raw analytic coordinates must not be imported by generator.'}
    (out/'glyph-outlines.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('Measured',len(data['glyphs']),'glyphs')
