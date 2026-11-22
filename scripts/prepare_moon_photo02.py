"""Extract the chosen 02 portrait without modifying the woman's face or hair."""
from pathlib import Path
from PIL import Image,ImageFilter
import cv2,numpy as np
R=Path(__file__).resolve().parents[1]
source=Image.open(R/'assets/moon-collage-8921.webp').convert('RGB')
w,h=source.size
im=source.crop((int(w*.667),int(h*.092),w,int(h*.276)))
rgb=np.asarray(im);h,w=rgb.shape[:2]
poly=np.array([(0,57),(14,38),(34,22),(62,13),(88,12),(113,16),(143,24),(168,33),(192,46),(214,64),(229,84),(233,103),(228,121),(217,140),(220,151),(228,165),(236,182),(242,198),(250,215),(254,230),(257,245),(260,263),(260,281),(266,303),(265,330),(272,352),(0,352)],np.int32)
seed=np.zeros((h,w),np.uint8);cv2.fillPoly(seed,[poly],255)
k=lambda n:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
inner=cv2.erode(seed,k(15));outer=cv2.dilate(seed,k(19));mask=np.full((h,w),cv2.GC_PR_BGD,np.uint8)
mask[seed>0]=cv2.GC_PR_FGD;mask[outer==0]=cv2.GC_BGD;mask[inner>0]=cv2.GC_FGD
cv2.grabCut(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),mask,None,np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),6,cv2.GC_INIT_WITH_MASK)
a=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype('uint8')
n,labels,stats,_=cv2.connectedComponentsWithStats(a,8);a=np.where(labels==1+np.argmax(stats[1:,4]),255,0).astype('uint8')
a=np.asarray(Image.fromarray(a).filter(ImageFilter.GaussianBlur(1.0))).copy()
for y in range(300,h):a[y]=(a[y].astype(float)*max(0,(h-1-y)/(h-1-300))).astype('uint8')
# Preserve the original astrological circle as a translucent backdrop behind
# the silhouette. Its rim fades naturally into the guide's marble background.
yy,xx=np.mgrid[0:h,0:w];dist=np.sqrt((xx-258.)**2+(yy-158.)**2)
wheel=np.clip((192-dist)/30.,0,1)*.68
wheel*=np.clip((w-1-xx)/20.,0,1)*np.clip(yy/18.,0,1)*np.clip((h-1-yy)/28.,0,1)
a=np.maximum(a,(wheel*255).astype('uint8'))
# Hide the collage divider on the far-left edge of the crop.
for x in range(12):a[:,x]=(a[:,x].astype(float)*(x/12)).astype('uint8')
im.putalpha(Image.fromarray(a));im.save(R/'assets/moon-photo02-transparent.png')
bg=Image.new('RGB',im.size,(205,194,186));bg.paste(im,mask=im.getchannel('A'));bg.save('/home/user/moon-photo02-cutout.png')
print('cutout',im.size,im.getbbox())
