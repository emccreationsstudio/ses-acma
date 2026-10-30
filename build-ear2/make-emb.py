# Egzersiz amblemleri (telefon tasarımlarından): mavi eebfc350, altın af2d0a67 -> emb.json
import json, io, base64
import numpy as np
import numpy as np
from PIL import Image, ImageDraw
A='/mnt/user-data/attachments/56b66296-fc03-5990-a0be-6d20ea602b9c/'
IDS=["uclu","besli","staccato","arpej","oktav","dokuzlu","plus"]
C={"b":("eebfc350",[(111,387,54),(112,570,52),(114,753,53),(114,936,53),(112,1120,52),(111,1301,50),(117,1485,58)]),
   "g":("af2d0a67",[(107,387,50),(107,565,52),(107,750,51),(108,931,55),(106,1111,55),(107,1294,55),(108,1474,56)])}
res={}; sheet=Image.new('RGBA',(7*130,2*130),(30,30,40,255))
for r,(p,(f,cs)) in enumerate(C.items()):
    im=Image.open(A+f+'-image.png').convert('RGBA')
    for c,(k,(x,y,rad)) in enumerate(zip(IDS,cs)):
        R=rad+5; S=4
        crop=im.crop((x-R,y-R,x+R,y+R)).resize((2*R*S,2*R*S),Image.LANCZOS)
        m=Image.new('L',crop.size,0); ImageDraw.Draw(m).ellipse((S,S,crop.width-S,crop.height-S),fill=255)
        crop.putalpha(m); crop=crop.resize((2*R*2,2*R*2),Image.LANCZOS)
        b=io.BytesIO(); crop.save(b,'WEBP',quality=88,method=6)
        res[f"{p}_emb_{k}"]="data:image/webp;base64,"+base64.b64encode(b.getvalue()).decode()
        t=crop.copy(); t.thumbnail((120,120)); sheet.alpha_composite(t,(c*130+4,r*130+4))
json.dump(res,open('emb.json','w')); sheet.save('/tmp/claude-0/-home-claude/56b66296-fc03-5990-a0be-6d20ea602b9c/scratchpad/emb.png'); print(len(res))

# Rustik: mavi metalik amblemler altın tonuna boyanır (koyu kahve -> altın -> açık altın)
pal=np.array([(0,(18,11,5)),(0.35,(92,58,22)),(0.62,(196,142,62)),(0.82,(238,200,120)),(1,(255,246,214))],dtype=object)
xs=np.array([p[0] for p in pal],float); cols=np.array([p[1] for p in pal],float)
sheet2=Image.new('RGBA',(7*130,130),(30,20,10,255))
for c,k in enumerate(IDS):
    src=Image.open(io.BytesIO(base64.b64decode(res[f"b_emb_{k}"].split(',')[1]))).convert('RGBA')
    a=np.asarray(src).astype(float); L=(a[...,:3]@np.array([.3,.59,.11]))/255
    L=np.clip((L-0.03)/0.92,0,1)**0.9
    rgb=np.stack([np.interp(L,xs,cols[:,i]) for i in range(3)],-1)
    o=Image.fromarray(np.dstack([rgb,a[...,3]]).astype(np.uint8),'RGBA')
    b=io.BytesIO(); o.save(b,'WEBP',quality=88,method=6)
    if k in ("uclu","besli","staccato"): continue
    res[f"g_emb_{k}"]="data:image/webp;base64,"+base64.b64encode(b.getvalue()).decode()
    t=o.copy(); t.thumbnail((120,120)); sheet2.alpha_composite(t,(c*130+4,4))
json.dump(res,open('emb.json','w')); sheet2.save('/tmp/claude-0/-home-claude/56b66296-fc03-5990-a0be-6d20ea602b9c/scratchpad/emb_g.png')

# Rustik: kullanıcının gönderdiği altın metalik amblemler (15545681) -> birebir
G=Image.open(A+'71416fac-image.png').convert('RGBA')
sheet3=Image.new('RGBA',(4*130,130),(30,20,10,255))
for c,(k,(x,y)) in enumerate(zip(["arpej","oktav","dokuzlu","plus"],[(362,269),(361,809),(363,1343),(363,1881)])):
    R=210; S=2
    crop=G.crop((x-R,y-R,x+R,y+R)).resize((2*R*S,2*R*S),Image.LANCZOS)
    m=Image.new('L',crop.size,0); ImageDraw.Draw(m).ellipse((6,6,crop.width-6,crop.height-6),fill=255)
    crop.putalpha(m); crop=crop.resize((240,240),Image.LANCZOS)
    b=io.BytesIO(); crop.save(b,'WEBP',quality=90,method=6)
    res[f"g_emb_{k}"]="data:image/webp;base64,"+base64.b64encode(b.getvalue()).decode()
    t=crop.copy(); t.thumbnail((120,120)); sheet3.alpha_composite(t,(c*130+4,4))
json.dump(res,open('emb.json','w')); sheet3.save('/tmp/claude-0/-home-claude/56b66296-fc03-5990-a0be-6d20ea602b9c/scratchpad/emb_g2.png')

# Parlatma: zemin koyulaşır, altın parlar, ışıltı (bloom) eklenir — ilk üç amblem gibi
import cv2
sheet4=Image.new('RGBA',(4*130,130),(30,20,10,255))
for c,k in enumerate(["arpej","oktav","dokuzlu","plus"]):
    im=Image.open(io.BytesIO(base64.b64decode(res[f"g_emb_{k}"].split(',')[1]))).convert('RGBA')
    a=np.asarray(im).astype(np.float32); rgb=a[...,:3]/255; al=a[...,3]
    L=rgb@np.array([.3,.59,.11],np.float32)
    sat=rgb.max(2)-rgb.min(2)
    gold=np.clip((L-0.30)/0.35,0,1)*np.clip(sat*3,0,1)          # altın kısımlar
    bgk=1-gold
    out=rgb*(1-bgk[...,None]*0.55)                                 # zemini koyulaştır
    out=out*(1+gold[...,None]*0.55)                                # altını parlat
    out=np.clip(out,0,1)**np.where(gold[...,None]>0.3,0.85,1.15)
    br=np.clip((L-0.55)/0.3,0,1)[...,None]*out
    bloom=cv2.GaussianBlur(br,(0,0),5)*0.9+cv2.GaussianBlur(br,(0,0),14)*0.6
    out=1-(1-out)*(1-bloom*np.array([1.0,0.72,0.32]))              # ekran karışımı, sıcak ışık
    o=Image.fromarray(np.dstack([np.clip(out,0,1)*255,al]).astype(np.uint8),'RGBA')
    b=io.BytesIO(); o.save(b,'WEBP',quality=90,method=6)
    res[f"g_emb_{k}"]="data:image/webp;base64,"+base64.b64encode(b.getvalue()).decode()
    t=o.copy(); t.thumbnail((120,120)); sheet4.alpha_composite(t,(c*130+4,4))
# karşılaştırma için ilk üç
ref=Image.new('RGBA',(7*130,130),(20,14,8,255))
for c,k in enumerate(["uclu","besli","staccato","arpej","oktav","dokuzlu","plus"]):
    t=Image.open(io.BytesIO(base64.b64decode(res[f"g_emb_{k}"].split(',')[1]))).convert('RGBA'); t.thumbnail((120,120)); ref.alpha_composite(t,(c*130+4,4))
json.dump(res,open('emb.json','w')); ref.save('/tmp/claude-0/-home-claude/56b66296-fc03-5990-a0be-6d20ea602b9c/scratchpad/emb_g3.png')
