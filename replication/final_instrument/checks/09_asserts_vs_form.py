# -*- coding: utf-8 -*-
"""Run the Stata build's skip-logic asserts against the form's OWN export.

Why this exists as a separate check. `01_generate_raw.py` builds internally consistent records, so it
can never produce the combinations the form actually emits -- which is exactly why an assert that the
form does not enforce sails through every other check in this folder and then halts the build the
first time a real Kobo export arrives. This file has already happened once in this project (the
cross-variable asserts removed from `02_build_final_dataset.do`), and it happened again on
2026-09-28: an assert that a Yatra-work month must be coded "here on the Yatra route" was violated in
54 respondent-months out of 50 forms, and was also substantively wrong -- a Guptkashi or Sonprayag
worker commuting up the route daily does Yatra work while living at the home place.

Scope: the mobility and closure-regime block (Module D plus the Module C location row). It is not a
complete transcription of every assert in the build. Extend it when you add a cross-variable assert.

Usage, from replication/final_instrument/:
    node checks/08_fill_and_export_test.js questionnaire/index.html <tmp>/form_export.csv
    python checks/09_asserts_vs_form.py <tmp>/form_export.csv
"""
import sys

import numpy as np
import pandas as pd

if len(sys.argv) < 2:
    sys.exit("usage: python checks/09_asserts_vs_form.py <form_export.csv>\n"
             "       produce the CSV with checks/08_fill_and_export_test.js first")

d = pd.read_csv(sys.argv[1], dtype=str).replace("", np.nan)

def num(c):
    return pd.to_numeric(d[c], errors="coerce")

def txt(c):
    return d[c].fillna("").astype(str)

fails = []

def chk(name, ok):
    """ok is a boolean Series that must be True on every row, as the Stata assert requires."""
    bad = int((~ok).sum())
    if bad:
        fails.append((name, bad))
    print(("  FAIL  " if bad else "  ok    ") + name + (f"   [{bad}/{len(d)} rows violate]" if bad else ""))

print(f"\nStata skip-logic asserts vs {len(d)} form-produced submissions\n")

migrant = num("origin") > 1
chk("!missing(migration_referral)", num("migration_referral").notna())
chk("!missing(worked_other_places)", num("worked_other_places").notna())
chk("closure_base in 1..4", num("closure_base").between(1, 4))
chk("!missing(worked_away_in_closure)", num("worked_away_in_closure").notna())
chk("missing(years_coming_here) == (closure_base==1)",
    num("years_coming_here").isna() == (num("closure_base") == 1))
chk("missing(came_here_reason) == (migrant!=1)", num("came_here_reason").isna() == (~migrant))
chk("(closure_work_detail=='') == !(worked_away_in_closure==1)",
    (txt("closure_work_detail") == "") == ~(num("worked_away_in_closure") == 1))
chk("(other_places_detail=='') == !(worked_other_places==1)",
    (txt("other_places_detail") == "") == ~(num("worked_other_places") == 1))
chk("loc_m1..12 all in 1..4",
    pd.concat([num(f"loc_m{m}").between(1, 4) for m in range(1, 13)], axis=1).all(1))
chk("home_rural_urban in 1..2", num("home_rural_urban").between(1, 2))

# Combinations the build deliberately does NOT assert. Printed so the counts stay visible: if either
# ever reads 0 across a few hundred forms, the form has gained a constraint somewhere and the
# corresponding data-quality check in 02_build_final_dataset.do has become dead code.
S = np.column_stack([num(f"status_m{m}") for m in range(1, 13)])
L = np.column_stack([num(f"loc_m{m}") for m in range(1, 13)])
print(f"\n  not asserted, by design -- Yatra-work month not coded on the route: "
      f"{int(((S == 1) & (L != 1)).sum())} respondent-months (local commuters; a true answer)")
print(f"  not asserted, counted as dq_act_loc_conflict -- activity 5 at a base: "
      f"{int(((S == 5) & ((L == 1) | (L == 2))).sum())} respondent-months")

print()
if fails:
    print(f"{len(fails)} ASSERT(S) THE FORM CAN VIOLATE -- the Stata build would halt on this export:")
    for n, b in fails:
        print(f"   {n}   ({b} rows)")
    sys.exit(1)
print("PASS  every skip-logic assert holds on data the form actually produced.")
