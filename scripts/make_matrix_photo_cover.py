"""Place photo 1 from the user's collage on the existing Matrix guide cover."""
from pathlib import Path
from io import BytesIO
from PIL import Image,ImageOps
import pymupdf as fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
R=Path(__file__).resolve().parents[1]
SOURCE=R/'documents/Matrix_zhemchug_sirenevy.pdf'
OUT=R/'documents/Matrix_zhemchug_foto.pdf'
BG=R/'assets/matrix-white-pearls-background.jpg'
PHOTO=R/'assets/matrix-photo-reading.png'
W,H=595.276,841.89
pdfmetrics.registerFont(TTFont('Display',str(R/'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body',str(R/'assets/Montserrat-Regular.ttf')))
im=ImageOps.fit(Image.open(BG).convert('RGB'),(1190,1684),method=Image.Resampling.LANCZOS)
im=Image.blend(im,Image.new('RGB',im.size,(250,250,250)),.42)
b=BytesIO();c=canvas.Canvas(b,pagesize=(W,H),pageCompression=1)
c.drawImage(ImageReader(im),0,0,W,H)
INK=HexColor('#564B64');MUTED=HexColor('#756786');LINE=HexColor('#B5A9BD')
def center(t,x,y,size,font='Display',color=INK):
    c.setFillColor(color);c.setFont(font,size);c.drawCentredString(x,y,t)
def rule(x1,y,x2):
    c.setStrokeColor(LINE);c.setLineWidth(.65);c.line(x1,y,x2,y)
c.setFillColor(MUTED);c.setFont('Body',8);c.drawString(40,793,'МАТРИЦА СУДЬБЫ')
rule(40,776,W-40)
# Exact pixels of the selected photograph, blended at its lower edge only.
c.drawImage(str(PHOTO),291,318,width=261,height=382.5,mask='auto')
mid=159
center('Женские',mid,594,45);center('чакры',mid,547,45)
rule(94,521,224)
center('Свадхистана · Анахата · Аджна',W/2,275,11,'Body')
center('Как вывести энергии в плюс',W/2,244,13,'Body')
rule(W/2-63,221,W/2+63)
center('Три пространства внимания к себе.',W/2,183,10,'Body')
center('Желания, чувства и ясность — через небольшие ежедневные',W/2,164,10,'Body')
center('действия.',W/2,148,10,'Body')
center('СИМВОЛИЧЕСКИЙ ПРАКТИКУМ ДЛЯ САМОПОЗНАНИЯ',W/2,78,7.4,'Body',MUTED)
c.showPage();c.save();b.seek(0)
with fitz.open(SOURCE) as doc,fitz.open(stream=b.read(),filetype='pdf') as new:
    toc=doc.get_toc();meta=doc.metadata
    doc.delete_page(0);doc.insert_pdf(new,from_page=0,to_page=0,start_at=0)
    doc.set_toc(toc);doc.set_metadata(meta);doc.save(OUT,garbage=4,deflate=True)
with fitz.open(SOURCE) as original,fitz.open(OUT) as result:
    assert len(original)==len(result)==70 and original.get_toc()==result.get_toc()
    for i in range(1,70):
        assert original[i].get_text()==result[i].get_text()
        assert original[i].get_pixmap().samples==result[i].get_pixmap().samples
    normalize=lambda t:''.join(t.split())
    assert normalize(original[0].get_text())==normalize(result[0].get_text())
    result[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save('/home/user/matrix-photo-cover-check.png')
print('Saved',OUT,'— 70 pages, 69 interior pages unchanged, cover text retained')
