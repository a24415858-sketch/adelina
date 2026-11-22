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
OUT = ROOT / 'documents/Venera_chem_ceptlyaet_brand.pdf'
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
    c.drawImage(im,x+(w-ww)/2,y+h-hh,ww,hh); c.restoreState()
def base(): fill(BG); c.rect(0,0,W,H,fill=1,stroke=0)

# Cover: editorial composition based on the user's own photo, not the old shell design.
base()
text('VENUS  /  PERSONAL GUIDE',38, H-52, 8.5,'Bold',ACCENT)
right('01',W-38,H-55,22,'Display',ACCENT)
line(38,H-67,W-38,H-67)
image_cover(photos[0],263,296,294,427)
text('Венера',38,660,62,'Display')
text('чем',40,606,38,'Display')
text('цепляет',40,568,38,'Display')
line(40,543,220,543)
text('В ЗНАКАХ',40,511,9,'Bold',ACCENT)
text('ЗОДИАКА',40,493,9,'Bold',ACCENT)
text('Красота вашей',40,407,19,'Display')
text('индивидуальности',40,385,19,'Display')
line(38,271,W-38,271)
image_cover(photos[2],38,63,161,181)
image_cover(photos[3],217,63,161,181)
image_cover(photos[6],396,63,161,181)
c.bookmarkPage('cover'); c.addOutlineEntry('Венера — чем цепляет','cover',0); c.showPage()

pairs=[(1,2),(3,4),(5,6),(7,1),(2,3),(4,7)]
for chunk in range(0,12,2):
    page=2+chunk//2; base()
    text('ВЕНЕРА  /  В ЗНАКАХ',38,H-48,8.5,'Bold',ACCENT)
    right(f'{page:02d}',W-38,H-52,23,'Display',ACCENT)
    line(38,H-64,W-38,H-64)
    text('Чем цепляет',38,H-110,37,'Display')
    line(38,H-127,W-38,H-127)
    y=H-158
    for n,s in enumerate(data[chunk:chunk+2]):
        text(s['title'],38,y,26,'Display')
        right(s['symbol'],W-40,y,18,'Body',ACCENT)
        y-=23
        text('«'+s['archetype']+'»',38,y,17,'Display',ACCENT)
        y-=24
        text('ЧЕМ ЦЕПЛЯЕТ',38,y,8,'Bold',ACCENT); y-=12
        for b in s['attraction']:
            fill(ACCENT); c.circle(41,y-5,1.7,fill=1,stroke=0)
            y=para(b,52,y,W-90)-6
        if n==0:
            y-=7; line(38,y,W-38,y); y-=30
        c.bookmarkPage('sign'+s['title']); c.addOutlineEntry(s['title'],'sign'+s['title'],1)
    assert y>250,(page,y)
    # Two portraits make a clean photographic footer, echoing the reference grid.
    i,j=pairs[chunk//2]
    image_cover(photos[i],38,48,253,178)
    image_cover(photos[j],304,48,253,178)
    c.showPage()
c.save()
with pymupdf.open(OUT) as pdf:
    assert len(pdf)==7
    extracted=''.join(''.join(p.get_text().split()) for p in pdf)
    for sign in data:
        for item in sign['attraction']:
            assert ''.join(item.split()) in extracted, (sign['title'],item)
    print(f'{OUT}: {len(pdf)} pages; all 36 descriptions retained')
