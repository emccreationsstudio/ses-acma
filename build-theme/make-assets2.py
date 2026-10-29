# Kulak / Konservatuvar / Nefes başlangıç ekranları / yüksek çözünürlüklü piyano parçalarını keser.
# Kullanım: python3 make-assets2.py <görsel klasörü> <önizleme klasörü>
# Çıktı: assets2.json (tema önekleri: g=rustik, s=siyah-beyaz, b=mavi)
import sys, json, io, base64
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter

A, OUT = sys.argv[1], sys.argv[2]
out = {}

def im(n): return Image.open(f"{A}/{n}-image.png").convert("RGB")

def save(name, img, width, q=80):
    if img.width > width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    b = io.BytesIO(); img.save(b, "WEBP", quality=q, method=4)
    out[name] = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
    img.save(f"{OUT}/{name}.png")

def circle(img, cx, cy, r):
    c = img.crop((cx - r, cy - r, cx + r, cy + r)).convert("RGBA")
    m = Image.new("L", (r * 8, r * 8), 0); ImageDraw.Draw(m).ellipse((0, 0, r * 8 - 1, r * 8 - 1), fill=255)
    c.putalpha(m.resize((2 * r, 2 * r), Image.LANCZOS)); return c

def feather(img, fx=0.16, fy=0.16):
    """Kenarları yumuşakça saydamlaştır (elips değil, yuvarlatılmış dikdörtgen geçiş)."""
    c = img.convert("RGBA"); w, h = c.size
    x = np.minimum(np.arange(w), np.arange(w)[::-1]) / max(1, w * fx)
    y = np.minimum(np.arange(h), np.arange(h)[::-1]) / max(1, h * fy)
    a = np.clip(np.minimum.outer(np.clip(y, 0, 1), np.clip(x, 0, 1)), 0, 1)
    a = (a * a * (3 - 2 * a))  # yumuşak geçiş
    c.putalpha(Image.fromarray((a * 255).astype(np.uint8))); return c

def tight(img, box, pad=0.10, delta=38, minfrac=0.25):
    """Kutu içinde çizimin (arka plandan farklı bölge) sınırını bul, pay bırakıp kes."""
    W, H = img.size
    x0, y0, x1, y1 = [int(v) for v in (box[0] * W, box[1] * H, box[2] * W, box[3] * H)]
    reg = cv2.GaussianBlur(np.asarray(img.crop((x0, y0, x1, y1)).convert("L")), (9, 9), 0).astype(int)
    bg = np.median(reg)
    m = (np.abs(reg - bg) > min(delta, 22)).astype(np.uint8)
    m = cv2.dilate(cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)), np.ones((15, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    if n <= 1: return (x0, y0, x1, y1)
    big_area = st[1:, cv2.CC_STAT_AREA].max()
    keep = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > big_area * 0.06]
    bx0 = min(st[i, 0] for i in keep); by0 = min(st[i, 1] for i in keep)
    bx1 = max(st[i, 0] + st[i, 2] for i in keep); by1 = max(st[i, 1] + st[i, 3] for i in keep)
    bw, bh = bx1 - bx0, by1 - by0
    px, py = bw * pad + 4, bh * pad + 4
    return (int(max(x0, x0 + bx0 - px)), int(max(y0, y0 + by0 - py)), int(min(x1, x0 + bx1 + px)), int(min(y1, y0 + by1 + py)))

def inpaint(img, boxes):
    a = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR); m = np.zeros(a.shape[:2], np.uint8)
    W, H = img.size
    for (x0, y0, x1, y1) in boxes: m[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)] = 255
    a = cv2.inpaint(a, m, 9, cv2.INPAINT_TELEA); return Image.fromarray(cv2.cvtColor(a, cv2.COLOR_BGR2RGB))

def cutout(img, lo=34, hi=80):
    """Arka planı (deri) saydam yap: simgeyi boyayıp yerel arka planı tahmin et, farka göre alfa."""
    a = np.asarray(img.convert("RGB")).astype(np.float32); h, w, _ = a.shape
    g = cv2.GaussianBlur(a, (0, 0), 2.5)
    e = max(4, min(h, w) // 25)
    border = np.concatenate([g[:e].reshape(-1, 3), g[-e:].reshape(-1, 3), g[:, :e].reshape(-1, 3), g[:, -e:].reshape(-1, 3)])
    bg0 = np.median(border, 0)
    m = (np.sqrt(((g - bg0) ** 2).sum(2)) > 30).astype(np.uint8)
    m = cv2.dilate(m, np.ones((15, 15), np.uint8))
    small = cv2.resize(a.astype(np.uint8), (max(8, w // 4), max(8, h // 4)), interpolation=cv2.INTER_AREA)
    ms = cv2.resize(m, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
    bgf = cv2.inpaint(small, ms * 255, 7, cv2.INPAINT_TELEA)
    bgf = cv2.GaussianBlur(cv2.resize(bgf, (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32), (0, 0), 12)
    g2 = cv2.GaussianBlur(a, (0, 0), 1.2)
    lum = lambda x: x @ np.array([0.3, 0.59, 0.11], np.float32)
    d = np.sqrt(((g2 - bgf) ** 2).sum(2)); dl = lum(g2) - lum(bgf)
    al = np.clip((d - lo) / (hi - lo), 0, 1)
    al = np.where(dl < 0, al * 0.7, al)
    # yalnızca simgeye bağlı bölgeler (küçük deri parıltıları gitsin)
    n, lab, st, _ = cv2.connectedComponentsWithStats((al > 0.25).astype(np.uint8))
    if n > 1:
        big_ = st[1:, cv2.CC_STAT_AREA].max(); keep = np.zeros(n, bool); keep[1:] = st[1:, cv2.CC_STAT_AREA] > big_ * 0.02
        for i in range(1, n):
            x, y, ww, hh, ar = st[i]
            edge = y <= 2 or x <= 2 or x + ww >= w - 2 or y + hh >= h - 2
            if edge and ar < big_ * 0.5 and (hh < h * 0.3 or ww < w * 0.12): keep[i] = False
        reach = cv2.dilate(keep[lab].astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
        al = np.where(reach, al, 0)
    al = cv2.GaussianBlur(al, (0, 0), 0.7)
    rgba = np.dstack([a, al * 255]).astype(np.uint8)
    out_ = Image.fromarray(rgba, "RGBA"); bb = Image.fromarray((al > 0.04).astype(np.uint8) * 255).getbbox()
    if bb:
        x0, y0, x1, y1 = bb; px = 8
        out_ = out_.crop((max(0, x0 - px), max(0, y0 - px), min(w, x1 + px), min(h, y1 + px)))
    return out_

def big(name, src, box, width=520, pad=0.10, delta=38, f=0.14, erase=None, cut=True):
    if erase: src = inpaint(src, erase)
    b = tight(src, box, pad=pad, delta=delta)
    c = src.crop(b)
    save(name, cutout(c) if cut else feather(c, f, f), (width if width < 400 else min(max(width, 700), 760)), q=84)

T = ["g", "s", "b"]

# ---------- 1) Yüksek çözünürlüklü piyano ----------
PIANO = {"s": "0f21d625", "b": "b594b690", "g": "6250fcfd"}
for p, f in PIANO.items():
    src = im(f); a = np.asarray(src.convert("L")).astype(int); H, W = a.shape
    # tuşların üst ve alt sınırı (beyaz tuş sütununda)
    col = a[:, 1000]
    ky0 = 90 + int(np.where(col[90:] > 120)[0][0]); ky1 = ky0
    while ky1 + 1 < H and col[ky1 + 1] > 100: ky1 += 1
    row = a[int(ky0 + (ky1 - ky0) * 0.85)]; xs = np.where(row > 140)[0]; kx0, kx1 = int(xs[0]), int(xs[-1])
    # çerçeve: tuş alanını koyu boya; border-image ile kullanılacak
    cb = a[:, 611]; seg = cb[ky0:int(ky0 + (ky1 - ky0) * 0.8)]; bky1 = ky0 + int(np.where(seg < 60)[0][-1]) + 3
    # tuşların alt ön yüzü (bevel) çerçeveye girmesin
    kb_bot = ky1
    while kb_bot + 1 < H and np.median(a[kb_bot + 1, kx0:kx1]) > 45: kb_bot += 1
    fr = src.copy(); ImageDraw.Draw(fr).rectangle((kx0 - 3, ky0 - 16, kx1 + 3, kb_bot + 3), fill=(8, 7, 6) if p == "g" else (6, 6, 8))
    ky1 = kb_bot
    out[f"{p}_kbd_slice"] = [ky0 - 12, W - kx1, H - ky1, kx0]
    save(f"{p}_kbd", fr, 2200, q=86)
    # beyaz tuş: Fa (466-611) — üstü siyah tuşsuz bölgeden genişletilir, alt kısım tam tuş
    xF0, xF1 = 473, 607
    # siyah tuş alt sınırı
    top = src.crop((xF0 + 4, ky0, 560, bky1 + 4)).resize((xF1 - xF0, bky1 + 4 - ky0), Image.BICUBIC)
    bot = src.crop((xF0, bky1 + 4, xF1, ky1 + 1))
    kw = Image.new("RGB", (xF1 - xF0, ky1 + 1 - ky0)); kw.paste(top, (0, 0)); kw.paste(bot, (0, bky1 + 4 - ky0))
    # birleşim yerini yumuşat
    seam = bky1 + 4 - ky0
    band = kw.crop((0, seam - 10, kw.width, seam + 10)).filter(ImageFilter.GaussianBlur(3)); kw.paste(band, (0, seam - 10))
    save(f"{p}_kw", kw, 220, q=82)
    # siyah tuş: Fa# (611 sınırı)
    r = a[ky0 + 40]; dk = np.where(r[560:665] < 70)[0]; bx0, bx1 = 560 + int(dk[0]), 560 + int(dk[-1])
    save(f"{p}_kb", src.crop((bx0, ky0, bx1 + 1, bky1 + 2)), 140, q=82)
    print("piano", p, (ky0, ky1, kx0, kx1, bky1, bx0, bx1))

# ---------- 2) Nefes başlangıç ekranları (büyük amblem) ----------
BS = {  # id: (g, s, b, kutu)
    "calm": ("0121929d", "a40a7fd9", "a6336e86", (0.33, 0.19, 0.68, 0.705)),
    "box": ("d752ddd3", "d4b84201", "e2a6d7da", (0.34, 0.22, 0.65, 0.65)),
    "hiss": ("e8029746", "721849a1", "a48e3f54", (0.13, 0.15, 0.83, 0.655)),
    "r478": ("9e24a0e3", "f8e449a3", "da6be53f", (0.35, 0.22, 0.65, 0.69)),
    "lip": ("e685da43", "e8b204b6", "e6abd2ba", (0.28, 0.25, 0.72, 0.65)),
    "ladder": ("7aafe758", "26290278", "e6a18d9f", (0.34, 0.205, 0.65, 0.70)),
    "pulse": ("6b6de8b7", "7e136ddf", "266c8ce9", (0.34, 0.195, 0.66, 0.67)),
    "holdHiss": ("8258f12f", "4007d6c7", "8abf5639", (0.32, 0.215, 0.85, 0.75)),
    "pant": ("ccc8dae5", "867868ac", "2ab0d0dc", (0.36, 0.225, 0.64, 0.655)),
}
for bid, (g, s, b, box) in BS.items():
    for p, f in zip(T, (g, s, b)):
        er = [(0.38, 0.16, 0.62, 0.235)] if bid == "hiss" else None
        bx = (box[0], 0.19, box[2], box[3]) if (bid == "r478" and p == "s") else box
        big(f"{p}_bs_{bid}", im(f), bx, width=460, erase=er, f=0.12, cut=False)

# ---------- 3) Kulak soru ekranları (büyük simge) ----------
EQ = {
    "chord": ("0f73710c", "9580fdb4", "ea18d7c7", (0.31, 0.27, 0.68, 0.77)),
    "interval": ("f73a7ee2", "c2c2e4dc", "e62199eb", (0.28, 0.315, 0.74, 0.73)),
    "note": ("ce3d0da0", "1ff5d7bc", "da70e7b8", (0.26, 0.30, 0.76, 0.76)),
    "sing": ("b701ba1b", "c862f6b2", "b49fb2ee", (0.10, 0.29, 0.90, 0.67)),
}
for k, (g, s, b, box) in EQ.items():
    for p, f in zip(T, (g, s, b)):
        big(f"{p}_bi_{k}", im(f), box, width=560, delta=30, f=0.12, cut=False)

# ---------- 4) Konservatuvar büyük kartları (büyük simge) ----------
CB = {
    "c_one": ("83ad6c91", "78acf685", "58eb5406"),
    "c_two": ("cfacbcf8", "a3a46931", "0e9540ff"),
    "c_three": ("61e22c43", "d01bb9cd", "3983c989"),
    "c_melody": ("fe131895", "9a9bd10f", "f151a608"),
    "c_rhythm": ("cfe70774", "fd8be634", "e82bd67a"),
    "c_four": ("8d4f4407", "8d588bce", "6f8c8198"),
    "c_sight": ("82ff68df", "e60e87f2", "7287f774"),
    "c_mdict": ("8fd909f0", "97fa67ec", "450ef4f8"),
    "c_rdict": ("19edb59b", "75a4db5f", "df4a7b35"),
    "c_theory": ("c2a6cc26", "f7f8f2a5", "a0de01de"),
}
CBOX = (0.26, 0.135, 0.74, 0.50)
for k, fs in CB.items():
    for p, f in zip(T, fs):
        big(f"{p}_bi_{k}", im(f), CBOX, width=480, delta=34, f=0.14)

# ---------- 5) Konservatuvar listesi (küçük simgeler) ----------
CONS_ORDER = ["c_one", "c_two", "c_three", "c_melody", "c_rhythm", "c_four", "c_sight", "c_mdict", "c_rdict", "c_theory"]
CL = {
    "g": ("ae9ad20f", [(177, 166), (629, 167), (1071, 167), (1510, 167), (177, 407), (630, 408), (1072, 410), (1512, 408), (598, 649), (1072, 648)], 66),
    "s": ("cb32ce7a", [(249, 153), (667, 154), (1089, 153), (1501, 153), (255, 399), (671, 402), (1091, 400), (1505, 402), (599, 652), (1090, 653)], 55),
}
for p, (f, cs, r) in CL.items():
    src = im(f)
    for k, (cx, cy) in zip(CONS_ORDER, cs): save(f"{p}_ei_{k}", circle(src, cx, cy, r), 160, q=84)
# Mavi listede çember yok: büyük karttaki simge kullanılır (küçültülmüş)
for k, fs in CB.items():
    big(f"b_ei_{k}", im(fs[2]), CBOX, width=320, delta=34, f=0.12)

# ---------- 6) Kulak listesi (sol simge bölgesi) + Kulak Testi kulağı ----------
EL = {  # tema: (dosya, [(x0,y0,x1,y1) her kart], kulak kutusu)
    "b": ("a4dbe4e4", [(82, 400, 330, 582), (665, 400, 890, 582), (1231, 400, 1480, 582), (340, 612, 562, 800), (948, 612, 1215, 800)], (150, 15, 590, 208)),
    "s": ("281251cf", [(62, 407, 300, 589), (657, 407, 875, 589), (1235, 407, 1472, 589), (327, 620, 558, 803), (949, 620, 1197, 803)], (150, 22, 440, 300)),
    "g": ("e06d9d89", [(76, 388, 315, 569), (657, 388, 885, 569), (1236, 388, 1473, 569), (354, 607, 595, 793), (952, 607, 1193, 793)], (140, 28, 385, 282)),
}
EAR_ORDER = ["note", "interval", "higher", "chord", "sing"]
for p, (f, boxes, ear) in EL.items():
    src = im(f)
    for k, bx in zip(EAR_ORDER, boxes): save(f"{p}_ei_{k}", feather(src.crop(bx), 0.10, 0.12), 300, q=82)
    save(f"{p}_hi_test", feather(src.crop(ear), 0.10, 0.10), 360, q=82)

# ---------- 7) Diyafram listesi: yeni amblemler (breath.json'daki br_* güncellenir) ----------
DL = {"g": ("0ad46a90", [(298, 268), (792, 269), (1272, 270), (1758, 269)], 114),
      "b": ("6891ddc5", [(301, 276), (786, 280), (1269, 276), (1752, 279)], 118),
      "s": ("4cd2f76e", [(296, 286), (786, 286), (1266, 283), (1753, 285)], 128)}
br = json.load(open("breath.json"))
for p, (f, cs, r) in DL.items():
    src = im(f)
    for k, (cx, cy) in zip(["ladder", "pulse", "holdHiss", "pant"], cs):
        c = circle(src, cx, cy, r); bb = io.BytesIO(); c2 = c; c2.save(bb, "WEBP", quality=88, method=6)
        br[f"{p}_br_{k}"] = "data:image/webp;base64," + base64.b64encode(bb.getvalue()).decode(); c2.save(f"{OUT}/{p}_br_{k}.png")
json.dump(br, open("breath.json", "w"))

json.dump(out, open("assets2.json", "w"))
print(len(out), sum(len(v) for v in out.values() if isinstance(v, str)) // 1024, "KB")
