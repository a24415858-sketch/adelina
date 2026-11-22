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
OUT=ROOT/'documents/Venera_12_znakov.pdf'
data=json.loads((ROOT/'assets/venus-content.json').read_text())
reference=Image.open(ROOT/'assets/venus-brand-leopard-reference.webp').convert('RGB')
# Direct crops from the reference: no generated or retouched faces.
portrait=reference.crop((145,25,472,455))
astro=reference.crop((905,30,1170,380))
new_reference=Image.open(ROOT/'assets/venus-brand-reference.webp').convert('RGB')
cover_portrait=new_reference.crop((135,30,374,390))
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
image_cover(cover_portrait,310,345,210,276)
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

for index,s in enumerate(data):
    page=index+2
    base()
    text('ВЕНЕРА  /  В ЗНАКАХ',42,H-53,8.5,'Bold',MUTED)
    right(f'{page:02}',W-42,H-57,22,'Display',MUTED)
    line(42,H-68,W-42,H-68)
    text('Чем цепляет',42,731,36,'Display')
    text('ВАША ИНДИВИДУАЛЬНОСТЬ',43,704,8,'Bold',MUTED)
    # One sign per page, with a single spacious editorial text panel.
    fill(PAPER); c.rect(42,295,W-84,370,fill=1,stroke=0)
    center(s['symbol'],W/2,625,20,'Body',MUTED)
    center(s['title'],W/2,582,32,'Display',INK)
    center('«'+s['archetype']+'»',W/2,556,18,'Display',MUTED)
    line(100,537,W-100,537)
    text('ЧЕМ ЦЕПЛЯЕТ',78,506,9,'Bold',MUTED)
    y=484
    for item in s['attraction']:
        fill(MUTED); c.circle(82,y-6,2,fill=1,stroke=0)
        y=para(item,96,y,W-174,size=12,leading=18)-13
    assert y>320,(page,s['title'],y)
    c.bookmarkPage('sign'+s['title']); c.addOutlineEntry(s['title'],'sign'+s['title'],1)
    line(42,264,W-42,264)
    # Keep the existing small interior photos; only the cover portrait changes.
    if index in (4,8):
        pic=portrait if index==4 else astro
        image_cover(pic,W-42-120,70,120,155)
        text('VENUS',48,215,10,'Bold',MUTED)
        text('Красота',48,180,24,'Display')
        text('в каждой детали',48,151,24,'Display')
        line(48,126,250,126); star(52,99,3)
    else:
        center('VENUS  /  '+f'{index+1:02} — 12',W/2,210,8.5,'Bold',MUTED)
        center('Красота вашей индивидуальности',W/2,166,23,'Display',INK)
        star(W/2,111,4)
        line(W/2-65,84,W/2+65,84)
    c.showPage()
c.save()
with pymupdf.open(OUT) as pdf:
    assert len(pdf)==13
    full=''.join(''.join(p.get_text().split()) for p in pdf)
    for idx,s in enumerate(data):
        sign_text=''.join(pdf[idx+1].get_text().split())
        assert ''.join(s['title'].split()) in sign_text
        for item in s['attraction']:
            assert ''.join(item.split()) in sign_text, (s['title'],item)
            assert ''.join(item.split()) in full,(s['title'],item)
    print(f'{OUT}: {len(pdf)} pages; all 36 descriptions retained')
