"""Build the single deliverable: cover + 12 zodiac signs + personal consultation."""
from pathlib import Path
import subprocess
import sys
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
for script in ['make_venus_pdf.py','make_venus_consultation_pdf.py']:
    subprocess.run([sys.executable,str(ROOT/'scripts'/script)],check=True)

out=pymupdf.open()
with pymupdf.open(ROOT/'documents/Венера в знаках зодиака.pdf') as signs:
    assert len(signs)==13
    contents=signs.get_toc()
    out.insert_pdf(signs)
with pymupdf.open(ROOT/'documents/Личный разбор Венеры.pdf') as offer:
    assert len(offer)==1
    out.insert_pdf(offer)
out.set_toc([[1,'Венера в знаках зодиака',1]]+contents+[[1,'Личный разбор Венеры — 1 000 ₽',14]])
out.set_metadata({'title':'Венера — полный гид и личный разбор',
                  'subject':'12 знаков зодиака. Знак, дом и аспекты Венеры. Личный разбор за 1 000 рублей.'})
path=ROOT/'documents/Venera.pdf'
out.save(path,garbage=4,deflate=True)
out.close()
print(path)
