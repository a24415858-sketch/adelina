from pathlib import Path
import re, html
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT/'assets/energies_2_22_user_text.md'
OUT = ROOT/'documents/Energii_2_22_zhemchuzhny_gayd.pdf'
pdfmetrics.registerFont(TTFont('Montserrat', str(ROOT/'assets/Montserrat-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Cormorant', str(ROOT/'assets/CormorantGaramond.ttf')))
W,H=A4
ink=HexColor('#344b5d'); muted=HexColor('#657b88'); gold=HexColor('#c4ad7a')
bg=Image.open(ROOT/'assets/moon-marble-pearl-background.jpg').convert('RGB')
interior=Image.blend(bg, Image.new('RGB', bg.size, (250,251,251)), .86)
cover=Image.blend(bg, Image.new('RGB', bg.size, (249,250,250)), .39)
interior_reader=ImageReader(interior); cover_reader=ImageReader(cover)
source=SOURCE.read_text()
chunks=re.split(r'(?m)^## (?=\d+ ЭНЕРГИЯ)',source)[1:]
assert len(chunks)==21
energies=[]
for n,chunk in enumerate(chunks,2):
    lines=chunk.strip().splitlines()
    title=lines[0]; assert title.startswith(f'{n} ЭНЕРГИЯ')
    m=re.search(r'(?ms)^(Главная энергия[^\n]+)\n\s*([^\n]+)',chunk); assert m,n
    parts=re.split(r'(?m)^### (\d+)\. ([^\n]+)\n',chunk)
    assert len(parts)==22,(n,len(parts))
    sections=[]
    lesson=None
    for j in range(7):
        num, name, body=parts[1+j*3:4+j*3]; assert int(num)==j+1
        points=re.findall(r'(?m)^[1-7]\. (.+)$',body); assert len(points)==7,(n,name)
        sections.append((name,points))
        if j==6:
            lm=re.search(rf'(?m)^(Главный урок {n} энергии:.+)$',body); assert lm,n
            lesson=lm.group(1)
    energies.append((n,title,m.group(1),m.group(2),sections,lesson))

c=canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
c.setTitle('Энергии 2–22 в матрице судьбы')
c.setAuthor('Гайд по энергиям матрицы судьбы')

def background(cover_page=False):
    c.drawImage(cover_reader if cover_page else interior_reader,0,0,width=W,height=H,mask='auto')

def centered(text,y,font,size,color=ink):
    c.setFillColor(color); c.setFont(font,size); c.drawCentredString(W/2,y,text)

def page_base(title, number):
    background()
    c.setFillColor(muted); c.setFont('Montserrat',8)
    c.drawString(52,H-40,'МАТРИЦА СУДЬБЫ  /  ЭНЕРГИИ 2–22')
    c.drawRightString(W-52,H-40,title)
    c.setStrokeColor(gold); c.setLineWidth(.5); c.line(52,H-50,W-52,H-50)
    c.line(52,43,W-52,43)
    c.setFillColor(muted); c.setFont('Montserrat',8); c.drawCentredString(W/2,28,str(number))

body_style=ParagraphStyle('body',fontName='Montserrat',fontSize=10.5,leading=15,textColor=ink,spaceAfter=0,allowWidows=0,allowOrphans=0)
intro_style=ParagraphStyle('intro',parent=body_style,fontSize=10.7,leading=16)
point_style=ParagraphStyle('point',parent=body_style,leftIndent=22,firstLineIndent=-22,leading=15.2)
lesson_style=ParagraphStyle('lesson',parent=body_style,fontSize=10.8,leading=16)

def para(txt,x,top,width,style):
    p=Paragraph(html.escape(txt),style); _,h=p.wrap(width,1000)
    p.drawOn(c,x,top-h)
    return top-h

def section(name,points,y):
    c.setFillColor(ink); c.setFont('Cormorant',18)
    c.drawString(58,y-16,name); y-=26
    for i,point in enumerate(points,1):
        y=para(f'{i}.  {point}',58,y,W-116,point_style)-3.4
    return y-15

# Cover
background(True)
c.setFillColor(ink); c.setFont('Montserrat',10); c.drawCentredString(W/2, H-195,'Г А Й Д   П О   М А Т Р И Ц Е   С У Д Ь Б Ы')
c.setStrokeColor(gold); c.setLineWidth(.8); c.line(W/2-105,H-218,W/2+105,H-218)
centered('Энергии',H-295,'Cormorant',56)
centered('2–22',H-365,'Cormorant',69)
centered('в матрице судьбы',H-408,'Cormorant',27)
c.showPage()

# Contents
page_base('СОДЕРЖАНИЕ',2)
c.bookmarkPage('contents'); c.addOutlineEntry('Содержание','contents',0,False)
c.setFillColor(ink); c.setFont('Cormorant',32); c.drawString(58,H-98,'Содержание')
c.setFillColor(muted); c.setFont('Montserrat',9); c.drawString(58,H-120,'Выберите энергию, чтобы перейти к её описанию')
for idx,(n,title,*_) in enumerate(energies):
    y=H-151-idx*28.5
    c.setFillColor(ink); c.setFont('Montserrat',10.5); c.drawString(60,y,title)
    c.setFillColor(muted); c.drawRightString(W-60,y,str(3+idx*3))
    c.setStrokeColor(HexColor('#d5d9d7')); c.setLineWidth(.3); c.line(60,y-7,W-60,y-7)
    c.linkAbsolute('',f'energy{n}',Rect=(55,y-7,W-55,y+16),thickness=0)
c.showPage()

for idx,(n,title,main,intro,sections,lesson) in enumerate(energies):
    pg=3+idx*3
    short=f'{n} ЭНЕРГИЯ'
    page_base(short,pg)
    c.bookmarkPage(f'energy{n}'); c.addOutlineEntry(title,f'energy{n}',0,False)
    c.setFillColor(muted); c.setFont('Montserrat',9); c.drawString(58,H-92,f'ЭНЕРГИЯ  {n:02d}')
    c.setFillColor(ink); c.setFont('Cormorant',31)
    c.drawString(58,H-129,title.split(' — ',1)[1].capitalize())
    y=H-152
    y=para(main,58,y,W-116,intro_style)-11
    y=para(intro,58,y,W-116,intro_style)-20
    for sec in sections[:2]: y=section(*sec,y)
    assert y>52,(n,'page1',y)
    c.showPage()
    page_base(short,pg+1)
    y=H-78
    for sec in sections[2:5]: y=section(*sec,y)
    assert y>52,(n,'page2',y)
    c.showPage()
    page_base(short,pg+2)
    y=H-78
    for sec in sections[5:]: y=section(*sec,y)
    y-=5
    c.setStrokeColor(gold); c.setLineWidth(.7); c.line(58,y,W-58,y); y-=18
    y=para(lesson,58,y,W-116,lesson_style)
    assert y>52,(n,'page3',y)
    c.showPage()
c.save()
print(f'Created {OUT}: {2+len(energies)*3} pages')
