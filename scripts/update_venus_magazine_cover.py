"""Replace only the cover of the Venus magazine with the left-hand shirt portrait."""
from pathlib import Path
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'documents/Venera_zhurnal.pdf'
OUT=ROOT/'documents/Venera_zhurnal_novaya_oblozhka.pdf'
PREVIEW=ROOT/'documents/Venera_novaya_oblozhka.png'
PHOTO=ROOT/'assets/venus-cover-shirt-clean.png'
pdfmetrics.registerFont(TTFont('Display',str(ROOT/'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
W,H=595.276,841.89
buf=BytesIO(); c=canvas.Canvas(buf,pagesize=(W,H))
c.setFillColor(HexColor('#F2EBE6')); c.rect(0,0,W,H,stroke=0,fill=1)
# Preserve the crop's proportions and show the entire white shirt, as in the reference.
photo_width=375/856*H
c.drawImage(str(PHOTO),0,0,photo_width,H)
x=photo_width+24
c.setFillColor(HexColor('#98796D')); c.setFont('Bold',8); c.drawString(x,770,'VENUS  /  GUIDE')
c.setStrokeColor(HexColor('#D7C6BC')); c.setLineWidth(.6); c.line(x,753,W-25,753)
c.setFillColor(HexColor('#59463E')); c.setFont('Display',40); c.drawString(x,632,'Венера')
c.setFont('Display',29); c.drawString(x,590,'чем')
c.drawString(x,558,'цепляет')
c.setStrokeColor(HexColor('#D7C6BC')); c.line(x,532,W-32,532)
c.setFillColor(HexColor('#98796D')); c.setFont('Body',10); c.drawString(x,497,'В знаках зодиака')
c.setFillColor(HexColor('#59463E')); c.setFont('Display',18); c.drawString(x,367,'Красота вашей')
c.drawString(x,344,'индивидуальности')
c.setFillColor(HexColor('#98796D'))
center=(x+W-25)/2
p=c.beginPath(); p.moveTo(center,133); p.lineTo(center+2,125); p.lineTo(center+8,123); p.lineTo(center+2,121); p.lineTo(center,113); p.lineTo(center-2,121); p.lineTo(center-8,123); p.lineTo(center-2,125); p.close()
c.drawPath(p,stroke=0,fill=1)
c.setStrokeColor(HexColor('#D7C6BC')); c.line(x,102,W-25,102)
c.showPage(); c.save(); buf.seek(0)
with pymupdf.open(SOURCE) as original, pymupdf.open(stream=buf.read(),filetype='pdf') as cover, pymupdf.open() as result:
    toc=original.get_toc()
    result.insert_pdf(cover); result.insert_pdf(original,from_page=1)
    result.set_toc(toc)
    result.set_metadata(original.metadata)
    assert len(result)==len(original)==13
    result.save(OUT,garbage=4,deflate=True)
with pymupdf.open(OUT) as doc:
    doc[0].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False).save(PREVIEW)
print('Updated only the cover:',OUT)
