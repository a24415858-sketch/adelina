"""Venus consultation invitation with the user-approved pearl-style AI-edited portrait."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from PIL import Image, ImageOps, ImageFilter
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

# Hair-only AI edit from the original photo: keep its makeup, grain and lighting.
# A softly feathered editorial mask integrates it into the page without a frame.
portrait=ImageOps.exif_transpose(Image.open(ROOT/'assets/venus-portrait-natural-curls.png')).convert('RGBA')
portrait=ImageOps.fit(portrait,(900,1200),method=Image.Resampling.LANCZOS,centering=(.5,.05))
h,w=1200,900
y,x=np.mgrid[0:h,0:w]
left=np.clip(x/(w*.12),0,1)
right=np.clip((w-1-x)/(w*.20),0,1)
top=np.clip(y/(h*.06),0,1)
bottom=np.clip((h-1-y)/(h*.20),0,1)
alpha=np.ones((h,w),dtype=float)
for fade in [left,right,top,bottom]:
    alpha*=fade*fade*(3-2*fade)
portrait.putalpha(Image.fromarray(np.uint8(alpha*255)))
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
