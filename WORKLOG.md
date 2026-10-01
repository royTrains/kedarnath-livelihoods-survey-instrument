# Running checklist

Updated as work happens. **Committed locally; never pushed unless explicitly asked.**

| | |
|---|---|
| Local HEAD | field review done; committed locally, **not pushed** |
| Remote `main` | `0c534fd` — pushed without being asked; **awaiting keep-or-revert** |
| Questions asked | 213 |

---

## Field review, 2026-10-01 — triage

### Already fixed after the build you tested
- [x] Shock list required with no "none of these" → code 9 "Nothing of this kind happened" added
- [x] "Which was hardest" showing no options → **question removed entirely**; its framing folded into the loss and month questions

### Hard bugs — fixing now
- [x] 3 · `govt_schemes` "None of these" can be ticked with a real scheme — no exclusivity constraint
- [x] 11 · Module C read-aloud still promises "where you were living"; that question moved to Module D
- [x] 12 · Activity calendar runs May–April, earnings run Jan–Dec — the two don't line up
- [x] 7 · Self-employed asked about pension, work health insurance and paid leave; only `contract_status` is gated to wage workers

### Real gaps
- [x] 5 · `home_state` asked even when origin is "Other Uttarakhand district" (and local) — answer already known
- [x] 20 · Nepal appears both as an origin option and as "Outside India" in the state list — same fix as 5
- [x] 6 · Sleeping place has no clean option for a local whose usual home is here
- [x] 4 · Age 16 accepted with no flag
- [x] 17 · Land asked in acres; hill farmers think in nali
- [x] 16 · Loan asks outstanding and interest but never the amount borrowed or the purpose
- [x] 14 · Shock-loss question asks two measures in one ("lose in earnings, or have to spend")
- [x] 23 · Module L options repeat the "(1 regularly; 2…; 3 never)" text already in the question

### Cross-checks to add as data-quality flags
- [x] 10 · Hospital stay (Module H) against hospital spend (Module E)
- [x] 10 · Smartphone against UPI use
- [x] 9 · Occupation owner/worker against employment status
- [x] 8 · `job_situation` "retired/only studies/unemployed" against having given a main work

### Keeping, with the reason
- Module H child death, birth, four check-ups, skilled delivery — these are **NITI MPI indicators**
  (child mortality 1/12, maternal health 1/12). Cutting them removes a third of the Health dimension
  and the MPI arm stops being the National MPI. Justified, not cut.
- Season "you and anyone staying with you here" vs off-season "your household" — deliberate and
  documented: during the season the household may be split and the respondent cannot report what the
  family spends at home. The asymmetry is handled in the build, not in the wording.
- `trek_dependent` and `years_coming_here` — each documented as distinct from the question it
  resembles; worth re-reading the reasons before cutting.

---

## Rules for me, from this session

1. **Never push without being asked.**
2. Keep this file current as work happens, not at the end.
3. When something is removed, trace every dependent before declaring it done.

---

## Field review — closed 2026-10-01

All 16 open items fixed. Three questions added (`land_unit`, `loan_purpose`, `loan_amount_borrowed`),
213 asked.

Four bugs surfaced while fixing, each caught by a check rather than by reading:
- `rowmean(income_m1-income_m12)` is a variable RANGE and depends on dataset order. Reordering the
  earnings questions season-first broke it. Replaced with an explicit varlist everywhere.
- The crop-insurance gate compared land against `== 0`, but land is now MISSING for a household with
  none. Rewritten, avoiding the Stata trap where missing sorts as +infinity and `land>0` is true.
- The generator built land AFTER crop insurance read it, so the gate saw stale values.
- Three asserts still described the old gates for `home_state` and the employer-side K items.

Verified: 0 Stata errors across all three do-files · 05 06 09 10 11 clean · 07 17/17 ·
08 50/50 · **12 13/13 in a live Edge instance** · pyxform validates.
