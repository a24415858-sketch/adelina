"""Build the separate Moon in Houses beach booklet. Run from any directory."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'documents' / 'Луна в Домах.pdf'
W, H = 595.276, 841.89
INK = HexColor('#23485D')
MUTED = HexColor('#5A8198')
pdfmetrics.registerFont(TTFont('Display', str(ROOT/'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))

# Use the supplied beach image itself; crop to A4 without stretching the shells.
original = Image.open(ROOT/'assets/houses-beach-reference.png').convert('RGB')
ARTWORK = ImageOps.fit(original, (1000, 1414), method=Image.Resampling.LANCZOS,
                       centering=(.5,.2))
BG=ImageReader(ARTWORK)
c=canvas.Canvas(str(OUT), pagesize=(W,H), pageCompression=1)
c.setTitle('Луна в Домах')
c.setAuthor('')
c.setSubject('Луна в двенадцати домах • голубое море и ракушки')

def text(x,y,s,font='Body',size=10,color=INK):
    c.setFillColor(color); c.setFont(font,size); c.drawString(x,y,s)

def center(y,s,font='Display',size=30,color=INK):
    c.setFillColor(color);c.setFont(font,size);c.drawCentredString(W/2,y,s)

def pearl(x,y,r):
    for k in range(50,0,-1):
        t=k/50
        c.setFillColor(Color(.97-.28*t,.99-.20*t,1-.11*t))
        c.circle(x+(1-t)*(-r*.24),y+(1-t)*r*.28,r*t,stroke=0,fill=1)
    c.setFillColor(Color(1,1,1,alpha=.8));c.circle(x-r*.27,y+r*.32,r*.12,fill=1,stroke=0)

def base():
    c.drawImage(BG,0,0,W,H)

def panel(bottom, top):
    c.setFillColor(Color(.965,.984,1,alpha=.94))
    c.setStrokeColor(Color(1,1,1,alpha=.95))
    c.setLineWidth(.8)
    c.roundRect(42,bottom,W-84,top-bottom,14,stroke=1,fill=1)
    c.setStrokeColor(Color(.57,.73,.84,alpha=.6))
    c.setLineWidth(.45)
    c.roundRect(49,bottom+7,W-98,top-bottom-14,10,stroke=1,fill=0)

def ornament(y):
    c.setStrokeColor(HexColor('#9DBACF'));c.setLineWidth(.5)
    c.line(W/2-49,y,W/2-13,y);c.line(W/2+13,y,W/2+49,y)
    pearl(W/2,y,4)

def paragraph_height(s,width,font,size,leading):
    p=Paragraph(s.replace(' - ',' — '),ParagraphStyle('measure',fontName=font,fontSize=size,leading=leading))
    return p.wrap(width,700)[1]

def para(s,x,top,width,font,size,leading,color=INK):
    # Typography only: spaced hyphens become em dashes; wording is unchanged.
    s=s.replace(' - ',' — ')
    p=Paragraph(s,ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=color))
    _,h=p.wrap(width,700);p.drawOn(c,x,top-h)
    return top-h

# A seamless pearly glow, not a title card: artwork continues behind the lettering.
cover = ARTWORK.copy()
arr = np.asarray(cover, dtype=float)
h, w = arr.shape[:2]
y, x = np.mgrid[0:h, 0:w]
x, y = x / w, y / h
glow = .89 * np.exp(-((x-.5)/.65)**4 - ((y-.135)/.115)**4)
arr = arr*(1-glow[...,None]) + np.array([239,248,255])*glow[...,None]
c.drawImage(ImageReader(Image.fromarray(np.uint8(np.clip(arr,0,255)))),0,0,W,H)
center(719,'Луна',size=88,color=HexColor('#347BAF'))
center(669,'в Домах',size=46,color=HexColor('#347BAF'))
c.setStrokeColor(Color(.40,.64,.80,alpha=.8));c.setLineWidth(.6)
c.line(W/2-27,647,W/2+27,647)
c.showPage()

data=json.loads((ROOT/'assets/houses-content.json').read_text())
for idx,item in enumerate(data,1):
    base()
    c.bookmarkPage(f'house{idx}');c.addOutlineEntry(item['title'],f'house{idx}',level=0)
    width=W-144
    # Fit the frosted panel to this sign's actual text, exposing more of the artwork.
    end=674-paragraph_height(item['paragraphs'][0],width,'Display',23,28)-22
    for s in item['paragraphs'][1:]:
        end-=paragraph_height(s,width,'Body',12.5,20)+14
    bottom=end-18
    assert bottom>205,(item['title'],bottom)
    panel(bottom,792)
    ornament(763)
    center(716,item['title'],font='Display',size=39)
    top=674
    top=para(item['paragraphs'][0],72,top,width,'Display',23,28)-22
    for s in item['paragraphs'][1:]:
        top=para(s,72,top,width,'Body',12.5,20)-14
    c.showPage()
c.save()
print(OUT)
