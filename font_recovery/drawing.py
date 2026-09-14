"""Original outline primitives. No external font data is read by this module.

Curves are cubic Beziers. A center-line stroke is a nonzero union of positive simple pieces on a
fixed subdivision grid shared by every master.
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
        """Sweep a positive-width pen along a cubic center line.

        Each chord is a clockwise rectangle, joined by clockwise circles.
        Their nonzero union remains valid even when a thick stroke exceeds
        the local bend radius. A fixed cubic sampling schedule keeps masters
        compatible; endpoints retain butt caps. No signed offset can fold
        backwards and cut a spurious white hole into a heavy stroke.
        """
        points = [start]
        current = start
        for segment in segments:
            if len(segment) == 2 and isinstance(segment[0], (int, float)):
                points.append(segment)
            else:
                a, b, c, d = current, *segment
                for step in range(1, 25):
                    t = step / 24
                    v = 1 - t
                    points.append((
                        a[0]*v**3 + 3*b[0]*v*v*t + 3*c[0]*v*t*t + d[0]*t**3,
                        a[1]*v**3 + 3*b[1]*v*v*t + 3*c[1]*v*t*t + d[1]*t**3,
                    ))
            current = points[-1]
        radius = width / 2
        for a, b in zip(points, points[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = max(hypot(dx, dy), 1e-8)
            nx, ny = -dy / length * radius, dx / length * radius
            self.polygon([(a[0]+nx, a[1]+ny), (b[0]+nx, b[1]+ny),
                          (b[0]-nx, b[1]-ny), (a[0]-nx, a[1]-ny)])
        joints = points[:-1] if points[0] == points[-1] else points[1:-1]
        for x, y in joints:
            self.ellipse(x-radius, y-radius, x+radius, y+radius)

    def line(self,a,b,s): self.stroke(a,[b],s)
