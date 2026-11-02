# Yeni egzersiz amblemleri (telefon): mavi 05c89fdc (uclu/besli/staccato), 855ce668 (arpej/oktav/dokuzlu), altın 9f641306 (arpej/oktav/dokuzlu)
import json, io, base64, cv2, numpy as np
from PIL import Image, ImageDraw
A='/mnt/user-data/attachments/56b66296-fc03-5990-a0be-6d20ea602b9c/'
J={('b',('uclu','besli','staccato')):'05c89fdc',('b',('arpej','oktav','dokuzlu')):'855ce668',('g',('arpej','oktav','dokuzlu')):'9f641306'}
res=json.load(open('emb.json')); sheet=Image.new('RGBA',(9*130,130),(20,20,30,255)); n=0
for (p,ids),f in J.items():
    im=Image.open(A+f+'-image.png').convert('RGBA'); g=cv2.cvtColor(np.asarray(im)[...,:3],cv2.COLOR_RGB2GRAY)
    W,H=im.size; cs=cv2.HoughCircles(cv2.GaussianBlur(g,(0,0),2),cv2.HOUGH_GRADIENT,1,H/5,param1=120,param2=60,minRadius=int(W*0.17),maxRadius=int(W*0.30))[0]
    cs=sorted(cs[np.argsort(-cs[:,2])][:3].tolist(),key=lambda c:c[1])
    print(f,[tuple(int(v) for v in c) for c in cs])
    for k,(x,y,r) in zip(ids,cs):
        R=int(r*1.035); S=2
        crop=im.crop((int(x-R),int(y-R),int(x+R),int(y+R))).resize((4*R,4*R),Image.LANCZOS)
        m=Image.new('L',crop.size,0); ImageDraw.Draw(m).ellipse((5,5,crop.width-5,crop.height-5),fill=255)
        crop.putalpha(m); crop=crop.resize((256,256),Image.LANCZOS)
        b=io.BytesIO(); crop.save(b,'WEBP',quality=90,method=6)
        res[f"{p}_emb_{k}"]="data:image/webp;base64,"+base64.b64encode(b.getvalue()).decode()
        t=crop.copy(); t.thumbnail((120,120)); sheet.alpha_composite(t,(n*130+4,4)); n+=1
json.dump(res,open('emb.json','w')); sheet.save('/tmp/claude-0/-home-claude/56b66296-fc03-5990-a0be-6d20ea602b9c/scratchpad/emb2.png')
