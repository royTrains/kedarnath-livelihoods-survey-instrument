# -*- coding: utf-8 -*-
"""Reconcile a live export's header against dictionary.py, so no collected record is stranded.

The instrument changes between builds. The Google Sheet accretes columns -- apps_script's ensure_()
appends any name it has not seen and never removes one -- so after a few builds the header is the
union of every instrument that has ever submitted. That is the right behaviour: deleting a column
would destroy the rows that hold it. What it needs is a reconciliation, which is this.

Three questions, in order of how much they matter:

  1. Is any column in the sheet a name the dictionary no longer knows AND does not record as
     retired?  That is an undocumented variable holding real answers -- the years_in_yatra_work
     case, which was asked in two builds on 2026-10-05, holds the values 8, 22 and 15, and was
     never in dictionary.py at all.
  2. Is any name reused for a different quantity?  RETIRED lists what each retired variable held
     and what replaced it; a replacement must NOT carry the old name. This is the rule that keeps
     the already-collected rows readable: n_children_out_school counted children NOT in school and
     n_children_in_school counts those who are, so reusing the name would have inverted 7 records.
  3. Which dictionary variables have no column yet?  Expected for anything added since the last
     submission -- they appear when the next interview arrives. Reported, never an error.

Usage:  python checks/14_sheet_vs_dictionary.py <export.csv|export.tsv>
        python checks/14_sheet_vs_dictionary.py            (header-only self-check)
"""
import csv, io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "questionnaire"))
from dictionary import ROWS, RETIRED, CODE_ADDITIONS   # noqa: E402

KNOWN = {r["name"] for r in ROWS}
ASKED = {r["name"] for r in ROWS if r["origin"] in ("asked", "paradata")}
# Columns the sink adds, not the instrument. Anything starting "__" is tablet metadata.
SINK = {"_received_at", "_sync_count", "_form_build", "resp_id"}

fails, warns, notes = [], [], []

# ---- 2. the name-reuse rule, checked against the dictionary alone ------------------------------
for name, (build, held, replaced) in sorted(RETIRED.items()):
    if name in ASKED:
        fails.append("RETIRED but still asked: %s -- it held %r. Either un-retire it or rename "
                     "the new question." % (name, held))
for name in sorted(CODE_ADDITIONS):
    if name not in KNOWN:
        warns.append("CODE_ADDITIONS names %s, which is not in the dictionary" % name)

path = sys.argv[1] if len(sys.argv) > 1 else None
if path:
    with io.open(path, encoding="utf-8-sig", newline="") as fh:
        sample = fh.read(8192); fh.seek(0)
        delim = "\t" if sample.count("\t") > sample.count(",") else ","
        header = next(csv.reader(fh, delimiter=delim))
    cols = [c.strip() for c in header if c.strip()]

    # ---- 1. undocumented columns holding real answers -----------------------------------------
    for c in cols:
        if c in SINK or c.startswith("__") or c in KNOWN:
            continue
        if c in RETIRED:
            notes.append("retired, documented: %-28s was %s" % (c, RETIRED[c][1][:58]))
        else:
            fails.append("UNDOCUMENTED column in the sheet: %s -- it may hold answers and nothing "
                         "says what they mean. Add it to RETIRED in dictionary.py." % c)

    # ---- 3. dictionary variables with no column yet -------------------------------------------
    missing = [n for n in sorted(ASKED) if n not in cols]
    if missing:
        notes.append("%d asked variable(s) have no column yet; they appear on the next submission: %s"
                     % (len(missing), ", ".join(missing[:12]) + (" ..." if len(missing) > 12 else "")))
    print("export: %s  (%d columns)" % (os.path.basename(path), len(cols)))
else:
    print("no export given -- dictionary self-check only")

print("dictionary: %d known, %d asked/paradata, %d retired, %d code additions"
      % (len(KNOWN), len(ASKED), len(RETIRED), len(CODE_ADDITIONS)))
for n in notes: print("  note  " + n)
for w in warns: print("  WARN  " + w)
for f in fails: print("  FAIL  " + f)
print(("  %d failure(s)" % len(fails)) if fails else "  OK -- no record is stranded and no name is reused")
sys.exit(1 if fails else 0)
