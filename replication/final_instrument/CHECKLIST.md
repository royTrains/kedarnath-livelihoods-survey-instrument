# final_instrument — working checklist

Tracks the final questionnaire, variable dictionary and worked-example dataset in this folder.

## Stage 1 — Questionnaire v1
- [x] 1.1 dictionary.py (single source), 146 variables, run pipeline (raw -> Stata build -> checks -> PDF)
- [x] 1.2 Stata build clean; independent pandas checks pass

## Stage 2 — Questionnaire v2 (user corrections, 2026-09-21)
- [x] 2.1 12-month calendar restored (activity + earnings per month, avoids heaping); reproduces earlier
      income/seasonality exactly (checked in checks/05_checks.py)
- [x] 2.2 Employment block rebuilt on Apablaza et al. 2026 Appendix 2 questions, their skip logic kept,
      all five deprivation indicators built from raw answers (Table 3 thresholds)
- [x] 2.3 Licence/certificate items removed; replaced with factual driving-experience items
      (motorcycle/car/truck-bus, asked regardless of licence)
- [x] 2.4 Consumption: food split into bought / home-grown-in-kind / eaten-outside, totals unchanged;
      duplicate medical question dropped; narrow and adult-equivalent consumption measures added
- [x] 2.5 Stata build clean (175 variables), independent checks pass, questionnaire PDF rebuilt

## Stage 3 — Consumption module: read the actual source questionnaires, cite by item
- [x] 3.1 Located and read HCES 2022-23 official questionnaire: MoSPI Appendix A (FDQ/CSQ/DGQ/HCQ, 56
      pages). Structure: 30-day staples (Sec 5.1-5.3), 7-day perishables + eating out (Sec 6-7), 30-day
      fuel/toiletries/conveyance/phone/rent (Sec 8-11), 365-day clothing/footwear/education/hospitalisation
      /durables (Sec 10,13-14), 30-day non-hospitalisation medical (Sec 10.3). No insurance in consumption.
- [x] 3.2 Located and read IHDS-II Income & Social Capital Questionnaire, Q14 (33 items at 30-day,
      14.1-14.33; 19 items at 365-day, 14.34-14.52, codes CO1-CO52). Matches HCES exactly on the
      hospitalisation/non-hospitalisation medical split and on clothing/footwear/education at 365-day;
      differs from HCES by asking all food at 30-day (no 7-day perishables tier)
- [x] 3.3 Located and read Nigeria GHS-Panel Wave 3 Household Questionnaire, Sections 10B (food, 7-day)
      and 11 (non-food: 7-day/30-day/6-month/12-month tiers). Confirms 30-day for fuel/toiletries/
      transport/rent and 12-month for durables across all three sources; uses 6-month (not 12) for
      clothing; combines medical into one 6-month item; treats insurance as consumption (HCES does not)
- [x] 3.4 Built the final consumption item list (13 items, up from 10), each cited to its exact section/
      question number in one or more of the three source questionnaires; divergences across sources
      documented and a choice made (follow HCES throughout, since it is also our poverty-line source)
- [x] 3.5 Updated dictionary.py (Module E rewritten + new constructed-variable formulas), 01_generate_raw.py
      (food split into staples-30d/perishables-7d/own-30d/eaten-out-7d; medical split by hospitalisation
      flag; routine split into routine-misc/transport-comm), 02_build_final_dataset.do (7-day items scaled
      x30/7; medical and food totals reconstructed), checks/05_checks.py, questionnaire PDF section 8
- [x] 3.6 Stata build clean (181 variables); independent checks pass. cons_pc_pm / total_cons_pm are no
      longer bit-identical to the pre-rebuild file (7-day scaling introduces rounding), but the difference
      is small (max 0.4-0.6% relative) and `poor` is unchanged for every respondent
- [x] 3.7 Noted in the questionnaire write-up (section 7, "points still open"): self-employed =
      employment_type 1/2 (own-account, employer), matching Apablaza Q8 codes 5/4; near-universal lack of
      pension among self-employed/casual is expected (EPFO is formal-wage-only; APY/PM-SYM uptake is low
      nationally) — flagged as low-variance within that group, not a data error

## Stage 4 — Migrant seasonality redesign (consumption + remittances) and variable-name-length fixes
- [x] 4.1 Consumption module E rebuilt as 9 Yatra-season/off-season pairs (instead of one 7-/30-day figure):
      fieldwork happens during the Yatra season, so a single recent-recall question could only capture
      on-site spending, not the "usual homeplace" figure the design needs for a migrant workforce. Module C
      remittances rebuilt the same way (4 seasonal items, was 2 flat annual). Both weighted into an annual
      figure by yatra_months/(12-yatra_months), mirroring the existing income calendar's logic
- [x] 4.2 Fixed a 32-character Stata variable-name-length bug (`cons_medical_nonhosp_offseason_pm` -> 33
      chars) in three places: dictionary.py + generators, the `foreach v in ... medical_nonhosp` loop list in
      02_build_final_dataset.do (bare name, missed by the first sed pass), and the constructed-variable tuple
      list in dictionary.py; renamed medical_nonhosp -> med_nonhosp throughout
- [x] 4.3 Stata build clean (201 variables); independent checks pass, including on/off-season ratios by item
      (purchased items ~0.72-0.73 off-season; home-grown food higher off-season for 53% of farming/animal-
      husbandry households; rent near-zero off-season for non-local migrants). cons_pc_pm fell from a mean
      of Rs 2,763 to Rs 2,406 and the poverty rate rose from 39% to 62.5% in the synthetic data — the old
      design implicitly treated on-season spending as if it held all year; noted in the questionnaire PDF
- [x] 4.4 Questionnaire PDF rebuilt (14 pages); minimal text corrections only (sections 6, 8.3), no new
      LaTeX/documentation sections added, per the "don't go overboard" instruction

## Stage 5 — Caste question replaced with native language; VASyR/Lyons et al. worked example
- [x] 5.1 Removed `social_group` (SC/ST/OBC/General) and the `social` value-label set: caste is sensitive to
      ask directly and does not classify non-Indian migrants (Nepali workers) in any comparable way. Added
      `native_language` (Garhwali/Kumaoni/Hindi/Bhojpuri-Maithili/Nepali/Bengali/Other) instead, generated in
      01_generate_raw.py as a function of origin, as a non-sensitive proxy for regional/class background that
      covers every respondent including out-of-country migrants
- [x] 5.2 Stata build clean (still 201 variables); independent checks pass; questionnaire PDF rebuilt
- [x] 5.3 Read Lyons, Kass-Hanna & Montoya Castano (2023, J. Int. Dev.) in full: builds a 5-dimension,
      21-indicator Alkire-Foster multidimensional livelihood index (MLI) from the 2018 VASyR survey, then
      runs Chaudhuri et al. (2002)'s 3-stage FGLS on the deprivation score (not log-consumption) to predict
      vulnerability to future poverty, with governorate fixed effects
- [x] 5.4 Built a small worked example of the same procedure in `replication/vasyr_example/` (separate from
      the Kedarnath instrument). Initially built as a synthetic dataset (`vasyr_synthetic_example.do`, kept as
      a fallback) since real VASyR microdata seemed to need a licensed UNHCR Microdata Library application —
      corrected once the user pointed out the real data was already in `vasyr/` at the repo root (2025 VASyR
      wave, Lebanon: 3,546 households, 16,006-row member roster, 975 household-level columns)
- [x] 5.5 `build_vasyr_real.py`: read both CSVs, aggregated the member roster to household level, mapped 21
      columns onto Lyons et al.'s Table 2 indicators (legal residency, curfew, host-community interaction,
      rCSI food-coping, 7-day food-group diet count, electricity/toilet/water/cooking-fuel/assets/crowding/
      shelter-type are exact or near-exact matches; adult-schooling, underemployment, healthcare-access,
      area-settlement, housing-stability and the expenditure/SMEB proxy are documented proxies since the 2025
      questionnaire doesn't carry every 2018 item — see README). Wrote `vasyr_real_raw.csv`, 3,490 households
- [x] 5.6 `vasyr_real_example.do`: same MLI + 3-stage FGLS procedure as the synthetic version, run on the real
      data. Runs clean. H=0.519, A=0.415, MLI=0.216 (vs. Lyons et al.'s 2018 H=0.365/MLI=0.159 — higher,
      consistent with Lebanon's 2019-2023 currency collapse); vulnerability groups 1,144 chronic/536
      transient/668 escaped/1,142 non-poor, overall vulnerability rate 48.1%. FGLS Stage-3 signs as expected:
      larger/married-head households and the poorest income quartile more deprived, employment-based income
      significantly less deprived (matches Lyons et al.'s own finding)
- [x] 5.7 User asked for a Stata-only version (no Python step): `vasyr_stata_only.do` imports both original
      CSVs directly, collapses the member roster to household level with `collapse`/`egen`, captures the two
      column names over Stata's 32-character limit by CSV column position rather than typing them, and drops
      5 of 3,549 rows with a blank id caused by stray unmatched quotes in a free-text answer (noted by Stata
      on import; confirmed the smaller fix vs. bindquote(nobind), which misaligns far more rows elsewhere).
      Runs clean; N=3,488, H=0.519/A=0.415/MLI=0.215, matching the Python-built version to within 2 rows

## Stage 6 — Real VASyR items ported into the Kedarnath instrument
- [x] 6.1 User asked to add VASyR's actual variables (or the equivalent) into the fielded Kedarnath survey
      itself, not just the standalone example. Reviewed the instrument for genuine gaps against VASyR/Lyons
      et al.'s "health and food security" dimension rather than duplicating what Module F/K already cover
      (living standards, employment) — found the instrument had no food-security or disability module at all
- [x] 6.2 Added to Module H (Health): `chronic_illness_disability` (VASyR 2025 `chronic_illness_yn` /
      Washington Group Short Set; Lyons et al. Table 2 indicator 1, "special needs") and
      `health_access_barrier_3m` (VASyR `barriers_health_case_access_phc_m`; Table 2 indicator 2, "healthcare
      access") — an unmet-need question, distinct from the existing insurance-coverage item
- [x] 6.3 Added to Module I (renamed "Food security, shocks and coping"): the 5-item WFP reduced Coping
      Strategy Index (rCSI) as day-counts over the last 7 days (`cope_less_pref_food_7d`, `cope_borrow_food_7d`,
      `cope_reduce_meals_7d`, `cope_reduce_portion_7d`, `cope_restrict_adult_7d`), matching VASyR's own items
      and Lyons et al. Table 2 indicator 3. A full dietary-diversity/FCS module was left out to stay inside
      the 45-minute budget; noted as a documented omission in the questionnaire PDF
- [x] 6.4 Constructed `rcsi_score` (standard WFP weights 1/2/1/1/3) and `food_coping_deprived` (rCSI>20, the
      Lyons et al./VASyR cutoff) in Stata. 7 new asked variables, 2 new constructed (210 total: 141 asked, 10
      paradata, 54 constructed, 5 synthetic-only). Interview-time budget bumped from 37 to 39 minutes base
      (+2 min) in the synthetic timing generator to reflect the added burden
- [x] 6.5 Full pipeline rebuilt clean: `01_generate_raw.py` (rCSI day-counts scaled to the existing `poor`
      tier, chronic illness scaled to age/poor), Stata build, independent checks (mean rCSI 7.3,
      food_coping_deprived 6%, chronic illness/disability 15%, unmet health need 20% — all sane, non-
      degenerate), questionnaire PDF rebuilt with a new changelog bullet. Total questionnaire time: 43.7
      minutes (was 41.4), still under the 45-minute cap

## Stage 7 — Vulnerability to Employment Poverty (new methodological contribution)
- [x] 7.1 User asked to apply the project's own Chaudhuri et al. (2002) 3-stage FGLS VEP machinery to
      Apablaza et al. (2026)'s employment-deprivation score, noting no paper has combined the two —
      "vulnerability to EMPLOYMENT poverty," as opposed to the monetary and MPI arms already in
      `kedarnath_vtp_analysis.do`. A candidate paper angle in its own right, not just an instrument addition
- [x] 7.2 New file `replication/final_instrument/do/03_employment_vulnerability.do`, self-contained, run on
      this instrument's own as-fielded dataset (n=104, not the older n125/n200 pool — only this dataset has
      the Apablaza domains). Welfare = `emp_dep_score` (0-1, already built); cutoff = 0.4 (k=2 of 5, matches
      `emp_poor_k2`); same 3-regression Stage1-OLS/Stage2-OLS/Stage3-WLS pattern as the MPI arm, flipped
      inequality (vulnerable = Pr(score EXCEEDS cutoff) ≥ 0.5)
- [x] 7.3 Covariates deliberately exclude every variable that mechanically builds emp_dep_* (job_situation,
      contract_status, pension_contrib, hours_week_yatra, etc.) — predictors OF deprivation, not deprivation
      itself, same discipline as the MPI arm. occupation (13 categories) left out of X for degrees-of-freedom
      reasons on n=104, matching the original file's own Xvars_sens choice
- [x] 7.4 Runs clean (N=98 of 104, 6 dropped for missing education_years as elsewhere in this project).
      Current emp_poor_k2 60.6%, employment-VtP rate 34.7% (26 chronic/8 transient/32 escaped/32 never-poor).
      FGLS signs sensible: casual wage (+0.45) and employer status (+0.15) more deprived than own-account,
      institutional credit access (-0.12) less deprived, all p<0.001. Cross-tab with current monetary poverty
      shows only partial overlap (67% of employment-poor are monetary-poor, but so are 61% of the NOT
      employment-poor) — the same kind of partial-overlap finding that motivated Lyons et al.'s own paper,
      here for employment vulnerability specifically

## Stage 8 — XLSForm for KoboToolbox
- [x] 8.1 User asked to build the survey in Kobo, then clarified: using XLSForm (the standard
      Excel-based form-definition format KoboToolbox and ODK both compile). New
      `questionnaire/build_xlsform.py`, reading from the same `dictionary.py` single source of truth
- [x] 8.2 Kobo-native substitutions for paradata (documented in README section 6): resp_id dropped
      (Kobo's own submission id serves this), interview_date/interview_duration_min dropped in favour
      of standard `start`/`end` meta questions, dur_tasks_min left out (marginal value vs. complexity),
      gps_lat/gps_lon merged into one `geopoint` question. Consent gates the whole rest of the form via
      `relevant = ${consent} = 1` on a wrapping group — the standard XLSForm "stop if no" pattern
- [x] 8.3 Skip logic (26 of 141 asked items) hand-built as XLSForm `relevant` expressions from the
      actual variable coding, not parsed from dictionary.py's free-text `skip` field. One hidden
      `calculate` field (`calc_months_no_work`) added to support `looked_for_work_idle`, which needs a
      count Stata normally only builds after the fact
- [x] 8.4 Installed pyxform and validated the output the same way KoboToolbox does internally
      (`xls2xform --skip_validate`): zero errors. Spot-checked the compiled XForm XML — consent gate,
      cross-references (e.g. income_m1 relevant to status_m1 != 8), and the hidden calculate all
      resolved to correct absolute XPath expressions. `questionnaire/Kedarnath_final_kobo.xlsx`: 149
      survey rows, 32 choice lists (135 choice rows), ready to upload as-is (New project -> Upload
      XLSForm on kf.kobotoolbox.org)

## Stage 9 — Same-day corrections: seasonal rCSI, household head, family structure, residence-migration
- [x] 9.1 User flagged that the new 7-day rCSI coping questions (Stage 6) have the same migrant-seasonality
      flaw already fixed once for consumption and remittances: fieldwork happens during the Yatra season, so
      a single "last 7 days" recall only captures on-site coping, not the household's usual (possibly very
      different) off-season pattern. Rebuilt as 10 Yatra-season/off-season pairs, same design as Module E,
      combined into an annual-average rcsi_score weighted by yatra_months/(12-yatra_months), same as income
      and consumption. cope_*_7d names retired; cope_*_yatra_wk/cope_*_offseason_wk take their place
- [x] 9.2 Added `usual_residence_differs` (Module D, skip-gated on non-local origin): whether the respondent's
      usual place of residence for most of the year differs from their family's native/home place, distinct
      from `origin` (where they're originally from) and the NSS short-term-migrant item (a specific 15-day-
      to-6-month threshold) — a genuine settled-elsewhere-vs-circular-migrant distinction the instrument
      didn't have.
      **SUPERSEDED 2026-09-28.** The variable no longer exists. Its gate was the problem: the pilot puts
      11 of 20 seasonal movers inside this same district, so gating on non-local origin skipped most of
      the people who move. Replaced by `closure_base` (ungated) plus the `loc_m1..12` location row on the
      monthly calendar — see Stage 13. The NSS reference above is also unsupported: this project holds
      no NSS schedule, and every NSS citation in the instrument has since been withdrawn or flagged.
- [x] 9.3 Added `hoh_relation` and `hoh_female` (Module A): respondent's relationship to the household head,
      and the head's sex — auto-filled with the respondent's own sex (`female`) when they are the head
      themselves, skip-gated in both the Stata build and the XLSForm, with an assert validating the auto-fill
      matches in the synthetic data
- [x] 9.4 Reworded `hhsize` (dropped the "eat from the same kitchen" framing, now "how many members live in
      your household") and added `family_structure` (nuclear/joint/single-member; single-member only valid
      when hhsize==1, asserted in Stata)
- [x] 9.5 221 variables total (150 asked, +9 net from Stage 6's 141: +4 new items, 5→10 coping items).
      Interview-time budget: Module A 3.7->4.0 min, D 1.5->1.6 min, I 3.2->4.0 min; total instrument time
      44.9 minutes (was 43.7), still just under the 45-minute cap. Full pipeline (raw generator, labels,
      Stata build, checks, PDF, XLSForm) rebuilt clean; pyxform re-validated the XLSForm with the corrected
      relevant expressions for the two new skip-gated items -- zero errors

## Stage 11 — Large correction round: education, multiple work, cards, migration, consumption
- [x] 11.1 **Education**: replaced the categorical `education_level` with a direct `years_schooling`
      count, gated by a `knows_years_schooling` yes/no; only respondents who can't recall get a
      4-category fallback bracket (`education_level_cat`, plus prefer-not-to-say) -- minimises
      categoricals as asked, rather than defaulting straight to a category
- [x] 11.2 **Multiple work-holding**: added `secondary_work_yn`/`secondary_work_type` (Module B) --
      the single main-occupation code undercounts workers who combine activities (a shop owner who
      also rents out a pony); the main quota variable is kept as is, this just adds a check for more
- [x] 11.3 **No cards anywhere**: removed every "Show card"/"Card." instruction across the whole
      questionnaire (occupation, prev_occ, hoh_relation, native_language, family_structure, the
      12-month calendar, shock_coping, job_situation, job_permanence, the task grid). High-cardinality
      classification items (occupation, prev_occ, secondary_work_type, hoh_relation, native_language)
      are asked openly and coded by the enumerator rather than read aloud; short scales are read aloud
      in full. Also fixed a systemic source: `build_questionnaire.py`'s PDF generator was auto-inserting
      "Card." for any categorical with >7 choices in its Answers column -- removed that branch entirely
- [x] 11.4 **NSS short-term-migrant item dropped** -- true by survey construction for a workplace-
      intercept sample, so uninformative. **`migration_reason` replaced with `migration_referral`**
      (who helped/guided the respondent to this work: family/friend/contractor/political-community
      connection/self/employer) -- a proxy for social/political capital, replacing a question whose
      answer would almost always just be "employment"
- [x] 11.5 **Consumption module (Module E)**: the Yatra-season question stem changed from "your
      household" to "you (and anyone staying with you here)" -- during the Yatra season the household
      may be split (respondent here, family elsewhere, linked by remittances), so asking about
      household-wide spending assumes knowledge the respondent may not have. `cons_food_own` reframed
      from "valued at market price" (assumes precise market-price knowledge of one's own produce) to
      "if you had to buy it" (the same imputation, in an answerable question)
- [x] 11.6 **Housing (Module F)**: `floor_material`/`roof_material`/`house_type` changed from
      "enumerator observes" to directly asked, self-reported about the respondent's *usual home* --
      the enumerator is at the Yatra worksite, not the respondent's actual home, and cannot observe it.
      `electricity`/`toilet_facility`/`drinking_water`/`cooking_fuel_lpg` reworded to match ("at your
      usual home") for consistency
- [x] 11.7 **Asset counts replaced with binary lists**: `livestock_count`+`pony_count` (2 items) ->
      `owns_cow_buffalo`/`owns_goat_sheep`/`owns_pony_mule` (3 binaries); `business_asset_owned` (1
      item) -> `owns_shop_stall`/`owns_work_vehicle`/`owns_work_equipment` (3 binaries). A count treats
      a goat and a buffalo, or a jeep and a hand-cart, as equally valuable, which they are not
- [x] 11.8 **`chronic_illness_disability` removed** (Module H) -- user challenge ("why this question?")
      taken as a removal request; `health_access_barrier_3m` (unmet care) kept
- [x] 11.9 **rCSI kept as day-counts (0-7), not converted to binary** -- checked for precedent first: no
      comparably-standard binary version of the WFP/FAO rCSI was found (the day-count x severity-weight
      design is the specification itself), and a day-count takes about as long to answer as a yes/no in
      practice, so little time would be saved either way. Documented in dictionary.py so the check is
      visible, not just asserted
- [x] 11.10 **Module K rebuilt on Apablaza et al.'s actual structure**, read directly with its own skip
      logic (roster-dependent items Q1-Q4 and open-text occupation/sector items Q6-Q8 not reproduced --
      already covered by Module B, or incompatible with the no-roster design): `job_situation` expanded
      to Apablaza's 5 categories; `job_permanence` un-merged back to 5 (was 4, probation/fixed-term
      combined); `hours_week_yatra` now asked directly in one question (Q13), replacing the
      hours-per-day x days-per-week pair in Module B; `leave_rights`' wage-worker-only skip dropped to
      match Apablaza (asked of everyone still working); `looked_for_work_idle` (yes/no) replaced with
      `weeks_looked_for_work` (duration in weeks, Apablaza's own unit, Q23), tied to the calendar's idle
      months rather than a single point in time. Every K-module item downstream of the screener is now
      also gated on `job_situation` being 1/2/3 (currently working), matching Apablaza's Q5 routing
- [x] 11.11 Full pipeline rebuilt clean end to end on the first real pass (raw generator, labels, Stata
      build with substantially rewritten skip-rule asserts, independent checks, PDF, XLSForm re-
      validated with pyxform, cross-references spot-checked in the compiled XForm XML -- including the
      cross-group reference from `weeks_looked_for_work` to `grp_C/calc_months_no_work`). 225 variables
      (154 asked, up from 150). Time estimate now 45.4 minutes (was 44.9) -- honestly reported as
      essentially at the cap rather than forced under it: no-cards plus the fuller Apablaza categories
      and the housing fix (observed -> genuinely asked) add real time that the removed items (NSS
      migrant question, disability question, the hours-pair merge) only partly offset. A pretest should
      confirm; if it runs long, Module F's newly-asked housing items and Module K's expanded categories
      are the clearest places to look first

## Stage 12 — Follow-up corrections: precedent-checked wording, un-reverted hours, Apablaza completeness
- [x] 12.1 **Secondary work recorded explicitly**: dropped the `secondary_work_yn` gate; `secondary_work_type`
      is now asked directly (coded 0 = none, using a new `occ0` list), and a follow-up
      `secondary_work_income_pm` (skip-gated on not-none) captures the income from it, not just its presence
- [x] 12.2 **Morbidity now asks impact**: added `morbidity_coping_15d` (same coping list as the shock
      question) and `morbidity_cost_15d`, both skip-gated on `morbidity_15d = 1` -- a reported illness with
      no cost/coping follow-up said nothing about its burden
- [x] 12.3 **Hours reverted to decomposed**: `hours_week_yatra` (Stage 11's single direct Apablaza-style
      ask) reverted back to `hours_day_yatra` x `days_week_yatra`, asked separately and multiplied in
      Stata -- a normal day is easier to recall accurately than a whole week at once; `hours_week_yatra` is
      constructed again, matching the pre-Stage-11 design
- [x] 12.4 **`migration_referral`'s "fellow villager" category simplified** to "Friend or acquaintance"
- [x] 12.5 **`years_since_migration` dropped** -- redundant with `years_in_yatra_work` (Module B) for this
      study's purposes; asking both a migration-duration and a work-tenure figure asked the same thing
      twice in most cases
- [x] 12.6 **rCSI reworded to VASyR's exact item text**, checked against both VASyR's own wording and the
      standard WFP CARI phrasing (searched online, both confirmed as the same underlying specification):
      "rely on less expensive/less preferred food", "borrow food and/or rely on help from friends/
      relatives", "reduce the number of meals eaten per day", "reduce portion size of meals", "restrict
      consumption of adults/mothers in order for young children to eat" -- only the recall-period framing
      (usual week per season, not literal "last 7 days") is adapted, not the coping-behaviour wording itself
- [x] 12.7 **Module K completed against Apablaza's full ~25-item list**: added `main_income_earner`
      (Module A, adapted Q4 -- "are you the main income earner" for a single-respondent report),
      `employer_type` (Q8's own 7-way employer/employee classification, alongside this project's own
      4-way employment_type), and `first_job_ever` (Q24). Documented explicitly why three more items are
      NOT reproduced: Q1-Q4 roster demographics (no-roster design), Q6/Q7 open-text occupation/sector
      (already covered by occupation's 13 groups, which blend occupation and workplace type for this
      economy), Q14/Q15 single-point earnings + fallback range (the 12-month calendar already asks
      earnings month by month, more informative than one point estimate)
- [x] 12.8 231 variables (159 asked, up from 154). Full pipeline rebuilt clean on the first real pass again
      (raw generator, labels, Stata build, checks, PDF, XLSForm re-validated with pyxform, all new/changed
      skip expressions spot-checked in the compiled XForm XML). Time estimate now 46.4 minutes (was 45.4) --
      reported honestly again rather than forced under 45. Across Stages 11-12 the instrument has grown
      past the 45-minute target through several rounds of well-justified fixes; worth flagging to the user
      directly rather than continuing to silently absorb it into module estimates

## Stage 10 — De-identifying paradata on the Kobo form
- [x] 10.1 User asked to remove the enumerator-name question, auto-capture GPS instead of asking, and stop
      naming the interview-site cluster. `enum_id` dropped from the XLSForm (`DROP_PARADATA`) -- each
      enumerator gets their own Kobo login, and Kobo's own `username`/`_submitted_by` export column replaces
      the manual "pick your name" question, with no risk of picking the wrong one
- [x] 10.2 `gps_location` changed from an interactive `geopoint` question to `background-geopoint`, triggered
      on `${consent}` (fires via `odk:setgeopoint` the moment consent is answered) -- no on-screen question,
      no enumerator interaction. Confirmed in the compiled XForm XML that pyxform wired the trigger correctly
- [x] 10.3 `location_cluster`'s choice labels genericised to "Cluster 1".."Cluster 4" in dictionary.py's
      `cluster` LSET (was the actual site names) -- enumerators now pick from a printed crosswalk card kept
      by the research team, not a name shown on the tablet or stored in the export. Numeric codes (1-4) and
      the Stata logic that reads them (`health_access_tier`) are unchanged, only the labels/prose; updated
      `health_access_tier`'s construction note to reference cluster numbers instead of place names.
      Ropeway-related questions (Module J) were deliberately left unchanged -- they reference the actual,
      publicly proposed Gaurikund-Kedarnath ropeway route, not the anonymised interview-site classification
- [x] 10.4 Full pipeline rebuilt clean (Stata build, checks, PDF, XLSForm); XLSForm re-validated with pyxform
      (zero errors) and the compiled XML spot-checked directly for all three changes. No variable-count or
      time-budget change (paradata/labelling only) -- still 221 variables, 44.9 minutes

## Stage 13 — Migration module replaced by a closure-regime block; read-aloud module intros (2026-09-28)
- [x] 13.1 **Source audit first, and it came back empty.** Searched `literature/` (~90 papers, all with text
      extractions) and `microdata/`: this project holds **no migration instrument** -- no NSS schedule, no
      PLFS, no Census D-series, and nothing on migration measurement in any of the three `.bib` files. The
      only mobility-measuring instrument held is VASyR 2025 (arrival dates, displacement, horizoned intention
      to move), which is forced displacement. Consequence: four NSS citations were **withdrawn** from
      `dictionary.py` (`origin`, and the two remittance pairs) and four more flagged
      `[source not held by this project; citation unverified]`. Three of the withdrawn ones had been written
      the previous day and were never verifiable
- [x] 13.2 **The module was measuring the wrong thing.** Everything was gated on `origin != 1` (non-local),
      but the pilot's own `residency_pattern x local` crosstab (n=46) puts **11 of the 20 seasonal migrants
      inside this same district**. The gate therefore skipped most of the people who actually move --
      including on `migration_pattern`, whose only purpose was to test whether people leave when the Yatra
      closes. Seasonal movement here is mostly *local* movement, up-valley for the season and down-valley at
      closure, and a migrant dummy built on district boundaries sees almost none of it
- [x] 13.3 **Closure relocation is now the baseline regime.** `closure_base` (4 codes, ungated) replaces
      `migration_pattern`, `migrates_with_family` and `usual_residence_differs`; its categories are the
      pilot's own three residency types with the split-household case broken out by whether the respondent
      himself returns (the pilot found 3 of 46 working here with family elsewhere -- the case Module E's
      "you and anyone staying with you here" wording was written for, which until now had nothing to key off)
- [x] 13.4 **`worked_away_in_closure` + `closure_work_detail`**: off-season labour migration, asked of
      everyone, verbatim destination office-coded to NCO-2015. This is the mobility variable that actually
      carries information in this population, and it is what `closure_labour_migrant` feeds into the VEP
      model in `04_vtp_analysis.do`. `migrant` is kept alongside as a distance control, which is all it
      ever measured
- [x] 13.5 **`loc_m1..loc_m12`: a location row on the monthly calendar.** Turns the Yatra-season/off-season
      split -- which every consumption, remittance and coping item in Modules C, E and I assumes -- from an
      assumption into a per-respondent measurement, and settles the mid-month season-boundary problem,
      because each respondent's boundary is now wherever their own row turns over instead of a constant we
      impose. Derives `months_here`, `months_home_base`, `months_third_place`
- [x] 13.6 **`home_admin_level` dropped**, `home_rural_urban` asked directly. The village/town/city tier
      asked the respondent to perform a Census classification they have no way of making, and then picked
      the Rs 2,515 or Rs 3,639 poverty line off the answer -- a 45% swing behind a subjective tier.
      `migration_referral` and `worked_other_places` ungated: who placed you in a job is a question about
      the employment relationship, not about migration
- [x] 13.7 **Read-aloud module introductions** for all twelve modules, EN and HI, in `dictionary.INTROS` /
      `translations_hi.INTROS_HI`. They reach the XLSForm (as `note` rows), the web form (a tinted
      read-aloud box rendered with the module heading on its first *visible* question -- not a screen of its
      own, which would have cost twelve taps and needed an entry in `shown`, and navigation is keyed on
      question names via `posOf()`), both interview scripts, the paper questionnaire and the question
      register. `build_scripts.py`'s `BRIDGE_EN`/`BRIDGE_HI` were a second, thinner copy of the same
      read-aloud text in a second file; they now alias `INTROS` so the two cannot drift
- [x] 13.8 **Two defects found and fixed in the post-build audit.** (a) `assert loc_m`m'==1 if
      status_m`m'==1` was both unenforced by the form (no such constraint exists, so it would have halted
      the build on data Kobo accepts -- the same failure this file already had to remove once) and
      substantively wrong: a Guptkashi or Sonprayag worker commuting up the route daily does Yatra work
      while living at the home place, and that is a true answer. Removed. (b) The activity row still carries
      two codes that encode *location* -- 4 "wage labour, staying at home" and 5 "went away from home for
      work" -- which can now contradict the location row; the impossible combinations are counted as
      `dq_act_loc_conflict` rather than asserted. **The overlap itself is left for a decision** -- see
      Open items
- [x] 13.9 Verified: 77/77 skip rules agree with the XLSForm across 100 simulated submissions, rule ordering
      clean, 7/7 navigation tests, 50/50 forms filled and exported end to end through the form's own code
      with zero validation dead-ends, pyxform validates, Stata build and both analyses run clean, all eight
      analysis-readiness groups pass. 361 dictionary rows / 220 asked

## Stage 14 — Field-review batch: nine issues from filling the form (2026-09-30)
- [x] 14.1 **A live error in the poverty headcount.** `cons_pc_pm` divided `total_cons_pm` by `hhsize`,
      but the Yatra-season consumption items are asked as "you and anyone staying with you here" while
      the off-season items are asked of "your household". A split household therefore had one man's six
      months of on-site spending charged against five people and fell below the line by arithmetic.
      Fixing it by dividing the season half by `n_here_season` **overcorrected** — split households went
      from 55% poor to 5% poor, because his on-site spend over 1.6 people looks affluent while the same
      earnings support 4.1 at home. Both are biased, opposite ways. The close is that the home-side flow
      IS observed: for a split household the season numerator is on-site spending **plus** outward
      remittances, over full `hhsize`. Poverty 0.55 → 0.42; split 0.33 against non-split 0.46.
      `cons_pc_onsite_pm` retained as the individual-welfare sensitivity
- [x] 14.2 **The season weight is now `months_here`, not `yatra_months`.** Months physically on the
      route, not months of Yatra *work* — the Yatra-season spending figure describes spending while
      here, so that is the weight it belongs to. Before the absence spell existed there was nothing
      else to use
- [x] 14.3 **`loc_m1..loc_m12` replaced by an absence spell** (`left_here_month`, `returned_here_month`,
      `months_away_for_work`). Twelve select_ones for what is almost always one contiguous absence was
      a sixth of the interview; three questions carry it, and `months_here` / `months_home_base` /
      `months_third_place` are all still derived. The spell straddles the new year, so the Stata
      arithmetic wraps with `mod()`
- [x] 14.4 **`closure_base` split into two binaries** (`resp_returns_at_closure`, `hh_at_home_place`).
      The old stem named two subjects in one breath and offered a binary against four options. Same
      four cells, derived in Stata from two plain yes/no answers
- [x] 14.5 **`water_on_premises`**: an either/or question ("at the house itself, **or** does someone
      have to go and fetch it?") answered Yes/No, so the gate on the two fetch questions fired on a
      coin flip. Now a plain "Is the drinking water available at the house itself?". Swept the
      instrument — it was the only remaining instance
- [x] 14.6 **`remit_mode`**: bank transfer and UPI were separate options, but UPI *is* a bank transfer.
      Recoded on the axis the item exists to measure — whether the respondent had to physically go
      somewhere: own phone / in person at a branch or bank mitra / money order / sent with someone /
      carried it myself / through an agent / other
- [x] 14.7 **`govt_scheme_beneficiary` → `govt_schemes`**, a check-all of **named** schemes (PDS,
      MGNREGA, pensions, PM-KISAN, Ujjwala, PM-SYM/APY, Ayushman, housing, other, none). "Any
      government scheme" asked the respondent to recall a category and almost certainly undercounted.
      Not a count of recipients: the schemes sit at different levels — household, person, job card,
      landholding — so a count across them is not a coherent quantity
- [x] 14.8 **`other_activity_types` no longer offers the main occupation.** It shares the 14-option
      occupation list with `occupation`, so a pony owner was offered "Pony/mule owner" again as a
      second activity. XLSForm `choice_filter` on a new `code` column; mirrored in the web form, where
      the exclusion is applied at render time so it re-filters if the enumerator goes Back
- [x] 14.9 **`meal_spend_day_self` and `cooks_own_meals_here` dropped.** The spend item never entered
      any consumption aggregate — assert-only — and duplicated `cons_food_out_yatra_pm`, which does
      feed it; adding it in would have double-counted. The cooks item existed only to gate it. This was
      the cause of the asymmetry a reviewer spotted, that buying meals led to a follow-up and cooking
      them did not
- [x] 14.10 **`employer_type` dropped; `emptype` gains "unpaid family worker".** Apablaza's Q8 asked
      employment status a second time, minutes after Module B, and is the worse instrument here: its
      codes cross status with institutional sector, so a porter paid by a thekedar or a shop worker
      paid by the shop owner — employed by an individual, which is most of this sample — had no true
      option but "employee of a private company". Only the Module B answer ever reached the analysis
- [x] 14.11 **Activity codes 4 and 5 stop encoding location.** They were "wage labour, staying at
      home" and "went away from home for work" — one activity split across two codes on a location
      criterion, which no labour-force classification does and which destroyed the activity
      information. Now "casual or daily wage labour" and "construction work", the commonest off-season
      destination occupation, which previously had nowhere to go. Checked against the held sources:
      Apablaza's Q5 carries no location at all, STEP's `emp_status` is plain ICSE, and Lindenberg's
      (2002) CARE seasonal calendar keeps migration timing and activity as separate rows
- [x] 14.12 **The calendar opens at the season, not January.** It used to show January first and then
      instruct "fill the Yatra months first" — an instruction the form cannot obey, one question per
      screen in dictionary order. `CAL_ORDER` is presentation only: `status_m1` is still January and no
      month arithmetic changed
- [x] 14.13 **Enumerator hints** (`dictionary.HINTS`) reach the tablet as XLSForm `hint::` columns, the
      web form, both scripts and the paper form. First one: seasonal vs occasional on `job_permanence`,
      where the error runs one way — every job here is seasonal because the Yatra closes — and where
      `emp_dep_stab` counts code 3 as unstable and code 2 as not
- [x] 14.14 **Two bugs caught by the checks during this batch, both the same class.** (a)
      `06_form_fill_check.py` rule-ordering found the three spell items placed in Module C while their
      gates sit in Module D — a gate answered *after* the question it controls can never open, so all
      three were unreachable; moved to D. (b) `09_asserts_vs_form.py` found five asserts requiring text
      in an optional verbatim field whenever its gate was open, which the form does not enforce; all
      made one-directional (the field cannot hold text when the gate is shut)
- [x] 14.15 Verified: 0 Stata errors across the build and both analyses, `05` clean, `06` clean on all
      eight analysis groups (79 of 210 asked items gated), 7/7 navigation, 50/50 forms filled and
      exported, 18/18 skip-logic asserts hold on form-produced data, pyxform validates with the
      choice_filter itemset and hint nodes compiled. 352 dictionary rows / 210 asked, down from 220
