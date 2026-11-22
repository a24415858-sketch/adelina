"""Use the original integrated portrait and typography, with portrait on the right."""
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
OUT=ROOT/'documents/Venera_vetochki_sleva.pdf'
BG=ROOT/'assets/venus-pearl-marble-background.jpg'
PORTRAIT=ROOT/'assets/venus-cover-transparent.png'
for n,f in [('Display','CormorantGaramond.ttf'),('Body','Montserrat-Regular.ttf')]:
    pdfmetrics.registerFont(TTFont(n,str(ROOT/'assets'/f)))
W,H=595.276,841.89
buf=BytesIO();c=canvas.Canvas(buf,pagesize=(W,H),pageCompression=1)
reader=ImageReader(str(BG));iw,ih=reader.getSize();s=max(W/iw,H/ih)
c.drawImage(reader,(W-iw*s)/2,(H-ih*s)/2,iw*s,ih*s)
c.saveState();c.setFillColor(HexColor('#F7F1E9'));c.setFillAlpha(.30);c.rect(0,0,W,H,fill=1,stroke=0);c.restoreState()
c.setFillColor(HexColor('#40302B'));c.setFont('Body',8);c.drawString(40,793,'VENUS  /  PERSONAL GUIDE')
def rule(x1,y,x2):
    c.setStrokeColor(HexColor('#AB958B'));c.setLineWidth(.65);c.line(x1,y,x2,y)
def center(t,x,y,size,font='Display'):
    c.setFillColor(HexColor('#40302B'));c.setFont(font,size);c.drawCentredString(x,y,t)
def star(x,y,sz=4):
    p=c.beginPath();p.moveTo(x,y+sz*2);p.curveTo(x+sz*.15,y+sz*.3,x+sz*.3,y+sz*.15,x+sz*2,y)
    p.curveTo(x+sz*.3,y-sz*.15,x+sz*.15,y-sz*.3,x,y-sz*2)
    p.curveTo(x-sz*.15,y-sz*.3,x-sz*.3,y-sz*.15,x-sz*2,y)
    p.curveTo(x-sz*.3,y+sz*.15,x-sz*.15,y+sz*.3,x,y+sz*2)
    c.setFillColor(HexColor('#654C42'));c.drawPath(p,fill=1,stroke=0)
rule(40,776,W-40)
# Move the exact original cutout, without mirroring or changing her face.
c.drawImage(str(PORTRAIT),W-18-280,247,280,424,mask='auto')
x=40;width=W-40-319;mid=x+width/2
center('ВЕНЕРА',mid,603,38);center('ЧЕМ ЦЕПЛЯЕТ',mid,570,25)
rule(x+14,548,x+width-14)
center('В знаках зодиака',mid,518,10,'Body')
center('Красота вашей',mid,467,19);center('индивидуальности',mid,443,19)
rule(x+14,391,x+width-14)
center('ПРИТЯЖЕНИЕ  ·  КРАСОТА',mid,367,8,'Body')
center('ИНДИВИДУАЛЬНОСТЬ',mid,351,8,'Body')
center('12 знаков зодиака',W/2,219,18)
rule(W/2-60,192,W/2+60);star(W/2,154)
c.showPage();c.save();buf.seek(0)
with fitz.open(SOURCE) as src,fitz.open(stream=buf.read(),filetype='pdf') as cover:
    toc=src.get_toc();metadata=src.metadata
    src.delete_page(0);src.insert_pdf(cover,from_page=0,to_page=0,start_at=0)
    src.set_toc(toc);src.set_metadata(metadata);src.save(OUT,garbage=4,deflate=True)
with fitz.open(SOURCE) as original,fitz.open(OUT) as result:
    assert len(original)==len(result)==13
    assert original.get_toc()==result.get_toc()
    for i in range(1,13):
        assert original[i].get_pixmap().samples==result[i].get_pixmap().samples
        assert original[i].get_text()==result[i].get_text()
    result[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save('/home/user/venus-branches-left-check.png')
print('Saved:',OUT,'; all interior pages and outline unchanged.')
