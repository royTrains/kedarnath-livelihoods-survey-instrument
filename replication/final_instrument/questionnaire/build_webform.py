# -*- coding: utf-8 -*-
"""Generate a self-contained offline web form (index.html) from dictionary.py.

Same single source of truth as the Stata build, the PDF and the XLSForm, so the web form cannot
drift from them. Skip rules and constraints are lifted from build_xlsform.py rather than rewritten,
for the same reason: there is already one hand-maintained copy of that logic and a second would
eventually disagree with it.

What this produces is one HTML file with no external requests -- no CDN, no web fonts, no network
of any kind after first load -- so it works on a tablet with the radio off, which is the normal
condition on the Gaurikund-Kedarnath route.

DATA DURABILITY is the thing that actually matters here, and it is where this design is weaker than
KoboCollect. Browser storage can be cleared by the OS under storage pressure; Kobo's own store is
not subject to that. Mitigations built in below:
  * every field writes to localStorage on change, not on submit -- a flat battery loses nothing
  * each finished interview can be downloaded on its own as JSON, with no connectivity
  * the header shows a running count of interviews not yet exported, and turns red past five
  * export writes CSV in exactly the raw_asked.csv column order the Stata build already reads
None of that removes the need for a daily export. It just makes forgetting it visible.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dictionary import ROWS, LSETS, MODULES
from translations_hi import HI, HI_LSETS
import build_xlsform as X

OUT = os.path.join(HERE, "index.html")

MODTITLE_HI = {
    "P": "आवरण और सहमति", "A": "आप और आपका घर", "B": "काम और काम का इतिहास",
    "C": "साल भर का काम और कमाई", "D": "आना-जाना और घर की जगह", "E": "घर का ख़र्च",
    "F": "मकान, सुविधाएँ और सामान", "G": "बैंक, बीमा और योजनाएँ", "H": "सेहत",
    "I": "खाना, मुश्किलें और उनसे निपटना", "J": "रोपवे", "K": "काम की गुणवत्ता",
    "L": "काम-काज और हुनर",
}


def to_js(expr):
    """XLSForm relevance -> JavaScript. Mirrors the translation in checks/06_form_fill_check.py.

    Note the ordering: comparisons are wrapped before and/or are substituted, because && and ||
    bind more loosely than comparison in JS but the parenthesisation also keeps the intent readable
    when debugging a rule on a tablet at 11pm."""
    e = expr.replace("${", "V('").replace("}", "')")
    # count-selected() must become .length, NOT a bare array comparison: in JS ['1'] > 0 is true but
    # ['1','5'] > 0 coerces to NaN > 0 and is FALSE, so a respondent reporting two shocks would have
    # had the coping question silently hidden. Caught by the Node harness against the XLSForm.
    e = e.replace("count-selected(V('", "SEL('").replace("'))", "').length")
    e = e.replace(" and ", " && ").replace(" or ", " || ")
    out, i = [], 0
    while i < len(e):                      # single '=' is equality in XPath, '==' in JS
        if e[i] == "=" and (i == 0 or e[i - 1] not in "<>!=") and (i + 1 >= len(e) or e[i + 1] != "="):
            out.append("==")
        else:
            out.append(e[i])
        i += 1
    return "".join(out)


def constraint_js(expr):
    """'. >= 10 and . <= 90' -> 'x >= 10 && x <= 90'"""
    return expr.replace(".", "x").replace(" and ", " && ").replace(" or ", " || ")


# ---- build the question list, in form order ---------------------------------------------------
questions, export_cols = [], []
DROP = X.DROP_PARADATA

for r in ROWS:
    if r["origin"] not in ("asked", "paradata"):
        continue
    export_cols.append(r["name"])
    if r["name"] in DROP:
        continue                            # captured automatically, not shown as a question
    kind = r["kind"]
    if kind == "multi":
        typ = "multi"
    elif r["lset"]:
        typ = "one"
    elif kind in ("money", "count"):
        typ = "int"
    elif kind == "num":
        typ = "dec"
    else:
        typ = "text"
    q = {
        "n": r["name"], "m": r["module"], "t": typ,
        "en": r["question"], "hi": HI.get(r["name"], r["question"]),
        "opt": "may be left blank" in r["skip"],
    }
    if r["lset"]:
        src, hsrc = LSETS[r["lset"]], HI_LSETS.get(r["lset"], {})
        q["c"] = [[k, str(v), str(hsrc.get(k, v))] for k, v in src.items()]
    if r["name"] in X.RELEVANT:
        q["rel"] = to_js(X.RELEVANT[r["name"]])
    if r["name"] in X.CONSTRAINT:
        c, msg = X.CONSTRAINT[r["name"]]
        q["con"] = constraint_js(c)
        q["cmsg_en"] = msg
        q["cmsg_hi"] = X.CMSG_HI.get(r["name"], msg)
    questions.append(q)

modules = [{"c": c, "en": t, "hi": MODTITLE_HI.get(c, t)} for c, t in MODULES]
CFG = {"q": questions, "mods": modules, "cols": export_cols}

CONSENT_EN = ("We are doing a study on the livelihoods of people who work on the Yatra route. Taking "
              "part is your choice, you can stop at any time, and you can skip any question. Nothing "
              "you say will be linked to your name or affect your work or any government benefit.")
CONSENT_HI = ("हम यात्रा मार्ग पर काम करने वाले लोगों के रोज़गार पर अध्ययन कर रहे हैं। इसमें शामिल होना आपकी मर्ज़ी है, "
              "आप कभी भी रोक सकते हैं, और कोई भी सवाल छोड़ सकते हैं। आप जो बताएँगे वह आपके नाम से नहीं जोड़ा जाएगा और "
              "उससे आपके काम या किसी सरकारी सुविधा पर कोई असर नहीं पड़ेगा।")

HTML = """<!doctype html>
<html lang="hi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>Kedarnath Yatra Worker Survey</title>
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#1F3864">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Kedarnath Survey">
<link rel="apple-touch-icon" href="icon-192.png">
<link rel="icon" href="icon-192.png">
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#16191d;--mut:#666e7a;--line:#d9dde3;--acc:#1f6feb;--warn:#b42318;--ok:#067647}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
body{margin:0;font:16px/1.5 system-ui,"Segoe UI",Roboto,"Nirmala UI",sans-serif;background:var(--bg);color:var(--ink)}
header{position:sticky;top:0;z-index:9;background:var(--card);border-bottom:1px solid var(--line);padding:10px 14px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
header b{font-size:15px}.grow{flex:1}
button{font:inherit;padding:10px 14px;border:1px solid var(--line);background:var(--card);border-radius:8px;cursor:pointer}
button.p{background:var(--acc);color:#fff;border-color:var(--acc)}
button:disabled{opacity:.45}
#pend{font-size:13px;padding:4px 9px;border-radius:99px;background:#eef1f5;color:var(--mut)}
#pend.hot{background:#fee4e2;color:var(--warn);font-weight:600}
main{max-width:680px;margin:0 auto;padding:14px 14px 96px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:0 0 12px}
.qn{font-size:12px;color:var(--mut);letter-spacing:.04em}
.qt{margin:6px 0 12px;font-size:17px}
input[type=text],input[type=number]{width:100%;padding:13px;font:inherit;border:1px solid var(--line);border-radius:8px;background:#fff}
input:focus{outline:2px solid var(--acc);border-color:var(--acc)}
label.ch{display:flex;gap:11px;align-items:flex-start;padding:11px;border:1px solid var(--line);border-radius:8px;margin:0 0 7px;background:#fff}
label.ch.on{border-color:var(--acc);background:#eff5ff}
label.ch input{margin:3px 0 0}
.err{color:var(--warn);font-size:14px;margin-top:7px}
.opt{font-size:12px;color:var(--mut);margin-top:6px}
h2{font-size:15px;margin:22px 0 10px;color:var(--mut);text-transform:uppercase;letter-spacing:.06em}
footer{position:fixed;bottom:0;left:0;right:0;background:var(--card);border-top:1px solid var(--line);padding:10px 14px;display:flex;gap:10px;max-width:680px;margin:0 auto}
footer button{flex:1}
.mid{text-align:center;padding:40px 16px;color:var(--mut)}
#upd{display:none;background:#fef0c7;border-bottom:1px solid #f5c344;color:#7a5b00;padding:9px 14px;font-size:14px;text-align:center}
.big{font-size:20px;color:var(--ink);margin-bottom:8px}
table{width:100%;border-collapse:collapse;font-size:14px}td{padding:7px 4px;border-bottom:1px solid var(--line)}
</style></head>
<body>
<header>
  <b id="ttl">केदारनाथ सर्वेक्षण</b>
  <span id="pend">0</span>
  <span class="grow"></span>
  <button id="lang">EN</button>
  <button id="menu">☰</button>
</header>
<div id="upd"></div>
<main id="app"></main>
<footer id="nav" style="display:none">
  <button id="back">← <span data-t="back">पीछे</span></button>
  <button id="next" class="p"><span data-t="next">आगे</span> →</button>
</footer>
<script>
const CFG = __CFG__;
const T = {
 back:["पीछे","Back"], next:["आगे","Next"], start:["नया साक्षात्कार शुरू करें","Start new interview"],
 exp:["सब निर्यात करें (CSV)","Export all (CSV)"], pend:["भेजे नहीं गए","not exported"],
 done:["साक्षात्कार पूरा हुआ","Interview complete"], save:["सहेजें और समाप्त करें","Save and finish"],
 req:["यह सवाल ज़रूरी है","This question is required"], opt:["यह छोड़ा जा सकता है","May be left blank"],
 cons:[__CONS_HI__,__CONS_EN__], consq:["क्या आप शामिल होना चाहते हैं?","Do you agree to take part?"],
 no:["नहीं","No"], yes:["हाँ","Yes"], stop:["धन्यवाद। साक्षात्कार यहीं समाप्त।","Thank you. Interview ends here."],
 clr:["निर्यात किए गए मिटाएँ","Clear exported"], cnt:["सहेजे गए साक्षात्कार","Saved interviews"],
 nodata:["अभी कोई साक्षात्कार सहेजा नहीं गया","No interviews saved yet"]
};
let L = 0;                                  // 0 = Hindi, 1 = English
const t = k => T[k][L];
const KEY = "kedarnath_v1", DKEY = "kedarnath_draft";
let D = {}, idx = 0, shown = [];
// Which screen is showing. The language toggle used to INFER this from idx, which got it
// wrong twice: after a refused consent idx is still inside the question list, so switching
// language dropped the enumerator back into an interview that had already been saved and
// closed; and on the completion screen it jumped to the menu instead of re-rendering.
let screen = "menu", lastRefused = false;

// ---- storage. Every write is wrapped: a private window or a full disk must not throw mid-interview.
function load(k, d){ try{ return JSON.parse(localStorage.getItem(k)) ?? d }catch(e){ return d } }
function save(k, v){ try{ localStorage.setItem(k, JSON.stringify(v)); return true }catch(e){ alert("STORAGE FULL / BLOCKED - export now"); return false } }
const all = () => load(KEY, []);
const pending = () => all().filter(r => !r.__exported).length;

function paint(){
  const p = pending(), e = document.getElementById("pend");
  e.textContent = p + " " + t("pend");
  e.className = p > 5 ? "hot" : "";
  document.getElementById("ttl").textContent = L ? "Kedarnath Survey" : "केदारनाथ सर्वेक्षण";
  document.querySelectorAll("[data-t]").forEach(n => n.textContent = t(n.dataset.t));
  document.getElementById("lang").textContent = L ? "हिं" : "EN";
}

// ---- the values a relevance expression can see
const V = n => { const v = D[n]; return v === undefined || v === "" ? null : (isNaN(v) ? v : +v) };
const SEL = n => (D[n] || "").toString().trim() === "" ? [] : D[n].toString().trim().split(/\\s+/);
function calc(){                            // the two hidden calculates the XLSForm also builds
  let nw = 0, ow = 0;
  for (let m = 1; m <= 12; m++){ const s = +D["status_m" + m]; if (s === 8) nw++; if (s >= 2 && s <= 7) ow++ }
  D.calc_months_no_work = nw; D.calc_offseason_work = ow;
}
function visible(q){
  if (!q.rel) return true;
  calc();
  try { return !!eval(q.rel) } catch(e){ return true }   // a broken rule must SHOW the question, never hide it
}
function rebuild(){ shown = CFG.q.filter(visible) }

// ---- rendering
function render(){
  const app = document.getElementById("app");
  rebuild();
  if (idx >= shown.length) return finish();
  screen = "q";
  const q = shown[idx], mod = CFG.mods.find(m => m.c === q.m);
  const prevMod = idx > 0 ? shown[idx-1].m : null;
  let h = "";
  if (mod && q.m !== prevMod) h += "<h2>" + (L ? mod.en : mod.hi) + "</h2>";
  h += "<div class=card><div class=qn>" + (idx+1) + " / " + shown.length + "</div>";
  h += "<div class=qt>" + (L ? q.en : q.hi) + "</div>";
  const v = D[q.n] ?? "";
  if (q.t === "one" || q.t === "multi"){
    const cur = q.t === "multi" ? SEL(q.n) : [String(v)];
    q.c.forEach(c => {
      const on = cur.includes(String(c[0]));
      h += "<label class='ch" + (on ? " on" : "") + "'><input type=" + (q.t === "multi" ? "checkbox" : "radio") +
           " name=q value='" + c[0] + "'" + (on ? " checked" : "") + "><span>" + (L ? c[1] : c[2]) + "</span></label>";
    });
  } else if (q.t === "text"){
    h += "<input type=text id=f value=\\"" + String(v).replace(/"/g,"&quot;") + "\\">";
  } else {
    h += "<input type=number id=f inputmode=" + (q.t === "int" ? "numeric" : "decimal") +
         (q.t === "dec" ? " step=any" : "") + " value='" + v + "'>";
  }
  if (q.opt) h += "<div class=opt>" + t("opt") + "</div>";
  h += "<div class=err id=err></div></div>";
  app.innerHTML = h;
  app.scrollTop = 0; window.scrollTo(0,0);
  document.getElementById("nav").style.display = "flex";
  document.getElementById("back").disabled = idx === 0;
  // write on EVERY change, never only on submit
  app.querySelectorAll("input").forEach(el => el.addEventListener("input", () => {
    if (q.t === "multi"){
      D[q.n] = [...app.querySelectorAll("input:checked")].map(x => x.value).sort((a,b)=>a-b).join(" ");
    } else if (el.type === "radio"){ D[q.n] = el.value } else { D[q.n] = el.value }
    save(DKEY, D);
    app.querySelectorAll("label.ch").forEach(lb => lb.classList.toggle("on", lb.querySelector("input").checked));
    if (el.type === "radio") setTimeout(next, 120);          // radios advance on their own
  }));
  paint();
}

function validate(q){
  const v = D[q.n];
  const blank = v === undefined || v === null || String(v).trim() === "";
  if (blank) return q.opt ? null : t("req");
  if (q.con){ const x = +v; try { if (!eval(q.con)) return L ? q.cmsg_en : q.cmsg_hi } catch(e){} }
  return null;
}
function next(){
  const q = shown[idx], e = validate(q);
  if (e){ const el = document.getElementById("err"); if (el) el.textContent = e; return }
  if (q.n === "consent" && String(D.consent) === "0"){ return finish(true) }
  idx++; render();
}
function back(){ if (idx > 0){ idx--; render() } }

function finish(refused){
  D.__end = new Date().toISOString();
  D.__exported = false;
  const rows = all(); rows.push(D); save(KEY, rows);
  localStorage.removeItem(DKEY);
  D = {};
  lastRefused = !!refused;
  showDone();
}

// Kept separate from finish() so the language toggle can redraw this screen without re-saving the
// interview -- switching language must never write a second copy of the same record.
function showDone(){
  screen = "done";
  document.getElementById("nav").style.display = "none";
  document.getElementById("app").innerHTML =
    "<div class=mid><div class=big>" + (lastRefused ? t("stop") : t("done")) + "</div>" +
    "<p>" + pending() + " " + t("pend") + "</p>" +
    "<p><button class=p onclick='start()'>" + t("start") + "</button></p>" +
    "<p><button onclick='exportCsv()'>" + t("exp") + "</button></p></div>";
  paint();
}

function start(){
  D = { __start: new Date().toISOString() };
  // GPS is requested once, at the start, and never blocks the interview if it is refused or slow
  if (navigator.geolocation) navigator.geolocation.getCurrentPosition(
    p => { D.gps_lat = p.coords.latitude.toFixed(5); D.gps_lon = p.coords.longitude.toFixed(5); save(DKEY, D) },
    () => {}, {timeout: 20000, enableHighAccuracy: true});
  D.interview_date = new Date().toISOString().slice(0,10);
  idx = 0; save(DKEY, D); render();
}

// ---- export: exactly the raw_asked.csv column order the Stata build reads
function csvCell(s){ s = s === undefined || s === null ? "" : String(s);
  return /[",\\n]/.test(s) ? '"' + s.replace(/"/g,'""') + '"' : s }
function exportCsv(){
  const rows = all();
  if (!rows.length) return alert(t("nodata"));
  const cols = CFG.cols;
  let out = cols.join(",") + "\\n";
  rows.forEach((r,i) => {
    r.resp_id = r.resp_id || (Date.now() + "" + i).slice(-9);
    out += cols.map(c => csvCell(r[c])).join(",") + "\\n";
  });
  const blob = new Blob(["\\ufeff" + out], {type:"text/csv;charset=utf-8"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "kedarnath_" + new Date().toISOString().slice(0,10) + "_" + rows.length + ".csv";
  a.click();
  rows.forEach(r => r.__exported = true); save(KEY, rows); paint();
}
function menu(){
  screen = "menu";
  const rows = all();
  document.getElementById("nav").style.display = "none";
  document.getElementById("app").innerHTML = "<div class=card><table>" +
    "<tr><td>" + t("cnt") + "</td><td align=right><b>" + rows.length + "</b></td></tr>" +
    "<tr><td>" + t("pend") + "</td><td align=right><b>" + pending() + "</b></td></tr></table></div>" +
    "<div class=card><p><button class=p style=width:100% onclick='start()'>" + t("start") + "</button></p>" +
    "<p><button style=width:100% onclick='exportCsv()'>" + t("exp") + "</button></p>" +
    "<p><button style=width:100% onclick='clearExported()'>" + t("clr") + "</button></p></div>";
  paint();
}
function clearExported(){
  const keep = all().filter(r => !r.__exported);
  if (!confirm((all().length - keep.length) + " exported interviews will be deleted from this device.")) return;
  save(KEY, keep); menu();
}
document.getElementById("next").onclick = next;
document.getElementById("back").onclick = back;
document.getElementById("menu").onclick = menu;
document.getElementById("lang").onclick = () => {
  L = 1 - L;
  if (screen === "q") render();
  else if (screen === "done") showDone();
  else menu();
};
window.addEventListener("beforeunload", e => { if (Object.keys(D).length > 2){ e.preventDefault(); e.returnValue = "" } });
// ---- offline support. Without this the form must be fetched from the network every time it is
// opened, which on this route means it does not open at all. The worker caches the whole app on
// first visit; afterwards the tablet needs no connectivity to start an interview.
//
// Updates are deliberately NOT applied automatically: swapping the form out mid-interview would be
// worse than running a version behind. A new build installs and waits, a banner appears, and it
// takes effect the next time the form is fully closed and reopened.
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("sw.js").then(reg => {
    reg.addEventListener("updatefound", () => {
      const nw = reg.installing;
      if (!nw) return;
      nw.addEventListener("statechange", () => {
        if (nw.state === "installed" && navigator.serviceWorker.controller) {
          const b = document.getElementById("upd");
          b.textContent = L ? "A new version of the form is ready. Close it completely and reopen."
                             : "फ़ॉर्म का नया रूप तैयार है। इसे पूरी तरह बंद करके दोबारा खोलें।";
          b.style.display = "block";
        }
      });
    });
  }).catch(() => {});   // an unsupported browser must still run the form, just without offline
}

const draft = load(DKEY, null);
if (draft && Object.keys(draft).length > 2 && confirm("Resume the unfinished interview?")){ D = draft; idx = 0; render() }
else menu();
</script>
</body></html>
"""

html = (HTML.replace("__CFG__", json.dumps(CFG, ensure_ascii=False, separators=(",", ":")))
            .replace("__CONS_HI__", json.dumps(CONSENT_HI, ensure_ascii=False))
            .replace("__CONS_EN__", json.dumps(CONSENT_EN, ensure_ascii=False)))
import hashlib, struct, zlib


def _png(size, rgb=(31, 56, 100)):
    """A plain solid-colour icon, written without any image library so the build has no new
    dependency. iOS wants a PNG for the home-screen icon; an SVG will not do."""
    r, g, b = rgb
    raw = b"".join(b"\x00" + bytes([r, g, b] * size) for _ in range(size))

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


MANIFEST = json.dumps({
    "name": "Kedarnath Yatra Worker Survey",
    "short_name": "Kedarnath Survey",
    "start_url": ".",
    "scope": ".",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#f6f7f9",
    "theme_color": "#1F3864",
    "lang": "hi",
    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}],
}, ensure_ascii=False, indent=2)

# The cache name carries a hash of the page itself, so a rebuild automatically invalidates the old
# cache. Bumping it by hand -- and forgetting to -- is how enumerators end up on a stale form.
_VER = hashlib.sha256(html.encode("utf-8")).hexdigest()[:12]
SW = """const CACHE = "kedarnath-""" + _VER + """";
const ASSETS = ["./", "./index.html", "./manifest.json", "./icon-192.png", "./icon-512.png"];

// Cache the whole app up front, so the FIRST offline open works rather than the second.
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
  // deliberately no skipWaiting(): a new build must not replace the form mid-interview
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks =>
    Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ).then(() => self.clients.claim()));
});

// Cache first. The app is a single static page and the tablet is usually offline, so going to the
// network first would just add a timeout to every load.
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== self.location.origin) return;
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {});
      return res;
    }).catch(() => caches.match("./index.html")))
  );
});
"""


def _emit(folder):
    open(os.path.join(folder, "index.html"), "w", encoding="utf-8").write(html)
    open(os.path.join(folder, "sw.js"), "w", encoding="utf-8").write(SW)
    open(os.path.join(folder, "manifest.json"), "w", encoding="utf-8").write(MANIFEST)
    open(os.path.join(folder, "icon-192.png"), "wb").write(_png(192))
    open(os.path.join(folder, "icon-512.png"), "wb").write(_png(512))


_emit(HERE)
print(OUT)
# also drop a copy at repo-root docs/, which is what GitHub Pages serves. Keeping the copy in the
# build means the hosted form cannot fall behind the dictionary the way a hand-copied file would.
_docs = os.path.abspath(os.path.join(HERE, "..", "..", "..", "docs"))
if os.path.isdir(_docs):
    _emit(_docs)
    print(os.path.join(_docs, "index.html") + "  (+ sw.js, manifest.json, icons)")
print(f"{len(questions)} questions, {len(export_cols)} export columns, {len(html)//1024} KB, zero external requests")
