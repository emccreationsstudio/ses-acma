# Mavi Konservatuvar liste simgeleri: telefon tasarımları 0ace6dc4 (ilk 6) + c639bb6d (son 4) -> consph.json
import sys, json, io, base64
import numpy as np, cv2
from PIL import Image
src = open("make-cons-big.py").read()
exec(src[src.index("def soft("):src.index("def icon_box(")])
A='/mnt/user-data/attachments/56b66296-fc03-5990-a0be-6d20ea602b9c/'
X=[(30,414),(440,824)]
J=[("0ace6dc4",204,["c_one","c_two"]),("0ace6dc4",683,["c_three","c_melody"]),("0ace6dc4",1171,["c_rhythm","c_four"]),
   ("c639bb6d",524,["c_sight","c_mdict"]),("c639bb6d",999,["c_rdict","c_theory"])]
res={}; sheet=Image.new('RGBA',(10*150,170),(30,58,120,255)); n=0
for f,top,ks in J:
    img=Image.open(A+f+'-image.png').convert('RGB'); g=np.asarray(img.convert('L')).astype(np.float32)
    for (x0,x1),k in zip(X,ks):
        y0,y1=top+18,top+215; sub=g[y0:y1,x0+20:x1-20]
        bg=cv2.GaussianBlur(sub,(0,0),30); m=((sub-bg)>22).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        nn,lab,st,_=cv2.connectedComponentsWithStats(m)
        C=[st[i] for i in range(1,nn) if st[i,4]>80 and not (st[i,3]<10 and st[i,2]>150)]
        xa=min(c[0] for c in C); ya=min(c[1] for c in C); xb=max(c[0]+c[2] for c in C); yb=max(c[1]+c[3] for c in C)
        bx=(x0+20+xa,y0+ya,x0+20+xb,y0+yb)
        o=soft(img,bx); b=io.BytesIO(); o.save(b,'WEBP',quality=88,method=6)
        res[f"b_ei_{k}"]="data:image/webp;base64,"+base64.b64encode(b.getvalue()).decode()
        t=o.copy(); t.thumbnail((140,150)); sheet.alpha_composite(t,(n*150+4,8)); n+=1; print(k,bx,o.size)
json.dump(res,open('consph.json','w')); sheet.save('/tmp/claude-0/-home-claude/56b66296-fc03-5990-a0be-6d20ea602b9c/scratchpad/consph.png')
