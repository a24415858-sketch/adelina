"""Complete Venus booklet: nine transcribed signs plus three newly written sections.
No screenshot crops or portraits are used in the PDF. Run from any directory.
"""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'documents/Венера в знаках зодиака.pdf'
W,H=595.276,841.89
INK=HexColor('#59404B');ROSE=HexColor('#A75E77');LINE=HexColor('#D7B5BF')
pdfmetrics.registerFont(TTFont('VenusDisplay',str(ROOT/'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('VenusBody','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('VenusBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('Венера в знаках зодиака')
c.setSubject('Притяжение, стиль, красота и личный магнетизм. Все 12 знаков зодиака.')

def base():
    c.drawImage(str(ROOT/'assets/venus-silk-shell-background.jpg'),0,0,W,H)

def center(y,text,size=30,font='VenusDisplay',color=INK):
    c.setFillColor(color);c.setFont(font,size);c.drawCentredString(W/2,y,text)

def paragraph(text,x,top,width,size=10.8,leading=15.6,font='VenusBody',color=INK):
    p=Paragraph(escape(text),ParagraphStyle('text',fontName=font,fontSize=size,leading=leading,textColor=color))
    _,height=p.wrap(width,800);p.drawOn(c,x,top-height)
    return top-height

def heading(top,title):
    c.setFillColor(ROSE);c.setFont('VenusBold',8.8);c.drawString(58,top-9,title.upper())
    return top-23

def bullet_block(top,title,lines):
    top=heading(top,title)
    for text in lines:
        c.setFillColor(ROSE);c.circle(61,top-6,1.4,stroke=0,fill=1)
        top=paragraph(text,71,top,W-129)-5
    return top-12

def separator(y):
    c.setStrokeColor(LINE);c.setLineWidth(.45);c.line(58,y,W-58,y)

base()
# Refined Venus glyph, vector-drawn rather than a portrait.
c.setStrokeColor(ROSE);c.setLineWidth(1.1)
c.circle(W/2,647,35,stroke=1,fill=0)
c.line(W/2,612,W/2,579);c.line(W/2-13,591,W/2+13,591)
c.setStrokeColor(Color(.75,.61,.66,alpha=.6));c.setLineWidth(.45)
c.circle(W/2,635,68,stroke=1,fill=0)
center(481,'Венера',size=83,color=ROSE)
center(433,'в знаках зодиака',size=34)
c.setStrokeColor(LINE);c.line(W/2-35,408,W/2+35,408)
center(379,'ПРИТЯЖЕНИЕ  ·  КРАСОТА  ·  МАГНЕТИЗМ',size=8.6,font='VenusBody',color=ROSE)
c.showPage()

items=json.loads((ROOT/'assets/venus-content.json').read_text())
for idx,item in enumerate(items):
    base()
    c.bookmarkPage(f'venus-{idx}');c.addOutlineEntry(item['title'],f'venus-{idx}',level=0)
    center(791,item['element'].upper(),size=8.2,font='VenusBody',color=ROSE)
    center(742,item['title'],size=38)
    center(710,'«'+item['archetype']+'»',size=23,color=ROSE)
    c.setStrokeColor(LINE);c.setLineWidth(.5)
    c.line(W/2-54,691,W/2-15,691);c.line(W/2+15,691,W/2+54,691)
    center(686,item['symbol'],size=14,font='VenusBody',color=ROSE)
    top=665
    top=bullet_block(top,'Чем цепляет',item['attraction'])
    top=bullet_block(top,'Как выкрутить на максимум',item['amplify'])
    separator(top+3);top-=13
    top=heading(top,'Как раскрывается')
    for label,key in [('Тело','body'),('Дом','home'),('Образ','style')]:
        paragraph(label,58,top,53,size=10.6,leading=15.6,font='VenusBold',color=ROSE)
        top=paragraph(item[key],116,top,W-174)-7
    top-=11
    # Measure and draw the final block before placing its text.
    p=Paragraph(escape(item['diminish']),ParagraphStyle('measure',fontName='VenusBody',fontSize=10.8,leading=15.6))
    _,height=p.wrap(W-146,800)
    box_h=height+43
    c.setFillColor(Color(.98,.91,.93,alpha=.86));c.setStrokeColor(LINE);c.setLineWidth(.5)
    c.roundRect(48,top-box_h,W-96,box_h,9,fill=1,stroke=1)
    c.setFillColor(ROSE);c.setFont('VenusBold',8.5);c.drawString(65,top-18,'ЧТО ГАСИТ МАГНЕТИЗМ')
    bottom=paragraph(item['diminish'],65,top-28,W-130)
    assert bottom>215,(item['title'],bottom)
    print(item['title'],round(bottom,1))
    c.showPage()
c.save()
print(OUT)
