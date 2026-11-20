"""Women's chakra workbook: 63 symbolic energy readings, 2–22 in three sections."""
from pathlib import Path
import csv, math, json
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'documents/Matrix_zhenskie_chakry.pdf'
actions_by_chakra={
    'Свадхистана': json.loads((ROOT/'assets/svadhisthana-actions.json').read_text()),
    'Анахата': json.loads((ROOT/'assets/anahata-actions.json').read_text()),
    'Аджна': json.loads((ROOT/'assets/ajna-actions.json').read_text()),
}
for entries in actions_by_chakra.values():
    assert set(entries)=={str(n) for n in range(2,23)}
    assert all(len(points)==3 for points in entries.values())
rows=list(csv.DictReader((ROOT/'assets/matrix-chakras.tsv').open(), delimiter='\t'))
names=['Жрица','Императрица','Император','Иерофант','Влюблённые','Колесница','Справедливость','Отшельник','Колесо Фортуны','Сила','Повешенный','Смерть','Умеренность','Дьявол','Башня','Звезда','Луна','Солнце','Суд','Мир','Шут']
sections=[('Свадхистана','Желания • удовольствие • творчество','Разрешать себе чувствовать'),('Анахата','Чувства • близость • границы','Любить, не теряя себя'),('Аджна','Восприятие • ясность • выбор','Видеть ясно и выбирать осознанно')]
for chakra,_,_ in sections:
    assert [int(r['energy']) for r in rows if r['chakra']==chakra]==list(range(2,23))
pdfmetrics.registerFont(TTFont('Display',str(ROOT/'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Bold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
W,H=595.276,841.89
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('Женские чакры • Энергии в плюс')
c.setAuthor('Практикум по матрице судьбы')
INK='#4A3F35';MUTED='#8A7A68';GOLD='#B08D57';PLUM='#F5EDDD';PAPER='#FBF7F0'
page=0

def text(s,x,y,size=11,font='Body',color=INK):
    c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,y,s)

def para(s,x,y,width,size=10.5,leading=15,color=INK,font='Body'):
    p=Paragraph(escape(s).replace('\n','<br/>'),ParagraphStyle('body',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color)))
    _,height=p.wrap(width,H);p.drawOn(c,x,y-height)
    assert y-height>55,(s,y,height)
    return y-height

def motif(cx,cy,r,dark=False):
    c.saveState();c.setStrokeColor(HexColor('#C9B18C' if dark else '#E3D5BE'));c.setLineWidth(.55)
    for a in range(0,360,60):
        rad=math.radians(a);c.circle(cx+math.cos(rad)*r*.5,cy+math.sin(rad)*r*.5,r*.65,stroke=1,fill=0)
    c.circle(cx,cy,r*1.2,stroke=1,fill=0);c.restoreState()

LEOPARD=str(ROOT/'assets/leopard-paper.png')
LEOPARD_COVER=str(ROOT/'assets/leopard-plum.png')
def leopard(x,y,w):
    c.drawImage(LEOPARD,x,y,w,w*1.499)
def base(label,leopard_w=95):
    global page
    page+=1
    c.setFillColor(HexColor(PAPER));c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(HexColor('#EFE6D4'));c.circle(W+65,H-90,190,fill=1,stroke=0)
    motif(W+8,55,100)
    leopard(W-40-leopard_w,H-38-leopard_w*1.499,leopard_w)
    text('ЖЕНСКИЕ ЧАКРЫ  /  МАТРИЦА СУДЬБЫ',46,805,7.5,color=MUTED)
    c.setStrokeColor(HexColor('#D9CBB2'));c.setLineWidth(.5);c.line(46,43,W-46,43)
    text(label,46,28,7,color=MUTED);text(f'{page:02d}',W-63,28,8,color=MUTED)

# Cover
page+=1
c.setFillColor(HexColor(PLUM));c.rect(0,0,W,H,fill=1,stroke=0)
motif(W/2,760,90,True)
text('МАТРИЦА СУДЬБЫ',174,800,12,color='#B08D57')
for title,y in [('Женские',712),('чакры',648)]:
    c.setFillColor(HexColor('#4A3F35'));c.setFont('Display',64);c.drawCentredString(W/2,y,title)
c.setStrokeColor(HexColor(GOLD));c.line(245,612,350,612)
c.drawImage(LEOPARD_COVER,W/2-115,232,230,230*1.499)
for s,y in [('Свадхистана · Анахата · Аджна',196),('Как вывести энергии в плюс',164)]:
    c.setFillColor(HexColor('#6B5D4F'));c.setFont('Body',12);c.drawCentredString(W/2,y,s)
para('Три пространства внимания к себе.\nЖелания, чувства и ясность — через небольшие ежедневные действия.',89,118,417,11,18,'#6B5D4F')
text('СИМВОЛИЧЕСКИЙ ПРАКТИКУМ ДЛЯ САМОПОЗНАНИЯ',98,52,8,color='#B08D57')
c.bookmarkPage('cover');c.addOutlineEntry('Женские чакры','cover',0);c.showPage()

base('Твоя схема • отмеченные позиции')
c.bookmarkPage('matrix');c.addOutlineEntry('Матрица с отметками','matrix',0)
text('Три точки внимания',46,745,38,'Display')
para('Ваша матрица в нежных пастельных тонах.',46,713,495,10.5,16)
from PIL import Image
photo=Image.open(ROOT/'assets/matrix-pastel.png')
iw=495;ih=iw*photo.height/photo.width
c.drawImage(str(ROOT/'assets/matrix-pastel.png'),50,168,iw,ih)
para('1 — Свадхистана: 18     •     2 — Анахата: 11\n3 — Аджна: 22',46,143,495,11,18)
para('Это ориентир по отмеченным точкам. Далее — энергии для каждой из трёх чакр, а не только числа на схеме.',46,96,495,9,14)
c.showPage()

base('Как пользоваться практикумом')
text('Твой путь к себе',46,745,38,'Display')
y=para('Здесь «вывести в плюс» означает выбрать более бережный и осознанный способ действовать, а не исправить себя или стать идеальной.',46,708,495,12,19)
y=para('Это авторские символические трактовки матрицы судьбы, а не научная оценка личности, медицинская диагностика или обещание результата. Чакры не используются здесь для определения заболеваний. Женский фокус — обращение к читательнице, а не набор обязательных женских качеств.',46,y-19,495,10.5,16)
y-=34
for i,(name,theme,_) in enumerate(sections):
    start=4+i*21
    end=start+20
    text(f'0{i+1}  {name}',46,y,22,'Display');text(f'{start}–{end}',485,y,11,color=MUTED)
    y=para(theme,46,y-12,470,10,15)-27
for s in [
'Найди число у нужной чакры в своей схеме и открой соответствующую энергию. В каждом разделе — все энергии; энергия 1 намеренно исключена. Это не индивидуальный разбор фотографии.',
'Прочитай описание как повод для размышления. Если оно не откликается, не подгоняй себя под него. Выбери одно предложенное действие и наблюдай за собственным опытом.',
'Возвращайся к практике несколько дней. Записывай: что попробовала, что почувствовала, что стало удобнее и что стоит изменить. «Блок» здесь — возможная привычка, а не диагноз.',
'Во всех трёх разделах каждой энергии посвящена отдельная страница: описание и три развёрнутых практических пункта. Выбирай подходящее, а не старайся выполнить всё сразу.']:
    y=para(s,46,y,495,10,15)-14
c.showPage()

for index,(chakra,theme,motto) in enumerate(sections):
    items=[r for r in rows if r['chakra']==chakra]
    actions=actions_by_chakra[chakra]
    for offset,row in enumerate(items):
        base(chakra+' • Энергии 2–22',140 if offset==0 else 95)
        if offset==0:
            c.bookmarkPage('section'+str(index));c.addOutlineEntry(chakra,'section'+str(index),0)
        text(f'0{index+1}',47,747,15,'Body',GOLD)
        text(chakra,86,742,38,'Display')
        text(theme,47,714,10,color=MUTED)
        top=675
        n=int(row['energy'])
        text(str(n),46,top-28,35,'Display',GOLD)
        y=top-44
        for label,field in [('В ПЛЮСЕ','plus'),('ЧТО МОЖЕТ МЕШАТЬ','block'),('КАК ВЫВЕСТИ В ПЛЮС','practice')]:
            text(label,105,y-8,7.2,'Bold',MUTED)
            y=para(row[field],105,y-16,441,10.3,14.7)-11
        assert y>top-282,(chakra,n,y,top)
        yy=y-25
        for j,action in enumerate(actions[str(n)]):
            text(f'0{j+1}',46,yy-12,17,'Display',GOLD)
            yy=para(action,82,yy,464,10.3,15.2)-18
        assert yy>100, (chakra,n,'action block too low',yy)
        footers=[
            'Твой ориентир: больше удовольствия и свободы выбора, а не больше требований к себе. Начни с одного шага.',
            'Твой ориентир: больше взаимности и тепла, без отказа от собственных границ. Начни с одного шага.',
            'Твой ориентир: больше ясности и самостоятельности, без требования знать всё заранее. Начни с одного шага.'
        ]
        para(footers[index],46,84,495,9,13,MUTED)
        c.showPage()
# Four closing pages: notes for each chakra and a final reflection (66 -> 70 pages).
for note_title, note_theme in [
    ('Заметки по Свадхистане', 'Желания • удовольствие • творчество'),
    ('Заметки по Анахате', 'Чувства • близость • границы'),
    ('Заметки по Аджне', 'Восприятие • ясность • выбор'),
]:
    base('Твои заметки')
    text(note_title, 46, 742, 34, 'Display')
    text(note_theme, 46, 712, 10, color=MUTED)
    y = 664
    while y > 92:
        c.setStrokeColor(HexColor('#D9CBB2')); c.setLineWidth(.5)
        c.line(46, y, W-46, y)
        y -= 40
    c.showPage()

base('Мои открытия и планы')
text('Мои открытия и планы', 46, 742, 34, 'Display')
para('Запиши, какие практики откликнулись сильнее всего и что ты хочешь сохранить в своей жизни.', 46, 710, 495, 11, 17)
y = 648
for prompt in [
    'Что я попробовала и что почувствовала?',
    'Какие маленькие удовольствия стали частью моей жизни?',
    'Где я стала мягче к себе и яснее в отношениях?',
    'Какой один шаг я сделаю на этой неделе?',
]:
    text(prompt, 46, y, 11, color=MUTED)
    c.setStrokeColor(HexColor('#D9CBB2')); c.setLineWidth(.5)
    c.line(46, y-30, W-46, y-30)
    y -= 118
c.showPage()
c.save()
with pymupdf.open(OUT) as pdf:
    assert len(pdf)==70,len(pdf)
    for i,(chakra,_,_) in enumerate(sections):
        extracted=''.join(p.get_text() for p in list(pdf)[3+i*21:24+i*21])
        for row in rows:
            if row['chakra']==chakra:
                compact=lambda value: ''.join(value.split())
                for field in ['plus','block','practice']:
                    assert compact(row[field]) in compact(extracted),(chakra,row['energy'],field)
    fulltext=''.join(p.get_text() for p in pdf)
    assert 'Чувственность в действиях' not in fulltext
    assert 'ПЯТЬ ШАГОВ' not in fulltext
    for name in names:
        assert name not in fulltext, ('Unexpected arcana name', name)
    for i,(chakra,_,_) in enumerate(sections):
        for n in range(2,23):
            page_text=compact(pdf[3+i*21+n-2].get_text())
            points=actions_by_chakra[chakra][str(n)]
            assert len(points)==3
            for action in points: assert compact(action) in page_text,(chakra,n,action)
    for p in pdf:
        for word in p.get_text('words'):
            assert word[0]>=0 and word[1]>=0 and word[2]<=W+1 and word[3]<=H+1,word
    pdf[3].get_pixmap(matrix=pymupdf.Matrix(1.2,1.2)).save('/home/user/matrix-preview.png')
print(f'Verified {len(rows)} readings across 70 pages: {OUT}')
