from PIL import Image
import numpy as np
from scipy import ndimage as nd
import json
im=np.asarray(Image.open('dist/campus-map.jpg').convert('RGB')).astype(int)
# Gray paved surfaces on the supplied map. Excludes colored roofs, grass, water.
raw=(im.max(2)-im.min(2)<31)&(im.min(2)>130)&(im.max(2)<245)
allowed=np.zeros(raw.shape,bool);allowed[300:1100,150:1655]=True
raw &= allowed
# Small print/anti-alias gaps only, never bridge a building or garden.
raw=nd.binary_closing(raw,iterations=2)
# Explicit footprints with pale interiors, to prevent entering courtyards through labels.
for x,y,w,h in [(1294,900,94,88),(1350,1042,120,45),(1474,991,91,100),(455,751,20,25),(1544,516,91,147),(1407,504,137,184)]:raw[y:y+h,x:x+w]=False
labels,n=nd.label(raw);target=int(labels[860,1397]);mask=labels==target
print('reachable pixels',mask.sum(),'components',n,'start component',target)
# Include only component connected to the chemistry-school street.
runs=[]
for y,row in enumerate(mask):
 d=np.diff(np.r_[False,row,False].astype(int));starts=np.where(d==1)[0];ends=np.where(d==-1)[0]
 for a,b in zip(starts,ends):runs.append([y,int(a),int(b)])
json.dump({'width':2048,'height':1228,'runs':runs},open('dist/walkable.json','w'),separators=(',',':'))
preview=np.asarray(Image.open('dist/campus-map.jpg').convert('RGB')).copy();preview[mask]=preview[mask]*.35+np.array([255,180,0])*.65
Image.fromarray(preview).save('/workspace/shared/dahua-mobile-mask-check.png')
