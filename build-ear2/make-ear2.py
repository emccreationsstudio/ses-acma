# Kulak ana ekranı: tasarım görsellerinden hero arka planı, buton, kart çerçeve ve resimleri -> ear2.json + ear2.css
import sys, json, io, base64
import numpy as np, cv2
from PIL import Image
from boxes import EH
A = "/mnt/user-data/attachments/56b66296-fc03-5990-a0be-6d20ea602b9c/"
OUT = sys.argv[1]
def b64(img, q=82, w=None):
    if w and img.width > w: img = img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
    b = io.BytesIO(); img.save(b, "WEBP", quality=q, method=6)
    return "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode()
def inpaint(img, rects, r=9):
    a = cv2.cvtColor(np.asarray(img.convert("RGB")), cv2.COLOR_RGB2BGR)
    m = np.zeros(a.shape[:2], np.uint8)
    for x0, y0, x1, y1 in rects: m[y0:y1, x0:x1] = 255
    o = cv2.inpaint(a, m, r, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(o, cv2.COLOR_BGR2RGB))
def glyph_mask(img, rect, dil=11):
    # başlık kutusundaki parlak yazı piksellerini bul (arka plana göre)
    x0, y0, x1, y1 = rect; g = np.asarray(img.convert("L")).astype(np.float32)
    sub = g[y0:y1, x0:x1]; bg = cv2.medianBlur(sub.astype(np.uint8), 31).astype(np.float32)
    m = ((sub - bg) > 12).astype(np.uint8)
    m = cv2.dilate(m, np.ones((dil, dil), np.uint8)); full = np.zeros(g.shape, np.uint8); full[y0:y1, x0:x1] = m
    return full
def softfill(img, rects, sig=28, extra=None):
    # maske içini çevredeki renklerin yumuşak ortalamasıyla doldur + çevredeki dokuya benzer ince gren
    a = np.asarray(img.convert("RGB")).astype(np.float32); h, w = a.shape[:2]
    m = np.ones((h, w), np.float32)
    for x0, y0, x1, y1 in rects: m[y0:y1, x0:x1] = 0
    if extra is not None: m[extra > 0] = 0
    num = cv2.GaussianBlur(a * m[..., None], (0, 0), sig); den = cv2.GaussianBlur(m, (0, 0), sig)[..., None] + 1e-4
    f = num / den
    for _ in range(2):
        num = cv2.GaussianBlur(np.where(m[..., None] > 0, a, f) * 1, (0, 0), sig * 0.6); f = np.where(m[..., None] > 0, a, num)
    hf = a - cv2.GaussianBlur(a, (0, 0), 3)
    rng = np.random.default_rng(3); gr = rng.normal(0, hf[m > 0].std() * 0.8, (h, w))[..., None]
    o = np.where(m[..., None] > 0, a, f + gr)
    mm = np.clip(cv2.GaussianBlur(1 - m, (0, 0), 2.5) * 1.6, 0, 1)[..., None]
    o = a * (1 - mm) + o * mm
    return Image.fromarray(np.clip(o, 0, 255).astype(np.uint8))
def divider_x(card):
    g = np.asarray(card.convert("L")).astype(np.float32); h, w = g.shape
    band = g[int(h * .22):int(h * .78)]
    col = band.mean(0); best, bx = 0, None
    for x in range(int(w * .30), int(w * .58)):
        loc = col[x] - (col[x - 6:x - 2].mean() + col[x + 3:x + 7].mean()) / 2
        # dikey çizgi: sütun boyunca tutarlı parlaklık
        cons = (band[:, x] > band[:, x - 5] + 6).mean()
        sc = loc * cons
        if sc > best: best, bx = sc, x
    return bx if best > 3 else None
res, css = {}, []
for p, d in EH.items():
    src = Image.open(A + d["f"] + "-image.png").convert("RGB")
    hx0, hy0, hx1, hy1 = d["hero"]; hw, hh = hx1 - hx0, hy1 - hy0
    tx0, ty0, tx1, ty1 = d["title"]; bx0, by0, bx1, by1 = d["btn"]
    hero = softfill(src, [d["btn"]], sig=14, extra=glyph_mask(src, d["title"])).crop(d["hero"])
    res[f"{p}_ehero"] = b64(hero, 80, 1500)
    top = hero.crop((0, 0, round(hw * 1100 / 1712), by0 - hy0)).convert("RGBA")
    al = np.ones((top.height, top.width), np.float32); f_ = int(top.height * .25)
    al[-f_:] = np.linspace(1, 0, f_)[:, None]; ta = np.asarray(top).copy(); ta[..., 3] = (al * 255).astype(np.uint8)
    res[f"{p}_eherotop"] = b64(Image.fromarray(ta, "RGBA"), 82, 1000)
    # buton: yazı ve PRO rozeti silinir
    btn = src.crop(d["btn"]); bw, bh = btn.size
    # yazı bölgesi: her satırda sol ve sağ sınır arasında doğrusal geçiş (kenarda basamak olmaz)
    a = np.asarray(btn).astype(np.float32); r0, r1 = {'b': (.36, .69), 's': (.19, .57), 'g': (.31, .66)}[p]; x0, x1 = int(bw * r0), int(bw * r1)
    cL = a[:, x0 - 5:x0].mean(1); cR = a[:, x1:x1 + 5].mean(1)
    t = np.linspace(0, 1, x1 - x0)[None, :, None]; t = t * t * (3 - 2 * t)
    a[:, x0:x1] = cL[:, None] * (1 - t) + cR[:, None] * t
    if p == "b":  # tasarımda kulak memesi butonun soluna taşıyor: o kısmı da temizle
        e0, e1 = int(bw * .025), int(bw * .19); cL2 = a[:, e0 - 4:e0].mean(1); cR2 = a[:, e1:e1 + 4].mean(1)
        t2 = np.linspace(0, 1, e1 - e0)[None, :, None]; t2 = t2 * t2 * (3 - 2 * t2); a[:, e0:e1] = cL2[:, None] * (1 - t2) + cR2[:, None] * t2
    rng = np.random.default_rng(1); a[:, x0:x1] += rng.normal(0, 1.6, a[:, x0:x1].shape[:2])[..., None]
    btn = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    # buton şekli dışını şeffaf yap (koyu köşeler kalmasın)
    g = cv2.GaussianBlur(np.asarray(btn.convert("L")).astype(np.float32), (0, 0), 1.5)
    bgv = np.median(np.concatenate([g[:4, :4].ravel(), g[:4, -4:].ravel(), g[-4:, :4].ravel(), g[-4:, -4:].ravel()]))
    m = (g > bgv + 28).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m); k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); m = (lab == k).astype(np.uint8)
    ff = m.copy(); mh_, mw_ = m.shape; msk = np.zeros((mh_ + 2, mw_ + 2), np.uint8); cv2.floodFill(ff, msk, (0, 0), 1); m = m | (1 - ff)
    al = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.0)
    btnA = Image.fromarray(np.dstack([np.asarray(btn), (al * 255).astype(np.uint8)]), "RGBA")
    res[f"{p}_ebtn"] = b64(btnA, 84, 1200)
    # kısa ve düz orta bölümlü sürüm (telefon / dar butonlar)
    cap = round(bh * 1.25); A_ = np.asarray(btnA).astype(np.float32)
    cl = A_[:, cap:cap + 3].mean(1); cr = A_[:, bw - cap - 3:bw - cap].mean(1); mid = round(bh * 3)
    prof = A_[:, cap:bw - cap].mean(1); midA = np.repeat(prof[:, None], mid, 1); e = max(2, mid // 5)
    tl = np.linspace(0, 1, e)[None, :, None]; midA[:, :e] = cl[:, None] * (1 - tl) + prof[:, None] * tl; midA[:, -e:] = prof[:, None] * (1 - tl) + cr[:, None] * tl
    sh = np.concatenate([A_[:, :cap], midA, A_[:, bw - cap:]], 1)
    res[f"{p}_ebtns"] = b64(Image.fromarray(np.clip(sh, 0, 255).astype(np.uint8), "RGBA"), 86, 900)
    sl = round(bh * 0.9)
    css.append(f'html[data-skin="{"blue" if p=="b" else "mono" if p=="s" else "rustic"}"] {{ --eh-ar: {hw}/{hh}; --eh-l: {100*(tx0-hx0)/hw:.1f}%; --eh-t: {100*(ty0-hy0)/hh:.1f}%; '
               f'--eb-l: {100*(bx0-hx0)/hw:.1f}%; --eb-r: {100*(hx1-bx1)/hw:.1f}%; --eb-t: {100*(by0-hy0)/hh:.1f}%; --eb-b: {100*(hy1-by1)/hh:.1f}%; '
               f'--eb-slice: {sl}; --ebs-slice: {round(bh*1.25)}; --eh-slice: {44 if p=="g" else 30}; --ec-slice: {38 if p=="g" else 24}; }}')
    for k, c in zip(["note", "interval", "higher", "chord", "sing"], d["cards"]):
        card = src.crop(c); cw, ch = card.size
        fr = np.asarray(card).copy(); S = 40; H_, W_ = fr.shape[:2]
        m0, m1 = int(W_ * .12), int(W_ * .88)
        for y in list(range(0, S)) + list(range(H_ - S, H_)): fr[y, m0:m1] = np.median(fr[y, m0:m1], axis=0)
        n0, n1 = int(H_ * .22), int(H_ * .78)
        for x in list(range(0, S)) + list(range(W_ - S, W_)): fr[n0:n1, x] = np.median(fr[n0:n1, x], axis=0)
        res[f"{p}_ecard_{k}"] = b64(Image.fromarray(fr), 82, 600)  # çerçeve (border-image)
        dx = divider_x(card) if p != "b" else None
        if p == "b": dx = {"note": 262, "interval": 250, "higher": 262, "chord": 238, "sing": 276}[k]
        if dx is None: dx = int(cw * 0.42)
        ins = 7 if p != "g" else 10
        im = card.crop((ins, ins, min(cw, dx + 3), ch - ins)).convert("RGBA")
        if p == "b":  # mavi: resim sağa doğru yumuşakça kaybolur
            a = np.asarray(im).copy(); w = a.shape[1]; f = int(w * .28)
            ramp = np.ones(w, np.float32); ramp[w - f:] = np.linspace(1, 0, f) ** 1.4
            a[..., 3] = (a[..., 3] * ramp[None, :]).astype(np.uint8); im = Image.fromarray(a, "RGBA")
        res[f"{p}_eimg_{k}"] = b64(im, 84, 420)
        print(p, k, "divider", dx, cw)
hq = Image.open(A + "3dd8b05b-image.png").convert("RGB"); W_, H_ = hq.size
hq = hq.crop((int(W_ * .09), int(H_ * .17), int(W_ * .93), int(H_ * .70))).convert("RGBA")
a = np.asarray(hq).copy(); hh, ww = a.shape[:2]; fx, fy = int(ww * .10), int(hh * .12)
rx = np.ones(ww, np.float32); rx[:fx] = np.linspace(0, 1, fx); rx[-fx:] = np.linspace(1, 0, fx)
ry = np.ones(hh, np.float32); ry[:fy] = np.linspace(0, 1, fy); ry[-fy:] = np.linspace(1, 0, fy)
a[..., 3] = (np.outer(ry, rx) * 255).astype(np.uint8); res["b_bi_higher"] = b64(Image.fromarray(a, "RGBA"), 86, 760)
json.dump(res, open("ear2.json", "w")); open("ear2-vars.css", "w").write("\n".join(css) + "\n")
print(sum(len(v) for v in res.values()) // 1024, "KB")
