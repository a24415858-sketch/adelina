"""Restyle the supplied seven-page Venus attraction guide without changing its text."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'documents/Venera_chem_ceptlyaet_brand.pdf'
PHOTO = ROOT / 'assets/venus-brand-photo.png'
FLOWERS = ROOT / 'assets/venus-attraction-flowers-detail.png'
data = json.loads((ROOT / 'assets/venus-content.json').read_text())
pdfmetrics.registerFont(TTFont('Display', str(ROOT / 'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
W, H = 595.276, 841.89
BG, INK, ACCENT, LINE = '#F3EBE7', '#57443E', '#98796B', '#D2BDB2'
c = canvas.Canvas(str(OUT), pagesize=(W, H), pageCompression=1)
c.setTitle('Венера — чем цепляет')

def fill(color): c.setFillColor(HexColor(color))
def line(x1,y1,x2,y2,color=LINE,width=.6):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width); c.line(x1,y1,x2,y2)
def text(s,x,y,size=10,font='Body',color=INK):
    fill(color); c.setFont(font,size); c.drawString(x,y,s)
def right(s,x,y,size=10,font='Body',color=INK):
    fill(color); c.setFont(font,size); c.drawRightString(x,y,s)
def paragraph(s,x,y,width,size=10.5,leading=15):
    st=ParagraphStyle('attraction', fontName='Body',fontSize=size,leading=leading,textColor=HexColor(INK))
    p=Paragraph(escape(s), st); _,h=p.wrap(width,H); p.drawOn(c,x,y-h); return y-h

def image_cover(path,x,y,w,h):
    im=ImageReader(str(path)); iw,ih=im.getSize(); scale=max(w/iw,h/ih)
    ww,hh=iw*scale,ih*scale
    c.saveState(); p=c.beginPath(); p.rect(x,y,w,h); c.clipPath(p,stroke=0,fill=0)
    c.drawImage(im,x+(w-ww)/2,y+(h-hh)/2,ww,hh,mask='auto')
    c.restoreState()

def base():
    fill(BG); c.rect(0,0,W,H,fill=1,stroke=0)

def floral_bar(y=30):
    image_cover(FLOWERS, 40,y,W-80,156)

# Cover: quiet editorial grid with original sunglasses photograph and original flowers.
base()
text('VENUS  /  GUIDE', 42, H-56, 9, 'Bold', ACCENT)
right('01', W-43, H-60, 21, 'Display', ACCENT)
line(42,H-72,W-42,H-72)
image_cover(PHOTO, 287, 282, 266, 452)
text('Венера', 42, 635, 61, 'Display', INK)
text('чем', 44, 584, 37, 'Display', INK)
text('цепляет', 44, 546, 37, 'Display', INK)
line(44,520,235,520)
text('КРАСОТА', 44, 486, 9, 'Bold', ACCENT)
text('ПРИТЯЖЕНИЕ', 44, 466, 9, 'Bold', ACCENT)
text('МАГНЕТИЗМ', 44, 446, 9, 'Bold', ACCENT)
text('12 знаков зодиака',44,367,16,'Display',INK)
floral_bar(42)
c.bookmarkPage('cover'); c.addOutlineEntry('Венера — чем цепляет','cover',0)
c.showPage()

for chunk in range(0,12,2):
    page=2+chunk//2
    base()
    text('ВЕНЕРА  /  В ЗНАКАХ', 42, H-53, 8.5, 'Bold', ACCENT)
    right(f'{page:02d}', W-43, H-58, 23, 'Display', ACCENT)
    line(42,H-70,W-42,H-70)
    text('Чем цепляет',42,H-120,38,'Display',INK)
    line(42,H-137,W-42,H-137)
    y=H-170
    for n,s in enumerate(data[chunk:chunk+2]):
        text(s['title'],42,y,27,'Display',INK)
        right(s['symbol'],W-44,y,18,'Body',ACCENT)
        y-=24
        text('«'+s['archetype']+'»',42,y,17,'Display',ACCENT)
        y-=26
        text('ЧЕМ ЦЕПЛЯЕТ',42,y,8,'Bold',ACCENT)
        y-=12
        for b in s['attraction']:
            fill(ACCENT); c.circle(45,y-5,1.8,fill=1,stroke=0)
            y=paragraph(b,56,y,W-98)-6
        if n==0:
            y-=8; line(42,y,W-42,y); y-=33
        c.bookmarkPage('sign'+s['title']); c.addOutlineEntry(s['title'],'sign'+s['title'],1)
    assert y>215,(page,y)
    floral_bar(35)
    # A second appearance of the same photo, in the guide itself, beside the original flowers.
    if page==4:
        fill(BG); c.rect(39,34,117,158,fill=1,stroke=0)
        image_cover(PHOTO,40,35,115,156)
    c.showPage()
c.save()
with pymupdf.open(OUT) as pdf:
    assert len(pdf)==7
    all_text=''.join(''.join(p.get_text().split()) for p in pdf)
    for sign in data:
        for item in sign['attraction']:
            assert ''.join(item.split()) in all_text, (sign['title'],item)
    print(f'{OUT}: {len(pdf)} pages; all 36 descriptions retained')
