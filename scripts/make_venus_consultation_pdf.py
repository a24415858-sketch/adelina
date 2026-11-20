"""Venus consultation invitation with the user-approved pearl-style AI-edited portrait."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from PIL import Image, ImageOps, ImageFilter, ImageDraw
from collections import deque
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'documents/Личный разбор Венеры.pdf'
d=json.loads((ROOT/'assets/venus-consultation-content.json').read_text())
W,H=595.276,841.89
INK=HexColor('#59404B');ROSE=HexColor('#A75E77');LINE=HexColor('#D7B5BF')
pdfmetrics.registerFont(TTFont('ConsultDisplay',str(ROOT/'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('ConsultBody','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('Личный разбор Венеры — 1 000 рублей')
c.setSubject('Знак, дом и аспекты Венеры. Приглашение на индивидуальный разбор.')

def centered(s,y,font='ConsultDisplay',size=28,color=INK):
    c.setFont(font,size);c.setFillColor(color);c.drawCentredString(W/2,y,s)

def paragraph(s,x,top,width,font='ConsultBody',size=11.2,leading=17,color=INK):
    text=escape(s).replace('\n','<br/>')
    p=Paragraph(text,ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=color))
    _,height=p.wrap(width,H)
    p.drawOn(c,x,top-height)
    return top-height

c.drawImage(str(ROOT/'assets/venus-background.jpg'),0,0,W,H)
# A quiet translucent veil leaves the silk texture visible behind the editorial layout.
c.setFillColor(Color(1,.985,.985,alpha=.68));c.roundRect(28,79,W-56,H-104,18,stroke=0,fill=1)
centered(d['label'],790,font='ConsultBody',size=8,color=ROSE)
centered(d['title'],746,size=44,color=ROSE)

# Use the exact approved portrait: no new generation, recoloring or face retouch.
portrait=Image.open(ROOT/'assets/venus-approved-portrait-loose-curls.png').convert('RGBA')
assert portrait.size==(680,960)
# Hand-drawn silhouette removes the studio backdrop; only alpha is changed.
mask=Image.new('L',portrait.size)
outline=[(190,55),(244,42),(294,48),(338,62),(373,88),(404,134),
         (425,183),(449,225),(450,277),(480,316),(493,365),(479,395),
         (540,401),(618,422),(680,451),(680,960),(0,960),(0,650),
         (20,573),(11,547),(34,487),(52,447),(66,401),(60,353),
         (62,287),(82,233),(83,177),(106,121),(135,85)]
ImageDraw.Draw(mask).polygon(outline,fill=255)
alpha=np.asarray(mask.filter(ImageFilter.GaussianBlur(3)),dtype=float)
h,w=960,680
y,x=np.mgrid[0:h,0:w]
bottom=np.clip((h-1-y)/(h*.17),0,1)
right=np.clip((w-1-x)/(w*.07),0,1)
alpha*=bottom*bottom*(3-2*bottom)*right*right*(3-2*right)
portrait.putalpha(Image.fromarray(np.uint8(alpha)))
# The center of the face is completely opaque; the RGB pixels remain untouched.
assert np.array_equal(np.asarray(portrait)[:,:,:3],np.asarray(Image.open(ROOT/'assets/venus-approved-portrait-loose-curls.png').convert('RGB')))
c.drawImage(ImageReader(portrait),29,425,228,305,mask='auto')
end=paragraph(d['intro_title'],263,690,282,font='ConsultDisplay',size=29,leading=31,color=ROSE)
end=paragraph(d['intro'],263,end-20,278,size=11.7,leading=18.3)
assert end>436,end

centered(d['bridge'],401,size=24)
c.setStrokeColor(LINE);c.setLineWidth(.45);c.line(W/2,278,W/2,377)
paragraph(d['house_title'],49,375,233,font='ConsultDisplay',size=24,leading=27,color=ROSE)
b1=paragraph(d['house'],49,342,230,size=10.8,leading=16)
paragraph(d['aspects_title'],319,375,230,font='ConsultDisplay',size=24,leading=27,color=ROSE)
b2=paragraph(d['aspects'],319,342,227,size=10.8,leading=16)
assert min(b1,b2)>257,(b1,b2)

c.setFillColor(Color(.98,.91,.93,alpha=.96));c.setStrokeColor(LINE)
c.roundRect(43,101,W-86,148,12,stroke=1,fill=1)
centered(d['offer_title'],222,size=24,color=ROSE)
b=paragraph(d['offer'],61,206,W-122,size=10.5,leading=15.5)
assert b>151,b
paragraph(d['price'],62,150,185,font='ConsultBody',size=27,leading=32,color=ROSE)
paragraph(d['price_label'],62,115,200,size=6.5,leading=8,color=ROSE)
paragraph(d['cta'],289,139,237,size=10.6,leading=16)
centered(d['footer'],61,font='ConsultDisplay',size=16,color=INK)
c.showPage();c.save()
print(OUT)
