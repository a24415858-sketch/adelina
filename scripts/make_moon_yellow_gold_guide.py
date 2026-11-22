"""Restyle the user-supplied Moon guide while preserving its content and outline."""
from pathlib import Path
from io import BytesIO
import re
import pymupdf as fitz
from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

R=Path(__file__).resolve().parents[1]
SOURCE=R/'assets/moon-source-upload.pdf';BG=R/'assets/moon-marble-pearl-background.jpg'
OUT=R/'documents/Luna_zheltoe_zoloto.pdf'
W,H=595.276,841.89
# Preblend a uniform, translucent veil into the image. No white card is added.
im=ImageOps.fit(Image.open(BG).convert('RGB'),(1190,1684),method=Image.Resampling.LANCZOS,centering=(.5,.5))
def background(veil):
    data=BytesIO();Image.blend(im,Image.new('RGB',im.size,(249,245,239)),veil).save(data,format='JPEG',quality=90,optimize=True);return data.getvalue()
inside=background(.76);cover_bg=background(.22)

pdfmetrics.registerFont(TTFont('Display',str(R/'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body',str(R/'assets/Montserrat-Regular.ttf')))
cbuf=BytesIO();c=canvas.Canvas(cbuf,pagesize=(W,H),pageCompression=1)
from reportlab.lib.utils import ImageReader
c.drawImage(ImageReader(BytesIO(cover_bg)),0,0,W,H)
c.setFillColor(HexColor('#A67C00'));c.setFont('Body',8);c.drawString(40,793,'LUNA  /  PERSONAL GUIDE')
c.setStrokeColor(HexColor('#C7A328'));c.setLineWidth(.65);c.line(40,776,W-40,776)
c.setFont('Display',69);c.drawCentredString(W/2,590,'ЛУНА')
c.setFont('Display',29);c.drawCentredString(W/2,552,'полный гайд')
c.line(W/2-62,525,W/2+62,525)
c.setFont('Body',9);c.drawCentredString(W/2,495,'ЭМОЦИИ  ·  КОМФОРТ  ·  ДОМ')
c.showPage();c.save();cbuf.seek(0)

# Only the original page-filling image and colored box backgrounds are removed.
# Text, vector ornaments, positions, page numbers and font data stay intact.
imgpat=re.compile(rb'q\s+595\.276 0 0 841\.89 0 0 cm\s+/FormXob\.[^\s]+ Do\s+Q\s*')
boxpat=re.compile(rb'\.917647 \.945098 \.972549 rg\s+\.72549 \.8 \.866667 RG\s+\.7 w\s+n\s+.*?\bh\s+B\*\s*',re.S)
colors={
 b'.2 .278431 .368627':b'.612 .463 0',
 b'.290196 .482353 .65098':b'.659 .494 0',
 b'.576471 .647059 .721569':b'.780 .639 .157',
 b'.72549 .8 .866667':b'.780 .639 .157',
}
boxes=0
with fitz.open(SOURCE) as doc,fitz.open(stream=cbuf.read(),filetype='pdf') as cover:
    assert len(doc)==111
    toc=doc.get_toc();meta=doc.metadata
    for page in list(doc)[1:]:
        ids=page.get_contents();assert len(ids)==1
        xref=ids[0];stream=doc.xref_stream(xref)
        stream,n=imgpat.subn(b'',stream,count=1);assert n==1,(page.number,n)
        stream,n=boxpat.subn(b'',stream);boxes+=n
        for old,new in colors.items():stream=stream.replace(old,new)
        # Give the existing layout more room and slightly larger type without
        # reflowing or altering any words; keep the page number in place.
        number=re.search(rb'\.659 \.494 0 rg\s+BT 1 0 0 1 [^\n]* 24 Tm [^\n]* ET\s*',stream)
        assert number, page.number
        page_number=number.group(0);stream=stream[:number.start()]+stream[number.end():]
        stream=page_number+b'\nq\n1.05 0 0 1.10 -14.882 -84.189 cm\n'+stream+b'\nQ\n'
        doc.update_stream(xref,stream)
        page.insert_image(page.rect,stream=inside,overlay=False)
    doc.delete_page(0);doc.insert_pdf(cover,from_page=0,to_page=0,start_at=0)
    doc.set_toc(toc);doc.set_metadata(meta);doc.save(OUT,garbage=4,deflate=True)
with fitz.open(SOURCE) as a,fitz.open(OUT) as b:
    assert len(a)==len(b)==111 and a.get_toc()==b.get_toc()
    for i in range(1,len(b)):
        assert a[i].get_text()==b[i].get_text(),f'text differs page {i+1}'
        assert b[i].get_text().strip(),f'empty page {i+1}'
        for word in b[i].get_text('words'):
            assert word[0]>=0 and word[1]>=0 and word[2]<=W+1 and word[3]<=H+1,(i+1,word)
    for i in [0,1,2,3,19,31,40,60,100,110]:
        b[i].get_pixmap(matrix=fitz.Matrix(1,1)).save(f'/home/user/moon-yellow-gold-{i+1}.png')
print(f'{OUT}: 111 pages; all interior text, order, outline preserved; {boxes} colored boxes removed')
