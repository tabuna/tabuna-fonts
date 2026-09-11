"""Original punctuation, mathematical signs and combining marks."""
from geometry import Drawing


def mark(design, char):
    d=Drawing(); s=design.s*.78; y=0
    if char=='\u0300':d.line((-94,148),(34,20),s)
    elif char=='\u0301':d.line((-34,20),(94,148),s)
    elif char=='\u0302':
        d.stroke((-120,20),[(0,140),(120,20)],s*.83)
    elif char=='\u0303':
        d.stroke((-142,48),[((-85,171),(59,-25),(142,107))],s*.80)
    elif char=='\u0304':d.rect(-130,60,260,s*.83)
    elif char=='\u0306':d.stroke((-130,133),[((-111,-4),(111,-4),(130,133))],s*.85)
    elif char=='\u0307':d.ellipse(-max(32,s*.54),45,max(32,s*.54),45+max(64,s*1.08))
    elif char=='\u0308':
        z=max(56,s*.90)
        d.ellipse(-126,44,-126+z,44+z);d.ellipse(126-z,44,126,44+z)
    elif char=='\u030A':d.ring(-93,0,93,186,min(s*.72,53))
    elif char=='\u030B':
        d.line((-106,15),(-17,147),s*.78);d.line((30,15),(119,147),s*.78)
    elif char=='\u030C':d.stroke((-120,142),[(0,22),(120,142)],s*.83)
    elif char=='\u0327':
        d.stroke((10,0),[(-35,-64),((108,-43),(85,-195),(-49,-152))],s*.75)
    elif char=='\u0328':
        d.stroke((51,0),[((-124,-130),(-23,-193),(70,-123))],s*.75)
    elif char=='\u0326':
        d.stroke((19,-48),[((37,-118),(3,-157),(-44,-182))],s*.78)
    else:raise KeyError(char)
    return d


def symbol(design,ch):
    d=Drawing();s=design.s;sy=s*.9;H=710;h=design.h; w=400
    dot=max(69,s*1.04)
    def line(a,b,sw=s):d.line(a,b,sw)
    def path(a,*segs,sw=s):d.stroke(a,list(segs),sw)
    if ch in '.,:;!¡':
        w=dot
        if ch in '.,':d.ellipse(0,0,dot,dot)
        if ch in ',;':path((dot*.71,dot*.67),((dot*1.07,-28),(dot*.22,-108),(-17,-110)),sw=dot*.50)
        if ch in ':;':d.ellipse(0,h*.72,dot,h*.72+dot);d.ellipse(0,0,dot,dot)
        if ch in '!¡':
            y=H if ch=='!' else h
            d.ellipse(0,0 if ch=='!' else y-dot,dot,dot if ch=='!' else y)
            d.polygon([(0,y),(dot,y),(dot*.85,dot*1.88),(dot*.15,dot*1.88)]) if ch=='!' else d.polygon([(0,-180),(dot,-180),(dot*.85,y-dot*1.9),(dot*.15,y-dot*1.9)])
    elif ch in '?¿':
        w=405
        path((s*.50,H*.82),((s*.8,H+12-sy/2),(w-s/2,H+12-sy/2),(w-s/2,H*.76)),
             ((w-s/2,H*.59),(w*.44,H*.53),(w*.44,H*.35)),(w*.44,H*.27))
        d.ellipse(w*.44-dot/2,0,w*.44+dot/2,dot)
        if ch=='¿':
            e=Drawing();d.replay(e.pen,(-1,0,0,-1,w,h));d=e
    elif ch in '-‐‑–—−_':
        w=280 if ch in '-‐‑' else 490 if ch=='−' else 500 if ch=='–' else 860 if ch=='—' else 510
        d.rect(0,-110 if ch=='_' else h*.46,w,sy*.85)
    elif ch in '+±=≠≤≥<>×÷≈':
        w=490;t=s*.86;mid=H*.38
        if ch in '+±':
            line((0,mid),(w,mid),t);line((w/2,mid-w/2),(w/2,mid+w/2),t)
            if ch=='±':line((0,-81),(w,-81),t)
        elif ch in '=≠':
            for yy in [mid-95,mid+95]:line((0,yy),(w,yy),t)
            if ch=='≠':line((w*.2,-20),(w*.8,mid*2+20),t*.87)
        elif ch in '<>≤≥':
            left=ch in '<≤'
            path((w if left else 0,mid+190),(0 if left else w,mid),(w if left else 0,mid-190),sw=t)
            if ch in '≤≥':line((0,-63),(w,-63),t)
        elif ch=='×':
            line((45,mid-195),(w-45,mid+195),t);line((45,mid+195),(w-45,mid-195),t)
        elif ch=='÷':
            line((0,mid),(w,mid),t)
            for yy in [mid-190,mid+190]:d.ellipse(w/2-dot/2,yy-dot/2,w/2+dot/2,yy+dot/2)
        else:
            for yy in [mid-90,mid+90]:path((0,yy-23),((w*.27,yy+183),(w*.65,yy-183),(w,yy+23)),sw=t*.85)
    elif ch in '/\\|¦':
        w=s if ch in '|¦' else 350
        if ch=='¦':
            d.rect(0,-145,s,350);d.rect(0,350,s,390)
        else:line((s/2 if ch!='\\' else w-s/2,-155),(w-s/2 if ch!='\\' else s/2,745),s*.83)
    elif ch in '()[]{}':
        w=208
        if ch in '()':path((w,790),((s*.1,550),(s*.1,22),(w,-178)),sw=s*.83)
        elif ch in '[]':
            d.rect(0,-175,s*.83,965);d.rect(0,790-s*.83,w,s*.83);d.rect(0,-175,w,s*.83)
        else:path((w,790),((w*.35,790),(w*.4,730),(w*.4,594)),(w*.4,448),((w*.4,350),(w*.15,315),(0,306)),
                  ((w*.15,296),(w*.4,263),(w*.4,165)),(w*.4,21),((w*.4,-117),(w*.35,-175),(w,-175)),sw=s*.80)
        if ch in ')]}':e=Drawing();d.replay(e.pen,(-1,0,0,1,w,0));d=e
    elif ch in "'\"‘’‚“”„":
        double=ch in '\"“”„';w=dot*(2.6 if double else 1)
        for x in ([0,dot*1.6] if double else [0]):
            low=ch in '‚„';yy=0 if low else 710-dot
            if ch in "'\"":d.rect(x,yy-80,dot*.76,dot+80)
            elif ch in '‘“':
                d.ellipse(x,yy-90,x+dot,yy-90+dot)
                path((x+dot*.25,yy-40),((x-dot*.03,yy+35),(x+dot*.56,yy+93),(x+dot,yy+98)),sw=dot*.48)
            else:
                d.ellipse(x,yy,x+dot,yy+dot)
                path((x+dot*.72,yy+dot*.55),((x+dot*1.05,yy-20),(x+dot*.37,yy-96),(x,yy-96)),sw=dot*.48)
    elif ch in '«»‹›':
        double=ch in '«»';w=350 if double else 170
        for x in ([0,180] if double else [0]):path((x+145,h*.78),(x,h*.45),(x+145,h*.12),sw=s*.85)
        if ch in '»›':e=Drawing();d.replay(e.pen,(-1,0,0,1,w,0));d=e
    elif ch=='…':
        w=dot*5
        for x in [0,dot*2,dot*4]:d.ellipse(x,0,x+dot,dot)
    elif ch in '·•':
        w=dot*(1 if ch=='·' else 1.8);d.ellipse(0,h*.47-w/2,w,h*.47+w/2)
    elif ch=='*':
        from math import sin,cos,pi
        w=325;cx=w/2;cy=H-170
        for i in range(5):
            angle=pi/2+2*pi*i/5
            line((cx,cy),(cx+cos(angle)*160,cy+sin(angle)*160),s*.73)
    elif ch=='%':
        w=716
        d.ring(0,430,264,720,s*.69,s*.65)
        d.ring(w-264,-10,w,280,s*.69,s*.65)
        line((w*.19,-8),(w*.81,718),s*.77)
    elif ch=='#':
        w=570
        for x in [w*.29,w*.70]:line((x-50,0),(x+50,H),s*.82)
        for yy in [H*.31,H*.67]:line((0,yy),(w,yy),s*.84)
    elif ch in '^~`':
        w=330
        if ch=='^':path((0,h*.61),(w/2,H),(w,h*.61),sw=s*.80)
        elif ch=='~':path((0,h*.46),((w*.28,h*.82),(w*.68,h*.12),(w,h*.48)),sw=s*.80)
        else:line((60,740),(190,605),s*.8)
    elif ch=='&':
        w=601
        path((w-s*.37,0),(w*.25,H*.61),((s*.34,H*.88),(w*.31,H+20-sy/2),(w*.43,H-sy/2)),
             ((w*.85,H-sy/2),(w*.77,H*.67),(w*.45,H*.50)),
             ((w*.10,H*.34),(s*.39,H*.30),(s*.39,H*.18)),
             ((s*.39,-32+sy/2),(w*.82,-56+sy/2),(w*.90,H*.47)),sw=s*.91)
    elif ch=='@':
        w=820
        d.ring(w*.31,120,w*.72,560,s*.78,s*.72)
        path((w*.72,556),(w*.66,193),((w*.64,88),(w-s*.35,66),(w-s*.35,345)),
             ((w-s*.35,792),(s*.4,827),(s*.4,312)),
             ((s*.4,-100),(w*.60,-167),(w*.89,-14)),sw=s*.77)
    elif ch=='∞':
        w=740;mid=280
        path((w*.5,mid),((w*.20,690),(-w*.21,mid),(w*.12,mid-140)),
             ((w*.32,mid-215),(w*.43,mid-90),(w*.5,mid)),
             ((w*.80,690),(w*1.21,mid),(w*.88,mid-140)),
             ((w*.68,mid-215),(w*.57,mid-90),(w*.5,mid)),sw=s*.88)
    elif ch=='√':
        w=618
        path((0,285),(102,337),(226,-24),(426,730),(w,730),sw=s*.87)
    elif ch=='°':w=248;d.ring(0,H-248,w,H,s*.70)
    elif ch=='¬':w=490;d.rect(0,H*.38,w,s*.85);d.rect(w-s*.85,H*.16,s*.85,H*.22)
    elif ch=='¶':
        w=460;d.ellipse(0,H*.46,w*.8,H);d.rect(w*.32,-135,s*.85,H+135);d.rect(w-s,-135,s*.85,H+135)
    elif ch=='§':
        w=403
        base,bw=design.latin('s');base.replay(d.pen,(w/bw,0,0,.83,0,260));base.replay(d.pen,(w/bw,0,0,.83,0,-120))
    elif ch=='¤':
        w=440;d.ring(65,100,w-65,410,s*.78)
        for a,b in [((0,40),(120,160)),((0,470),(120,350)),((w,40),(w-120,160)),((w,470),(w-120,350))]:line(a,b,s*.78)
    else:raise KeyError(ch)
    return d,w
