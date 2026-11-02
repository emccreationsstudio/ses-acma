# Konservatuvar kart simgeleri — kullanıcının 3 tema görselinden birebir (mono 2e88069d, altın d76f6fac, mavi cc6b2c4c) -> consm.json
import json, io, base64, numpy as np, cv2
from PIL import Image
src=open('make-cons-big.py').read()
exec(src[src.index('def soft('):src.index('def icon_box')].replace('', ''), globals())
A='/mnt/user-data/attachments/56b66296-fc03-5990-a0be-6d20ea602b9c/'
F={'s':'2e88069d','g':'d76f6fac','b':'cc6b2c4c'}
K=["c_one","c_two","c_three","c_melody","c_rhythm","c_four","c_sight","c_mdict","c_rdict","c_theory"]
# arama kutuları (2086x754 görsel ölçeğinde, başlıkların üstü / alt satırda solu)
f=2086/2000
BOX=[(40,30,300,150),(530,30,800,150),(1030,30,1300,150),(1530,30,1960,150),
     (40,292,330,408),(530,292,800,410),(1030,292,1330,410),(1530,292,1820,408),
     (485,556,668,688),(1015,556,1225,690)]
res={}; sheet=Image.new('RGBA',(10*150,3*150),(60,60,60,255))
for r,(p,fn) in enumerate(F.items()):
    im=Image.open(A+fn+'-image.png').convert('RGB'); g=np.asarray(im.convert('L')).astype(np.float32)
    for c,(k,b) in enumerate(zip(K,BOX)):
        x0,y0,x1,y1=[int(v*f) for v in b]
        sub=g[y0:y1,x0:x1]; bg=cv2.GaussianBlur(sub,(0,0),35); m=((sub-bg)>28).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,_=cv2.connectedComponentsWithStats(m)
        big_=max(st[1:,4]); C=[st[i] for i in range(1,n) if st[i,4]>max(40,big_*0.01)]
        xa=min(s_[0] for s_ in C); ya=min(s_[1] for s_ in C); xb=max(s_[0]+s_[2] for s_ in C); yb=max(s_[1]+s_[3] for s_ in C)
        P=8; X0,Y0,X1,Y1=max(0,x0+xa-P),max(0,y0+ya-P),x0+xb+P,y0+yb+P
        rgb=np.asarray(im).astype(np.float32)[Y0:Y1,X0:X1]; L=g[Y0:Y1,X0:X1]
        hh_,ww_=L.shape; yy_,xx_=np.mgrid[:hh_,:ww_]; bm=np.zeros_like(L,bool); bm[:4]=bm[-4:]=True; bm[:,:4]=bm[:,-4:]=True
        Aq=np.c_[xx_[bm],yy_[bm],np.ones(bm.sum())]; vals=L[bm]
        for _ in range(3):
            cf_,*_r=np.linalg.lstsq(Aq,vals,rcond=None); res_=vals-Aq@cf_; ok=res_<np.percentile(res_,80); Aq,vals=Aq[ok],vals[ok]
        bgv=cf_[0]*xx_+cf_[1]*yy_+cf_[2]+6
        d=L-bgv; la=np.clip((d-6)/34,0,1)
        hard=(d>16).astype(np.uint8); hard=cv2.morphologyEx(hard,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        nn_,lb,st2,_=cv2.connectedComponentsWithStats(hard); keep=np.zeros_like(hard)
        for q in range(1,nn_):
            if st2[q,4]>max(30,st2[1:,4].max()*0.01): keep[lb==q]=1
        al=np.maximum(la*cv2.dilate(keep,np.ones((3,3),np.uint8)),cv2.GaussianBlur(cv2.erode(keep,np.ones((3,3),np.uint8)).astype(np.float32),(0,0),1.0))
        o=Image.fromarray(np.dstack([rgb,np.clip(al,0,1)*255]).astype(np.uint8),'RGBA')
        S=2; o=o.resize((o.width*S,o.height*S),Image.LANCZOS)
        bb=io.BytesIO(); o.save(bb,'WEBP',quality=90,method=6)
        res[f'{p}_ecm_{k}']='data:image/webp;base64,'+base64.b64encode(bb.getvalue()).decode()
        t=o.copy(); t.thumbnail((140,140)); sheet.alpha_composite(t,(c*150+5,r*150+5))
json.dump(res,open('consm.json','w')); sheet.save('/tmp/claude-0/-home-claude/56b66296-fc03-5990-a0be-6d20ea602b9c/scratchpad/consm.png')
