"""Venus magazine in one palette and font system matching the supplied reference."""
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
OUT=ROOT/'documents/Venera_ediny_stil.pdf'
COVER=ROOT/'documents/Venera_oblozhka_referens.pdf'
data=json.loads((ROOT/'assets/venus-content.json').read_text())
source=Image.open(ROOT/'assets/venus-brand-reference.webp').convert('RGB')
# Crops are from the user's supplied image, unaltered; avoid the collage's printed numerals.
portrait=source.crop((135,30,374,390))
astrology=source.crop((714,0,928,310))
beauty=source.crop((990,600,1180,856))
for name,path in [('Display',ROOT/'assets/CormorantGaramond.ttf'),('Body',ROOT/'assets/Montserrat-Regular.ttf'),('Bold',ROOT/'assets/Montserrat-Regular.ttf'),('Zodiac',Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))]:
    pdfmetrics.registerFont(TTFont(name,str(path)))
W,H=595.276,841.89
BG='#EFE9E4'; INK='#785B51'; MUTED='#98796D'; LINE='#D4C2B7'
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
def para(s,x,y,width,size=12.2,leading=19):
    p=Paragraph(escape(s),ParagraphStyle('copy',fontName='Body',fontSize=size,leading=leading,textColor=HexColor(INK)))
    _,h=p.wrap(width,H); p.drawOn(c,x,y-h); return y-h

def image_cover(image,x,y,w,h):
    reader=ImageReader(image); iw,ih=reader.getSize(); scale=max(w/iw,h/ih); ww,hh=iw*scale,ih*scale
    c.saveState(); path=c.beginPath(); path.rect(x,y,w,h); c.clipPath(path,stroke=0,fill=0)
    c.drawImage(reader,x+(w-ww)/2,y+(h-hh)/2,ww,hh); c.restoreState()
def base(): fill(BG); c.rect(0,0,W,H,fill=1,stroke=0)
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

for index,s in enumerate(data):
    page=index+2; base(); page_head(page)
    text('ВЕНЕРА  /  ЗНАКИ ЗОДИАКА',47,731,8.5,'Bold',MUTED)
    right(s['symbol'],W-49,703,26,'Zodiac',MUTED)
    text(s['title'],45,662,40,'Display',INK)
    text('«'+s['archetype']+'»',47,629,21,'Display',MUTED)
    line(45,605,W-45,605)
    text('ЧЕМ ЦЕПЛЯЕТ',47,574,9,'Bold',MUTED)
    # The descriptions sit directly on the page, with light editorial rules instead of boxes.
    y=548
    for num,item in enumerate(s['attraction'],1):
        text(f'{num:02}',48,y-4,12,'Display',MUTED)
        end=para(item,86,y,W-135)
        y=end-18
        line(86,y+5,W-49,y+5,width=.4)
        y-=12
    assert y>300,(s['title'],y)
    if index in (3,8):
        img=astrology if index==3 else beauty
        image_cover(img,W-47-120,65,120,154)
        text('VENUS',48,207,9,'Bold',MUTED)
        text('Красота',48,172,24,'Display',INK)
        text('вашей индивидуальности',48,144,21,'Display',INK)
        line(48,122,290,122); star(52,97,3)
    else:
        line(47,219,W-47,219)
        text('VENUS',48,184,9,'Bold',MUTED)
        text('Красота вашей',48,151,24,'Display',INK)
        text('индивидуальности',48,125,24,'Display',INK)
        right(f'{index+1:02}  /  12',W-48,128,16,'Display',MUTED)
        star(W-54,172,3)
    c.showPage()
c.save()
buffer.seek(0)
# Retain the previously approved cover exactly; regenerate the 12 sign pages only.
with pymupdf.open(COVER) as previous, pymupdf.open(stream=buffer.read(),filetype='pdf') as signs, pymupdf.open() as result:
    assert len(previous)==13 and len(signs)==12
    result.insert_pdf(previous,from_page=0,to_page=0)
    result.insert_pdf(signs)
    result.set_toc(previous.get_toc()); result.set_metadata(previous.metadata)
    result.save(OUT,garbage=4,deflate=True)
with pymupdf.open(OUT) as doc:
    assert len(doc)==13
    for i,s in enumerate(data):
        actual=''.join(doc[i+1].get_text().split())
        assert ''.join(s['title'].split()) in actual
        for item in s['attraction']: assert ''.join(item.split()) in actual,(s['title'],item)
    print(f'{OUT}: {len(doc)} pages, all signs and descriptions checked')
