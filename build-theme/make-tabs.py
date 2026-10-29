# Alt sekme çubuğu simgeleri: her tema kendi tasarım görselinden -> tabs.json
import sys, json, io, base64
import numpy as np
from PIL import Image
A, OUT = sys.argv[1], sys.argv[2]
src = open(__file__.replace("make-tabs.py", "make-assets2.py")).read()
exec(src[:src.index('T = ["g", "s", "b"]')])
SRC = {"b": "a2c9e8ac", "g": "f868d650", "s": "7081dc18"}
boxes = {"voice": (190, 222, 385, 350), "breath": (728, 198, 915, 375), "ear": (1292, 206, 1428, 375), "cons": (1782, 220, 1990, 360)}
res = {}
sheet = Image.new("RGBA", (900, 600), (40, 40, 60, 255))
for r, (p, f) in enumerate(SRC.items()):
    img = im(f)
    for c, (k, bx) in enumerate(boxes.items()):
        o = cutout(img.crop(bx), lo=40, hi=95)
        bb = o.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
        if bb: o = o.crop((max(0, bb[0]-3), max(0, bb[1]-3), min(o.width, bb[2]+3), min(o.height, bb[3]+3)))
        b = io.BytesIO(); o.save(b, "WEBP", quality=90, method=4)
        res[f"{p}_tab_{k}"] = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
        t = o.copy(); t.thumbnail((200, 180)); sheet.alpha_composite(t, (c * 220, r * 195))
json.dump(res, open("tabs.json", "w")); sheet.save(f"{OUT}/tabs.png"); print(len(res), sum(len(v) for v in res.values())//1024, "KB")
