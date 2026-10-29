# Konservatuvar soru ekranı büyük simgeleri: her görselde simgenin tam sınırı bulunup kesilir -> consbig.json
import sys, json, io, base64
import numpy as np, cv2
from PIL import Image
A, OUT = sys.argv[1], sys.argv[2]
src = open("/home/claude/sesacma-web/build-theme/make-assets2.py").read()
exec(src[:src.index('T = ["g", "s", "b"]')])
CB = {
    "c_one": ("83ad6c91", "78acf685", "58eb5406"), "c_two": ("cfacbcf8", "a3a46931", "0e9540ff"),
    "c_three": ("61e22c43", "d01bb9cd", "3983c989"), "c_melody": ("fe131895", "9a9bd10f", "f151a608"),
    "c_rhythm": ("cfe70774", "fd8be634", "e82bd67a"), "c_four": ("8d4f4407", "8d588bce", "6f8c8198"),
    "c_sight": ("82ff68df", "e60e87f2", "7287f774"), "c_mdict": ("8fd909f0", "97fa67ec", "450ef4f8"),
    "c_rdict": ("19edb59b", "75a4db5f", "df4a7b35"), "c_theory": ("c2a6cc26", "f7f8f2a5", "a0de01de"),
}
def soft(img, bx, padf=0.0, below=0.0):
    # GrabCut ile simgeyi ayır: gölgeli taraf da simgeye dahil olur, deri zemin ve kart çizgileri atılır
    x0, y0, x1, y1 = bx; W, H = img.size; P = 26
    X0, Y0, X1, Y1 = max(0, x0 - P), max(0, y0 - P), min(W, x1 + P), min(H, y1 + 10)
    c = np.asarray(img.crop((X0, Y0, X1, Y1)).convert("RGB")); hh, ww = c.shape[:2]
    mask = np.zeros((hh, ww), np.uint8); bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
    r = (max(1, x0 - X0 - 8), max(1, y0 - Y0 - 8), min(ww - 2, x1 - x0 + 16), min(hh - 2, y1 - y0 + 12))
    cv2.grabCut(cv2.cvtColor(c, cv2.COLOR_RGB2BGR), mask, r, bgd, fgd, 6, cv2.GC_INIT_WITH_RECT)
    fg = np.isin(mask, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.uint8)
    # zemin rengine çok yakın pikseller (kirişler arası, çizgiler arası boşluk) simge değildir
    brd = np.concatenate([c[:6].reshape(-1, 3), c[-6:].reshape(-1, 3), c[:, :6].reshape(-1, 3), c[:, -6:].reshape(-1, 3)]).astype(np.float32)
    bgc = np.median(brd, 0); cf = c.astype(np.float32)
    dist = np.sqrt(((cf - bgc) ** 2).sum(2)); lum = cf @ np.array([.3, .59, .11], np.float32); bl = float(bgc @ np.array([.3, .59, .11]))
    fg[((dist < 26) & (lum < bl + 14)) | (lum < bl + 5)] = 0
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg)
    keep = np.zeros_like(fg); big = max([st[i, 4] for i in range(1, n)] or [1])
    for i in range(1, n):
        w_, h_, ar = st[i, 2], st[i, 3], st[i, 4]
        if ar < big * 0.025: continue
        if h_ < 7 and w_ > 4 * h_: continue  # kart kenar çizgisi
        if st[i, 1] <= 2 and w_ > ww * 0.6 and h_ < hh * 0.25: continue  # üstteki kart kenarı bandı
        keep[lab == i] = 1
    al = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 1.1)
    a = np.dstack([c, (np.clip(al, 0, 1) * 255).astype(np.uint8)])
    o = Image.fromarray(a, "RGBA"); bb = o.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
    return o.crop((max(0, bb[0] - 3), max(0, bb[1] - 3), min(ww, bb[2] + 3), min(hh, bb[3] + 3))) if bb else o
def icon_box(img):
    W, H = img.size; x0, x1, y0, y1 = int(W * .20), int(W * .80), int(H * .10), int(H * .66)
    g = np.asarray(img.convert("L")).astype(np.float32)[y0:y1, x0:x1]
    bg = cv2.GaussianBlur(g, (0, 0), 40); m = ((g - bg) > 30).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    C = [tuple(int(v) for v in st[i]) for i in range(1, n) if st[i, 4] > 120 and st[i, 3] > 8 and st[i, 2] < g.shape[1] * .98 and not (st[i, 3] < 14 and st[i, 2] > 200)]
    # başlık satırı: aynı hizada başlayan en az 3 harf
    big = max(C, key=lambda c: c[4])
    tops = sorted(c[1] for c in C if 30 < c[3] < 110 and c[1] > big[1] + big[3] * 0.6)
    title = None
    for t in tops:
        if sum(1 for u in tops if abs(u - t) < 16) >= 3: title = t; break
    if title is None: title = g.shape[0]
    I = [c for c in C if c[1] + c[3] < title - 4] or [big]
    xa = min(c[0] for c in I); ya = min(c[1] for c in I); xb = max(c[0] + c[2] for c in I); yb = max(c[1] + c[3] for c in I)
    return (x0 + xa, y0 + ya, x0 + xb, y0 + yb)
res = {}; sheet = Image.new("RGBA", (10 * 130, 3 * 150), (30, 50, 90, 255))
for c, (k, fs) in enumerate(CB.items()):
    for r, (p, f) in enumerate(zip(["g", "s", "b"], fs)):
        img = im(f); bx = icon_box(img)
        o = soft(img, bx)
        if o.height > 420: o = o.resize((round(o.width * 420 / o.height), 420), Image.LANCZOS)
        b = io.BytesIO(); o.save(b, "WEBP", quality=84, method=6)
        res[f"{p}_bi_{k}"] = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
        t = o.copy(); t.thumbnail((120, 140)); sheet.alpha_composite(t, (c * 130 + 4, r * 150 + 4))
        print(p, k, bx, o.size)
# mavi liste simgeleri de aynı yöntemle (bb23f727)
L = im("bb23f727")
LB = {"c_one": (240,108,345,215), "c_two": (630,108,760,215), "c_three": (1020,108,1110,210), "c_melody": (1395,118,1660,200),
      "c_rhythm": (238,362,352,462), "c_four": (640,352,725,470), "c_sight": (1012,370,1210,456), "c_mdict": (1402,362,1590,458),
      "c_rdict": (528,618,690,742), "c_theory": (1012,622,1170,742)}
for n, (k, bx) in enumerate(LB.items()):
    o = soft(L, bx, 0.12, 0.0); b = io.BytesIO(); o.save(b, "WEBP", quality=88, method=6)
    res[f"b_ei_{k}"] = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
    t = o.copy(); t.thumbnail((120, 120)); sheet.alpha_composite(t, (n * 130 + 4, 3 * 150 - 0)) if False else None
json.dump(res, open("consbig.json", "w")); sheet.save(f"{OUT}/consbig.png")
