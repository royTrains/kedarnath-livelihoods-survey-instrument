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
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dictionary import ROWS, LSETS, MODULES, INTROS, HINTS, CONSENT_SCRIPT
from translations_hi import HI, HI_LSETS, INTROS_HI, HINTS_HI, CONSENT_SCRIPT_HI
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
    # Both multi-select helpers are matched as whole calls, with a regex each. An earlier version
    # substituted the bare string "'))" to close count-selected(), which also matched the tail of
    # selected(V('x'), '9')) and produced ".includes('9').length" with the parentheses unbalanced --
    # broken JS, which throws, and visible() shows a question whose rule throws. The gate was
    # therefore always open. Order matters too: selected() is a SUBSTRING of count-selected(), so the
    # count form is taken first and the plain form guarded with (?<!-) against matching inside it.
    #
    # count-selected() must become .length and not a bare array comparison: in JS ['1'] > 0 is true
    # but ['1','5'] > 0 coerces to NaN > 0 and is FALSE, so a respondent reporting two shocks would
    # have had the coping question silently hidden.
    e = re.sub(r"count-selected\(V\('(\w+)'\)\)",
               lambda m: "SEL('%s').length" % m.group(1), e)
    # selected(${multi}, 'code') -> membership in the split code list, never a substring test: a
    # substring test for '1' would also match the code 10.
    # A lambda, not a replacement template: a "\1" backreference written into this file through a
    # Python string became a control character, and the rule compiled to SEL('\x01').includes('\x02'),
    # which never throws and never matches -- so that gated question was silently never asked.
    e = re.sub(r"(?<!-)selected\(V\('(\w+)'\),\s*'(\w+)'\)",
               lambda m: "SEL('%s').includes('%s')" % (m.group(1), m.group(2)), e)
    e = e.replace(" and ", " && ").replace(" or ", " || ")
    e = e.replace("not(", "!(")             # XPath not() -> JS !
    out, i = [], 0
    while i < len(e):                      # single '=' is equality in XPath, '==' in JS
        if e[i] == "=" and (i == 0 or e[i - 1] not in "<>!=") and (i + 1 >= len(e) or e[i + 1] != "="):
            out.append("==")
        else:
            out.append(e[i])
        i += 1
    return "".join(out)


def constraint_js(expr):
    """'. >= 10 and . <= 90' -> 'x >= 10 && x <= 90'.

    Must also resolve ${other_field}, because constraints now reference sibling answers -- a count of
    insured members cannot exceed household size. Without this the expression reaches eval() with a
    literal ${...} still in it, throws, and the throw is swallowed by validate()'s try/catch, so the
    constraint silently does nothing. That is worse than never having added it: the form looks like
    it is validating and is not."""
    # A multi-select constraint speaks about the selected CODES, not a number, so the "." that means
    # "this answer" has to become the code list rather than the numeric x. Handled before the numeric
    # path, which would otherwise turn selected(., '9') into selected(x, '9') and throw.
    if "selected(" in expr:
        e = expr.replace("count-selected(.)", "SELF.length").replace("selected(., ", "SELF.includes(")
        e = e.replace(" and ", " && ").replace(" or ", " || ").replace("not(", "!(")
        return e
    e = expr.replace("${", "@REF@").replace("}", "@END@")   # park refs before the dot substitution
    e = e.replace(".", "x").replace(" and ", " && ").replace(" or ", " || ")
    return e.replace("@REF@", "NUM('").replace("@END@", "')")


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
    # the XLSForm's choice_filter has no equivalent in this form, so carry the one rule it needs as
    # data: exclude whatever `occupation` holds from the other-activities list, so a pony owner is not
    # offered "Pony/mule owner" again as a second activity.
    if r["name"] in X.CHOICE_FILTER:
        _f = X.CHOICE_FILTER[r["name"]]
        # two shapes are in use: exclude one answer's value, or keep only the codes ticked in a
        # multi-select. Carried as data so the web form applies the same rule the XLSForm compiles.
        if _f.startswith("selected("):
            q["cfo"] = _f.split("${")[1].split("}")[0]
        else:
            q["cfx"] = _f.split("${")[1].rstrip("}")
    if r["name"] in HINTS:
        q["hn"] = HINTS[r["name"]]
        q["hnh"] = HINTS_HI.get(r["name"], HINTS[r["name"]])
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

modules = [{"c": c, "en": t, "hi": MODTITLE_HI.get(c, t),
            "ien": INTROS.get(c, ""), "ihi": INTROS_HI.get(c, "")} for c, t in MODULES]
# Code -> label, for the readable export. Built for EVERY exported column that carries a value
# label, including the paradata ones that never appear on screen as questions (enum_id), which is
# why this is keyed off ROWS/export_cols rather than off `questions`.
LABS = {}
for r in ROWS:
    if r["origin"] not in ("asked", "paradata") or not r["lset"]:
        continue
    _hs = HI_LSETS.get(r["lset"], {})
    LABS[r["name"]] = {str(k): {"e": str(v), "h": str(_hs.get(k, v))} for k, v in LSETS[r["lset"]].items()}

CFG = {"q": questions, "mods": modules, "cols": export_cols, "labs": LABS}

# The consent script now comes from dictionary.CONSENT_SCRIPT. This file used to hold its own shorter
# paraphrase, which is how two versions of an informed-consent statement came to exist in one repo.
CONSENT_EN, CONSENT_HI = CONSENT_SCRIPT, CONSENT_SCRIPT_HI

HTML = """<!doctype html>
<html lang="hi" translate="no">
<head>
<meta charset="utf-8">
<!-- Stop the browser offering to translate. A Hindi form auto-translated to English turns
     "पक्का" (permanent) into "Sure!" and "जमा पैसे से" (used savings) into "from the deposited
     money" -- the reviewer then critiques wording that was never in the instrument. All three
     signals are needed: Chrome honours the meta, Safari and Edge honour the attribute, and the
     class covers dynamically inserted text. -->
<meta name="google" content="notranslate">
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
/* Enumerator hint: how to CODE this question, never read to the respondent. Amber and rule-marked so
   it is visibly a different kind of thing from the question above it and from the read-aloud intro,
   which is blue. Three kinds of text on one screen need three unmistakable looks. */
.hint{background:#fff8e6;border-left:4px solid #b78103;border-radius:0 6px 6px 0;padding:9px 11px;margin:0 0 11px;font-size:13.5px;color:#5c4708}
.card.off{display:none}
/* The consent script. Read verbatim, so it gets its own look -- green rule, larger text than a hint,
   and the label says word for word. Three read-aloud registers on this form now: blue module intro
   (read it), amber hint (do NOT read it), green consent (read it exactly). */
.consent{background:#f0f7f0;border-left:4px solid var(--ok);border-radius:0 8px 8px 0;padding:13px 15px;margin:0 0 14px;font-size:15.5px}
.consent p{margin:0 0 9px}.consent p:last-child{margin:0}
.consent .lead{display:block;font-size:11.5px;color:var(--ok);text-transform:uppercase;letter-spacing:.06em;font-weight:600;margin-bottom:6px}
.card.bad{border-color:var(--warn);box-shadow:0 0 0 1px var(--warn)}
.mc{font-weight:400;text-transform:none;letter-spacing:0}
.hint b{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.06em;margin-bottom:3px;color:#8a6200}
h2{font-size:15px;margin:22px 0 10px;color:var(--mut);text-transform:uppercase;letter-spacing:.06em}
/* Read-aloud module introduction. Deliberately styled unlike a question card -- tinted, ruled down
   the side, italic lead-in -- so an enumerator glancing at the screen can never mistake it for
   something the respondent is meant to answer. */
.intro{background:#eff5ff;border-left:4px solid var(--acc);border-radius:0 8px 8px 0;padding:12px 14px;margin:0 0 12px;font-size:15px}
.intro .lead{display:block;font-size:12px;color:var(--acc);text-transform:uppercase;letter-spacing:.06em;margin-bottom:5px}
footer{position:fixed;bottom:0;left:0;right:0;background:var(--card);border-top:1px solid var(--line);padding:10px 14px;display:flex;gap:10px;align-items:center;max-width:680px;margin:0 auto}
#mprog{flex:1;text-align:center;font-size:13px;color:var(--mut)}
footer button{flex:1}
.mid{text-align:center;padding:40px 16px;color:var(--mut)}
#upd{display:none;background:#fef0c7;border-bottom:1px solid #f5c344;color:#7a5b00;padding:9px 14px;font-size:14px;text-align:center}
.big{font-size:20px;color:var(--ink);margin-bottom:8px}
table{width:100%;border-collapse:collapse;font-size:14px}td{padding:7px 4px;border-bottom:1px solid var(--line)}
</style></head>
<body class="notranslate" translate="no">
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
  <span id="mprog"></span>
  <button id="next" class="p"><span data-t="next">आगे</span> →</button>
</footer>
<script>
const CFG = __CFG__;
const T = {
 back:["पीछे","Back"], next:["आगे","Next"], start:["नया साक्षात्कार शुरू करें","Start new interview"],
 exp:["सब निर्यात करें — कोड (CSV)","Export all — codes (CSV)"],
 expl:["सब निर्यात करें — जवाब शब्दों में (CSV)","Export all — answers in words (CSV)"], pend:["भेजे नहीं गए","not exported"],
 done:["साक्षात्कार पूरा हुआ","Interview complete"], save:["सहेजें और समाप्त करें","Save and finish"],
 req:["यह सवाल ज़रूरी है","This question is required"], opt:["यह छोड़ा जा सकता है","May be left blank"],
 cons:[__CONS_HI__,__CONS_EN__], consq:["क्या आप शामिल होना चाहते हैं?","Do you agree to take part?"],
 no:["नहीं","No"], yes:["हाँ","Yes"], stop:["धन्यवाद। साक्षात्कार यहीं समाप्त।","Thank you. Interview ends here."],
 clr:["निर्यात किए गए मिटाएँ","Clear exported"], cnt:["सहेजे गए साक्षात्कार","Saved interviews"],
 nodata:["अभी कोई साक्षात्कार सहेजा नहीं गया","No interviews saved yet"],
 // Label on the module-introduction box. Addressed to the enumerator, not the respondent: it is an
 // instruction to speak, which is why it is not in the respondent-facing Hindi of INTROS_HI itself.
 readout:["पढ़कर सुनाएँ","Read aloud"],
 // Label on the enumerator hint. Says plainly that this one is not for the respondent.
 foryou:["सर्वेक्षक के लिए — पढ़कर न सुनाएँ","For the enumerator — do not read out"],
 qs:["सवाल","questions"],
 // Label on the consent script. It is an instruction to the enumerator about HOW to deliver the
 // block below it, which is why it is not part of the script text itself.
 verbatim:["यह ज्यों का त्यों पढ़कर सुनाएँ","Read this out, word for word"]
};
let L = 0;                                  // 0 = Hindi, 1 = English
const t = k => T[k][L];
const KEY = "kedarnath_v1", DKEY = "kedarnath_draft";
let D = {}, shown = [];
const QBY = Object.fromEntries(CFG.q.map(q => [q.n, q]));
// Which screen is showing. The language toggle used to INFER this from idx, which got it
// wrong twice: after a refused consent idx is still inside the question list, so switching
// language dropped the enumerator back into an interview that had already been saved and
// closed; and on the completion screen it jumped to the menu instead of re-rendering.
let screen = "menu", lastRefused = false;
// Position is tracked by question NAME, never by index. shown[] is rebuilt from the relevance
// rules on every render, so answering a gate question changes its length and every index after
// that point silently refers to a different question -- which looked, from the field, like typed
// answers disappearing. `cur` survives that; an index cannot.
// Navigation is per MODULE, not per question: the whole module is on one screen and Next moves to
// the next module. One question per screen meant ~210 taps per interview before anyone had answered
// anything twice. `curMod` is a module CODE, not an index, for the same reason navigation used to be
// keyed on question names -- an index into a list that gates can reshape is the bug that ate the
// enumerator's place once already.
let curMod = null;
const modList = () => CFG.mods.filter(m => CFG.q.some(q => q.m === m.c)).map(m => m.c);
function modPos(code){ const i = modList().indexOf(code); return i < 0 ? 0 : i }

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
// A constraint that names another field needs that field as a NUMBER. An unanswered one must not
// make the constraint fail -- treat it as no limit rather than as zero.
const NUM = n => { const v = +D[n]; return isNaN(v) ? Infinity : v };
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

// ---- rendering: one MODULE per screen ---------------------------------------------------------
// Every question in the module is written into the DOM, including ones a gate currently hides --
// those get `hidden` and are toggled by applyGates() on each keystroke. Hiding with a class rather
// than re-rendering is deliberate: re-rendering the module on every input would throw away focus and
// the caret mid-number, which is precisely the "input is buggy" defect that was fixed once already.
function qBlock(q){
  const v = D[q.n] ?? "";
  let h = "<div class=card data-q='" + q.n + "'>";
  // The consent script is rendered ON the consent question, not as a module preamble. It is the one
  // block in this form that must be read word for word, so it is marked as such and styled unlike
  // both the question and the enumerator hint -- which says the opposite, do not read out.
  if (q.n === "consent"){
    h += "<div class=consent><span class=lead>" + t("verbatim") + "</span>" +
         t("cons").split("\\n\\n").map(x => "<p>" + x + "</p>").join("") + "</div>";
  }
  h += "<div class=qt>" + (L ? q.en : q.hi) + "</div>";
  if (q.hn) h += "<div class=hint><b>" + t("foryou") + "</b>" + (L ? q.hn : q.hnh) + "</div>";
  if (q.t === "one" || q.t === "multi"){
    const sel = q.t === "multi" ? SEL(q.n) : [String(v)];
    const drop = q.cfx ? String(D[q.cfx] ?? "") : "";
    const only = q.cfo ? SEL(q.cfo) : null;
    let opts = q.c;
    if (drop) opts = opts.filter(c => String(c[0]) !== drop);
    if (only) opts = opts.filter(c => only.includes(String(c[0])));
    opts.forEach(c => {
      const on = sel.includes(String(c[0]));
      h += "<label class='ch" + (on ? " on" : "") + "'><input type=" + (q.t === "multi" ? "checkbox" : "radio") +
           " name='q_" + q.n + "' value='" + c[0] + "'" + (on ? " checked" : "") + "><span>" +
           (L ? c[1] : c[2]) + "</span></label>";
    });
  } else if (q.t === "text"){
    h += "<input type=text value=\\"" + String(v).replace(/"/g,"&quot;") + "\\">";
  } else {
    h += "<input type=number inputmode=" + (q.t === "int" ? "numeric" : "decimal") +
         (q.t === "dec" ? " step=any" : "") + " value='" + v + "'>";
  }
  if (q.opt) h += "<div class=opt>" + t("opt") + "</div>";
  h += "<div class=err></div></div>";
  return h;
}

// Clearing answers that a gate has closed is not tidiness, it is correctness. A module shows all its
// questions at once, so this sequence is ordinary: answer origin = "other state", answer "why did you
// first come here", then correct origin to "local". The reason question disappears -- and used to keep
// its answer, which then went into the export and broke the skip-logic asserts on a fact the
// respondent never asserted. Kobo and ODK drop irrelevant answers at submission; this matches them.
function clearHidden(){
  let changed = false;
  CFG.q.forEach(q => {
    if (!visible(q) && D[q.n] !== undefined && D[q.n] !== ""){ delete D[q.n]; changed = true }
  });
  if (changed) save(DKEY, D);
  return changed;
}

// Rebuild the option list of a question whose choices depend on another answer. This has to happen
// as answers land, not only at render: the whole module is on one screen, so `occupation` is answered
// on the SAME screen as other_activity_types, and a list built once at render still carried the
// primary occupation through the entire pass. It only ever looked fixed because leaving the module
// and coming back re-rendered it.
// Only the dependent question's own card is rewritten, never the one being typed into, so nothing
// loses focus or the caret.
// Drop an answer that its own filter has made unavailable -- say the enumerator ticks an activity as
// a second occupation and then names that same activity as the primary one. Done over CFG.q from the
// DATA, not by walking the DOM: a card for a module the enumerator has not opened does not exist, and
// pruning that depended on the card existing would leave the stale answer in the export. Same lesson
// as next() deciding from data rather than from the rendered page.
function pruneFiltered(){
  CFG.q.forEach(q => {
    if (!q.cfx && !q.cfo) return;
    const drop = q.cfx ? String(D[q.cfx] ?? "") : "";
    const only = q.cfo ? SEL(q.cfo) : null;
    let opts = q.c;
    if (drop) opts = opts.filter(c => String(c[0]) !== drop);
    if (only) opts = opts.filter(c => only.includes(String(c[0])));
    const avail = opts.map(c => String(c[0]));
    if (q.t === "multi"){
      const keep = SEL(q.n).filter(v => avail.includes(v));
      if (keep.join(" ") !== String(D[q.n] ?? "")){ D[q.n] = keep.join(" "); save(DKEY, D) }
    } else if (D[q.n] !== undefined && D[q.n] !== "" && !avail.includes(String(D[q.n]))){
      delete D[q.n]; save(DKEY, D);
    }
  });
}

function refilter(){
  document.querySelectorAll("#app .card[data-q]").forEach(card => {
    const q = QBY[card.dataset.q];
    if (!q || (!q.cfx && !q.cfo)) return;
    const key = (q.cfx ? String(D[q.cfx] ?? "") : "") + "|" + (q.cfo ? String(D[q.cfo] ?? "") : "");
    if (card.dataset.filterKey === key) return;          // source unchanged; leave the DOM alone
    card.dataset.filterKey = key;
    const drop = q.cfx ? String(D[q.cfx] ?? "") : "";
    const only = q.cfo ? SEL(q.cfo) : null;
    let opts = q.c;
    if (drop) opts = opts.filter(c => String(c[0]) !== drop);
    if (only) opts = opts.filter(c => only.includes(String(c[0])));
    const sel = q.t === "multi" ? SEL(q.n) : [String(D[q.n] ?? "")];
    let h = "";
    opts.forEach(c => {
      const on = sel.includes(String(c[0]));
      h += "<label class='ch" + (on ? " on" : "") + "'><input type=" + (q.t === "multi" ? "checkbox" : "radio") +
           " name='q_" + q.n + "' value='" + c[0] + "'" + (on ? " checked" : "") + "><span>" +
           (L ? c[1] : c[2]) + "</span></label>";
    });
    card.querySelectorAll("label.ch").forEach(n => n.remove());
    const err = card.querySelector(".err");
    if (err) err.insertAdjacentHTML("beforebegin", h);
    bindCard(card, q);
  });
}

// Attach the write-on-every-change handler. Called from render() and again from refilter() whenever a
// list is rebuilt, since replacing the inputs drops their listeners with them.
function bindCard(card, q){
  if (!q) return;
  card.querySelectorAll("input").forEach(el => {
    if (el.dataset.bound) return;
    el.dataset.bound = "1";
    el.addEventListener("input", () => {
      if (q.t === "multi"){
        D[q.n] = [...card.querySelectorAll("input:checked")].map(x => x.value).sort((a,b)=>a-b).join(" ");
      } else { D[q.n] = el.value }
      save(DKEY, D);
      card.querySelectorAll("label.ch").forEach(lb => lb.classList.toggle("on", lb.querySelector("input").checked));
      const e = card.querySelector(".err"); if (e) e.textContent = "";
      applyGates();
    });
  });
}

function applyGates(){
  calc();
  clearHidden();
  pruneFiltered();
  refilter();
  let n = 0;
  document.querySelectorAll("#app .card[data-q]").forEach(el => {
    const q = QBY[el.dataset.q];
    const on = visible(q);
    el.classList.toggle("off", !on);
    if (on) n++;
  });
  const c = document.getElementById("mcount");
  if (c) c.textContent = n + " " + t("qs");
}

function render(){
  const app = document.getElementById("app");
  const mods = modList();
  if (!mods.length) return finish();
  if (curMod === null) curMod = mods[0];
  screen = "q";
  const mod = CFG.mods.find(m => m.c === curMod);
  const qs = CFG.q.filter(q => q.m === curMod);
  let h = "<h2>" + (L ? mod.en : mod.hi) + " <span id=mcount class=mc></span></h2>";
  const intro = L ? mod.ien : mod.ihi;
  if (intro) h += "<div class=intro><span class=lead>" + t("readout") + "</span>" + intro + "</div>";
  qs.forEach(q => { h += qBlock(q) });
  app.innerHTML = h;
  app.scrollTop = 0; window.scrollTo(0,0);
  document.getElementById("nav").style.display = "flex";
  document.getElementById("back").disabled = modPos(curMod) === 0;
  document.getElementById("mprog").textContent =
    (L ? "Module " : "खंड ") + (modPos(curMod)+1) + " / " + mods.length;

  // write on EVERY change, never only on submit
  app.querySelectorAll(".card[data-q]").forEach(card => bindCard(card, QBY[card.dataset.q]));
  applyGates();
  paint();
}

function validate(q){
  const v = D[q.n];
  const blank = v === undefined || v === null || String(v).trim() === "";
  if (blank) return q.opt ? null : t("req");
  if (q.con){
    const x = +v;                      // numeric constraints read x
    const SELF = SEL(q.n);             // multi-select constraints read the code list
    try { if (!eval(q.con)) return L ? q.cmsg_en : q.cmsg_hi } catch(e){}
  }
  return null;
}

// Validate every question the module is currently SHOWING. A hidden question is not the enumerator's
// problem and must never block the screen -- that is how a gated-off required field used to trap the
// interview with no visible error to fix.
// The decision is computed from DATA, not by reading the DOM. That keeps next() exercisable by the
// headless harness in checks/08, which has no real document -- and a validation path the tests cannot
// reach is one that breaks silently.
function moduleErrors(){
  return CFG.q.filter(q => q.m === curMod && visible(q))
              .map(q => [q, validate(q)]).filter(p => p[1]);
}
function showErrors(errs){
  const byName = Object.fromEntries(errs.map(p => [p[0].n, p[1]]));
  let first = null;
  document.querySelectorAll("#app .card[data-q]").forEach(card => {
    const e = byName[card.dataset.q] || "";
    const slot = card.querySelector(".err");
    if (slot) slot.textContent = e;
    card.classList.toggle("bad", !!e);
    if (e && !first) first = card;
  });
  if (first && first.scrollIntoView) first.scrollIntoView({block:"center"});
}
function next(){
  const errs = moduleErrors();
  showErrors(errs);
  if (errs.length) return;
  if (curMod === "P" && String(D.consent) === "0") return finish(true);
  const mods = modList(), here = modPos(curMod);
  if (here + 1 >= mods.length) return finish();
  curMod = mods[here + 1];
  render();
}
function back(){
  const mods = modList(), here = modPos(curMod);
  if (here <= 0) return;
  curMod = mods[here - 1];
  render();
}

function finish(refused){
  // final sweep: a gate can close a question in a module the enumerator has already left, and that
  // stale answer must not reach the export either.
  calc(); clearHidden();
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
    "<p><button onclick='exportCsv()'>" + t("exp") + "</button></p>" +
    "<p><button onclick='exportCsv(1)'>" + t("expl") + "</button></p></div>";
  paint();
}

function start(){
  D = { __start: new Date().toISOString() };
  // GPS is requested once, at the start, and never blocks the interview if it is refused or slow
  if (navigator.geolocation) navigator.geolocation.getCurrentPosition(
    p => { D.gps_lat = p.coords.latitude.toFixed(5); D.gps_lon = p.coords.longitude.toFixed(5); save(DKEY, D) },
    () => {}, {timeout: 20000, enableHighAccuracy: true});
  D.interview_date = new Date().toISOString().slice(0,10);
  curMod = null; save(DKEY, D); render();
}

// ---- export: exactly the raw_asked.csv column order the Stata build reads
function csvCell(s){ s = s === undefined || s === null ? "" : String(s);
  return /[",\\n]/.test(s) ? '"' + s.replace(/"/g,'""') + '"' : s }
// Code -> the option text that was actually chosen. Multi-selects are stored as space-separated
// codes, so each one is mapped and the labels rejoined with "; " -- a semicolon, not a comma, so a
// labelled multi-select never needs quoting and can never be mistaken for a column break.
function labelOf(col, v){
  const m = CFG.labs[col];
  if (!m || v === undefined || v === null || String(v).trim() === "") return v;
  return String(v).trim().split(/\\s+/).map(x => (m[x] ? (L ? m[x].e : m[x].h) : x)).join("; ");
}
// labelled falsy -> the numeric codes the Stata build reads. labelled truthy -> what the respondent
// actually chose. Same rows, same column order; only coded columns differ, and numbers, dates and
// verbatim text are identical either way.
function exportCsv(labelled){
  const rows = all();
  if (!rows.length) return alert(t("nodata"));
  const cols = CFG.cols;
  let out = cols.join(",") + "\\n";
  rows.forEach((r,i) => {
    r.resp_id = r.resp_id || (Date.now() + "" + i).slice(-9);
    out += cols.map(c => csvCell(labelled ? labelOf(c, r[c]) : r[c])).join(",") + "\\n";
  });
  const blob = new Blob(["\\ufeff" + out], {type:"text/csv;charset=utf-8"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "kedarnath_" + new Date().toISOString().slice(0,10) + "_" + rows.length +
               (labelled ? (L ? "_labels_en" : "_labels_hi") : "") + ".csv";
  a.click();
  // Only the coded export marks records as delivered. Taking a readable copy to check the day's work
  // must not make the interviews look already handed over -- clearExported() deletes on that flag,
  // and losing interviews to a reading convenience would be the worst trade in this whole form.
  if (!labelled){ rows.forEach(r => r.__exported = true); save(KEY, rows) }
  paint();
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
    "<p><button style=width:100% onclick='exportCsv(1)'>" + t("expl") + "</button></p>" +
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
if (draft && Object.keys(draft).length > 2 && confirm("Resume the unfinished interview?")){ D = draft; curMod = null; render() }
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
