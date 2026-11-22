"""Create an alpha cutout from the approved cover portrait without changing its pixels."""
from pathlib import Path
from PIL import Image, ImageFilter
import cv2,numpy as np
ROOT=Path(__file__).resolve().parents[1]
im=Image.open(ROOT/'assets/venus7-personalized.png').convert('RGB')
rgb=np.array(im); h,w=rgb.shape[:2]
poly=np.array([(624,204),(653,188),(688,179),(730,176),(778,180),(815,197),(838,224),(852,255),(861,302),(864,350),(870,400),(869,455),(864,490),(894,497),(920,510),(934,532),(941,562),(940,594),(961,607),(979,632),(989,675),(985,730),(980,780),(969,837),(964,886),(974,1023),(540,1023),(533,1000),(507,978),(493,954),(472,930),(454,903),(450,866),(457,829),(473,781),(490,735),(510,680),(525,643),(536,625),(539,601),(526,572),(516,548),(507,526),(501,502),(498,470),(502,445),(515,427),(536,412),(554,406),(573,393),(602,381),(603,364),(599,345),(598,312),(604,279),(608,249),(614,224)],np.int32)
seed=np.zeros((h,w),np.uint8);cv2.fillPoly(seed,[poly],255)
k=lambda n:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
inner=cv2.erode(seed,k(43));outer=cv2.dilate(seed,k(29))
mask=np.full((h,w),cv2.GC_PR_BGD,np.uint8);mask[seed>0]=cv2.GC_PR_FGD;mask[outer==0]=cv2.GC_BGD;mask[inner>0]=cv2.GC_FGD
cv2.grabCut(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),mask,None,np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),6,cv2.GC_INIT_WITH_MASK)
a=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype('uint8')
n,lab,st,_=cv2.connectedComponentsWithStats(a,8); main=1+np.argmax(st[1:,4]);a=np.where(lab==main,255,0).astype('uint8')
a=np.array(Image.fromarray(a).filter(ImageFilter.GaussianBlur(1.2)))
# feather at the cropped lower edge of the shirt, not around the face
for y in range(936,1024):a[y]=(a[y].astype('float')*((1023-y)/87)).astype('uint8')
# Remove a detached chair/background fragment below the sleeve and a narrow
# strip of window at the right. No RGB pixels are altered.
exclude=np.zeros((h,w),np.uint8)
cv2.fillPoly(exclude,[np.array([(435,905),(462,924),(495,940),(545,949),(580,952),(585,1023),(435,1023)],np.int32)],255)
cv2.fillPoly(exclude,[np.array([(976,560),(1004,560),(1004,899),(977,899)],np.int32)],255)
exclude=cv2.GaussianBlur(exclude,(9,9),2)
a=(a.astype('float32')*(1-exclude.astype('float32')/255)).astype('uint8')
im.putalpha(Image.fromarray(a));im=im.crop((435,160,1005,1024))
im.save(ROOT/'assets/venus-cover-transparent.png')
print('alpha extents',im.getbbox())
