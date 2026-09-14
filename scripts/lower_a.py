"""Original two-storey a: eight outer and four counter cubic arcs."""
from parameters import at_location
from pathlib import Path
from functools import lru_cache
import json
from geometry import Drawing

NAMES=['notchY','bottomX','leftY','neckX','neckY','bowlRightY','hookRightY','innerTopX','innerTopY','tipY','tipOuterX','tipInnerX','outerTopX','outerRightY','counterLeftX','counterLeftY','counterBottomX','counterBottomY','counterRightY','counterTopX','counterTopY','counterTopRightY']


def contours(p,k):
    s,b=p['stem'],p['bottom'];ny,bx,ly,nx,nyb,bry,hy,ix,iy,ty,to,ti,ox,oy,cl,cly,cbx,cby,cry,ctx,cty,ctry=[p[n] for n in NAMES]
    outer=[(s,0),(s,ny),
        ((s-(s-bx)*k[0],ny-(ny-b)*k[0]),(bx+(s-bx)*k[1],b),(bx,b)),
        ((bx-bx*k[2],b),(0,ly-(ly-b)*k[3]),(0,ly)),
        ((0,ly+(nyb-ly)*k[4]),(nx-nx*k[5],nyb),(nx,nyb)),
        ((nx+(s-nx)*k[6],nyb),(s-(s-nx)*k[7],bry),(s,bry)),
        (s,hy),
        ((s,hy+(iy-hy)*k[8]),(ix+(s-ix)*k[9],iy),(ix,iy)),
        ((ix-(ix-ti)*k[10],iy),(ti,ty+(iy-ty)*k[11]),(ti,ty)),
        (to,ty),
        ((to,ty+(1-ty)*k[12]),(ox-(ox-to)*k[13],1),(ox,1)),
        ((ox+(1-ox)*k[14],1),(1,oy+(1-oy)*k[15]),(1,oy))]
    inner=[
        ((s-(s-ctx)*k[16],ctry),(ctx+(s-ctx)*k[17],cty),(ctx,cty)),
        ((ctx-(ctx-cl)*k[18],cty),(cl,cly+(cty-cly)*k[19]),(cl,cly)),
        ((cl,cly-(cly-cby)*k[20]),(cbx-(cbx-cl)*k[21],cby),(cbx,cby)),
        ((cbx+(s-cbx)*k[22],cby),(s,cry-(cry-cby)*k[23]),(s,cry))]
    return [((1,0),outer,False),((s,ctry),inner,True)]


@lru_cache(maxsize=1)
def load():
    path=Path(__file__).resolve().parents[1]/'sources/lower-a.json'
    return json.loads(path.read_text())['glyphs'] if path.exists() else {}


def apply(glyph,key,design):
    ch={'uni0430':'а'}.get(key,key);data=load().get(ch)
    if data is None:return
    p=at_location(data, design);drawing=Drawing()
    for start,segments,counter in contours(p['parameters'],p['handles']):drawing.outline(start,segments,counter)
    left,bottom,right,top=p['bounds'];glyph.clearContours()
    drawing.replay(glyph.getPen(),(right-left,0,0,top,left,0));glyph.width=p['advance']
