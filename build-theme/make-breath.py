# Nefes ekranı görsellerini keser (amblemler + nefes al/ver çizimleri) ve breath.json'a yazar.
import sys, json, io, base64
import numpy as np, cv2
from PIL import Image, ImageDraw
A, OUT = sys.argv[1], sys.argv[2]
out = {}
def im(n): return Image.open(f"{A}/{n}-image.png").convert("RGB")
def save(name, img, width, q=80):
    if img.width > max(width, 1400): img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    b = io.BytesIO(); img.save(b, "WEBP", quality=max(q, 88), method=6)
    out[name] = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode(); img.save(f"{OUT}/{name}.png")
def circle(img, cx, cy, r):
    c = img.crop((cx-r, cy-r, cx+r, cy+r)).convert("RGBA"); m = Image.new("L", (r*8, r*8), 0)
    ImageDraw.Draw(m).ellipse((0, 0, r*8-1, r*8-1), fill=255); c.putalpha(m.resize((2*r, 2*r), Image.LANCZOS)); return c
def erase(img, boxes, lines=()):
    a = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR); m = np.zeros(a.shape[:2], np.uint8)
    for (x0, y0, x1, y1) in boxes: m[y0:y1, x0:x1] = 255
    for (x0, y0, x1, y1) in lines: cv2.line(m, (x0, y0), (x1, y1), 255, 9); cv2.circle(m, (x1, y1), 9, 255, -1)
    a = cv2.inpaint(a, m, 7, cv2.INPAINT_TELEA); return Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))
def soft(img, feather=40):
    c = img.convert("RGBA"); w, h = c.size; m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m)
    for i in range(feather): d.rounded_rectangle((i, i, w-1-i, h-1-i), radius=feather, outline=int(255 * (i + 1) / feather))
    d.rounded_rectangle((feather, feather, w-1-feather, h-1-feather), radius=feather, fill=255); c.putalpha(m); return c
# Diyafram kartı amblemleri: ladder, pulse, holdHiss, pant
for p, f, cs, r in [("g", "26470f5e", [(302,270),(791,270),(1273,270),(1759,268)], 108),
                    ("b", "e3ff967e", [(301,279),(785,279),(1266,279),(1752,279)], 112),
                    ("s", "c6ed5908", [(299,280),(789,280),(1273,280),(1755,278)], 126)]:
    src = im(f)
    for (cx, cy), n in zip(cs, ["ladder", "pulse", "holdHiss", "pant"]):
        save(f"{p}_br_{n}", circle(src, cx, cy, r), 180)
# Nefes al / ver çizimleri (yazılar silinir, dile göre uygulama yazar)
G = im("0297dc26")
G = erase(G, [(55,362,178,395),(60,568,180,600),(655,362,775,395),(655,568,770,600)], [(170,395,253,428),(175,590,248,604),(768,395,828,430),(768,590,829,604)])
save("g_anat_in", soft(G.crop((60,200,620,712))), 520); save("g_anat_out", soft(G.crop((640,200,1198,712))), 520)
B = im("78dd60cf")
B = erase(B, [(62,338,182,370),(56,545,166,578),(664,344,782,376),(664,548,776,582)], [(172,368,253,406),(160,570,246,599),(775,372,831,421),(770,575,831,586)])
save("b_anat_in", soft(B.crop((40,190,630,712))), 520); save("b_anat_out", soft(B.crop((640,190,1228,712))), 520)
M = im("3d76538c")
M = erase(M, [(55,348,192,380),(80,515,188,548),(1078,358,1198,392),(1095,520,1198,555)], [(172,366,276,393),(178,535,279,522),(1083,375,977,393),(1095,537,971,497)])
save("s_anat_in", circle(M, 366, 408, 230), 460); save("s_anat_out", circle(M, 890, 408, 230), 460)
json.dump(out, open("breath.json", "w")); print(len(out), sum(len(v) for v in out.values()) // 1024, "KB")
