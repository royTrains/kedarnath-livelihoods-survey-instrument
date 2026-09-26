# Instrument vs. research goal — gap analysis

Companion to `FUJII_2016_GAPS.md` (which checks the *analysis* against the vulnerability
literature). This file checks the *questionnaire* against what the project actually set out
to answer. Sources: `HANDOFF.md`, the project memory's design commitments, `dictionary.py`
(159 asked items, 46.4 min), and the real 46-respondent pilot `livelihood_clean.dta`
(102 variables).

## The goal, as stated

1. **Vulnerability to poverty** among Kedarnath Yatra-route workers — VEP applied to monetary
   consumption, an AF/MPI deprivation score, and an Apablaza employment-deprivation score.
2. **The ropeway**: "estimate how many workers are likely displaced if they cannot take up
   ropeway-created jobs." This is why the study exists.
3. **Occupational task transferability** — explicitly a *second* paper; its questions must be short.

## Where the 46.4 minutes actually go

| Mod | items | min | % | title |
|-----|------:|----:|--:|-------|
| P | 0 | 1.5 | 3.2% | Cover, consent, paradata |
| A | 16 | 4.2 | 9.1% | Respondent and household |
| B | 12 | 3.3 | 7.1% | Work and work history |
| C | 28 | 4.5 | 9.7% | Monthly calendar; remittances |
| D | 3 | 1.4 | 3.0% | Migration |
| E | 22 | 8.0 | 17.2% | Consumption |
| F | 20 | 4.6 | 9.9% | Housing, amenities, assets |
| G | 7 | 2.7 | 5.8% | Finance, insurance, schemes |
| H | 6 | 2.6 | 5.6% | Health |
| I | 12 | 4.0 | 8.6% | Food security, shocks, coping |
| **J** | **2** | **1.0** | **2.2%** | **Ropeway** |
| K | 14 | 4.6 | 9.9% | Job quality (Apablaza) |
| L | 17 | 4.0 | 8.6% | Tasks and skills |

Goal 2 — the reason the study exists — gets **2 questions and 2.2% of the interview**.
Goal 3 — explicitly the *second* paper, explicitly "must be short" — gets **4× that**.

---

## G1. The ropeway module cannot answer the ropeway question

- [ ] **G1a. No counterfactual/expectation item at all.** Module J is `ropeway_stance`
      (favour/neutral/against) and `trek_dependent` (binary). Of those, only `trek_dependent`
      does analytical work; `ropeway_stance` is an attitude with no role in a VEP framework and
      is the single lowest-yield item in the instrument. Nothing asks what the respondent
      expects to happen to their own income, work or location. The displacement estimate
      therefore has to be built **entirely from the analyst's assumptions**, with no respondent-
      side quantity to discipline or validate it.

- [ ] **G1b. The destination side of the displacement question is missing.** Module L asks
      which of 12 tasks a worker does — that gives *task distance* to ropeway-adjacent
      occupations, and nothing more. It cannot say whether a worker would take such a job, could
      reach one, or has any intention of trying. **The pilot asked exactly this and it was
      dropped**: `opp_ropeway`, `opp_hospitality`, `opp_transport`, `opp_stationshop`,
      `opp_guiding`, `opp_other`, `opp_none` (+ constructed `n_opportunities`), plus
      `willing_to_learn_skills`. Without them, Module L is a half-built bridge: the supply side
      of skills with no demand or intention side. Reinstating a compressed version is the
      single highest-value change available to this instrument.

- [ ] **G1c. `dist_to_ropeway_station` should be constructed, not asked.** The pilot asked it
      directly and **20 of 46 (43%) answered "Don't know"** — workers do not know where the
      station will be. But `gps_lat`/`gps_lon` are already captured silently at every interview
      (Module P, `background-geopoint` in the Kobo form), and the Gaurikund–Kedarnath alignment
      is public. Distance-to-alignment and distance-to-planned-terminal are therefore **free
      constructed variables costing zero interview seconds**, and they are better data than the
      pilot's question produced. This is the cheapest spatial-exposure measure in the project
      and it is currently unused.

- [ ] **G1d. No anticipation/adjustment channel.** A shock that is announced but not yet
      delivered changes behaviour *now* — deferred pony purchases, deferred shop investment,
      children not brought to the site. Nothing in the instrument would detect this, and it is
      the one ropeway effect that is actually observable in a single pre-construction round.
      The pilot's `expected_income_effect` / `expected_income_reduction` /
      `expected_modal_shift` / `expect_more_yatris` covered the belief side of it.

## G2. No financial buffer — the largest hole in "adaptive capacity"

The analysis claims an Azeem et al. (2016) adaptive-capacity / sensitivity / exposure structure.
Adaptive capacity is currently `education_years`, `has_bank_account`, `credit_inst`,
`training_received`, `smartphone_owned` — **four binaries and a year count, with no stock
measure of any kind.**

- [ ] **G2a. No savings.** Whether the household has savings, and how long they would last, is
      the first self-insurance channel Fujii §4 names and the most direct measure of ability to
      absorb a shock without becoming poor. The pilot had `has_savings` and
      `savings_survival_duration`. (Caveat: the pilot's duration variable came back degenerate —
      25 blank, 21 ">6 months" — so re-word it rather than copy it; a "could you cover a month
      of expenses without borrowing?" form is more answerable than a duration bracket.)

- [ ] **G2b. No debt stock.** `credit_source` records *who lent*, last 12 months. It does not
      record whether debt is outstanding, how much, or the repayment burden. For VEP this is
      backwards: a household with a large outstanding loan is more vulnerable regardless of who
      the lender was. The pilot had `has_debt`, `debt_total_outstanding`,
      `debt_monthly_repayment`, `debt_repay_difficulty` and — best of the set —
      `debt_repay_risk_if_income_falls`, which is an *ex ante* vulnerability question asked
      directly. `debt_ratio` was constructed from them. Islam & Chowdhury (2025), "From struggle
      to strain: effects of financial distress on household vulnerability to poverty," is
      already in `vulnerability-to-poverty/`.

- [ ] **G2c. No asset value.** Module F replaced asset counts with six ownership binaries, for
      the stated reason that "a count would treat a goat and a buffalo as equally valuable."
      Correct — but the fix chosen was to drop value entirely, and the pilot shows the harder
      question was askable in this population: `asset_resale_value` and
      `asset_replacement_cost`. A pony is the archetypal lumpy productive asset (Dercon's cattle
      case); whether a household can sell one to smooth consumption depends on what it is worth.
      Blocks `FUJII_2016_GAPS.md` A10 (Chiwaula structural vs. stochastic decomposition), which
      needs an asset *base*, not an asset *list*.

## G3. Shocks are recorded without magnitude or incidence

- [ ] **G3a. No shock magnitude.** `distress_event_last365d` records *which* shock (one, "the
      most serious"); nothing records what it cost. The pilot had `income_affected_by_shock`
      **and `shock_income_loss`**. Without magnitude, the shock variable can only ever enter the
      model as the binary `distress_any` it is currently collapsed to — which is what
      `kedarnath_vtp_analysis.do` does.

- [ ] **G3b. No covariate shock, and no shock history — this blocks the ropeway scenario.**
      Covered as B1 in `FUJII_2016_GAPS.md` on Fujii/Günther–Harttgen grounds, but the
      goal-side consequence is sharper: the ropeway is a **covariate** shock that will hit every
      trek-dependent worker at once. The instrument has no way to observe how this workforce
      responded to the covariate shocks it has already survived — the 2013 floods, the COVID
      yatra closures. That history is the only empirical basis available in a single
      cross-section for calibrating a ropeway scenario. Without it, any displacement or
      poverty-impact simulation is assumption all the way down. A short retrospective block
      ("in the closure years, did you work here / what did you do instead / did you sell
      anything") would change the ropeway analysis from stipulated to estimated.

- [ ] **G3c. No household-level exposure concentration.** `n_earners` counts earners;
      nothing asks how many of them work in the Yatra economy. A household with three earners
      all on the trek has no diversification and is fully exposed to a single covariate shock;
      one with three earners in three sectors is not. `yatra_income_share` is a *respondent*
      income share, not a household one, so it cannot distinguish these. The pilot had
      `hh_members_in_yatra_work`. One question, and it is the household-level analogue of the
      exposure the whole study is about.

## G4. Smaller goal-fit gaps

- [ ] **G4a. Government schemes: a single binary.** `govt_scheme_beneficiary` (yes/no, "for
      example ration, pension, cash transfer") cannot identify which scheme, and cannot identify
      public works at all — see `FUJII_2016_GAPS.md` B2. The pilot separately measured
      `income_govt_scheme` in rupees and `bpl_card` (targeting status). For a paper whose policy
      section will be about what protects these workers, one binary is thin.
- [ ] **G4b. `occupation_inherited` dropped.** Whether the work was inherited speaks directly to
      how plausible occupational transition is — a pilot item, one binary.
- [ ] **G4c. `ropeway_stance` is the weakest item in the instrument.** If any single question
      must be cut to buy time, this is the one; it is an attitude, it has no place in any of the
      three VEP arms, and the pilot's richer stance battery (`support_or_oppose`,
      `consulted_by_official`, five `attitude_*` items) is not being reinstated anyway.

## What is solid — do not reopen

- **Seasonal two-season design** (Modules C, E, I) — the strongest thing about this instrument.
  Every migrant-relevant quantity is asked per season and calendar-weighted; that is more
  careful than most published VtP instruments and it is the right call.
- **The 12-month calendar** (activity *and* earnings per month) — user-committed, anti-heaping,
  and the source of `income_seasonality_cv`, `yatra_months` and the season weights everything
  else depends on. Don't touch.
- **Module K / Apablaza** — the employment-VEP arm is the project's novel contribution; its
  14 items are load-bearing.
- **MPI coverage is complete**, including child school attendance via `n_children_6_14` /
  `n_children_out_school` → `child_school_dep`. (The limitation comment at
  `kedarnath_vtp_analysis.do:100-104` saying school attendance "cannot be constructed here" is
  **stale** — the final instrument added the items. Worth correcting when that file is next
  touched.)
- **No rating scales; factual three-answer task grid** — a real design commitment, consistently
  applied.

## The arithmetic problem

The instrument is at 46.4 min against a 45-min cap (HANDOFF open item 3), and HANDOFF open
item 2 (`secondary_work_type` → select_multiple) will add more. Everything above is additive.
So this is a **reallocation** decision, not an addition list. The honest options:

1. **Take it out of Module L.** L is 4.0 min for the explicitly-second paper; J is 1.0 min for
   the first paper's entire policy rationale. Trimming the 12-task grid to the 8 tasks that
   actually discriminate ropeway-adjacent occupations frees ~1.3 min, and G1b would make the
   remaining task data far more useful than the four dropped items were.
2. **Take it out of Module E.** 22 items / 8.0 min / 17.2% is the largest block, but it is the
   basis of the poverty line and one of the three welfare measures — the least safe cut.
3. **Accept ~50 minutes.** With 4 enumerators over ~10 days this is a real cost in achieved n,
   and n ≈ 250–320 is already at the low end for a 3-stage FGLS with ~15 covariates.

**Recommendation:** option 1, plus G1c (free — GPS is already collected), G3c and G2a/G2b
(cheapest high-value adds). That buys the ropeway module the substance it needs without
touching the consumption or calendar design.

## Suggested order

1. **G1c** — free, no interview time, data already captured.
2. **G1b** — highest value; decide the L-vs-J trade first.
3. **G3c, G2a, G2b** — one to three short items each, all adaptive-capacity/exposure.
4. **G3b** — the retrospective covariate-shock block; needed before any ropeway scenario
   (and before `FUJII_2016_GAPS.md` A1/A11 are worth doing).
5. **G2c, G3a, G4a** — magnitude and value items; cost more time, decide after 1–4 are costed.
6. **G1a/G1d, G4b** — expectation items; cheap individually, but only if the budget allows.
7. **G4c** — cut `ropeway_stance` whenever time is needed.
