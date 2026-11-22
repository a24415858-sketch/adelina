"""Subtle, non-generative retouch of the previously approved cover photograph."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
photo=Image.open(ROOT/'assets/venus-cover-shirt-clean.png').convert('RGB')
# No face, clothing, proportions or pose changes. Keep natural skin texture.
photo=ImageEnhance.Brightness(photo).enhance(1.018)
photo=ImageEnhance.Contrast(photo).enhance(1.025)
photo=ImageEnhance.Color(photo).enhance(1.025)
photo=photo.resize((photo.width*2,photo.height*2),Image.Resampling.LANCZOS)
photo=photo.filter(ImageFilter.UnsharpMask(radius=1.2,percent=38,threshold=3))
photo.save(ROOT/'assets/venus-cover-shirt-retouched.png',optimize=True)
