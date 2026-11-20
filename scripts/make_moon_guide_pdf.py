"""70-page Moon guide in the pearl-ocean styling (gentle blue, pearls, shells)."""
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
OUT = ROOT / 'documents/Luna_polny_gayd.pdf'
BG = ROOT / 'assets/pearl-ocean-background.jpg'
data = json.loads((ROOT / 'assets/moon-guide-content.json').read_text())

pdfmetrics.registerFont(TTFont('Display', str(ROOT / 'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='Bold', italic='Body', boldItalic='Bold')

W, H = 595.276, 841.89
INK = '#33475E'; ACCENT = '#4A7BA6'; SILVER = '#93A5B8'; LINE = '#B9CCDD'; BOX = '#EAF1F8'
MARGIN = 48; CW = W - 2 * MARGIN
LIMIT = 292  # lowest y (from bottom) text may reach; image busy area below
c = canvas.Canvas(str(OUT), pagesize=(W, H), pageCompression=1)
c.setTitle('Луна — полный гайд')
c.setAuthor('Практикум по Луне')
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


def measure(s, width, size=10.5, leading=16, font='Body'):
    p = Paragraph(escape(s), ParagraphStyle('m', fontName=font, fontSize=size, leading=leading))
    return p.wrap(width, H)[1]


def bg():
    global page
    page += 1
    c.drawImage(str(BG), 0, 0, W, H)
    ctext(f'— {page} —', 24, 8, 'Body', ACCENT)


def header(kicker, title, sub=None, symbol=None):
    """Centered demo-style header. Returns y (from bottom) below header."""
    y = H - 62
    ctext(kicker.upper(), y, 8.5, 'Bold', ACCENT); y -= 20
    ctext(title, y, 30, 'Display', INK); y -= 34
    if sub:
        ctext(sub, y, 19, 'Display', ACCENT); y -= 26
    c.setStrokeColor(HexColor(LINE)); c.setLineWidth(.7)
    c.line(W / 2 - 90, y, W / 2 - 14, y); c.line(W / 2 + 14, y, W / 2 + 90, y)
    if symbol:
        ctext(symbol, y - 4, 15, 'Body', SILVER)
    y -= 30
    return y


def label(y, s):
    text(s.upper(), MARGIN, y, 8.5, 'Bold', ACCENT)
    return y - 16


def bullets(items, y, size=10.5, leading=15.5, gap=4):
    for it in items:
        c.setFillColor(HexColor(ACCENT)); c.circle(MARGIN + 3, y - 4, 2.2, fill=1, stroke=0)
        y = para(it, MARGIN + 16, y, CW - 16, size, leading) - gap
    return y


def box(y, title, body):
    """Light-blue rounded box like the demo. y = top of box (from bottom)."""
    st = ParagraphStyle('x', fontName='Body', fontSize=10.5, leading=15.5, textColor=HexColor(INK))
    p = Paragraph(escape(body), st)
    _, hh = p.wrap(CW - 36, H)
    top = y; bottom = y - (10 + 14 + hh + 8)
    assert bottom > LIMIT, (title, bottom)
    c.setFillColor(HexColor(BOX)); c.setStrokeColor(HexColor(LINE)); c.setLineWidth(.7)
    c.roundRect(MARGIN, bottom, CW, top - bottom, 10, fill=1, stroke=1)
    text(title.upper(), MARGIN + 18, top - 24, 8.5, 'Bold', ACCENT)
    p.drawOn(c, MARGIN + 18, top - 30 - hh)
    return bottom - 12


def kv(y, key, val):
    text(key, MARGIN, y, 10.5, 'Bold', ACCENT)
    return para(val, MARGIN + 62, y, CW - 62, 10.5, 15.5) - 4


# ---------- Cover ----------
page += 1
c.drawImage(str(BG), 0, 0, W, H)
c.setStrokeColor(HexColor(ACCENT)); c.setLineWidth(.8)
c.circle(W / 2, H - 210, 52, stroke=1, fill=0)
ctext('☽', H - 222, 52, 'Body', ACCENT)
ctext('Луна', H - 330, 78, 'Display', ACCENT)
ctext('полный гайд', H - 372, 30, 'Display', INK)
c.setStrokeColor(HexColor(SILVER)); c.setLineWidth(.8); c.line(W / 2 - 55, H - 400, W / 2 + 55, H - 400)
ctext('ЭМОЦИИ · КОМФОРТ · ДОМ', H - 430, 9, 'Bold', ACCENT)
c.bookmarkPage('cover'); c.addOutlineEntry('Луна — полный гайд', 'cover', 0); c.showPage()

# ---------- Contents ----------
bg()
y = header('Содержание', 'Что внутри')
toc = [
    ('Введение', 'Что такое Луна и как читать гайд'),
    ('Луна в знаках', '12 способов чувствовать и заботиться'),
    ('Луна в домах', '12 сфер жизни'),
    ('Аспекты Луны', 'Соединение, трин, секстиль, оппозиция, квадрат с другими планетами'),
    ('Архетипы Луны', '12 лиц лунной богини'),
    ('Как вывести Луну в плюс', 'Практики комфорта, заботы и внутреннего спокойствия'),
    ('Луна и стихии', 'Огонь, земля, воздух, вода'),
    ('Луна в жизни', 'Дом, семья, привычки, сны, ритмы'),
    ('Вопросы к себе', 'Творчество, отдых, карма, праздники'),
    ('Заключение', 'Ваша Луна уже заботится о вас'),
]
for t, d in toc:
    y = para(f'{t} — {d}', MARGIN, y, CW, 11, 16, INK, align=TA_CENTER) - 10
c.showPage()


# ---------- Intro (1 page) ----------
bg()
y = header('Введение', 'Что такое Луна')
for sec in data['intro']:
    y = label(y, sec['title'])
    for p in sec['paragraphs']:
        y = para(p, MARGIN, y, CW, 10, 13) - 6
    y -= 6
c.showPage()

# ---------- Part I: Signs (1 page each, demo layout) ----------
for s in data['signs']:
    bg()
    y = header(s['element'], s['title'], f'«{s["archetype"]}»', s['symbol'])
    y = label(y, 'Как проявляется')
    y = bullets(s['manifest'], y) - 4
    y = label(y, 'Как усилить')
    y = bullets(s['amplify'], y) - 4
    y = label(y, 'Как раскрывается')
    y = kv(y, 'Дом', s['home'])
    y = kv(y, 'Образ', s['style']) - 4
    y = label(y, 'В плюсе')
    y = para(s['plus'], MARGIN, y, CW, 10.5, 15.5) - 8
    box(y, 'Что гасит', s['dim'])
    c.bookmarkPage('sign' + s['title']); c.addOutlineEntry(s['title'], 'sign' + s['title'], 1)
    c.showPage()

# ---------- Part II: Houses (1 page each) ----------
for h in data['houses']:
    bg()
    y = header(f'Дом {h["symbol"]}', h['title'], h['sphere'])
    y = para(h['intro'], MARGIN, y, CW, 10.5, 15) - 10
    y = label(y, 'Как проявляется')
    y = para(h['express'], MARGIN, y, CW, 10.5, 15) - 4
    y = label(y, 'Сильные стороны')
    y = bullets(h['strengths'], y) - 4
    y = label(y, 'Вызовы')
    y = bullets(h['challenges'], y) - 6
    box(y, 'Как вывести в плюс', h['plus'])
    c.bookmarkPage('house' + h['title']); c.addOutlineEntry(h['title'], 'house' + h['title'], 1)
    c.showPage()

# ---------- Part III: Aspects (5 types with planets) ----------
for a in data['aspects']:
    bg()
    y = header('Аспект', a['title'], None, a['symbol'])
    y = para(a['intro'], MARGIN, y, CW, 10.5, 15) - 6
    for pl in ['Солнце', 'Меркурий', 'Марс', 'Юпитер', 'Сатурн', 'Уран', 'Нептун', 'Плутон']:
        st = ParagraphStyle('pl', fontName='Body', fontSize=9, leading=12, textColor=HexColor(INK))
        p = Paragraph(f'<b><font color="{ACCENT}">{pl}.</font></b> ' + escape(a['planets'][pl]), st)
        _, hh = p.wrap(CW, H); p.drawOn(c, MARGIN, y - hh)
        assert y - hh > LIMIT, (pl, y, hh)
        y = y - hh - 2
    box(y, 'Как вывести в плюс', a['plus'])
    c.bookmarkPage('aspect' + a['title']); c.addOutlineEntry(a['title'], 'aspect' + a['title'], 1)
    c.showPage()

# ---------- Part IV: Archetypes (1 page each) ----------
for ar in data['archetypes']:
    bg()
    y = header('Архетип', ar['name'], f'знак: {ar["sign"]}')
    y = para(ar['desc'], MARGIN, y, CW, 10.5, 16) - 8
    y = label(y, 'Сила архетипа')
    y = bullets(ar['strengths'], y) - 4
    y = label(y, 'Тень архетипа')
    y = bullets(ar['shadow'], y) - 4
    box(y, 'Как жить в плюсе', ar['plus'])
    c.bookmarkPage('arch' + ar['name']); c.addOutlineEntry(ar['name'], 'arch' + ar['name'], 1)
    c.showPage()

# ---------- Practical (1 page each) ----------
for sec in data['practical']:
    bg()
    y = header('Практика', sec['title'])
    for p in sec['paragraphs'][:4]:
        y = para(p, MARGIN, y, CW, 10.5, 15) - 9
    c.showPage()

# ---------- Part VI: Elements ----------
for e in data['elements']:
    bg()
    y = header('Стихия', e['title'], e['name'], e['symbol'])
    y = para(e['intro'], MARGIN, y, CW, 10.5, 16) - 8
    y = label(y, 'Сильные стороны')
    y = bullets(e['strengths'], y) - 4
    y = label(y, 'Вызовы')
    y = bullets(e['challenges'], y) - 6
    box(y, 'Как вывести в плюс', e['plus'])
    c.showPage()

# ---------- Themes ----------
for th in data['themes']:
    bg()
    y = header('Тема', th['title'], None, th['symbol'])
    y = para(th['intro'], MARGIN, y, CW, 10.5, 15) - 8
    y = label(y, 'Сильные стороны')
    y = bullets(th['strengths'], y) - 4
    y = label(y, 'Вызовы')
    y = bullets(th['challenges'], y) - 6
    box(y, 'Как вывести в плюс', th['plus'])
    c.showPage()

# ---------- Questions / Creativity / Rest / Karma ----------
bg()
y = header('Вопросы', 'Вопросы к себе')
y = bullets(data['questions'], y, gap=7)
c.showPage()

for key in ('creativity', 'rest', 'karma', 'holidays'):
    sec = data[key]
    bg()
    y = header('Глубже', sec['title'])
    for p in sec['paragraphs']:
        y = para(p, MARGIN, y, CW, 10.5, 16) - 10
    c.showPage()

# ---------- Notes ----------
for i in range(1, 4):
    bg()
    y = header('Дневник', 'Дневник Луны')
    y = para('Записывайте сюда свои наблюдения: когда вы чувствуете себя в безопасности, что приносит вам спокойствие, какие практики заботы работают именно для вас.', MARGIN, y, CW, 10.5, 15.5, ACCENT) - 24
    for _ in range(7):
        c.setStrokeColor(HexColor(LINE)); c.setLineWidth(.6); c.line(MARGIN, y, W - MARGIN, y)
        y -= 46
    c.showPage()
bg()
y = header('Планы', 'Мои открытия и планы')
y = para('Что вы узнали о своей Луне и что хотите попробовать в ближайшие недели.', MARGIN, y, CW, 10.5, 15.5, ACCENT) - 24
for _ in range(8):
    c.setStrokeColor(HexColor(LINE)); c.setLineWidth(.6); c.line(MARGIN, y, W - MARGIN, y)
    y -= 44
c.showPage()

# ---------- Closing ----------
bg()
y = header('Заключение', 'Ваша Луна уже заботится о вас')
for p in data['closing']:
    y = para(p, MARGIN, y, CW, 11, 17) - 12
c.showPage()

c.save()
with pymupdf.open(OUT) as pdf:
    full = ''.join(p.get_text() for p in pdf)
    compact = lambda v: ''.join(v.split())
    for s in data['signs']:
        assert compact(s['plus']) in compact(full), s['title']
    for a in data['aspects']:
        for pl, t in a['planets'].items():
            assert compact(t) in compact(full), (a['title'], pl)
    assert 'синастри' not in full.lower(), 'synastry must be removed'
    assert 'магнетизм' not in full.lower(), 'magnetism must be removed'
    for p in pdf:
        for word in p.get_text('words'):
            assert word[0] >= 0 and word[1] >= 0 and word[2] <= W + 1 and word[3] <= H + 1, word
    for i, name in [(0, 'cover'), (4, 'sign'), (16, 'house'), (28, 'aspect'), (34, 'arch'), (len(pdf) - 1, 'closing')]:
        pdf[i].get_pixmap(matrix=pymupdf.Matrix(1.1, 1.1)).save(f'/home/user/moon-{name}.png')
    print(f'Moon guide built: {len(pdf)} pages: {OUT}')
