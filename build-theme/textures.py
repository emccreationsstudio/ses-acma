# Tasarım görsellerindeki düğmelerden yazıyı silip yazısız doku üretir (assets.json'a yazar).
import sys,json,io,base64
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
A,S=sys.argv[1:3]; out=json.load(open('assets.json'))
def im(n): return Image.open(f"{A}/{n}").convert("RGB")
G_LANG=im("2eccef13-image.png"); S_LANG=im("3252fdc1-image.png"); G_SET=im("ed44b164-image.png"); S_SET=im("a9eaab52-image.png")
def heal(c,t0,t1,c0,c1):
    a=np.asarray(c).astype(np.float32); h,w,_=a.shape
    # sınır sütunları (3 px ortalama)
    L=a[:,t0-4:t0-1].mean(1); R=a[:,t1+1:t1+4].mean(1)
    n=t1-t0; t=np.linspace(0,1,n)[None,:,None]
    base=L[:,None,:]*(1-t)+R[:,None,:]*t
    # yüksek frekanslı fırça dokusu: temiz parçayı yatay uzat, dikey bulanığını çıkar
    seg=Image.fromarray(a[:,c0:c1].astype(np.uint8)).resize((n,h),Image.BICUBIC)
    sg=np.asarray(seg).astype(np.float32)
    lo=np.asarray(seg.filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
    new=np.clip(base+(sg-lo)*1.0,0,255)
    pad=max(6,int(h*0.16)); wgt=np.ones((h,1,1),np.float32); wgt[:pad]=np.linspace(0,1,pad)[:,None,None]; wgt[h-pad:]=np.linspace(1,0,pad)[:,None,None]
    a[:,t0:t1]=a[:,t0:t1]*(1-wgt)+new*wgt
    return Image.fromarray(a.astype(np.uint8))
def rr(img,rad):
    c=img.convert("RGBA"); w,h=c.size; m=Image.new("L",(w*4,h*4),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w*4-1,h*4-1),radius=rad*4,fill=255); c.putalpha(m.resize((w,h),Image.LANCZOS)); return c
def save(n,img,width):
    if img.width>width: img=img.resize((width,round(img.height*width/img.width)),Image.LANCZOS)
    b=io.BytesIO(); img.save(b,"WEBP",quality=82,method=6); out[n]="data:image/webp;base64,"+base64.b64encode(b.getvalue()).decode(); return img
specs=[('g_play',G_LANG,(40,690,1495,830),400,1060,160,390,40),
       ('g_demo',G_LANG,(40,845,1495,968),470,960,160,440,36),
       ('s_play',S_LANG,(45,688,1488,828),430,1020,160,410,40),
       ('s_demo',S_LANG,(45,848,1488,966),520,930,160,500,34),
       ('g_lang_on',G_LANG,(78,108,760,208),220,470,60,210,18),
       ('g_lang_off',G_LANG,(776,108,1458,208),210,460,60,200,18),
       ('s_lang_on',S_LANG,(98,140,766,232),220,450,60,210,16),
       ('s_lang_off',S_LANG,(776,140,1432,232),215,440,60,205,16),
       ('g_seg_on',G_SET,(97,180,393,260),80,225,25,78,16),
       ('s_seg_on',S_SET,(95,195,369,275),80,205,25,78,16)]
sheet=Image.new('RGB',(1000,700),(60,90,60)); y=0;x=0;rh=0
for n,src,box,t0,t1,c0,c1,r in specs:
    m=save(n, rr(heal(src.crop(box),t0,t1,c0,c1),r), 900 if ('play' in n or 'demo' in n) else 480)
    t=m.resize((480,int(m.height*480/m.width)))
    if x+480>1000: x=0; y+=rh+6
    sheet.paste(t,(x,y),t); rh=t.height; x+=486
sheet.crop((0,0,1000,y+rh)).save(f"{S}/sheet4.png")
json.dump(out,open('assets.json','w'))
