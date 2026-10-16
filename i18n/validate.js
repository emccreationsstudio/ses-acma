// node validate.js xx  -> compares lang/xx.js with en.js
const path = require("path");
const en = require("./en.js"), code = process.argv[2];
const xx = require(path.join(__dirname, code + ".js"));
let errs = [];
function walk(a, b, p) {
  if (typeof a === "function") {
    if (typeof b !== "function") return errs.push(p + " should be function");
    if (a.length !== b.length) errs.push(p + ` arity ${b.length} != ${a.length}`);
    const args = [3, 7, 2, 5].slice(0, a.length);
    try { const r = b(...args); if (typeof r !== "string" || !r.trim()) errs.push(p + " returns non-string"); if (/undefined|NaN|\$\{/.test(r)) errs.push(p + " bad output: " + r); } catch (e) { errs.push(p + " throws " + e.message); }
    return;
  }
  if (Array.isArray(a)) { if (!Array.isArray(b) || a.length !== b.length) return errs.push(p + " array length"); a.forEach((v, i) => walk(v, b[i], p + "[" + i + "]")); return; }
  if (a && typeof a === "object") {
    if (!b || typeof b !== "object") return errs.push(p + " missing object");
    for (const k of Object.keys(a)) walk(a[k], b[k], p + "." + k);
    for (const k of Object.keys(b)) if (!(k in a) && !(p === code && (k === "notes" || k === "langName"))) errs.push(p + "." + k + " extra key");
    return;
  }
  if (typeof b !== typeof a) return errs.push(p + ` type ${typeof b}`);
  if (typeof a === "string" && !b.trim() && a.trim()) errs.push(p + " empty");
}
walk(en, xx, code);
if (!xx.langName) errs.push("langName missing (native language name, e.g. Deutsch)");
if (!Array.isArray(xx.notes) || xx.notes.length !== 12) errs.push("notes must be 12 note names");
console.log(errs.length ? errs.join("\n") : `${code}: OK`);
process.exit(errs.length ? 1 : 0);
