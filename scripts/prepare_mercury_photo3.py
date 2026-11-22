"""Extract photo 3 (woman with laptop) from the user's supplied collage."""
from pathlib import Path
from PIL import Image, ImageFilter
import cv2
import numpy as np
R=Path(__file__).resolve().parents[1]
im=Image.open(R/'assets/matrix-cover-collage.webp').convert('RGB').crop((1053,78,1502,630))
rgb=np.asarray(im);h,w=rgb.shape[:2]
# The original portrait, jacket, hands and laptop, excluding the number/background.
poly=np.array([(202,135),(206,115),(218,99),(236,88),(259,87),(284,96),(310,113),(328,133),(337,156),(338,183),(336,205),(342,216),(356,226),(375,235),(400,245),(424,254),(448,268),(448,551),(0,551),(0,375),(137,389),(139,364),(143,334),(149,302),(159,281),(177,264),(196,254),(204,240),(205,220),(202,202),(200,177),(200,151)],np.int32)
seed=np.zeros((h,w),np.uint8);cv2.fillPoly(seed,[poly],255)
k=lambda n:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
inside=cv2.erode(seed,k(19));outside=cv2.dilate(seed,k(17))
mask=np.full((h,w),cv2.GC_PR_BGD,np.uint8);mask[seed>0]=cv2.GC_PR_FGD;mask[outside==0]=cv2.GC_BGD;mask[inside>0]=cv2.GC_FGD
cv2.grabCut(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),mask,None,np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),6,cv2.GC_INIT_WITH_MASK)
a=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype('uint8')
n,lab,stats,_=cv2.connectedComponentsWithStats(a,8);a=np.where(lab==1+np.argmax(stats[1:,4]),255,0).astype('uint8')
a=np.asarray(Image.fromarray(a).filter(ImageFilter.GaussianBlur(1.2))).copy()
# Feather the cropped lower edge and the laptop's left edge; keep face intact.
for y in range(470,h):a[y]=(a[y].astype(float)*max(0,(h-1-y)/(h-1-470))).astype('uint8')
for x in range(26):a[:,x]=(a[:,x].astype(float)*(x/26)).astype('uint8')
im.putalpha(Image.fromarray(a));im=im.crop((0,75,449,552));im.save(R/'assets/mercury-photo3-transparent.png')
bg=Image.new('RGB',im.size,(194,207,217));bg.paste(im,mask=im.getchannel('A'));bg.save('/home/user/mercury-photo3-cutout.png')
