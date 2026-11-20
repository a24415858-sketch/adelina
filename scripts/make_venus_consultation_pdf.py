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
portrait=Image.open(ROOT/'assets/venus-user-selected-portrait.png').convert('RGBA')
w,h=portrait.size
# Remove only the surrounding studio backdrop using a feathered silhouette mask.
# The uploaded photograph itself is not regenerated or retouched.
outline=[(190,100),(255,82),(300,62),(355,55),(407,66),(450,87),
         (476,121),(491,158),(525,189),(546,224),(553,264),(575,299),
         (569,338),(595,364),(592,400),(610,427),(604,461),(624,494),
         (720,508),(810,550),(864,589),(864,1220),(0,1220),(0,832),
         (26,757),(13,727),(27,681),(45,645),(54,609),(78,571),
         (77,532),(92,494),(90,451),(101,410),(104,370),(116,334),
         (114,290),(131,251),(143,213),(143,173),(162,136)]
mask=Image.new('L',(w,h))
ImageDraw.Draw(mask).polygon([(round(px*w/864),round(py*h/1220)) for px,py in outline],fill=255)
alpha=np.asarray(mask.filter(ImageFilter.GaussianBlur(4)),dtype=float)/255
y,x=np.mgrid[0:h,0:w]
for edge in [np.clip((w-1-x)/(w*.055),0,1),np.clip((h-1-y)/(h*.19),0,1)]:
    alpha*=edge*edge*(3-2*edge)
portrait.putalpha(Image.fromarray(np.uint8(alpha*255)))
assert np.array_equal(np.asarray(portrait)[:,:,:3],np.asarray(Image.open(ROOT/'assets/venus-user-selected-portrait.png').convert('RGB')))
# Larger borderless silhouette flows naturally into the description and page background.
c.drawImage(ImageReader(portrait),32,425,220,220*h/w,mask='auto')
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
