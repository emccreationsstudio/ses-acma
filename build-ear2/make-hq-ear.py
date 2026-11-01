# Rustik Akor Tanıma + Duyduğunu Söyle kart resimleri: EDSR x4 büyütme + simge alana tam sığsın diye deri ile genişletme -> ear2.json (g_eimg_chord, g_eimg_sing)
import sys, json, io, base64
import numpy as np, cv2
from PIL import Image
A='/mnt/user-data/attachments/56b66296-fc03-5990-a0be-6d20ea602b9c/'
MODEL=sys.argv[1]
sr=cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(MODEL); sr.setModel('edsr',4)
src=cv2.imread(A+'7bc3d73f-Rustik_alt_n_kulak_testi_aray_z_-3.png')
cards={'chord':(350,600,918,800),'sing':(942,600,1512,800)}
d=json.load(open('ear2.json'))
for k,(x0,y0,x1,y1) in cards.items():
    card=src[y0:y1,x0:x1]; h,w=card.shape[:2]
    # ayırıcı çizgiye kadar resim bölgesi (çerçeve içi)
    g=cv2.cvtColor(card,cv2.COLOR_BGR2GRAY).astype(np.float32); band=g[int(h*.25):int(h*.75)]
    col=band.mean(0); dx=max(range(int(w*.36),int(w*.55)),key=lambda x: col[x]-(col[x-6:x-2].mean()+col[x+3:x+7].mean())/2)
    reg=card[14:h-11, 30:dx-5]
    up=sr.upsample(reg); up=cv2.bilateralFilter(up,5,20,5); H,W=up.shape[:2]
    tw=int(max(W*1.04, H*1.04*1.6)); th=int(tw/1.6)
    # düz deri dokusu: başlığın üstündeki boş deri şeridinden, aynalanarak döşenir
    patch=card[16:40, dx+40:dx+220]; patch=sr.upsample(patch)
    tile=np.concatenate([patch, patch[::-1]],0); tile=np.concatenate([tile, tile[:, ::-1]],1)
    reps=(th//tile.shape[0]+2, tw//tile.shape[1]+2)
    canvas=np.tile(tile,(reps[0],reps[1],1))[:th,:tw].astype(np.float32)
    # dokuyu resmin ortalama zemin tonuna eşitle
    edge=np.concatenate([up[:6].reshape(-1,3),up[-6:].reshape(-1,3),up[:,:6].reshape(-1,3),up[:,-6:].reshape(-1,3)]).astype(np.float32)
    canvas=canvas-canvas.reshape(-1,3).mean(0)+np.median(edge,0)
    oy,ox=(th-H)//2,(tw-W)//2
    m=np.zeros((th,tw),np.float32); m[oy+18:oy+H-18,ox+18:ox+W-18]=1; m=cv2.GaussianBlur(m,(0,0),26)
    big=canvas.copy(); big[oy:oy+H,ox:ox+W]=up
    out=np.clip(big*m[...,None]+canvas*(1-m[...,None]),0,255).astype(np.uint8)
    yy,xx=np.mgrid[0:th,0:tw].astype(np.float32); fx,fy=tw*0.10,th*0.10
    al=np.clip(np.minimum(xx,tw-1-xx)/fx,0,1)*np.clip(np.minimum(yy,th-1-yy)/fy,0,1); al=al*al*(3-2*al)
    rgba=np.dstack([cv2.cvtColor(out,cv2.COLOR_BGR2RGB),(al*255).astype(np.uint8)])
    im=Image.fromarray(rgba,'RGBA')
    if im.width>900: im=im.resize((900,round(900*im.height/im.width)),Image.LANCZOS)
    b=io.BytesIO(); im.save(b,'WEBP',quality=88,method=6)
    d[f'g_eimg_{k}']='data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode()
    im.save(f'/tmp/claude-0/-home-claude/56b66296-fc03-5990-a0be-6d20ea602b9c/scratchpad/hq_{k}.png'); print(k,reg.shape,im.size)
json.dump(d,open('ear2.json','w'))
