"""Put the selected 02 portrait and zodiac wheel on the Moon guide cover."""
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
SOURCE=R/'documents/Luna_mramor_i_zhemchug.pdf'
PHOTO=R/'assets/moon-photo02-transparent.png'
BG=R/'assets/moon-marble-pearl-background.jpg'
OUT=R/'documents/Luna_mramor_foto_02.pdf'
W,H=595.276,841.89
pdfmetrics.registerFont(TTFont('Display',str(R/'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body',str(R/'assets/Montserrat-Regular.ttf')))
im=ImageOps.fit(Image.open(BG).convert('RGB'),(1190,1684),method=Image.Resampling.LANCZOS,centering=(.5,.5))
im=Image.blend(im,Image.new('RGB',im.size,(249,245,239)),.22)
b=BytesIO();c=canvas.Canvas(b,pagesize=(W,H),pageCompression=1)
c.drawImage(ImageReader(im),0,0,W,H)
ink=HexColor('#40302B');line=HexColor('#AB958B')
c.setFillColor(ink);c.setFont('Body',8);c.drawString(40,793,'LUNA  /  PERSONAL GUIDE')
c.setStrokeColor(line);c.setLineWidth(.65);c.line(40,776,W-40,776)
# The figure and zodiac motif come directly from photo 02, without a photo frame.
c.drawImage(str(PHOTO),0,342,width=333,height=275.3,mask='auto')
mid=450
c.setFillColor(ink);c.setFont('Display',48);c.drawCentredString(mid,591,'ЛУНА')
c.setFont('Display',24);c.drawCentredString(mid,556,'полный гайд')
c.setStrokeColor(line);c.line(mid-67,531,mid+67,531)
c.setFont('Body',8);c.drawCentredString(mid,502,'ЭМОЦИИ  ·  КОМФОРТ')
c.drawCentredString(mid,486,'ДОМ')
c.showPage();c.save();b.seek(0)
with fitz.open(SOURCE) as d,fitz.open(stream=b.read(),filetype='pdf') as cover:
    toc=d.get_toc();meta=d.metadata
    d.delete_page(0);d.insert_pdf(cover,from_page=0,to_page=0,start_at=0)
    d.set_toc(toc);d.set_metadata(meta);d.save(OUT,garbage=4,deflate=True)
with fitz.open(SOURCE) as old,fitz.open(OUT) as new:
    assert len(old)==len(new)==111 and old.get_toc()==new.get_toc()
    for i in range(1,111):
        assert old[i].get_text()==new[i].get_text(),i+1
        assert old[i].get_pixmap().samples==new[i].get_pixmap().samples,i+1
    for item in ['ЛУНА','полный гайд','ЭМОЦИИ','КОМФОРТ','ДОМ']:
        assert item in new[0].get_text()
    new[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save('/home/user/moon-photo02-cover.png')
print('Saved',OUT,'— 111 pages; all interior pages and outline unchanged')
