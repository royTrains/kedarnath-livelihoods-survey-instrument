"""W2 - plain-language write-up of the test dataset. All numbers are read from the data files."""
import csv, json, os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from latex_helpers import esc, header, compile_tex

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "02_data")
full = pd.read_csv(os.path.join(D, "tasks_synth_full.csv"))
fld = pd.read_csv(os.path.join(D, "tasks_synth_fielded.csv"))
prof = pd.read_csv(os.path.join(D, "occupation_profiles.csv"))
log = json.load(open(os.path.join(D, "generation_log.json")))
items = list(csv.DictReader(open(os.path.join(HERE, "..", "01_questions", "task_items.csv"), encoding="utf-8-sig")))
LAB = {int(i["variable"].split("_")[1]): i["label"] for i in items if i["variable"].startswith("t1_") and i["variable"] != "t1_28"}

def table(spec, head, rows, size="\\small"):
    s = "{" + size + "\n\\begin{longtable}{" + spec + "}\n\\toprule\n" + head + " \\\\\n\\midrule\n\\endfirsthead\n"
    s += "\\toprule\n" + head + " \\\\\n\\midrule\n\\endhead\n"
    for r in rows: s += " & ".join(r) + " \\\\\n"
    return s + "\\bottomrule\n\\end{longtable}\n}\n"

nf, nn = len(full), len(fld)
tex = header("Tasks Module, Part 2: A Test Dataset", "How the made-up answers were built, and what they can and cannot tell us")

tex += r"""
\section*{1. Why we made a test dataset}
We have not run the survey yet. Before we do, we want to know that the answers to the task questions
can be turned into useful results. So we made up answers for """ + str(nf) + r""" imaginary workers and ran the
analysis on them. This is the same idea as the earlier test data for the poverty work.

\plainbox{\textbf{Important.} Every pattern in this data comes from a rule we wrote down. Nothing in it is a finding
about real workers. It tests the \emph{questions and the method}, not the world.}

\section*{2. What we started from}
We reused the imaginary workers already made for the poverty work: """ + str(nf) + r""" people, filled by fixed quotas for each job.
After the same drop-out as before, """ + str(nn) + r""" remain (the ones that would be ``interviewed''). We kept their
job, off-season work, age, schooling, place of origin, phone and training. The task answers were then made to fit those facts.
"""

j = full.groupby("occupation").size().rename("full").to_frame().join(fld.groupby("occupation").size().rename("fld")).fillna(0).astype(int)
j = j.sort_values("full", ascending=False)
rows = [[esc(k), str(r.full), str(r.fld)] for k, r in j.iterrows()]
rows.append(["\\textbf{All}", "\\textbf{" + str(j.full.sum()) + "}", "\\textbf{" + str(j.fld.sum()) + "}"])
tex += "\n" + table("lrr", "\\textbf{Job} & \\textbf{Full pool} & \\textbf{After drop-out}", rows)

lv = log["level_p"]
tex += r"""
\section*{3. How the answers were made}
\textbf{Step 1. Who does which task, by job.} For each of the 13 jobs we sorted the 27 tasks into four levels:
\emph{core} tasks (a worker does it regularly with chance """ + f"{lv['core']*100:.0f}" + r""" in 100), \emph{common} tasks (""" + f"{lv['common']*100:.0f}" + r""" in 100),
\emph{occasional} tasks (""" + f"{lv['occasional']*100:.0f}" + r""" in 100) and \emph{rare} tasks (""" + f"{lv['rare']*100:.0f}" + r""" in 100).
The core tasks come from the wording of the job in India's National Classification of Occupations (NCO 2015).
Where NCO has no entry (palki and dandi bearers) they are our judgement, and the last column of the table in section 4 says so.

\textbf{Step 2. People differ.} Some people simply do more of everything. More years in the work adds a little.
More schooling adds a little to tasks that use records and judgement.

\textbf{Step 3. Work done before elsewhere (answer 2).} The chance starts low (6 in 100).
It rises with off-season work: farming raises animal care and carrying; wage labour raises building and loading;
petty trade raises selling and cash. A past job in a different trade brings in that trade's tasks. Older workers have a little more.

\textbf{Step 4. Main task.} It is the job's usual main task, if the person does it regularly.
Otherwise it is the person's most typical regular task.

\textbf{Step 5. Job conditions and skills.} Made from the person's job, schooling, place of origin, phone and training.
For example, someone who supervises others regularly must report at least one person directed.

\section*{4. The core tasks we gave each job}
"""
rows = []
for _, r in prof.iterrows():
    core = [] if pd.isna(r["core"]) or str(r["core"]).strip() == "" else [int(x) for x in str(r["core"]).split(",")]
    ctext = "; ".join(f"{t} {esc(LAB[t].lower())}" for t in core) if core else "none (mixed group)"
    rows.append([esc(r["occupation"]), ctext, esc(r["evidence"])])
tex += table("p{2.7cm}p{5.6cm}p{6.5cm}", "\\textbf{Job} & \\textbf{Core tasks} & \\textbf{Where it comes from}", rows, size="\\footnotesize")

nok = sum(1 for _, ok in log["checks"] if ok)
tex += r"""
\section*{5. Checks on the made-up data}
We ran """ + str(len(log["checks"])) + r""" checks. All """ + str(nok) + r""" passed. The checks catch answers that could not happen in real life.
\begin{itemize}[leftmargin=1.2em,itemsep=1pt]
"""
for name, ok in log["checks"]:
    tex += "\\item " + esc(name[0].upper() + name[1:]) + ".\n"
tex += r"""\end{itemize}
The same checks can be run on the real survey data as a first quality test.

\section*{6. What the test data can and cannot show}
\textbf{It can show} whether the answers fit together, whether the analysis code runs, and what kind of result each method gives.
\textbf{It cannot show} what Kedarnath workers really do. Every job profile is our assumption, and the sample is small
(""" + str(nn) + r""" people). Two results that look different in this data may not differ in real life.
When real answers arrive, the code is run again on them without change.

\section*{7. Files}
\begin{itemize}[leftmargin=1.2em,itemsep=1pt]
\item \texttt{02\_data/generate\_task\_data.py}: the code that makes the data.
\item \texttt{02\_data/tasks\_synth\_full.csv} and \texttt{tasks\_synth\_fielded.csv} (also \texttt{.dta} for Stata).
\item \texttt{02\_data/occupation\_profiles.csv}: the levels given to each job.
\end{itemize}
\end{document}
"""
out = os.path.join(HERE, "W2_test_data.tex")
open(out, "w", encoding="utf-8").write(tex)
print(compile_tex(out))
