# Nefes sayfası başlığı: üç tema banner'ı -> çerçeve içi kırpılır, yazı silinir (deri ile doldurulur) -> bhero.json
import json, io, base64
import numpy as np, cv2
from PIL import Image
A='/mnt/user-data/attachments/56b66296-fc03-5990-a0be-6d20ea602b9c/'
J={'g':('73d188e8-image.png',(16,102,2160,628),(1020,206,2150,548)),
   's':('9041d646-image.png',(16,138,2160,628),(1050,206,2150,548)),
   'b':('2de66398-image.png',(22,144,2140,598),(955,206,2132,466))}
res={}; css=[]
for p,(f,frame,text) in J.items():
    img=cv2.imread(A+f); x0,y0,x1,y1=frame
    tx0,ty0,tx1,ty1=text
    # temiz deri: yazının altındaki boş şeritten (ty1..y1-25) alınıp yukarı doğru aynalanarak döşenir
    sy0=max(ty1+30, y1-28-70); src=img[sy0:y1-26, tx0:x1-22].astype(np.float32)
    src=cv2.medianBlur(src.astype(np.uint8),3).astype(np.float32)
    H=y1-26-(y0+26); tile=np.concatenate([src,src[::-1]],0)
    fill=np.tile(tile,(H//tile.shape[0]+2,1,1))[:H]
    clean=img.copy().astype(np.float32); region=clean[y0+26:y1-26, tx0:x1-22]
    # sol kenarda yumuşak geçiş (ışık izi/simge korunur)
    ww=region.shape[1]; ramp=np.clip((np.arange(ww)-0)/40.0,0,1)[None,:,None]
    region[:]=region*(1-ramp)+fill[:, :ww]*ramp
    clean=np.clip(clean,0,255).astype(np.uint8)
    crop=clean[y0:y1,x0:x1]; h,w=crop.shape[:2]
    o=Image.fromarray(cv2.cvtColor(crop,cv2.COLOR_BGR2RGB))
    b=io.BytesIO(); o.save(b,'WEBP',quality=86,method=6); res[f'{p}_bhero']='data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode()
    o.save(f'/tmp/claude-0/-home-claude/56b66296-fc03-5990-a0be-6d20ea602b9c/scratchpad/bhero_{p}.png')
    sk={'g':'rustic','s':'mono','b':'blue'}[p]
    css.append(f'html[data-skin="{sk}"] {{ --bh-ar: {w}/{h}; --bh-tx: {100*(tx0-x0)/w:.1f}%; }}')
    print(p,o.size)
json.dump(res,open('bhero.json','w')); open('bhero-vars.css','w').write('\n'.join(css)+'\n')
