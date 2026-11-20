"""Change the hair in the user's approved PDF while restoring its actual face pixels.
This is the current reference-based build; older layout builders are retained separately.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import pymupdf
import subprocess, sys, re

ROOT=Path(__file__).resolve().parents[1]
original=Image.open(ROOT/'assets/venus-approved-reference-portrait.png').convert('RGB')
edit=Image.open(ROOT/'assets/venus-pdf-hair-edit.png').convert('RGB').resize(original.size,Image.Resampling.LANCZOS)
assert original.size==(680,960)
# Restrict AI-generated pixels to the hair and nearby silhouette, not the whole photo.
hair=Image.new('L',original.size)
ImageDraw.Draw(hair).polygon([(135,25),(275,20),(365,45),(420,115),(460,215),(470,300),(495,410),(438,449),(354,396),(274,443),(231,509),(147,568),(35,601),(8,570),(24,466),(65,323),(83,173)],fill=255)
hair=hair.filter(ImageFilter.GaussianBlur(9))
# Protect the original face, ears, jaw and neck. No generated beauty retouch remains here.
face=Image.new('L',original.size)
ImageDraw.Draw(face).polygon([(207,96),(248,82),(286,86),(320,106),(346,143),(364,185),(374,226),(377,270),(371,316),(354,348),(349,389),(333,433),(293,457),(251,431),(226,391),(214,356),(194,324),(165,299),(159,271),(182,250),(194,208),(195,157)],fill=255)
# Feather only the silhouette edge; central facial features stay pixel-identical.
face=face.filter(ImageFilter.GaussianBlur(2))
a=np.asarray(hair,dtype=float)/255*(1-np.asarray(face,dtype=float)/255)
result=Image.fromarray(np.uint8(np.asarray(original,dtype=float)*(1-a[...,None])+np.asarray(edit,dtype=float)*a[...,None]))
portrait=ROOT/'assets/venus-approved-portrait-loose-curls.png'
result.save(portrait)
# Explicit check: central facial features come from the original image, unchanged.
assert np.array_equal(np.asarray(result)[190:320,220:345],np.asarray(original)[190:320,220:345])
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
print('Verified: original facial pixels restored, all text and first 13 pages unchanged.')
print(output)
