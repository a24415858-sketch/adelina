"""Expanded free demo (12 pages): cover + matrix + brief descriptions with
'how to bring into plus' + detailed samples of the three highlighted energies
+ an enticing closing page.

Assembles the brief PDF (cover + brief-description pages), inserts the pastel
matrix page and the detailed pages for energies 18/11/22 from the full
workbook, and appends a freshly drawn closing page inviting to the full guide.
"""
from pathlib import Path
import math
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / 'documents/Matrix_zhenskie_chakry_kratko.pdf'
FULL = ROOT / 'documents/Matrix_zhenskie_chakry.pdf'
OUT = ROOT / 'documents/Matrix_zhenskie_chakry_demo.pdf'
TMP = ROOT / 'documents/_demo_closing.pdf'

pdfmetrics.registerFont(TTFont('Display', str(ROOT / 'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
W, H = 595.276, 841.89
INK = '#503B4C'; MUTED = '#826578'; GOLD = '#A66E87'; PAPER = '#FCF7F8'

# --- closing page -----------------------------------------------------------
c = canvas.Canvas(str(TMP), pagesize=(W, H), pageCompression=1)


def text(s, x, y, size=11, font='Body', color=INK):
    c.setFillColor(HexColor(color)); c.setFont(font, size); c.drawString(x, y, s)


def para(s, x, y, width, size=11, leading=17, color=INK):
    p = Paragraph(escape(s).replace('\n', '<br/>'),
                  ParagraphStyle('b', fontName='Body', fontSize=size, leading=leading, textColor=HexColor(color)))
    _, hh = p.wrap(width, H); p.drawOn(c, x, y - hh); return y - hh


def motif(cx, cy, r):
    c.saveState(); c.setStrokeColor(HexColor('#E8D6E1')); c.setLineWidth(.55)
    for a in range(0, 360, 60):
        rad = math.radians(a); c.circle(cx + math.cos(rad) * r * .5, cy + math.sin(rad) * r * .5, r * .65, stroke=1, fill=0)
    c.circle(cx, cy, r * 1.2, stroke=1, fill=0); c.restoreState()


c.setFillColor(HexColor(PAPER)); c.rect(0, 0, W, H, fill=1, stroke=0)
c.setFillColor(HexColor('#F0E2EB')); c.circle(W + 65, H - 90, 190, fill=1, stroke=0)
motif(W + 8, 55, 100)
text('ЖЕНСКИЕ ЧАКРЫ  /  МАТРИЦА СУДЬБЫ', 46, 805, 7.5, color=MUTED)
c.setStrokeColor(HexColor('#DFC8D5')); c.setLineWidth(.5); c.line(46, 43, W - 46, 43)
text('Полный гайд', 46, 28, 7, color=MUTED)

# Beautiful offer of the full guide with the pastel matrix image (no contents list).
img_size = 270
c.drawImage(str(ROOT / 'assets/matrix-pastel.png'), W / 2 - img_size / 2, 470, img_size, img_size)
c.setFillColor(HexColor(INK)); c.setFont('Display', 34)
c.drawCentredString(W / 2, 425, 'Полный гайд «Женские чакры»')
c.setFillColor(HexColor(MUTED)); c.setFont('Body', 13)
c.drawCentredString(W / 2, 388, '70 страниц с описаниями всех чакр')
c.setStrokeColor(HexColor(GOLD)); c.setLineWidth(.8); c.line(W / 2 - 55, 360, W / 2 + 55, 360)
c.setFillColor(HexColor(INK)); c.setFont('Display', 24)
c.drawCentredString(W / 2, 322, 'Напиши мне, чтобы получить полный гайд')
c.showPage(); c.save()

# --- assemble ---------------------------------------------------------------
demo = pymupdf.open(BRIEF)                       # cover + brief-description pages
assert len(demo) == 7, len(demo)
with pymupdf.open(FULL) as src:
    assert len(src) == 70, len(src)
    demo.insert_pdf(src, from_page=1, to_page=1, start_at=1)   # matrix after cover
    demo.insert_pdf(src, from_page=19, to_page=19)             # Svadhisthana 18 (detailed)
    demo.insert_pdf(src, from_page=33, to_page=33)             # Anahata 11 (detailed)
    demo.insert_pdf(src, from_page=65, to_page=65)             # Ajna 22 (detailed)
with pymupdf.open(TMP) as closing:
    demo.insert_pdf(closing)
TMP.unlink()
assert len(demo) == 12, len(demo)
demo.set_metadata({'title': 'Женские чакры • Демо-версия', 'author': 'Практикум по матрице судьбы'})
demo.save(OUT, garbage=4, deflate=True)

with pymupdf.open(OUT) as pdf:
    assert len(pdf) == 12
    t = [p.get_text() for p in pdf]
    assert 'Краткие описания энергий' in t[0]          # cover
    assert 'Три точки внимания' in t[1]                # matrix page
    assert 'Свадхистана' in t[2] and 'в плюс:' in t[2]  # brief page with how-to
    assert 'Полный гайд «Женские чакры»' in t[11] and '70 страниц с описаниями всех чакр' in t[11]  # closing offer
    pdf[2].get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save('/home/user/matrix-demo-brief.png')
print(f'Expanded demo assembled (12 pages): {OUT}')
