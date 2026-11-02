# Üç Ses / Dört Ses ikonlarını yeniden çizer (kirişli 3 ve 4 nota), renkleri her temanın c_two ikonundan alır
import json, io, base64, cv2, numpy as np
from PIL import Image, ImageDraw
files=['consb','consbig','consph']; D={f:json.load(open(f+'.json')) for f in files}
def dec(u): return Image.open(io.BytesIO(base64.b64decode(u.split(',')[1]))).convert('RGBA')
def enc(im): b=io.BytesIO(); im.save(b,'WEBP',quality=90,method=6); return "data:image/webp;base64,"+base64.b64encode(b.getvalue()).decode()
def glyph(n):
    # küçük porte üzerinde üst üste dizili akor notaları (3 veya 4) + sap
    W,H=900,900; S=2
    m=Image.new('L',(W*S,H*S),0); d=ImageDraw.Draw(m)
    ly=[150,290,430,570,710]
    for y in ly: d.rectangle((90*S,(y-6)*S,810*S,(y+6)*S),fill=255)
    heads=[710,570,430] if n==3 else [710,570,430,290]
    cx=400
    for y in heads:
        e=Image.new('L',(220*S,170*S),0); ImageDraw.Draw(e).ellipse((22*S,36*S,198*S,134*S),fill=255); e=e.rotate(20,resample=Image.BICUBIC)
        m.paste(255,(int((cx-110)*S),int((y-85)*S)),e)
    sx=cx+76; top=heads[-1]-300
    d.rectangle(((sx-17)*S,top*S,(sx+17)*S,(heads[0]-12)*S),fill=255)
    return np.asarray(m.resize((W,H),Image.LANCZOS)).astype(np.float32)/255
def lut_from(im):
    a=np.asarray(im).astype(np.float32); al=a[...,3]>200; px=a[al][:,:3]
    L=px@np.array([.3,.59,.11]); o=np.argsort(L); px=px[o]; L=L[o]
    q=np.linspace(0,1,64); idx=(q*(len(px)-1)).astype(int)
    cols=np.array([px[max(0,i-20):i+21].mean(0) for i in idx]); return q,cols
def shade(M,lut):
    h=cv2.GaussianBlur(cv2.distanceTransform((M>0.5).astype(np.uint8),cv2.DIST_L2,5).astype(np.float32),(0,0),3)
    h=np.minimum(h,14); gy,gx=np.gradient(cv2.GaussianBlur(h,(0,0),2))
    nz=np.ones_like(gx)*2.2; nl=np.sqrt(gx**2+gy**2+nz**2); nx,ny,nzn=-gx/nl,-gy/nl,nz/nl
    l=np.array([-0.45,-0.6,0.66]); l/=np.linalg.norm(l)
    diff=np.clip(nx*l[0]+ny*l[1]+nzn*l[2],0,1)
    spec=np.clip(nx*l[0]+ny*l[1]+nzn*l[2],0,1)**28
    Hh=M.shape[0]; vg=np.linspace(1.08,0.82,Hh)[:,None]
    I=np.clip(0.06+0.9*diff**1.4*vg+0.7*spec,0,1)
    q,cols=lut; rgb=np.stack([np.interp(I,q,cols[:,i]) for i in range(3)],-1)
    sh=cv2.GaussianBlur(M,(0,0),6); sh=np.roll(np.roll(sh,6,0),4,1)*0.55
    al=np.clip(M+sh*(1-M),0,1); rgb=rgb*(M/np.maximum(al,1e-3))[...,None]
    return Image.fromarray(np.dstack([np.clip(rgb,0,255),al*255]).astype(np.uint8),'RGBA')
G={3:glyph(3),4:glyph(4)}
sheet=Image.new('RGBA',(17*140,150),(40,40,40,255)); i=0
for f in files:
    for k in list(D[f]):
        if 'c_three' not in k and 'c_four' not in k: continue
        n=3 if 'c_three' in k else 4
        ref=dec(D[f][k.replace('c_three','c_two').replace('c_four','c_two')]); old=dec(D[f][k])
        im=shade(G[n],lut_from(ref))
        bb=im.getbbox(); im=im.crop(bb)
        tw=max(old.size)*2 if max(old.size)<200 else 420
        im=im.resize((tw,int(tw*im.height/im.width)),Image.LANCZOS)
        D[f][k]=enc(im); t=im.copy(); t.thumbnail((130,130)); sheet.alpha_composite(t,(i*140+5,5)); i+=1
for f in files: json.dump(D[f],open(f+'.json','w'))
A2='../build-theme/assets2.json'; AS=json.load(open(A2))
for p in 'gs':
    base=dec(AS[f'{p}_ei_c_two']); B=base.resize((512,512),Image.LANCZOS); a=np.asarray(B).astype(np.float32)
    rgb=a[...,:3]; L=rgb@np.array([.3,.59,.11]); yy,xx=np.mgrid[:512,:512]; r=np.hypot(xx-256,yy-256)
    glyphm=((L>70)&(r<185)).astype(np.uint8)*255; glyphm=cv2.dilate(glyphm,np.ones((17,17),np.uint8))
    lut=lut_from(Image.fromarray(np.dstack([rgb,(glyphm>0)*255]).astype(np.uint8),'RGBA'))
    clean=cv2.inpaint(rgb.astype(np.uint8),glyphm,9,cv2.INPAINT_TELEA)
    clean=np.where(glyphm[...,None]>0,cv2.GaussianBlur(clean,(0,0),10),clean)
    bg=Image.fromarray(np.dstack([clean,a[...,3]]).astype(np.uint8),'RGBA')
    for n,k in ((3,'c_three'),(4,'c_four')):
        g=shade(G[n],lut); g=g.crop(g.getbbox()); sc=300/max(g.size); g=g.resize((int(g.width*sc),int(g.height*sc)),Image.LANCZOS)
        o=bg.copy(); o.alpha_composite(g,((512-g.width)//2+6,(512-g.height)//2)); o=o.resize((256,256),Image.LANCZOS)
        AS[f'{p}_ei_{k}']=enc(o); t=o.copy(); t.thumbnail((130,130)); sheet.alpha_composite(t,(i*140+5,5)); i+=1
json.dump(AS,open(A2,'w'))
sheet.save('/tmp/claude-0/-home-claude/56b66296-fc03-5990-a0be-6d20ea602b9c/scratchpad/c34new.png')
