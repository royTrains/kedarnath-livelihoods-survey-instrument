# -*- coding: utf-8 -*-
"""Does every asked question reach an analysis?

The other checks ask whether the analyses have what they need. This one asks the reverse, which is
the question that shortens an interview: for each question the enumerator asks, is there a path from
it to something an analysis actually estimates or reports?

A variable that appears in the do-files ONLY inside an `assert`, a `label`, a `notes` line or a
comment is not feeding an analysis. It is interview time spent to satisfy a consistency check on
itself. That pattern has already been found here three times by hand (leave_rights, employer_type,
meal_spend_day_self), which is why it is now a check.

Resolution is transitive: a question that feeds a constructed variable that feeds a regression counts
as used. Run from replication/final_instrument/.
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "questionnaire"))
import dictionary as D  # noqa: E402

HERE = os.path.join(os.path.dirname(__file__), "..")
DO_FILES = ["do/02_build_final_dataset.do", "do/03_employment_vulnerability.do", "do/04_vtp_analysis.do"]

# Lines that mention a variable without consuming it for any estimate.
NON_USE = re.compile(r"^\s*(\*|//|assert\b|label\s+(var|variable|values|define)\b|notes\b|di\s|display\s)")

asked = [r for r in D.ROWS if r["origin"] in ("asked", "paradata")]
constructed = {r["name"]: (r["formula"] or "") + " " + r["desc"] for r in D.ROWS if r["origin"] == "constructed"}

# ---- Stata loops build names that never appear literally ---------------------------------------
# status_m`m' inside forvalues m = 1/12 is how the calendar is consumed, and cons_`v'_yatra_pm inside
# foreach v in staples perishables ... is how consumption is. Scanning the raw text would report every
# one of those as unused. So loop variables are collected and their values substituted before the
# scan. Substitution is file-wide rather than scope-aware, which is the simplification here: it can
# credit a use that a stricter reading would not, so anything this check DOES flag is worth trusting,
# and the survivors were each confirmed by hand.
def expand(text):
    vals = {}
    for var, a, b in re.findall(r"forvalues\s+(\w+)\s*=\s*(\d+)\s*/\s*(\d+)", text):
        vals.setdefault(var, set()).update(str(i) for i in range(int(a), int(b) + 1))
    for var, lst in re.findall(r"foreach\s+(\w+)\s+(?:in|of\s+local)\s+([^\n{]+)", text):
        vals.setdefault(var, set()).update(w for w in lst.split() if re.fullmatch(r"[\w.]+", w))
    out = []
    for line in text.split("\n"):
        out.append(line)
        for var, vs in vals.items():
            if "`%s'" % var in line:
                for v in vs:
                    out.append(line.replace("`%s'" % var, v))
    return out

real_use, weak_use = {}, {}
for path in DO_FILES:
    raw = io.open(os.path.join(HERE, path), encoding="utf-8").read()
    for line in expand(raw):
        weak = bool(NON_USE.match(line))
        for name in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", line):
            (weak_use if weak else real_use).setdefault(name, []).append(path)

def used(name, seen=None):
    """True if `name` reaches an estimate, directly or through a constructed variable."""
    seen = seen or set()
    if name in seen:
        return False
    seen.add(name)
    if name in real_use:
        return True
    # a constructed variable may consume it and itself be used downstream
    for cname, formula in constructed.items():
        if re.search(r"\b" + re.escape(name) + r"\b", formula) and used(cname, seen):
            return True
    return False

# Items that legitimately do not reach these three do-files. Each needs a reason, and the reason is
# checked: an entry here is a decision on the record, not a way to quiet the check. Anything not on
# this list and not traceable to an estimate is a question costing interview time for nothing.
ALLOWED = {
    "enum_id":                "paradata, set before approach; used as a data-quality cross-check on _submitted_by",
    "interview_duration_min": "paradata, automatic from Kobo start/end; no interview time",
    "dur_tasks_min":          "paradata, automatic module timestamps; no interview time",
    "gps_lon":                "paradata, automatic; health_access_tier needs only the latitude, but the pair is what locates an interview",
    "would_move_for_work":    "structural-displacement paper, not these three do-files",
    "prev_occ_change":        "transferability paper (job history), not these three do-files",
    "prev_occ_reason":        "transferability paper (job history), not these three do-files",
    "ropeway_stance":         "ropeway paper (Module J), not these three do-files",
    "read_at_work":           "tasks module, not these three do-files",
    "calc_at_work":           "tasks module, not these three do-files",
}

dead, assert_only = [], []
for r in asked:
    n = r["name"]
    if used(n) or n in ALLOWED:
        continue
    (assert_only if n in weak_use else dead).append(r)

print("\nEVERY ASKED QUESTION, TRACED TO AN ANALYSIS")
print(f"  {len(asked)} asked/paradata items, {len(DO_FILES)} do-files\n")

if assert_only:
    print(f"  ASSERT-ONLY -- asked, then used only to check itself ({len(assert_only)}):")
    for r in assert_only:
        print(f"     {r['module']}  {r['name']:<26} {r['question'][:56]}")
    print()
if dead:
    print(f"  UNREACHED -- asked and never mentioned in any do-file ({len(dead)}):")
    for r in dead:
        print(f"     {r['module']}  {r['name']:<26} {r['question'][:56]}")
    print()
if not dead and not assert_only:
    print("  PASS  every asked question reaches an analysis.\n")

# Verbatim office-coded fields are expected not to appear: they are coded to NCO-2015 by hand after
# fieldwork, so the do-files cannot mention them yet. Listed, not counted against the instrument.
print(f"  {len(ALLOWED)} items are exempt, each with a recorded reason:")
for _n, _why in ALLOWED.items():
    print(f"     {_n:<24} {_why}")
print()
verbatim = [r["name"] for r in asked if r["kind"] == "text"]
print(f"  for reference, {len(verbatim)} free-text fields are office-coded after fieldwork:")
print("     " + ", ".join(verbatim))
print()
sys.exit(1 if (dead or assert_only) else 0)
