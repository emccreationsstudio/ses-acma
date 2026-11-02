# Mavi tema (telefon): Kulak kartı resimleri — EDSR x4, kenarlar şeffafa yumuşak geçiş, şeffaf boşlukla küçültülür -> b_eimgp_*
import sys, json, io, base64
import numpy as np, cv2
from PIL import Image
sr=cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(sys.argv[1]); sr.setModel('edsr',4)
d=json.load(open('ear2.json'))
for k in ['note','interval','higher','chord','sing']:
    im=Image.open(io.BytesIO(base64.b64decode(d[f'b_eimg_{k}'].split(',')[1]))).convert('RGBA')
    a=np.asarray(im); h,w=a.shape[:2]
    rgb=cv2.cvtColor(a[...,:3],cv2.COLOR_RGB2BGR)[4:h-4,4:w-4]; al=a[4:h-4,4:w-4,3]
    up=cv2.cvtColor(cv2.bilateralFilter(sr.upsample(rgb),5,20,5),cv2.COLOR_BGR2RGB); H,W=up.shape[:2]
    alu=cv2.resize(al,(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32)/255
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    f=np.clip(np.minimum(xx,W-1-xx)/(W*.12),0,1)*np.clip(np.minimum(yy,H-1-yy)/(H*.14),0,1); f=f*f*(3-2*f)
    alu=alu*f
    S=1.30; tw=int(W*S); th=int(max(H*S, tw/1.6))
    can=np.zeros((th,tw,4),np.uint8); oy,ox=(th-H)//2,(tw-W)//2
    can[oy:oy+H,ox:ox+W,:3]=up; can[oy:oy+H,ox:ox+W,3]=(alu*255).astype(np.uint8)
    o=Image.fromarray(can,'RGBA')
    if o.width>900: o=o.resize((900,round(900*o.height/o.width)),Image.LANCZOS)
    b=io.BytesIO(); o.save(b,'WEBP',quality=88,method=6); d[f'b_eimgp_{k}']='data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode()
    print(k,(w,h),o.size)
json.dump(d,open('ear2.json','w'))
