"""W4 - plain-language write-up of the specific (ropeway) analysis. Numbers come from results_specific.json."""
import json, os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from latex_helpers import esc, header, compile_tex

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "..", "03_analysis", "results_specific.json")))
df = pd.read_csv(os.path.join(HERE, "..", "02_data", "tasks_synth_fielded.csv"))
FIG = "../03_analysis/outputs/"
LAB = {int(k): v for k, v in R["labels"].items()}
pc = lambda x: f"{100 * x:.0f}"
p1 = lambda x: f"{x:.0f}"

def table(spec, head, rows, size="\\small"):
    s = "{" + size + "\n\\begin{longtable}{" + spec + "}\n\\toprule\n" + head + " \\\\\n\\midrule\n\\endfirsthead\n"
    s += "\\toprule\n" + head + " \\\\\n\\midrule\n\\endhead\n"
    for r in rows: s += " & ".join(r) + " \\\\\n"
    return s + "\\bottomrule\n\\end{longtable}\n}\n"

def fig(name, cap, w="0.85"):
    return "\\begin{center}\n\\includegraphics[width=" + w + "\\linewidth]{" + FIG + name + "}\\\\[2pt]\n{\\small " + cap + "}\n\\end{center}\n"

dest = {d["id"]: d for d in R["dest"]}
def tl(ids): return "; ".join(f"{t} {esc(LAB[t].lower())}" for t in ids)

# ---- worked example: an exposed worker whose 'done before' answers open a job ----
TC = [f"t1_{k:02d}" for k in range(1, 28)]
ex = None
for i, r in df[df.occupation.isin(["Porter", "Palki", "Pony worker", "Pony business"])].iterrows():
    for d in R["dest"]:
        req = [int(x) for x in d["required"].split(";")]
        have1 = {t for t in range(1, 28) if r[f"t1_{t:02d}"] == 1}
        haveb = {t for t in range(1, 28) if r[f"t1_{t:02d}"] in (1, 2)}
        s1 = sum(1 for t in req if t not in have1) / len(req); sb = sum(1 for t in req if t not in haveb) / len(req)
        gate_ok = (d["gate"] == "") or r[d["gate"]] == 1
        if s1 > 1 / 3 and sb <= 1 / 3 and gate_ok and len(req) >= 3:
            ex = (r, d, req, have1, haveb, s1, sb); break
    if ex: break

E = R["E_base"]; b = R["base"]; bo = R["boot"]
tex = header("Tasks Module, Part 4: The Ropeway Analysis", "Which workers could take the jobs the ropeway may bring, and how many may be left without work")
tex += r"""
\plainbox{\textbf{Remember.} The workers are \textbf{made-up}. The number of ropeway jobs is a \textbf{placeholder} (we do not know it yet).
The job task lists are \textbf{provisional}, taken from the national occupation list. The results show how the method works and what it can and cannot say.
They are not a forecast.}

\section*{1. The question}
If the ropeway takes work away from people who carry pilgrims and goods on the trek, how many of them might end up without work?
Two things decide this. First, \emph{how many new jobs there are}. Second, \emph{whether the people who lose work can actually do those jobs}.
The task questions help with the second thing.

\section*{2. Which jobs might people move to?}
We listed """ + str(len(R["dest"])) + r""" jobs that a ropeway and the trade around it may bring. Each has a short list of tasks it needs.
The lists come from the national occupation list (NCO 2015), so we can say where each one comes from. Where the list does not cover a job, we used judgement and say so.
Some jobs also need a paper (a licence or certificate). We call that a \textbf{gate}: without it the person cannot take the job, however many tasks they know.
"""
rows = []
for d in R["dest"]:
    req = [int(x) for x in d["required"].split(";")]
    gate = esc(d["gate_note"]) if d["gate"] else "none"
    rows.append([esc(d["id"]), esc(d["title"]), tl(req), esc(d["source"]), gate])
tex += table("p{0.9cm}p{2.8cm}p{3.8cm}p{3.6cm}p{2.9cm}", "\\textbf{Id} & \\textbf{Job} & \\textbf{Tasks it needs} & \\textbf{Where from} & \\textbf{Gate}", rows, "\\scriptsize")
tex += r"""
\textbf{Two cautions.} (1) The national list gives only 1 to 3 tasks for most of these jobs. That is few (see section 6). (2) The gate for ropeway operator, mechanic and guide is our assumption, since the national list does not state one.
Before real use, these lists should be checked with the ropeway company, hotel owners and unions.

\section*{3. Two simple measures}
For each worker and each job we count:
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item \textbf{Shortage}: of the tasks the new job needs, what share does the worker \emph{not} do? 0 means they can do all of them. 1 means none.
\item \textbf{Unused}: of the tasks the worker does now, what share would the new job not use? High means a lot of their skill goes to waste.
\end{itemize}
(These two ideas come from Neffke and co-authors, 2024, but their version uses many skills per job; ours uses tasks that are answered yes or no.)
We use two views of what a worker can do. \textbf{Strict}: only tasks done regularly now. \textbf{Broad}: tasks done regularly plus tasks done before (answer 2).

\textbf{Rule fixed before looking at the data:} a worker \emph{could take} a job if the shortage is one-third or less, \emph{and} the worker holds any gate paper. The base case uses the broad view.
We also test other cut-offs (0 and one-half).
"""
if ex:
    r, d, req, have1, haveb, s1, sb = ex
    prior = sorted(haveb - have1)
    tex += r"""
\textbf{Worked example.} Worker """ + str(int(r["resp_id"])) + r""" is a """ + esc(r["occupation"].lower()) + r""". The job ``""" + esc(d["title"].lower()) + r"""'' needs: """ + tl(req) + r""".
Doing tasks regularly now, the worker lacks """ + str(sum(1 for t in req if t not in have1)) + r""" of the """ + str(len(req)) + r""" (shortage """ + f"{s1:.2f}" + r"""), so the strict view says \emph{no}.
The worker also did before: """ + tl([t for t in prior if t in req]) + r""". In the broad view the shortage is """ + f"{sb:.2f}" + r""" and the answer is \emph{yes}.
This is the reason we ask answer 2 on the task grid.
"""

tex += r"""
\section*{4. Who is exposed to the ropeway?}
We need to know whose work the ropeway may replace. The test data gives three ways to decide:
"""
rows = []
for key, name in (("E_base", "By job title: porters, palki bearers, pony workers, pony owners"), ("E_main", "By main task: carrying, passenger, or pack animals"), ("E_any", "By any regular carrying, passenger or pack-animal task")):
    rows.append([esc(name), str(R[key.replace("E_", "E_")])])
tex += table("p{11cm}r", "\\textbf{Way of deciding} & \\textbf{Workers}", rows)
tex += r"""
The first is used in the base case (""" + str(E) + r""" workers). The second misses pony people whose main task is feeding animals, loading, or selling rides, and it includes one wage labourer.
The third counts """ + str(R["E_any"]) + r""" workers, including many shop and hotel workers who sometimes carry loads. This is too wide.
\textbf{Lesson.} Exposure should not be guessed from a task or a title. The survey needs its own direct exposure questions (module D), such as ``does your income come from taking people or goods on the Kedarnath trek?''.

\section*{5. Who could take which job?}
The picture and table show, for the """ + str(E) + r""" exposed workers, the share who pass the rule for each job.
""" + fig("4_5_eligible.png", "Share of exposed workers who could take each job (shortage one-third or less, and gate paper held).", "0.85")
rows = []
for r_ in R["elig_rows"]:
    rows.append([esc(r_["title"]), str(r_["n_required"]), pc(r_["gate_share_all"]), pc(r_["strict_gate"]), pc(r_["broad_gate"]), pc(r_["broad_no_gate"])])
tex += table("p{5.2cm}rrrrr", "\\textbf{Job} & \\textbf{Tasks} & \\textbf{Hold gate, all workers (\\%)} & \\textbf{Strict (\\%)} & \\textbf{Broad (\\%)} & \\textbf{Broad, no gate (\\%)}", rows, "\\footnotesize")
tex += r"""
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item The jobs closest to carrying work (station attendant, room attendant, construction, ticket counter) suit """ + pc(min(x["broad_gate"] for x in R["elig_rows"] if x["id"] in ("RW4", "RW5", "HOS1", "CON"))) + r"""--""" + pc(max(x["broad_gate"] for x in R["elig_rows"] if x["id"] in ("RW4", "RW5", "HOS1", "CON"))) + r""" in 100 exposed workers.
\item The technical ropeway jobs (electrician, mechanic) suit almost no one. Few people hold an ITI or similar paper, and fewer do electrical or engine work.
\item Guard, guide and driver jobs are open on tasks to many, but few hold the paper. \textbf{Gates matter more than tasks for these jobs.} This is why the questions on licences (T3) are in the survey.
\item On average an exposed worker could take \textbf{""" + f"{R['n_options_broad_mean']:.1f}" + r"""} of the """ + str(len(R["dest"])) + r""" jobs.
\textbf{""" + pc(R["no_option_broad"]) + r""" in 100} could take none at all (""" + pc(R["no_option_strict"]) + r""" in 100 in the strict view). Weighted for drop-out, """ + pc(R["no_option_broad_w"]) + r""" in 100.
\end{itemize}
The number who could take \emph{no} job is important. It does not depend on how many jobs exist. It is a floor: even if jobs were unlimited, these workers could not be placed with the tasks and papers they hold now.

\section*{6. Type of move, and a warning}
Neffke and co-authors sort moves into four types by combining shortage and unused skills: a \emph{close match} (low, low), \emph{downskilling} (few tasks to add, many unused), \emph{upskilling} (many to add, few unused), and \emph{reskilling} (many to add, many unused).
"""
lev = ["close match", "downskill (surplus skills)", "upskill (tasks to add)", "reskill (start over)"]
rows = [[esc(x), pc(R["types_all_pairs"][x]), pc(R["types_best"][x])] for x in lev]
tex += table("lrr", "\\textbf{Type of move} & \\textbf{All worker-job pairs (\\%)} & \\textbf{To the worker's closest job (\\%)}", rows)
tex += fig("4_3_types.png", "Type of move to each worker's closest job, by present job.", "0.7")
tex += r"""
Almost every move is called ``downskilling'' or ``reskilling'', and """ + pc(R["share_pairs_redundancy_high"]) + r""" in 100 pairs have a high ``unused'' share.
This is not a finding. It happens because our job lists have only about """ + f"{R['mean_D']:.1f}" + r""" tasks while a worker does about """ + f"{R['mean_O']:.1f}" + r""", so most of what the worker does can never be used by a short list.
\textbf{Lesson.} The ``unused'' measure and the four types need long task lists for each job (10 or more). With the short lists we have, use \textbf{shortage only}. To use the four types, the survey needs job task lists from employers or a ropeway operator.

We also checked whether the closest job changes with the measure. The closest job by shortage is the same as the closest by two other common measures (cosine and Jaccard) for """ + pc(R["agree_shortage_cosine"]) + r""" in 100 workers.
So the ranking of jobs \emph{is} sensitive to the measure when job lists are short. Shortage is the only measure with a plain meaning (``how many of the new job's tasks are new to me''), so we keep it.

\section*{7. How many may be left without work?}
We count three things, all per 100 exposed workers:
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item \textbf{Numbers only}: exposed workers minus new jobs. This is what most reports do. It ignores who can do what.
\item \textbf{Skills, best possible}: give jobs to workers so that as many as possible are placed, each worker only in a job they could take (maximum matching). This is the best case.
\item \textbf{Skills, by lottery}: jobs are given at random among workers who could take them, repeated 300 times. This is closer to how hiring might go.
\end{itemize}
\textbf{Job supply is a placeholder.} We tried three totals (25, 50 and 100 new jobs per 100 exposed workers) and three mixes (equal across job types; three times as many technical jobs; three times as many service jobs). The real numbers must come from the ropeway plan and an employer check.
""" + fig("4_6_curve.png", "Workers left without a job per 100 exposed, as new jobs increase (equal mix).", "0.7")
rows = []
for s in R["scenarios"]:
    rows.append([str(int(s["vacancies_per_100_exposed"])), esc(s["mix"]), f"{s['displaced_min_per100']:.0f}", f"{s['displaced_skill_best_per100']:.0f}", f"{s['displaced_skill_lottery_per100']:.0f}"])
tex += table("rlrrr", "\\textbf{New jobs per 100 exposed} & \\textbf{Mix} & \\textbf{Numbers only} & \\textbf{Skills, best} & \\textbf{Skills, lottery}", rows)
tex += r"""
\textbf{Reading the table.} In the middle case (50 new jobs per 100 exposed, equal mix), numbers alone give """ + p1(b["min_per100"]) + r""" without a job per 100.
Once tasks and papers are taken into account, it is \textbf{""" + p1(b["best_per100"]) + r"""} in the best case and \textbf{""" + p1(b["lottery_per100"]) + r"""} by lottery.
Resampling the workers 1{,}000 times gives a range of about """ + p1(bo["best"][0]) + r""" to """ + p1(bo["best"][2]) + r""" for the best case. That range comes only from having few workers; it does not include uncertainty about the job supply or the job lists, which are larger.

Even if there were \textbf{one new job for every exposed worker}, about """ + p1(R["scenarios"][6]["displaced_skill_best_per100"]) + r""" in 100 would still be without work, because the new jobs are of the wrong kind or need papers.
When there are more technical jobs, the number without work is higher.

\section*{8. Do the choices change the answer?}
The middle case (50 new jobs per 100 exposed, equal mix, exposed by job title) under different rules:
"""
rows = []
for s in R["sens"]:
    if s["exposure"] != "title": continue
    rows.append([esc(s["view"]), f"{s['cut']:.2f}", "yes" if s["gates"] else "no", f"{s['no_option']:.0f}", f"{s['displaced_min']:.0f}", f"{s['displaced_skill_best']:.0f}"])
tex += table("llrrrr", "\\textbf{View} & \\textbf{Shortage cut} & \\textbf{Gates} & \\textbf{Could take no job (\\%)} & \\textbf{Numbers only} & \\textbf{Skills, best}", rows, "\\footnotesize")
oth = [s for s in R["sens"] if s["view"] == "broad" and abs(s["cut"] - 0.33) < 0.01 and s["gates"] and s["exposure"] != "title"]
tex += r"""
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item A stricter rule (cut 0) or the strict view raises the count. A looser rule (cut one-half) lowers it. \textbf{The result is quite sensitive to the cut}, so real results should show all three.
\item Ignoring gates lowers the count by about 10 points. Gates matter.
\item If we require the optional tasks too, the share who could take no job rises to """ + p1(R["sens_optional"]["no_option"]) + r""" in 100.
\item If the ropeway operator job needs a certificate, the answer barely changes here.
\item Using the other two ways of deciding who is exposed:"""
for s in oth:
    tex += " " + esc(s["exposure"]) + " (" + str(int(s["E"])) + " workers): " + p1(s["displaced_skill_best"]) + " in 100 without a job;"
tex += r"""
\end{itemize}

\section*{9. What we learn for the survey}
\begin{enumerate}[leftmargin=1.4em,itemsep=2pt]
\item \textbf{Keep the three-answer task grid.} Answer 2 changes who could take a job, though not by a lot.
\item \textbf{Keep the licence and certificate questions (T3).} Gates decide more than tasks for the driver, guard, guide and technical jobs.
\item \textbf{Add direct exposure questions (module D).} Exposure cannot be guessed from job titles or tasks.
\item \textbf{Get long task lists for the destination jobs.} The national list is too short for the ``unused'' measure. A short employer or operator questionnaire can give this, and also the number of jobs.
\item \textbf{Report ranges, not one number.} The result depends on the cut, the gate rules, the job supply and the job mix.
\item \textbf{More workers in the small groups.} Twenty-six exposed workers give crude results. The real quota should give enough in each of the four exposed jobs.
\end{enumerate}

\section*{10. What this cannot tell us}
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item The job supply is invented. The answer is a function of it.
\item Only exposed workers compete for jobs here. In fact others (workers from elsewhere, other locals) will also apply, so real competition is stronger and the count without work is a \textbf{lower} figure.
\item Workers may also lose part of their work rather than all of it, or move into work that is not on the list (for example their own small business). We do not count that here.
\item Having the tasks is not the same as being hired. Age, health, language, caste and contacts also matter and are not in this analysis.
\item The task answers were made from our own rules, so agreement with them is not evidence about the world.
\end{itemize}

\section*{11. Files}
\begin{itemize}[leftmargin=1.2em,itemsep=1pt]
\item \texttt{03\_analysis/specific\_analysis.py}: the code. \texttt{03\_analysis/results\_specific.json}: all numbers.
\item \texttt{03\_analysis/outputs/4\_1} to \texttt{4\_7}: tables and pictures. The destination job list is \texttt{4\_1\_destination\_jobs.csv}.
\end{itemize}
\end{document}
"""
out = os.path.join(HERE, "W4_ropeway_results.tex")
open(out, "w", encoding="utf-8").write(tex)
print(compile_tex(out))
