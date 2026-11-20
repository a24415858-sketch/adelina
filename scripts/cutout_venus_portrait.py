"""Remove the portrait backdrop with segmentation, not a fade or new generation.
Only the alpha channel is changed; all RGB pixels match the user's chosen image.
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
im=Image.open(ROOT/'assets/venus-user-selected-portrait.png').convert('RGB')
rgb=np.array(im);h,w=rgb.shape[:2]
outline=np.array([(190,100),(255,82),(300,62),(355,55),(407,66),(450,87),
 (476,121),(491,158),(525,189),(546,224),(553,264),(575,299),
 (569,338),(595,364),(592,400),(610,427),(604,461),(624,494),
 (720,508),(810,550),(864,589),(864,1220),(0,1220),(0,832),
 (26,757),(13,727),(27,681),(45,645),(54,609),(78,571),
 (77,532),(92,494),(90,451),(101,410),(104,370),(116,334),
 (114,290),(131,251),(143,213),(143,173),(162,136)],dtype=float)
outline*=np.array([w/864,h/1220]);outline=outline.astype(np.int32)
seed=np.zeros((h,w),np.uint8);cv2.fillPoly(seed,[outline],255)
k=lambda n:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
inner=cv2.erode(seed,k(65))
outer=cv2.dilate(seed,k(61))
mask=np.full((h,w),cv2.GC_PR_BGD,np.uint8)
mask[seed>0]=cv2.GC_PR_FGD
mask[outer==0]=cv2.GC_BGD
mask[inner>0]=cv2.GC_FGD
# All interior face, flowers and clothing are fixed foreground.
cv2.grabCut(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),mask,None,np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),7,cv2.GC_INIT_WITH_MASK)
alpha=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype('uint8')
# Remove disconnected backdrop specks, keeping the main subject.
n,labels,stats,_=cv2.connectedComponentsWithStats(alpha,8)
main=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);alpha=np.where(labels==main,255,0).astype('uint8')
# Subpixel antialiasing only, no wide blur, vignette, rectangle or bottom fade.
alpha=Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(.45))
im.putalpha(alpha)
assert np.array_equal(np.array(im)[:,:,:3],rgb)
assert np.array(alpha)[0].max()==0
out=ROOT/'assets/venus-portrait-transparent.png';im.save(out)
print(out)
