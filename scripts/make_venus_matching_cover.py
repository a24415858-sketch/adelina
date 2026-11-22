"""Replace only the cover with a full-length portrait and CT-style powder compact."""
from pathlib import Path
from io import BytesIO
import pymupdf as fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'documents/Venera_foto_v_fone.pdf'
OUT=ROOT/'documents/Venera_v_polny_rost.pdf'
BG=ROOT/'assets/venus-pearl-marble-background.jpg'
PORTRAIT=ROOT/'assets/venus-fullbody-matching-transparent.png'
for n,f in [('Display','CormorantGaramond.ttf'),('Body','Montserrat-Regular.ttf')]:
    pdfmetrics.registerFont(TTFont(n,str(ROOT/'assets'/f)))
W,H=595.276,841.89
buf=BytesIO(); c=canvas.Canvas(buf,pagesize=(W,H),pageCompression=1)
reader=ImageReader(str(BG)); iw,ih=reader.getSize(); s=max(W/iw,H/ih)
c.drawImage(reader,(W-iw*s)/2,(H-ih*s)/2,iw*s,ih*s)
c.saveState();c.setFillColor(HexColor('#F7F1E9'));c.setFillAlpha(.30);c.rect(0,0,W,H,fill=1,stroke=0);c.restoreState()
c.setFillColor(HexColor('#40302B'));c.setFont('Body',8);c.drawString(40,793,'VENUS  /  PERSONAL GUIDE')
def rule(x1,y,x2):
    c.setStrokeColor(HexColor('#AB958B'));c.setLineWidth(.65);c.line(x1,y,x2,y)
rule(40,776,W-40)
# Show the full silhouette, with the shoes and the mirror inside the page.
c.drawImage(str(PORTRAIT),18,45,width=278,height=688.96,mask='auto')
def center(t,x,y,size,font='Display'):
    c.setFillColor(HexColor('#40302B'));c.setFont(font,size);c.drawCentredString(x,y,t)
x=319;mid=(x+W-40)/2
center('ВЕНЕРА',mid,603,38);center('ЧЕМ ЦЕПЛЯЕТ',mid,570,25)
rule(x+14,548,W-54)
center('В знаках зодиака',mid,518,10,'Body')
center('Красота вашей',mid,467,19);center('индивидуальности',mid,443,19)
rule(x+14,391,W-54)
center('ПРИТЯЖЕНИЕ  ·  КРАСОТА',mid,367,8,'Body')
center('ИНДИВИДУАЛЬНОСТЬ',mid,351,8,'Body')
center('12 знаков зодиака',mid,252,18)
rule(mid-60,228,mid+60)
# A restrained editorial divider, without unsupported glyphs.
rule(mid-12,198,mid+12)
c.showPage();c.save();buf.seek(0)
with fitz.open(SOURCE) as src, fitz.open(stream=buf.read(),filetype='pdf') as cover:
    toc=src.get_toc(); meta=src.metadata
    src.delete_page(0);src.insert_pdf(cover,from_page=0,to_page=0,start_at=0)
    src.set_toc(toc);src.set_metadata(meta);src.save(OUT,garbage=4,deflate=True)
with fitz.open(SOURCE) as a,fitz.open(OUT) as b:
    assert len(a)==len(b)==13
    for i in range(1,13):
        assert a[i].get_pixmap().samples==b[i].get_pixmap().samples, i
        assert a[i].get_text()==b[i].get_text(), i
    assert a.get_toc()==b.get_toc()
    b[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save('/home/user/venus-matching-cover-check.png')
print('Saved',OUT,'— 13 pages; all 12 interior pages and contents unchanged.')
