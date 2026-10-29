# Nefes grubu amblemleri (Sakin, Kare, Uzun Sss, 4-7-8, Dudak) -> breath.json'a ekler
import sys, json, io, base64
from PIL import Image, ImageDraw, ImageFilter
A, OUT = sys.argv[1], sys.argv[2]
out = json.load(open("breath.json"))
def im(n): return Image.open(f"{A}/{n}-image.png").convert("RGB")
def save(name, img, width, q=80):
    if img.width > max(width, 1400): img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    b = io.BytesIO(); img.save(b, "WEBP", quality=max(q, 88), method=6)
    out[name] = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode(); img.save(f"{OUT}/{name}.png")
def circle(img, cx, cy, r):
    c = img.crop((cx-r, cy-r, cx+r, cy+r)).convert("RGBA"); m = Image.new("L", (r*8, r*8), 0)
    ImageDraw.Draw(m).ellipse((0, 0, r*8-1, r*8-1), fill=255); c.putalpha(m.resize((2*r, 2*r), Image.LANCZOS)); return c
def softsq(img, cx, cy, h):
    c = img.crop((cx-h, cy-h, cx+h, cy+h)).convert("RGBA"); s = 2*h
    m = Image.new("L", (s, s), 0); ImageDraw.Draw(m).ellipse((s*0.04, s*0.04, s*0.96, s*0.96), fill=255)
    c.putalpha(m.filter(ImageFilter.GaussianBlur(s*0.06))); return c
ids = ["calm", "box", "hiss", "r478", "lip"]
G = im("cf3a301f")
for n, (cx, cy) in zip(ids, [(193,173),(866,173),(1585,173),(470,488),(1235,488)]): save(f"g_br_{n}", circle(G, cx, cy, 104), 200)
M = im("05890aa0")
for n, (cx, cy, h) in zip(ids, [(192,195,118),(786,195,112),(1425,195,128),(412,512,128),(1140,512,140)]): save(f"s_br_{n}", softsq(M, cx, cy, h), 200)
B = im("57bbbcad")
for n, (cx, cy, h) in zip(ids, [(195,205,118),(822,205,112),(1478,200,128),(465,515,126),(1152,505,140)]): save(f"b_br_{n}", softsq(B, cx, cy, h), 200)
json.dump(out, open("breath.json", "w")); print(len(out))
