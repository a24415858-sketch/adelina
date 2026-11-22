"""Restyle only the Venus cover to echo the user's reference collage."""
from pathlib import Path
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import pymupdf
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'documents/Venera_zhurnal_zerkalo.pdf'
OUT=ROOT/'documents/Venera_oblozhka_referens.pdf'
PREVIEW=ROOT/'documents/Venera_referens_oblozhka.png'
PHOTO=ROOT/'assets/venus-cover-mirror-enhanced.png'
for name,path in [('Display',ROOT/'assets/CormorantGaramond.ttf'),('Sans',ROOT/'assets/Montserrat-Regular.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(path)))
W,H=595.276,841.89
BG='#EFE9E4'; INK='#785B51'; LINE='#CDB9AE'
buf=BytesIO(); c=canvas.Canvas(buf,pagesize=(W,H))
c.setFillColor(HexColor(BG)); c.rect(0,0,W,H,stroke=0,fill=1)
c.setFillColor(HexColor(INK)); c.setFont('Sans',8); c.drawString(40,793,'VENUS  /  PERSONAL GUIDE')
c.setStrokeColor(HexColor(LINE)); c.setLineWidth(.6); c.line(40,776,W-40,776)
# The photograph stays on the left, without cropping away the mirror or shirt.
photo_w=257; photo_h=photo_w*256/252
c.drawImage(str(PHOTO),40,403,photo_w,photo_h)
x=319; width=W-40-x; mid=x+width/2
c.setFillColor(HexColor(INK)); c.setFont('Display',38); c.drawCentredString(mid,603,'ВЕНЕРА')
c.setFont('Display',25); c.drawCentredString(mid,570,'ЧЕМ ЦЕПЛЯЕТ')
c.setStrokeColor(HexColor(LINE)); c.line(x+14,548,W-54,548)
c.setFont('Sans',10); c.drawCentredString(mid,518,'В знаках зодиака')
c.setFont('Display',19); c.drawCentredString(mid,467,'Красота вашей')
c.drawCentredString(mid,443,'индивидуальности')
c.line(40,361,W-40,361)
c.setFont('Sans',8); c.drawCentredString(W/2,329,'ПРИТЯЖЕНИЕ  ·  КРАСОТА  ·  ИНДИВИДУАЛЬНОСТЬ')
c.setFont('Display',18); c.drawCentredString(W/2,219,'12 знаков зодиака')
c.line(W/2-60,192,W/2+60,192)
p=c.beginPath();x=W/2;y=154
p.moveTo(x,y+9);p.lineTo(x+2,y+2);p.lineTo(x+9,y);p.lineTo(x+2,y-2);p.lineTo(x,y-9);p.lineTo(x-2,y-2);p.lineTo(x-9,y);p.lineTo(x-2,y+2);p.close();c.drawPath(p,stroke=0,fill=1)
c.showPage();c.save();buf.seek(0)
with pymupdf.open(SOURCE) as original, pymupdf.open(stream=buf.read(),filetype='pdf') as cover, pymupdf.open() as result:
    toc=original.get_toc();result.insert_pdf(cover);result.insert_pdf(original,from_page=1);result.set_toc(toc);result.set_metadata(original.metadata)
    assert len(result)==len(original)==13
    result.save(OUT,garbage=4,deflate=True)
with pymupdf.open(OUT) as doc:doc[0].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False).save(PREVIEW)
print('Saved',OUT)
