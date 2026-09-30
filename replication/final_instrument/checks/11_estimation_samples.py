# -*- coding: utf-8 -*-
"""Did the regressions actually estimate on the sample, or on what survived listwise deletion?

This check exists because of a specific failure. Four skip-gated covariates were added to the FGLS
covariate set; each is missing wherever its gate excluded the respondent, the deletions intersect,
and the estimation sample fell from 104 observations to 4. Stata raised nothing. Every other check in
this folder passed: the build had no errors, every analysis had its inputs, the form logic was sound.
The number was printed in a "Number of obs" line nobody read.

So: read the lines. Any regression estimating on a small fraction of the built sample is a defect,
whatever else passed. Run after 04, from replication/final_instrument/.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

LOGS = [("do/04_vtp_analysis.log", "monetary and multidimensional VEP"),
        ("03_employment_vulnerability.log", "employment VEP")]

# A regression on fewer than this share of the built rows is treated as a collapse.
MIN_SHARE = 0.50

try:
    import pandas as pd
    built = len(pd.read_stata(os.path.join(ROOT, "data", "kedarnath_final_n200_fielded.dta")))
except Exception:
    built = None

print("\nESTIMATION SAMPLES")
fail = 0
for rel, label in LOGS:
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        print(f"  skip  {rel} not found -- run the do-file first")
        continue
    text = io.open(path, encoding="utf-8", errors="replace").read()
    ns = [int(m) for m in re.findall(r"Number of obs\s*=\s*([\d,]+)", text.replace(",", ""))]
    if not ns:
        print(f"  skip  {rel}: no estimation commands found")
        continue
    lo, hi = min(ns), max(ns)
    base = built or hi
    share = lo / base if base else 0
    status = "ok  " if share >= MIN_SHARE else "FAIL"
    if share < MIN_SHARE:
        fail += 1
    print(f"  {status}  {label}: {len(ns)} regressions, n from {lo} to {hi}"
          + (f" (built sample {base}, smallest keeps {share:.0%})" if base else ""))
    if share < MIN_SHARE:
        print(f"        a regression on {lo} of {base} rows is listwise deletion, not a sample.")
        print("        find the covariate that is missing where a skip rule excluded the respondent,")
        print("        and give it a form defined for every row -- see the regression-safe block in 02.")

print()
if fail:
    print(f"{fail} analysis file(s) estimating on a collapsed sample.")
    sys.exit(1)
print("PASS  every regression estimates on a usable share of the built sample.")
