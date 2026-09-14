#!/usr/bin/env python3
"""Render the README specimen as portable SVG paths from the release font."""
from pathlib import Path
from html import escape
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'dist/TabunaSansVariable.ttf'
font=TTFont(path);upm=font['head'].unitsPerEm
face=hb.Face(path.read_bytes());shaper=hb.Font(face);shaper.scale=(upm,upm)
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="590" viewBox="0 0 1200 590" role="img" aria-labelledby="title desc">',
 '<title id="title">Tabuna Sans</title>',
 '<desc id="desc">Вариативная гарнитура с латиницей и кириллицей. Образцы весов 100, 400 и 900.</desc>',
 '<rect width="1200" height="590" rx="16" fill="#f7f7f2"/>']
def line(text,x,y,size,weight,color='#20221e'):
 variations={'wght':weight,'opsz':size};shaper.set_variations(variations);glyphs=font.getGlyphSet(location=variations)
 buf=hb.Buffer();buf.add_str(text);buf.guess_segment_properties();hb.shape(shaper,buf)
 cursor=0;scale=size/upm
 for info,pos in zip(buf.glyph_infos,buf.glyph_positions):
  pen=SVGPathPen(glyphs);glyphs[font.getGlyphOrder()[info.codepoint]].draw(pen)
  d=pen.getCommands()
  if d:parts.append(f'<path fill="{color}" transform="translate({x+(cursor+pos.x_offset)*scale:.4f} {y-pos.y_offset*scale:.4f}) scale({scale:.8f} {-scale:.8f})" d="{escape(d,quote=True)}"/>')
  cursor+=pos.x_advance
 assert x+cursor*scale<1160,(text,cursor*scale)
line('Tabuna Sans',72,158,112,450)
line('Латиница · Кириллица · 100–900',78,209,25,400,'#60635b')
parts.append('<path d="M78 250H1122" stroke="#d2d5cc"/>')
for y,weight in [(328,100),(426,400),(524,900)]:
 line(str(weight),78,y-5,20,400,'#60635b')
 line('Точность формы Aa Бб 0123456789',176,y,44,weight)
parts.append('</svg>')
out=ROOT/'docs/assets/specimen.svg';out.parent.mkdir(parents=True,exist_ok=True);out.write_text('\n'.join(parts)+'\n');print(out)
