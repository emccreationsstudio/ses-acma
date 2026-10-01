"""App Store ekran görüntüleri (6.9", 1320×2868) — Türkçe ve İngilizce.
Gereksinim: pip install playwright pillow && playwright install chromium
Kullanım: npm run build && python3 scripts/screenshots.py
Çıktı: appstore/screenshots/tr/*.png, appstore/screenshots/en/*.png
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
APP = (ROOT / "www" / "index.html").as_uri()
OUT = ROOT / "appstore" / "screenshots"
W, H = 1320, 2868
VIEW = {"width": 440, "height": 956}

TEXGYRE = "/usr/share/texmf/fonts/opentype/public/tex-gyre"
FONT_CANDIDATES = [
    "/System/Library/Fonts/NewYork.ttf",
    f"{TEXGYRE}/texgyrepagella-bold.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
]
SUB_CANDIDATES = [
    "/System/Library/Fonts/SFNS.ttf",
    f"{TEXGYRE}/texgyreheros-regular.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def font(cands, size):
    for c in cands:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


CAPTIONS = {
    "tr": [
        ("Piyano eşliğinde\nses açma", "Her tur bir akorla başlar, yarım ton yükselir"),
        ("Doğru notada mısın?", "Mikrofon söylediğini anında gösterir"),
        ("Yıldızları topla", "Isınmanın sonunda kaç notayı tutturduğunu gör"),
        ("Her sese göre ayarla", "Çocuk, soprano, alto, tenor, bas ve tempo"),
    ],
    "en": [
        ("Vocal warm-ups\nwith piano", "Each round starts with a chord and rises by a half step"),
        ("Are you on the note?", "The microphone shows your pitch in real time"),
        ("Collect the stars", "See how many notes you hit at the end"),
        ("Fits every voice", "Child, soprano, alto, tenor, bass and tempo"),
    ],
}

# Linux'ta New York / SF Pro yok: en yakın serif ve sans fontlarla çek (iPhone'da sistem fontları görünür)
FONT_CSS = f"""
@font-face {{ font-family: "ShotSerif"; src: url("file://{TEXGYRE}/texgyrepagella-bold.otf"); font-weight: 600 800; }}
@font-face {{ font-family: "ShotSerif"; src: url("file://{TEXGYRE}/texgyrepagella-regular.otf"); font-weight: 400 500; }}
@font-face {{ font-family: "ShotSans"; src: url("file://{TEXGYRE}/texgyreheros-regular.otf"); font-weight: 400 500; }}
@font-face {{ font-family: "ShotSans"; src: url("file://{TEXGYRE}/texgyreheros-bold.otf"); font-weight: 600 900; }}
:root {{ --font-display: "ShotSerif", serif; --font-body: "ShotSans", sans-serif; }}
body {{ font-family: var(--font-body); }}
"""


def shoot(page, lang, name):
    path = OUT / lang / f"_raw_{name}.png"
    page.screenshot(path=str(path))
    return path


def capture(lang):
    (OUT / lang).mkdir(parents=True, exist_ok=True)
    raws = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        ctx = b.new_context(viewport=VIEW, device_scale_factor=3, color_scheme="light", locale=lang)
        page = ctx.new_page()
        page.add_init_script(f"localStorage.setItem('sesacma', JSON.stringify({{ex:'besli',range:'child',start:60,end:67,bpm:100,dir:'upDown',melody:true,lang:'{lang}'}}))")
        page.goto(APP)
        page.add_style_tag(content=FONT_CSS)
        page.wait_for_timeout(300)

        # 1) Çalarken: 3. turda, notalar yanıyor
        page.evaluate("start()")
        page.evaluate("run.t0 = piano.ctx.currentTime - (run.tl.total / 13 * 2 + 4.3)")
        page.wait_for_timeout(250)
        raws.append(shoot(page, lang, "1"))

        # 2) Mikrofon göstergesi: hedefte, tam isabet
        page.evaluate("""() => {
            document.getElementById('meter').hidden = false;
            document.getElementById('mic').checked = true;
            const ev = run.tl.events.find(e => e.kind === 'note' && piano.ctx.currentTime - run.t0 < e.t + e.len && piano.ctx.currentTime - run.t0 >= e.t);
            const tgt = ev ? ev.target : 64;
            mic.midi = tgt + 0.08;
            renderMeter(tgt);
            run.scored = 14; run.hits = 13; run.listening = false;
            document.getElementById('score').hidden = false;
            document.getElementById('score').textContent = S().notesScore(13, 14);
        }""")
        page.wait_for_timeout(50)
        raws.append(shoot(page, lang, "2"))

        # 3) Bitti: yıldızlar
        page.evaluate("""() => {
            stop(true); lastResult = { hits: 15, scored: 16 }; showResult();
            document.getElementById('meter').hidden = true;
        }""")
        page.wait_for_timeout(50)
        raws.append(shoot(page, lang, "3"))

        # 4) Ayarlar: tenor seçili, kaydırılmış
        page.evaluate("""() => { lastResult = null; document.getElementById('ranges-tenor').click(); window.scrollTo(0, document.getElementById('exercises').offsetTop - 70); }""")
        page.wait_for_timeout(100)
        raws.append(shoot(page, lang, "4"))
        b.close()
    return raws


def frame(raw_path, title, sub, out_path):
    bg = Image.new("RGB", (W, H))
    px = bg.load()
    top, bottom = (35, 32, 66), (11, 10, 22)
    for y in range(H):
        t = y / H
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = c
    d = ImageDraw.Draw(bg)
    f_title = font(FONT_CANDIDATES, 116)
    f_sub = font(SUB_CANDIDATES, 50)
    y = 150
    for line in title.split("\n"):
        w = d.textlength(line, font=f_title)
        d.text(((W - w) / 2, y), line, font=f_title, fill=(245, 231, 196))
        y += 128
    w = d.textlength(sub, font=f_sub)
    if w > W - 140:
        f_sub = font(SUB_CANDIDATES, int(50 * (W - 140) / w))
        w = d.textlength(sub, font=f_sub)
    d.text(((W - w) / 2, y + 22), sub, font=f_sub, fill=(190, 184, 214))

    shot = Image.open(raw_path).convert("RGB")
    top_y = y + 140
    scale = (H - top_y + 260) / shot.height  # alt kısım taşsın; telefon ekranı gibi görünür
    sw, sh = int(shot.width * scale * 0.86), int(shot.height * scale * 0.86)
    shot = shot.resize((sw, sh), Image.LANCZOS)
    radius = 70
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw, sh), radius=radius, fill=255)
    x = (W - sw) // 2
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle((x, top_y + 30, x + sw, top_y + 30 + sh), radius=radius, fill=150)
    shadow = shadow.filter(ImageFilter.GaussianBlur(40))
    bg = Image.composite(Image.new("RGB", (W, H), (5, 7, 18)), bg, shadow)
    border = Image.new("RGB", (sw + 24, sh + 24), (8, 10, 22))
    bmask = Image.new("L", (sw + 24, sh + 24), 0)
    ImageDraw.Draw(bmask).rounded_rectangle((0, 0, sw + 24, sh + 24), radius=radius + 12, fill=255)
    bg.paste(border, (x - 12, top_y - 12), bmask)
    bg.paste(shot, (x, top_y), mask)
    bg.save(out_path, optimize=True)


for lang in ("tr", "en"):
    raws = capture(lang)
    for i, (raw, (title, sub)) in enumerate(zip(raws, CAPTIONS[lang]), start=1):
        frame(raw, title, sub, OUT / lang / f"{i}.png")
        raw.unlink()
    print(f"appstore/screenshots/{lang}: 4 görsel (1320×2868)")
