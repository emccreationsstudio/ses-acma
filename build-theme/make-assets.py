# Tasarım görsellerinden tema parçalarını keser ve assets.json'a yazar.
# Kullanım: python3 make-assets.py <görsel klasörü> <önizleme klasörü>
import sys, json, io, base64
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
A, OUT = sys.argv[1], sys.argv[2]
out = {}
def im(n): return Image.open(f"{A}/{n}-image.png").convert("RGB")
def heal(c, t0, t1, c0, c1):
    a = np.asarray(c).astype(np.float32); h = a.shape[0]
    L = a[:, t0-4:t0-1].mean(1); R = a[:, t1+1:t1+4].mean(1)
    n = t1 - t0; t = np.linspace(0, 1, n)[None, :, None]
    base = L[:, None, :] * (1 - t) + R[:, None, :] * t
    seg = Image.fromarray(a[:, c0:c1].astype(np.uint8)).resize((n, h), Image.BICUBIC)
    sg = np.asarray(seg).astype(np.float32); lo = np.asarray(seg.filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
    new = np.clip(base + (sg - lo), 0, 255)
    pad = max(6, int(h * 0.16)); w = np.ones((h, 1, 1), np.float32)
    w[:pad] = np.linspace(0, 1, pad)[:, None, None]; w[h-pad:] = np.linspace(1, 0, pad)[:, None, None]
    a[:, t0:t1] = a[:, t0:t1] * (1 - w) + new * w
    return Image.fromarray(a.astype(np.uint8))
def rr(img, rad):
    c = img.convert("RGBA"); w, h = c.size; m = Image.new("L", (w*4, h*4), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w*4-1, h*4-1), radius=rad*4, fill=255); c.putalpha(m.resize((w, h), Image.LANCZOS)); return c
def circle(img, cx, cy, r):
    c = img.crop((cx-r, cy-r, cx+r, cy+r)).convert("RGBA"); m = Image.new("L", (r*8, r*8), 0)
    ImageDraw.Draw(m).ellipse((0, 0, r*8-1, r*8-1), fill=255); c.putalpha(m.resize((2*r, 2*r), Image.LANCZOS)); return c
def pill(img, box):
    c = img.crop(box); return rr(c, c.height // 2)
def save(name, img, width=None, q=82):
    if width and img.width > max(width, 1400): img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    b = io.BytesIO(); img.save(b, "WEBP", quality=max(q, 88), method=6)
    out[name] = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
    img.save(f"{OUT}/{name}.png")
def ring(img, cx, cy, r, col, glow):
    c = circle(img, cx, cy, r); d = ImageDraw.Draw(c); inner = int(r * 0.80)
    d.ellipse((r-inner, r-inner, r+inner, r+inner), fill=col)
    g = Image.new("RGBA", c.size, (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((r-inner, r-inner, r+inner, r+inner), fill=glow)
    return Image.alpha_composite(c, g.filter(ImageFilter.GaussianBlur(10)))
def kbd(src, col):
    fr = src.crop((25, 362, 1342, 672)); w, h = fr.size
    ImageDraw.Draw(fr).rectangle((14, 36, w-14, h-16), fill=col); return fr

def theme(p, LANG, SET, EX, ST, c, inner_col, glow):
    # c: koordinatlar
    for n, src, key in [("play", LANG, "play"), ("demo", LANG, "demo"), ("lang_on", c.get("lang_on_src", LANG), "lang_on"), ("lang_off", LANG, "lang_off"), ("seg_on", SET, "seg_on")]:
        box, t0, t1, c0, c1, r = c[key]
        save(f"{p}_{n}", rr(heal(src.crop(box), t0, t1, c0, c1), r), 900 if n in ("play", "demo") else 480)
    save(f"{p}_minus", circle(SET, *c["minus"], 40), 110); save(f"{p}_plus", circle(SET, *c["plus"], 40), 110)
    save(f"{p}_on", pill(SET, c["on"]), 130); save(f"{p}_off", pill(SET, c["off"]), 130)
    save(f"{p}_check", circle(EX, *c["check"], 42), 90)
    for i, n in enumerate(["uclu", "besli", "staccato"]):
        save(f"{p}_emb_{n}", circle(EX, *c["emb"][i], 84), 150)
    save(f"{p}_emb_ring", ring(EX, *c["emb"][0], 84, inner_col, glow), 150)
    save(f"{p}_kbd", kbd(ST, inner_col[:3]), 900, q=78)
    save(f"{p}_kw", ST.crop((218, 560, 300, 655)), 120)
    save(f"{p}_kb", ST.crop((100, 392, 153, 546)), 80)

GOLD = dict(play=((40,690,1495,830),400,1060,160,390,40), demo=((40,845,1495,968),470,960,160,440,36),
    lang_on=((78,108,760,208),220,470,60,210,18), lang_off=((776,108,1458,208),210,460,60,200,18),
    seg_on=((97,180,393,260),80,225,25,78,16), minus=(156,383), plus=(683,383),
    on=(1313,793,1437,869), off=(1313,897,1437,971), check=(2061,392), emb=[(178,210),(178,398),(178,575)])
SILVER = dict(play=((45,688,1488,828),430,1020,160,410,40), demo=((45,848,1488,966),520,930,160,500,34),
    lang_off=((776,140,1432,232),215,440,60,205,16),
    seg_on=((95,195,369,275),80,205,25,78,16), minus=(140,405), plus=(1398,405),
    on=(1318,802,1438,868), off=(1318,906,1438,970), check=(2058,379), emb=[(170,200),(170,400),(170,590)])
# Altın (Rustik)
theme("g", im("2eccef13"), im("ed44b164"), im("0d5daa55"), im("41619bf6"), GOLD, (20,15,10,255), (255,220,160,18))
# Mavi: altınla aynı yerleşim
theme("b", im("22934bed"), im("798775a9"), im("802465df"), im("d6563750"), GOLD, (8,14,30,255), (150,190,255,22))
# Siyah-Beyaz: yeni Ayarlar/sahne/egzersiz görselleri; dil ve büyük düğmeler eski gümüşten,
# seçili dil düğmesi yeni beyaz segmentten (yazılar karışmasın diye düz beyaz)
NEWSET = im("5d881fdd")
S2 = dict(SILVER); S2["lang_on"] = SILVER["seg_on"]; S2["lang_on_src"] = NEWSET
theme("s", im("3252fdc1"), NEWSET, im("e40f99c6"), im("e8ff791f"), S2, (8,8,8,255), (255,255,255,14))
json.dump(out, open("assets.json", "w"))
print(len(out), sum(len(v) for v in out.values()) // 1024, "KB")
