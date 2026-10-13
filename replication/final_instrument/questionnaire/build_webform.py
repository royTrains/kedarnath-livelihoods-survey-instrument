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
import datetime as _dt
import io
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dictionary import ROWS, LSETS, MODULES, INTROS, HINTS, CONSENT_SCRIPT, STUDY_BRIEF, HIDDEN_ON_FORM, BUILD
from translations_hi import HI, HI_LSETS, INTROS_HI, HINTS_HI, CONSENT_SCRIPT_HI, STUDY_BRIEF_HI
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
    if r["name"] in HIDDEN_ON_FORM:
        # Rendered by nothing: render() skips type "hidden", and modList() ignores a module whose
        # questions are all hidden, which is what keeps the old cover module from appearing as an
        # empty screen now that all four of its items are set automatically.
        typ = "hidden"
    elif kind == "multi":
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
        # Case-INSENSITIVE on purpose. This read r["skip"] literally until 2026-10-01, so a skip
        # rule that opened with "May be left blank" left the question REQUIRED, with nothing
        # anywhere saying so -- which is how the optional earnings gate shipped still compulsory.
        # A hidden question can never be answered on screen, so it must never be able to block
        # Next. This is not a judgement about whether the value matters -- consent and site matter
        # a great deal -- it is that validate() has no field to point the enumerator at.
        "opt": True if r["name"] in HIDDEN_ON_FORM else "may be left blank" in r["skip"].lower(),
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
    if r["lset"] and typ != "hidden":
        src, hsrc = LSETS[r["lset"]], HI_LSETS.get(r["lset"], {})
        q["c"] = [[k, str(v), str(hsrc.get(k, v))] for k, v in src.items()]
        # Long single-choice lists are drawn as a dropdown. The threshold is on the BUILDER rather
        # than marked per question so it cannot be forgotten when a list grows: at 15 options a
        # column of radio rows is already taller than a phone screen, and the question it belongs
        # to has scrolled off the top by the time the enumerator reaches the bottom of it.
        # Multi-selects are excluded -- "tick all that apply" in a dropdown hides the ticks.
        if typ == "one" and len(src) >= 15:
            q["dd"] = True
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

# A build stamp, shown in the header and written into every exported row. A stale service-worker
# copy of this page is indistinguishable from the current one otherwise, and a field report against
# the wrong build costs more time than the bug does: three issues in one review had already been
# fixed, and the reporter had no way to know.
# BUILD comes from dictionary.BUILD so this form and the Kobo form stamp the SAME value. It was
# computed here until 2026-10-01, over this builder's own question list, which meant the two forms
# could disagree about the build id for one and the same question set -- and the id exists precisely
# so a field report can be matched to a build.
export_cols.append("form_build")

# ---- Google Sheets sink. Optional, and deliberately NOT in the repo.
# sync_config.json sits next to this file, is gitignored, and holds {"url": ..., "token": ...} for
# the Apps Script deployment. If it is absent the form still builds and still works -- it just
# starts with sync switched off, and an enumerator can paste the address into Sync settings on the
# tablet instead. Two routes because they fail differently: baking it in means a freshly wiped
# tablet is ready the moment it loads the page, while typing it per device keeps the address out of
# a build that is published on GitHub Pages.
_sync = {"url": "", "token": ""}
_scfg = os.path.join(HERE, "sync_config.json")
if os.path.isfile(_scfg):
    _sync.update(json.load(open(_scfg, encoding="utf-8")))
    print("sync_config.json found -- baking the sheet address into this build")

CFG = {"q": questions, "mods": modules, "cols": export_cols, "labs": LABS, "build": BUILD,
       "sync": _sync}

# The consent script now comes from dictionary.CONSENT_SCRIPT. This file used to hold its own shorter
# paraphrase, which is how two versions of an informed-consent statement came to exist in one repo.
CONSENT_EN, CONSENT_HI = CONSENT_SCRIPT, CONSENT_SCRIPT_HI

# ---- the page itself ---------------------------------------------------------------------------
# The markup, the stylesheet and the form's own JavaScript live in template.html / template.css
# beside this file rather than inside a Python string. They used to be one 700-line triple-quoted
# literal, which made every UI change a careful exercise in not breaking Python quoting, and made
# the diff of a hand-edit to the built page impossible to read back into the builder. The builder
# now fills exactly four holes in the template and otherwise copies it through untouched:
#
#   __CFG__       the question set, choices, labels and export columns, from dictionary.py
#   __CONS_HI__   the informed-consent script, Hindi    )  from dictionary.CONSENT_SCRIPT
#   __CONS_EN__   the informed-consent script, English  )  and translations_hi
#   __BRIEF_HI__  the plain-language study description, Hindi    )  from dictionary.STUDY_BRIEF
#   __BRIEF_EN__  the plain-language study description, English  )
#
# Everything a respondent or an enumerator reads therefore still comes from the dictionary, which
# is the whole point of having one: the page cannot say something the instrument does not.
HTML = io.open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
STYLE = io.open(os.path.join(HERE, "template.css"), encoding="utf-8").read()

html = (HTML.replace("__CFG__", json.dumps(CFG, ensure_ascii=False, separators=(",", ":")))
            .replace("__CONS_HI__", json.dumps(CONSENT_HI, ensure_ascii=False))
            .replace("__CONS_EN__", json.dumps(CONSENT_EN, ensure_ascii=False))
            .replace("__BRIEF_HI__", json.dumps(STUDY_BRIEF_HI, ensure_ascii=False))
            .replace("__BRIEF_EN__", json.dumps(STUDY_BRIEF, ensure_ascii=False)))
for _hole in ("__CFG__", "__CONS_HI__", "__CONS_EN__", "__BRIEF_HI__", "__BRIEF_EN__"):
    assert _hole not in html, "template hole never filled: " + _hole
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
_VER = hashlib.sha256((html + STYLE).encode("utf-8")).hexdigest()[:12]
SW = """const CACHE = "kedarnath-""" + _VER + """";
const ASSETS = ["./", "./index.html", "./style.css", "./manifest.json", "./icon-192.png", "./icon-512.png"];

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
    open(os.path.join(folder, "style.css"), "w", encoding="utf-8").write(STYLE)
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
