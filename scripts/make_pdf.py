"""Build the blue mother-of-pearl zodiac booklet. Run from any directory."""
from pathlib import Path
import json, math
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

def background():
    w,h=1240,1754
    y,x=np.mgrid[0:h,0:w]; x=x/w; y=y/h
    flow=np.sin(8*x+5*y+1.7*np.sin(5*y-3*x))
    sheen=np.exp(-((flow-.65)/.22)**2)
    edge=np.clip((abs(x-.5)*2)**2+.25*abs(y-.5)*2,0,1)
    rgb=np.zeros((h,w,3))+np.array([245.,250.,251.])
    rgb+=edge[:,:,None]*np.array([-37.,-18.,-7.])
    rgb+=sheen[:,:,None]*np.array([9.,6.,4.])*edge[:,:,None]
    lavender=(.5+.5*np.sin(11*y+7*x))*edge
    rgb+=lavender[:,:,None]*np.array([7.,-3.,5.])
    return ImageReader(Image.fromarray(np.uint8(np.clip(rgb,0,255))))

BG=background()
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

def shell(cx,cy,r,rotation=0):
    # A scallop with individually shaded nacre ribs and a scalloped rim.
    c.saveState();c.translate(cx,cy);c.rotate(rotation)
    n=13
    for rib in range(n):
        for j in range(12):
            t0=(rib+j/12)/n; t1=(rib+(j+1)/12)/n
            a0=math.radians(18+144*t0); a1=math.radians(18+144*t1)
            def radius(t):
                return r*(.97+.03*math.sin(math.pi*((t*n)%1)))
            rr0,rr1=radius(t0),radius(t1)
            light=math.sin(math.pi*(j+.5)/12)
            c.setFillColor(Color(.84+.13*light,.91+.075*light,.95+.045*light))
            p=c.beginPath();p.moveTo(0,0)
            p.lineTo(rr0*math.cos(a0),rr0*math.sin(a0))
            p.lineTo(rr1*math.cos(a1),rr1*math.sin(a1));p.close()
            c.drawPath(p,fill=1,stroke=0)
    c.setStrokeColor(HexColor('#CADFE8'));c.setLineWidth(.25)
    for i in range(n+1):
        a=math.radians(18+144*i/n)
        p=c.beginPath();p.moveTo(0,0);p.curveTo(r*.22*math.cos(a),r*.38*math.sin(a),r*.7*math.cos(a),r*.74*math.sin(a),r*.97*math.cos(a),r*.97*math.sin(a));c.drawPath(p)
    c.setFillColor(HexColor('#E1EDF2'));c.setStrokeColor(HexColor('#CADFE8'))
    p=c.beginPath();p.moveTo(-r*.19,-r*.025);p.lineTo(0,r*.10);p.lineTo(r*.19,-r*.025);p.close();c.drawPath(p,fill=1,stroke=1)
    c.restoreState()

def base(num=None):
    c.drawImage(BG,0,0,W,H)
    c.setStrokeColor(Color(1,1,1,alpha=.8));c.setLineWidth(.7)
    c.roundRect(23,23,W-46,H-46,9,stroke=1,fill=0)
    if num:
        text(51,H-57,'Л У Н А  В  З Н А К А Х  З О Д И А К А',size=8,color=MUTED)
        c.setStrokeColor(HexColor('#BDD2DE'));c.line(51,67,W-51,67)
        text(51,46,'Лунные знаки',size=8,color=MUTED)

def para(s,x,top,width,font,size,leading,color=INK):
    # Typography only: spaced hyphens become em dashes; wording is unchanged.
    s=s.replace(' - ',' — ')
    p=Paragraph(s,ParagraphStyle('p',fontName=font,fontSize=size,leading=leading,textColor=color))
    _,h=p.wrap(width,700);p.drawOn(c,x,top-h)
    return top-h

base()
# Moon medallion, fine orbital lines and a nacre pearl.
c.setStrokeColor(HexColor('#AEC9D9'));c.setLineWidth(.65)
c.circle(W/2,637,66,stroke=1,fill=0);c.circle(W/2,637,79,stroke=1,fill=0)
pearl(W/2,637,49)
for x,y,r in [(W/2+76,659,3),(W/2-62,589,2),(W/2+7,716,2)]:pearl(x,y,r)
center(496,'Луна',size=78)
center(441,'в знаках зодиака',size=43)
c.setStrokeColor(HexColor('#9DBECD'));c.line(254,409,341,409)
shell(W/2,136,158,-7)
pearl(409,159,17);pearl(434,141,8);pearl(194,152,6)
center(59,'ЧУВСТВА   /   ПРИВЫЧКИ   /   ОБРАЗ МАМЫ',font='Body',size=7.5,color=MUTED)
c.showPage()

data=json.loads((ROOT/'assets/content.json').read_text())
for idx,item in enumerate(data,1):
    base(idx)
    c.bookmarkPage(f'sign{idx}');c.addOutlineEntry(item['title'],f'sign{idx}',level=0)
    text(51,650,item['title'],font='Display',size=40)
    c.setStrokeColor(HexColor('#A6C5D6'));c.setLineWidth(.8);c.line(52,626,111,626)
    top=599
    top=para(item['paragraphs'][0],52,top,W-104,'Display',23,28)-24
    for s in item['paragraphs'][1:-1]:
        top=para(s,52,top,W-113,'Body',12,19)-13
    top-=3
    c.setStrokeColor(HexColor('#A4C2D3'));c.setLineWidth(1.2)
    mother=item['paragraphs'][-1]
    end=para(mother,65,top,W-130,'Body',12,19)
    c.line(52,end+2,52,top-2)
    assert end>197, (item['title'],end)
    shell(W-125,96,78,13)
    pearl(W-60,105,9);pearl(W-76,92,4)
    c.showPage()
c.save()
print(OUT)
