"""Assemble the free demo version: cover + matrix + brief descriptions (5 pages).

Takes the brief PDF (cover + three brief-description pages) and inserts the
pastel matrix page from the full workbook after the cover.
"""
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / 'documents/Matrix_zhenskie_chakry_kratko.pdf'
FULL = ROOT / 'documents/Matrix_zhenskie_chakry.pdf'
OUT = ROOT / 'documents/Matrix_zhenskie_chakry_demo.pdf'

demo = pymupdf.open(BRIEF)
assert len(demo) == 4, len(demo)
with pymupdf.open(FULL) as src:
    assert len(src) == 70, len(src)
    demo.insert_pdf(src, from_page=1, to_page=1, start_at=1)

assert len(demo) == 5, len(demo)
demo.set_metadata({'title': 'Женские чакры • Демо-версия', 'author': 'Практикум по матрице судьбы'})
demo.save(OUT, garbage=4, deflate=True)

with pymupdf.open(OUT) as pdf:
    assert len(pdf) == 5
    texts = [p.get_text() for p in pdf]
    assert 'Краткие описания энергий' in texts[0]          # cover
    assert 'Три точки внимания' in texts[1]                # matrix page
    assert 'Свадхистана' in texts[2] and 'Анахата' in texts[3] and 'Аджна' in texts[4]
    pdf[1].get_pixmap(matrix=pymupdf.Matrix(1.2, 1.2)).save('/home/user/matrix-demo.png')
print(f'Demo assembled (5 pages): {OUT}')
