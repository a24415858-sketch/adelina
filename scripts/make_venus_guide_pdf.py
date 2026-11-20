"""Big Venus guide (~100 pages): signs, houses, aspects, archetypes, practices."""
from pathlib import Path
import json, math
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
OUT = ROOT / 'documents/Venera_polny_gayd.pdf'
data = json.loads((ROOT / 'assets/venus-guide-content.json').read_text())

pdfmetrics.registerFont(TTFont('Display', str(ROOT / 'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))

W, H = 595.276, 841.89
INK = '#4A3542'; MUTED = '#8A6B7C'; GOLD = '#B08D57'
PAPER = '#FDF9F5'
c = canvas.Canvas(str(OUT), pagesize=(W, H), pageCompression=1)
c.setTitle('Венера — полный гайд')
c.setAuthor('Практикум по Венере')
page = 0


def text(s, x, y, size=11, font='Body', color=INK):
    c.setFillColor(HexColor(color)); c.setFont(font, size); c.drawString(x, y, s)


def ctext(s, y, size=11, font='Body', color=INK):
    c.setFillColor(HexColor(color)); c.setFont(font, size); c.drawCentredString(W / 2, y, s)


def para(s, x, y, width, size=11, leading=17, color=INK, font='Body', align=None):
    st = ParagraphStyle('b', fontName=font, fontSize=size, leading=leading, textColor=HexColor(color))
    if align is not None:
        st.alignment = align
    p = Paragraph(escape(s).replace('\n', '<br/>'), st)
    _, hh = p.wrap(width, H); p.drawOn(c, x, y - hh)
    assert y - hh > 60, (s[:40], y, hh)
    return y - hh


def motif(cx, cy, r):
    c.saveState(); c.setStrokeColor(HexColor('#D9C3B0')); c.setLineWidth(.5)
    for a in range(0, 360, 60):
        rad = math.radians(a); c.circle(cx + math.cos(rad) * r * .5, cy + math.sin(rad) * r * .5, r * .65, stroke=1, fill=0)
    c.circle(cx, cy, r * 1.2, stroke=1, fill=0); c.restoreState()


def base(label):
    global page
    page += 1
    c.setFillColor(HexColor(PAPER)); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(HexColor('#F3E7DC')); c.circle(W + 70, H - 80, 180, fill=1, stroke=0)
    motif(W + 10, 50, 95)
    text('ВЕНЕРА  /  ПОЛНЫЙ ГАЙД', 46, 805, 7.5, color=MUTED)
    c.setStrokeColor(HexColor('#E0CDBB')); c.setLineWidth(.5); c.line(46, 43, W - 46, 43)
    text(label, 46, 28, 7, color=MUTED); text(f'{page:02d}', W - 63, 28, 8, color=MUTED)


def divider(num, title, subtitle):
    base(title)
    ctext(f'ЧАСТЬ {num}', 640, 12, 'Body', GOLD)
    ctext(title, 590, 44, 'Display')
    c.setStrokeColor(HexColor(GOLD)); c.setLineWidth(.8); c.line(W / 2 - 50, 555, W / 2 + 50, 555)
    para(subtitle, 110, 520, 375, 12, 20, MUTED, align=TA_CENTER)
    c.showPage()


def section_head(kicker, title, sub=None):
    text(kicker, 46, 752, 8, 'Bold', GOLD)
    text(title, 46, 718, 34, 'Display')
    if sub:
        text(sub, 46, 692, 10, color=MUTED)
    return 668 if sub else 690


def block_label(y, label):
    text(label, 46, y, 8, 'Bold', GOLD)
    return y - 20


def bullets(items, y, size=11, leading=17, gap=6):
    for it in items:
        text('•', 46, y - 3, size, 'Body', GOLD)
        y = para(it, 66, y, 483, size, leading) - gap
    return y


# ---------- Cover ----------
page += 1
c.setFillColor(HexColor('#F3E7DC')); c.rect(0, 0, W, H, fill=1, stroke=0)
motif(W / 2, 600, 130)
ctext('ВЕНЕРА', 780, 13, 'Body', GOLD)
for t, y in [('Полный', 470), ('гайд', 400)]:
    c.setFillColor(HexColor(INK)); c.setFont('Display', 72); c.drawCentredString(W / 2, y, t)
c.setStrokeColor(HexColor(GOLD)); c.setLineWidth(.8); c.line(W / 2 - 55, 362, W / 2 + 55, 362)
ctext('Любовь · Красота · Притяжение', 325, 12, 'Body', MUTED)
ctext('Знаки · Дома · Аспекты · Практики', 295, 11, 'Body', MUTED)
para('Большой подробный гайд по Венере: что она значит в вашей карте и как вывести её в плюс.', 120, 220, 355, 11.5, 19, MUTED, align=TA_CENTER)
c.bookmarkPage('cover'); c.addOutlineEntry('Венера — полный гайд', 'cover', 0); c.showPage()

# ---------- Contents ----------
base('Содержание')
y = section_head('СОДЕРЖАНИЕ', 'Что внутри')
toc = [
    ('Введение', 'Что такое Венера и как читать гайд'),
    ('Часть I', 'Венера в знаках — 12 стилей любви и красоты'),
    ('Часть II', 'Венера в домах — 12 сфер жизни'),
    ('Часть III', 'Аспекты Венеры — связи с другими планетами'),
    ('Часть IV', 'Архетипы Венеры — 12 лиц богини'),
    ('Часть V', 'Как вывести Венеру в плюс — практики'),
    ('Заключение', 'Ваша Венера уже прекрасна'),
]
for t, d in toc:
    text(t, 46, y, 15, 'Display', GOLD)
    y = para(d, 46, y - 22, 503, 11, 17, MUTED) - 18
c.showPage()

# ---------- Intro ----------
base('Введение')
y = section_head('ВВЕДЕНИЕ', 'Что такое Венера')
for sec in data['intro']:
    y = block_label(y, sec['title'].upper())
    for p in sec['paragraphs']:
        y = para(p, 46, y, 503, 11, 17.5) - 12
    y -= 14
    if y < 200:
        c.showPage(); base('Введение'); y = 760
c.showPage()

# ---------- Part 1: Signs (2 pages each) ----------
divider('I', 'Венера в знаках', 'Стиль любви и красоты: как Венера проявляется в каждом знаке зодиака.')
for s in data['signs']:
    base(s['title'])
    y = section_head(s['element'].upper(), s['title'], f'Архетип: {s["archetype"]}')
    text(s['symbol'], W - 90, 720, 40, 'Body', GOLD)
    y = para(s['intro'], 46, y, 503, 11, 17.5) - 16
    y = block_label(y, 'ЧЕМ ЦЕПЛЯЕТ')
    y = bullets(s['attraction'], y) - 10
    y = block_label(y, 'КАК ВЫКРУТИТЬ НА МАКСИМУМ')
    y = bullets(s['amplify'], y)
    c.showPage()
    base(s['title'] + ' · продолжение')
    y = section_head(s['element'].upper(), s['title'], f'Архетип: {s["archetype"]}')
    text(s['symbol'], W - 90, 720, 40, 'Body', GOLD)
    y = block_label(y, 'ТЕЛО · ДОМ · СТИЛЬ')
    y = para(f'Тело: {s["body"]}', 46, y, 503, 11, 17) - 4
    y = para(f'Дом: {s["home"]}', 46, y, 503, 11, 17) - 4
    y = para(f'Стиль: {s["style"]}', 46, y, 503, 11, 17) - 12
    y = block_label(y, 'ЧТО УМЕНЬШАЕТ')
    y = para(s['diminish'], 46, y, 503, 11, 17) - 12
    y = block_label(y, 'В ПЛЮСЕ')
    y = para(s['plus'], 46, y, 503, 11, 17.5)
    c.showPage()

# ---------- Part 2: Houses (2 pages each) ----------
divider('II', 'Венера в домах', 'Сфера жизни, где Венера проявляется сильнее всего: дом, деньги, партнёрство, глубина.')
for h in data['houses']:
    base(h['title'])
    y = section_head(f'ДОМ {h["symbol"]}', h['title'], h['sphere'])
    y = para(h['intro'], 46, y, 503, 11, 17.5) - 14
    y = block_label(y, 'КАК ПРОЯВЛЯЕТСЯ')
    y = para(h['express'], 46, y, 503, 11, 17.5) - 14
    y = block_label(y, 'СИЛЬНЫЕ СТОРОНЫ')
    y = bullets(h['strengths'], y)
    c.showPage()
    base(h['title'] + ' · продолжение')
    y = section_head(f'ДОМ {h["symbol"]}', h['title'], h['sphere'])
    y = block_label(y, 'ВЫЗОВЫ')
    y = bullets(h['challenges'], y) - 10
    y = block_label(y, 'КАК ВЫВЕСТИ В ПЛЮС')
    y = para(h['plus'], 46, y, 503, 11, 17.5)
    c.showPage()

# ---------- Part 3: Aspects (2 pages each) ----------
divider('III', 'Аспекты Венеры', 'Связи Венеры с другими планетами: что поддерживает, а где бывают трения.')
for a in data['aspects']:
    base(a['title'])
    y = section_head('АСПЕКТ', a['title'])
    text(a['symbol'], W - 90, 720, 40, 'Body', GOLD)
    y = para(a['intro'], 46, y, 503, 11, 17.5) - 14
    y = block_label(y, 'СИЛЬНЫЕ СТОРОНЫ')
    y = bullets(a['strengths'], y)
    c.showPage()
    base(a['title'] + ' · продолжение')
    y = section_head('АСПЕКТ', a['title'])
    y = block_label(y, 'ВЫЗОВЫ')
    y = bullets(a['challenges'], y) - 10
    y = block_label(y, 'КАК ВЫВЕСТИ В ПЛЮС')
    y = para(a['plus'], 46, y, 503, 11, 17.5)
    c.showPage()

# ---------- Part 4: Archetypes (1 page each) ----------
divider('IV', 'Архетипы Венеры', 'Двенадцать лиц Венеры: найдите свой архетип и его силу.')
for ar in data['archetypes']:
    base(ar['name'])
    y = section_head('АРХЕТИП', ar['name'], f'Знак: {ar["sign"]}')
    y = para(ar['desc'], 46, y, 503, 12, 19) - 16
    y = block_label(y, 'СИЛА АРХЕТИПА')
    y = bullets(ar['strengths'], y) - 10
    y = block_label(y, 'ТЕНЬ АРХЕТИПА')
    y = bullets(ar['shadow'], y) - 10
    y = block_label(y, 'КАК ЖИТЬ В ПЛЮСЕ')
    y = para(ar['plus'], 46, y, 503, 11, 17.5)
    c.showPage()

# ---------- Part 5: Practical ----------
divider('V', 'Как вывести Венеру в плюс', 'Практики красоты, удовольствия, любви и самоценности.')
for sec in data['practical']:
    base(sec['title'])
    y = section_head('ПРАКТИКА', sec['title'])
    for p in sec['paragraphs']:
        y = para(p, 46, y, 503, 11, 17.5) - 12
    c.showPage()

# ---------- Notes ----------
for i in range(1, 3):
    base('Дневник Венеры')
    y = section_head('ДНЕВНИК', 'Дневник Венеры')
    y = para('Записывайте сюда свои наблюдения: когда Венера приносит вам радость, что вы любите в себе, какие практики работают именно для вас.', 46, y, 503, 11, 17.5, MUTED) - 20
    for _ in range(9):
        c.setStrokeColor(HexColor('#D9C3B0')); c.setLineWidth(.5); c.line(46, y, W - 46, y)
        y -= 62
    c.showPage()
base('Мои открытия и планы')
y = section_head('ПЛАНЫ', 'Мои открытия и планы')
y = para('Что вы узнали о своей Венере и что хотите попробовать в ближайшие недели.', 46, y, 503, 11, 17.5, MUTED) - 20
for _ in range(10):
    c.setStrokeColor(HexColor('#D9C3B0')); c.setLineWidth(.5); c.line(46, y, W - 46, y)
    y -= 58
c.showPage()

# ---------- Closing ----------
base('Заключение')
y = section_head('ЗАКЛЮЧЕНИЕ', 'Ваша Венера уже прекрасна')
for p in data['closing']:
    y = para(p, 46, y, 503, 11.5, 18.5) - 14
c.showPage()

c.save()
with pymupdf.open(OUT) as pdf:
    full = ''.join(p.get_text() for p in pdf)
    compact = lambda v: ''.join(v.split())
    for s in data['signs']:
        assert compact(s['intro']) in compact(full), s['title']
    for h in data['houses']:
        assert compact(h['intro']) in compact(full), h['title']
    for a in data['aspects']:
        assert compact(a['intro']) in compact(full), a['title']
    for p in pdf:
        for word in p.get_text('words'):
            assert word[0] >= 0 and word[1] >= 0 and word[2] <= W + 1 and word[3] <= H + 1, word
    pdf[3].get_pixmap(matrix=pymupdf.Matrix(1.2, 1.2)).save('/home/user/venus-guide-preview.png')
    print(f'Venus guide built: {len(pdf)} pages: {OUT}')
