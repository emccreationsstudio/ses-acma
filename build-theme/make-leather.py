# Tasarım görsellerindeki deri dokusunu ve sayfa arka planını keser -> leather.json
import sys, json, io, base64
import numpy as np, cv2
from PIL import Image
A, OUT = sys.argv[1], sys.argv[2]
out = {}
def im(n): return np.asarray(Image.open(f"{A}/{n}-image.png").convert("RGB")).astype(np.float32)
def enc(name, arr, q=80):
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); b = io.BytesIO(); img.save(b, "WEBP", quality=q, method=6)
    out[name] = "data:image/webp;base64," + base64.b64encode(b.getvalue()).decode(); img.save(f"{OUT}/{name}.png")
def flatten(a, k=61):
    lo = cv2.GaussianBlur(a, (0, 0), k); mean = a.reshape(-1, 3).mean(0)
    return a / np.maximum(lo, 1) * mean
def mirror_tile(a):
    top = np.concatenate([a, a[:, ::-1]], 1); return np.concatenate([top, top[::-1]], 0)
# (dosya, kart içi boş bölge, sayfa kenarı)
SRC = {"g": ("d752ddd3", (250, 225, 600, 590), (0, 0, 195, 954)),
       "b": ("e2a6d7da", (240, 225, 600, 590), (0, 0, 195, 954)),
       "s": ("d4b84201", (250, 225, 600, 590), (0, 0, 195, 954))}
for p, (f, (x0, y0, x1, y1), (bx0, by0, bx1, by1)) in SRC.items():
    a = im(f)
    leather = flatten(a[y0:y1, x0:x1])
    enc(f"{p}_leather", mirror_tile(leather), q=82)
    side = a[by0:by1, bx0:bx1]
    page = side
    enc(f"{p}_page", page, q=78)
    print(p, leather.mean(axis=(0, 1)).round(), page.mean(axis=(0, 1)).round())
json.dump(out, open("leather.json", "w"))
