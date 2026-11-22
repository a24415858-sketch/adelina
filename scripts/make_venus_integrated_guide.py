"""Venus magazine with a naturally integrated portrait and accessible text."""
from pathlib import Path
import json
from io import BytesIO
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
OUT=ROOT/'documents/Venera_foto_v_fone.pdf'
COVER=ROOT/'documents/Venera_personal_photo.pdf'
BACKGROUND=ROOT/'assets/venus-pearl-marble-background.jpg'
COVER_PHOTO=ROOT/'assets/venus-cover-transparent.png'
data=json.loads((ROOT/'assets/venus-content.json').read_text())
source=Image.open(ROOT/'assets/venus-brand-reference.webp').convert('RGB')
# Crops are from the user's supplied image, unaltered; avoid the collage's printed numerals.
portrait=source.crop((135,30,374,390))
astrology=source.crop((714,0,928,310))
beauty=source.crop((990,600,1180,856))
for name,path in [('Display',ROOT/'assets/CormorantGaramond.ttf'),('Body',ROOT/'assets/Montserrat-Regular.ttf'),('Bold',ROOT/'assets/Montserrat-Regular.ttf'),('Zodiac',Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))]:
    pdfmetrics.registerFont(TTFont(name,str(path)))
W,H=595.276,841.89
BG='#F7F1E9'; INK='#40302B'; MUTED='#654C42'; LINE='#AB958B'
buffer=BytesIO()
c=canvas.Canvas(buffer,pagesize=(W,H),pageCompression=1)
c.setTitle('Венера — чем цепляет | журнал')

def fill(color): c.setFillColor(HexColor(color))
def text(s,x,y,size=10,font='Body',color=INK):
    fill(color); c.setFont(font,size); c.drawString(x,y,s)
def center(s,x,y,size=10,font='Body',color=INK):
    fill(color); c.setFont(font,size); c.drawCentredString(x,y,s)
def right(s,x,y,size=10,font='Body',color=INK):
    fill(color); c.setFont(font,size); c.drawRightString(x,y,s)
def line(x1,y1,x2,y2,color=LINE,width=.65):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width); c.line(x1,y1,x2,y2)
def para(s,x,y,width,size=13.8,leading=21):
    p=Paragraph(escape(s),ParagraphStyle('copy',fontName='Body',fontSize=size,leading=leading,textColor=HexColor(INK)))
    _,h=p.wrap(width,H); p.drawOn(c,x,y-h); return y-h

def image_cover(image,x,y,w,h):
    reader=ImageReader(image); iw,ih=reader.getSize(); scale=max(w/iw,h/ih); ww,hh=iw*scale,ih*scale
    c.saveState(); path=c.beginPath(); path.rect(x,y,w,h); c.clipPath(path,stroke=0,fill=0)
    c.drawImage(reader,x+(w-ww)/2,y+(h-hh)/2,ww,hh); c.restoreState()
def base(veil=.30):
    # Preserve the supplied image's proportions; a gentle full-page veil keeps text readable.
    image_cover(ImageReader(str(BACKGROUND)),0,0,W,H)
    c.saveState(); c.setFillColor(HexColor(BG)); c.setFillAlpha(veil)
    c.rect(0,0,W,H,fill=1,stroke=0); c.restoreState()
def star(x,y,sz=3.5):
    p=c.beginPath(); p.moveTo(x,y+sz*2); p.curveTo(x+sz*.15,y+sz*.3,x+sz*.3,y+sz*.15,x+sz*2,y)
    p.curveTo(x+sz*.3,y-sz*.15,x+sz*.15,y-sz*.3,x,y-sz*2)
    p.curveTo(x-sz*.15,y-sz*.3,x-sz*.3,y-sz*.15,x-sz*2,y)
    p.curveTo(x-sz*.3,y+sz*.15,x-sz*.15,y+sz*.3,x,y+sz*2)
    fill(MUTED); c.drawPath(p,fill=1,stroke=0)

def page_head(page):
    text('VENUS  /  ЛИЧНЫЙ БРЕНД',45,H-51,8,'Bold',MUTED)
    right(f'{page:02}',W-45,H-55,21,'Display',MUTED)
    line(45,H-66,W-45,H-66)

# The same personalized cover photograph, title and layout, over the new background.
base()
text('VENUS  /  PERSONAL GUIDE',40,793,8,'Body',INK)
line(40,776,W-40,776)
# Transparent portrait: its original pixels remain intact and the lower shirt
# fades gently into the background rather than ending in a rectangular frame.
c.drawImage(str(COVER_PHOTO),18,247,280,424,mask='auto')
x=319; width=W-40-x; mid=x+width/2
center('ВЕНЕРА',mid,603,38,'Display',INK)
center('ЧЕМ ЦЕПЛЯЕТ',mid,570,25,'Display',INK)
line(x+14,548,W-54,548)
center('В знаках зодиака',mid,518,10,'Body',INK)
center('Красота вашей',mid,467,19,'Display',INK)
center('индивидуальности',mid,443,19,'Display',INK)
line(x+14,391,W-54,391)
center('ПРИТЯЖЕНИЕ  ·  КРАСОТА',mid,367,8,'Body',INK)
center('ИНДИВИДУАЛЬНОСТЬ',mid,351,8,'Body',INK)
center('12 знаков зодиака',W/2,219,18,'Display',INK)
line(W/2-60,192,W/2+60,192)
star(W/2,154,4)
c.showPage()

for index,s in enumerate(data):
    page=index+2; base(.76); page_head(page)
    text('ВЕНЕРА  /  ЗНАКИ ЗОДИАКА',47,731,8.5,'Bold',MUTED)
    right(s['symbol'],W-49,703,26,'Zodiac',MUTED)
    text(s['title'],45,662,40,'Display',INK)
    text('«'+s['archetype']+'»',47,629,21,'Display',MUTED)
    line(45,605,W-45,605)
    text('ЧЕМ ЦЕПЛЯЕТ',47,574,10,'Bold',MUTED)
    # The descriptions sit directly on the page, with light editorial rules instead of boxes.
    y=548
    for num,item in enumerate(s['attraction'],1):
        text(f'{num:02}',48,y-4,14,'Display',MUTED)
        end=para(item,86,y,W-135)
        y=end-18
        line(86,y+5,W-49,y+5,width=.4)
        y-=12
    assert y>300,(s['title'],y)
    # Only typography below: all the extra small photos are removed.
    line(47,219,W-47,219)
    text('VENUS',48,184,10,'Bold',MUTED)
    text('Красота вашей',48,151,24,'Display',INK)
    text('индивидуальности',48,125,24,'Display',INK)
    right(f'{index+1:02}  /  12',W-48,128,16,'Display',MUTED)
    star(W-54,172,3)
    c.showPage()
c.save()
buffer.seek(0)
# Preserve the existing outline and metadata while replacing all backgrounds.
with pymupdf.open(COVER) as previous, pymupdf.open(stream=buffer.read(),filetype='pdf') as pages:
    assert len(previous)==len(pages)==13
    pages.set_toc(previous.get_toc()); pages.set_metadata(previous.metadata)
    pages.save(OUT,garbage=4,deflate=True)
with pymupdf.open(OUT) as doc:
    assert len(doc)==13
    for i,s in enumerate(data):
        actual=''.join(doc[i+1].get_text().split())
        assert ''.join(s['title'].split()) in actual
        for item in s['attraction']: assert ''.join(item.split()) in actual,(s['title'],item)
    print(f'{OUT}: {len(doc)} pages, all signs and descriptions checked')
