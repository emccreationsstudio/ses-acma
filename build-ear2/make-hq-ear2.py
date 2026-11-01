# Telefon: Aralık Tanıma + Hangisi Yüksek resimleri — EDSR x4, simge küçültülüp deri boşlukla ortalanır, kenarlar şeffaf geçiş -> g_eimgp_*
import sys, json, io, base64
import numpy as np, cv2
from PIL import Image
sr=cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(sys.argv[1]); sr.setModel('edsr',4)
d=json.load(open('ear2.json'))
for k in ['interval','higher']:
    if f'g_eimgp_{k}_src' not in d: d[f'g_eimgp_{k}_src']=d[f'g_eimgp_{k}']
    im=np.asarray(Image.open(io.BytesIO(base64.b64decode(d[f'g_eimgp_{k}_src'].split(',')[1]))).convert('RGB'))
    bgr=cv2.cvtColor(im,cv2.COLOR_RGB2BGR); h,w=bgr.shape[:2]
    reg=bgr[14:h-14,14:w-20]
    up=sr.upsample(reg); up=cv2.bilateralFilter(up,5,20,5); H,W=up.shape[:2]
    S=1.42  # simge alanın ~%70'i
    tw=int(W*S); th=int(tw/1.6)
    if th<H*1.25: th=int(H*1.25); tw=int(th*1.6)
    # deri: resmin kendi zemininden (kenar şeritleri) aynalı döşeme
    edge=np.concatenate([up[:8].reshape(-1,3),up[-8:].reshape(-1,3),up[:,:8].reshape(-1,3),up[:,-8:].reshape(-1,3)]).astype(np.float32)
    base=np.median(edge,0)
    rng=np.random.default_rng(5); grain=cv2.GaussianBlur(rng.normal(0,1,(th,tw)).astype(np.float32),(0,0),1.6)*9
    canvas=np.clip(base[None,None,:]+grain[...,None],0,255)
    oy,ox=(th-H)//2,(tw-W)//2
    m=np.zeros((th,tw),np.float32); m[oy+20:oy+H-20,ox+20:ox+W-20]=1; m=cv2.GaussianBlur(m,(0,0),28)
    big=canvas.copy(); big[oy:oy+H,ox:ox+W]=up
    out=np.clip(big*m[...,None]+canvas*(1-m[...,None]),0,255).astype(np.uint8)
    yy,xx=np.mgrid[0:th,0:tw].astype(np.float32); al=np.clip(np.minimum(xx,tw-1-xx)/(tw*.10),0,1)*np.clip(np.minimum(yy,th-1-yy)/(th*.10),0,1); al=al*al*(3-2*al)
    o=Image.fromarray(np.dstack([cv2.cvtColor(out,cv2.COLOR_BGR2RGB),(al*255).astype(np.uint8)]),'RGBA')
    if o.width>900: o=o.resize((900,round(900*o.height/o.width)),Image.LANCZOS)
    b=io.BytesIO(); o.save(b,'WEBP',quality=88,method=6); d[f'g_eimgp_{k}']='data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode()
    print(k,(w,h),o.size)
json.dump(d,open('ear2.json','w'))
