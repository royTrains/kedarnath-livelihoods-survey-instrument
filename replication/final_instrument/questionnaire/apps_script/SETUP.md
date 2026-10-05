# Connecting the form to a Google Sheet

Each finished interview is sent to one Google Sheet, in two tabs written from the same request:

| Tab | What is in it |
|---|---|
| `answers` | Every answer as the respondent's own words (the option text as chosen, verbatim answers as typed). This is the tab a person reads. |
| `codes` | The same rows as the numeric codes the Stata build reads. One row per interview, same `resp_id` as the `answers` tab. |
| `rejected` | Any POST the sheet refused, with the reason and the payload. Nothing is dropped silently. |
| `collisions` | Two different interviews that arrived with the same `resp_id`. The second is kept under `<id>-b`. |

Rows are matched on `resp_id`, so a tablet that retries after a dropped connection overwrites its own row rather than adding a duplicate.

## One-time setup (about 10 minutes)

1. **Create the sheet.** In Google Drive, create a new Google Sheet. Name it for the survey, for example `Kedarnath survey, live`.

2. **Add the script.** In the sheet: *Extensions → Apps Script*. Delete the placeholder code, paste the whole of `Code.gs`, and save (Ctrl+S). Name the project `kedarnath-survey-sink`.

3. **Set the script properties.** In Apps Script: *Project Settings (gear) → Script Properties → Add script property*. Add:

   | Property | Value | Required? |
   |---|---|---|
   | `ENUM_IDS` | `1,2,3,4` | Already the default in the code. Set it anyway so it is visible. |
   | `TOKEN` | any long random string | Optional. A speed bump only: the form is public (GitHub Pages), so anything in it can be read. The real checks are in `Code.gs`. |
   | `DAILY_CAP` | `200` | Optional. Default is 200 rows per Indian calendar day. |

4. **Deploy as a web app.** *Deploy → New deployment → type: Web app*.
   - Execute as: **Me**
   - Who has access: **Anyone**
   - Click *Deploy*, approve the Google permissions prompt, and copy the **Web app URL** (it ends in `/exec`).

5. **Check it works.** Open the Web app URL in a browser. It should show:

   ```json
   {"ok":true,"service":"kedarnath-survey-sink", ...}
   ```

   If it shows `"no spreadsheet"`, the script is not bound to the sheet: redo step 2 from *inside* the sheet.

6. **Give the URL to the tablets.** Either:
   - **Per tablet:** open the form → *menu → Sync settings* → paste the URL → *Sync now*. This is what you do on a tablet that is already in use.
   - **Baked into the build:** create `questionnaire/sync_config.json` containing `{"url": "<the /exec URL>", "token": "<TOKEN, or empty>"}` and run `build_webform.py`. This file is gitignored. Do not commit it.

## Before any interview is taken on a tablet

The form will not start an interview until the tablet has **both** an enumerator (1 Raman, 2 Rishit, 3 Tanmay, 4 Anuj) **and** a route (1 Kedarnath, 2 Hemkund). Both are set once on the menu screen. The sheet also refuses rows whose enumerator is not 1–4, so a tablet left on a random device ID would have every interview rejected.

## Testing before the first day

Use a test tablet, fill one full interview, and tap *Sync now*. Then check:

- `answers` has one new row, with words in the choice columns (`Own-account (self-employed, no hired workers)`, not `1`).
- `codes` has one new row with the same `resp_id`, with numbers in the choice columns.
- `rejected` is empty.

Delete the test rows before fieldwork starts. The sink does not know the difference between a test and a real interview.

## If something goes wrong

| Symptom | Likely cause |
|---|---|
| Tablet says *Sync failed* | No signal, or the URL is wrong. Check the URL on the health-check page. The interview stays on the tablet and is sent on the next sync. |
| Rows appear in `rejected` with `enum_id not on the team` | The tablet's enumerator is not set, or is set to a value outside 1–4. |
| Rows appear in `rejected` with `daily cap` | More than the daily cap came in on one day. Raise `DAILY_CAP` if the count is real. |
| Rows appear in `rejected` with `bad token` | The token in the tablet's sync settings does not match the script property. |
| `busy, retry` | Two tablets synced at the same instant. Nothing is lost; the tablet retries. |

## Redeploying after a change to `Code.gs`

*Deploy → Manage deployments → pencil icon → Version: New version → Deploy.* The URL stays the same, so tablets do not need reconfiguring. Do not create a *New deployment*, which gives a new URL.
