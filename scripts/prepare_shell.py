"""Remove edge-connected white background while preserving nacre highlights."""
from collections import deque
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
root = Path(__file__).resolve().parents[1]
im = Image.open(root/'assets/spiral-shell.png').convert('RGB')
a = np.array(im)
background = a.min(axis=2) >= 246
h,w = background.shape
seen = np.zeros((h,w), dtype=bool)
queue = deque()
for y,x in [(0,x) for x in range(w)]+[(h-1,x) for x in range(w)]+[(y,0) for y in range(h)]+[(y,w-1) for y in range(h)]:
    if background[y,x] and not seen[y,x]:
        seen[y,x]=True;queue.append((y,x))
while queue:
    y,x=queue.popleft()
    for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
        if 0<=yy<h and 0<=xx<w and background[yy,xx] and not seen[yy,xx]:
            seen[yy,xx]=True;queue.append((yy,xx))
alpha=Image.fromarray(np.uint8(~seen)*255).filter(ImageFilter.GaussianBlur(.65))
im.putalpha(alpha)
im.save(root/'assets/spiral-shell-cutout.png')
