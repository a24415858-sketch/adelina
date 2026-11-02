"""Build the blue mother-of-pearl zodiac booklet. Run from any directory."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'documents' / 'Луна в знаках зодиака.pdf'
W, H = 595.276, 841.89
INK = HexColor('#23485D')
MUTED = HexColor('#5A8198')
pdfmetrics.registerFont(TTFont('Display', str(ROOT/'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))

def blue_background():
    # Grade the original artwork, keeping its colorful nacre rather than desaturating it.
    image = Image.open(ROOT/'assets/pearl-ocean-background.jpg').convert('RGB')
    hsv = np.asarray(image.convert('HSV'), dtype=float).copy()
    hue, saturation = hsv[..., 0] / 255, hsv[..., 1] / 255
    # Map green, mint and cyan directly to sky blue rather than partially rotating aqua.
    water = np.clip((hue - .15) / .08, 0, 1) * np.clip((.64 - hue) / .04, 0, 1)
    water = water * water * (3 - 2 * water)
    target_hue = .595  # 214 degrees: blue, not cyan/turquoise.
    hsv[..., 0] = 255 * (hue * (1 - water) + target_hue * water)
    hsv[..., 1] = np.clip(hsv[..., 1] * (1.18 + water * .18), 0, 255)
    hsv[..., 2] = np.clip(hsv[..., 2] * 1.025 + 2, 0, 255)
    graded = Image.fromarray(hsv.astype('uint8'), mode='HSV').convert('RGB')
    return ImageReader(graded)

BG=blue_background()
c=canvas.Canvas(str(OUT), pagesize=(W,H), pageCompression=1)
c.setTitle('Луна в знаках зодиака')
c.setAuthor('')
c.setSubject('Двенадцать лунных знаков • голубой перламутр и ракушки')

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

def base(num=None):
    c.drawImage(BG,0,0,W,H)
    if num:
        # A translucent ivory-blue reading panel keeps the rich art off the text.
        c.setFillColor(Color(.95,.978,1,alpha=.91))
        c.setStrokeColor(Color(1,1,1,alpha=.95))
        c.setLineWidth(.8)
        c.roundRect(34,246,W-68,536,18,stroke=1,fill=1)
        text(57,750,'Л У Н А  В  З Н А К А Х  З О Д И А К А',size=8,color=MUTED)

def para(s,x,top,width,font,size,leading,color=INK):
    # Typography only: spaced hyphens become em dashes; wording is unchanged.
    s=s.replace(' - ',' — ')
    p=Paragraph(s,ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=color))
    _,h=p.wrap(width,700);p.drawOn(c,x,top-h)
    return top-h

base()
# The generated open shell and pearl are part of the full-bleed ocean scene.
c.setStrokeColor(HexColor('#AFC7CB'));c.setLineWidth(.65)
c.circle(W/2,718,29,stroke=1,fill=0)
pearl(W/2,718,20)
center(626,'Луна',size=80)
center(572,'в знаках зодиака',size=43)
c.setStrokeColor(HexColor('#B9B6A4'));c.line(256,545,339,545)
c.showPage()

data=json.loads((ROOT/'assets/content.json').read_text())
for idx,item in enumerate(data,1):
    base(idx)
    c.bookmarkPage(f'sign{idx}');c.addOutlineEntry(item['title'],f'sign{idx}',level=0)
    text(57,699,item['title'],font='Display',size=40)
    c.setStrokeColor(HexColor('#A6C5D6'));c.setLineWidth(.8);c.line(58,676,117,676)
    top=650
    top=para(item['paragraphs'][0],58,top,W-116,'Display',23,28)-24
    for s in item['paragraphs'][1:-1]:
        top=para(s,58,top,W-122,'Body',12,19)-13
    top-=3
    c.setStrokeColor(HexColor('#A4C2D3'));c.setLineWidth(1.2)
    mother=item['paragraphs'][-1]
    end=para(mother,71,top,W-142,'Body',12,19)
    c.line(58,end+2,58,top-2)
    assert end>265, (item['title'],end)
    c.showPage()
c.save()
print(OUT)
