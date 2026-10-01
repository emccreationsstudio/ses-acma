// src/index.html → www/index.html (iOS uygulaması için tam HTML belgesi)
// - Google Fonts bağlantılarını çıkarır: uygulama internetsiz çalışır, iPhone'un yuvarlak sistem fontu kullanılır.
// - Tam <!doctype html> iskeleti, mobil viewport ve güvenli alan boşlukları ekler.
// Kullanım: node scripts/build.js
const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..");
const src = fs.readFileSync(path.join(root, "src", "index.html"), "utf8");

const withoutFonts = src
  .split("\n")
  .filter((line) => !/fonts\.(googleapis|gstatic)\.com/.test(line))
  .join("\n");

const cut = withoutFonts.indexOf("</style>");
if (cut < 0) throw new Error("src/index.html içinde </style> bulunamadı");
const head = withoutFonts.slice(0, cut + "</style>".length);
const body = withoutFonts.slice(cut + "</style>".length);

const base = `<style>
:root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
html, body { margin: 0; overscroll-behavior: none; }
body { -webkit-user-select: none; user-select: none; -webkit-touch-callout: none; -webkit-text-size-adjust: 100%; }
img { max-width: 100%; }
[hidden] { display: none !important; }
</style>`;

const out = `<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, maximum-scale=1, user-scalable=no">
<meta name="color-scheme" content="light dark">
<meta name="format-detection" content="telephone=no">
${base}
${head}
</head>
<body>
${body.trim()}
</body>
</html>
`;

if (/fonts\.googleapis|fonts\.gstatic|https?:\/\//.test(out.replace(/xmlns="http:\/\/www\.w3\.org\/2000\/svg"/g, ""))) {
  throw new Error("Uygulama dosyasında dış bağlantı kaldı");
}

fs.mkdirSync(path.join(root, "www"), { recursive: true });
fs.writeFileSync(path.join(root, "www", "index.html"), out);
console.log(`www/index.html yazıldı (${(out.length / 1024).toFixed(1)} KB, dış bağlantı yok)`);
