# Running checklist

Updated as work happens. **Committed locally; never pushed unless explicitly asked.**

| | |
|---|---|
| Local HEAD | survey revisions done and **pushed** (asked for, 2026-10-01) |
| Remote `main` | up to date; `0c534fd` superseded, no revert needed |
| Questions asked | 211 |

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

---

## Second field review (14 personas) — closed 2026-10-01

**Three of the five reported issues were already fixed** in `2fbf158`, after the build that was
tested: home_state for local respondents, pension/insurance/leave for own-account workers, and the
"hardest shock" question, which is in neither the pushed build nor local HEAD. That last one means a
**stale service-worker copy** was being tested, which is now addressed directly.

- [x] Ropeway module read to Hemkund respondents — gated to `site = 1`. Module J names the
      Gaurikund-Kedarnath proposal specifically; `trek_dependent` reworded to be route-neutral.
      If Hemkund needs its own ropeway question it needs its own wording and gate, not this one widened.
- [x] "not exported" badge disagreed with the completion page — the completion count was written into
      the HTML once and never refreshed, so exporting from that screen dropped the header to 0 while
      the paragraph still claimed 2. Now the same live element.
- [x] **Build stamp added.** Header shows it, and `form_build` is written into every exported row.
      A stale cached page was indistinguishable from the current one, which cost this review three
      already-fixed issues.
- [x] Negative monthly income, negative land, negative loan amounts — non-negative constraints
- [x] 30 years of schooling at age 20 — `years_schooling <= age - 4`
- [x] 40 Yatra seasons at age 30 — `years_in_yatra_work <= age - 10`
- [x] Extra hours wanted beyond a day — `more_hours_day + hours_day_yatra <= 18`
- [x] "Local" home with the state set to Assam — closed by the home_state gate in `2fbf158`
- [x] `GETTING_THE_DATASET.md` — how to get from collected interviews to the analysis file

Still untested by the reviewer and now constrained anyway: pony-owner against owning no ponies
(a cross-check flag, not a block), and negative loan amounts.

Verified: 0 Stata errors across all three do-files · 05 06 09 10 11 clean · 07 17/17 · 08 50/50 ·
**12 13/13 in a live Edge instance** · pyxform validates. 213 asked.

---

## Survey revisions from the review pass — 2026-10-01 (pushed, `066ee9d` + follow-up)

Sixteen question-level notes, worked through in order. Three were questions rather than
instructions and are answered in chat, not in the instrument.

### Changed
- [x] q7 · enumerator hint converting a LEVEL to a year count. A level is not a "don't know":
      class 1-12 = that number, ITI/diploma after 10th = 12, BA 15 or 16 (ask the course length),
      MA 17 or 18. EN and HI.
- [x] q11 · skipped where the respondent's own schooling entails Yes. He is himself a member aged
      10+, so six years of his own settles the household indicator. Stata fills those rows and
      asserts none is left missing. The bracket route can only settle it at "secondary or higher" —
      "primary but not secondary" spans 5 to 9 years and straddles the threshold.
- [x] q15/q16 · two DISJOINT bands, under-6 and 6-to-14, replacing under-15 and a 6-to-14 subset of
      it. `n_children_u15` is now constructed as their sum. Under-6 is also NITI's nutrition range.
- [x] q44-58 · the earnings calendar is no longer required, gate included. A blank gate = declined.
- [x] q74 · reworded to "away from your home place". KEPT: the calendar records the activity in each
      month, not the place, and the spell says he went to the home place, not past it.
- [x] q78 · `months_away_for_work` cut. Nothing regressed on it; `closure_labour_migrant` comes off
      the yes/no. The proposed replacement was not added — origin, resp_returns_at_closure and
      hh_at_home_place already answer it.
- [x] q79/q80 · `worked_other_places` and its verbatim cut; removed from X_extra.
- [x] q152 · the ten schemes become the PROBE LIST in the hint; a yes/no plus verbatim names,
      office-coded. `ration_portable_here` ungated, "we have no ration card" is now code 4.
- [x] q159 · coping code 6 split: "paid it out of normal earnings" (not stressed) from "something
      else" (stressed, unlisted). Code 6 exclusive on the check-all.
- [x] q166 · "Don't know" removed from both maternal limbs, with a probe hint.
- [x] q167 · asks the CADRE now. An ASHA is its own code and does NOT count as skilled under
      NFHS/NITI — the old wording would have had an accompanying ASHA read as a yes.
- [x] q169 · split into weeks of work lost and money spent; the weeks are valued at his OWN measured
      wage in Stata rather than at his estimate of it.
- [x] MPI · all 12 audited. Eleven collected; nutrition needs anthropometry. `mpi_score` stays
      strict and reweighted, `mpi_score_lyons` substitutes the Lyons food-coping indicator into the
      1/6 slot. The index was labelled "ten of twelve" everywhere and summed eleven.

### Answered, not changed
- home_state vs native_language — different variables, so no move. See chat.
- q72 `years_coming_here` — in the VEP covariate list; kept. See chat.
- q171-179 — kept, and the nutrition substitution makes the rCSI block MORE load-bearing.

### Bugs found while making the changes
- `form_build` reached the Kobo form as a REQUIRED TEXT QUESTION labelled "Recorded
  automatically." — an unanswerable required field, the same failure the last review hit. Now a
  hidden calculate, and BUILD moved into dictionary.py so both forms stamp one value.
- The optional-question test read `"may be left blank" in skip` case-SENSITIVELY, so a rule opening
  "May be left blank" left the question required with nothing saying so. That is how the optional
  earnings gate was still compulsory in the first build. Match is case-insensitive now.
- `home_outside_state` was missing for 178 of 200 rows and sat in a covariate list — the
  n=104-to-4 failure mode, still live from when home_state was gated. Filled from origin instead.
- `egen rowtotal` read an unmeasured employment domain as a NON-deprivation. Alkire-Foster drops
  the observation; the count is now reported.
- `income_declined` was defined after the block that reads it. The build caught it.

Verified: 0 Stata errors across all three do-files · 05 06 09 10 11 clean · 07 17/17 · 08 50/50 ·
**12 13/13 in a live Edge instance** · pyxform validates · Hindi complete for every question and
every choice. **211 asked.**
