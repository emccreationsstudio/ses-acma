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
  assert.strictEqual(C.pickLanguage("de-DE"), "de");
  assert.strictEqual(C.pickLanguage("pt-BR"), "pt");
  assert.strictEqual(C.pickLanguage("zh-Hans-CN"), "zh");
  assert.strictEqual(C.pickLanguage("ko-KR"), "en");
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

// ---------- Kulak eğitimi ----------
function seeded(seed) { let x = seed >>> 0 || 1; return () => { x = (x * 1664525 + 1013904223) >>> 0; return x / 4294967296; }; }

test("kulak: her tür ve seviyede geçerli soru üretilir", () => {
  const rng = seeded(7);
  for (const type of C.EAR_TYPES) for (const level of C.EAR_LEVELS) for (let i = 0; i < 300; i++) {
    const q = C.makeEarQuestion(type, level, rng, { voiceLo: 48, voiceHi: 60 });
    assert.ok(q.play.length > 0 && q.len > 0, `${type}/${level} çalınacak bir şey yok`);
    for (const ev of q.play) for (const n of ev.notes) assert.ok(n >= 36 && n <= 84, `${type}/${level} nota aralık dışı: ${n}`);
    if (type !== "sing" && type !== "note") assert.ok(q.choices.includes(q.answer), `${type}/${level} cevap seçeneklerde yok`);
    if (type !== "sing") assert.ok(C.checkEarAnswer(q, type === "note" ? q.target : q.answer));
  }
});

test("kulak: nota bulma oktavı önemsemez, kolay seviyede siyah tuş sormaz", () => {
  const rng = seeded(3);
  for (let i = 0; i < 200; i++) {
    const q = C.makeEarQuestion("note", "easy", rng);
    assert.ok(!C.isBlack(q.target), "kolayda siyah tuş");
    assert.ok(C.checkEarAnswer(q, q.target + 12) && C.checkEarAnswer(q, q.target - 12));
    assert.ok(!C.checkEarAnswer(q, q.target + 1));
  }
  for (let i = 0; i < 200; i++) { const q = C.makeEarQuestion("note", "adv", rng); assert.notStrictEqual(q.target % 12, q.ref % 12); }
});

test("kulak: aralıklar doğru ölçülür, kolay seviyede yalnızca 3'lü, 5'li, oktav", () => {
  const rng = seeded(11);
  for (const level of C.EAR_LEVELS) for (let i = 0; i < 200; i++) {
    const q = C.makeEarQuestion("interval", level, rng);
    assert.strictEqual(Math.abs(q.b - q.a), q.answer);
    if (level === "easy") assert.ok([4, 7, 12].includes(q.answer));
    if (level !== "adv") assert.ok(!q.down && !q.harmonic);
  }
  assert.strictEqual(C.INTERVAL_NAMES.tr.length, 13);
  assert.strictEqual(C.INTERVAL_NAMES.tr[7], "Tam 5'li");
});

test("kulak: hangisi yüksek — cevap gerçekten yüksek olan ses; zor seviyede fark yarım tondan az", () => {
  const rng = seeded(5);
  for (const level of C.EAR_LEVELS) for (let i = 0; i < 200; i++) {
    const q = C.makeEarQuestion("higher", level, rng);
    assert.strictEqual(q.answer, q.n1 > q.n2 ? 1 : 2);
    if (level === "adv") assert.ok(q.diff > 0.2 && q.diff < 0.61);
    else assert.ok(q.diff >= 1);
  }
});

test("kulak: akor notaları akor türüyle uyumlu", () => {
  const rng = seeded(9);
  for (const level of C.EAR_LEVELS) for (let i = 0; i < 100; i++) {
    const q = C.makeEarQuestion("chord", level, rng);
    assert.deepStrictEqual(q.notes.map((n) => n - q.root), C.CHORD_TYPES[q.kind]);
    assert.ok(C.CHORD_SETS[level].includes(q.kind));
  }
  for (const lang of ["tr", "en"]) for (const k of Object.keys(C.CHORD_TYPES)) assert.ok(C.CHORD_NAMES[lang][k]);
});

test("kulak: söyleme melodisi kullanıcının ses aralığında kalır", () => {
  const rng = seeded(13);
  for (const [lo, hi] of [[43, 55], [48, 60], [55, 67], [60, 72], [60, 67]]) for (let i = 0; i < 200; i++) {
    const q = C.makeEarQuestion("sing", "adv", rng, { voiceLo: lo, voiceHi: hi });
    assert.strictEqual(q.targets.length, 5);
    for (const m of q.targets) assert.ok(m >= lo && m <= hi + 2, `${lo}-${hi}: ${m}`);
  }
  assert.strictEqual(C.makeEarQuestion("sing", "easy", rng).targets.length, 1);
  assert.strictEqual(C.makeEarQuestion("sing", "mid", rng).targets.length, 3);
});

test("kulak: söylenen nota puanlaması (oktav ve küçük sapma kabul)", () => {
  assert.ok(C.gradeSungNote([60.1, 59.9, 60.2, 60, null], 60));
  assert.ok(C.gradeSungNote([48.1, 47.9, 48.2, 48], 60), "bir oktav aşağısı");
  assert.ok(!C.gradeSungNote([61, 61.1, 60.9, 61], 60), "yarım ton yanlış");
  assert.ok(!C.gradeSungNote([null, null, 60, null], 60), "çok az ses");
  assert.ok(C.singPassed(1, 1) && !C.singPassed(0, 1));
  assert.ok(C.singPassed(2, 3) && !C.singPassed(1, 3));
  assert.ok(C.singPassed(4, 5) && !C.singPassed(3, 5));
});

test("kulak testi: plan ve sonuç", () => {
  const plan = C.earTestPlan(true);
  assert.strictEqual(plan.length, 15);
  assert.deepStrictEqual(plan.slice(0, 5).map((p) => p.level), ["easy", "easy", "easy", "easy", "easy"]);
  assert.strictEqual(plan[14].level, "adv");
  assert.strictEqual(C.earTestPlan(false).length, 12);
  assert.ok(!C.earTestPlan(false).some((p) => p.type === "sing"));
  const all = plan.map((p) => ({ ...p, ok: true }));
  assert.deepStrictEqual([C.earTestSummary(all).pct, C.earTestSummary(all).rank, C.earTestSummary(all).weakest], [100, "adv", null]);
  const none = plan.map((p) => ({ ...p, ok: false }));
  assert.strictEqual(C.earTestSummary(none).rank, "easy");
  const someBad = plan.map((p) => ({ ...p, ok: p.type !== "chord" }));
  const r = C.earTestSummary(someBad);
  assert.strictEqual(r.weakest, "chord");
  assert.strictEqual(r.rank, "adv");
  const easyOnly = plan.map((p) => ({ ...p, ok: p.level === "easy" }));
  assert.strictEqual(C.earTestSummary(easyOnly).rank, "easy");
  const easyMid = plan.map((p) => ({ ...p, ok: p.level !== "adv" }));
  assert.strictEqual(C.earTestSummary(easyMid).rank, "mid");
});

test("kulak: metinler iki dilde eksiksiz", () => {
  const keys = (o, p = "") => Object.entries(o).flatMap(([k, v]) => (v && typeof v === "object" ? keys(v, p + k + ".") : [p + k]));
  assert.deepStrictEqual(keys(C.STRINGS.tr.ear).sort(), keys(C.STRINGS.en.ear).sort());
  for (const lang of ["tr", "en"]) for (const t of C.EAR_TYPES) assert.ok(C.STRINGS[lang].ear.types[t].name && C.STRINGS[lang].ear.types[t].desc);
});

// ---------- Konservatuvar ----------
test("konservatuvar: sesler kullanıcının ses aralığında, akorlar doğru kurulur", () => {
  const rng = seeded(21);
  for (const [lo, hi] of [[43, 55], [48, 60], [55, 67], [60, 72], [60, 67]]) for (const level of C.EAR_LEVELS) for (let i = 0; i < 150; i++) {
    const one = C.makeConsQuestion("c_one", level, rng, { voiceLo: lo, voiceHi: hi });
    assert.ok(one.targets[0] >= lo && one.targets[0] <= hi);
    const two = C.makeConsQuestion("c_two", level, rng, { voiceLo: lo, voiceHi: hi });
    assert.strictEqual(two.targets[1] - two.targets[0], two.interval);
    assert.ok(C.TWO_SETS[level].includes(two.interval));
    assert.ok(two.targets[0] >= lo && two.targets[1] <= Math.max(hi, lo + 12));
    const three = C.makeConsQuestion("c_three", level, rng, { voiceLo: lo, voiceHi: hi });
    assert.strictEqual(three.targets.length, 3);
    assert.ok(three.targets[0] < three.targets[1] && three.targets[1] < three.targets[2], "alttan üste sıralı");
    const pcs = three.targets.map((m) => ((m - three.targets[0]) % 12 + 12) % 12).sort((a, b) => a - b);
    assert.ok(three.targets[0] >= lo);
    if (level === "easy") assert.strictEqual(three.inversion, 0);
    const mel = C.makeConsQuestion("c_melody", level, rng, { voiceLo: lo, voiceHi: hi });
    assert.strictEqual(mel.targets.length, { easy: 4, mid: 6, adv: 8 }[level]);
    for (const m of mel.targets) assert.ok(m >= lo && m <= Math.max(hi, lo + 7) + 2);
  }
});

test("konservatuvar: kolay seviyede iki/üç ses ayrıca tek tek de çalar, zor seviyede çalmaz", () => {
  const rng = seeded(4);
  assert.strictEqual(C.makeConsQuestion("c_two", "easy", rng).play.length, 3);
  assert.strictEqual(C.makeConsQuestion("c_two", "adv", rng).play.length, 1);
  assert.strictEqual(C.makeConsQuestion("c_three", "easy", rng).play.length, 4);
  assert.strictEqual(C.makeConsQuestion("c_three", "adv", rng).play.length, 1);
});

test("konservatuvar: ritim kalıpları geçerli", () => {
  const rng = seeded(8);
  for (const level of C.EAR_LEVELS) for (let i = 0; i < 300; i++) {
    const r = C.makeRhythm(level, rng);
    assert.strictEqual(r.onsets[0], 0, "ilk vuruş başta");
    assert.ok(r.onsets.length >= 4);
    for (let k = 1; k < r.onsets.length; k++) assert.ok(r.onsets[k] > r.onsets[k - 1], "artan zaman");
    assert.ok(r.onsets[r.onsets.length - 1] < r.beats);
    if (level === "easy") for (const o of r.onsets) assert.ok(o * 2 === Math.round(o * 2), "kolayda sekizlikten kısa yok");
  }
  const q = C.makeConsQuestion("c_rhythm", "mid", rng);
  assert.strictEqual(q.play.length, q.onsets.length + 2, "iki sayış + ritim");
  assert.ok(q.len > q.onsetsSec[q.onsetsSec.length - 1]);
});

test("konservatuvar: ritim puanlaması başlama anından bağımsız", () => {
  const on = [1.5, 2.25, 2.625, 3.0];
  assert.ok(C.gradeRhythm(on.map((t) => t + 10.37), on, 0.12).ok, "aynı ritim, farklı başlangıç");
  assert.ok(C.gradeRhythm([10, 10.8, 11.13, 11.5], on, 0.12).ok, "küçük sapmalar kabul");
  assert.ok(!C.gradeRhythm([10, 10.5, 11.13, 11.5], on, 0.12).ok, "kaymış vuruş");
  const r = C.gradeRhythm([10, 10.75, 11.3, 11.5], on, 0.12);
  assert.strictEqual(r.hits, 3);
  assert.ok(!C.gradeRhythm([10, 10.75, 11.125], on, 0.12).ok, "eksik vuruş");
  assert.ok(!C.gradeRhythm([], on).ok);
});

test("konservatuvar: sınav provası planı ve sonuç", () => {
  const plan = C.consExamPlan();
  assert.strictEqual(plan.length, 11);
  for (const t of C.CONS_TYPES) assert.ok(plan.some((p) => p.type === t), t);
  const all = plan.map((p) => ({ ...p, ok: true, part: 1 }));
  const r1 = C.consExamSummary(all);
  assert.strictEqual(r1.pct, 100); assert.strictEqual(r1.weakest, null);
  const mixed = plan.map((p) => ({ ...p, ok: p.type !== "c_rhythm", part: p.type === "c_rhythm" ? 0.5 : 1 }));
  const r2 = C.consExamSummary(mixed);
  assert.strictEqual(r2.areas.rhythm.pct, 50);
  assert.strictEqual(r2.areas.pitch.pct, 100);
  assert.strictEqual(r2.weakest, "rhythm");
  assert.strictEqual(r2.pct, Math.round((100 + 100 + 50) / 3));
  assert.ok(C.CONS_PLAYS >= 1);
});

test("konservatuvar: metinler iki dilde eksiksiz", () => {
  const keys = (o, p = "") => Object.entries(o).flatMap(([k, v]) => (v && typeof v === "object" ? keys(v, p + k + ".") : [p + k]));
  assert.deepStrictEqual(keys(C.STRINGS.tr.cons).sort(), keys(C.STRINGS.en.cons).sort());
  for (const lang of ["tr", "en"]) for (const t of [...C.CONS_TYPES, ...C.CONS_SOON]) assert.ok(C.STRINGS[lang].cons.types[t].name);
});

test("söyleme ışığı: doğru / pes / tiz (oktav önemsiz)", () => {
  assert.strictEqual(C.pitchState(60.2, 60).state, "ok");
  assert.strictEqual(C.pitchState(48.1, 60).state, "ok", "bir oktav aşağı");
  assert.strictEqual(C.pitchState(59.2, 60).state, "low");
  assert.strictEqual(C.pitchState(60.8, 60).state, "high");
  assert.ok(C.pitchState(58, 60).far && !C.pitchState(59.2, 60).far);
  assert.strictEqual(C.pitchState(null, 60).state, "none");
});

test("dil paketi: 10 dil, her dilde aynı yapı ve tüm metinler", () => {
  assert.strictEqual(C.LANGS.length, 10);
  const walk = (a, b, p) => {
    if (typeof a === "function") {
      assert.strictEqual(typeof b, "function", p); assert.strictEqual(b.length, a.length, p + " param");
      const r = b(...[3, 7, 2, 5].slice(0, a.length)); assert.ok(typeof r === "string" && r.trim() && !/undefined|NaN/.test(r), p + " -> " + r); return;
    }
    if (Array.isArray(a)) { assert.ok(Array.isArray(b) && b.length === a.length, p); a.forEach((v, i) => walk(v, b[i], p + i)); return; }
    if (a && typeof a === "object") { assert.ok(b && typeof b === "object", p); assert.deepStrictEqual(Object.keys(b).sort(), Object.keys(a).sort(), p); for (const k in a) walk(a[k], b[k], p + "." + k); return; }
    assert.strictEqual(typeof b, typeof a, p); if (typeof a === "string" && a.trim()) assert.ok(b.trim(), p + " boş");
  };
  for (const [code] of C.LANGS) {
    walk(C.STRINGS.en, C.STRINGS[code], code);
    assert.strictEqual(C.NOTE_NAMES[code].length, 12, code);
    assert.strictEqual(C.INTERVAL_NAMES[code].length, 13, code);
    assert.deepStrictEqual(Object.keys(C.CHORD_NAMES[code]).sort(), Object.keys(C.CHORD_NAMES.en).sort(), code);
    for (const ex of C.EXERCISES) assert.ok(ex.name[code] && ex.syllables[code], ex.id + " " + code);
    assert.ok(C.noteName(60, code).length > 1, code);
  }
});

console.log(`\n${passed} test geçti`);
