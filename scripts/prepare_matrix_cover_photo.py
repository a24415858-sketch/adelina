"""Cut out the woman reading from photo 1, without changing the image of her face."""
from pathlib import Path
from PIL import Image,ImageFilter
import cv2
import numpy as np
R=Path(__file__).resolve().parents[1]
im=Image.open(R/'assets/matrix-cover-collage.webp').convert('RGB').crop((68,78,528,630))
rgb=np.asarray(im);h,w=rgb.shape[:2]
# Head, arms, book and sweater; the printed number and collage borders stay out.
poly=np.array([(153,83),(168,68),(190,62),(220,67),(247,77),(267,105),(278,138),(279,166),(278,193),(301,196),(327,205),(338,220),(338,262),(342,298),(343,328),(350,356),(356,384),(353,408),(335,425),(331,443),(325,468),(305,482),(278,483),(256,480),(232,477),(208,479),(177,476),(150,468),(125,455),(105,440),(89,420),(81,399),(81,368),(87,342),(91,307),(99,267),(108,237),(121,218),(142,211),(148,191),(147,161),(146,126)],np.int32)
seed=np.zeros((h,w),np.uint8);cv2.fillPoly(seed,[poly],255)
k=lambda n:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
inside=cv2.erode(seed,k(21));outside=cv2.dilate(seed,k(17))
mask=np.full((h,w),cv2.GC_PR_BGD,np.uint8);mask[seed>0]=cv2.GC_PR_FGD;mask[outside==0]=cv2.GC_BGD;mask[inside>0]=cv2.GC_FGD
cv2.grabCut(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),mask,None,np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),7,cv2.GC_INIT_WITH_MASK)
a=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype('uint8')
n,lab,stats,_=cv2.connectedComponentsWithStats(a,8);a=np.where(lab==1+np.argmax(stats[1:,4]),255,0).astype('uint8')
a=np.asarray(Image.fromarray(a).filter(ImageFilter.GaussianBlur(1.2))).copy()
# Fade only the bottom of the sweater, not the face, hands or book.
for y in range(436,h):a[y]=(a[y].astype(float)*max(0,(500-y)/64)).astype('uint8')
im.putalpha(Image.fromarray(a));im=im.crop((65,53,370,500));im.save(R/'assets/matrix-photo-reading.png')
bg=Image.new('RGB',im.size,(187,188,197));bg.paste(im,mask=im.getchannel('A'));bg.save('/home/user/matrix-reading-cutout.png')
print(im.size,im.getbbox())
