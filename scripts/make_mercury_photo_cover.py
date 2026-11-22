"""Add the selected astrology photo to the Mercury cover, leaving other pages unchanged."""
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
SOURCE=R/'documents/Merkuriy_polny_gayd.pdf'
OUT=R/'documents/Merkuriy_s_foto.pdf'
BG=R/'assets/mercury-sky-interior.jpg'
PHOTO=R/'assets/mercury-reading-photo.png'
W,H=595.276,841.89
pdfmetrics.registerFont(TTFont('Display',str(R/'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body',str(R/'assets/Montserrat-Regular.ttf')))
im=ImageOps.fit(Image.open(BG).convert('RGB'),(1190,1684),method=Image.Resampling.LANCZOS)
im=Image.blend(im,Image.new('RGB',im.size,(247,250,252)),.45)
b=BytesIO();c=canvas.Canvas(b,pagesize=(W,H),pageCompression=1)
c.drawImage(ImageReader(im),0,0,W,H)
ink=HexColor('#294C65');accent=HexColor('#446C86');line=HexColor('#91A6B5')
def center(s,x,y,size,font='Display',col=ink):
    c.setFillColor(col);c.setFont(font,size);c.drawCentredString(x,y,s)
def rule(x1,y,x2):c.setStrokeColor(line);c.setLineWidth(.55);c.line(x1,y,x2,y)
c.setFillColor(accent);c.setFont('Body',8);c.drawString(42,797,'MERCURY  /  PERSONAL GUIDE');rule(42,781,W-42)
# The original photo 1 from the provided collage, without a rectangular frame.
c.drawImage(str(PHOTO),25,299,260,381.05,mask='auto')
mid=446
center('МЕРКУРИЙ',mid,584,34);center('полный гайд',mid,550,24)
rule(mid-70,525,mid+70)
center('МЫШЛЕНИЕ',mid,493,9,'Body',accent)
center('ОБЩЕНИЕ  ·  ОБУЧЕНИЕ',mid,473,9,'Body',accent)
c.showPage();c.save();b.seek(0)
with fitz.open(SOURCE) as old,fitz.open(stream=b.read(),filetype='pdf') as new:
    toc=old.get_toc();metadata=old.metadata
    old.delete_page(0);old.insert_pdf(new,from_page=0,to_page=0,start_at=0)
    old.set_toc(toc);old.set_metadata(metadata);old.save(OUT,garbage=4,deflate=True)
with fitz.open(SOURCE) as a,fitz.open(OUT) as b:
    assert len(a)==len(b)==111 and a.get_toc()==b.get_toc()
    for i in range(1,len(a)):
        assert a[i].get_text()==b[i].get_text(),i+1
        assert a[i].get_pixmap().samples==b[i].get_pixmap().samples,i+1
    # Check that every title word from the original cover is still on the new one.
    for t in ['МЕРКУРИЙ','полный гайд','МЫШЛЕНИЕ','ОБЩЕНИЕ','ОБУЧЕНИЕ']:
        assert t in b[0].get_text(),t
    b[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save('/home/user/mercury-new-cover-check.png')
print('Saved',OUT,'— cover updated; all 110 interior pages unchanged')
