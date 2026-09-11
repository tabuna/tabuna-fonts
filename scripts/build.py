#!/usr/bin/env python3
"""Generate original sources and compile Tabuna Sans. Run from any directory."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import unicodedata as ud

from fontTools.agl import UV2AGL
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables.ttProgram import Program
from fontTools.otlLib.builder import buildStatTable
from ufoLib2 import Font
from ufoLib2.objects import Component, Anchor
from design import Design
from geometry import Drawing
from symbols import symbol, mark
import optical as optics
import metrics
import weight_metrics
import lower_a
import lower_e
import open_rounds
import stem_bowls
import lower_g
import upper_g
import u_bowls
import mw_strokes
import s_curves
import ze_curves
import bowl_curves
import reading_marks
import kerning
import contextual
import rounds
import shoulders
import rectilinear
import latin_rectangles
import bowls
import upper_bowls
import double_bowls

ROOT=Path(__file__).resolve().parents[1]
SOURCES=ROOT/'sources'
DIST=ROOT/'dist'
MARKS='\u0300\u0301\u0302\u0303\u0304\u0306\u0307\u0308\u030A\u030B\u030C\u0326\u0327\u0328'
EXTRA='ȘșȚțҐґ€₽₴№−×÷±≠≤≥≈∞√‘’‚“”„‹›«»‐‑–—…•\u2002\u2003\u2009\u202F\u2007\u200B\u2060\uFEFF'
CHARSET=sorted(set(chr(c) for c in list(range(0x20,0x7f))+list(range(0xA0,0x180))+list(range(0x400,0x460))) | set(MARKS+EXTRA))
WEIGHTS={100:'Thin',200:'ExtraLight',300:'Light',400:'Regular',500:'Medium',600:'SemiBold',700:'Bold',800:'ExtraBold',900:'Black'}


def name(ch):return UV2AGL.get(ord(ch),f'uni{ord(ch):04X}')


class Source:
    def __init__(self,weight,optical):
        self.d=Design(weight,optical)
        self.metrics=metrics.load()
        self.f=Font();i=self.f.info
        i.familyName='Tabuna Sans';i.styleName=f'{WEIGHTS[weight]} Optical {optical}'
        i.unitsPerEm=1000;i.ascender=950;i.descender=-260;i.capHeight=710;i.xHeight=self.d.h
        i.versionMajor=0;i.versionMinor=900
        i.copyright='Copyright 2026 The Tabuna Sans Project Authors'
        i.openTypeNameDesigner='The Tabuna Sans Project Authors'
        i.openTypeNameManufacturer='Tabuna Sans Project'
        i.openTypeNameDescription='Original variable sans serif drawn from scratch. Weight and optical size axes.'
        i.openTypeNameLicense='This Font Software is licensed under the SIL Open Font License, Version 1.1.'
        i.openTypeNameLicenseURL='https://openfontlicense.org'
        i.openTypeOS2VendorID='TBNA';i.openTypeOS2WeightClass=weight;i.openTypeOS2WidthClass=5
        i.openTypeOS2Type=[];i.openTypeOS2Selection=[7]
        i.openTypeOS2TypoAscender=1030;i.openTypeOS2TypoDescender=-300;i.openTypeOS2TypoLineGap=0
        i.openTypeOS2WinAscent=1030;i.openTypeOS2WinDescent=300
        i.openTypeHheaAscender=1030;i.openTypeHheaDescender=-300;i.openTypeHheaLineGap=0
        i.postscriptUnderlinePosition=-100;i.postscriptUnderlineThickness=50
        i.openTypeOS2Panose=[2,11,5,3,2,2,2,2,2,4]
        i.openTypeHeadCreated='2026/09/11 00:00:00'
        self.done=set()

    def draw(self,key,d,width,unicode=None,spacing=True):
        f=self.f;g=f.newGlyph(key);sb=self.d.space if spacing else 0
        d.replay(g.getPen(),(self.d.xscale,0,0,1,sb,0))
        g.width=round(width*self.d.xscale+2*sb)
        if key in ('I',name('І')):
            # The rectangle and bearings are authored from the controlled PNG
            # comparison. 2048 output units preserve the measured boundaries.
            g.clearContours()
            left=(184-44*self.d.display)/2.048
            d.replay(g.getPen(),(1,0,0,1,left,0))
            g.width=width+(328-41*self.d.display)/2.048
        if unicode is not None:g.unicodes=[unicode]
        metrics.apply(g,metrics.coefficients(self.metrics,key,self.d.display))
        rounds.apply(g,key,self.d)
        shoulders.apply(g,key,self.d)
        rectilinear.apply(g,key,self.d)
        latin_rectangles.apply(g,key,self.d)
        bowls.apply(g,key,self.d)
        upper_bowls.apply(g,key,self.d)
        double_bowls.apply(g,key,self.d)
        weight_metrics.apply(g,key,self.d)
        lower_a.apply(g,key,self.d)
        lower_e.apply(g,key,self.d)
        open_rounds.apply(g,key,self.d)
        stem_bowls.apply(g,key,self.d)
        lower_g.apply(g,key,self.d)
        upper_g.apply(g,key,self.d)
        u_bowls.apply(g,key,self.d)
        mw_strokes.apply(g,key,self.d)
        s_curves.apply(g,key,self.d)
        ze_curves.apply(g,key,self.d)
        if key=='three' and key in bowl_curves.load():
            # Superscript/fraction drawings are outside this reconstruction.
            # Preserve their original source rather than moving them with 3.
            small=self.f.newGlyph('three.small')
            g.draw(small.getPen());small.width=g.width
        bowl_curves.apply(g,key,self.d)
        return g

    def comp(self,key,components,width,unicode=None):
        g=self.f.newGlyph(key);g.width=width
        for base,t in components:g.components.append(Component(base,t))
        if unicode is not None:g.unicodes=[unicode]
        return g

    def copy(self,ch,base,transform=None):
        self.ensure(base)
        b=self.f[name(base)]
        return self.comp(name(ch),[(name(base),transform or (1,0,0,1,0,0))],b.width,ord(ch))

    def raw_latin(self,ch,base):
        d,w=self.d.latin(base) if base in '23' else (bowl_curves.raw(self.d,base) or self.d.latin(base))
        return self.draw(name(ch),d,w,ord(ch))

    def anchors(self,g,ch):
        if not ch.isalpha():return
        d=self.d
        height=740 if ch in 'bdfhklt' else 710 if ch.isupper() else d.h
        transform=metrics.coefficients(self.metrics,g.name,d.display)
        if transform:height=transform['y'](height)
        weight_transform=weight_metrics.coefficients(g.name,d)
        if weight_transform:height=weight_transform['y'](height)
        # Cyrillic be has an ascender. Its measured outline is taller than
        # the lowercase x-height; above marks must clear that actual outline.
        if ch=='б':
            from fontTools.pens.boundsPen import BoundsPen
            pen=BoundsPen(self.f);g.draw(pen)
            if pen.bounds:height=pen.bounds[3]
        x=g.width/2
        g.anchors.extend([Anchor(x=x,y=height+43,name='top'),Anchor(x=x,y=0,name='bottom')])

    def ensure(self,ch):
        key=name(ch)
        if key in self.f:
            if ord(ch) not in self.f[key].unicodes:self.f[key].unicodes.append(ord(ch))
            return self.f[key]
        d=self.d;s=d.s
        if ch in MARKS:
            g=self.draw(key,mark(d,ch),0,ord(ch),False)
            reading_marks.apply_mark(g,ch,d)
            g.width=0
            below=ord(ch)>=0x0326
            g.anchors.extend([Anchor(x=0,y=0,name='_bottom' if below else '_top'),Anchor(x=0,y=-210 if below else 190,name='bottom' if below else 'top')])
            return g
        # Measured default-space advances at text/display endpoints, before
        # the common HVAR tracking field. NBSP must preserve ordinary spacing.
        word_space=(536-109*d.display)/2.048
        spaces={' ':word_space,'\u00a0':word_space,'\u2002':500,'\u2003':1000,'\u2009':180,'\u202f':180,'\u2007':600,'\u200b':0,'\u2060':0,'\ufeff':0}
        if ch in spaces:
            g=self.f.newGlyph(key);g.width=spaces[ch];g.unicodes=[ord(ch)];return g
        if ch=='\u00ad':return self.copy(ch,'-')
        if ch in 'Ľďľť':
            base={'Ľ':'L','ď':'d','ľ':'l','ť':'t'}[ch];b=self.ensure(base)
            if 'caron.alt' not in self.f:
                drawing=Drawing();drawing.outline((0,0),[(24,177),(s*.72+24,177),(s*.61+16,64),(24,-9)])
                self.draw('caron.alt',drawing,s*.72+24,spacing=False)
            xpos=b.width-self.d.space+(10 if base in 'dl' else -16)
            g=self.comp(key,[(name(base),(1,0,0,1,0,0)),('caron.alt',(1,0,0,1,xpos,560))],b.width+s*.62,ord(ch))
            self.anchors(g,ch);return g
        # Canonical decomposition provides real base + mark glyphs, not fallback.
        decomp=ud.normalize('NFD',ch)
        if len(decomp)>1 and all(c in MARKS for c in decomp[1:]):
            base=decomp[0]
            b=self.ensure(base)
            basekey=name(base)
            if base in ('i','j'):
                basekey='dotlessi' if base=='i' else 'dotlessj'
                self.dotless(base)
            components=[(basekey,(1,0,0,1,0,0))]
            top=next(a.y for a in b.anchors if a.name=='top')
            x=b.width/2
            for accent in decomp[1:]:
                self.ensure(accent)
                below=ord(accent)>=0x0326
                components.append((name(accent),(1,0,0,1,x,0 if below else top)))
                if not below:top+=185
            g=self.comp(key,components,b.width,ord(ch));reading_marks.attach(self,ch,g);self.anchors(g,ch);return g
        if ch.isascii() and ch.isalnum():
            g=self.raw_latin(ch,ch)
        elif ('\u0400'<=ch<='\u045f' or ch in 'Ґґ') and ch not in 'ЁёЙйЃѓЇїЌќЍѝЎўЀѐ':
            # з now has an independent closed outline; only its calibrated
            # advance passes through the old metrics path.
            drawing,w=(Drawing(),416) if ch=='з' and ze_curves.load() else (bowl_curves.raw(d,ch) or d.cyrillic(ch))
            g=self.draw(key,drawing,w,ord(ch))
        elif ch in 'Øø':
            drawing,w=d.latin('O' if ch=='Ø' else 'o')
            drawing.line((w*.10,-28),(w*.9,(710 if ch=='Ø' else d.h)+28),s*.72)
            g=self.draw(key,drawing,w,ord(ch))
        elif ch in 'ÐðĐđĦħŁłŦŧ':
            base={'Ð':'D','ð':'o','Đ':'D','đ':'d','Ħ':'H','ħ':'h','Ł':'L','ł':'l','Ŧ':'T','ŧ':'t'}[ch]
            drawing,w=d.latin(base)
            if ch in 'Łł':drawing.line((-30,270),(w*.73,473),s*.75)
            elif ch=='ð':
                drawing.stroke((w-s/2,d.h*.47),[((w-s/2,694),(w*.30,745),(w*.21,710))],s)
                drawing.line((w*.33,600),(w*.85,733),s*.70)
            else:drawing.rect(-29,573 if ch in 'Ħħ' else 341,w*.70+35,s*.73)
            g=self.draw(key,drawing,w,ord(ch))
        elif ch in 'Þþ':
            drawing,w=d.latin('P')
            out=Drawing();drawing.replay(out.pen,(1,0,0,.69,0,120 if ch=='Þ' else 0))
            out.rect(0,-200 if ch=='þ' else 0,s,940 if ch=='þ' else 710)
            g=self.draw(key,out,w,ord(ch))
        elif ch in 'ÆæŒœ':
            base='A' if ch=='Æ' else 'a' if ch=='æ' else 'O' if ch=='Œ' else 'o'
            second='E' if ch.isupper() else 'e'
            a,wa=d.latin(base);b,wb=d.latin(second)
            drawing=Drawing();a.replay(drawing.pen,(.90,0,0,1,0,0));b.replay(drawing.pen,(.90,0,0,1,wa*.90-s*.45,0))
            g=self.draw(key,drawing,(wa+wb)*.90-s*.45,ord(ch))
        elif ch in 'Ŋŋ':
            drawing,w=d.latin('N' if ch=='Ŋ' else 'n')
            drawing.stroke((w-s/2,55),[(w-s/2,-85),((w-s/2,-205),(w*.6,-230),(w*.48,-184))],s)
            g=self.draw(key,drawing,w,ord(ch))
        elif ch=='ı':
            self.dotless('i');g=self.f['dotlessi'];g.unicodes=[ord(ch)]
        elif ch=='ſ':
            drawing,w=d.latin('f');g=self.draw(key,drawing,w,ord(ch))
        elif ch=='ß':
            drawing=Drawing();w=492
            drawing.stroke((s/2,0),[(s/2,540),((s/2,755-s/2),(w*.79,766-s/2),(w*.77,570)),
                ((w*.76,440),(w*.46,427),(w*.47,383)),((w*.49,343),(w-s/2,346),(w-s/2,191)),
                ((w-s/2,5+s/2),(w*.47,-4+s/2),(w*.36,s*.61))],s)
            g=self.draw(key,drawing,w,ord(ch))
        elif ch in 'ĸ':g=self.raw_latin(ch,'k')
        elif ch in 'Ĳĳ':
            a,b=('I','J') if ch.isupper() else ('i','j');aa=self.ensure(a);bb=self.ensure(b)
            g=self.comp(key,[(name(a),(1,0,0,1,0,0)),(name(b),(1,0,0,1,aa.width-25,0))],aa.width+bb.width-25,ord(ch))
        elif ch in 'Ŀŀ':
            base='L' if ch=='Ŀ' else 'l';b=self.ensure(base);dot=self.ensure('·')
            g=self.comp(key,[(name(base),(1,0,0,1,0,0)),(name('·'),(.62,0,0,.62,b.width-25,150))],b.width+dot.width*.5,ord(ch))
        elif ch=='ŉ':
            b=self.ensure('n');a=self.ensure('’')
            g=self.comp(key,[(name('’'),(.7,0,0,.7,0,235)),(name('n'),(1,0,0,1,a.width*.75,0))],b.width+a.width*.75,ord(ch))
        elif ch in '©®':
            b=self.ensure('C' if ch=='©' else 'R');drawing=Drawing();drawing.ring(0,-5,750,745,s*.65)
            g=self.draw(key,drawing,750,ord(ch))
            g.components.append(Component(b.name,(.57,0,0,.57,(g.width-b.width*.57)/2,165)))
        elif ch in 'ªº¹²³':
            base={'ª':'a','º':'o','¹':'1','²':'2','³':'3'}[ch];b=self.ensure(base)
            component='three.small' if base=='3' and 'three.small' in self.f else name(base)
            g=self.comp(key,[(component,(.60,0,0,.60,0,320))],round(b.width*.60),ord(ch))
        elif ch in '¼½¾':
            a,b={'¼':('1','4'),'½':('1','2'),'¾':('3','4')}[ch]
            aa=self.ensure(a);bb=self.ensure(b)
            if 'fraction' not in self.f:
                drawing=Drawing();drawing.line((0,0),(315,710),s*.64);self.draw('fraction',drawing,315,0x2044)
            numerator='three.small' if a=='3' and 'three.small' in self.f else name(a)
            g=self.comp(key,[(numerator,(.58,0,0,.58,0,305)),('fraction',(1,0,0,1,aa.width*.43,0)),(name(b),(.58,0,0,.58,aa.width*.43+325,0))],aa.width*.43+325+bb.width*.58,ord(ch))
        elif ch in '¢$£€₽₴¥':
            if ch=='¥':
                drawing,w=d.latin('Y')
                for yy in [203,330]:drawing.rect(w*.12,yy,w*.76,s*.65)
            elif ch=='₽':
                drawing,w=d.latin('P');drawing.rect(-23,170,w*.72,s*.86)
            elif ch=='£':
                drawing=Drawing();w=466
                drawing.stroke((w*.13,0),[((w*.39,150),(w*.13,356),(w*.13,537)),((w*.13,740),(w*.76,758),(w-s*.43,611))],s)
                drawing.rect(0,0,w,s*.9);drawing.rect(0,324,w*.76,s*.80)
            else:
                drawing,w=d.latin('S' if ch in '$₴' else 'C')
                if ch in '$¢':drawing.rect(w*.5-s*.28,-88,s*.56,884)
                else:
                    for yy in [286,411]:drawing.rect(-24,yy,w*.78,s*.64)
            g=self.draw(key,drawing,w,ord(ch))
        elif ch=='µ':
            drawing,w=d.latin('u');drawing.rect(0,-210,s,320);g=self.draw(key,drawing,w,ord(ch))
        elif ch=='№':
            n=self.ensure('N');o=self.ensure('o');drawing=Drawing();drawing.rect(n.width+8,231,o.width*.55,s*.68)
            g=self.draw(key,drawing,n.width+o.width*.6,ord(ch),False)
            g.components.extend([Component('N'),Component('o',(.58,0,0,.58,n.width,338))])
        elif ch in '¨¯´¸':
            accent={'¨':'\u0308','¯':'\u0304','´':'\u0301','¸':'\u0327'}[ch]
            drawing=mark(d,accent);g=self.draw(key,drawing,280,ord(ch))
            for contour in g.contours:
                for pt in contour.points:pt.x+=140;pt.y+=0 if ch=='¸' else d.h+40
        else:
            drawing,w=symbol(d,ch);g=self.draw(key,drawing,w,ord(ch))
        self.anchors(g,ch)
        return g

    def dotless(self,base):
        key='dotlessi' if base=='i' else 'dotlessj'
        if key in self.f:return
        drawing,w=self.d.latin(base)
        # Last contour is the dot in both original drawings.
        drawing.pen.value=drawing.pen.value[:-6]
        self.draw(key,drawing,w)

    def finish(self):
        d=Drawing();d.rect(0,0,490,710);d.rect(130,240,230,230)
        # A visible box with reversed counter for .notdef.
        d=Drawing();d.ring(0,0,490,710,55)
        self.draw('.notdef',d,490)
        for ch in CHARSET:self.ensure(ch)
        contextual.build(self,name)
        digit_names=[name(str(i)) for i in range(10)]
        tab_width=round(506*self.d.xscale+2*self.d.space)
        self.f[name('\u2007')].width=tab_width
        for n in digit_names:
            b=self.f[n];self.comp(n+'.tnum',[(n,(1,0,0,1,(tab_width-b.width)/2,0))],tab_width)
        self.dotless('i');self.dotless('j')
        for text in ('ff','fi','fl','ffi','ffl'):
            components=[];advance=0
            for j,c in enumerate(text):
                base='dotlessi' if c=='i' else name(c)
                components.append((base,(1,0,0,1,advance,0)))
                advance+=self.f[base].width
            lig=self.comp(''.join(text)+'.liga',components,advance)
            for j,(_,transform) in enumerate(components[1:],1):
                lig.anchors.append(Anchor(name=f'caret_{j}',x=transform[4],y=0))
        kerning.apply(self.f,self.d,CHARSET,name)
        contextual.position(self.f,self.d,name)
        features='languagesystem DFLT dflt;\nlanguagesystem latn dflt;\nlanguagesystem cyrl dflt;\n'
        features+='feature liga {\n'
        for text in ('ffi','ffl','ff','fi','fl'):features+=f"  sub {' '.join(name(c) for c in text)} by {text}.liga;\n"
        features+='} liga;\nfeature tnum {\n'
        features+=f"  sub [{' '.join(digit_names)}] by [{' '.join(n+'.tnum' for n in digit_names)}];\n}} tnum;\n"
        features+=f"feature pnum {{ sub [{' '.join(n+'.tnum' for n in digit_names)}] by [{' '.join(digit_names)}]; }} pnum;\n"
        self.f.features.text=features+contextual.features(name)+reading_marks.features(self.f)
        # Append this private component so all public glyph IDs stay stable.
        private=['three.small'] if 'three.small' in self.f else []
        self.f.glyphOrder=['.notdef']+sorted(n for n in self.f.keys() if n!='.notdef' and n not in private)+private
        return self.f


def generate():
    SOURCES.mkdir(exist_ok=True)
    ds=DesignSpaceDocument()
    for tag,n,mi,default,ma in [('wght','Weight',100,400,900),('opsz','Optical size',*optics.AXIS_RANGE)]:
        axis=AxisDescriptor();axis.tag=tag;axis.name=n;axis.minimum=mi;axis.default=default;axis.maximum=ma
        ds.addAxis(axis)
    for optical in optics.MASTER_SIZES:
        for weight in (100,400,900):
            f=Source(weight,optical).finish()
            scale_source(f)
            path=SOURCES/f'TabunaSans-{weight}-{optical}.ufo';f.save(path,overwrite=True)
            src=SourceDescriptor();src.path=str(path);src.name=f'w{weight}o{optical}'
            src.familyName=f.info.familyName;src.styleName=f.info.styleName
            src.location={'Weight':weight,'Optical size':optical}
            if weight==400 and optical==14:src.copyInfo=True;src.copyLib=True;src.copyFeatures=True
            ds.addSource(src)
            print(f'Source: {weight:3} / {optical:2}: {len(f)} glyphs',flush=True)
    for weight,style in WEIGHTS.items():
        instance=InstanceDescriptor();instance.familyName='Tabuna Sans';instance.styleName=style
        instance.name=f'Tabuna Sans {style}';instance.location={'Weight':weight,'Optical size':14}
        ds.addInstance(instance)
    ds.write(SOURCES/'TabunaSans.designspace')
    charset_json = json.dumps([{'codepoint':f'U+{ord(c):04X}','character':c,'name':ud.name(c,'')} for c in CHARSET],ensure_ascii=False,indent=2)
    (SOURCES/'charset.json').write_text(charset_json+'\n')
    # Classic script works when the specimen is opened directly via file://.
    (SOURCES/'charset.js').write_text('// Generated by scripts/build.py; do not edit.\nwindow.TABUNA_CHARSET = '+charset_json+';\n')


def scale_source(font):
    """Keep the design grid readable, export at finer 2048-unit precision."""
    factor=2.048
    for glyph in font:
        glyph.width*=factor
        for contour in glyph.contours:
            for point in contour.points:point.x*=factor;point.y*=factor
        for component in glyph.components:
            a,b,c,d,e,f=component.transformation
            component.transformation=(a,b,c,d,e*factor,f*factor)
        for anchor in glyph.anchors:anchor.x*=factor;anchor.y*=factor
    for pair,value in list(font.kerning.items()):font.kerning[pair]=round(value*factor)
    for key in ('unitsPerEm','ascender','descender','capHeight','xHeight',
                'openTypeOS2TypoAscender','openTypeOS2TypoDescender','openTypeOS2TypoLineGap',
                'openTypeOS2WinAscent','openTypeOS2WinDescent','openTypeHheaAscender','openTypeHheaDescender',
                'openTypeHheaLineGap','postscriptUnderlinePosition','postscriptUnderlineThickness'):
        value=getattr(font.info,key)
        if value is not None:setattr(font.info,key,round(value*factor))
    font.info.capHeight=1443


def compile_font():
    DIST.mkdir(exist_ok=True)
    build_dir=ROOT/'build';build_dir.mkdir(exist_ok=True)
    env=os.environ.copy();env['SOURCE_DATE_EPOCH']='1789084800'
    # IUP compression permits up to 0.5 FU of outline error. Keep authored
    # master vertices exact; WOFF2 still supplies lossless web compression.
    subprocess.run([sys.executable,'-m','fontmake','-m',str(SOURCES/'TabunaSans.designspace'),
                    '-o','variable','--output-path',str(build_dir/'TabunaSansVariable.ttf'),
                    '--no-autohint','--keep-overlaps','--keep-direction','--no-optimize-gvar',
                    '--verbose','WARNING'],check=True,env=env)
    font=TTFont(build_dir/'TabunaSansVariable.ttf',recalcTimestamp=False)
    font['name'].setName('Tabuna Sans',1,3,1,0x409)
    font['name'].setName('Regular',2,3,1,0x409)
    font['name'].setName('Tabuna Sans Regular',4,3,1,0x409)
    font['name'].setName('TabunaSans-Regular',6,3,1,0x409)
    font['name'].setName('Tabuna Sans',16,3,1,0x409)
    font['name'].setName('Regular',17,3,1,0x409)
    font['name'].setName('0.900;TBNA;TabunaSans-Regular',3,3,1,0x409)
    for glyph_name in font.getGlyphOrder():
        glyph=font['glyf'][glyph_name]
        if glyph.isComposite():
            glyph.components[0].flags |= 0x0400
        elif glyph.numberOfContours>0:glyph.flags[0] |= 0x40
    buildStatTable(font,[
        {'tag':'wght','name':'Weight','ordering':0,'values':[dict(value=w,name=n,**({'flags':2,'linkedValue':700} if w==400 else {})) for w,n in WEIGHTS.items()]},
        {'tag':'opsz','name':'Optical size','ordering':1,'values':[
            {'name':'Small','value':9},{'name':'Text','value':14,'flags':2},{'name':'Display','value':72}]}])
    font['name'].names=[n for n in font['name'].names if n.platformID!=1]
    font['avar']=newTable('avar');font['avar'].segments={tag:{-1.0:-1.0,0.0:0.0,1.0:1.0} for tag in ('wght','opsz')}
    font['avar'].segments['opsz']=optics.initial_map()
    optical_path=SOURCES/'optical-map.json'
    if optical_path.exists():
        optical_map=json.loads(optical_path.read_text())
        assert optical_map['axisRange']==optics.AXIS_RANGE, 'Recalibrate the optical map for the current axis'
        font['avar'].segments['opsz'].update({row['normalizedInput']:row['normalizedOutput']
                                            for row in optical_map['records']})
    font['prep']=newTable('prep');font['prep'].program=Program()
    font['prep'].program.fromBytecode([0xB8,0x01,0xFF,0x85,0xB0,0x04,0x8D])
    font['gasp']=newTable('gasp');font['gasp'].gaspRange={65535:15}
    font['OS/2'].fsSelection |= (1<<7)
    font.save(build_dir/'TabunaSans-untracked.ttf')
    font=TTFont(build_dir/'TabunaSans-untracked.ttf',recalcTimestamp=False)
    tracking_path=SOURCES/'tracking.json'
    if tracking_path.exists():
        from portable_tracking import apply_tracking
        tracking=json.loads(tracking_path.read_text())
        assert tracking['unitsPerEm']==font['head'].unitsPerEm
        assert tracking['axisRange']==optics.AXIS_RANGE, 'Recalibrate tracking for the current axis'
        tracking_build=apply_tracking(font,tracking)
        (build_dir/'portable-tracking-build.json').write_text(json.dumps(tracking_build,indent=2)+'\n')
    optical_widths_path=SOURCES/'optical-widths.json'
    if optical_widths_path.exists():
        from optical_widths import apply as apply_optical_widths
        optical_widths_build=apply_optical_widths(font,json.loads(optical_widths_path.read_text()))
        (build_dir/'optical-widths-build.json').write_text(json.dumps(optical_widths_build,indent=2)+'\n')
    space_widths_path=SOURCES/'space-widths.json'
    if space_widths_path.exists():
        from space_widths import apply as apply_space_widths
        space_widths_build=apply_space_widths(font,json.loads(space_widths_path.read_text()))
        (build_dir/'space-widths-build.json').write_text(json.dumps(space_widths_build,indent=2)+'\n')
    # Keep a build-only HVAR control for checking all phantom-point advances.
    # Chromium retains fractional HVAR interpolation but rounds gvar phantom
    # advances like the measured system-ui. Tracking is already in both.
    font.save(build_dir/'TabunaSans-with-hvar.ttf')
    del font['HVAR']
    font.save(build_dir/'TabunaSansVariable.ttf')
    font.flavor='woff2';font.save(build_dir/'TabunaSansVariable.woff2')
    for filename in ('TabunaSansVariable.ttf','TabunaSansVariable.woff2'):
        (build_dir/filename).replace(DIST/filename)
    manifest={'family':'Tabuna Sans','version':'0.900','unitsPerEm':font['head'].unitsPerEm,'masters':len(optics.MASTER_SIZES)*3,'axes':{'wght':[100,400,900],'opsz':optics.AXIS_RANGE},
              'glyphs':len(font.getGlyphOrder()),'characters':len(font.getBestCmap()),
              'files':{p.name:p.stat().st_size for p in DIST.glob('*') if p.suffix in ('.ttf','.woff2')}}
    (DIST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--compile-only',action='store_true');parser.add_argument('--sources-only',action='store_true')
    args=parser.parse_args()
    if not args.compile_only:generate()
    if not args.sources_only:compile_font()
