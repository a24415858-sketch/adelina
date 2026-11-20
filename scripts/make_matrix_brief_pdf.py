"""Compact brief descriptions: energies 2-22 in three chakras, one line each."""
from pathlib import Path
import math
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'documents/Matrix_zhenskie_chakry_kratko.pdf'

brief = {
 'Свадхистана': {
  '2': 'Тонкая чувственность и умение замечать своё «хочу» в тишине.',
  '3': 'Радость красоты и заботы, умение создавать уют и принимать тепло.',
  '4': 'Спокойная опора на себя, умение отдыхать и не держать всё на себе.',
  '5': 'Свобода выбирать свою женственность без чужих правил.',
  '6': 'Притягательность через живой контакт с собой и своими желаниями.',
  '7': 'Удовольствие от движения и свободы тела.',
  '8': 'Умение принимать заботу и не отдавать себя без остатка.',
  '9': 'Наслаждение уединением и тихими радостями.',
  '10': 'Лёгкость и умение находить удовольствие в обычном дне.',
  '11': 'Уверенность и смелость быть заметной.',
  '12': 'Нежность к себе и умение просить о заботе.',
  '13': 'Гибкость и умение обновляться без борьбы с собой.',
  '14': 'Гармония удовольствий и умение наслаждаться в меру.',
  '15': 'Свободная чувственность и страсть без зависимости от чужого внимания.',
  '16': 'Принятие себя и освобождение от сравнений.',
  '17': 'Вдохновение и умение видеть красоту вокруг.',
  '18': 'Чуткость к настроению и умение создавать уют.',
  '19': 'Радость и умение делиться светом.',
  '20': 'Связь с родом и умение беречь семейное тепло.',
  '21': 'Открытость новому и вкус к впечатлениям.',
  '22': 'Лёгкость и свобода пробовать без страха ошибиться.',
 },
 'Анахата': {
  '2': 'Тонкое слышание чувств и умение говорить о них прямо.',
  '3': 'Тепло и забота, умение дарить и принимать внимание.',
  '4': 'Надёжность и спокойная опора в отношениях.',
  '5': 'Уважение к ценностям и умение выстраивать близость на честности.',
  '6': 'Баланс между близостью и собственной жизнью.',
  '7': 'Терпение и умение слышать другого.',
  '8': 'Справедливая взаимность и умение говорить о важном.',
  '9': 'Глубина и умение делиться сокровенным с близкими.',
  '10': 'Устойчивая привязанность и тёплые традиции.',
  '11': 'Сила нежности и умение держать границы без жёсткости.',
  '12': 'Сострадание и умение поддерживать, не растворяясь.',
  '13': 'Умение отпускать и обновлять отношения.',
  '14': 'Мягкая честность и спокойное общение.',
  '15': 'Живая страсть и умение сохранять доверие.',
  '16': 'Ясность в чувствах и умение видеть реальность.',
  '17': 'Вдохновляющая любовь и вера в лучшее.',
  '18': 'Чуткость и умение создавать душевный уют.',
  '19': 'Открытое сердце и радость близости.',
  '20': 'Тепло к семье и умение беречь родные связи.',
  '21': 'Открытость людям и широта душевных связей.',
  '22': 'Лёгкость в общении и умение быть собой рядом с другими.',
 },
 'Аджна': {
  '2': 'Тонкая интуиция и умение слышать себя в тишине.',
  '3': 'Творческое видение и умение воплощать идеи.',
  '4': 'Практичный ум и умение строить понятные планы.',
  '5': 'Стремление к истине и умение учиться.',
  '6': 'Ясность выбора и умение слышать себя.',
  '7': 'Сосредоточенность и умение направлять внимание.',
  '8': 'Трезвый взгляд и умение видеть суть.',
  '9': 'Глубокое понимание и мудрость тишины.',
  '10': 'Умение видеть закономерности и учиться на опыте.',
  '11': 'Устойчивое внимание и умение не сдаваться.',
  '12': 'Принятие неопределённости и доверие процессу.',
  '13': 'Гибкость мышления и умение пересматривать взгляды.',
  '14': 'Взвешенность и умение собирать полную картину.',
  '15': 'Ясность желаний и умение не поддаваться иллюзиям.',
  '16': 'Умение пересобирать картину мира после потрясений.',
  '17': 'Вдохновляющее видение будущего.',
  '18': 'Различение чувств и фактов, спокойный взгляд.',
  '19': 'Уверенность в себе и умение ясно выражать мысли.',
  '20': 'Мудрость рода и умение видеть шире.',
  '21': 'Широта взгляда и интерес к миру.',
  '22': 'Любопытство и открытость новым идеям.',
 },
}
sections = [
 ('Свадхистана', 'Желания • удовольствие • творчество'),
 ('Анахата', 'Чувства • близость • границы'),
 ('Аджна', 'Восприятие • ясность • выбор'),
]
for chakra, _ in sections:
    assert set(brief[chakra]) == {str(n) for n in range(2, 23)}

pdfmetrics.registerFont(TTFont('Display', str(ROOT / 'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
W, H = 595.276, 841.89
c = canvas.Canvas(str(OUT), pagesize=(W, H), pageCompression=1)
c.setTitle('Женские чакры • Краткие описания энергий')
c.setAuthor('Практикум по матрице судьбы')
INK = '#503B4C'; MUTED = '#826578'; GOLD = '#A66E87'; PLUM = '#EFE1E9'; PAPER = '#FCF7F8'
page = 0


def text(s, x, y, size=11, font='Body', color=INK):
    c.setFillColor(HexColor(color)); c.setFont(font, size); c.drawString(x, y, s)


def para(s, x, y, width, size=10.5, leading=15, color=INK, font='Body'):
    p = Paragraph(escape(s).replace('\n', '<br/>'),
                  ParagraphStyle('body', fontName=font, fontSize=size, leading=leading, textColor=HexColor(color)))
    _, height = p.wrap(width, H); p.drawOn(c, x, y - height)
    assert y - height > 55, (s, y, height)
    return y - height


def motif(cx, cy, r):
    c.saveState(); c.setStrokeColor(HexColor('#E8D6E1')); c.setLineWidth(.55)
    for a in range(0, 360, 60):
        rad = math.radians(a); c.circle(cx + math.cos(rad) * r * .5, cy + math.sin(rad) * r * .5, r * .65, stroke=1, fill=0)
    c.circle(cx, cy, r * 1.2, stroke=1, fill=0); c.restoreState()


def base(label):
    global page
    page += 1
    c.setFillColor(HexColor(PAPER)); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(HexColor('#F0E2EB')); c.circle(W + 65, H - 90, 190, fill=1, stroke=0)
    motif(W + 8, 55, 100)
    text('ЖЕНСКИЕ ЧАКРЫ  /  КРАТКИЕ ОПИСАНИЯ', 46, 805, 7.5, color=MUTED)
    c.setStrokeColor(HexColor('#DFC8D5')); c.setLineWidth(.5); c.line(46, 43, W - 46, 43)
    text(label, 46, 28, 7, color=MUTED); text(f'{page:02d}', W - 63, 28, 8, color=MUTED)


# Cover
page += 1
c.setFillColor(HexColor(PLUM)); c.rect(0, 0, W, H, fill=1, stroke=0)
motif(W / 2, 595, 125)
text('МАТРИЦА СУДЬБЫ', 174, 775, 12, color='#A66E87')
for title, y in [('Женские', 441), ('чакры', 377)]:
    c.setFillColor(HexColor('#624257')); c.setFont('Display', 70); c.drawCentredString(W / 2, y, title)
c.setStrokeColor(HexColor(GOLD)); c.line(245, 340, 350, 340)
for s, y in [('Свадхистана · Анахата · Аджна', 298), ('Краткие описания энергий', 262)]:
    c.setFillColor(HexColor('#76596D')); c.setFont('Body', 12); c.drawCentredString(W / 2, y, s)
para('Каждая энергия — в одном предложении.\nБыстрый ориентир по трём чакрам.', 89, 190, 417, 11, 18, '#76596D')
text('СИМВОЛИЧЕСКИЙ ПРАКТИКУМ ДЛЯ САМОПОЗНАНИЯ', 98, 68, 8, color='#A66E87')
c.bookmarkPage('cover'); c.addOutlineEntry('Женские чакры — кратко', 'cover', 0); c.showPage()

# Sections
for index, (chakra, theme) in enumerate(sections):
    base(chakra)
    c.bookmarkPage('sec' + str(index)); c.addOutlineEntry(chakra, 'sec' + str(index), 0)
    text(f'0{index + 1}', 47, 747, 15, 'Body', GOLD)
    text(chakra, 86, 742, 38, 'Display')
    text(theme, 47, 714, 10, color=MUTED)
    y = 680
    for n in range(2, 23):
        desc = brief[chakra][str(n)]
        probe = Paragraph(escape(desc), ParagraphStyle('d', fontName='Body', fontSize=11, leading=15, textColor=HexColor(INK)))
        _, hh = probe.wrap(455, H)
        if y - hh < 70:
            c.showPage(); base(chakra); y = 762
        text(str(n), 46, y - 13, 20, 'Display', GOLD)
        y = para(desc, 92, y, 455, 11, 15)
        y -= 13
    c.showPage()

c.save()
with pymupdf.open(OUT) as pdf:
    full = ''.join(p.get_text() for p in pdf)
    compact = lambda v: ''.join(v.split())
    count = 0
    for chakra in brief:
        for n, desc in brief[chakra].items():
            assert compact(desc) in compact(full), (chakra, n)
            count += 1
    for p in pdf:
        for word in p.get_text('words'):
            assert word[0] >= 0 and word[1] >= 0 and word[2] <= W + 1 and word[3] <= H + 1, word
    pdf[1].get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save('/home/user/matrix-brief.png')
    print(f'Verified {count} brief descriptions across {len(pdf)} pages: {OUT}')
