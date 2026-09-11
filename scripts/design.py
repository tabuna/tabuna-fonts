"""Tabuna Sans original glyph drawings, in 1000 units/em.

Every coordinate in this file belongs to this project's original construction.
There is no font-file input. Shared shapes are internal components only.
"""
from geometry import Drawing


class Design:
    def __init__(self, weight, optical):
        self.weight, self.optical = weight, optical
        self.display = max(0,min(1,(optical-16)/12))
        self.s = (26+(weight-100)*52/300 if weight<=400 else 78+(weight-400)*64/500)
        self.s *= 1.025-.065*self.display
        self.h = 524-18*self.display
        self.cap = 1443/2.048
        self.space = 42+10*(1-self.display)-5*(weight-400)/500
        self.xscale = 1.018-.036*self.display

    def latin(self, ch):
        from refined import core
        refined=core(self,ch)
        if refined is not None:return refined
        d=Drawing(); s=self.s; h=self.h; H=self.cap
        # Bounds describe actual black shapes, apart from optical overshoots.
        lower=ch.islower(); y=h if lower else H
        widths={
            'A':580,'B':506,'C':568,'D':562,'E':458,'F':434,'G':598,
            'H':556,'I':210,'J':394,'K':529,'L':441,'M':678,'N':568,
            'O':612,'P':492,'Q':612,'R':522,'S':506,'T':518,'U':554,
            'V':570,'W':850,'X':560,'Y':558,'Z':504,
            'a':446,'b':470,'c':438,'d':470,'e':460,'f':280,'g':472,
            'h':455,'i':s,'j':s+70,'k':432,'l':s+36,'m':725,'n':455,
            'o':481,'p':470,'q':470,'r':290,'s':403,'t':293,'u':455,
            'v':452,'w':664,'x':453,'y':453,'z':410,
            '0':506,'1':285,'2':468,'3':478,'4':509,'5':466,
            '6':491,'7':473,'8':489,'9':491,
        }
        w=widths[ch]; sy=s*.91
        if ch in 'HEFL':
            # Scalar stroke dimensions measured from native raster rows.
            # All contours remain our rectangle construction; weight changes
            # expand the bars around their original vertical centers.
            strength=s/(78*(1.025-.065*self.display))
            black_width={'H':1152,'E':894,'F':876,'L':876}[ch]
            s=w*180/black_width*strength
            sy=H*162/1443*strength
        def stem(x,bot=0,top=y,sw=s): d.rect(x,bot,sw,top-bot)
        def bar(bot,l=0,r=w): d.rect(l,bot,r-l,sy)
        def path(start,*segs,sw=s): d.stroke(start,list(segs),sw)
        def bowl(l,b,r,t): d.ring(l,b,r,t,s,sy)
        def arch(l,r,top,bottom=0):
            path((l+s/2,top*.69),((l+s/2,top*.94),(l+s*.98,top-sy/2+9),((l+r)/2,top-sy/2+9)),
                 ((r-s*.8,top-sy/2+9),(r-s/2,top*.86),(r-s/2,top*.66)),(r-s/2,bottom))
        if ch in 'Oo0':
            bowl(0,-11,w,y+11)
        elif ch=='Q':
            bowl(0,-11,w,H+11)
            d.line((w*.56,H*.24),(w+15,-61),s*.9)
        elif ch=='A':
            d.polygon([(0,0),(w*.43,H),(w*.57,H),(w,0),(w-s*1.08,0),(w*.5,H-s*1.2),(s*1.02,0)])
            bar(H*.32,w*.22,w*.78)
        elif ch in 'BPR':
            stem(0)
            mid=H*.48 if ch=='B' else H*.43
            right=w-15 if ch=='R' else w
            path((s*.5,H-sy/2),(right*.52,H-sy/2),((right-s/2,H-sy/2),(right-s/2,H*.85),(right-s/2,(H+mid)/2)),
                 ((right-s/2,mid+sy/2),(right*.62,mid+sy/2),(s*.5,mid+sy/2)))
            if ch=='B':
                path((s*.5,mid+sy/2),(w*.55,mid+sy/2),((w-s/2,mid+sy/2),(w-s/2,mid*.72),(w-s/2,mid*.51)),
                     ((w-s/2,sy/2),(w*.64,sy/2),(s*.5,sy/2)))
            if ch=='R': d.line((w*.54,mid+sy/2),(w-s*.42,0),s)
        elif ch in 'CcG':
            path((w-s*.5,y*.80),((w*.74,y+24-sy/2),(w*.37,y+35-sy/2),(w*.20,y*.86)),
                 ((s*.18,y*.70),(s*.18,y*.29),(w*.20,y*.14)),
                 ((w*.38,-30+sy/2),(w*.76,-23+sy/2),(w-s*.40,y*.19)),sw=s*.97)
            if ch=='G':
                d.rect(w-s,y*.10,s,y*.37)
                bar(y*.43,w*.55,w)
        elif ch=='D':
            stem(0)
            path((s/2,H-sy/2),(w*.36,H-sy/2),((w*.80,H-sy/2),(w-s/2,H*.82),(w-s/2,H*.5)),
                 ((w-s/2,H*.18),(w*.80,sy/2),(w*.36,sy/2)),(s/2,sy/2))
        elif ch in 'EF':
            middle=738 if ch=='E' else 705
            thickness=H*160/1443*strength
            bottom=H*middle/1443-thickness/2;top=bottom+thickness
            reach=w*(857/894 if ch=='E' else 819/876)
            points=[(0,0),(0,H),(w,H),(w,H-sy),(s,H-sy),(s,top),
                    (reach,top),(reach,bottom),(s,bottom)]
            points+=([(s,sy),(w,sy),(w,0)] if ch=='E' else [(s,0)])
            d.polygon(points)
        elif ch=='H':
            bottom=H*738/1443-sy/2;top=bottom+sy
            d.polygon([(0,0),(0,H),(s,H),(s,top),(w-s,top),(w-s,H),
                       (w,H),(w,0),(w-s,0),(w-s,bottom),(s,bottom),(s,0)])
        elif ch=='I': stem((w-s)/2); bar(0); bar(H-sy)
        elif ch=='J':
            path((w-s/2,H),(w-s/2,H*.27),((w-s/2,-18+sy/2),(s/2,-20+sy/2),(s/2,H*.19)))
        elif ch in 'Kk':
            stem(0,0,740 if lower else H)
            d.line((s*.50,y*.39),(w-s*1.30,y-s*.2),s*.93)
            d.line((w*.40,y*.52),(w-s*.45,s*.2),s*.98)
        elif ch=='L':d.polygon([(0,0),(0,H),(s,H),(s,sy),(w,sy),(w,0)])
        elif ch=='M':
            stem(0); stem(w-s)
            d.polygon([(s*.2,H),(s*1.3,H),(w/2,s*1.25),(w-s*1.3,H),(w-s*.2,H),(w*.5+s*.48,0),(w*.5-s*.48,0)])
        elif ch=='N':
            stem(0); stem(w-s)
            d.polygon([(s*.12,H),(s*1.17,H),(w-s*.12,0),(w-s*1.17,0)])
        elif ch in 'Ss':
            path((w-s*.48,y*.81),((w*.79,y+28-sy/2),(s*.50,y+22-sy/2),(s*.50,y*.73)),
                 ((s*.50,y*.53),(w*.30,y*.53),(w*.51,y*.46)),
                 ((w*.76,y*.38),(w-s*.47,y*.37),(w-s*.47,y*.22)),
                 ((w-s*.47,-23+sy/2),(w*.19,-27+sy/2),(s*.40,y*.18)),sw=s*.96)
        elif ch=='T': bar(H-sy); stem((w-s)/2)
        elif ch=='U':
            path((s/2,H),(s/2,H*.30),((s/2,-12+sy/2),(w-s/2,-12+sy/2),(w-s/2,H*.30)),(w-s/2,H))
        elif ch in 'Vv':
            d.polygon([(0,y),(s*1.05,y),(w/2,s*1.25),(w-s*1.05,y),(w,y),(w*.5+s*.49,0),(w*.5-s*.49,0)])
        elif ch in 'Ww':
            d.polygon([(0,y),(s,y),(w*.25,s*1.2),(w*.5-s*.42,y),(w*.5+s*.42,y),(w*.75,s*1.2),(w-s,y),(w,y),(w*.75+s*.48,0),(w*.75-s*.48,0),(w*.5,y-s*1.65),(w*.25+s*.48,0),(w*.25-s*.48,0)])
        elif ch in 'Xx':
            d.polygon([(0,0),(s*1.12,0),(w,y),(w-s*1.12,y)])
            d.polygon([(0,y),(s*1.12,y),(w,0),(w-s*1.12,0)])
        elif ch=='Y':
            stem((w-s)/2,0,H*.44)
            d.polygon([(0,H),(s*1.1,H),(w/2,H*.45+s*.3),(w-s*1.1,H),(w,H),(w/2+s*.47,H*.40),(w/2-s*.47,H*.40)])
        elif ch in 'Zz':
            bar(0); bar(y-sy)
            d.polygon([(0,sy*.8),(w-s*1.14,y-sy*.8),(w,y-sy*.8),(s*1.14,sy*.8)])
        elif ch=='a':
            stem(w-s,0,h*.61)
            path((s*.66,h*.78),((s*1.05,h+12-sy/2),(w-s/2,h+12-sy/2),(w-s/2,h*.67)),
                 (w-s/2,h*.10))
            path((w-s*.60,h*.54),(w*.39,h*.48),((s*.44,h*.45),(s*.46,h*.27),(s*.46,h*.22)),
                 ((s*.46,-24+sy/2),(w*.69,-30+sy/2),(w-s*.51,h*.26)),sw=s*.95)
        elif ch in 'bdpq':
            bowl(0,-10,w,h+10)
            if ch in 'bp': stem(0,-210 if ch=='p' else 0,740 if ch=='b' else h)
            else: stem(w-s,-210 if ch=='q' else 0,740 if ch=='d' else h)
        elif ch=='e':
            path((w-s*.46,h*.17),((w*.68,-24+sy/2),(w*.27,-26+sy/2),(w*.13,h*.23)),
                 ((s*.14,h*.53),(s*.14,h*.85),(w*.32,h*.96-sy*.16)),
                 ((w*.71,h+30-sy/2),(w-s/2,h*.80),(w-s/2,h*.49)))
            bar(h*.46,s*.53,w-s*.06)
        elif ch=='f':
            path((s*.77,0),(s*.77,740-s*1.4),((s*.77,760-sy/2),(w*.70,760-sy/2),(w,729-sy/2)))
            bar(h*.70,0,w*.91)
        elif ch=='g':
            bowl(0,0,w,h+10)
            path((w-s/2,h),(w-s/2,-34),((w-s/2,-236+sy/2),(w*.24,-240+sy/2),(s*.59,-134)))
        elif ch in 'hnm':
            stem(0,0,740 if ch=='h' else h)
            if ch=='m':
                mid=w*.50
                arch(0,mid+s*.25,h); arch(mid-s*.75,w,h)
            else: arch(0,w,h)
        elif ch in 'ijl':
            if ch=='i': stem(0); d.ellipse(-3,h+104,w+3,h+104+max(s,65))
            elif ch=='j':
                path((w-s/2,h),(w-s/2,-86),((w-s/2,-198),(w*.36,-220+sy/2),(-28,-200+sy/2)))
                d.ellipse(w-s-3,h+104,w+3,h+104+max(s,65))
            else:
                regular_stem=78*(1.025-.065*self.display)
                d.rect(0,0,(regular_stem+36)*s/regular_stem,740)
        elif ch=='r':
            stem(0)
            path((s/2,h*.62),((s/2,h*.95),(w*.67,h+18-sy/2),(w,h-1-sy/2)))
        elif ch=='t':
            path((s*.86,h+138),(s*.86,s*1.18),((s*.86,sy*.35),(w*.63,sy*.15),(w,sy*.77)))
            bar(h*.72,0,w)
        elif ch=='u':
            stem(w-s)
            path((s/2,h),(s/2,h*.29),((s/2,-20+sy/2),(w-s/2,-27+sy/2),(w-s/2,h*.37)))
        elif ch=='y':
            d.line((s*.47,h),(w*.50,h*.06),s*.95)
            path((w-s*.47,h),(w*.37,-80),((w*.30,-186),(w*.19,-220+sy/2),(0,-204+sy/2)),sw=s*.94)
        elif ch=='1':
            stem(w-s)
            d.line((0,H*.78),(w-s/2,H-s*.50),s*.89)
        elif ch=='2':
            path((s/2,H*.78),((s*.82,H+21-sy/2),(w-s/2,H+20-sy/2),(w-s/2,H*.74)),
                 ((w-s/2,H*.57),(w*.77,H*.50),(w*.57,H*.35)),(s*.6,sy*.85))
            bar(0)
        elif ch=='3':
            path((s*.5,H*.84),((w*.23,H+25-sy/2),(w-s*.48,H+22-sy/2),(w-s*.48,H*.75)),
                 ((w-s*.48,H*.53),(w*.68,H*.53),(w*.34,H*.52)),sw=s*.95)
            path((w*.34,H*.52),((w*.84,H*.52),(w-s*.48,H*.43),(w-s*.48,H*.26)),
                 ((w-s*.48,-23+sy/2),(w*.20,-27+sy/2),(s*.40,H*.15)),sw=s*.97)
        elif ch=='4':
            stem(w*.69-s/2)
            d.polygon([(w*.63,H),(w*.76,H),(s*1.04,H*.30),(w,H*.30),(w,H*.30-sy),(0,H*.30-sy),(0,H*.30)])
        elif ch=='5':
            bar(H-sy,s*.20,w*.96)
            d.line((s*.83,H),(s*.55,H*.44),s*.95)
            path((s*.57,H*.46),((w*.43,H*.66),(w-s/2,H*.55),(w-s/2,H*.29)),
                 ((w-s/2,-22+sy/2),(w*.19,-26+sy/2),(s*.4,H*.16)))
        elif ch=='6':
            path((w-s*.50,H*.83),((w*.72,H+28-sy/2),(s/2,H+25-sy/2),(s/2,H*.38)),(s/2,H*.30))
            bowl(0,-11,w,H*.63)
        elif ch=='7':
            bar(H-sy)
            d.polygon([(w-s*1.15,H-sy*.8),(w,H-sy*.8),(w*.40,0),(w*.40-s*1.05,0)])
        elif ch=='8':
            bowl(w*.04,H*.46,w*.96,H+11)
            bowl(0,-11,w,H*.54)
        elif ch=='9':
            bowl(0,H*.38,w,H+11)
            path((w-s/2,H*.70),(w-s/2,H*.39),((w-s/2,-25+sy/2),(w*.26,-28+sy/2),(s*.48,H*.16)))
        if ch=='j':
            out=Drawing();d.replay(out.pen,(1,0,0,1,-15.625,0));d=out
        elif ch in 'Kk':
            out=Drawing();d.replay(out.pen,(1,0,0,1,0,-15.625));d=out
        return d,w

    def cyrillic(self,ch):
        """Independent Cyrillic skeletons; shared shapes use our own Latin."""
        from refined import cyrillic_core
        refined=cyrillic_core(self,ch)
        if refined is not None:return refined
        same={'А':'A','В':'B','Е':'E','К':'K','М':'M','Н':'H','О':'O','Р':'P','С':'C','Т':'T','Х':'X',
              'а':'a','е':'e','о':'o','р':'p','с':'c','х':'x','у':'y','і':'i','І':'I','ј':'j','Ј':'J','ѕ':'s','Ѕ':'S'}
        if ch in same: return self.latin(same[ch])
        if ch in 'кмн':
            base,w=self.latin({'к':'K','м':'M','н':'H'}[ch])
            out=Drawing();base.replay(out.pen,(.84,0,0,self.h/710,0,0))
            return out,w*.84
        low=ch.islower(); H=self.h if low else self.cap
        s=self.s; sy=s*.91; d=Drawing()
        widths={'б':465,'Б':501,'в':444,'Г':419,'г':343,'Д':598,'д':518,'Ж':824,'ж':700,'З':480,'з':416,
                'И':559,'и':459,'Л':557,'л':469,'П':550,'п':457,'т':565,'У':550,'Ф':697,'ф':635,
                'Ц':574,'ц':478,'Ч':513,'ч':434,'Ш':752,'ш':661,'Щ':752,'щ':661,
                'Ъ':594,'ъ':496,'Ы':699,'ы':607,'Ь':488,'ь':416,'Э':555,'э':444,'Ю':811,'ю':723,'Я':523,'я':454,
                'Є':555,'є':444,'Ґ':419,'ґ':343,'Љ':790,'љ':670,'Њ':799,'њ':680,
                'Ђ':628,'ђ':469,'Ћ':550,'ћ':455,'Џ':550,'џ':457}
        w=widths[ch]
        def stem(x,b=0,t=H): d.rect(x,b,s,t-b)
        def bar(y,l=0,r=w): d.rect(l,y,r-l,sy)
        def path(a,*segments,sw=s):d.stroke(a,list(segments),sw)
        c=ch.upper()
        if ch=='б':
            d.ring(0,-10,w,H+8,s,sy)
            path((s/2,H*.48),(s/2,H*.97),((s/2,735),(w*.66,674),(w-12,752)))
        elif c in ('Б','Ь','Ъ','Ы') or ch=='в':
            if ch=='в':
                base,bw=self.latin('B'); base.replay(d.pen,((w/bw)*(0.96 if low else 1),0,0,H/710,0,0)); return d,w
            offset=s*1.24 if c=='Ъ' else 0
            if c=='Ъ':bar(H-sy,0,s*2.5)
            stem(offset)
            bw=w-s*1.7 if c=='Ы' else w
            top=H*.55 if c=='Б' else H*.60
            path((offset+s/2,top),(bw*.61,top),((bw-s/2,top),(bw-s/2,top*.65),(bw-s/2,top*.5)),
                 ((bw-s/2,sy/2),(bw*.60,sy/2),(offset+s/2,sy/2)))
            if c=='Б':bar(H-sy,0,w*.93)
            if c=='Ы':stem(w-s)
        elif c in ('Г','Ґ'):
            stem(0);bar(H-sy)
            if c=='Ґ':stem(w-s,H-sy,H+126)
        elif c in ('Д','Л','Љ'):
            body=w if c!='Љ' else w*.61
            left=s*.6 if c=='Д' else 0
            right=body-s*.65 if c=='Д' else body
            # A flat-topped Cyrillic construction with a distinct left foot.
            path((left,sy/2),((left+s*1.8,sy/2),(left+s*1.7,H*.55),(left+s*1.85,H-sy/2)),(right-s/2,H-sy/2),(right-s/2,0))
            if c=='Д':
                bar(0);stem(0,-130,sy);stem(w-s,-130,sy)
            if c=='Љ':
                path((body-s*.5,H*.53),(w*.78,H*.53),((w-s/2,H*.53),(w-s/2,sy/2),(w*.77,sy/2)),(body-s*.5,sy/2))
        elif c=='Ж':
            stem((w-s)/2)
            for side in (-1,1):
                center=w/2
                x=center+side*w*.15
                d.line((center,H*.44),(center+side*(w*.5-s*.40),H-s*.22),s*.91)
                d.line((x,H*.60),(center+side*(w*.5-s*.4),s*.17),s*.98)
        elif c=='З':
            base,bw=self.latin('3');base.replay(d.pen,((w/bw)*(0.96 if low else 1),0,0,H/710,0,0))
        elif c=='И':
            stem(0);stem(w-s)
            d.polygon([(s*.3,0),(s*1.22,0),(w-s*.3,H),(w-s*1.22,H)])
        elif c in ('П','Џ') or ch=='т':
            stem(0);stem(w-s);bar(H-sy)
            if ch=='т':stem((w-s)/2)
            if c=='Џ':bar(0);stem((w-s)/2,-133,sy)
        elif ch=='У':
            d.line((s*.45,H),(w*.48,H*.28),s*.95)
            path((w-s*.45,H),(w*.40,H*.15),((w*.25,sy/2),(w*.16,sy/2),(s*.5,sy/2)),sw=s*.97)
        elif c=='Ф':
            # Optical compensation for the Cyrillic ef: the system face keeps
            # a readable counter at Thin while avoiding an over-heavy Black.
            edge = abs(self.weight - 400) / 300
            fs = s * (1.0 + (0.22 if self.weight < 400 else 0.06) * edge)
            fsy = sy * (1.0 + (0.16 if self.weight < 400 else 0.04) * edge)
            d.ring(0,H*(.09 if not low else .03),w,H*(.91 if not low else .97),fs,fsy)
            stem((w-fs)/2,-210 if low else -12,740 if low else H+12)
        elif c in ('Ц','Ш','Щ'):
            # The descender projects to the right of the final upright.
            body=w-s if c in ('Ц','Щ') else w
            stem(0);stem(body-s);bar(0)
            if c in ('Ш','Щ'):stem((body-s)/2)
            if c in ('Ц','Щ'):stem(w-s,-132,sy)
        elif c=='Ч':
            stem(w-s)
            path((s/2,H),(s/2,H*.65),((s/2,H*.33),(w*.61,H*.39),(w-s*.5,H*.51)))
        elif c in ('Э','Є'):
            base,bw=self.latin('c' if low else 'C')
            base.replay(d.pen,(-w/bw if c=='Э' else w/bw,0,0,1,w if c=='Э' else 0,0))
            bar(H*.46,w*.28,w)
        elif c=='Ю':
            stem(0);bar(H*.46,0,w*.39)
            d.ring(w*.26,-10,w,H+10,s,sy)
        elif c=='Я':
            base,bw=self.latin('R');base.replay(d.pen,(-w/bw,0,0,H/710,w,0))
        elif c=='Њ':
            stem(0);stem(w*.48-s);bar(H*.48,0,w*.48)
            path((w*.48-s/2,H*.53),(w*.76,H*.53),((w-s/2,H*.53),(w-s/2,sy/2),(w*.76,sy/2)),(w*.48-s/2,sy/2))
        elif c in ('Ђ','Ћ'):
            stem(s*.95,0,740 if low else H)
            bar((self.h*.82) if low else H-sy,0,w*.72)
            top=self.h*.72 if low else H*.59
            segments=[((s*1.45,top),(w-s/2,top+s*.6),(w-s/2,top*.58)),(w-s/2,-100 if c=='Ђ' else 0)]
            if c=='Ђ':segments.append(((w-s/2,-213),(w*.60,-223),(w*.49,-167)))
            path((s*1.45,top*.70),*segments)
        if ch=='У':
            out=Drawing();d.replay(out.pen,(1,0,0,1,7.8125,0));d=out
        return d,w
