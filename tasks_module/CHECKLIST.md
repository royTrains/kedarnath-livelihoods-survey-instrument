# Tasks module - working checklist

Purpose: build the task-based questions for the survey, then test on a made-up dataset
that the answers can be analysed (the same idea as the earlier FGLS pipeline).

Ground rules (from the project owner)
- No rating-style questions (no numeric scales, no Likert). Ask what people DO, not how good they are.
- Every question is tied to a source in the literature folder. Anything new is marked "NEW - needs field check".
- Go general first (whole task space), then specific (ropeway jobs).
- Every result set gets a plain-language PDF.
- All work stays inside `tasks_module/`. Nothing in `replication/` is changed.
- Everything serves the survey instrument.

Folder map
- `01_questions/`  the question list (`task_items.csv`)
- `02_data/`       made-up data and the code that makes it
- `03_analysis/`   analysis code and output tables
- `04_writeups/`   LaTeX sources and the PDFs

## Stage 0 - Setup
- [x] 0.1 Folder and checklist created
- [x] 0.2 Tools checked (Python, pandas, scipy, matplotlib, LaTeX all present)

## Stage 1 - Generate the task questions
- [x] 1.1 Design rules written down (oral, no ratings, three-answer task grid) - see W1 sections 2-3
- [x] 1.2 27-task list built with 3 broad groups (4/16/7) and 5 finer groups (13/3/3/1/7)
- [x] 1.3 Eight job-condition items built (no scales; the STEP 1-10 physical scale was replaced by a count and a yes/no)
- [x] 1.4 Sixteen skills-and-credentials items built
- [x] 1.5 Source claims checked against the files: Gathmann-Schonberg task table, Spitz-Oener table, Autor-Levy-Murnane Table I (truck driving, janitorial), Autor-Handel item list, STEP variable labels, Sengupta table, Pal figure, NCO entries. Still open: exact STEP wording and lifting weight (labels are truncated)
- [x] 1.6 Saved as `01_questions/task_items.csv` (52 items: 28 direct, 21 adapted, 3 new)
- [x] 1.7 PDF W1 built: `04_writeups/W1_task_questions.pdf`

## Stage 2 - Made-up test data
- [x] 2.1 "Who does which task" profile for each of the 13 jobs, from NCO text (`02_data/occupation_profiles.csv`; palki/dandi = judgement, no NCO code)
- [x] 2.2 Answers generated for the 200-person quota pool (`tasks_synth_full`), seed 20260921
- [x] 2.3 Same drop-out as the existing sample: 104 remain (`tasks_synth_fielded`)
- [x] 2.4 Consistency checks: 11 of 11 pass (valid codes, main task is regular, skip rules)
- [x] 2.5 PDF W2 built: `04_writeups/W2_test_data.pdf`

## Stage 3 - General analysis (whole task space)
- [x] 3.1 Tasks per worker: regular 7.4 (range 2-16), done before 1.9; 79% report at least one (`outputs/3_1_*`)
- [x] 3.2 Job-by-task table and heatmap (`3_2_*`)
- [x] 3.3 Three broad groups and five finer groups by job (`3_3_*`); only 1 task in "judging varied", too thin alone
- [x] 3.4 Job-to-job overlap (cosine), nearest jobs, clusters (`3_4_*`). Cut 0.5 fixed in advance gave 2 groups (not useful); cut 0.3 added AFTER seeing this, flagged exploratory
- [x] 3.5 Inside-job differences: job title explains 38% (adj. 30%), permutation p < 0.001; own job is closest for 62.5% (`3_5_*`)
- [x] 3.6 Hidden experience: 72% of "done before" tasks are new to the job; nearest other job changes for 27% (`3_6_*`)
- [x] 3.7 PDF W3 built: `04_writeups/W3_general_results.pdf`
- Flags: Guide (n=3) and Other (n=4) too small to analyse alone; all patterns come from the generator assumptions

## Stage 4 - Specific analysis (ropeway jobs)
- [x] 4.1 13 provisional destination jobs (families: ropeway 5, hospitality 3, transport, station shop, guiding, other 2 = security, construction), task lists from NCO-2015 text (`outputs/4_1_destination_jobs.csv`). Changed from the planned 10: NCO gives only 1-3 tasks per job
- [x] 4.2 Shortage and unused-task measures for every worker x job; cosine and Jaccard as checks (`specific_analysis.py`)
- [x] 4.3 Type of move (Neffke-style). Result degenerate (short job lists) -> shortage only recommended; flagged in W4 section 6
- [x] 4.4 Entry gates: driver (car licence), electrician/mechanic (ITI), guard (NSQF-4 certificate), guide (permit, assumed). Checked in NCO: wireman NSQF 3, unarmed guard NSQF 4; ropeway operator has no stated level
- [x] 4.5 Who could take which job (`4_5_*`); gates matter more than tasks for licensed jobs
- [x] 4.6 Displacement count: numbers-only vs skills (best matching, lottery), 9 placeholder supply scenarios (`4_6_*`)
- [x] 4.7 Sensitivity (view, cut, gates, exposure definition, optional tasks) and bootstrap range (`4_7_*`)
- [x] 4.8 PDF W4 built: `04_writeups/W4_ropeway_results.pdf`
- Base case (26 exposed by title, 50 new jobs per 100 exposed, equal mix): numbers-only 50 per 100 without work; skills 69 (best) / 71 (lottery); 15 per 100 could take no job even with unlimited jobs. All from made-up data and placeholder supply.
- Flags: exposure by title (26) vs main task (23) vs any carrying (66) differ a lot -> module D must ask exposure directly; cut 0 / 1/2 change the answer a lot -> report all three

## Stage 5 - Wrap up
- [x] 5.1 What the test showed about the questions (keep / change / add): see W5 section 2
- [x] 5.2 What real data and outside inputs are still needed: see W5 section 3
- [x] 5.3 Final checklist review done; PDF W5 built: `04_writeups/W5_wrapup.pdf`
