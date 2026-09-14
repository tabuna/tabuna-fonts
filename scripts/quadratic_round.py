"""Round contour made from eight G1 quadratic arcs, expressed as cubics."""
from geometry import Drawing


def elevate(a,c,b):
    return (tuple(a[i]+2*(c[i]-a[i])/3 for i in (0,1)),tuple(b[i]+2*(c[i]-b[i])/3 for i in (0,1)),b)


def contour(bounds,quadrants):
    l,b,r,t=bounds;d=Drawing();segments=[];start=None
    for rotation,(a,c,mix) in enumerate(quadrants):
        control1=(0,a);control2=(c,1);middle=(mix*c,(1-mix)*a+mix)
        def point(p):
            x,y=p[0]/2,.5+p[1]/2
            for _ in range(rotation):x,y=y,1-x
            return (l+x*(r-l),b+y*(t-b))
        p0,p1,p2,p3,p4=map(point,[(0,0),control1,middle,control2,(1,1)])
        if start is None:start=p0
        segments.extend([elevate(p0,p1,p2),elevate(p2,p3,p4)])
    d.outline(start,segments);return d
