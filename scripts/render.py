"""HarfBuzz shaping + FreeType rasterization for honest font proof images."""
from functools import lru_cache
from pathlib import Path
import freetype
import uharfbuzz as hb
from PIL import Image


@lru_cache(maxsize=128)
def engines(path,size,weight,optical):
    face=freetype.Face(path)
    face.set_var_design_coords([weight,optical])
    face.set_pixel_sizes(0,size)
    font=hb.Font(hb.Face(Path(path).read_bytes()))
    font.scale=(size*64,size*64)
    font.ppem=(size,size)
    font.ptem=size
    font.set_variations({'wght':weight,'opsz':optical})
    return face,font


def draw_text(image,path,text,x,y,size,weight=400,optical=14,center=False,color='#20221f'):
    face,font=engines(str(path),size,weight,optical)
    buffer=hb.Buffer();buffer.add_str(text);buffer.guess_segment_properties();hb.shape(font,buffer)
    width=sum(p.x_advance for p in buffer.glyph_positions)/64
    if center:x-=width/2
    baseline=y+size*.98
    for info,pos in zip(buffer.glyph_infos,buffer.glyph_positions):
        face.load_glyph(info.codepoint,freetype.FT_LOAD_RENDER)
        slot=face.glyph;bm=slot.bitmap
        if bm.width and bm.rows:
            raw=bytes(bm.buffer)
            packed=b''.join(raw[j*bm.pitch:j*bm.pitch+bm.width] for j in range(bm.rows))
            mask=Image.frombytes('L',(bm.width,bm.rows),packed)
            left=round(x+pos.x_offset/64+slot.bitmap_left)
            top=round(baseline-pos.y_offset/64-slot.bitmap_top)
            image.paste(color,(left,top,left+bm.width,top+bm.rows),mask)
        x+=pos.x_advance/64
    return width
