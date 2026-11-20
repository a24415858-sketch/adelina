"""Venus guide: only 'Чем цепляет' for each sign, demo styling."""
from pathlib import Path
import json
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
OUT = ROOT / 'documents/Venera_chem_ceptlyaet.pdf'
BG = ROOT / 'assets/venus-silk-bg.png'
data = json.loads((ROOT / 'assets/venus-content.json').read_text())

pdfmetrics.registerFont(TTFont('Display', str(ROOT / 'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Body', boldItalic='Bold')

W, H = 595.276, 841.89
INK = '#59404B'; ROSE = '#A75E77'; GOLD = '#B08D57'; LINE = '#D7B5BF'
MARGIN = 48; CW = W - 2 * MARGIN
LIMIT = 292
c = canvas.Canvas(str(OUT), pagesize=(W, H), pageCompression=1)
c.setTitle('Венера — чем цепляет')
page = 0


def text(s, x, y, size=11, font='Body', color=INK):
    c.setFillColor(HexColor(color)); c.setFont(font, size); c.drawString(x, y, s)


def ctext(s, y, size=11, font='Body', color=INK):
    c.setFillColor(HexColor(color)); c.setFont(font, size); c.drawCentredString(W / 2, y, s)


def para(s, x, y, width, size=10.5, leading=15.5, color=INK, font='Body', align=None):
    st = ParagraphStyle('b', fontName=font, fontSize=size, leading=leading, textColor=HexColor(color))
    if align is not None:
        st.alignment = align
    p = Paragraph(escape(s), st)
    _, hh = p.wrap(width, H); p.drawOn(c, x, y - hh)
    assert y - hh > LIMIT, (s[:50], y, hh)
    return y - hh


def bg():
    global page
    page += 1
    c.drawImage(str(BG), 0, 0, W, H)
    ctext(f'— {page} —', 24, 8, 'Body', ROSE)


def header(kicker, title, sub=None, symbol=None):
    y = H - 62
    ctext(kicker.upper(), y, 8.5, 'Bold', ROSE); y -= 20
    ctext(title, y, 30, 'Display', INK); y -= 34
    if sub:
        ctext(sub, y, 19, 'Display', ROSE); y -= 26
    c.setStrokeColor(HexColor(LINE)); c.setLineWidth(.7)
    c.line(W / 2 - 90, y, W / 2 - 14, y); c.line(W / 2 + 14, y, W / 2 + 90, y)
    if symbol:
        ctext(symbol, y - 4, 15, 'Body', GOLD)
    y -= 30
    return y


# ---------- Cover ----------
page += 1
c.drawImage(str(BG), 0, 0, W, H)
c.setStrokeColor(HexColor(ROSE)); c.setLineWidth(.8)
c.circle(W / 2, H - 210, 52, stroke=1, fill=0)
ctext('♀', H - 222, 52, 'Body', ROSE)
ctext('Венера', H - 330, 78, 'Display', ROSE)
ctext('чем цепляет', H - 372, 30, 'Display', INK)
c.setStrokeColor(HexColor(GOLD)); c.setLineWidth(.8); c.line(W / 2 - 55, H - 400, W / 2 + 55, H - 400)
ctext('ПРИТЯЖЕНИЕ · КРАСОТА · МАГНЕТИЗМ', H - 430, 9, 'Bold', ROSE)
c.bookmarkPage('cover'); c.addOutlineEntry('Венера — чем цепляет', 'cover', 0); c.showPage()

# ---------- Signs: 3 per page, only "Чем цепляет" ----------
for chunk_start in range(0, len(data), 2):
    bg()
    y = header('Венера в знаках', 'Чем цепляет')
    for s in data[chunk_start:chunk_start + 2]:
        ctext(s['title'], y, 24, 'Display', INK); y -= 26
        ctext(f'«{s["archetype"]}»', y, 15, 'Display', ROSE); y -= 20
        c.setStrokeColor(HexColor(LINE)); c.setLineWidth(.7)
        c.line(W / 2 - 70, y, W / 2 - 12, y); c.line(W / 2 + 12, y, W / 2 + 70, y)
        ctext(s['symbol'], y - 3, 13, 'Body', GOLD); y -= 22
        text('ЧЕМ ЦЕПЛЯЕТ', MARGIN, y, 8.5, 'Bold', ROSE); y -= 16
        for it in s['attraction']:
            c.setFillColor(HexColor(ROSE)); c.circle(MARGIN + 3, y - 4, 2.2, fill=1, stroke=0)
            y = para(it, MARGIN + 16, y, CW - 16, 10.5, 15.5) - 4
        y -= 18
        c.bookmarkPage('sign' + s['title']); c.addOutlineEntry(s['title'], 'sign' + s['title'], 1)
    c.showPage()

c.save()
with pymupdf.open(OUT) as pdf:
    full = ''.join(p.get_text() for p in pdf)
    for s in data:
        for b in s['attraction']:
            assert ''.join(b.split()) in ''.join(full.split()), s['title']
    pdf[1].get_pixmap(matrix=pymupdf.Matrix(1.1, 1.1)).save('/home/user/attraction-preview.png')
    print(f'Attraction PDF built: {len(pdf)} pages: {OUT}')
