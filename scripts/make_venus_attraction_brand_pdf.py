"""Seven-page Venus guide with photographs from the supplied brand collage."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'documents/Venera_brand_novyi_dizain.pdf'
data = json.loads((ROOT / 'assets/venus-content.json').read_text())
# Crops are taken directly from the newly supplied collage, without regenerating faces.
collage = Image.open(ROOT / 'assets/venus-brand-reference.webp').convert('RGB')
photos = [collage.crop(box) for box in [
    (135, 30, 374, 390),     # sunglasses portrait, from the left panel
    (420, 0, 670, 310),      # reading
    (714, 0, 928, 310),      # astrology
    (990, 0, 1180, 310),     # working
    (421, 600, 670, 856),    # music
    (714, 600, 928, 856),    # studying
    (990, 600, 1180, 856),   # beauty
    (1240, 600, 1433, 856),  # career
]]
for name, path in [('Display',ROOT/'assets/CormorantGaramond.ttf'),('Body',Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')),('Bold',Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))]:
    pdfmetrics.registerFont(TTFont(name,str(path)))
W,H=595.276,841.89
BG, PAPER, INK, ACCENT, LINE = '#F2ECE8', '#FAF7F4', '#59463F', '#95796D', '#D8C8C0'
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('Венера — чем цепляет')
def fill(color): c.setFillColor(HexColor(color))
def line(x1,y1,x2,y2,color=LINE,width=.65):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width); c.line(x1,y1,x2,y2)
def text(s,x,y,size=10,font='Body',color=INK):
    fill(color); c.setFont(font,size); c.drawString(x,y,s)
def right(s,x,y,size=10,font='Body',color=INK):
    fill(color); c.setFont(font,size); c.drawRightString(x,y,s)
def para(s,x,y,width,size=10.4,leading=15.2):
    style=ParagraphStyle('body',fontName='Body',fontSize=size,leading=leading,textColor=HexColor(INK))
    p=Paragraph(escape(s),style); _,h=p.wrap(width,H); p.drawOn(c,x,y-h); return y-h

def image_cover(image,x,y,w,h):
    im=ImageReader(image); iw,ih=im.getSize(); scale=max(w/iw,h/ih); ww,hh=iw*scale,ih*scale
    c.saveState(); clip=c.beginPath(); clip.rect(x,y,w,h); c.clipPath(clip,stroke=0,fill=0)
    vertical = y+(h-hh)/2 if image is photos[0] and w < 280 else y+h-hh
    c.drawImage(im,x+(w-ww)/2,vertical,ww,hh); c.restoreState()
def base(): fill(BG); c.rect(0,0,W,H,fill=1,stroke=0)

# Cover: a full-height portrait and typography in the reference's magazine grid.
base()
fill(PAPER); c.rect(0,0,237,H,fill=1,stroke=0)
image_cover(photos[0],237,165,W-237,H-165)
text('VENUS',35,H-64,10,'Bold',ACCENT)
line(35,H-81,200,H-81)
text('Венера',35,616,54,'Display')
text('чем',35,565,37,'Display')
text('цепляет',35,526,37,'Display')
line(35,493,178,493)
text('В ЗНАКАХ',35,464,8.5,'Bold',ACCENT)
text('ЗОДИАКА',35,446,8.5,'Bold',ACCENT)
text('Красота',35,358,20,'Display')
text('вашей',35,334,20,'Display')
text('индивидуальности',35,310,18,'Display')
line(35,109,200,109)
text('PERSONAL GUIDE',35,82,8,'Bold',ACCENT)
# A short photo strip uses images from the new reference, without shells.
image_cover(photos[2],237,0,(W-237)/2,165)
image_cover(photos[6],237+(W-237)/2,0,(W-237)/2,165)
c.bookmarkPage('cover'); c.addOutlineEntry('Венера — чем цепляет','cover',0); c.showPage()

pairs=[(1,2),(3,4),(5,6),(7,0),(2,3),(4,7)]
for chunk in range(0,12,2):
    page=2+chunk//2; base()
    text('ВЕНЕРА  /  В ЗНАКАХ',26,H-37,8.5,'Bold',ACCENT)
    right(f'{page:02d}',W-26,H-40,22,'Display',ACCENT)
    line(26,H-51,W-26,H-51)
    gutter=12; margin=26; cw=(W-2*margin-gutter)/2
    for n,s in enumerate(data[chunk:chunk+2]):
        x=margin+n*(cw+gutter)
        fill(PAPER); c.rect(x,50,cw,734,fill=1,stroke=0)
        # Reference layout: photograph above the light editorial text panel.
        image_cover(photos[pairs[chunk//2][n]],x,491,cw,293)
        y=457
        # Scale only if the title needs a little more room.
        size=25
        while pdfmetrics.stringWidth(s['title'],'Display',size)>cw-30: size-=0.5
        fill(INK); c.setFont('Display',size); c.drawCentredString(x+cw/2,y,s['title'])
        y-=25
        fill(ACCENT); c.setFont('Display',17); c.drawCentredString(x+cw/2,y,'«'+s['archetype']+'»')
        y-=23
        line(x+26,y,x+cw-26,y)
        y-=28
        text('ЧЕМ ЦЕПЛЯЕТ',x+19,y,8,'Bold',ACCENT); y-=16
        for item in s['attraction']:
            fill(ACCENT); c.circle(x+21,y-5,1.7,fill=1,stroke=0)
            y=para(item,x+30,y,cw-49,size=10.2,leading=15.6)-9
        assert y>95,(page,s['title'],y)
        fill(ACCENT); c.setFont('Body',16); c.drawCentredString(x+cw/2,78,s['symbol'])
        c.bookmarkPage('sign'+s['title']); c.addOutlineEntry(s['title'],'sign'+s['title'],1)
    c.showPage()
c.save()
with pymupdf.open(OUT) as pdf:
    assert len(pdf)==7
    extracted=''.join(''.join(p.get_text().split()) for p in pdf)
    for sign in data:
        for item in sign['attraction']:
            assert ''.join(item.split()) in extracted, (sign['title'],item)
    print(f'{OUT}: {len(pdf)} pages; all 36 descriptions retained')
