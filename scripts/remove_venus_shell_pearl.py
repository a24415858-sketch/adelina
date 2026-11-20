"""Remove only the pearl inside the shell in the user's exact uploaded PDF."""
from pathlib import Path
import cv2
import numpy as np
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'assets/venus-user-reference-remove-pearl.pdf'
doc = pymupdf.open(source)
pix = pymupdf.Pixmap(doc, doc[0].get_images()[0][0])
original = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3).copy()
assert original.shape == (1491, 1055, 3)
mask = np.zeros(original.shape[:2], np.uint8)
# Local pearl and its cast shadow only; the shell rim and surrounding beads stay intact.
cv2.ellipse(mask, (857, 1334), (27, 31), 0, 0, 360, 255, -1)
repaired = cv2.inpaint(original, mask, 5, cv2.INPAINT_TELEA)
assert np.array_equal(original[mask == 0], repaired[mask == 0])
background = ROOT / 'assets/venus-background-no-shell-pearl.png'
cv2.imwrite(str(background), cv2.cvtColor(repaired, cv2.COLOR_RGB2BGR))
replaced = set()
for page in doc:
    for image in page.get_images():
        xref = image[0]
        if image[2:4] == (1055, 1491) and xref not in replaced:
            assert pymupdf.Pixmap(doc, xref).samples == pix.samples
            page.replace_image(xref, filename=str(background))
            replaced.add(xref)
output = ROOT / 'documents/Venera_bez_zhemchuzhiny.pdf'
doc.save(output, garbage=4, deflate=True)
doc.close()
with pymupdf.open(source) as before, pymupdf.open(output) as after:
    assert len(before) == len(after) == 14
    for a, b in zip(before, after):
        assert a.get_text('words') == b.get_text('words')
        # Even rendered pixels outside the small shell repair are unchanged.
        pa, pb = a.get_pixmap(), b.get_pixmap()
        aa = np.frombuffer(pa.samples, np.uint8).reshape(pa.height, pa.width, 3)
        bb = np.frombuffer(pb.samples, np.uint8).reshape(pb.height, pb.width, 3)
        outside = np.ones(aa.shape[:2], bool)
        outside[730:775, 465:505] = False
        assert np.array_equal(aa[outside], bb[outside])
print('Verified: 14 pages, identical text and all rendered pixels outside the pearl repair.')
print(output)
