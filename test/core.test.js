// Ses Açma — mantık testleri (node test/core.test.js)
const fs = require("fs");
const path = require("path");
const assert = require("assert");

const html = fs.readFileSync(path.join(__dirname, "..", "src", "index.html"), "utf8");
const core = html.match(/<script id="core">([\s\S]*?)<\/script>/)[1];
const mod = { exports: {} };
new Function("module", core)(mod);
const C = mod.exports;

let passed = 0;
function test(name, fn) { fn(); passed++; console.log("✓", name); }

test("nota adları", () => {
  assert.strictEqual(C.noteName(60), "Do4");
  assert.strictEqual(C.noteName(69), "La4");
  assert.strictEqual(C.noteName(43), "Sol2");
  assert.strictEqual(C.noteName(61), "Do#4");
  assert.strictEqual(C.noteName(60, "en"), "C4");
  assert.strictEqual(C.noteName(67, "en"), "G4");
});

test("dil seçimi", () => {
  assert.strictEqual(C.pickLanguage("tr-TR"), "tr");
  assert.strictEqual(C.pickLanguage("tr"), "tr");
  assert.strictEqual(C.pickLanguage("en-US"), "en");
  assert.strictEqual(C.pickLanguage("de-DE"), "en");
  assert.strictEqual(C.pickLanguage(undefined), "en");
});

test("Türkçe ve İngilizce metinler eksiksiz", () => {
  const tr = Object.keys(C.STRINGS.tr).sort(), en = Object.keys(C.STRINGS.en).sort();
  assert.deepStrictEqual(tr, en);
  for (const lang of ["tr", "en"]) {
    for (const ex of C.EXERCISES) {
      assert.ok(ex.name[lang] && ex.syllables[lang], `${ex.id} ${lang}`);
      assert.ok(C.STRINGS[lang].levels[ex.level], `seviye ${ex.level} ${lang}`);
    }
    for (const r of C.RANGES) assert.ok(C.STRINGS[lang].ranges[r.id], `${r.id} ${lang}`);
  }
  // Sayfadaki her data-i18n anahtarının iki dilde de karşılığı olmalı
  const keys = [...html.matchAll(/data-i18n="([^"]+)"/g)].map((m) => m[1]);
  for (const k of keys) {
    assert.strictEqual(typeof C.STRINGS.tr[k], "string", `tr eksik: ${k}`);
    assert.strictEqual(typeof C.STRINGS.en[k], "string", `en eksik: ${k}`);
  }
});

test("uygulama derlemesi internetsiz", () => {
  require("child_process").execSync("node scripts/build.js", { cwd: path.join(__dirname, "..") });
  const out = fs.readFileSync(path.join(__dirname, "..", "www", "index.html"), "utf8");
  assert.ok(out.startsWith("<!doctype html>"));
  assert.ok(out.includes("viewport-fit=cover"));
  assert.ok(!/https?:\/\//.test(out), "dış bağlantı var");
});

test("siyah tuşlar", () => {
  assert.ok(C.isBlack(61) && C.isBlack(70));
  assert.ok(!C.isBlack(60) && !C.isBlack(64) && !C.isBlack(65));
});

test("kök dizisi: çık ve in", () => {
  assert.deepStrictEqual(C.rootSequence(60, 63, "upDown"), [60, 61, 62, 63, 62, 61, 60]);
  assert.deepStrictEqual(C.rootSequence(60, 63, "up"), [60, 61, 62, 63]);
  assert.deepStrictEqual(C.rootSequence(65, 60, "up"), [65]);
});

test("zaman çizelgesi: süre ve olay sayısı", () => {
  const ex = C.EXERCISES.find((e) => e.id === "besli");
  const tl = C.buildTimeline({ exercise: ex, start: 60, end: 61, dir: "up", bpm: 60, melody: true });
  // tur başına: akor 2 vuruş + 8 nota×1 + son nota 2 + nefes 1 = 13 sn (60 BPM)
  assert.strictEqual(tl.rounds, 2);
  assert.strictEqual(tl.events.length, 2 * (1 + 9));
  assert.ok(Math.abs(tl.total - 26) < 1e-9, "toplam " + tl.total);
  const notes = tl.events.filter((e) => e.kind === "note" && e.round === 1).map((e) => e.target);
  assert.deepStrictEqual(notes, [61, 63, 65, 66, 68, 66, 65, 63, 61]);
  // olaylar çakışmasın
  for (let i = 1; i < tl.events.length; i++) {
    const a = tl.events[i - 1], b = tl.events[i];
    assert.ok(a.t + a.len <= b.t + 1e-9, "çakışma " + i);
    assert.ok(a.dur <= a.len + 1e-9);
  }
});

test("melodi kapalıyken notalar çalınmaz ama akor çalar", () => {
  const tl = C.buildTimeline({ exercise: C.EXERCISES[0], start: 60, end: 60, dir: "up", bpm: 100, melody: false });
  assert.ok(tl.events.filter((e) => e.kind === "chord").every((e) => e.sound));
  assert.ok(tl.events.filter((e) => e.kind === "note").every((e) => !e.sound));
});

test("staccato notalar kısa", () => {
  const ex = C.EXERCISES.find((e) => e.id === "staccato");
  const tl = C.buildTimeline({ exercise: ex, start: 60, end: 60, dir: "up", bpm: 120, melody: true });
  const n = tl.events.filter((e) => e.kind === "note");
  assert.ok(n[0].dur < n[0].len * 0.5);
});

test("sent farkı ve oktav eşdeğerliği", () => {
  assert.strictEqual(Math.round(C.centsOff(60.2, 60)), 20);
  assert.strictEqual(Math.round(C.centsOff(48.0, 60)), 0);   // bir oktav aşağı
  assert.strictEqual(Math.round(C.centsOff(59.7, 60)), -30);
});

test("yıldızlar", () => {
  assert.strictEqual(C.starsFor(9, 10), "★★★");
  assert.strictEqual(C.starsFor(6, 10), "★★☆");
  assert.strictEqual(C.starsFor(0, 10), "☆☆☆");
});

// --- Perde algılama: sentetik sesler ---
function voice(freq, sr, n, opts = {}) {
  const buf = new Float32Array(n);
  const vib = opts.vibrato || 0;
  for (let i = 0; i < n; i++) {
    const t = i / sr;
    const f = freq * Math.pow(2, (vib * Math.sin(2 * Math.PI * 5.5 * t)) / 1200);
    const ph = 2 * Math.PI * f * t;
    // insan sesine benzer armonikler + biraz gürültü
    buf[i] = 0.3 * (Math.sin(ph) + 0.6 * Math.sin(2 * ph) + 0.35 * Math.sin(3 * ph) + 0.15 * Math.sin(4 * ph))
      + (opts.noise || 0) * (Math.random() * 2 - 1);
  }
  return buf;
}

test("perde algılama: bas'tan çocuk sesine kadar", () => {
  for (const sr of [44100, 48000]) {
    for (let midi = 43; midi <= 84; midi += 1) {
      const f = 440 * Math.pow(2, (midi - 69) / 12);
      const m = C.detectMidi(voice(f, sr, 4096, { noise: 0.02 }), sr);
      assert.ok(m != null, `algılanamadı midi=${midi} sr=${sr}`);
      assert.ok(Math.abs(m - midi) < 0.1, `midi=${midi} bulunan=${m.toFixed(3)} sr=${sr}`);
    }
  }
});

test("perde algılama: vibratolu ses", () => {
  const m = C.detectMidi(voice(261.63, 48000, 4096, { vibrato: 40, noise: 0.03 }), 48000);
  assert.ok(Math.abs(m - 60) < 0.5, "bulunan " + m);
});

test("perde algılama: 30 sent pes ses doğru ölçülür", () => {
  const f = 440 * Math.pow(2, (60 - 0.3 - 69) / 12);
  const m = C.detectMidi(voice(f, 48000, 4096), 48000);
  assert.strictEqual(Math.round(C.centsOff(m, 60)), -30);
});

test("sessizlik ve gürültü null döner", () => {
  assert.strictEqual(C.detectMidi(new Float32Array(4096), 48000), null);
  const noise = new Float32Array(4096).map(() => 0.004 * (Math.random() * 2 - 1));
  assert.strictEqual(C.detectMidi(noise, 48000), null);
});

test("perde algılama hızı", () => {
  const buf = voice(196, 48000, 4096);
  const t = Date.now();
  for (let i = 0; i < 50; i++) C.detectMidi(buf, 48000);
  const ms = (Date.now() - t) / 50;
  console.log(`   bir analiz ≈ ${ms.toFixed(2)} ms (saniyede ~22 analiz yapılıyor)`);
  assert.ok(ms < 20);
});

console.log(`\n${passed} test geçti`);
