"""Render the actual compiled font with FreeType, without substituting glyphs."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from render import draw_text
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'proofs';out.mkdir(exist_ok=True)
fontfile=ROOT/'dist/TabunaSansVariable.ttf'
im=Image.new('RGB',(1800,1610),'#f8f8f4');p=ImageDraw.Draw(im)
def text(content,x,y,size=55,weight=400,optical=14):
    draw_text(im,fontfile,content,x,y,size,weight,optical)
text('Tabuna Sans / Regular 400',60,24,62)
rows=['АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ',
      'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
      'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
      'abcdefghijklmnopqrstuvwxyz 0123456789',
      'Ясность в каждой букве. Знакомое ощущение.',
      'Designed to feel familiar. Attention to detail.',
      'Il1 O0 ДЛЖФЫЙё — AVATAR Typography 12 480,00 ₽']
for i,row in enumerate(rows):text(row,60,135+i*97,52)
for j,w in enumerate((100,400,700,900)):
    text(f'{w}  Буквы складываются в слова. Hamburgefontsiv',60,850+j*116,49,w,14)
text('Мелкий текст: формы, числа 1234567890, диакритика Йё éü. Подтвердить действие',60,1350,20)
text('Открытый рисунок для текста и интерфейсов. The quick brown fox jumps over the lazy dog.',60,1420,16)
im.save(out/'overview.png')
print(out/'overview.png')

# Full Cyrillic and extended coverage proofs use actual glyphs from the font.
import json
charset=json.loads((ROOT/'sources/charset.json').read_text())
groups={
    'cyrillic':[r for r in charset if 0x400<=ord(r['character'])<=0x491],
    'extended':[r for r in charset if 0xA0<ord(r['character'])<0x180 and r['character'].isalpha()],
    'signs':[r for r in charset if not r['character'].isalpha() and not r['character'].isspace() and ord(r['character'])<0xFEFF],
}
for group,chars in groups.items():
    for weight in ([400,900] if group=='cyrillic' else [400]):
        cols=10;cw=150;rh=137
        sheet=Image.new('RGB',(cols*cw,((len(chars)+cols-1)//cols)*rh),'#f8f8f4');draw=ImageDraw.Draw(sheet)
        for index,entry in enumerate(chars):
            x=(index%cols)*cw;y=(index//cols)*rh
            c=entry['character']
            if 0x300<=ord(c)<=0x328:c='a'+c
            draw.rectangle((x,y,x+cw,y+rh),outline='#c7c9bf')
            draw_text(sheet,fontfile,c,x+cw/2,y+7,62,weight,14,center=True)
            draw.text((x+cw/2,y+rh-25),entry['codepoint'],anchor='mt',fill='#62655d')
        sheet.save(out/f'{group}-{weight}.png')

before=ROOT/'build/TabunaSans-before.ttf'
if before.exists():
    comparison=Image.new('RGB',(1600,640),'#f8f8f4');label=ImageDraw.Draw(comparison)
    label.text((45,30),'INITIAL CONSTRUCTION',fill='#62655d')
    label.text((835,30),'CURRENT ORIGINAL OUTLINES',fill='#62655d')
    for x,path in [(45,before),(835,fontfile)]:
        for y,weight in [(80,100),(245,400),(410,900)]:
            draw_text(comparison,path,'Ясность в каждой букве.',x,y,48,weight,14)
            draw_text(comparison,path,'Дд Лл Жж Тт · 1234567890',x,y+65,40,weight,14)
    comparison.save(out/'revision-comparison.png')

previous=ROOT/'build/TabunaSans-before-cyrillic-refinement.ttf'
if previous.exists():
    sheet=Image.new('RGB',(1500,700),'#f8f8f4');labels=ImageDraw.Draw(sheet)
    labels.text((40,25),'BEFORE',fill='#62655d')
    labels.text((795,25),'REVISED ORIGINAL OUTLINES',fill='#62655d')
    for x,path in [(40,previous),(795,fontfile)]:
        for y,weight in [(60,100),(260,400),(460,900)]:
            draw_text(sheet,path,'Жж Ыы Ьь Ъъ',x,y,68,weight,14)
            draw_text(sheet,path,'Жизнь. Связь. Ясные мысли.',x,y+90,40,weight,14)
    sheet.save(out/'cyrillic-refinement.png')
