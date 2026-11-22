"""Enlarge the supplied mirror photo with FSRCNN x4, preserving the original composition.

Model: https://github.com/Saafke/FSRCNN_Tensorflow (Apache-2.0).
Requires opencv-contrib-python-headless 4.11 and numpy < 2.
Super-resolution estimates pixels; it cannot recover detail absent from the source.
"""
from pathlib import Path
import cv2
ROOT=Path(__file__).resolve().parents[1]
sr=cv2.dnn_superres.DnnSuperResImpl_create()
sr.readModel(str(ROOT/'assets/FSRCNN_x4.pb')); sr.setModel('fsrcnn',4)
im=cv2.imread(str(ROOT/'assets/venus-cover-mirror.png'))
assert im is not None
result=sr.upsample(im)
assert cv2.imwrite(str(ROOT/'assets/venus-cover-mirror-enhanced.png'),result)
print('Super-resolution:', im.shape[:2], '->', result.shape[:2])
