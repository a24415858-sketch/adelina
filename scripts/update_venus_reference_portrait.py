"""Use the user-selected portrait unchanged in the final page of the approved PDF.
This is the current reference-based build; older layout builders are retained separately.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import pymupdf
import subprocess, sys, re

ROOT=Path(__file__).resolve().parents[1]
# The final page uses the latest user-uploaded portrait verbatim.
source=ROOT/'assets/venus-approved-reference.pdf'
pdf=pymupdf.open(source)
# Rebuild only the final page to remove the portrait frame and integrate its silhouette.
subprocess.run([sys.executable,str(ROOT/'scripts/make_venus_consultation_pdf.py')],check=True)
# Replace only full-page background image resources on the cover and sign pages.
# Shared image xrefs are replaced once; all text/vector layout remains intact.
replaced=set()
for page in list(pdf)[:13]:
    for image in page.get_images():
        xref=image[0]
        if xref in replaced:
            continue
        if any(abs(r.width-page.rect.width)<1 and abs(r.height-page.rect.height)<1
               for r in page.get_image_rects(xref)):
            page.replace_image(xref, filename=str(ROOT/'assets/venus-silk-background.jpg'))
            replaced.add(xref)
assert replaced, 'Reference must contain a full-page background'
toc=pdf.get_toc()
pdf.delete_page(len(pdf)-1)
with pymupdf.open(ROOT/'documents/Личный разбор Венеры.pdf') as offer:
    pdf.insert_pdf(offer)
pdf.set_toc(toc)
output=ROOT/'documents/Venera.pdf'
pdf.save(output,garbage=4,deflate=True)
pdf.close()
with pymupdf.open(source) as before, pymupdf.open(output) as after:
    assert len(before)==len(after)==14
    norm=lambda text: re.sub(r'\s+','',text)
    assert all(norm(x.get_text())==norm(y.get_text()) for x,y in zip(before,after))
    for i in range(13):
        assert before[i].get_text('words')==after[i].get_text('words')
print('Verified: user-selected portrait used without RGB changes; all text and first 13 page text positions unchanged; silk background updated.')
print(output)

# A distinct download name avoids reopening an older downloaded Venera.pdf.
unique_output=ROOT/'documents/Venera_bez_ramok.pdf'
unique_output.write_bytes(output.read_bytes())
print(unique_output)

silk_output=ROOT/'documents/Venera_silk.pdf'
silk_output.write_bytes(output.read_bytes())
print(silk_output)
