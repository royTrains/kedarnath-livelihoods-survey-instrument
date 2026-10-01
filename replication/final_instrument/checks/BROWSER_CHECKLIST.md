# Live browser checklist — Edge, real instance, over the DevTools Protocol

**Run 2026-10-01 · Microsoft Edge 153.0.4234.48 · 13 passed, 0 failed.**

Checks 07 and 08 drive the form's functions against a stubbed DOM. This one loads the built page in
an actual browser, so it exercises what those cannot: real rendering, real event listeners, real
clicks, real computed CSS, and whatever the console says while it happens.

## How to run it

```bash
# 1. launch Edge listening on 9222, with the form open
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/edge_cdp_profile --no-first-run --no-default-browser-check \
  "file:///D:/OneDrive/Desktop/vulnerability-2-poverty/replication/final_instrument/questionnaire/index.html" &

# 2. drive it
node checks/12_edge_live_test.js
```

No dependencies: Node 24 has a built-in `WebSocket`, so the harness speaks the DevTools Protocol
directly. Edge needs its own scratch `--user-data-dir` or it attaches to the user's running profile
and ignores the debugging port.

## Results

| # | Check | Result | Observed |
|---|---|---|---|
| 1 | Edge loads the page and the form boots | **pass** | 214 questions, 13 modules |
| 2 | Consent script renders as a verbatim read-aloud block | **pass** | 86 words, labelled "यह ज्यों का त्यों पढ़कर सुनाएँ" |
| 3 | Module P refuses to advance while consent is unanswered | **pass** | 3 blocking questions reported |
| 4 | **The shock list offers a no-shock option and accepts it** | **pass** | required=true, option "Nothing of this kind happened" |
| 5 | **Ticking it alongside a real shock is refused, with a message** | **pass** | constraint message shown |
| 6 | **A real click on a primary occupation removes it from the other-activities list, same screen** | **pass** | list 14 → 13; chosen code absent |
| 7 | An other-activity answer equal to the occupation is dropped | **pass** | stale code pruned, the other kept |
| 8 | A module intro renders as a styled read-aloud block | **pass** | 57 words, 4px left rule |
| 9 | The enumerator hint renders on `job_permanence`, marked do-not-read | **pass** | "सर्वेक्षक के लिए — पढ़कर न सुनाएँ", 82 words |
| 10 | A gate reshapes its module in place without losing a typed value | **pass** | 29 vs 19 questions; typed 4321 captured via a real `input` event |
| 11 | A full interview completes in the browser | **pass** | 1 record stored |
| 12 | Both exports fire, coded and labelled | **pass** | `kedarnath_<date>_1.csv` and `..._labels_hi.csv` |
| 13 | No uncaught JavaScript errors during the whole run | **pass** | console clean |

Rows 4–7 in bold are the two defects reported from live use, and their regressions.

## Notes from the run

- **Row 6 is the one that needed a browser.** It clicks a real radio, which fires the real listener,
  which calls `applyGates` → `refilter`, which rebuilds the dependent card's option list in the live
  DOM. The headless harness can call those functions but cannot prove the rendered list changed.
- **Row 10 dispatches a genuine `input` event** rather than assigning to `D`, so it tests that the
  binding survives a list being rebuilt — the thing `bindCard` exists for.
- One failure on the first run was **the test's own regex**, not the form: the hint label reads
  "पढ़कर न सुनाएँ", where the negation follows the verb, and the pattern looked for "न पढ़". The hint
  itself rendered correctly throughout. Corrected and re-run.
- Edge opens a sync-confirmation dialog on a fresh profile. It is a separate target and does not
  block the page, so the harness ignores it.
