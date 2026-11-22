"""Cut out the full-length continuation of the approved cover portrait."""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageFilter
R=Path(__file__).resolve().parents[1]
im=Image.open(R/'assets/venus-fullbody-matching-cover.png').convert('RGB')
rgb=np.asarray(im);h,w=rgb.shape[:2];assert (w,h)==(848,1264)
pts=[(370,130),(405,115),(459,120),(490,139),(510,173),(520,222),(515,294),(548,316),(572,333),(588,367),(587,421),(590,475),(605,542),(606,610),(599,668),(615,700),(644,744),(648,797),(629,817),(593,817),(569,794),(555,774),(553,803),(547,875),(539,956),(529,1039),(519,1123),(510,1192),(493,1222),(469,1235),(443,1228),(435,1209),(438,1135),(442,1050),(448,963),(448,884),(445,821),(434,769),(410,750),(392,797),(367,864),(344,944),(320,1025),(297,1107),(278,1177),(265,1210),(244,1231),(220,1235),(212,1224),(219,1190),(233,1125),(248,1049),(261,973),(272,900),(281,833),(295,759),(312,702),(315,675),(315,633),(322,584),(316,552),(297,538),(283,519),(279,492),(285,460),(292,427),(293,387),(299,351),(313,325),(337,309),(340,283),(348,260),(370,248),(368,216),(371,178)]
seed=np.zeros((h,w),np.uint8);cv2.fillPoly(seed,[np.array(pts,np.int32)],255)
k=lambda n:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
inner=cv2.erode(seed,k(65));outer=cv2.dilate(seed,k(29))
mask=np.full((h,w),cv2.GC_PR_BGD,np.uint8);mask[seed>0]=cv2.GC_PR_FGD;mask[outer==0]=cv2.GC_BGD;mask[inner>0]=cv2.GC_FGD
# Compact mirror and powder pan; keep their pale interiors.
cv2.circle(mask,(567,735),19,cv2.GC_FGD,-1);cv2.circle(mask,(605,778),19,cv2.GC_FGD,-1)
# Preserve the pale left trouser leg against the similarly colored studio backdrop.
cv2.fillPoly(mask,[np.array([(282,936),(301,943),(286,1010),(269,1080),(251,1152),(241,1183),(229,1180),(242,1120),(256,1050),(269,985)],np.int32)],cv2.GC_FGD)
# Leg gap is background, even where it is similar to cream trousers.
cv2.fillPoly(mask,[np.array([(414,791),(428,797),(434,853),(435,930),(428,1000),(415,1070),(395,1140),(372,1185),(325,1205),(315,1185),(341,1110),(365,1030),(383,950),(399,870)],np.int32)],cv2.GC_BGD)
cv2.grabCut(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),mask,None,np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),7,cv2.GC_INIT_WITH_MASK)
a=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype('uint8')
n,lab,st,_=cv2.connectedComponentsWithStats(a,8);a=np.where(lab==1+np.argmax(st[1:,4]),255,0).astype('uint8')
im.putalpha(Image.fromarray(a).filter(ImageFilter.GaussianBlur(.7)));im=im.crop((200,105,660,1245))
im.save(R/'assets/venus-fullbody-matching-transparent.png')
print(im.size,im.getbbox())
