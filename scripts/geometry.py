"""Original outline primitives. No external font data is read by this module.

Curves are cubic Beziers. A centre-line ribbon is offset analytically, then
approximated by cubics on a fixed subdivision grid shared by every master.
This keeps the editable source contours interpolation-compatible.
"""
from math import hypot
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen


def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def mul(a, k): return (a[0] * k, a[1] * k)
def lerp(a, b, t): return add(mul(a, 1-t), mul(b, t))


class Drawing:
    def __init__(self):
        self.pen = RecordingPen()

    def replay(self, pen, transform=(1, 0, 0, 1, 0, 0)):
        output = TransformPen(pen, transform)
        if transform[0]*transform[3]-transform[1]*transform[2] < 0:
            from fontTools.pens.reverseContourPen import ReverseContourPen
            output = ReverseContourPen(output)
        self.pen.replay(output)

    def polygon(self, points):
        # All solid contours clockwise; counters explicitly reversed.
        area = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points, points[1:]+points[:1]))
        if area > 0: points = list(reversed(points))
        p = self.pen
        p.moveTo(points[0])
        for pt in points[1:]: p.lineTo(pt)
        p.closePath()

    def outline(self, start, segments, counter=False):
        """An explicitly designed filled contour, with normalized winding."""
        from fontTools.pens.areaPen import AreaPen
        from fontTools.pens.reverseContourPen import ReverseContourPen
        p=RecordingPen();p.moveTo(start)
        for seg in segments:
            if len(seg)==2 and isinstance(seg[0],(int,float)):p.lineTo(seg)
            else:p.curveTo(*seg)
        p.closePath()
        area=AreaPen();p.replay(area)
        reverse=(area.value>0) != counter
        p.replay(ReverseContourPen(self.pen) if reverse else self.pen)

    def rect(self, x, y, w, h):
        self.polygon([(x,y), (x,y+h), (x+w,y+h), (x+w,y)])

    def ellipse(self, l, b, r, t, reverse=False):
        k = .5522847498307936
        cx,cy=(l+r)/2,(b+t)/2
        rx,ry=(r-l)/2,(t-b)/2
        d=RecordingPen()
        d.moveTo((l,cy))
        d.curveTo((l,cy+k*ry),(cx-k*rx,t),(cx,t))
        d.curveTo((cx+k*rx,t),(r,cy+k*ry),(r,cy))
        d.curveTo((r,cy-k*ry),(cx+k*rx,b),(cx,b))
        d.curveTo((cx-k*rx,b),(l,cy-k*ry),(l,cy))
        d.closePath()
        if reverse:
            from fontTools.pens.reverseContourPen import ReverseContourPen
            d.replay(ReverseContourPen(self.pen))
        else: d.replay(self.pen)

    def ring(self, l, b, r, t, sx, sy=None):
        sy = sy if sy is not None else sx*.93
        self.ellipse(l,b,r,t)
        self.ellipse(l+sx,b+sy,r-sx,t-sy,reverse=True)

    def stroke(self, start, segments, width):
        """Segments: end point for a line, or (control1, control2, end)."""
        curves=[]
        q=start
        for seg in segments:
            if len(seg)==2 and isinstance(seg[0], (int,float)):
                curves.append((q,lerp(q,seg,1/3),lerp(q,seg,2/3),seg))
                q=seg
            else:
                curves.append((q,*seg))
                q=seg[-1]
        sides=[]
        for sign in (1,-1):
            chain=[]
            for points in curves:
                def offset(t):
                    a,b,c,d=points
                    v=1-t
                    xy=add(add(mul(a,v**3),mul(b,3*v*v*t)),add(mul(c,3*v*t*t),mul(d,t**3)))
                    der=add(add(mul(sub(b,a),3*v*v),mul(sub(c,b),6*v*t)),mul(sub(d,c),3*t*t))
                    length=max(hypot(*der),1e-8)
                    return add(xy,(-der[1]/length*width/2*sign,der[0]/length*width/2*sign))
                def derivative(t):
                    a,b=max(0,t-1e-5),min(1,t+1e-5)
                    return mul(sub(offset(b),offset(a)),1/(b-a))
                for j in range(6):
                    a,b=j/6,(j+1)/6
                    p0,p3=offset(a),offset(b)
                    p1=add(p0,mul(derivative(a),(b-a)/3))
                    p2=sub(p3,mul(derivative(b),(b-a)/3))
                    chain.append((p0,p1,p2,p3))
            sides.append(chain)
        p=self.pen
        if start==q:
            # Closed centre lines have no end caps. Draw the two offset rings
            # separately so duplicate cap segments cannot survive compilation.
            for side,reverse in ((sides[0],False),(sides[1],True)):
                curves_side=[(d,c,b,a) for a,b,c,d in reversed(side)] if reverse else side
                p.moveTo(curves_side[0][0]);last=curves_side[0][0]
                for a,b,c,d in curves_side:
                    if hypot(*sub(a,last))>1e-6:p.lineTo(a)
                    p.curveTo(b,c,d);last=d
                p.closePath()
            return
        p.moveTo(sides[0][0][0])
        last=sides[0][0][0]
        for a,b,c,d in sides[0]:
            if hypot(*sub(a,last))>1e-6: p.lineTo(a)
            p.curveTo(b,c,d)
            last=d
        p.lineTo(sides[1][-1][-1])
        last=sides[1][-1][-1]
        for a,b,c,d in reversed(sides[1]):
            if hypot(*sub(d,last))>1e-6: p.lineTo(d)
            p.curveTo(c,b,a)
            last=a
        p.closePath()

    def line(self,a,b,s): self.stroke(a,[b],s)
