"""Use the supplied reading portrait, gently remove a cropped laptop edge."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter,ImageChops
R=Path(__file__).resolve().parents[1]
im=Image.open(R/'assets/matrix-photo-reading.png').convert('RGBA')
mask=Image.new('L',im.size,0)
d=ImageDraw.Draw(mask);d.polygon([(158,369),(304,363),(304,446),(155,446)],fill=255)
mask=mask.filter(ImageFilter.GaussianBlur(3))
alpha=ImageChops.multiply(im.getchannel('A'),ImageChops.invert(mask))
im.putalpha(alpha);im.save(R/'assets/mercury-reading-photo.png')
