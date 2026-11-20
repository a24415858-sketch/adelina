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
actions=json.loads((ROOT/'assets/svadhisthana-actions.json').read_text())
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
c.setTitle('Женские чакры • Энергии 2–22 в плюс')
c.setAuthor('Практикум по матрице судьбы')
INK='#F8ECF1';MUTED='#DBAFBF';GOLD='#ED9EB7';PLUM='#301326';PAPER='#321B30'
page=0

def text(s,x,y,size=11,font='Body',color=INK):
    c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,y,s)

def para(s,x,y,width,size=10.5,leading=15,color=INK,font='Body'):
    p=Paragraph(escape(s).replace('\n','<br/>'),ParagraphStyle('body',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color)))
    _,height=p.wrap(width,H);p.drawOn(c,x,y-height)
    assert y-height>55,(s,y,height)
    return y-height

def motif(cx,cy,r,dark=False):
    c.saveState();c.setStrokeColor(HexColor('#92506C' if dark else '#66314D'));c.setLineWidth(.55)
    for a in range(0,360,60):
        rad=math.radians(a);c.circle(cx+math.cos(rad)*r*.5,cy+math.sin(rad)*r*.5,r*.65,stroke=1,fill=0)
    c.circle(cx,cy,r*1.2,stroke=1,fill=0);c.restoreState()

def base(label):
    global page
    page+=1
    c.setFillColor(HexColor(PAPER));c.rect(0,0,W,H,fill=1,stroke=0)
    c.setFillColor(HexColor('#551C36'));c.circle(W+65,H-90,190,fill=1,stroke=0)
    motif(W+8,55,100)
    text('ЖЕНСКИЕ ЧАКРЫ  /  МАТРИЦА СУДЬБЫ',46,805,7.5,color=MUTED)
    c.setStrokeColor(HexColor('#75415B'));c.setLineWidth(.5);c.line(46,43,W-46,43)
    text(label,46,28,7,color=MUTED);text(f'{page:02d}',W-63,28,8,color=MUTED)

# Cover
page+=1
c.setFillColor(HexColor(PLUM));c.rect(0,0,W,H,fill=1,stroke=0)
motif(W/2,595,125,True)
text('МАТРИЦА СУДЬБЫ',174,775,12,color='#ED9EB7')
for title,y in [('Женские',441),('чакры',377)]:
    c.setFillColor(HexColor('#FFF0F4'));c.setFont('Display',70);c.drawCentredString(W/2,y,title)
c.setStrokeColor(HexColor(GOLD));c.line(245,340,350,340)
for s,y in [('Свадхистана · Анахата · Аджна',298),('Как вывести энергии 2–22 в плюс',262)]:
    c.setFillColor(HexColor('#EAC1CF'));c.setFont('Body',12);c.drawCentredString(W/2,y,s)
para('Три пространства внимания к себе.\nЖелания, чувства и ясность — через небольшие ежедневные действия.',89,190,417,11,18,'#EAC1CF')
text('СИМВОЛИЧЕСКИЙ ПРАКТИКУМ ДЛЯ САМОПОЗНАНИЯ',98,68,8,color='#ED9EB7')
c.bookmarkPage('cover');c.addOutlineEntry('Женские чакры','cover',0);c.showPage()

base('Твоя схема • отмеченные позиции')
c.bookmarkPage('matrix');c.addOutlineEntry('Матрица с отметками','matrix',0)
text('Три точки внимания',46,745,38,'Display')
para('Исходное фото матрицы с вашими обведёнными цифрами.',46,713,495,10.5,16)
from PIL import Image
photo=Image.open(ROOT/'assets/matrix-user-annotated.jpeg')
iw=495;ih=iw*photo.height/photo.width
c.drawImage(str(ROOT/'assets/matrix-user-annotated.jpeg'),50,168,iw,ih)
para('1 — Свадхистана: 18     •     2 — Анахата: 11\n3 — Аджна: 22',46,143,495,11,18)
para('Это ориентир по отмеченным точкам. Далее — все энергии 2–22 для каждой из трёх чакр, а не только числа на фото.',46,96,495,9,14)
c.showPage()

base('Как пользоваться практикумом')
text('Твой путь к себе',46,745,38,'Display')
y=para('Здесь «вывести в плюс» означает выбрать более бережный и осознанный способ действовать, а не исправить себя или стать идеальной.',46,708,495,12,19)
y=para('Это авторские символические трактовки матрицы судьбы, а не научная оценка личности, медицинская диагностика или обещание результата. Чакры не используются здесь для определения заболеваний. Женский фокус — обращение к читательнице, а не набор обязательных женских качеств.',46,y-19,495,10.5,16)
y-=34
for i,(name,theme,_) in enumerate(sections):
    start=[4,25,36][i]
    end=[24,35,46][i]
    text(f'0{i+1}  {name}',46,y,22,'Display');text(f'{start}–{end}',485,y,11,color=MUTED)
    y=para(theme,46,y-12,470,10,15)-27
for s in [
'Найди число у нужной чакры в своей схеме и открой соответствующую энергию. В каждом разделе есть все числа от 2 до 22; энергия 1 намеренно исключена. Это не индивидуальный разбор фотографии.',
'Прочитай описание как повод для размышления. Если оно не откликается, не подгоняй себя под него. Выбери одно предложенное действие и наблюдай за собственным опытом.',
'Возвращайся к практике несколько дней. Записывай: что попробовала, что почувствовала, что стало удобнее и что стоит изменить. «Блок» здесь — возможная привычка, а не диагноз.',
'Использована нумерация: 8 — Справедливость, 11 — Сила, 22 — Шут. В других традициях названия и порядок могут отличаться.']:
    y=para(s,46,y,495,10,15)-14
c.showPage()

for index,(chakra,theme,motto) in enumerate(sections):
    items=[r for r in rows if r['chakra']==chakra]
    step=1 if index==0 else 2
    for offset in range(0,21,step):
        base(chakra+' • Энергии 2–22')
        if offset==0:
            c.bookmarkPage('section'+str(index));c.addOutlineEntry(chakra,'section'+str(index),0)
        text(f'0{index+1}',47,747,15,'Body',GOLD)
        text(chakra,86,742,38,'Display')
        text(theme,47,714,10,color=MUTED)
        for slot,row in enumerate(items[offset:offset+step]):
            top=675-slot*289
            n=int(row['energy'])
            text(f'{n:02d}',46,top-28,35,'Display',GOLD)
            text(names[n-2],105,top-24,29,'Display')
            y=top-44
            for label,field in [('В ПЛЮСЕ','plus'),('ЧТО МОЖЕТ МЕШАТЬ','block'),('КАК ВЫВЕСТИ В ПЛЮС','practice')]:
                text(label,105,y-8,7.2,'Bold',MUTED)
                y=para(row[field],105,y-16,441,10.3,14.7)-11
            assert y>top-282,(chakra,n,y,top)
            if index!=0 and slot==0 and offset<20:
                c.setStrokeColor(HexColor('#75415B'));c.line(105,top-275,548,top-275)
        if index==0:
            text('Шик — в действиях',46,369,29,'Display')
            text('ТРИ ИДЕИ ДЛЯ ТВОЕЙ НЕДЕЛИ',46,344,8,'Bold',MUTED)
            yy=322
            for j,action in enumerate(actions[str(int(items[offset]['energy']))]):
                text(f'0{j+1}',46,yy-14,18,'Display',GOLD)
                yy=para(action,82,yy,464,10.6,16)-16
            para('Выбери одно действие и попробуй его сегодня. Шик — это внимание к себе, а не цена покупок. Заметь, что приносит удовольствие именно тебе.',46,112,495,9.5,14,MUTED)
        if index!=0 and offset==20:
            text('Небольшой шаг на неделю',46,344,28,'Display')
            para(motto+'. Выбери одну практику из своего описания. Не нужно делать всё сразу: важнее заметить, помогает ли выбранное действие именно тебе.',46,315,492,11,17)
            for yy,question in [(228,'Что я попробовала?'),(172,'Что изменилось в моих ощущениях или действиях?'),(116,'Что я хочу сохранить или изменить?')]:
                text(question,46,yy,10,color=MUTED)
                c.setStrokeColor(HexColor('#75415B'));c.line(46,yy-24,547,yy-24)
        c.showPage()
c.save()
with pymupdf.open(OUT) as pdf:
    assert len(pdf)==46,len(pdf)
    for i,(chakra,_,_) in enumerate(sections):
        extracted=''.join(p.get_text() for p in list(pdf)[[3,24,35][i]:[24,35,46][i]])
        for n in range(2,23): assert names[n-2] in extracted,(chakra,n)
    for p in pdf:
        for word in p.get_text('words'):
            assert word[0]>=0 and word[1]>=0 and word[2]<=W+1 and word[3]<=H+1,word
    pdf[3].get_pixmap(matrix=pymupdf.Matrix(1.2,1.2)).save('/home/user/matrix-preview.png')
print(f'Verified {len(rows)} readings across 46 pages: {OUT}')
