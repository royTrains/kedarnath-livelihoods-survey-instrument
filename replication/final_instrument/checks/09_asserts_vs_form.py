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
chk("!missing(resp_returns_at_closure)", num("resp_returns_at_closure").notna())
chk("!missing(hh_at_home_place)", num("hh_at_home_place").notna())
chk("!missing(worked_away_in_closure)", num("worked_away_in_closure").notna())
chk("missing(n_here_season) == (hh_at_home_place!=1)",
    num("n_here_season").isna() == (num("hh_at_home_place") != 1))
chk("missing(years_coming_here) == (resp_returns_at_closure!=1)",
    num("years_coming_here").isna() == (num("resp_returns_at_closure") != 1))
chk("missing(left_here_month) == (resp_returns_at_closure!=1)",
    num("left_here_month").isna() == (num("resp_returns_at_closure") != 1))
chk("missing(returned_here_month) == (resp_returns_at_closure!=1)",
    num("returned_here_month").isna() == (num("resp_returns_at_closure") != 1))
chk("left_here_month in 1..12 when asked",
    num("left_here_month").between(1, 12) | num("left_here_month").isna())
chk("missing(came_here_reason) == (migrant!=1)", num("came_here_reason").isna() == (~migrant))
# One-directional, matching the build. These are optional verbatim fields: the gate being open does
# not oblige the enumerator to have typed anything, so only the reverse is enforceable.
chk("closure_work_detail blank when its gate is shut",
    (txt("closure_work_detail") == "") | (num("worked_away_in_closure") == 1))
chk("home_rural_urban in 1..2", num("home_rural_urban").between(1, 2))
chk("site in 1..2", num("site").between(1, 2))
chk("accom_type_here in 1..8", num("accom_type_here").between(1, 8))
chk("func_limitation in 1..4", num("func_limitation").between(1, 4))
# ration_portable_here is UNGATED as of 2026-10-01: "we have no ration card" is code 4 on the item
# itself rather than an absence, so every respondent answers it.
chk("ration_portable_here always answered", num("ration_portable_here").notna())
chk("ration_portable_here in 1..4 or 97",
    num("ration_portable_here").isin([1, 2, 3, 4, 97]))
# A real shock means the list is non-empty AND is not just code 9, the "nothing happened" escape
# that was added when this item turned out to be a required multi-select with no way to answer no.
_shk = (txt("distress_event_last365d") != "") & ~txt("distress_event_last365d").str.split().apply(
    lambda t: "9" in t)
for _v in ("shock_work_lost_weeks", "shock_money_spent", "shock_month"):
    chk(f"missing({_v}) == (no shock reported)", num(_v).isna() == ~_shk)
# the worst shock must be one the household actually reported
chk("code 9 is never ticked alongside a real shock",
    ~(txt("distress_event_last365d").str.split().apply(lambda t: "9" in t and len(t) > 1)))
# The scheme check-all became a yes/no plus a verbatim list on 2026-10-01. govt_schemes_detail is
# the one verbatim field that IS required when its gate is open -- it is now the only place a
# benefit's identity is recorded -- so unlike the others, BOTH directions are enforceable.
chk("govt_any_benefit never blank", num("govt_any_benefit").notna())
chk("govt_schemes_detail blank when no benefit was reported",
    (txt("govt_schemes_detail") == "") | (num("govt_any_benefit") == 1))
chk("govt_schemes_detail filled when a benefit WAS reported",
    (txt("govt_schemes_detail") != "") | (num("govt_any_benefit") != 1))
# The household 6-years indicator is skipped wherever the respondent's own schooling entails Yes.
_settled = ((num("knows_years_schooling") == 1) & (num("years_schooling") >= 6)) |            ((num("knows_years_schooling") == 0) & (num("education_level_cat") == 4))
chk("any_member_6yr_schooling asked exactly when the respondent's own answer does not settle it",
    num("any_member_6yr_schooling").isna() == _settled)
# Children are asked as two disjoint bands now; together they cannot exceed the household.
chk("children under 6 plus children 6-14 do not exceed household size minus the respondent",
    (num("n_children_u6") + num("n_children_6_14")) <= (num("hhsize") - 1))
chk("skilled_birth_attendant in 1..5 when asked",
    num("skilled_birth_attendant").isin([1, 2, 3, 4, 5]) | num("skilled_birth_attendant").isna())
chk("anc_4_visits never 'don't know' (97 was removed)",
    ~num("anc_4_visits").eq(97))
chk("coping code 6 is never ticked alongside another answer",
    ~txt("shock_coping").str.split().apply(lambda t: "6" in t and len(t) > 1))
chk("other_activity_types never repeats the main occupation",
    ~pd.Series([str(o) in str(a).split() for o, a in zip(d["occupation"], txt("other_activity_types"))]))

# Printed so the count stays visible rather than asserted. The pair that lived here concerned the
# loc_m1..12 location row and then months_away_for_work, and both are gone. What is worth watching
# now is the earnings-refusal rate: the only blank on this form that is a legitimate ANSWER rather
# than a defect, and the one whose size decides how much the income covariates are worth.
_declined = num("knows_monthly_income").isna()
print(f"\n  not a failure -- declined the earnings calendar entirely: "
      f"{int(_declined.sum())} of {len(d)} rows "
      f"(their income covariates come through MISSING, never zero)")

print()
if fails:
    print(f"{len(fails)} ASSERT(S) THE FORM CAN VIOLATE -- the Stata build would halt on this export:")
    for n, b in fails:
        print(f"   {n}   ({b} rows)")
    sys.exit(1)
print("PASS  every skip-logic assert holds on data the form actually produced.")
