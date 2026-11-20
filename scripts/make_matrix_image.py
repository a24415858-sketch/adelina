"""Redraw the user's Matrix of Destiny photo as a clean pastel diagram.

Values and layout follow assets/matrix-user-annotated.jpeg; the three
circled chakra positions (Svadhisthana 18, Anahata 11, Ajna 22) are
highlighted with elegant double rings. Transparent background so the
diagram blends with the workbook page.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/matrix-pastel.png'
FONT = Path('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf')

S = 1600
img = Image.new('RGBA', (S, S), (251, 247, 240, 255))  # page colour #FBF7F0
d = ImageDraw.Draw(img)

INK = (74, 63, 53)         # #4A3F35 warm taupe text
LINE = (217, 203, 178)    # #D9CBB2 beige lines
EDGE = (176, 141, 87)     # #B08D57 bronze outline
RING = (201, 177, 140)    # #C9B18C decorative ring
FILL = (253, 251, 247)    # near-white point fill
FILL_HL = (243, 234, 217) # #F3EAD9 highlight fill
FILL_OUT = (250, 243, 230) # #FAF3E6 outer point fill

cx = cy = 800
h = 480    # square half-size
o = 170    # outer-point offset

TL = (cx - h, cy - h); TR = (cx + h, cy - h); BR = (cx + h, cy + h); BL = (cx - h, cy + h)
T = (cx, cy - h); R = (cx + h, cy); B = (cx, cy + h); L = (cx - h, cy)
CEN = (cx, cy)
OT = (cx, cy - h - o); OR = (cx + h + o, cy); OB = (cx, cy + h + o); OL = (cx - h - o, cy)
DTL = (cx - h // 2, cy - h // 2); DTR = (cx + h // 2, cy - h // 2)
DBR = (cx + h // 2, cy + h // 2); DBL = (cx - h // 2, cy + h // 2)
ET1 = (cx - h // 2, cy - h); ET2 = (cx + h // 2, cy - h)
ER1 = (cx + h, cy - h // 2); ER2 = (cx + h, cy + h // 2); EB1 = (cx + h // 2, cy + h)

lw = 2
d.line([TL, TR, BR, BL, TL], fill=LINE, width=lw)                 # square
d.ellipse([cx - h, cy - h, cx + h, cy + h], outline=LINE, width=lw)  # circle
d.line([TL, BR], fill=LINE, width=lw)                              # diagonals
d.line([TR, BL], fill=LINE, width=lw)
d.line([OT, OB], fill=LINE, width=lw)                              # vertical
d.line([OL, OR], fill=LINE, width=lw)                              # horizontal
for a, b in [(OT, TL), (OT, TR), (OR, TR), (OR, BR), (OB, BR), (OB, BL), (OL, BL), (OL, TL)]:
    d.line([a, b], fill=LINE, width=lw)                            # outer octagon

# (value, position, kind) — kind: n normal, o outer, c center, h highlighted chakra point
points = [
    ('5', OT, 'o'), ('22', OR, 'o'), ('6', OB, 'o'), ('15', OL, 'o'),
    ('20', TL, 'n'), ('9', TR, 'n'), ('10', BR, 'n'), ('21', BL, 'n'),
    ('12', CEN, 'c'),
    ('22', T, 'h'), ('7', R, 'n'), ('6', B, 'n'), ('6', L, 'n'),
    ('5', DTL, 'n'), ('21', DTR, 'n'), ('22', DBR, 'n'), ('6', DBL, 'n'),
    ('7', ET1, 'n'), ('3', ET2, 'n'), ('11', ER1, 'n'), ('5', ER2, 'n'), ('9', EB1, 'n'),
    ('17', (cx, cy - 346), 'n'),
    ('11', (cx, cy - 216), 'h'),
    ('18', (cx, cy + 376), 'h'),
    ('9', (cx - 346, cy), 'n'),
    ('21', (cx - 216, cy), 'n'),
    ('18', (cx + 216, cy), 'n'),
    ('6', (cx + 346, cy), 'n'),
    ('11', (cx + 576, cy), 'n'),
    ('14', (cx + 330, cy + 100), 'n'),
    ('7', (cx + 200, cy + 170), 'n'),
    ('7', (cx + 170, cy + 300), 'n'),
]


def draw_point(value, pos, kind):
    x, y = pos
    if kind == 'c':
        r, fill, fs = 54, FILL_HL, 52
    elif kind == 'o':
        r, fill, fs = 46, FILL_OUT, 46
    elif kind == 'h':
        r, fill, fs = 40, FILL_HL, 40
    else:
        r, fill, fs = 34, FILL, 36
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=EDGE, width=3)
    if kind == 'h':
        rr = r + 13
        d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=RING, width=2)
    font = ImageFont.truetype(str(FONT), fs)
    d.text((x, y), value, font=font, fill=INK, anchor='mm')


for value, pos, kind in points:
    draw_point(value, pos, kind)

img.save(OUT)
print('saved', OUT, img.size)
