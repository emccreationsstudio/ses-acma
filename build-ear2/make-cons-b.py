# Mavi Konservatuvar listesi simgeleri (bb23f727 tasarım görselinden) -> consb.json
import sys, json, io, base64
from PIL import Image
A, OUT = sys.argv[1], sys.argv[2]
src = open("/home/claude/sesacma-web/build-theme/make-assets2.py").read()
exec(src[:src.index('T = ["g", "s", "b"]')])
img = im("bb23f727")
B = {"c_one": (240,108,345,215), "c_two": (630,108,760,215), "c_three": (1020,108,1110,210), "c_melody": (1395,118,1660,200),
     "c_rhythm": (238,362,352,462), "c_four": (640,352,725,470), "c_sight": (1012,370,1210,456), "c_mdict": (1402,362,1590,458),
     "c_rdict": (528,618,690,742), "c_theory": (1012,622,1170,742)}
res = {}; sheet = Image.new("RGBA", (1100, 260), (20, 40, 80, 255))
for n, (k, bx) in enumerate(B.items()):
    o = cutout(img.crop(bx), lo=(14 if k == "c_four" else 30), hi=(46 if k == "c_four" else 80))
    bb = o.getchannel("A").point(lambda v: 255 if v > 90 else 0).getbbox()
    if bb: o = o.crop((max(0, bb[0]-3), max(0, bb[1]-3), min(o.width, bb[2]+3), min(o.height, bb[3]+3)))
    b = io.BytesIO(); o.save(b, "WEBP", quality=88, method=6)
    res[f"b_ei_{k}"] = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
    t = o.copy(); t.thumbnail((200, 120)); sheet.alpha_composite(t, ((n % 5) * 220, (n // 5) * 130))
json.dump(res, open("consb.json", "w")); sheet.save(f"{OUT}/consb.png"); print(len(res))
