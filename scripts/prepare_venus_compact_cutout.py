"""Create a transparent full-length cutout; preserve all generated RGB pixels."""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
im=Image.open(ROOT/'assets/venus-fullbody-compact-mirror.png').convert('RGB')
rgb=np.asarray(im);h,w=rgb.shape[:2]
assert (w,h)==(768,1376)
# Approximate the subject, mirror and lipstick; GrabCut refines the boundary.
poly=np.array([
 (330,207),(343,192),(365,181),(390,179),(415,183),(440,195),(454,214),(462,239),
 (467,275),(468,310),(466,343),(496,352),(518,364),(535,385),(547,416),
 (547,449),(541,476),(533,506),(519,538),(500,580),(492,627),(489,675),
 (498,713),(504,753),(513,815),(521,876),(531,947),(541,1015),(551,1090),
 (560,1170),(566,1232),(577,1270),(594,1286),(604,1308),(604,1327),
 (585,1330),(559,1323),(535,1311),(516,1294),(508,1271),
 (497,1216),(488,1156),(478,1094),(466,1025),(454,960),(441,892),(427,831),
 (413,790),(391,759),(377,751),(384,810),(391,886),(398,960),(406,1031),
 (413,1108),(415,1174),(414,1228),(406,1269),(393,1283),(376,1292),(354,1298),
 (339,1294),(329,1281),(322,1259),(315,1227),(308,1177),(303,1123),
 (295,1050),(288,982),(280,910),(272,839),(265,772),(263,726),(267,687),
 (267,660),(260,633),(256,606),(253,573),(253,542),(258,517),(264,495),
 (266,478),(259,466),(258,451),(259,436),(263,424),(261,413),(258,391),
 (252,369),(237,365),(224,356),(219,341),(218,320),(216,294),(218,274),
 (224,264),(238,259),(255,258),(275,259),(291,266),(300,277),(303,295),
 (305,318),(303,339),(298,355),(287,365),(289,385),(291,405),
 (286,418),(286,427),(295,411),(301,392),(306,375),(311,359),(316,342),
 (325,323),(333,311),(330,291),(329,268),(329,239)
],np.int32)
seed=np.zeros((h,w),np.uint8);cv2.fillPoly(seed,[poly],255)
k=lambda n:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(n,n))
inner=cv2.erode(seed,k(27)); outer=cv2.dilate(seed,k(21))
mask=np.full((h,w),cv2.GC_PR_BGD,np.uint8);mask[seed>0]=cv2.GC_PR_FGD
mask[outer==0]=cv2.GC_BGD;mask[inner>0]=cv2.GC_FGD
# Keep the mirror's face and centre of the clothing (which resembles the backdrop).
cv2.ellipse(mask,(262,302),(18,22),0,0,360,cv2.GC_FGD,-1)
cv2.ellipse(mask,(272,370),(17,20),0,0,360,cv2.GC_FGD,-1)
# Background between the legs and beside the compact must not inherit the old mirror seed.
cv2.fillPoly(mask,[np.array([(389,935),(402,950),(411,990),(415,1040),(417,1110),(416,1170),(407,1187),(403,1150),(400,1080),(396,1010)],np.int32)],cv2.GC_BGD)
cv2.fillPoly(mask,[np.array([(226,330),(238,336),(243,351),(241,362),(232,354)],np.int32)],cv2.GC_BGD)
cv2.grabCut(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),mask,None,np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),6,cv2.GC_INIT_WITH_MASK)
a=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype('uint8')
count,labels,stats,_=cv2.connectedComponentsWithStats(a,8)
main=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);a=np.where(labels==main,255,0).astype('uint8')
a=Image.fromarray(a).filter(ImageFilter.GaussianBlur(.8))
im.putalpha(a);im=im.crop((195,160,620,1345))
im.save(ROOT/'assets/venus-fullbody-compact-transparent.png')
print('Cutout:', im.size, im.getbbox())
