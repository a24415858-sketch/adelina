"""Editorial Venus guide using a small number of photos from the supplied collage."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from PIL import Image
import pymupdf
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'documents/Venera_lichny_brend.pdf'
data=json.loads((ROOT/'assets/venus-content.json').read_text())
reference=Image.open(ROOT/'assets/venus-brand-leopard-reference.webp').convert('RGB')
# Direct crops from the reference: no generated or retouched faces.
portrait=reference.crop((145,25,472,455))
astro=reference.crop((905,30,1170,380))
for name,path in [('Display',ROOT/'assets/CormorantGaramond.ttf'),('Body',Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')),('Bold',Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))]:
    pdfmetrics.registerFont(TTFont(name,str(path)))
W,H=595.276,841.89
BG='#F2EBE6'; PAPER='#F9F5F1'; INK='#59463E'; MUTED='#967A6C'; LINE='#D7C6BC'
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('Венера — чем цепляет')

def fill(color): c.setFillColor(HexColor(color))
def text(s,x,y,size=10,font='Body',color=INK):
    fill(color); c.setFont(font,size); c.drawString(x,y,s)
def center(s,x,y,size=10,font='Body',color=INK):
    fill(color); c.setFont(font,size); c.drawCentredString(x,y,s)
def right(s,x,y,size=10,font='Body',color=INK):
    fill(color); c.setFont(font,size); c.drawRightString(x,y,s)
def line(x1,y1,x2,y2,color=LINE,width=.65):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width); c.line(x1,y1,x2,y2)
def para(s,x,y,width,size=10.8,leading=16):
    style=ParagraphStyle('copy',fontName='Body',fontSize=size,leading=leading,textColor=HexColor(INK))
    p=Paragraph(escape(s),style); _,h=p.wrap(width,H); p.drawOn(c,x,y-h); return y-h

def image_cover(image,x,y,w,h):
    im=ImageReader(image); iw,ih=im.getSize(); scale=max(w/iw,h/ih)
    ww,hh=iw*scale,ih*scale
    c.saveState(); path=c.beginPath(); path.rect(x,y,w,h); c.clipPath(path,stroke=0,fill=0)
    c.drawImage(im,x+(w-ww)/2,y+(h-hh)/2,ww,hh); c.restoreState()
def base(): fill(BG); c.rect(0,0,W,H,fill=1,stroke=0)
def star(x,y,sz=4):
    p=c.beginPath(); p.moveTo(x,y+sz*2); p.curveTo(x+sz*.15,y+sz*.3,x+sz*.3,y+sz*.15,x+sz*2,y)
    p.curveTo(x+sz*.3,y-sz*.15,x+sz*.15,y-sz*.3,x,y-sz*2)
    p.curveTo(x-sz*.15,y-sz*.3,x-sz*.3,y-sz*.15,x-sz*2,y)
    p.curveTo(x-sz*.3,y+sz*.15,x-sz*.15,y+sz*.3,x,y+sz*2)
    fill(MUTED); c.drawPath(p,fill=1,stroke=0)

# Cover: one modest, original-resolution portrait and editorial whitespace.
base()
text('VENUS  /  PERSONAL GUIDE',42,H-53,8.5,'Bold',MUTED)
right('01',W-42,H-57,22,'Display',MUTED)
line(42,H-68,W-42,H-68)
image_cover(portrait,310,345,210,276)
text('Венера',43,611,58,'Display')
text('чем',45,565,36,'Display')
text('цепляет',45,527,36,'Display')
line(45,502,248,502)
text('В ЗНАКАХ ЗОДИАКА',45,470,8.5,'Bold',MUTED)
text('Красота вашей',45,391,19,'Display')
text('индивидуальности',45,367,19,'Display')
line(42,298,W-42,298)
center('ПРИТЯЖЕНИЕ  ·  КРАСОТА  ·  МАГНЕТИЗМ',W/2,254,8.2,'Bold',MUTED)
star(W/2,176,4)
line(W/2-80,150,W/2+80,150)
center('12 знаков зодиака',W/2,118,16,'Display',INK)
c.bookmarkPage('cover'); c.addOutlineEntry('Венера — чем цепляет','cover',0); c.showPage()

for chunk in range(0,12,2):
    page=2+chunk//2
    base()
    text('ВЕНЕРА  /  В ЗНАКАХ',42,H-53,8.5,'Bold',MUTED)
    right(f'{page:02}',W-42,H-57,22,'Display',MUTED)
    line(42,H-68,W-42,H-68)
    text('Чем цепляет',42,731,36,'Display')
    text('ДВА ОБРАЗА  /  ДВЕ ИСТОРИИ',43,704,8,'Bold',MUTED)
    # Two columns echo the clean reference layout without large photographs.
    panel_y=312; panel_h=355; margin=42; gap=14; cw=(W-2*margin-gap)/2
    for n,s in enumerate(data[chunk:chunk+2]):
        x=margin+n*(cw+gap)
        fill(PAPER); c.rect(x,panel_y,cw,panel_h,fill=1,stroke=0)
        center(s['symbol'],x+cw/2,626,19,'Body',MUTED)
        size=24
        while pdfmetrics.stringWidth(s['title'],'Display',size)>cw-20: size-=.5
        center(s['title'],x+cw/2,590,size,'Display',INK)
        center('«'+s['archetype']+'»',x+cw/2,567,16,'Display',MUTED)
        line(x+20,549,x+cw-20,549)
        text('ЧЕМ ЦЕПЛЯЕТ',x+17,526,8,'Bold',MUTED)
        y=510
        for item in s['attraction']:
            fill(MUTED); c.circle(x+19,y-5,1.6,fill=1,stroke=0)
            y=para(item,x+29,y,cw-45)-9
        assert y>panel_y+18,(page,s['title'],y)
        c.bookmarkPage('sign'+s['title']); c.addOutlineEntry(s['title'],'sign'+s['title'],1)
    # Only two interior pages have one small photograph; the other pages remain clean.
    line(42,278,W-42,278)
    if page in (4,6):
        pic=portrait if page==4 else astro
        image_cover(pic,W-42-123,79,123,157)
        text('VENUS',48,221,10,'Bold',MUTED)
        text('Красота',48,185,24,'Display')
        text('в каждой детали',48,156,24,'Display')
        line(48,132,250,132); star(52,104,3)
    else:
        center('VENUS  /  '+f'{chunk+1:02} — {chunk+2:02}',W/2,221,8.5,'Bold',MUTED)
        center('Красота вашей индивидуальности',W/2,177,23,'Display',INK)
        star(W/2,122,4)
        line(W/2-65,95,W/2+65,95)
    c.showPage()
c.save()
with pymupdf.open(OUT) as pdf:
    assert len(pdf)==7
    full=''.join(''.join(p.get_text().split()) for p in pdf)
    for s in data:
        for item in s['attraction']:
            assert ''.join(item.split()) in full,(s['title'],item)
    print(f'{OUT}: {len(pdf)} pages; all 36 descriptions retained')
