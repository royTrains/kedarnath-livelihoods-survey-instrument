# final_instrument (worked example, SYNTHETIC)

Final questionnaire and variable list for the Kedarnath Yatra-worker survey, plus a worked-example Stata dataset.
Focus: vulnerability to poverty (VEP, MPI). Short employment-quality block (Apablaza et al. 2026 core) and a short tasks block.

Run order
1. `python do/01_generate_raw.py`          raw answers as numeric codes (`data/raw_asked.csv`); keeps all earlier synthetic draws
2. `python do/make_labels_do.py`           writes `do/labels.do` from the dictionary
3. Stata 17: `do do/02_build_final_dataset.do`   constructs derived variables, runs skip-rule checks, applies labels, saves the .dta files
4. `python checks/05_checks.py`            independent checks vs the earlier pipeline (`checks/check_report.txt`)
5. `python questionnaire/build_questionnaire.py`  questionnaire PDF and `variable_dictionary.csv`

Single source of truth: `questionnaire/dictionary.py` (edit there, then re-run 2, 3, 4, 5, and 6 below if fielding on Kobo).
Outputs: `data/kedarnath_final_n200_full.dta` (200), `data/kedarnath_final_n200_fielded.dta` (retained==1, 104).
Everything is synthetic: it tests the instrument and pipeline, not real workers.

## 6. Fielding on KoboToolbox

`python questionnaire/build_xlsform.py` builds `questionnaire/Kedarnath_final_kobo.xlsx`, an
XLSForm generated from the same `dictionary.py` (159 asked items + 4 real Module-P paradata
questions -> 166 form rows across 12 module groups, 35 choice lists). Validated clean with
pyxform (`xls2xform --skip_validate`, zero errors) -- the same converter KoboToolbox runs
internally.

**To deploy:** on kf.kobotoolbox.org (or your own Kobo server), New project -> Upload XLSForm ->
select `Kedarnath_final_kobo.xlsx` -> Deploy. No manual edits needed first. Give each of the 4
enumerators their own Kobo login (needed for the enumerator-identity point below).

**Design notes (Kobo-native substitutions, not a literal 1:1 with dictionary.py's paradata rows):**
- `resp_id` is dropped -- Kobo's own submission id (`_uuid`/`_id`) serves this on export.
- `enum_id` is dropped -- with separate logins per enumerator, Kobo's own `username`/
  `_submitted_by` column on every export identifies who did the interview automatically; no
  "pick your name" question, and no risk of picking the wrong one.
- `interview_date` / `interview_duration_min` are dropped in favour of standard `start`/`end`
  meta questions (Kobo auto-timestamps these); compute duration as `end - start` when the
  exported CSV is read into Stata, before running `02_build_final_dataset.do`.
- `dur_tasks_min` (time on the tasks block) is left out -- timing a sub-block needs extra
  mid-form fields for limited value; not fielded.
- `gps_lat`/`gps_lon` become one `background-geopoint` field (`gps_location`): captured silently
  the moment `consent` is answered (`odk:setgeopoint` fires on that field's value-changed event),
  with no on-screen question and no enumerator interaction. Kobo splits it into separate
  latitude/longitude/altitude/accuracy columns on export.
- `location_cluster`'s choice labels are deliberately generic ("Cluster 1".."Cluster 4"), not the
  actual site names -- enumerators pick from a printed crosswalk card kept by the research team,
  never from a place name shown on the tablet or stored in the exported data. Every place-name
  reference was removed from `dictionary.py`'s `cluster` value-label set and the
  `health_access_tier` construction note; the numeric codes (and the Stata logic that reads them)
  are unchanged.
- Skip logic (41 of 159 asked items) is implemented as XLSForm `relevant` expressions, hand-built
  from the variable coding -- dictionary.py's `skip` field is free English text, not parsed
  automatically. One hidden `calculate` field (`calc_months_no_work`) exists only to support the
  `looked_for_work_idle` skip rule, which depends on a count Stata normally builds after the fact.
- Consent gates the entire rest of the form: everything after Module P sits inside a group with
  `relevant = ${consent} = 1`, the standard XLSForm pattern for "stop if the answer is no."
- After export, Kobo's CSV/XLSX download uses the same variable names as `dictionary.py`, so
  `01_generate_raw.py`'s column-matching logic needs the real export in place of the synthetic
  `raw_asked.csv` before running the rest of the pipeline on real data -- not yet wired up, since
  no real data exists yet.
