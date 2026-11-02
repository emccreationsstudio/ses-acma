# Konservatuvar "Sınav Provası" başlığı: üç tema banner'ı -> çerçeve kırpılır, yazı bölgesi temiz deri ile doldurulur -> chero.json
import json, io, base64
import numpy as np, cv2
from PIL import Image
A='/mnt/user-data/attachments/56b66296-fc03-5990-a0be-6d20ea602b9c/'
# tema: dosya, çerçeve(x0,y0,x1,y1), yazı kutusu, temiz deri şeridi (y0,y1,x0,x1)
J={'s':('a40a29b9-image.png',(12,113,2125,624),(750,170,2090,575),(582,606,800,2050)),
   'g':('d8980176-image.png',(12,80,2162,618),(820,190,2080,540),(548,580,860,1960)),
   'b':('4025ab34-image.png',(22,107,2156,612),(805,180,2125,565),(570,598,840,2080))}
res={}; css=[]
for p,(f,frame,tb,ss) in J.items():
    img=cv2.imread(A+f).astype(np.float32); x0,y0,x1,y1=frame; tx0,ty0,tx1,ty1=tb
    strip=img[ss[0]:ss[1], ss[2]:ss[3]]
    tile=np.concatenate([strip,strip[::-1]],0); tile=np.concatenate([tile,tile[:,::-1]],1)
    h,w=ty1-ty0,tx1-tx0
    fill=np.tile(tile,(h//tile.shape[0]+2,w//tile.shape[1]+2,1))[:h,:w]
    orig=img[ty0:ty1,tx0:tx1]
    # hedef düşük frekans: kutunun hemen dışındaki bantlardan (yazı yok) Coons yaması
    B=14
    top=cv2.GaussianBlur(img[ty0-B:ty0, tx0:tx1],(0,0),8).mean(0); bot=cv2.GaussianBlur(img[ty1:ty1+B, tx0:tx1],(0,0),8).mean(0)
    lef=cv2.GaussianBlur(img[ty0:ty1, tx0-B:tx0],(0,0),8).mean(1); rig=cv2.GaussianBlur(img[ty0:ty1, tx1:tx1+B],(0,0),8).mean(1)
    v=np.linspace(0,1,h)[:,None,None]; u=np.linspace(0,1,w)[None,:,None]
    vert=top[None]*(1-v)+bot[None]*v; horz=lef[:,None]*(1-u)+rig[:,None]*u
    corners=(top[0][None,None]*(1-u)*(1-v)+top[-1][None,None]*u*(1-v)+bot[0][None,None]*(1-u)*v+bot[-1][None,None]*u*v)
    target=cv2.GaussianBlur(vert+horz-corners,(0,0),20)
    fb=cv2.GaussianBlur(fill,(0,0),20)
    fill=np.clip(fill-fb+target,0,255)
    m=np.ones((h,w),np.float32); e=14
    m[:e]*=np.linspace(0,1,e)[:,None]; m[-e:]*=np.linspace(1,0,e)[:,None]; m[:,:e]*=np.linspace(0,1,e)[None,:]; m[:,-e:]*=np.linspace(1,0,e)[None,:]
    img[ty0:ty1,tx0:tx1]=orig*(1-m[...,None])+fill*m[...,None]
    crop=np.clip(img[y0:y1,x0:x1],0,255).astype(np.uint8); H,W=crop.shape[:2]
    o=Image.fromarray(cv2.cvtColor(crop,cv2.COLOR_BGR2RGB))
    b=io.BytesIO(); o.save(b,'WEBP',quality=86,method=6); res[f'{p}_chero']='data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode()
    o.save(f'/tmp/claude-0/-home-claude/56b66296-fc03-5990-a0be-6d20ea602b9c/scratchpad/chero_{p}.png')
    sk={'g':'rustic','s':'mono','b':'blue'}[p]
    css.append(f'html[data-skin="{sk}"] {{ --ch-ar: {W}/{H}; --ch-tx: {100*(tx0+10-x0)/W:.1f}%; }}')
    print(p,o.size)
json.dump(res,open('chero.json','w')); open('chero-vars.css','w').write('\n'.join(css)+'\n')
