"""Filled, optically corrected outlines for the core reading alphabet.

The inner and outer curves are authored independently. They are not automatic
offsets of a skeleton; shoulders, joins and counters have their own coordinates.
"""
import json
import os

from geometry import Drawing


def core(design,ch):
    d=Drawing();s=design.s;sy=s*.89;H=design.cap;h=design.h
    heavy=max(0,(design.weight-400)/500)
    low=ch.islower();y=h if low else H;o=10
    widths={'a':454,'b':471,'c':430,'d':471,'e':464,'f':278,'g':471,'h':451,
            'm':728,'n':451,'o':480,'p':471,'q':471,'r':274,'s':401,'t':280,'u':451,
            'B':507,'P':496,'R':533,'D':567,'C':562,'G':597,'S':504,'O':615,'Q':615,
            '0':505,'1':298,'2':477,'3':478,'4':513,'5':469,'6':494,'7':472,'8':496,'9':494,'I':87.890625}
    if ch not in widths:return None
    w=widths[ch]+heavy*(35 if ch in 'abdegopqBPR' else 18 if ch not in 'frt' else 8)
    if ch in 'ft':w+=heavy*72
    if ch.isupper() and H<650:w*=.87
    p=d.outline
    if ch=='I':
        raw=(26+(design.weight-100)*52/300 if design.weight<=400 else 78+(design.weight-400)*64/500)
        w=180/2.048*raw/78
        d.rect(0,0,w,1443/2.048)
    elif ch in 'oOQ0':
        # Slightly straighter sides and more generous interior than an ellipse.
        def oval(l,b,r,t,counter=False):
            cx=(l+r)/2;cy=(b+t)/2;rx=(r-l)/2;ry=(t-b)/2;k=.565
            d.outline((l,cy),[
                ((l,cy+ry*k),(cx-rx*k,t),(cx,t)),
                ((cx+rx*k,t),(r,cy+ry*k),(r,cy)),
                ((r,cy-ry*k),(cx+rx*k,b),(cx,b)),
                ((cx-rx*k,b),(l,cy-ry*k),(l,cy))],counter=counter)
        oval(0,-o,w,y+o);oval(s,sy-o,w-s,y+o-sy,True)
        if ch=='Q':d.polygon([(w*.52,y*.20),(w*.52+s*.80,y*.25),(w+10,-48),(w-s*.87,-48)])
    elif ch in 'n hm'.replace(' ',''):
        top=740 if ch=='h' else h
        if ch=='m':
            # Two authored shoulders, with a full-height central stem.
            mid=w*.50
            p((0,0),[(0,h),(s,h),(s,h*.86),
                ((w*.19,h+o),(w*.36,h+o),(mid-s*.27,h*.81)),
                ((w*.68,h+o),(w,h+o),(w,h*.62)),(w,0),(w-s,0),(w-s,h*.59),
                ((w-s,h-sy+o),(mid+s*.30,h-sy+o),(mid+s*.30,h*.55)),(mid+s*.30,0),(mid-s*.70,0),(mid-s*.70,h*.60),
                ((mid-s*.70,h-sy+o),(s,h-sy+o),(s,h*.55)),(s,0)])
        else:
            p((0,0),[(0,top),(s,top),(s,h*.84),
                ((s*1.55,h+o),(w*.50,h+o),(w*.55,h+o)),
                ((w*.86,h+o),(w,h*.87),(w,h*.62)),(w,0),(w-s,0),(w-s,h*.59),
                ((w-s,h-sy+o),(s,h-sy+o),(s,h*.55)),(s,0)])
    elif ch=='u':
        b,bw=core(design,'n');b.replay(d.pen,(-1,0,0,-1,bw,h));w=bw
    elif ch=='r':
        p((0,0),[(0,h),(s,h),(s,h*.82),
            ((s*1.42,h+o),(w*.77,h+o),(w,h-2)),(w,h-sy-5),
            ((w*.54,h-sy+7),(s,h*.91-sy),(s,h*.53)),(s,0)])
    elif ch in 'bdpqg':
        # b/p use the same bowl, mirrored for d/q/g.
        top=740 if ch in 'bd' else h
        bottom=-210 if ch in 'pq' else 0
        bowl=Drawing()
        bowl.outline((0,bottom),[(0,top),(s,top),(s,h*.84),
            ((w*.28,h+o),(w*.42,h+o),(w*.53,h+o)),
            ((w*.86,h+o),(w,h*.79),(w,h*.50)),
            ((w,h*.20),(w*.86,-o),(w*.53,-o)),
            ((w*.40,-o),(w*.23,15),(s,h*.14)),(s,bottom)])
        bowl.outline((s,h*.50),[
            ((s,h*.29),(w*.25,sy-o),(w*.50,sy-o)),
            ((w*.76,sy-o),(w-s,h*.29),(w-s,h*.50)),
            ((w-s,h*.71),(w*.76,h+o-sy),(w*.50,h+o-sy)),
            ((w*.25,h+o-sy),(s,h*.71),(s,h*.50))],counter=True)
        if ch in 'dq':bowl.replay(d.pen,(-1,0,0,1,w,0))
        elif ch=='g':
            p((w,h),[(w,-30),((w,-178),(w*.79,-220),(w*.48,-220)),
                ((w*.25,-220),(w*.10,-183),(0,-130)),(s*.63,-75),
                ((w*.23,-133),(w*.33,-220+sy),(w*.49,-220+sy)),
                ((w*.76,-220+sy),(w-s,-110),(w-s,-24)),(w-s,h*.12),
                ((w*.72,-o),(w*.56,-o),(w*.46,-o)),
                ((w*.15,-o),(0,h*.20),(0,h*.49)),
                ((0,h*.80),(w*.16,h+o),(w*.46,h+o)),
                ((w*.60,h+o),(w*.76,h*.95),(w-s,h*.84)),(w-s,h)])
            p((s,h*.49),[
                ((s,h*.28),(w*.26,sy-o),(w*.50,sy-o)),
                ((w*.75,sy-o),(w-s,h*.29),(w-s,h*.49)),
                ((w-s,h*.71),(w*.76,h+o-sy),(w*.50,h+o-sy)),
                ((w*.26,h+o-sy),(s,h*.71),(s,h*.49))],counter=True)
        else:bowl.replay(d.pen)
    elif ch in 'cCG':
        p((w,y*.82),[
            ((w*.89,y*.96),(w*.74,y+o),(w*.52,y+o)),
            ((w*.18,y+o),(0,y*.81),(0,y*.50)),
            ((0,y*.19),(w*.17,-o),(w*.51,-o)),
            ((w*.74,-o),(w*.90,y*.07),(w,y*.18)),(w-s*.66,y*.18+sy*.53),
            ((w*.80,sy+13),(w*.67,sy-o),(w*.52,sy-o)),
            ((w*.25,sy-o),(s,y*.24),(s,y*.50)),
            ((s,y*.76),(w*.25,y+o-sy),(w*.52,y+o-sy)),
            ((w*.67,y+o-sy),(w*.80,y*.90-sy*.12),(w-s*.66,y*.82-sy*.53))])
        if ch=='G':
            d.rect(w-s,y*.11,s,y*.36)
            d.rect(w*.56,y*.43,w*.44,sy)
    elif ch=='e':
        # The upper counter and lower aperture are designed separately.
        p((w,h*.46),[(s,h*.46),
            ((s,h*.23),(w*.26,sy-o),(w*.52,sy-o)),
            ((w*.69,sy-o),(w*.80,h*.11),(w*.88,h*.21)),(w,h*.12),
            ((w*.89,h*.03),(w*.73,-o),(w*.51,-o)),
            ((w*.18,-o),(0,h*.19),(0,h*.50)),
            ((0,h*.79),(w*.17,h+o),(w*.50,h+o)),
            ((w*.83,h+o),(w,h*.79),(w,h*.53))])
        p((s,h*.46+sy*.88),[(w-s,h*.46+sy*.88),
            ((w-s,h*.79),(w*.73,h+o-sy),(w*.50,h+o-sy)),
            ((w*.28,h+o-sy),(s,h*.77),(s,h*.46+sy*.88))],counter=True)
    elif ch=='a':
        p((w,0),[(w-s,0),(w-s,h*.10),
            ((w*.73,h*.03),(w*.57,-o),(w*.40,-o)),
            ((w*.14,-o),(0,h*.11),(0,h*.28)),
            ((0,h*.45),(w*.17,h*.49),(w*.44,h*.53)),(w-s,h*.58),(w-s,h*.67),
            ((w-s,h+o-sy),(w*.29,h+o-sy),(s*.80,h*.76)),(s*.10,h*.81),
            ((w*.17,h*.97),(w*.32,h+o),(w*.51,h+o)),
            ((w*.84,h+o),(w,h*.84),(w,h*.64))])
        p((w-s,h*.46),[(w*.46,h*.41),
            ((s*1.35,h*.37),(s,h*.36),(s,h*.26)),
            ((s,sy-o),(w*.34,sy-o),(w*.43,sy-o)),
            ((w*.67,sy-o),(w-s,h*.19),(w-s,h*.34))],counter=True)
    elif ch in 'sS':
        p((w,y*.82),[
            ((w*.91,y*.95),(w*.73,y+o),(w*.50,y+o)),
            ((w*.21,y+o),(0,y*.88),(0,y*.70)),
            ((0,y*.52),(w*.18,y*.47),(w*.45,y*.40)),
            ((w*.72,y*.33),(w-s,y*.31),(w-s,y*.21)),
            ((w-s,sy-o),(w*.67,sy-o),(w*.49,sy-o)),
            ((w*.28,sy-o),(s*1.03,y*.11),(s*.82,y*.22)),(0,y*.17),
            ((w*.10,y*.03),(w*.27,-o),(w*.49,-o)),
            ((w*.79,-o),(w,y*.10),(w,y*.23)),
            ((w,y*.43),(w*.81,y*.48),(w*.53,y*.55)),
            ((w*.24,y*.62),(s,y*.62),(s,y*.73)),
            ((s,y+o-sy),(w*.33,y+o-sy),(w*.50,y+o-sy)),
            ((w*.68,y+o-sy),(w*.78,y*.89),(w-s*.78,y*.78-sy*.3))])
    elif ch=='t':
        sy=s*.96;join=h-sy;top=h+128;x=s*1.02;stem=s*1.24
        p((x,top),[(x+stem,top),(x+stem,join+sy),(w,join+sy),(w,join),
            (x+stem,join),(x+stem,s*1.12),
            ((x+stem,sy*.6),(w*.70,sy*.67),(w,sy*.92)),(w,sy*.02),
            ((w*.55,-o),(x,-o),(x,s*1.05)),(x,join),(0,join),(0,join+sy),(x,join+sy)])
    elif ch=='f':
        x=s*1.04;stem=s*1.148;join=h-sy
        p((x,0),[(x,join),(0,join),(0,join+sy),(x,join+sy),(x,740-s*.9),
            ((x,757),(w*.72,760),(w,735)),(w,735-sy),
            ((w*.78,752-sy),(x+stem,750-sy),(x+stem,740-s*1.1)),
            (x+stem,join+sy),(w,join+sy),(w,join),(x+stem,join),(x+stem,0)])
    elif ch in 'BPR':
        mid=H*.47 if ch=='B' else H*.43
        right=w-(25 if ch=='R' else 0)
        p((0,0),[(0,H),(right*.53,H),
            ((right*.88,H),(right,H*.88),(right,H*.73)),
            ((right,H*.60),(right*.89,mid+sy*.35),(right*.75,mid+sy*.20)),
            *(([((w,H*.43),(w,H*.31),(w,H*.23)),((w,H*.07),(w*.85,0),(w*.55,0))]) if ch=='B' else [(s,mid)]),
            (s,0)])
        counter_top=H-sy;counter_bottom=mid+sy
        center=(counter_top+counter_bottom)/2
        p((s,counter_top),[(right*.52,counter_top),
            ((right*.76,counter_top),(right-s,center+(counter_top-center)*.55),(right-s,center)),
            ((right-s,center-(center-counter_bottom)*.55),(right*.70,counter_bottom),(right*.49,counter_bottom)),(s,counter_bottom)],counter=True)
        if ch=='B':
            center=(mid+sy)/2
            p((s,mid),[(w*.53,mid),((w*.80,mid),(w-s,center+(mid-center)*.55),(w-s,center)),
                ((w-s,center-(center-sy)*.55),(w*.74,sy),(w*.53,sy)),(s,sy)],counter=True)
        if ch=='R':d.polygon([(w*.50,mid+sy*.60),(w*.50+s,mid+sy*.60),(w,0),(w-s*1.15,0)])
    elif ch=='D':
        p((0,0),[(0,H),(w*.35,H),((w*.79,H),(w,H*.79),(w,H*.50)),
            ((w,H*.20),(w*.79,0),(w*.35,0))])
        p((s,sy),[(w*.34,sy),((w*.69,sy),(w-s,H*.23),(w-s,H*.50)),
            ((w-s,H*.77),(w*.69,H-sy),(w*.34,H-sy)),(s,H-sy)],counter=True)
    elif ch=='1':
        # A defined flag and flat baseline; no diagonal overshoot above caps.
        p((w-s,0),[(w-s,H-sy*1.06),(s*.34,H*.74),(0,H*.74+sy*.92),
            (w-s*.93,H),(w,H),(w,0)])
    elif ch=='2':
        p((0,0),[(0,sy*.99),
            ((0,H*.18),(w*.23,H*.36),(w*.45,H*.50)),
            ((w*.70,H*.66),(w-s,H*.69),(w-s,H*.77)),
            ((w-s,H+10-sy),(s*1.31,H+10-sy),(s*.85,H*.78)),(0,H*.81),
            ((w*.05,H*.98),(w*.32,H+10),(w*.51,H+10)),
            ((w*.83,H+10),(w,H*.92),(w,H*.75)),
            ((w,H*.56),(w*.83,H*.49),(w*.57,H*.32)),
            ((w*.36,H*.18),(s*1.25,sy*1.26),(s*1.18,sy)),(w,sy),(w,0)])
    elif ch=='3':
        pilot_three = os.environ.get('TABUNA_PILOT_THREE')
        cfg = json.loads(pilot_three) if pilot_three and pilot_three.startswith('{') else {}
        start_y_h = cfg.get('start_y_h', .85)
        top_c1_x_w = cfg.get('top_c1_x_w', .12)
        top_c1_y_h = cfg.get('top_c1_y_h', .99)
        top_c2_x_w = cfg.get('top_c2_x_w', .29)
        top_end_x_w = cfg.get('top_end_x_w', .49)
        upper_right_c1_x_w = cfg.get('upper_right_c1_x_w', .80)
        upper_right_c2_x_w = cfg.get('upper_right_c2_x_w', .98)
        upper_right_c2_y_h = cfg.get('upper_right_c2_y_h', .91)
        upper_right_end_x_w = cfg.get('upper_right_end_x_w', .98)
        upper_right_end_y_h = cfg.get('upper_right_end_y_h', .75)
        upper_side_c1_x_w = cfg.get('upper_side_c1_x_w', .98)
        upper_side_c1_y_h = cfg.get('upper_side_c1_y_h', .62)
        upper_side_c2_x_w = cfg.get('upper_side_c2_x_w', .86)
        upper_side_c2_y_h = cfg.get('upper_side_c2_y_h', .55)
        waist_right_x_w = cfg.get('waist_right_x_w', .73)
        waist_right_y_h = cfg.get('waist_right_y_h', .51)
        mid_c1_x_w = cfg.get('mid_c1_x_w', .93)
        mid_c1_y_h = cfg.get('mid_c1_y_h', .47)
        mid_c2_y_h = cfg.get('mid_c2_y_h', .37)
        lower_right_end_y_h = cfg.get('lower_right_end_y_h', .3021760221760222)
        bottom_right_c1_y_h = cfg.get('bottom_right_c1_y_h', .09)
        bottom_c2_x_w = cfg.get('bottom_c2_x_w', .79)
        bottom_end_x_w = cfg.get('bottom_end_x_w', .5226882845188285)
        bottom_left_c1_x_w = cfg.get('bottom_left_c1_x_w', .28268828451882844)
        bottom_left_c2_x_w = cfg.get('bottom_left_c2_x_w', .08)
        bottom_left_c2_y_h = cfg.get('bottom_left_c2_y_h', .07217602217602218)
        bottom_left_end_y_h = cfg.get('bottom_left_end_y_h', .20217602217602217)
        left_waist_x_s = cfg.get('left_waist_x_s', 1.015434646654159)
        left_waist_y_h = cfg.get('left_waist_y_h', .18)
        left_waist_y_sy = cfg.get('left_waist_y_sy', .51)
        lower_inner_c1_x_w = cfg.get('lower_inner_c1_x_w', .25)
        lower_inner_c2_x_w = cfg.get('lower_inner_c2_x_w', .33)
        lower_inner_end_x_w = cfg.get('lower_inner_end_x_w', .49)
        lower_inner_right_c1_x_w = cfg.get('lower_inner_right_c1_x_w', .72)
        lower_inner_right_c2_x_s = cfg.get('lower_inner_right_c2_x_s', 1.0)
        lower_inner_right_c2_y_h = cfg.get('lower_inner_right_c2_y_h', .12)
        lower_inner_right_end_x_s = cfg.get('lower_inner_right_end_x_s', 1.0)
        lower_inner_right_end_y_h = cfg.get('lower_inner_right_end_y_h', .28)
        lower_join_c1_x_s = cfg.get('lower_join_c1_x_s', 1.0)
        lower_join_c1_y_h = cfg.get('lower_join_c1_y_h', .40)
        lower_join_c2_x_w = cfg.get('lower_join_c2_x_w', .74)
        lower_join_end_x_w = cfg.get('lower_join_end_x_w', .43)
        waist_left_x_w = cfg.get('waist_left_x_w', .28)
        upper_inner_c1_x_w = cfg.get('upper_inner_c1_x_w', .70)
        upper_inner_c2_x_w = cfg.get('upper_inner_c2_x_w', .98)
        upper_inner_c2_x_s = cfg.get('upper_inner_c2_x_s', 1.0)
        upper_inner_c2_y_h = cfg.get('upper_inner_c2_y_h', .63)
        upper_inner_end_x_w = cfg.get('upper_inner_end_x_w', .98)
        upper_inner_end_x_s = cfg.get('upper_inner_end_x_s', 1.0)
        upper_inner_end_y_h = cfg.get('upper_inner_end_y_h', .75)
        upper_inner_top_c1_x_w = cfg.get('upper_inner_top_c1_x_w', .98)
        upper_inner_top_c1_x_s = cfg.get('upper_inner_top_c1_x_s', 1.0)
        upper_inner_top_c2_x_w = cfg.get('upper_inner_top_c2_x_w', .69)
        upper_inner_top_end_x_w = cfg.get('upper_inner_top_end_x_w', .49)
        top_return_c1_x_w = cfg.get('top_return_c1_x_w', .34)
        top_return_c2_x_w = cfg.get('top_return_c2_x_w', .24)
        top_return_c2_y_h = cfg.get('top_return_c2_y_h', .92)
        top_return_c2_y_sy = cfg.get('top_return_c2_y_sy', .12)
        top_return_end_x_s = cfg.get('top_return_end_x_s', .77)
        top_return_end_y_h = cfg.get('top_return_end_y_h', .85)
        top_return_end_y_sy = cfg.get('top_return_end_y_sy', .47)
        p((0,H*start_y_h),[
            ((w*top_c1_x_w,H*top_c1_y_h),(w*top_c2_x_w,H+10),(w*top_end_x_w,H+10)),
            ((w*upper_right_c1_x_w,H+10),(w*upper_right_c2_x_w,H*upper_right_c2_y_h),(w*upper_right_end_x_w,H*upper_right_end_y_h)),
            ((w*upper_side_c1_x_w,H*upper_side_c1_y_h),(w*upper_side_c2_x_w,H*upper_side_c2_y_h),(w*waist_right_x_w,H*waist_right_y_h)),
            ((w*mid_c1_x_w,H*mid_c1_y_h),(w,H*mid_c2_y_h),(w,H*lower_right_end_y_h)),
            ((w,H*bottom_right_c1_y_h),(w*bottom_c2_x_w,-10),(w*bottom_end_x_w,-10)),
            ((w*bottom_left_c1_x_w,-10),(w*bottom_left_c2_x_w,H*bottom_left_c2_y_h),(0,H*bottom_left_end_y_h)),(s*left_waist_x_s,H*left_waist_y_h+sy*left_waist_y_sy),
            ((w*lower_inner_c1_x_w,sy+3),(w*lower_inner_c2_x_w,sy-10),(w*lower_inner_end_x_w,sy-10)),
            ((w*lower_inner_right_c1_x_w,sy-10),(w-s*lower_inner_right_c2_x_s,H*lower_inner_right_c2_y_h),(w-s*lower_inner_right_end_x_s,H*lower_inner_right_end_y_h)),
            ((w-s*lower_join_c1_x_s,H*lower_join_c1_y_h),(w*lower_join_c2_x_w,H*.46),(w*lower_join_end_x_w,H*.46)),(w*waist_left_x_w,H*.46),
            (w*waist_left_x_w,H*.46+sy),(w*lower_join_end_x_w,H*.46+sy),
            ((w*upper_inner_c1_x_w,H*.46+sy),(w*upper_inner_c2_x_w-s*upper_inner_c2_x_s,H*upper_inner_c2_y_h),(w*upper_inner_end_x_w-s*upper_inner_end_x_s,H*upper_inner_end_y_h)),
            ((w*upper_inner_top_c1_x_w-s*upper_inner_top_c1_x_s,H+10-sy),(w*upper_inner_top_c2_x_w,H+10-sy),(w*upper_inner_top_end_x_w,H+10-sy)),
            ((w*top_return_c1_x_w,H+10-sy),(w*top_return_c2_x_w,H*top_return_c2_y_h-sy*top_return_c2_y_sy),(s*top_return_end_x_s,H*top_return_end_y_h-sy*top_return_end_y_sy))])
        if pilot_three:
            if cfg.get('top', False):
                d.polygon([(s*.02,H*.74),(w*.53,H*.74),(w*.49,H*.88),(s*.10,H*.88)])
            if cfg.get('bottom', False):
                d.polygon([(s*.00,H*.20),(w*.56,H*.20),(w*.50,H*.04),(s*.08,H*.04)])
            if cfg.get('waist', False):
                d.polygon([(w*.40,H*.47),(w*.70,H*.47),(w*.65,H*.53),(w*.38,H*.53)])
    elif ch=='4':
        upright=w*.72
        d.rect(upright-s/2,0,s,H)
        d.polygon([(upright-s*.55,H),(upright+s*.45,H),(s*1.13,H*.29),
                   (w,H*.29),(w,H*.29-sy),(0,H*.29-sy),(0,H*.29)])
    elif ch=='5':
        pilot_five = os.environ.get('TABUNA_PILOT_FIVE')
        cfg = json.loads(pilot_five) if pilot_five and pilot_five.startswith('{') else {}
        top_left_x_s = cfg.get('top_left_x_s', .18)
        left_wall_y_h = cfg.get('left_wall_y_h', .43)
        upper_left_x_s = cfg.get('upper_left_x_s', .82)
        upper_left_y_h = cfg.get('upper_left_y_h', .38)
        shoulder_c1_x_w = cfg.get('shoulder_c1_x_w', .26)
        shoulder_c1_y_h = cfg.get('shoulder_c1_y_h', .48)
        shoulder_c2_x_w = cfg.get('shoulder_c2_x_w', .38)
        shoulder_c2_y_h = cfg.get('shoulder_c2_y_h', .51)
        shoulder_end_x_w = cfg.get('shoulder_end_x_w', .5266844349680171)
        shoulder_end_y_h = cfg.get('shoulder_end_y_h', .5571760221760222)
        right_c1_x_w = cfg.get('right_c1_x_w', .82)
        right_c1_y_h = cfg.get('right_c1_y_h', .51)
        right_c2_x_s = cfg.get('right_c2_x_s', 1.0)
        right_c2_y_h = cfg.get('right_c2_y_h', .43)
        right_end_x_s = cfg.get('right_end_x_s', 1.0)
        right_end_y_h = cfg.get('right_end_y_h', .31217602217602214)
        lower_top_c1_x_s = cfg.get('lower_top_c1_x_s', 1.0)
        lower_top_c2_x_w = cfg.get('lower_top_c2_x_w', .67)
        lower_top_end_x_w = cfg.get('lower_top_end_x_w', .45668443496801703)
        lower_c1_x = cfg.get('lower_c1_x_w', .313315565031983)
        lower_c2_x = cfg.get('lower_c2_x_s', 1.1954346466541588)
        lower_end_x = cfg.get('lower_end_x_s', .9954346466541589)
        lower_end_y = cfg.get('lower_end_y_h', .2121760221760222)
        left_corner_y = cfg.get('left_corner_y_h', .17217602217602218)
        bottom_left_x = cfg.get('bottom_left_x_w', .10331556503198294)
        bottom_left_y_h = cfg.get('bottom_left_y_h', .05217602217602217)
        bottom_c1_x_w = cfg.get('bottom_c1_x_w', .28331556503198296)
        bottom_c2_x_w = cfg.get('bottom_c2_x_w', .49)
        bottom_right_c1_x_w = cfg.get('bottom_right_c1_x_w', .79)
        bottom_right_c1_y = cfg.get('bottom_right_c1_y', -10)
        bottom_right_c2_y_h = cfg.get('bottom_right_c2_y_h', .08)
        bottom_right_end_y_h = cfg.get('bottom_right_end_y_h', .27)
        outer_c1_y_h = cfg.get('outer_c1_y_h', .48)
        outer_c2_x_w = cfg.get('outer_c2_x_w', .85)
        outer_c2_y_h = cfg.get('outer_c2_y_h', .62)
        outer_end_x_w = cfg.get('outer_end_x_w', .6133155650319829)
        outer_end_y_h = cfg.get('outer_end_y_h', .6621760221760222)
        top_return_c1_x_w = cfg.get('top_return_c1_x_w', .36)
        top_return_c1_y_h = cfg.get('top_return_c1_y_h', .62)
        top_return_c2_x_w = cfg.get('top_return_c2_x_w', .23)
        top_return_c2_y_h = cfg.get('top_return_c2_y_h', .57)
        top_return_end_x_s = cfg.get('top_return_end_x_s', 1.0)
        top_return_end_y_h = cfg.get('top_return_end_y_h', .5621760221760222)
        p((w,H),[(s*top_left_x_s,H),(0,H*left_wall_y_h),(s*upper_left_x_s,H*upper_left_y_h),
            ((w*shoulder_c1_x_w,H*shoulder_c1_y_h),(w*shoulder_c2_x_w,H*shoulder_c2_y_h),(w*shoulder_end_x_w,H*shoulder_end_y_h)),
            ((w*right_c1_x_w,H*right_c1_y_h),(w-s*right_c2_x_s,H*right_c2_y_h),(w-s*right_end_x_s,H*right_end_y_h)),
            ((w-s*lower_top_c1_x_s,sy-10),(w*lower_top_c2_x_w,sy-10),(w*lower_top_end_x_w,sy-10)),
            ((w*lower_c1_x,sy-10),(s*lower_c2_x,H*.09),(s*lower_end_x,H*lower_end_y)),(0,H*left_corner_y),
            ((w*bottom_left_x,H*bottom_left_y_h),(w*bottom_c1_x_w,-10),(w*bottom_c2_x_w,-10)),
            ((w*bottom_right_c1_x_w,bottom_right_c1_y),(w,H*bottom_right_c2_y_h),(w,H*bottom_right_end_y_h)),
            ((w,H*outer_c1_y_h),(w*outer_c2_x_w,H*outer_c2_y_h),(w*outer_end_x_w,H*outer_end_y_h)),
            ((w*top_return_c1_x_w,H*top_return_c1_y_h),(w*top_return_c2_x_w,H*top_return_c2_y_h),(s*top_return_end_x_s,H*top_return_end_y_h)),(s*(1.36+.22*max(0,min(1,(design.weight-100)/300))),H-sy),(w*(1-.07*max(0,min(1,(design.weight-100)/300))),H-sy)])
        if pilot_five:
            if cfg.get('lower', False):
                d.polygon([(s*.02,H*.18),(w*.54,H*.18),(w*.46,H*.03),(s*.10,H*.03)])
            if cfg.get('shoulder', False):
                d.polygon([(w*.36,H*.48),(w*.92,H*.48),(w*.88,H*.61),(w*.40,H*.58)])
            if cfg.get('topbar', False):
                d.polygon([(s*.22,H-sy*.72),(w*.96,H-sy*.72),(w*.96,H-sy*.46),(s*.20,H-sy*.46)])
    elif ch in '69':
        p((w,H*.85),[
            ((w*.85,H*.98),(w*.66,H+10),(w*.48,H+10)),
            ((w*.15,H+10),(0,H*.78),(0,H*.36)),
            ((0,H*.13),(w*.15,-10),(w*.49,-10)),
            ((w*.81,-10),(w,H*.13),(w,H*.31)),
            ((w,H*.51),(w*.80,H*.63),(w*.51,H*.63)),
            ((w*.32,H*.63),(s*1.24,H*.54),(s,H*.48)),
            ((s,H*.80),(w*.28,H+10-sy),(w*.48,H+10-sy)),
            ((w*.64,H+10-sy),(w*.78,H*.91),(w-s*.67,H*.85-sy*.57))])
        d.ellipse(s,sy-10,w-s,H*.63-sy,reverse=True)
        if ch=='9':out=Drawing();d.replay(out.pen,(-1,0,0,-1,w,H));d=out
    elif ch=='7':
        d.polygon([(0,H),(w,H),(w,H-sy),(w*.39,0),(w*.39-s*1.08,0),
                   (w-s*1.08,H-sy),(0,H-sy)])
    elif ch=='8':
        p((w*.50,H+10),[
            ((w*.81,H+10),(w*.96,H*.90),(w*.96,H*.76)),
            ((w*.96,H*.64),(w*.87,H*.57),(w*.76,H*.52)),
            ((w*.93,H*.46),(w,H*.36),(w,H*.24)),
            ((w,H*.08),(w*.82,-10),(w*.50,-10)),
            ((w*.18,-10),(0,H*.08),(0,H*.24)),
            ((0,H*.36),(w*.07,H*.46),(w*.24,H*.52)),
            ((w*.13,H*.57),(w*.04,H*.64),(w*.04,H*.76)),
            ((w*.04,H*.90),(w*.19,H+10),(w*.50,H+10))])
        d.ellipse(s+w*.04,H*.51+sy*.49,w-s-w*.04,H+10-sy,reverse=True)
        d.ellipse(s,sy-10,w-s,H*.51-sy*.49,reverse=True)
    if ch=='4':
        out=Drawing();d.replay(out.pen,(1,0,0,1,0,15.625));d=out
    elif ch=='7':
        out=Drawing();d.replay(out.pen,(1,0,0,1,-15.625,0));d=out
    return d,w


def cyrillic_core(design,ch):
    """Upright Cyrillic has its own proportions, joins and stroke weights."""
    from copy import copy
    d=Drawing();s=design.s;sy=s*.89;low=ch.islower();h=design.h if low else design.cap
    heavy=max(0,(design.weight-400)/500)
    p=d.outline
    pilot_ya = os.environ.get('TABUNA_PILOT_YA')
    if ch=='Я' and pilot_ya:
        cfg = json.loads(pilot_ya)
        w=523
        base,bw=core(design,'R')
        base.replay(d.pen,(-w/bw,0,0,h/710,w,0))
        if cfg.get('leg', False):
            d.polygon([(w*.18,0),(w*.42,0),(w*.70,h*.47),(w*.53,h*.47)])
        if cfg.get('bowl', False):
            d.polygon([(w*.18,h*.67),(w*.72,h*.67),(w*.66,h*.82),(w*.24,h*.86)])
        if cfg.get('join', False):
            d.polygon([(w*.46,h*.46),(w*.78,h*.50),(w*.72,h*.37),(w*.43,h*.34)])
        return d,w
    if ch=='Я':
        w=523
        base,bw=core(design,'R')
        base.replay(d.pen,(-w/bw,0,0,h/710,w,0))
        d.polygon([(w*.46,h*.46),(w*.78,h*.50),(w*.72,h*.37),(w*.43,h*.34)])
        return d,w
    if ch=='К':
        w=529
        d.rect(0,0,s,h)
        cfg = json.loads(os.environ.get('TABUNA_PILOT_CYR_K', '{}'))
        if cfg:
            upper_join_x = s * cfg.get('upper_join_x_s', .7554346466541589)
            upper_join_y = h * cfg.get('upper_join_y_h', .3978239778239778)
            d.polygon([
                (upper_join_x, upper_join_y),
                (upper_join_x, upper_join_y + s * cfg.get('upper_thick_s', 1.2754346466541588)),
                (w - s * cfg.get('upper_tip_inset_s', 1.1354346466541587), h),
                (w, h),
            ])
            lower_join_x = w * cfg.get('lower_join_x_w', .18046313799621927)
            lower_join_y = h * cfg.get('lower_join_y_h', .5321760221760222)
            d.polygon([
                (lower_join_x, lower_join_y),
                (lower_join_x + s * cfg.get('lower_width_s', 1.18), lower_join_y),
                (w, 0),
                (w - s * cfg.get('lower_tip_inset_s', 1.1554346466541587), 0),
            ])
            fill = cfg.get('join_fill')
            if fill:
                d.polygon([
                    (
                        w * pt.get('x_w', 0) + s * pt.get('x_s', 0),
                        h * pt.get('y_h', 0) + s * pt.get('y_s', 0),
                    )
                    for pt in fill
                ])
            return d,w
        d.polygon([(s*.7554346466541589,h*.3978239778239778),
                   (s*.7554346466541589,h*.3978239778239778+s*1.2754346466541588),
                   (w-s*1.1354346466541587,h),(w,h)])
        d.polygon([(w*.18046313799621927,h*.5321760221760222),
                   (w*.18046313799621927+s*1.18,h*.5321760221760222),
                   (w,0),(w-s*1.1554346466541587,0)])
        d.polygon([(w*.17,h*.49),(w*.36,h*.57),(w*.32,h*.41),(w*.15,h*.38)])
        return d,w
    pilot_cap_z = os.environ.get('TABUNA_PILOT_CAP_Z')
    if ch=='З' and pilot_cap_z:
        cfg = json.loads(pilot_cap_z)
        w=480
        base,bw=core(design,'3')
        base.replay(d.pen,(w/bw*.96,0,0,h/710,0,0))
        if cfg.get('top', False):
            d.polygon([(s*.05,h*.76),(w*.54,h*.76),(w*.48,h*.88),(s*.11,h*.88)])
        if cfg.get('bottom', False):
            d.polygon([(s*.02,h*.20),(w*.56,h*.20),(w*.50,h*.04),(s*.09,h*.04)])
        if cfg.get('waist', False):
            d.polygon([(w*.66,h*.52),(w*.96,h*.47),(w*.94,h*.35),(w*.66,h*.41)])
        return d,w
    if ch=='З':
        w=480
        base,bw=core(design,'3')
        base.replay(d.pen,(w/bw*.96,0,0,h/710,0,0))
        d.polygon([(w*.66,h*.52),(w*.96,h*.47),(w*.94,h*.35),(w*.66,h*.41)])
        return d,w
    pilot_z = os.environ.get('TABUNA_PILOT_Z')
    if ch=='з' and pilot_z:
        if pilot_z == 'augment':
            cfg = {'top': True, 'bottom': True, 'right': True}
        elif pilot_z.startswith('{'):
            cfg = json.loads(pilot_z)
        else:
            cfg = None
        if cfg and cfg.get('mode', 'augment') == 'augment':
            w=416
            base,bw=core(design,'3')
            base.replay(d.pen,(w/bw*.96,0,0,h/710,0,0))
            if cfg.get('top', False):
                d.polygon([(s*.08,h*.69),(w*.40,h*.69),(w*.35,h*.77),(s*.12,h*.80)])
            if cfg.get('bottom', False):
                d.polygon([(s*.02,h*.18),(w*.42,h*.18),(w*.38,h*.05),(s*.10,h*.04)])
            if cfg.get('right', False):
                d.polygon([(w*.76,h*.58),(w*.98,h*.52),(w*.95,h*.38),(w*.76,h*.44)])
            return d,w
        w=416
        cfg = json.loads(pilot_z)
        top_left = cfg.get('top_left_s', .34)
        top_right = cfg.get('top_right_s', .50)
        waist_left = cfg.get('waist_left_w', .33)
        waist_y = cfg.get('waist_y_h', .51)
        lower_left = cfg.get('lower_left_s', .35)
        lower_right = cfg.get('lower_right_s', .50)
        lower_y = cfg.get('lower_y_h', .23)
        width_top = cfg.get('width_top_s', .96)
        width_bottom = cfg.get('width_bottom_s', .98)
        d.stroke(
            (w - s * top_right, h * .79),
            [
                ((w * .84, h + 10 - sy / 2), (s * top_left, h + 14 - sy / 2), (s * top_left, h * .72)),
                ((s * top_left, h * .56), (w * waist_left, h * .54), (w * waist_left, waist_y * h)),
                ((w * .74, h * .48), (w - s * .42, h * .45), (w - s * .42, h * .36)),
            ],
            s * width_top,
        )
        d.stroke(
            (w * waist_left, waist_y * h),
            [
                ((w * .82, h * .50), (w - s * .43, h * .38), (w - s * .43, lower_y * h)),
                ((w - s * lower_right, -10 + sy / 2), (s * lower_left, -13 + sy / 2), (s * lower_left, h * .15)),
            ],
            s * width_bottom,
        )
        fill = cfg.get('join_fill')
        if fill:
            d.polygon([
                (
                    w * pt.get('x_w', 0) + s * pt.get('x_s', 0),
                    h * pt.get('y_h', 0) + s * pt.get('y_s', 0),
                )
                for pt in fill
            ])
        return d,w
    if ch=='з':
        w=416
        base,bw=core(design,'3')
        base.replay(d.pen,(w/bw*.96,0,0,h/710,0,0))
        d.polygon([(s*.02,h*.18),(w*.42,h*.18),(w*.38,h*.05),(s*.10,h*.04)])
        out=Drawing();d.replay(out.pen,(1,0,0,1,7.8125,0));d=out
        return d,w
    if ch in 'вя':
        small=copy(design);small.cap=h
        base,w=core(small,'B' if ch=='в' else 'R')
        if ch=='я':base.replay(d.pen,(-1.00,0,0,1.04,w*1.00,-h*.04));return d,w
        return base,w
    if ch in 'кмнт':
        w={'к':440,'м':588,'н':457,'т':433}[ch]+heavy*20
        if ch=='н':d.rect(0,0,s,h);d.rect(w-s,0,s,h);d.rect(0,h*.46,w,sy)
        elif ch=='т':d.rect(0,h-sy,w,sy);d.rect((w-s)/2,0,s,h)
        elif ch=='к':
            d.rect(0,0,s,h)
            pilot = os.environ.get('TABUNA_PILOT_K')
            if pilot:
                cfg = json.loads(pilot)
                upper_join_x = s * cfg.get('upper_join_x_s', .7554346466541589)
                upper_join_y = h * cfg.get('upper_join_y_h', .39018129770992366)
                d.polygon([
                    (upper_join_x, upper_join_y),
                    (upper_join_x, upper_join_y + s * cfg.get('upper_thick_s', .9354346466541589)),
                    (w - s * cfg.get('upper_tip_inset_s', 1.2754346466541588), h),
                    (w, h),
                ])
                lower_join_x = w * cfg.get('lower_join_x_w', .27)
                lower_join_y = h * cfg.get('lower_join_y_h', .5498187022900763)
                d.polygon([
                    (lower_join_x, lower_join_y),
                    (lower_join_x + s * cfg.get('lower_width_s', .84), lower_join_y),
                    (w, 0),
                    (w - s * cfg.get('lower_tip_inset_s', 1.285434646654159), 0),
                ])
                fill = cfg.get('join_fill')
                if fill:
                    d.polygon([
                        (
                            w * pt.get('x_w', 0) + s * pt.get('x_s', 0),
                            h * pt.get('y_h', 0) + s * pt.get('y_s', 0),
                        )
                        for pt in fill
                    ])
                return d,w
            # OPTIMIZER-REFINED-BEGIN: k
            d.polygon([(s*.7554346466541589,h*.39018129770992366),
                       (s*.7554346466541589,h*.39018129770992366+s*.9354346466541589),
                       (w-s*1.2754346466541588,h),(w,h)])
            d.polygon([(w*.27,h*.5498187022900763),
                       (w*.27+s*.84,h*.5498187022900763),
                       (w,0),(w-s*1.285434646654159,0)])
            d.polygon([(w*.18,h*.49),(w*.31,h*.55),(w*.28,h*.44),(w*.17,h*.42)])
            # OPTIMIZER-REFINED-END: k
        else:
            d.rect(0,0,s,h);d.rect(w-s,0,s,h)
            d.polygon([(s*.38,h),(s*1.39,h),(w*.5,s*1.24),(w-s*1.39,h),(w-s*.38,h),
                       (w*.5+s*.45,0),(w*.5-s*.45,0)])
        return d,w
    if ch.upper() in ('Д','Л'):
        de=ch.upper()=='Д';w=(526 if low else 589) if de else (468 if low else 554)
        w+=heavy*(90 if de else 30)
        # Sloping left leg; short, intentional foot; stable counters in Black.
        regularity = ((design.weight - 100) / 300 if design.weight <= 400
                      else (900 - design.weight) / 500) if de else 0.0
        regularity = max(0.0, min(1.0, regularity))
        # At text sizes Canvas rounds the short foot differently from
        # CoreText.  Ramp the node correction with the existing optical axis;
        # display masters retain the full Regular refinement.
        regularity *= .5 + .5 * design.display
        if design.display < .5 and (design.weight < 300 or design.weight > 700):
            regularity = 0.0
        l=s*.65 if de else 0;r=w-s*(.55 + .65*regularity) if de else w
        left_top=w*(0.33 - .09*regularity)
        left_low=l+w*.13
        p((l,0),[(l,sy),
            ((l+w*.08,sy),(left_low-s*.1,sy*1.08),(left_low,h*.20)),
            (left_top,h),(r,h),(r,0),(r-s,0),(r-s,h-sy),(left_top+s*.86,h-sy),
            (left_low+s*.94,h*.25),((left_low+s*.78,sy*.08),(l+s*.89,-7),(l,0))])
        if de:
            d.rect(0,0,w,sy);d.rect(0,-120,s,120+sy);d.rect(w-s,-120,s,120+sy)
        return d,w
    if ch.upper()=='Ж':
        w=(710 if low else 892)+heavy*26;c=w/2
        d.rect(c-s/2,0,s,h)
        join=h*.49
        tip=s*(1.77 if low else 1.60)
        junction=s*(.60 if low else .64)
        for sign in (-1,1):
            side=Drawing()
            # Both arms meet the central stem. The old lower arm began away
            # from it, leaving a visible white break at regular/text weights.
            side.polygon([(0,h),(tip,h),(c-s*.40,join+junction),
                          (c-s*.40,join-junction),(tip,0),(0,0),
                          (c-s*1.65,join)])
            side.replay(d.pen,(1,0,0,1,0,0) if sign==1 else (-1,0,0,1,w,0))
        return d,w
    if ch.upper() in ('Ь','Ъ','Ы','Б') and ch!='б':
        c=ch.upper();w=({'Ь':378,'Ъ':461,'Ы':598,'Б':464} if low else {'Ь':458,'Ъ':566,'Ы':685,'Б':509})[c]+heavy*30
        offset=(83 if low else 108) if c=='Ъ' else 0
        # Keep the bowl compact across weights; subtracting stem thickness
        # from the full width previously made the regular bowl too wide.
        r=w*(.65 if low else .70) if c=='Ы' else w
        top=h*(.58 if c=='Б' else .63 if low else .62)
        center=(offset+r)/2
        p((offset,0),[(offset,h),(offset+s,h),(offset+s,top),(center,top),
            ((r*.85,top),(r,top*.81),(r,top*.50)),
            ((r,top*.18),(r*.82,0),(r*.54,0))])
        p((offset+s,sy),[(center,sy),
            ((r*.75,sy),(r-s,top*.29),(r-s,top*.50)),
            ((r-s,top*.73),(r*.74,top-sy),(center,top-sy)),(offset+s,top-sy)],counter=True)
        if c=='Б':d.rect(0,h-sy,w*.96,sy)
        if c=='Ъ':d.rect(0,h-sy,offset+s*1.45,sy)
        if c=='Ы':d.rect(w-s,0,s,h)
        return d,w
    if ch=='б':
        base,w=core(design,'o');base.replay(d.pen)
        p((0,h*.42),[(0,h*.89),((0,663),(w*.24,669),(w*.52,687)),
            ((w*.75,702),(w*.89,709),(w*.96,744)),(w,744-sy),
            ((w*.88,692-sy),(w*.67,691-sy),(w*.49,676-sy)),
            ((s*1.18,659-sy),(s,h*1.09),(s,h*.78)),(s,h*.42)])
        return d,w
    if ch.upper()=='Ч':
        w=(434 if low else 513)+heavy*25
        p((0,h),[(s,h),(s,h*.68),
            ((s,h*.46),(w*.38,h*.46),(w-s,h*.61)),(w-s,h),(w,h),(w,0),(w-s,0),(w-s,h*.44),
            ((w*.38,h*.30),(0,h*.32),(0,h*.63))])
        return d,w
    if ch in 'ЋЂћђ':
        desc=ch in 'Ђђ';w=(451 if low else 550)+heavy*24
        top=h if low else h*.64;asc=740 if low else h;x=42
        p((x,0),[(x,asc),(x+s,asc),(x+s,top*.84),
            ((x+s*1.5,top+10),(w*.57,top+10),(w*.60,top+10)),
            ((w*.88,top+10),(w,top*.85),(w,top*.61)),(w,0),(w-s,0),(w-s,top*.58),
            ((w-s,top-sy+10),(x+s,top-sy+10),(x+s,top*.54)),(x+s,0)])
        d.rect(0,asc-(sy*1.7 if low else sy),w*.81,sy)
        if desc:
            p((w-s,6),[(w,6),(w,-78),
                ((w,-206),(w*.73,-231),(w*.47,-199)),(w*.47,-199+sy),
                ((w*.73,-210+sy),(w-s,-163),(w-s,-76))])
        return d,w
    if ch in 'ЉљЊњ':
        if ch in 'Љљ':left,bw=cyrillic_core(design,'л' if low else 'Л')
        elif low:left,bw=cyrillic_core(design,'н')
        else:left,bw=design.latin('H')
        left.replay(d.pen)
        w=bw+(270 if low else 320)+heavy*20
        top=h*.58;cx=(bw+w-s)/2
        p((bw-s*.5,0),[(bw-s*.5,top),(cx,top),
            ((w*.95,top),(w,top*.77),(w,top*.50)),
            ((w,top*.22),(w*.95,0),(cx,0))])
        p((bw,sy),[(cx,sy),
            ((w-s,sy),(w-s,top*.35),(w-s,top*.50)),
            ((w-s,top-sy),(w*.95-s,top-sy),(cx,top-sy)),(bw,top-sy)],counter=True)
        return d,w
    return None
