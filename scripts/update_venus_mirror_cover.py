"""Swap only the magazine's cover for the mirror photograph from the supplied collage."""
from pathlib import Path
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'documents/Venera_zhurnal_retush.pdf'
OUT=ROOT/'documents/Venera_zhurnal_zerkalo.pdf'
PREVIEW=ROOT/'documents/Venera_oblozhka_zerkalo.png'
PHOTO=ROOT/'assets/venus-cover-mirror.png'
for name,path in [('Display',ROOT/'assets/CormorantGaramond.ttf'),('Body',Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')),('Bold',Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))]:
    pdfmetrics.registerFont(TTFont(name,str(path)))
W,H=595.276,841.89
buf=BytesIO(); c=canvas.Canvas(buf,pagesize=(W,H))
c.setFillColor(HexColor('#F2EBE6')); c.rect(0,0,W,H,stroke=0,fill=1)
c.setFillColor(HexColor('#98796D')); c.setFont('Bold',8); c.drawString(42,789,'VENUS  /  PERSONAL GUIDE')
c.setStrokeColor(HexColor('#D7C6BC')); c.setLineWidth(.6); c.line(42,770,W-42,770)
# Keep the original crop's full composition and aspect ratio: mirror and white shirt visible.
image_width=257; image_height=image_width*256/252
c.drawImage(str(PHOTO),42,390,image_width,image_height)
x=326
c.setFillColor(HexColor('#59463E')); c.setFont('Display',42); c.drawString(x,611,'Венера')
c.setFont('Display',30); c.drawString(x,569,'чем'); c.drawString(x,536,'цепляет')
c.setStrokeColor(HexColor('#D7C6BC')); c.line(x,511,W-42,511)
c.setFillColor(HexColor('#98796D')); c.setFont('Body',10); c.drawString(x,480,'В знаках зодиака')
c.setFillColor(HexColor('#59463E')); c.setFont('Display',18); c.drawString(x,429,'Красота вашей'); c.drawString(x,406,'индивидуальности')
c.setStrokeColor(HexColor('#D7C6BC')); c.line(42,343,W-42,343)
c.setFillColor(HexColor('#98796D')); c.setFont('Bold',8); c.drawString(42,309,'ПРИТЯЖЕНИЕ  ·  КРАСОТА  ·  ИНДИВИДУАЛЬНОСТЬ')
c.setFont('Display',19); c.drawString(42,199,'12 знаков зодиака')
center=(W-42); p=c.beginPath(); p.moveTo(center,215); p.lineTo(center+2,207); p.lineTo(center+8,205); p.lineTo(center+2,203); p.lineTo(center,195); p.lineTo(center-2,203); p.lineTo(center-8,205); p.lineTo(center-2,207); p.close(); c.drawPath(p,stroke=0,fill=1)
c.showPage(); c.save(); buf.seek(0)
with pymupdf.open(SOURCE) as original, pymupdf.open(stream=buf.read(),filetype='pdf') as cover, pymupdf.open() as result:
    toc=original.get_toc(); result.insert_pdf(cover); result.insert_pdf(original,from_page=1); result.set_toc(toc); result.set_metadata(original.metadata)
    assert len(result)==len(original)==13
    result.save(OUT,garbage=4,deflate=True)
with pymupdf.open(OUT) as doc:
    doc[0].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False).save(PREVIEW)
print('Cover replaced:',OUT)
