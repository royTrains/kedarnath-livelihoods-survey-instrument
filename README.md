# Kedarnath Yatra Worker Survey — Vulnerability to Poverty

Survey instrument and analysis pipeline for a study of vulnerability to poverty among workers on
the Kedarnath Yatra route — porters, pony and palki workers, shopkeepers, dhaba and lodge staff,
drivers and guides, most of them seasonal migrants.

**Everything in this repository is the instrument and its code. No data is tracked** — see
[What is not in git](#what-is-not-in-git).

---

## Where things are

| Folder | What it holds | In git? |
|---|---|---|
| **`replication/final_instrument/`** | **The deliverable.** Questionnaire source, every artefact built from it, the Stata build, checks and analysis. Start here. | yes |
| `replication/vasyr_example/` | Separate method demonstration: Lyons et al. (2023) MLI + Chaudhuri VEP on real UNHCR VASyR microdata. Not part of the Kedarnath instrument. | yes |
| `docs/` | The offline web form as published by GitHub Pages. A build-time copy — never edit it by hand. | yes |
| `reports/` | Write-ups (the Char Dham ropeway report). | yes |
| `tasks_module/` | The occupational-transferability side project — a separate, later paper. Synthetic data and exploratory write-ups. | yes |
| `literature/` | Papers, `.bib` files, and text extractions, in three topic folders. | **no** |
| `microdata/` | External survey datasets: VASyR, STEP, Philippines STEP, HCES documentation. | **no** |
| `pilot/` | The real 46-respondent field pilot. | **no** |

## Inside `replication/final_instrument/`

| Path | What it is |
|---|---|
| `questionnaire/dictionary.py` | **The single source of truth.** Every variable: module, wording, type, value labels, skip rule, and the source it comes from. Also `INTROS`, the read-aloud introduction the enumerator gives before each module. Read this before changing anything. |
| `questionnaire/translations_hi.py` | Hindi for every question and every choice, at roughly a class-5 reading level. |
| `questionnaire/build_*.py` | Six builders, all reading `dictionary.py`, so the outputs cannot drift apart. |
| `do/01_generate_raw.py` | Synthetic raw answers, as numeric codes — a worked example, not data. |
| `do/make_labels_do.py` → `do/labels.do` | Stata labels. Generated; do not hand-edit. |
| `do/02_build_final_dataset.do` | Builds every derived variable, asserts the skip logic, applies labels. |
| `do/03_employment_vulnerability.do` | Employment-deprivation VEP (Apablaza × Chaudhuri). |
| `do/04_vtp_analysis.do` | Monetary and multidimensional VEP. |
| `checks/05_checks.py` | Independent Python re-check of the Stata output. |
| `checks/06_form_fill_check.py` | Fills the form 100 times, tests the skip logic against the XLSForm, and checks each analysis has what it needs. |
| `checks/07_navigation_test.js` / `08_fill_and_export_test.js` | Drive the web form's own navigation and export code: gate/back behaviour, then 50 full interviews to CSV. |
| `checks/09_asserts_vs_form.py` | Runs the Stata build's cross-variable asserts against that 50-form CSV. The synthetic generator makes consistent records, so only this catches an assert the form can actually violate — which halts the build on real field data. |

### The six outputs, all from one dictionary

| File | Use |
|---|---|
| `Kedarnath_final_kobo.xlsx` | XLSForm — upload to KoboToolbox as-is |
| `index.html` | Offline web form, self-contained, no server |
| `Kedarnath_final_questionnaire.pdf` | Paper questionnaire |
| `Interview_script_EN.md` / `Interview_script_HI.md` | Enumerator scripts, read-aloud |
| `Question_register.xlsx` / `.pdf` | Every question with the literature it comes from |

## Rebuilding after any edit to `dictionary.py`

Run in order, from `replication/final_instrument/`:

```
python do/01_generate_raw.py
python do/make_labels_do.py
stata -e do do/02_build_final_dataset.do
python checks/05_checks.py
python checks/06_form_fill_check.py
python questionnaire/build_xlsform.py
python questionnaire/build_webform.py
python questionnaire/build_questionnaire.py
python questionnaire/build_scripts.py
python questionnaire/build_question_register.py

# then drive the built web form itself, and test the build's asserts against what it produces
node   checks/07_navigation_test.js questionnaire/index.html
node   checks/08_fill_and_export_test.js questionnaire/index.html /tmp/form_export.csv
python checks/09_asserts_vs_form.py /tmp/form_export.csv
```

Three traps worth knowing. `build_xlsform.py` keeps its skip rules in a **hand-built `RELEVANT` dict** —
it does not parse `dictionary.py`'s `skip` text, so a skip-logic change must be made in both places
(`06_form_fill_check.py` will catch it if you forget). `build_question_register.py` needs
**XeLaTeX**, not pdflatex, because it prints Hindi. And **never add a cross-variable `assert` to
`02_build_final_dataset.do` without a matching form constraint** — the synthetic generator makes
internally consistent records, so such an assert passes every other check here and then halts the
build on the first real export. `09_asserts_vs_form.py` is what catches it; if the form cannot
enforce the rule, make it a data-quality flag instead.

## What is not in git

`.gitignore` excludes four things, for reasons written into the file:

- **`microdata/`** — VASyR, STEP and HCES are redistributable only under their own licences, which a
  GitHub repo does not satisfy.
- **`pilot/`** — real field data about identifiable people in a small population. A private repo is
  not a safeguard.
- **`literature/`** — copyrighted papers and their text extractions.
- **generated datasets** (`*.dta`, `*.csv`, `*.log`) — the pipeline rebuilds all of them from source.

## Status

The instrument is complete and every indicator has been checked against its source: the MPI against
NITI Aayog's National MPI, the employment dimension against Apablaza et al. Table 3, consumption
against HCES, the poverty line against Sethu et al. (2024), and the coping index against the VASyR
item text. `Question_register.xlsx` records which source each question comes from.

Nothing here has been fielded yet. Every number the pipeline produces is synthetic — a test of the
instrument, not a finding about Kedarnath workers.
