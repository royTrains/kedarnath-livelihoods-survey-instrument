# Transfer packet — Kedarnath survey instrument

*For a session picking this up cold to make changes. Current as of 2026-10-01.
Longer background is in `replication/final_instrument/HANDOFF.md`; this file is the operating manual.*

---

## The one thing to understand first

**`replication/final_instrument/questionnaire/dictionary.py` is the single source of truth.** Every
artefact — the web form, the Kobo XLSForm, the paper questionnaire, both interview scripts, the
question register, the Stata labels — is generated from it. Never hand-edit a generated file; the next
rebuild overwrites it.

Current state: **354 rows — 211 asked, 9 paradata, 129 constructed. 45 label sets, 13 modules (P, A–L).**

---

## Where things are

```
replication/final_instrument/
├── questionnaire/
│   ├── dictionary.py              ← EDIT THIS
│   ├── translations_hi.py         ← and its Hindi twin (every question + every choice)
│   ├── build_xlsform.py           → Kedarnath_final_kobo.xlsx   (upload to Kobo)
│   ├── build_webform.py           → index.html + sw.js + manifest.json + icons
│   ├── build_questionnaire.py     → Kedarnath_final_questionnaire.pdf
│   ├── build_scripts.py           → Interview_script_EN.md / _HI.md
│   ├── build_question_register.py → Question_register.xlsx / .pdf
│   └── index.html                 ← THE WEB FORM (built; do not edit by hand)
├── do/
│   ├── 01_generate_raw.py         synthetic raw answers
│   ├── make_labels_do.py          → do/labels.do
│   ├── 02_build_final_dataset.do  all derived variables, asserts, labels
│   ├── 03_employment_vulnerability.do
│   └── 04_vtp_analysis.do
├── checks/                        05–11, see below
└── data/                          gitignored; generated datasets land here

docs/index.html                    ← LIVE COPY, served by GitHub Pages. Written by
                                     build_webform.py automatically. Never edit directly.
```

**The form lives in two places and the builder writes both.** `questionnaire/index.html` is the source
artefact; `docs/index.html` is what the public URL serves. Running `build_webform.py` updates both, so
they should always be byte-identical. Check it:

```bash
for f in index.html sw.js manifest.json; do
  diff -q "docs/$f" "replication/final_instrument/questionnaire/$f" && echo "OK $f"
done
```

If they differ, you edited a built file or forgot to rebuild.

---

## Rebuild after ANY edit to dictionary.py

From `replication/final_instrument/`:

```bash
python questionnaire/build_xlsform.py          # do this first — the webform imports from it
python questionnaire/build_webform.py
python questionnaire/build_questionnaire.py
python questionnaire/build_scripts.py
python questionnaire/build_question_register.py
python questionnaire/build_question_map.py       # QUESTION_MAP.txt -- the flow map
python do/01_generate_raw.py
python do/make_labels_do.py
"/c/Program Files/Stata17/StataMP-64.exe" -e do do/02_build_final_dataset.do
"/c/Program Files/Stata17/StataMP-64.exe" -e do do/03_employment_vulnerability.do
"/c/Program Files/Stata17/StataMP-64.exe" -e do do/04_vtp_analysis.do
```

Stata writes its log beside the do-file. **Stata exits 0 even when the do-file failed**, so always
check for errors explicitly:

```bash
grep -c '^r([0-9]*);' checks/build_final_log.log      # 02 writes here
grep -c '^r([0-9]*);' 03_employment_vulnerability.log
grep -c '^r([0-9]*);' do/04_vtp_analysis.log
```

Zero means clean. Anything else, read the lines before the `r(...)`.

---

## The check suite

```bash
python checks/05_checks.py                             # independent re-check of the Stata output
python checks/06_form_fill_check.py                    # 100 fills; skip logic vs the XLSForm; rule ordering
node   checks/07_navigation_test.js questionnaire/index.html
node   checks/08_fill_and_export_test.js questionnaire/index.html data/form_export_50.csv
python checks/09_asserts_vs_form.py data/form_export_50.csv
python checks/10_every_question_earns_its_place.py
python checks/11_estimation_samples.py                 # run AFTER 04
```

What each one exists to catch — these were all written after the corresponding bug bit:

| Check | Catches |
|---|---|
| 06 | A gate that doesn't match the XLSForm, and **a question whose gate is answered later than itself** (it can then never appear) |
| 07 | Module navigation, gates reshaping a module in place, gated-off required questions blocking the screen |
| 08 | 50 full interviews through the form's own code; also proves the labelled export is a pure relabelling |
| 09 | **An assert in Stata that the form can violate.** The synthetic generator makes consistent records, so only this catches a rule the form doesn't enforce |
| 10 | A question that is asked and then reaches no analysis |
| 11 | **A regression estimating on what survived listwise deletion.** The FGLS sample silently fell from 104 to 4 once |

---

## Hard rules, each learned from a real failure

1. **A skip change must be made in TWO places.** `build_xlsform.py` keeps its own hand-built `RELEVANT`
   dict and does *not* parse `dictionary.py`'s prose `skip` field. Change both. `06` catches it if you forget.
2. **Never add a cross-variable `assert` to `02_build_final_dataset.do` without a matching form
   constraint.** If the form permits it, the assert halts the build on real data. Make it a
   data-quality flag instead. `09` is the check for this.
3. **Never put a skip-gated variable into a regression raw.** Each is missing where its gate excluded
   the respondent, the deletions intersect, and the sample collapses. Use the regression-safe forms
   (`*_r`) built in `02`. `11` is the check.
4. **Optional verbatim fields get one-directional asserts only.** "Gate open implies text present" is
   not enforceable — the enumerator may decline. Only "gate shut implies blank" is.
5. **`build_question_register.py` needs XeLaTeX, not pdflatex** (it prints Devanagari). `extarticle`
   hangs MiKTeX; use `article`.
6. **Hindi is mandatory, not optional.** `build_xlsform.py` fails loudly if any question or choice
   lacks a translation. Add to `translations_hi.py` in the same edit.
7. **Writing Python patches that emit JS?** Escaping bites. A `\n` inside the JS template needs `\\n`
   in the Python source, and a regex backreference written as `\1` through a non-raw string becomes a
   control character — that silently broke a `selected()` gate so a question was never asked.

---

## Pushing

```bash
git status --porcelain
# confirm nothing from microdata/ pilot/ literature/ or *.dta is staged:
git status --porcelain | grep -Ei "microdata/|pilot/|literature/|\.dta$"   # expect no output
git add -A
git commit -m "..."
git push origin main
```

Remote: `https://github.com/royTrains/kedarnath-livelihoods-survey-instrument.git`, branch `main`.

**Pushing `docs/` redeploys the live form.** That is outward-facing, so rebuild and run the checks
before pushing, and confirm `docs/` is in sync. GitHub Pages takes a minute or two. `sw.js` carries a
hash of the page in its cache name, so tablets holding the old form refetch rather than serve stale.

`.gitignore` excludes `microdata/`, `pilot/`, `literature/`, and generated datasets (`*.dta`, `*.csv`,
`*.log`, `replication/final_instrument/data/`). Those are real field data, licensed microdata and
copyrighted papers — **verify zero leaks before every push.**

---

## Environment

- Windows, Git Bash available; `python` on PATH (not `python3`)
- **Set `PYTHONIOENCODING=utf-8` before any Python that prints Hindi**, or it dies on cp1252
- Stata: `/c/Program Files/Stata17/StataMP-64.exe`, invoked `-e do <file>`
- Node for checks 07/08; `pyxform` for XLSForm validation:
  ```python
  from pyxform.xls2xform import convert
  r = convert('questionnaire/Kedarnath_final_kobo.xlsx')
  ```

---

## Form behaviour worth knowing before you change it

- **One module per screen**, not one question. `appearance=field-list` on each group in the XLSForm;
  the web form renders all of a module's questions and toggles gated ones with a CSS class rather than
  re-rendering (re-rendering loses focus and the caret mid-number).
- **Answers whose gate closes are deleted**, on every change and again at submission — matching Kobo.
  Without it a stale answer reaches the export for a fact the respondent never asserted.
- **Two export buttons.** Codes (feeds Stata) and answers-in-words. Only the coded export marks records
  `__exported`; `clearExported()` deletes on that flag.
- **Three read-aloud registers, deliberately distinct:** blue = module intro (read it), amber = enumerator
  hint (do *not* read it), green = consent script (read it verbatim).
- Navigation is keyed on module **codes** and question **names**, never indices into a list that gates
  can reshape. That bug ate the enumerator's place once.

---

## Open items

**Instrument content — must be decided before fielding, cannot be added after:**
- Module J is 2 questions in a study named for the ropeway; the pilot had 9
- No retrospective shock block for the 2013 floods and COVID (`distress_event_last365d` covers 12 months only).
  This one blocks analysis gap A1 and A11
- Savings was assessed and **dropped deliberately** — not required by any of the four methods; see the
  reasoning in the conversation record

**Analysis code — can be written any time before data lands:**
expected FGT₁/FGT₂, Calvo–Dercon aggregate, expected Watts, Calvo 2008 multidimensional, scenario
simulation (blocked on the shock block), explicit time horizon, welfarist-arm exclusion note, the
ropeway destination task vector, `dist_to_ropeway` from stored GPS.

**Also outstanding:** the closing script exists only in the printed interview script, not on the
tablet — same shape as the consent-script bug that was fixed, but nothing depends on it.

---

## Current verified state

0 Stata errors across all three do-files · checks 05, 06, 09, 10, 11 clean · 10/10 navigation ·
50/50 forms filled and exported · pyxform validates with 12 field-list groups, the choice-filter
itemsets and the hint nodes · `docs/` in sync with the source.
