"""Ses Açma uygulama ikonu ve açılış ekranı — assets/logo.svg'den üretilir.
Çıktı: assets/icon-1024.png (App Store ikonu, saydamlıksız RGB) ve assets/splash-2732.png
Gereksinim: pip install playwright pillow && playwright install chromium
Kullanım: python3 scripts/make_icon.py
"""
from pathlib import Path
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
svg = (ASSETS / "logo.svg").read_text(encoding="utf-8")

html = f"""<!doctype html><html><head><meta charset="utf-8">
<style>html,body{{margin:0;background:#000}} svg{{display:block;width:1024px;height:1024px}}</style>
</head><body>{svg}</body></html>"""

tmp = ASSETS / "_logo_render.png"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1024, "height": 1024}, device_scale_factor=2)
    pg.set_content(html)
    pg.locator("svg").screenshot(path=str(tmp))
    b.close()

big = Image.open(tmp).convert("RGB")          # 2048×2048
tmp.unlink()
big.resize((1024, 1024), Image.LANCZOS).save(ASSETS / "icon-1024.png", optimize=True)

# Açılış ekranı: logonun zemin rengi, ortada yuvarlatılmış logo
SPLASH, M = 2732, 820
splash = Image.new("RGB", (SPLASH, SPLASH), (17, 16, 34))  # #111022
mark = big.resize((M, M), Image.LANCZOS)
mask = Image.new("L", (M * 4, M * 4), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, M * 4, M * 4), radius=int(M * 4 * 0.225), fill=255)
mask = mask.resize((M, M), Image.LANCZOS)
splash.paste(mark, ((SPLASH - M) // 2, (SPLASH - M) // 2), mask)
splash.save(ASSETS / "splash-2732.png", optimize=True)
print("assets/icon-1024.png ve assets/splash-2732.png yazıldı")
