"""Create a 111-page Mercury guide, structured like the user's Moon guide."""
from pathlib import Path
from io import BytesIO
from xml.sax.saxutils import escape
from PIL import Image,ImageOps
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import pymupdf
from mercury_guide_content import SIGNS,HOUSES,TOPICS,TOPIC_NOTES,PRACTICES,ELEMENTS,THEMES,DEEP,QUESTIONS,PLANETS,ASPECTS
R=Path(__file__).resolve().parents[1]
OUT=R/'documents/Merkuriy_polny_gayd.pdf'; BG=R/'assets/mercury-sky-interior.jpg'
W,H=595.276,841.89
pdfmetrics.registerFont(TTFont('Display',str(R/'assets/CormorantGaramond.ttf')))
pdfmetrics.registerFont(TTFont('Body',str(R/'assets/Montserrat-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Zodiac','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
INK=HexColor('#294C65');ACCENT=HexColor('#446C86');LIGHT=HexColor('#91A6B5')
im=ImageOps.fit(Image.open(BG).convert('RGB'),(1190,1684),method=Image.Resampling.LANCZOS)
def make_bg(veil):
    b=BytesIO();Image.blend(im,Image.new('RGB',im.size,(247,250,252)),veil).save(b,'JPEG',quality=90,optimize=True);b.seek(0);return ImageReader(b)
cover_bg=make_bg(.45);inner_bg=make_bg(.84)
c=canvas.Canvas(str(OUT),pagesize=(W,H),pageCompression=1)
c.setTitle('Меркурий — полный гайд');c.setAuthor('Практикум по астрологии')
page=0

def string(t,x,y,size=10,font='Body',color=INK):c.setFillColor(color);c.setFont(font,size);c.drawString(x,y,t)
def center(t,x,y,size=10,font='Display',color=INK):c.setFillColor(color);c.setFont(font,size);c.drawCentredString(x,y,t)
def right(t,x,y,size=10,font='Body',color=INK):c.setFillColor(color);c.setFont(font,size);c.drawRightString(x,y,t)
def rule(x1,y,x2):c.setStrokeColor(LIGHT);c.setLineWidth(.55);c.line(x1,y,x2,y)
def para(t,x,y,width=499,size=11.4,leading=17.4,color=INK):
    p=Paragraph(escape(t),ParagraphStyle('body',fontName='Body',fontSize=size,leading=leading,textColor=color,allowWidows=0,allowOrphans=0))
    _,h=p.wrap(width,H);p.drawOn(c,x,y-h)
    assert y-h>48,(page,t[:70],y-h)
    return y-h

def base(kicker,title,sub=None,bookmark=None):
    global page
    page+=1;c.drawImage(inner_bg,0,0,W,H)
    string('MERCURY  /  ПОЛНЫЙ ГАЙД',46,803,7.8,color=ACCENT)
    right(f'{page:02}',W-46,802,9,'Body',ACCENT);rule(46,790,W-46)
    string(kicker.upper(),46,757,8.5,color=ACCENT)
    # Shrink only unusually long headings so they never overrun the page.
    title_size=35
    while pdfmetrics.stringWidth(title,'Display',title_size)>W-92:title_size-=1
    string(title,46,716,title_size,'Display',INK)
    y=690
    if sub:
        string(sub,47,y,16,'Display',ACCENT);y-=25
    rule(46,y,W-46);y-=23
    if bookmark:c.bookmarkPage(bookmark);c.addOutlineEntry(title,bookmark,0)
    return y

def label(s,y):string(s.upper(),47,y,8.8,'Body',ACCENT);return y-16

def entry(head,body,y,gap=15):
    y=label(head,y);return para(body,47,y,501)-gap

def end():c.showPage()

cases=['Овне','Тельце','Близнецах','Раке','Льве','Деве','Весах','Скорпионе','Стрельце','Козероге','Водолее','Рыбах']
# Cover.
page=1;c.drawImage(cover_bg,0,0,W,H)
string('MERCURY  /  PERSONAL GUIDE',42,797,8,color=ACCENT);rule(42,781,W-42)
center('МЕРКУРИЙ',W/2,599,57,'Display');center('полный гайд',W/2,559,28,'Display')
rule(W/2-70,535,W/2+70)
center('МЫШЛЕНИЕ  ·  ОБЩЕНИЕ  ·  ОБУЧЕНИЕ',W/2,505,9,'Body',ACCENT)
c.bookmarkPage('cover');c.addOutlineEntry('Меркурий — полный гайд','cover',0);end()
# Contents, page 2.
y=base('Содержание','Что внутри',bookmark='contents')
for h,t in [('03','Введение: что такое Меркурий'),('04–15','Меркурий в знаках: 12 стилей мышления'),('16–18','Знаки — краткий обзор'),('19–30','Меркурий в домах'),('31–35','Аспекты Меркурия'),('36–89','18 тем Меркурия: значения и все 12 знаков'),('90–93','Практики для ясности и общения'),('94–97','Меркурий в стихиях'),('98–105','Повседневность, вопросы и важные темы'),('106–111','Дневник, планы и заключение')]:
    string(h,47,y-4,12,'Display',ACCENT);y=para(t,116,y,427,11.5,17)-12
end()
# Intro.
y=base('Введение','Что такое Меркурий',bookmark='intro')
for h,t in [
('Значение','В астрологической традиции Меркурий связывают с мышлением, обучением, речью, обменом информацией и повседневными связями. Знак описывает символический стиль, дом — область жизни, а аспекты — связи с другими планетами.'),
('Как читать гайд','Сначала найдите знак Меркурия в натальной карте, затем посмотрите дом и аспекты. Для домов важно точное время рождения; без него интерпретация положения по домам может быть ненадёжной.'),
('Как использовать','Это символический инструмент самонаблюдения, а не научный тест интеллекта, диагноз или предсказание. Описание не определяет ваши способности: учитывайте опыт, обстоятельства и личный выбор.'),
('В плюс','Развивать Меркурий здесь значит тренировать ясность, любопытство, внимательное слушание и комфортный ритм работы с информацией. Начните с одного подходящего действия.')]:y=entry(h,t,y,16)
end()
# Sign pages.
for i,(name,sym,el,thinking,speech,learn,strength,risk,action,rest) in enumerate(SIGNS):
    y=base('Меркурий в знаках',f'Меркурий в {cases[i]}',f'{el}  ·  мышление и общение',f'sign-{i}')
    for h,t in [('Мышление',f'Такой стиль символически {thinking}. Это может быть удобным способом начинать рассуждение, а не обязательным описанием каждого решения.'),('Общение',f'В диалоге человек часто {speech}. Полезно учитывать ситуацию и проверять, как собеседник понял основную мысль.'),('Обучение',f'В этом подходе человек нередко {learn}. Экспериментируйте с форматами и выбирайте тот, который работает сейчас.'),('Сильная сторона',f'Возможный ресурс — {strength}. Он раскрывается, когда есть место для практики и обратной связи.'),('Что может мешать',f'При напряжении стоит заметить: {risk}. Это не недостаток личности, а сигнал замедлиться и уточнить задачу.'),('Как вывести в плюс',f'Попробуйте {action}. Для восстановления внимания можно {rest}.')]:y=entry(h,t,y,11)
    end()
# Brief overview, four signs per page.
for start in range(0,12,4):
    y=base('Краткий обзор','Меркурий в знаках',f'Знаки {start+1}–{start+4}',f'overview-{start}')
    for j in range(start,start+4):
        name,sym,el,thinking,speech,learn,strength,risk,action,rest=SIGNS[j]
        y=label(f'{name}  /  {el}',y)
        y=para(f'Мышление: {thinking}. В общении {speech}. Ресурс — {strength}; полезный шаг — {action}.',47,y,501,11.7,18)-24
    end()
# Houses.
for n,title,body,action,caution in HOUSES:
    y=base('Меркурий в домах',f'Меркурий в {n} доме',title,f'house-{n}')
    for h,t in [('Сфера проявления',body),('Как это может проявляться','Этот дом показывает область, в которой могут быть заметны вопросы, обучение и обмен сведениями. Проявление зависит от всей карты и жизненных обстоятельств, а не только от номера дома.'),('Сильная сторона',f'Внимание к теме «{title.lower()}» помогает задавать вопросы и находить подходящие способы взаимодействия.'),('На что обратить внимание',f'Полезно {caution}. Уточняйте, что действительно происходит, прежде чем делать вывод.'),('Как вывести в плюс',f'Попробуйте {action}. Выберите небольшой шаг и посмотрите, подходит ли он именно вам.')]:y=entry(h,t,y,19)
    end()
# Aspect pages: natal constraints are important, especially Mercury–Sun/Venus.
for idx,(title,symbol,meaning,approach) in enumerate(ASPECTS):
    y=base('Аспекты Меркурия',title,'Связи с другими планетами',f'aspect-{idx}')
    y=para(f'В астрологической интерпретации {meaning}. Полезно {approach}. Аспект описывает символическое взаимодействие, а не предопределённое событие.',47,y,501,11.2,16.5)-13
    planets=list(PLANETS)
    if title=='Соединение':planets=[('Солнце','самовыражения и личного направления','слова помогают выразить свою позицию','отделять идею от оценки личности'),('Венера','ценностей и взаимодействия','такт помогает обсуждать разные взгляды','говорить о своих предпочтениях прямо')]+planets
    if title=='Секстиль':planets=[('Венера','ценностей и взаимодействия','такт помогает обсуждать разные взгляды','говорить о своих предпочтениях прямо')]+planets
    for planet,concept,resource,advice in planets:
        descriptions={
            'Соединение':f'Взаимодействие с темой {concept} заметнее: {resource}. Полезно {advice}.',
            'Трин':f'Может легче получаться следующее: {resource}. Чтобы ресурс работал осознанно, полезно {advice}.',
            'Секстиль':f'Есть возможность развить связь общения с темой {concept}: {resource}. Стоит {advice}.',
            'Оппозиция':f'Возможны колебания между логикой и темой {concept}. Для баланса полезно {advice}.',
            'Квадрат':f'В напряжении тема {concept} может требовать гибкости. Полезно {advice}.',
        }
        y=para(f'{planet}. {descriptions[title]}',47,y,501,10.2,14.5)-4
    if title=='Соединение':note='Меркурий находится близко к Солнцу: соединение возможно, но точность аспекта и его трактовка зависят от карты.'
    elif title=='Секстиль':note='Меркурий не образует натальный секстиль с Солнцем: их видимое угловое удаление ограничено. Секстиль с Венерой возможен не во всех картах.'
    else:note='В натальной карте Меркурий не образует этот аспект с Солнцем или Венерой: их взаимное видимое угловое удаление ограничено.'
    y=para(note,47,y-6,501,9.7,14,ACCENT)
    end()
# 18 themes, three pages for each: meaning, signs 1–6, signs 7–12.
def sign_topic(k,s):
    name,sym,el,thinking,speech,learn,strength,risk,action,rest=s
    variants=[
      f'Мыслительный стиль: {thinking}. Ресурс — {strength}. Возможная сложность: {risk}.',
      f'Внимание часто направлено туда, где человек {thinking}. Для баланса можно {action}.',
      f'Человек нередко {learn}. Полезно учитывать свой темп и не сравнивать первый опыт с чужим результатом.',
      f'В потоке сведений человек {thinking}. Чтобы не поспешить с трактовкой, стоит {action}.',
      f'Лучше закреплять материал в том формате, в котором человек {learn}. Сохраните короткий конспект или пример.',
      f'В речи человек {speech}. Проверяйте, понятна ли главная мысль адресату, и при необходимости уточняйте.',
      f'Любопытство проявляется через то, как человек {thinking}. Открытый вопрос помогает не застрять в первой версии.',
      f'В переписке человек обычно {speech}. Перед отправкой полезно {action}, а затем проверить конкретику просьбы.',
      f'В диалоге ресурсом становится {strength}. При слушании полезно {action} и уточнить услышанное.',
      f'В общении человек {speech}; сильная сторона — {strength}. Важно оставить место и своей мысли, и ответу другого.',
      f'На переговорах человек {speech}. Чтобы договорённость была ясной, стоит {action} и записать условия.',
      f'Для проверки фактов опора — {strength}. Возможная сложность: {risk}. Сверьте вывод с источником.',
      f'При выборе человек {thinking}. Для более ясного решения полезно {action} и заранее определить срок.',
      f'Сведения легче воспринимаются, когда человек {learn}. При перегрузке можно {rest}.',
      f'В работе помогает {strength}. Для удобного ритма попробуйте {action} и завершить одну задачу прежде следующей.',
      f'Новые идеи возникают, когда человек {thinking}. Сохраните возможность экспериментировать и позже проверяйте детали.',
      f'В напряжённом разговоре человек {speech}. Возможная сложность: {risk}. Полезно замедлиться и переспросить.',
      f'Ваш ресурс — {strength}. В качестве бережной практики попробуйте {action}, а при усталости — {rest}.',
    ]
    return variants[k]
for k,((title,meaning,focus,exercise),(note1,note2)) in enumerate(zip(TOPICS,TOPIC_NOTES)):
    y=base('Основы Меркурия',f'{k+1}. {title}',bookmark=f'topic-{k}')
    for h,t in [('Значение',f'В этой теме Меркурий символически описывает {meaning}. Это способ рассмотреть привычки общения и мышления, а не измерение способностей.'),('Как проявляется',note1),('На что обратить внимание',f'В повседневности полезно {focus}. {note2}'),('Как вывести в плюс',exercise)]:y=entry(h,t,y,22)
    end()
    for first in [0,6]:
        y=base('Основы Меркурия',f'{k+1}. По знакам',f'{title}  ·  {first+1}–{first+6}')
        for j in range(first,first+6):
            y=label(f'{SIGNS[j][0]}',y)
            y=para(sign_topic(k,SIGNS[j]),47,y,501,11,16.3)-15
        end()
# Practices 90–93.
for i,(title,body) in enumerate(PRACTICES):
    y=base('Практика',title,bookmark=f'practice-{i}')
    y=entry('Зачем',body,y,21)
    y=entry('Попробуйте', ['Выберите удобное время и один пример из дня. Записывайте мысли так, как удобно вам: словами, списком или короткой схемой.','Перед разговором проверьте, чего вы хотите попросить. Не торопитесь заполнять паузу: ответ другого человека тоже важен.','Начните с доступного объёма и повторите упражнение в другой день. Если формат не подошёл, поменяйте его без самокритики.','После паузы оставьте только те источники, которые помогают задаче. Вы можете менять режим уведомлений в зависимости от обстоятельств.'][i],y,22)
    y=entry('Отметьте', 'Что оказалось полезным? Что хочется изменить в следующий раз? Один наблюдаемый результат важнее попытки выполнить всё идеально.',y,18)
    end()
# Elements 94–97.
for i,(title,signs,body) in enumerate(ELEMENTS):
    y=base('Меркурий в стихиях',title,signs,f'element-{i}')
    y=entry('Общий подход',body,y,22)
    y=entry('Как использовать', 'Стихия добавляет общий язык для сравнения знаков, но не отменяет различий между ними. Вернитесь к странице своего знака и выберите то, что откликается вашему опыту.',y,22)
    y=entry('Практика','Запишите свою сильную сторону в разговоре и один способ сделать её гибче. Проверьте новый подход в спокойной повседневной ситуации.',y,22);end()
# Three themes 98–100.
for title,body in THEMES:
    y=base('Меркурий в жизни',title)
    y=entry('О чём это',body,y,22)
    y=entry('Вопрос к себе','Что в этой сфере уже помогает мне понимать других и быть понятой? Какая небольшая настройка сделает общение или работу с информацией удобнее?',y,20)
    y=entry('Небольшой шаг','Выберите одно конкретное действие на ближайшие дни. После него отметьте результат и при необходимости измените подход.',y,18);end()
# Questions 101.
y=base('Вопросы','Вопросы к себе')
for q in QUESTIONS:
    string('•',48,y-3,12,'Zodiac',ACCENT);y=para(q,68,y,478,11.2,17)-13
end()
# Further topics 102–105.
for title,body in DEEP:
    y=base('Глубже',title)
    y=entry('Суть',body,y,24)
    y=entry('Наблюдение','Замечайте свой опыт без оценки: что добавляет ясности, а что создаёт лишнюю спешку? Необязательно следовать каждому описанию буквально.',y,24)
    y=entry('Попробуйте','Выберите одну небольшую перемену и дайте себе время заметить её эффект. Оставьте то, что поддерживает вас, а остальное адаптируйте.',y,20);end()
# Four journaling pages; purposeful writing space, not blank.
for i in range(4):
    y=base('Дневник','Дневник Меркурия',f'Страница {i+1} из 4')
    y=para('Запишите мысли, вопросы и наблюдения: что помогло вам выразиться яснее, чему вы научились и какую идею хотите проверить.',47,y,501,11.2,17)-28
    while y>105:
        rule(47,y,W-47);y-=39
    end()
# Plans 110.
y=base('Планы','Мои открытия и планы')
y=para('Соберите свои наблюдения и выберите один комфортный шаг на ближайшую неделю.',47,y,501,11.5,17)-28
for q in ['Что я узнала о своём способе думать?','Какая практика общения оказалась полезной?','Что я хочу проверить или изучить дальше?','Какой один шаг я сделаю на этой неделе?']:
    y=para(q,47,y,501,11,17)-30;rule(47,y,W-47);y-=55
end()
# Closing 111.
y=base('Заключение','Ваш голос имеет значение')
for h,t in [('Главное','Ваш способ мыслить и говорить может меняться вместе с опытом. Описание Меркурия не определяет вас и не требует соответствовать какому-либо образу.'),('Бережная практика','Ясность рождается не из идеального ответа, а из любопытства, вопросов и готовности проверять свои выводы. Дайте себе право на паузу, черновик и новые знания.'),('Ваш следующий шаг','Сохраните то, что действительно помогает вам учиться и общаться. Возвращайтесь к гайду как к приглашению наблюдать за собой, а не как к набору обязательных правил.')]:y=entry(h,t,y,25)
end()
assert page==111,page
c.save()
with pymupdf.open(OUT) as d:
    assert len(d)==111
    for i,p in enumerate(d):
        text=p.get_text().strip();assert len(text)>30,(i+1,'empty')
        for word in p.get_text('words'):
            assert word[0]>=0 and word[1]>=0 and word[2]<=W+1 and word[3]<=H+1,(i+1,word)
    for i in range(12):assert f'Меркурий в {cases[i]}' in d[3+i].get_text()
    for i in range(12):assert f'Меркурий в {i+1} доме' in d[18+i].get_text()
    for k in range(18):
        combined=d[36+3*k].get_text()+d[37+3*k].get_text()
        for sign in SIGNS:assert sign[0].upper() in combined,(k,sign[0])
    for i in [0,1,2,3,15,18,30,31,35,36,37,89,92,100,104,105,110]:
        d[i].get_pixmap(matrix=pymupdf.Matrix(1.1,1.1)).save(f'/home/user/mercury-{i+1}.png')
    print('Verified:',len(d),'pages, 12 signs, 12 houses, 5 aspects, 18 themes × 12 signs, outlines:',len(d.get_toc()))
