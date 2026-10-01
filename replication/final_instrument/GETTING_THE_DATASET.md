# Getting the full dataset, after the office coding is done

What to run, in order, to turn collected interviews into the analysis file. Allow an afternoon for
the coding, ten minutes for the rest.

---

## 0 · What you are starting from

One CSV of raw answers, as numeric codes. Either:

- **the web form** — open it, Menu, *"Export all — codes (CSV)"*. Not the "answers in words" file; that
  one is for reading, and Stata cannot use it.
- **KoboToolbox** — Download, XLS or CSV, **Value and header format: XML values and headers**. Not
  "Labels". The pipeline reads codes.

Put it at `replication/final_instrument/data/raw_asked.csv`. That exact path and name: every script
downstream expects it.

**Check the build stamp first.** Every row carries `form_build`, like `2026-10-01.1537a6`. If rows
disagree, some tablets were running an older form — sort that out before analysing, because the older
build may be missing questions or carrying ones since dropped. The web form and the Kobo form stamp
the same value for the same question set, so a disagreement always means a stale tablet and never a
difference between the two ways of collecting.

**A blank `knows_monthly_income` is an answer, not a gap.** The earnings calendar is deliberately
not compulsory: it is a control in the vulnerability models, not the dependent variable, and a
required earnings question ends interviews. A blank means the respondent declined earnings
altogether. The build sets `income_declined = 1` and leaves every income variable MISSING rather
than zero — a zero would read as destitution, put him under the poverty line, mark him deprived on
Apablaza's compensation domain, and drag the sample median down for everybody else. The build prints
the count as a NOTE; watch it. If it is large, the income covariates are worth less than the
regressions imply, and `checks/11_estimation_samples.py` is where that shows up.

---

## 1 · Code the five free-text fields to NCO-2015

Nothing automatic can do this. Each needs a human with the NCO volumes
(`literature/papers-structural-transformation/National_Classification_of_Occupations_*`).

| Column | What it holds |
|---|---|
| `occupation_detail` | the main work, in the respondent's own words |
| `prev_occ` | the previous main work |
| `target_occ` | what they would move to if this work ended |
| `closure_work_detail` | where they went and what they did in the closure |

Add one column per field, named `<field>_nco`, holding the **4-digit NCO-2015 code**. Leave blank
where the text is too vague to code — blank is a usable answer, a guessed code is not. Keep a tally
of how many you left blank; it belongs in the methods section.

### `govt_schemes_detail` is coded too, but not to NCO

The ten named government schemes stopped being tick-boxes on 2026-10-01. The enumerator reads the
list out as a probe and writes down what the respondent says, so the scheme NAMES arrive as free
text and are coded here instead. Add `govt_schemes_detail_coded` holding the codes the respondent
named, space-separated, from the list in the enumerator hint:

`1` ration/PDS · `2` MGNREGA · `3` old-age, widow or disability pension · `4` PM-KISAN ·
`5` Ujjwala · `6` PM-SYM or Atal Pension · `7` Ayushman Bharat · `8` housing (PMAY or state) ·
`9` anything else

One respondent can name several. `govt_any_benefit = 0` means no schemes at all and needs no coding.
This is the one coding step the analyses genuinely need: without it there is a yes/no where there
used to be eight indicators, and a ration card and a widow pension protect against different things.

Three others are free text too and need no coding at all: `native_language_other`,
`migration_referral_other`, `work_equipment_detail`. Code these only if you want them as categories;
the analyses do not require it.

---

## 2 · Build the dataset

From `replication/final_instrument/`:

```bash
python do/make_labels_do.py                                   # regenerate do/labels.do
stata -e do do/02_build_final_dataset.do                      # the build
```

On Windows, Stata is invoked by its full path:

```bash
"/c/Program Files/Stata17/StataMP-64.exe" -e do do/02_build_final_dataset.do
```

**Stata exits 0 even when the do-file failed.** Always check:

```bash
grep -c '^r([0-9]*);' checks/build_final_log.log      # 0 means clean
```

If it is not zero, read the lines just before the `r(...)`. An assert that fails is telling you the
data contradicts a rule the form was supposed to enforce — fix the data or the rule, never delete
the assert.

### What the build produces

| File | What it is |
|---|---|
| `data/kedarnath_final_n200_full.dta` | **everyone**, every derived variable, labelled |
| `data/kedarnath_final_n200_fielded.dta` | only those who consented — the analysis sample |
| `data/kedarnath_final_n200_fielded_empvtp.dta` | the employment-VEP working file |

Use the **fielded** file for analysis. The full file is for checking what was dropped and why.

---

## 3 · Read the data-quality report

The build prints a block of `DATA QUALITY:` lines and ends with a count. These are contradictions
the form permits and so cannot refuse — a hospital stay with zero hospital spending, UPI use without
a smartphone, an owner-occupation recorded as wage work, a respondent under 18.

```bash
grep "DATA QUALITY:" checks/build_final_log.log
```

Every flagged record also carries `dq_flag == 1` in the dataset, so you can look at them directly:

```stata
use "data/kedarnath_final_n200_full.dta", clear
list resp_id enum_id site if dq_flag==1
```

**Query these with the enumerator while the fieldwork is still fresh.** That is what the flags are
for. None of them stops the build.

---

## 4 · Run the analyses

```bash
stata -e do do/03_employment_vulnerability.do     # Apablaza employment deprivation + VEP
stata -e do do/04_vtp_analysis.do                 # monetary and multidimensional VEP
```

Then confirm the regressions actually estimated on the sample, which no other check does:

```bash
python checks/11_estimation_samples.py
```

A regression running on a small fraction of the rows means a gated variable reached a covariate list
and listwise deletion ate the sample. It happened once and nothing caught it — the sample fell from
104 to 4 and Stata raised nothing.

---

## 5 · Verify before you believe any number

```bash
python checks/05_checks.py        # independent re-check of the Stata output
python checks/06_form_fill_check.py   # skip logic, rule ordering, analysis readiness
python checks/10_every_question_earns_its_place.py
```

---

## The whole thing, once the coding is done

```bash
cd replication/final_instrument
python do/make_labels_do.py
"/c/Program Files/Stata17/StataMP-64.exe" -e do do/02_build_final_dataset.do
grep -c '^r([0-9]*);' checks/build_final_log.log          # must print 0
grep "DATA QUALITY:" checks/build_final_log.log           # read these
"/c/Program Files/Stata17/StataMP-64.exe" -e do do/03_employment_vulnerability.do
"/c/Program Files/Stata17/StataMP-64.exe" -e do do/04_vtp_analysis.do
python checks/11_estimation_samples.py
python checks/05_checks.py
```

Output: `data/kedarnath_final_n200_fielded.dta`, and
`data/kedarnath_final_vtp_results.dta` carrying the vulnerability estimates.

---

## Two things that will bite

**The synthetic generator overwrites your data.** `do/01_generate_raw.py` writes
`data/raw_asked.csv` — the same path the real export goes to. **Do not run it** once you have real
data, or back the real file up first. It exists to test the pipeline, and it has no business near
fieldwork.

**`data/` is gitignored.** Nothing in it is tracked, by design — it holds real answers from
identifiable people in a small population. Keep your own backups; do not solve this by committing it.
