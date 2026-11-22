"""Apply the supplied white-pearl design to the 70-page Matrix workbook."""
from pathlib import Path
from io import BytesIO
import re
import numpy as np
from PIL import Image,ImageOps
import pymupdf as fitz

R=Path(__file__).resolve().parents[1]
SOURCE=R/'assets/matrix-source-upload.pdf';BG=R/'assets/matrix-white-pearls-background.jpg'
OUT=R/'documents/Matrix_bely_zhemchug.pdf'
W,H=595.276,841.89
# The pale veil is page-wide, so there are no opaque white cards.
img=ImageOps.fit(Image.open(BG).convert('RGB'),(1190,1684),method=Image.Resampling.LANCZOS)
def backdrop(opacity):
    b=BytesIO();Image.blend(img,Image.new('RGB',img.size,(250,250,250)),opacity).save(b,'JPEG',quality=90,optimize=True);return b.getvalue()
inner=backdrop(.80);cover=backdrop(.42)

# Retain every number and line of the source matrix, but remove its flat pink
# rectangular ground and recolor its strokes to fit the pearl palette.
with fitz.open(SOURCE) as doc:
    xref=doc[1].get_images(full=True)[0][0]
    pix=fitz.Pixmap(doc,xref); raw=Image.open(BytesIO(pix.tobytes('png'))).convert('RGB')
array=np.asarray(raw,dtype=np.int16)
bg=np.array([252,247,248],dtype=np.int16)
delta=np.abs(array-bg).max(axis=2)
a=np.clip((delta.astype(np.float32)-2)*255/150,0,255).astype('uint8')
rgba=np.empty((array.shape[0],array.shape[1],4),dtype=np.uint8);rgba[:,:,:3]=[60,80,96];rgba[:,:,3]=a
matrix=Image.fromarray(rgba,'RGBA');b=BytesIO();matrix.save(b,'PNG');matrix_data=b.getvalue()

# Remove only the old solid backgrounds and large pink circle/motif, leaving
# the PDF's text, structure, numbers, page layout and vector content untouched.
basepat=re.compile(rb'\.988235 \.968627 \.972549 rg\s+n 0 0 595\.276 841\.89 re f\*\s+\.941176 \.886275 \.921569 rg\s+n\s+.*?f\*\s+q\s+\.909804 \.839216 \.882353 RG\s+.*?\nQ\s*',re.S)
coverpat=re.compile(rb'\.937255 \.882353 \.913725 rg\s+n 0 0 595\.276 841\.89 re f\*\s+q\s+\.788235 \.654902 \.72549 RG\s+.*?\nQ\s*',re.S)
matrixpat=re.compile(rb'q\s+495 0 0 495 50 168 cm\s+/FormXob\.[^\s]+ Do\s+Q\s*')
colors={
 b'.313725 .231373 .298039':b'.204 .290 .349',  # main text: soft slate blue
 b'.509804 .396078 .470588':b'.310 .400 .459',  # small captions
 b'.65098 .431373 .529412':b'.365 .475 .545',  # highlights
 b'.87451 .784314 .835294':b'.671 .733 .765',  # hairline rules
 b'.462745 .34902 .427451':b'.204 .290 .349',
 b'.384314 .258824 .341176':b'.204 .290 .349',
}
with fitz.open(SOURCE) as doc:
    assert len(doc)==70
    toc=doc.get_toc();meta=doc.metadata
    for i,page in enumerate(doc):
        ids=page.get_contents();assert len(ids)==1
        xref=ids[0];stream=doc.xref_stream(xref)
        stream,n=(coverpat if i==0 else basepat).subn(b'',stream,count=1)
        assert n==1,(i+1,'background removal failed')
        if i==1:
            stream,n=matrixpat.subn(b'',stream,count=1);assert n==1
        for old,new in colors.items():stream=stream.replace(old,new)
        doc.update_stream(xref,stream)
        page.insert_image(page.rect,stream=cover if i==0 else inner,overlay=False)
        if i==1:
            page.insert_image(fitz.Rect(50,H-(168+495),545,H-168),stream=matrix_data,overlay=True)
    doc.set_toc(toc);doc.set_metadata(meta)
    doc.save(OUT,garbage=4,deflate=True)
with fitz.open(SOURCE) as a,fitz.open(OUT) as b:
    assert len(a)==len(b)==70 and a.get_toc()==b.get_toc()
    for i in range(70):
        assert a[i].get_text()==b[i].get_text(),f'text differs on page {i+1}'
        assert b[i].get_text().strip(),f'empty page {i+1}'
        for word in b[i].get_text('words'):
            assert word[0]>=0 and word[1]>=0 and word[2]<=W+1 and word[3]<=H+1,(i+1,word)
    for i in [0,1,2,3,10,23,24,45,65,66,69]:
        b[i].get_pixmap(matrix=fitz.Matrix(1,1)).save(f'/home/user/matrix-pearls-{i+1}.png')
print(f'{OUT}: 70 pages; text, page order, outline and matrix figures preserved')
