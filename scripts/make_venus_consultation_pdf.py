"""Venus consultation invitation with the user-approved pearl-style AI-edited portrait."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from PIL import Image, ImageFilter
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
# One continuous page background: no card, frame or rounded panel.
c.setFillColor(Color(1,.985,.985,alpha=.60));c.rect(0,0,W,H,stroke=0,fill=1)
centered(d['label'],790,font='ConsultBody',size=8,color=ROSE)
centered(d['title'],746,size=44,color=ROSE)

# Transparent silhouette with inward edge feathering; no generated pixels or frame.
portrait=Image.open(ROOT/'assets/venus-portrait-transparent.png').convert('RGBA')
w,h=portrait.size
# Remove the hard cut-paper fringe without blurring facial or hair RGB detail.
original_alpha=portrait.getchannel('A')
soft_alpha=original_alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(2.2))
portrait.putalpha(Image.fromarray(np.minimum(np.asarray(original_alpha),np.asarray(soft_alpha))))
# Preserve the natural segmented silhouette; absolutely no oval or rounded clipping.
# Only dissolve the original image's cropped lower boundary, without adding backdrop.
y,x=np.mgrid[0:h,0:w]
lower=np.clip((.985-y/(h-1))/.22,0,1)
lower=lower*lower*(3-2*lower)
# Broader transition across cropped bouquet wrapping, not an oval crop.
side=np.clip((w-1-x)/(w*.16),0,1)
side=side*side*(3-2*side)
left=np.clip(x/(w*.07),0,1)
left=left*left*(3-2*left)
alpha=np.asarray(portrait.getchannel('A'),dtype=float)*lower*side*left
portrait.putalpha(Image.fromarray(np.uint8(alpha)))
assert np.array_equal(np.asarray(portrait)[:,:,:3],np.asarray(Image.open(ROOT/'assets/venus-user-selected-portrait.png').convert('RGB')))
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

# Offer text also sits directly on the same background, without a box.
centered(d['offer_title'],222,size=24,color=ROSE)
b=paragraph(d['offer'],61,206,W-122,size=10.5,leading=15.5)
assert b>151,b
paragraph(d['price'],62,150,185,font='ConsultBody',size=27,leading=32,color=ROSE)
paragraph(d['price_label'],62,115,200,size=6.5,leading=8,color=ROSE)
paragraph(d['cta'],289,139,237,size=10.6,leading=16)
centered(d['footer'],61,font='ConsultDisplay',size=16,color=INK)
c.showPage();c.save()
print(OUT)
