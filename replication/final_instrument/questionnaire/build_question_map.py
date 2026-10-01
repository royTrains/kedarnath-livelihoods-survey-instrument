# -*- coding: utf-8 -*-
"""Render the instrument as an ASCII flow map: every question, every gate, every branch.

Built from the same two sources the form itself is: dictionary.py for the question order and types,
and build_xlsform.RELEVANT for the gates -- the hand-built dict that IS the skip logic, rather than
the prose `skip` field, which is documentation. So this map cannot drift from the form.

Output: QUESTION_MAP.txt
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from dictionary import ROWS, LSETS, MODULES, INTROS   # noqa: E402
import build_xlsform as X                              # noqa: E402

OUT = os.path.join(HERE, "QUESTION_MAP.txt")
MODNAME = dict(MODULES)

asked = [r for r in ROWS if r["origin"] == "asked"]
num = {r["name"]: i for i, r in enumerate(asked, 1)}
byname = {r["name"]: r for r in asked}

# ---- who gates whom -------------------------------------------------------------------------
# A rule names one or more source variables. The first is the one the question hangs off; any others
# are recorded so a compound condition is visible rather than hidden.
gates = {}          # question -> (primary source, full condition text)
children = {}       # source -> [questions it gates]
for q, rule in X.RELEVANT.items():
    if q not in byname:
        continue
    srcs = re.findall(r"\$\{(\w+)\}", rule)
    if not srcs:
        continue
    gates[q] = (srcs[0], rule)
    children.setdefault(srcs[0], []).append(q)

# A choice filter is a second kind of control: it changes a question's OPTIONS rather than whether
# the question appears at all. Q18 -> Q22 is the case that matters, and it is invisible in RELEVANT.
cfilter = {}
for q, rule in getattr(X, "CHOICE_FILTER", {}).items():
    srcs = re.findall(r"\$\{(\w+)\}", rule)
    if q in byname and srcs:
        cfilter[q] = srcs[0]
cfilter_children = {}
for q, src in cfilter.items():
    cfilter_children.setdefault(src, []).append(q)


def cond(rule):
    """The rule as a reader needs it: variable references replaced by their question numbers."""
    def sub(m):
        v = m.group(1)
        return f"Q{num[v]}" if v in num else v
    s = re.sub(r"\$\{(\w+)\}", sub, rule)
    s = s.replace("count-selected(", "count(").replace(" and ", " AND ").replace(" or ", " OR ")
    return s.strip()

def kind_of(r):
    if r["kind"] == "multi":
        return f"CHECK ALL ({len(LSETS[r['lset']])} options)"
    if r["lset"]:
        return f"CHOOSE 1 ({len(LSETS[r['lset']])} options)"
    return {"count": "number", "num": "number", "money": "amount in Rs",
            "text": "free text", "date": "date", "id": "id"}.get(r["kind"], r["kind"]).upper()


def wrap(text, indent, width=None):
    """The question as the enumerator reads it, wrapped. A map that names only the variable sends the
    reader back to the dictionary, which defeats the point of having a map."""
    width = width or (W - 4)
    out, line, first = [], indent + '"', True
    for word in text.split():
        if len(line) + len(word) + 1 > width and not first:
            out.append(line)
            line = indent + " "          # continuation lines align under the opening quote
            first = True
        line += ("" if first else " ") + word
        first = False
    if line.strip():
        out.append(line + '"')
    return out


def options(r, indent):
    """Every option, in full, wrapped to the page. The whole point of the map is that nothing has to
    be looked up somewhere else, so no list is abbreviated however long it runs."""
    if not r["lset"]:
        return []
    out, line = [], indent
    for k, v in LSETS[r["lset"]].items():
        bit = f"{k}={v}"
        if len(line) + len(bit) + 3 > W - 2 and line.strip() != indent.strip():
            out.append(line.rstrip(" |"))
            line = indent
        line += bit + "  |  "
    if line.strip():
        out.append(line.rstrip(" |"))
    return out

W = 92
lines = []
A = lines.append

A("=" * W)
A("KEDARNATH SURVEY — QUESTION MAP".center(W))
A("every question, every gate, in the order the form asks them".center(W))
A("=" * W)
A("")
A("  LEGEND")
A("    123  question number, as the enumerator meets it")
A("    |->  this question only appears when the condition holds")
A("    ..   optional; may be left blank")
A("    **   this answer opens or closes other questions")
A("")
A(f"  {len(asked)} questions asked · {len(gates)} of them gated · {len(children)} questions act as gates")
A("")

for code, title in MODULES:
    mod = [r for r in asked if r["module"] == code]
    if not mod:
        continue
    A("")
    A("+" + "-" * (W - 2) + "+")
    A("| " + f"MODULE {code} — {title}".ljust(W - 4) + " |")
    A("| " + f"{len(mod)} questions".ljust(W - 4) + " |")
    A("+" + "-" * (W - 2) + "+")
    if code in INTROS:
        intro = INTROS[code]
        A("")
        A("   [read aloud] " + intro[:74] + ("..." if len(intro) > 74 else ""))
    A("")

    for r in mod:
        n, name = num[r["name"]], r["name"]
        opt = ".." if "may be left blank" in r["skip"] else "  "
        opens = "**" if (name in children or name in cfilter_children) else "  "
        gated = name in gates
        qt = r["question"]

        if gated:
            src, rule = gates[name]
            # a gate inside this module is drawn as a branch; one from an earlier module is labelled
            same = src in byname and byname[src]["module"] == code
            lead = "   |-> " if same else "   :-> "
            A(f"{lead}if {cond(rule)}")
            A(f"   |    {n:>3} {opens}{name:<26} {kind_of(r)}{opt}")
            for ln in wrap(qt, "   |         ", W - 8):
                A(ln)
            for ln in options(r, "   |         "):
                A(ln)
        else:
            A(f"       {n:>3} {opens}{name:<26} {kind_of(r)}{opt}")
            for ln in wrap(qt, "             ", W - 8):
                A(ln)
            for ln in options(r, "             "):
                A(ln)

        if name in children:
            kids = ", ".join(f"Q{num[c]}" for c in children[name] if c in num)
            A(f"           \\__ opens/closes: {kids}")
        if name in cfilter_children:
            k2 = ", ".join(f"Q{num[c]}" for c in cfilter_children[name] if c in num)
            A(f"           \\__ this answer is removed from the options of: {k2}")
        if name in cfilter:
            A(f"           \\__ options exclude whatever was answered at Q{num[cfilter[name]]}")

A("")
A("=" * W)
A("CROSS-MODULE GATES".center(W))
A("a question whose gate was answered in an earlier module".center(W))
A("=" * W)
A("")
cross = [(q, s) for q, (s, _) in sorted(gates.items(), key=lambda kv: num[kv[0]])
         if s in byname and byname[s]["module"] != byname[q]["module"]]
if not cross:
    A("   none — every gate is answered in the same module as the question it controls.")
for q, s in cross:
    A(f"   Q{num[q]:<4}{q:<28} <- Q{num[s]} {s} (module {byname[s]['module']})")

A("")
A("=" * W)
A("THE BRANCH POINTS THAT MATTER MOST".center(W))
A("=" * W)
A("")
for src, kids in sorted(children.items(), key=lambda kv: -len(kv[1])):
    if len(kids) < 2 or src not in num:
        continue
    A(f"   Q{num[src]} {src} ({kind_of(byname[src])})")
    A(f"      controls {len(kids)} questions: " + ", ".join(f"Q{num[c]}" for c in sorted(kids, key=lambda c: num[c])))
    A("")

A("=" * W)
A("Generated by build_question_map.py from dictionary.py and build_xlsform.RELEVANT,")
A("which is the same pair the form itself is built from, so this map cannot drift from it.")
A("=" * W)

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print(OUT)
print(f"{len(lines)} lines · {len(asked)} questions · {len(gates)} gated · {len(children)} gate sources")
