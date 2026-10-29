
// ---------- Konservatuvar: Dört Ses, Deşifre Solfej, Melodi Diktesi, Ritim Diktesi, Teori (arayüz) ----------
const STF = { top: 40, gap: 10 };
const stY = (d) => 80 - (d - 30) * 5;
const SHARP_STEPS = [38, 35, 39, 36, 33];
function staffSVG(o) {
  const notes = o.notes || [], key = o.key || 0, time = o.time || null;
  const x0 = 46 + key * 10 + (time ? 22 : 0);
  const n = Math.max(notes.length, o.slots || 0, 1);
  const sp = o.chord ? 0 : Math.max(26, Math.min(44, (o.w || 340) - x0 - 16) / Math.max(1, n));
  const W = o.chord ? x0 + 60 : Math.max(o.w || 340, x0 + sp * n + 16);
  let g = "";
  for (let i = 0; i < 5; i++) g += `<line x1="4" x2="${W - 4}" y1="${40 + i * 10}" y2="${40 + i * 10}" class="st-l"/>`;
  g += `<text x="6" y="88" class="st-clef">𝄞</text>`;
  for (let i = 0; i < key; i++) g += `<text x="${44 + i * 10}" y="${stY(SHARP_STEPS[i]) + 6}" class="st-acc">♯</text>`;
  if (time) g += `<text x="${46 + key * 10}" y="59" class="st-time">${time[0]}</text><text x="${46 + key * 10}" y="79" class="st-time">${time[1]}</text>`;
  const head = (x, d, cls) => {
    const y = stY(d); let s = "";
    for (let l = 28; l >= d; l -= 2) s += `<line x1="${x - 10}" x2="${x + 10}" y1="${stY(l)}" y2="${stY(l)}" class="st-l"/>`;
    for (let l = 40; l <= d; l += 2) s += `<line x1="${x - 10}" x2="${x + 10}" y1="${stY(l)}" y2="${stY(l)}" class="st-l"/>`;
    return s + `<ellipse cx="${x}" cy="${y}" rx="6.4" ry="4.6" transform="rotate(-20 ${x} ${y})" class="st-h ${cls || ""}"/>`;
  };
  const stem = (x, ds, cls) => {
    const lo = Math.min(...ds), hi = Math.max(...ds), up = (lo + hi) / 2 < 34;
    return up ? `<line x1="${x + 5.8}" x2="${x + 5.8}" y1="${stY(lo)}" y2="${stY(hi) - 32}" class="st-s ${cls || ""}"/>`
      : `<line x1="${x - 5.8}" x2="${x - 5.8}" y1="${stY(hi)}" y2="${stY(lo) + 32}" class="st-s ${cls || ""}"/>`;
  };
  const steps = notes.map(staffStep);
  if (o.chord) {
    const x = x0 + 22; steps.forEach((d) => (g += head(x, d))); g += stem(x, steps);
  } else {
    steps.forEach((d, i) => { const x = x0 + sp * (i + 0.5), cls = (o.cls && o.cls[i]) || ""; g += head(x, d, cls) + stem(x, [d], cls); });
  }
  return `<svg class="staff" viewBox="0 0 ${W} 112" preserveAspectRatio="xMidYMid meet" data-x0="${x0}" data-sp="${sp}">${g}</svg>`;
}
/** Ritim kalıbı simgesi (bir vuruş). */
function cellSVG(c) {
  const key = JSON.stringify(c), y = 34, top = 8;
  const H = (x, filled = true) => `<ellipse cx="${x}" cy="${y}" rx="5.4" ry="4" transform="rotate(-20 ${x} ${y})" class="rc-h"/>`;
  const S = (x) => `<line x1="${x + 4.8}" x2="${x + 4.8}" y1="${y - 1}" y2="${top}" class="rc-s"/>`;
  const B = (a, b, lv = 0) => `<rect x="${a + 4.8}" y="${top + lv * 6}" width="${b}" height="3.6" class="rc-b"/>`;
  const flag = (x) => `<path d="M${x + 4.8} ${top} q 9 7 4 16" class="rc-f"/>`;
  const qrest = (x) => `<path d="M${x - 3} ${top + 4} l 6 7 l -6 6 l 6 7 q -8 -2 -3 6" class="rc-r"/>`;
  const erest = (x) => `<circle cx="${x - 2}" cy="${y - 12}" r="2.6" class="rc-rd"/><path d="M${x - 2} ${y - 10} q 5 1 7 -3 l -6 16" class="rc-r"/>`;
  let s = "";
  switch (key) {
    case "[0]": s = H(26) + S(26); break;
    case "[]": s = qrest(28); break;
    case "[0,0.5]": s = H(14) + S(14) + H(36) + S(36) + B(14, 22); break;
    case "[0.5]": s = erest(16) + H(36) + S(36) + flag(36); break;
    case "[0,0.75]": s = H(12) + S(12) + `<circle cx="22" cy="${y - 2}" r="1.6" class="rc-rd"/>` + H(38) + S(38) + B(12, 26) + `<rect x="${38 - 2}" y="${top + 6}" width="7" height="3.4" class="rc-b"/>`; break;
    case "[0,0.25,0.5,0.75]": s = [6, 18, 30, 42].map((x) => H(x) + S(x)).join("") + B(6, 36) + B(6, 36, 1); break;
    case "[0,0.25,0.5]": s = [8, 21, 38].map((x) => H(x) + S(x)).join("") + B(8, 30) + B(8, 13, 1); break;
    case "[0,0.5,0.75]": s = [8, 25, 38].map((x) => H(x) + S(x)).join("") + B(8, 30) + B(25, 13, 1); break;
  }
  return `<svg class="rcell" viewBox="0 0 54 46" aria-hidden="true">${s}</svg>`;
}
const DICT = { notes: [], cells: [] };
function dictRender() {
  const q = ear.q, box = $("earDict"), c = CXS();
  if (q.type === "c_mdict") {
    $("earStaff").innerHTML = staffSVG({ notes: [60, ...DICT.notes], slots: q.melody.length, cls: ["given"] });
    const svg = $("earStaff").querySelector("svg");
    svg.onpointerdown = (e) => {
      if (ear.answered || DICT.notes.length >= q.melody.length - 1) return;
      const r = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal;
      const k = Math.min(r.width / vb.width, r.height / vb.height), oy = (r.height - vb.height * k) / 2;
      const y = (e.clientY - r.top - oy) / k;
      const d = Math.max(26, Math.min(40, Math.round(30 + (80 - y) / 5)));
      DICT.notes.push(stepToMidi(d)); piano.ensure(); piano.play(stepToMidi(d), piano.ctx.currentTime + 0.01, 0.5, 0.8); dictRender();
    };
  } else {
    $("earStaff").innerHTML = `<div class="rslots">${Array.from({ length: 4 }, (_, i) => `<span class="rslot${i === DICT.cells.length ? " cur" : ""}">${DICT.cells[i] ? cellSVG(DICT.cells[i]) : ""}</span>`).join("")}</div>`;
  }
  const full = q.type === "c_mdict" ? DICT.notes.length >= q.melody.length - 1 : DICT.cells.length >= 4;
  box.querySelectorAll(".dpick").forEach((b) => (b.disabled = ear.answered || full));
  $("dUndo").disabled = ear.answered || !(q.type === "c_mdict" ? DICT.notes.length : DICT.cells.length);
  $("dCheck").disabled = ear.answered || !full;
  $("dUndo").textContent = c.undo; $("dCheck").textContent = c.check;
}
function dictSetup(q) {
  DICT.notes = []; DICT.cells = [];
  const box = $("earDict"); box.hidden = false; $("earStaff").hidden = false;
  let pal = "";
  if (q.type === "c_mdict") pal = [60, 62, 64, 65, 67, 69, 71, 72].map((m) => `<button type="button" class="dpick" data-m="${m}">${NOTE_NAMES[state.lang][m % 12]}${m === 72 ? "'" : ""}</button>`).join("");
  else pal = q.palette.map((c, i) => `<button type="button" class="dpick rpick" data-i="${i}" aria-label="${i + 1}">${cellSVG(c)}</button>`).join("");
  box.innerHTML = `<div class="dpal${q.type === "c_rdict" ? " rpal" : ""}">${pal}</div><div class="dact"><button type="button" class="ghost-btn" id="dUndo"></button><button type="button" class="ghost-btn gold" id="dCheck"></button></div>`;
  box.querySelectorAll(".dpick").forEach((b) => (b.onclick = () => {
    if (q.type === "c_mdict") { const m = Number(b.dataset.m); DICT.notes.push(m); piano.ensure(); piano.play(m, piano.ctx.currentTime + 0.01, 0.5, 0.8); }
    else DICT.cells.push(q.palette[Number(b.dataset.i)]);
    dictRender();
  }));
  $("dUndo").onclick = () => { (q.type === "c_mdict" ? DICT.notes : DICT.cells).pop(); dictRender(); };
  $("dCheck").onclick = () => dictCheck();
  dictRender();
}
function dictCheck() {
  const q = ear.q, s = ES(), c = CXS();
  if (ear.answered) return;
  let ok, part;
  if (q.type === "c_mdict") {
    const want = q.melody.slice(1), got = DICT.notes;
    const hits = want.map((m, i) => got[i] === m);
    part = hits.filter(Boolean).length / want.length; ok = part === 1;
    $("earStaff").innerHTML = `<small class="st-cap">${c.yours}</small>` + staffSVG({ notes: [60, ...got], cls: ["given", ...hits.map((h) => (h ? "ok" : "no"))] })
      + (ok ? "" : `<small class="st-cap">${c.right}</small>` + staffSVG({ notes: q.melody, cls: ["given"] }));
  } else {
    const hits = q.cells.map((cell, i) => JSON.stringify(cell) === JSON.stringify(DICT.cells[i]));
    part = hits.filter(Boolean).length / 4; ok = part === 1;
    $("earStaff").innerHTML = `<small class="st-cap">${c.yours}</small><div class="rslots">${DICT.cells.map((cl, i) => `<span class="rslot ${hits[i] ? "ok" : "no"}">${cellSVG(cl)}</span>`).join("")}</div>`
      + (ok ? "" : `<small class="st-cap">${c.right}</small><div class="rslots">${q.cells.map((cl) => `<span class="rslot">${cellSVG(cl)}</span>`).join("")}</div>`);
  }
  earRecord(ok, part);
  $("earBig").textContent = ok ? "✓" : `${Math.round(part * 100)}%`;
  $("earFeedback").textContent = ok ? s.correct : `${c.right} ↑`;
  $("earFeedback").className = "ear-fb " + (ok ? "ok" : "no");
  $("earDict").querySelectorAll("button").forEach((b) => (b.disabled = true));
}
