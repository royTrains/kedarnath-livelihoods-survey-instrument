# Handoff brief — Kedarnath Yatra-worker survey instrument

## What this is
A fieldable survey instrument (questionnaire + worked-example Stata dataset + KoboToolbox
XLSForm) for a study of vulnerability to poverty among Kedarnath Yatra-route workers
(porters, pony workers, shopkeepers, hotel staff, guides, etc. — most are seasonal migrants).
Primary framework: Chaudhuri, Jalan & Suryahadi (2002) vulnerability-as-expected-poverty
(VEP), applied to (a) monetary consumption, (b) an Alkire-Foster MPI deprivation score, and
(c) an Apablaza et al. employment-deprivation score (a genuinely new combination — see
`do/03_employment_vulnerability.do`). Occupational skill-transferability is a **separate**,
later paper (`tasks_module/`), so its questions in this instrument are deliberately short.

Hard constraints: 4 enumerators, ~10 days fieldwork, one round (no phased/screener design),
**45-minute interview cap**. Current estimate is 46.4 minutes — over the cap, unresolved (see
"Open item" below). Everything here is a SYNTHETIC worked example; no real data exists yet.

## Where everything is
```
replication/final_instrument/         <- the deliverable; work here
  questionnaire/dictionary.py         <- SINGLE SOURCE OF TRUTH. Every variable: module,
                                          question wording, description, type, value labels,
                                          skip rule, and a `source` field citing exactly what
                                          informed it. Read this file first.
  questionnaire/build_questionnaire.py -> Kedarnath_final_questionnaire.pdf (paper script)
  questionnaire/build_xlsform.py      -> Kedarnath_final_kobo.xlsx (upload to KoboToolbox as-is)
  do/01_generate_raw.py               <- synthetic raw answers, numeric codes
  do/make_labels_do.py                -> do/labels.do (Stata labels, generated, don't hand-edit)
  do/02_build_final_dataset.do        <- Stata: builds all derived vars, asserts skip logic,
                                          applies labels -> data/kedarnath_final_n200_full.dta
                                          and kedarnath_final_n200_fielded.dta (retained==1)
  do/03_employment_vulnerability.do   <- 3-stage FGLS VEP applied to the employment-deprivation
                                          score (novel; no prior paper does this combination)
  checks/05_checks.py                 <- independent Python re-check of the Stata output
  README.md                           <- run order (do these 5 steps in sequence after any edit
                                          to dictionary.py) + Kobo deployment notes
  CHECKLIST.md                        <- full stage-by-stage history (12 stages) if you need
                                          the "why" behind a past decision in detail
```
Adjacent, NOT part of this instrument (don't confuse the two):
- `replication/kedarnath_vtp_analysis.do` — monetary + MPI VEP analysis on an OLDER,
  separate synthetic pool (predates this instrument's redesign). Different `poor` variable,
  not comparable to this instrument's numbers.
- `replication/vasyr_example/` — a separate illustrative piece replicating Lyons, Kass-Hanna
  & Montoya Castano (2023)'s MLI+VEP method on real UNHCR VASyR 2025 microdata (in `vasyr/`
  at the repo root). Not part of the Kedarnath instrument; a method demonstration.
- `tasks_module/` — the occupational-transferability side project (separate future paper).

## To rebuild after any edit to dictionary.py
Run in order (from `replication/final_instrument/`):
1. `python do/01_generate_raw.py`
2. `python do/make_labels_do.py`
3. Stata: `do do/02_build_final_dataset.do`
4. `python checks/05_checks.py`
5. `python questionnaire/build_questionnaire.py` and `python questionnaire/build_xlsform.py`

## Sources actually used (read directly, not just cited secondhand)
- **Chaudhuri, Jalan & Suryahadi (2002)** — 3-stage FGLS VEP methodology (the backbone).
- **Apablaza et al. (2026), "The Work Dimension in Multidimensional Poverty Measurement,"
  Appendix 2** — Module K (job quality) questions and skip logic, read and used directly.
- **HCES 2022-23 (MoSPI, India), IHDS-II Income & Social Capital Questionnaire, Nigeria
  GHS-Panel Wave 3** — consumption module (E) recall-period design, read directly section by
  section; also the Rangarajan-method poverty line (Sethu, Surya & Ruthu 2024; Rangarajan &
  Dev 2024 as CPI-adjusted sensitivity line).
- **VASyR 2025 (UNHCR/WFP/UNICEF Lebanon), real microdata in `vasyr/`** — Module I's reduced
  Coping Strategy Index items are worded to match VASyR's own item text exactly (checked
  against standard WFP CARI phrasing too; do not paraphrase these five items further).
- **Lyons, Kass-Hanna & Montoya Castano (2023), J. Int. Dev.** — combines Alkire-Foster MPI
  with Chaudhuri VEP; informs the MPI-VEP arm's logic (see `kedarnath_vtp_analysis.do` and
  `replication/vasyr_example/`).
- **NITI Aayog National MPI** — Module F housing/asset indicators, education indicator logic.
- **NSS 64th Round / PLFS** — migration classification (Module D), employment status
  classification (Module B).
- **Dercon & Krishnan (2000); Beegle et al. (2012); Deaton & Grosh (2000)** — monthly
  calendar / seasonality measurement and recall-period design principles.
- **Azeem, Mugera & Schilizzi (2016)** — adaptive-capacity/sensitivity/exposure covariate
  structure used in the VEP regressions.
- **STEP (World Bank) and Gathmann & Schonberg (2010)** — Module L task/skills items
  (belongs to the separate transferability paper; kept short here).
- **UN Livelihood Assessment Toolkit** — the user has identified this (not Dercon & Krishnan
  or Apablaza alone) as the actual source design for the monthly-calendar / occupation
  questions in Module B/C. **This has not yet been read directly in this project** — do that
  next, the same way every other source above was read in full before being cited, and
  re-align Module B/C's citations and wording with it where it differs from what's there now.

## Open items — discussed with the user, NOT yet implemented

1. **Poverty line choice.** Recommendation already agreed in chat, not yet written into
   `dictionary.py`: keep ONE national rural line for everyone (current choice: Sethu et al.
   2024, Rs 2,515), including Nepal-origin workers — same principle Lyons et al. (2023) use
   for Syrian refugees in Lebanon (measured against Lebanese thresholds, not a Syrian line:
   vulnerability is measured within the economy the worker is currently embedded in, not
   their home country/state). Do NOT switch to an Uttarakhand state line — it would wrongly
   apply hill-economy prices to off-season consumption that mostly occurs outside Uttarakhand
   for a majority-migrant sample. To implement: add one new question, whether the
   respondent's *usual place of residence* (not the Yatra site) is rural or urban — India has
   separate rural/urban lines, and this lets the right one be applied per respondent without
   needing a full spatial price deflator. State explicitly as a limitation: consumption is
   not price-deflated between the Yatra season and the off-season/home context.

2. **Secondary-work item needs a different widget.** `secondary_work_type` (Module B) is
   currently a single select_one (one code, drop-down-style). User wants a select_multiple
   checklist (check every other activity that applies) plus a free-text "other, specify" —
   real workers combine more than one side activity, and a single choice undercounts that,
   same complaint that motivated adding this item in the first place. This is a genuine
   redesign, not a small edit: dictionary.py's `R()`/`kind`/`lset` system currently assumes
   one variable = one value; there is no multi-select concept yet. Kobo's select_multiple
   exports as a space-separated string plus auto-generated binary sub-columns per choice,
   which nothing in `01_generate_raw.py` or `02_build_final_dataset.do` currently parses.
   Plan the multi-select representation (e.g. one binary variable per occupation code, like
   the productive-assets pattern already used in Module F) before touching the code, then
   update the synthetic generator, Stata build, checks, PDF and XLSForm builders together.

3. **Time budget.** Interview time is estimated at 46.4 minutes against a 45-minute hard cap
   (see `MODULES` list at the top of `dictionary.py`, and `CHECKLIST.md` Stages 11-12 for how
   it got here — several rounds of well-justified fixes each added real time). Do not just
   nudge the numbers down to force compliance. Either get the user to accept a longer
   interview, or work with them to name specific items to cut, then rebuild per the steps
   above. Item 2 above will add more time, not less — factor that in when this is resolved.

## How reasoning/citations are recorded
Every question's rationale lives in `dictionary.py` itself: the `desc` field explains the
measurement choice, and the `source` field gives the citation (often down to a section or
question number). That is the reasoning trail — read the `R(...)` row for a variable before
changing it, not just the CHECKLIST.md summary.
