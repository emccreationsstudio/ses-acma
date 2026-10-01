// appstore/listing.md içindeki metinlerin App Store karakter sınırlarını kontrol eder.
// Kullanım: node scripts/check-listing.js
const fs = require("fs");
const path = require("path");

const md = fs.readFileSync(path.join(__dirname, "..", "appstore", "listing.md"), "utf8");
const LIMITS = [
  [/Ad \(30\)|Name \(30\)/, 30, "Ad"],
  [/Alt başlık \(30\)|Subtitle \(30\)/, 30, "Alt başlık"],
  [/Tanıtım metni \(170\)|Promotional text \(170\)/, 170, "Tanıtım"],
  [/Açıklama \(4000\)|Description \(4000\)/, 4000, "Açıklama"],
  [/Anahtar kelimeler \(100|Keywords \(100/, 100, "Anahtar kelimeler"]
];

const blocks = [];
const re = /\*\*([^*]+)\*\*\s*\n```\n([\s\S]*?)\n```/g;
let m;
while ((m = re.exec(md))) blocks.push({ label: m[1], text: m[2] });

let ok = true;
for (const b of blocks) {
  const lim = LIMITS.find(([r]) => r.test(b.label));
  if (!lim) continue;
  const n = [...b.text].length;
  const pass = n <= lim[1];
  if (!pass) ok = false;
  let extra = "";
  if (lim[2] === "Anahtar kelimeler" && /,\s/.test(b.text)) { ok = false; extra = "  (virgülden sonra boşluk var!)"; }
  console.log(`${pass ? "✓" : "✗"} ${b.label.padEnd(38)} ${String(n).padStart(4)} / ${lim[1]}${extra}`);
}
process.exit(ok ? 0 : 1);
