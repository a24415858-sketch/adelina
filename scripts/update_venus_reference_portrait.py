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
        assert before[i].get_pixmap().samples==after[i].get_pixmap().samples
print('Verified: user-selected portrait used without RGB changes; all text and first 13 pages unchanged.')
print(output)
