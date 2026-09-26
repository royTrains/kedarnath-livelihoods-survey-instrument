"""W3 - plain-language write-up of the general analysis. Every number is read from results_general.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from latex_helpers import esc, header, compile_tex

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "..", "03_analysis", "results_general.json")))
FIG = "../03_analysis/outputs/"
pc = lambda x: f"{100 * x:.0f}"
f1 = lambda x: f"{x:.1f}"
f2 = lambda x: f"{x:.2f}"

def table(spec, head, rows, size="\\small"):
    s = "{" + size + "\n\\begin{longtable}{" + spec + "}\n\\toprule\n" + head + " \\\\\n\\midrule\n\\endfirsthead\n"
    s += "\\toprule\n" + head + " \\\\\n\\midrule\n\\endhead\n"
    for r in rows: s += " & ".join(r) + " \\\\\n"
    return s + "\\bottomrule\n\\end{longtable}\n}\n"

def fig(name, cap, w="0.85"):
    return ("\\begin{center}\n\\includegraphics[width=" + w + "\\linewidth]{" + FIG + name + "}\\\\[2pt]\n{\\small " + cap + "}\n\\end{center}\n")

c = R["counts"]; n = R["n"]
tex = header("Tasks Module, Part 3: General Results", "What the task answers show about all 13 jobs, before we look at any ropeway job")
tex += r"""
\plainbox{\textbf{Remember.} These results come from \textbf{made-up} answers for """ + str(n) + r""" imaginary workers (see Part 2).
They show that the methods work and what the output looks like. They are not findings about real workers.}

\section*{1. What we did, in one paragraph}
For each worker we have 27 answers: does this task \emph{regularly} in the main job (answer 1), \emph{did it before} elsewhere (answer 2), or never.
We first use only answer 1 (called the \textbf{strict} view: what the person does now). Then we add answer 2 (the \textbf{broad} view: what the person has done at some time).
We start with the whole picture, and leave the ropeway jobs to Part 4.

\section*{2. How many tasks does a worker do?}
The average worker does \textbf{""" + f1(c["regular_mean"]) + r"""} of the 27 tasks regularly. The range is """ + str(c["regular_min"]) + r""" to """ + str(c["regular_max"]) + r""".
The average worker has also done \textbf{""" + f1(c["before_mean"]) + r"""} more tasks before, elsewhere, so about """ + f1(c["any_mean"]) + r""" in the broad view.
""" + pc(c["share_any_before"]) + r""" in 100 workers report at least one task done before.
""" + fig("3_1_hist.png", "Number of tasks done regularly, by worker.", "0.7")

rows = [[esc(r["occupation"]), str(int(r["n"])), f1(r["regular_mean"]), f"{int(r['regular_min'])}--{int(r['regular_max'])}", f1(r["before_mean"]), f1(r["any_mean"])] for r in R["c1_rows"]]
tex += "\n" + table("lrrrrr", "\\textbf{Job} & \\textbf{Workers} & \\textbf{Regular (avg)} & \\textbf{Range} & \\textbf{Before (avg)} & \\textbf{Both (avg)}", rows)
tex += r"""
Owners do more tasks than workers: they sell, handle money, buy stock and supervise. Wage labourers report the most work done before, as we built them to (they often work in other trades in the off-season).
\textbf{Small groups.} Guides (3 workers) and ``Other'' (4 workers) are too few to say anything on their own. In the real survey they need a top-up sample or must be pooled.

\section*{3. Which jobs do which tasks?}
The picture below has one row per job and one column per task. Dark means most workers in that job do the task regularly.
Each job has a clear ``signature'': porters and wage labourers carry loads (1) and load and unload (3);
owners sell (14), bargain (15), handle cash (16) and supervise (26); drivers drive (7) and check the vehicle (9); the palki job carries a passenger (2).
""" + fig("3_2_heatmap.png", "Share of workers in each job who do each task regularly. Task numbers are listed in Part 1.", "1.0")
top = "; ".join(f"{esc(l.lower())} ({pc(p)}\\%)" for _, l, p in R["task_prev_top"][:3])
bot = "; ".join(f"{esc(l.lower())} ({pc(p)}\\%)" for _, l, p in R["task_prev_bottom"][:3])
tex += r"""
\textbf{Most common tasks} across all workers: """ + top + r""".
\textbf{Least common}: """ + bot + r""".
A task that few people do is not useless for our purpose. Electrical work or running an engine can be exactly what a ropeway job needs, so the count of people who do it matters most when we compare against jobs in Part 4.

\section*{4. Broad task groups}
We sorted the 27 tasks into three broad groups: \emph{hands-on} (16 tasks), \emph{dealing with people} (7) and \emph{thinking and counting} (4).
Overall, workers spend """ + pc(R["group3_overall"]["manual"]) + r""" in 100 of their regular tasks on hands-on work,
""" + pc(R["group3_overall"]["interactive"]) + r""" on dealing with people and """ + pc(R["group3_overall"]["analytical"]) + r""" on thinking and counting.
These shares depend partly on how many tasks fall in each group, so compare jobs with each other rather than with 100.
""" + fig("3_3_groups.png", "Share of each job's regular tasks in the three broad groups.", "0.85")
rows = [[esc(r["occupation"]), pc(r["manual"]), pc(r["interactive"]), pc(r["analytical"])] for r in R["t33_rows"]]
tex += table("lrrr", "\\textbf{Job} & \\textbf{Hands-on (\\%)} & \\textbf{With people (\\%)} & \\textbf{Thinking, counting (\\%)}", rows)
c5 = R["class5_overall"]
tex += r"""
The finer five-way split (Part 1, section 7) gives, for all workers: hands-on varied """ + pc(c5["non-routine manual"]) + r""" in 100,
dealing with people """ + pc(c5["non-routine interactive"]) + r""",
checking and counting repeated """ + pc(c5["routine cognitive"]) + r""",
hands-on repeated """ + pc(c5["routine manual"]) + r""" and judging varied """ + pc(c5["non-routine analytic"]) + r""".
Only one task falls in the last group, so it is too thin to use on its own. The per-job table is in the output file \texttt{3\_3\_class5\_share\_by\_job.csv}.

\section*{5. Which jobs are close to each other?}
Two jobs are close when workers in them do the same tasks. We measure this by \textbf{overlap} (a number from 0 to 1, called cosine similarity).
1 means the same tasks in the same shares; 0 means no task in common. We compute it between the average task lists of each pair of jobs.
The average overlap between two different jobs is """ + f2(R["job_sim_mean"]) + r""".
"""
rows = [[esc(a), esc(b), f2(s), esc(w), f2(sw)] for a, b, s, w, sw in R["nearest"]]
tex += table("p{3.4cm}p{3.4cm}rp{3.2cm}r", "\\textbf{Job} & \\textbf{Closest job} & \\textbf{Overlap} & \\textbf{Furthest job} & \\textbf{Overlap}", rows, "\\footnotesize")
tex += fig("3_4_dendrogram.png", "Jobs joined step by step by task overlap. Jobs that join near the right are very alike. The dashed line is the 0.5 cut and the dotted line the 0.3 cut.", "0.8")
cl1 = R["clusters"]; cl2 = R["clusters2"]
c2txt = "; ".join("(" + ", ".join(esc(x) for x in v) + ")" for v in cl2.values())
tex += r"""
We fixed one rule before looking: jobs stay together while their average overlap is at least 0.5 (a cut of """ + str(R["cluster_cut"]) + r""").
That rule puts \textbf{""" + str(len(cl1)) + r""" groups}: almost all jobs together and wage labourers alone. This is not useful, because
selling, cash and carrying are so common that everyone overlaps a little. We then tried a stricter cut of """ + str(R["cluster_cut2"]) + r""" \textbf{after} seeing that result, so please treat it as exploratory. It gives """ + str(len(cl2)) + r""" groups:
""" + c2txt + r""".
The shop and food owners form one tight group. Ponies form a second. Porters and palki bearers are next to each other.

\textbf{Lesson for the survey.} The task list separates the trade-owner jobs from the carrying jobs well, but many jobs share a middle ground of selling, bargaining and cash.
For the ropeway question this is helpful, because the ropeway jobs also sit in that middle ground, but the group size (13 jobs, 104 workers) is too small to trust any exact cluster.

\section*{6. How different are workers inside the same job?}
Job titles are not enough to describe people. To check how much a job title explains, we asked how much of the total difference in task lists is between jobs.
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item Job title explains \textbf{""" + pc(R["r2"]["r2"]) + r""" in 100} of the differences (""" + pc(R["r2"]["r2_adj"]) + r""" in 100 after allowing for the small groups).
If we shuffled job titles at random it would explain about """ + pc(R["r2"]["null_mean"]) + r""" in 100. In """ + str(R["r2"]["n_perm"]) + r""" random shuffles, none reached the real figure. So job titles matter, but most differences (about 6 in 10) are between workers in the same job.
\item Two workers in the same job have an overlap of \textbf{""" + f2(R["pair_cos"]["same"]) + r"""}. Two workers in different jobs have """ + f2(R["pair_cos"]["diff"]) + r""".
""" + fig("3_5_pairs.png", "Overlap between pairs of workers.", "0.65") + r"""
\item If we hide one worker and guess the job from the tasks, the right job is the closest match for \textbf{""" + pc(R["own_closest"]) + r""" in 100} workers (guessing at random would be about 1 in 13).
\end{itemize}
These figures come partly from how we built the test data (each imaginary worker has some random variation). The real survey may show more or less. What matters is that the method gives a clear reading.
The table below shows how close each worker is, on average, to the rest of their own job.
"""
rows = [[esc(r["occupation"]), str(int(r["count"])), f2(r["mean"]), f2(r["min"])] for r in R["t5_rows"]]
tex += table("lrrr", "\\textbf{Job} & \\textbf{Workers} & \\textbf{Average fit to own job} & \\textbf{Lowest}", rows)
tex += r"""
Fit is low for ``Other'' and guides because those groups are mixed or tiny.

\section*{7. Hidden experience from other work}
Answer 2 asks about tasks done before, elsewhere. How much does it add?
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item """ + pc(c["share_any_before"]) + r""" in 100 workers report at least one; in all, workers gave """ + str(R["hidden"]["total_code2"]) + r""" such answers.
\item """ + pc(R["hidden"]["share_new_to_job"]) + r""" in 100 of these are tasks that fewer than 1 in 5 of the person's own job colleagues do regularly. So most of them are \emph{new information}, which the job title would not have shown.
\item Adding them moves a worker's closest other job for """ + pc(R["hidden"]["share_switch_nearest"]) + r""" in 100 workers. The average gain in overlap with that job is small (""" + f"{R['hidden']['mean_gain_closest_other']:.3f}" + r"""). The hidden tasks are common but usually small in size.
\end{itemize}
Here we compare by the person's main off-season activity. Those who work with animals or work for wages elsewhere report the most tasks done before; those with no other work report the fewest, as one would expect.
"""
rows = [[esc(r["offseason_primary"]), str(int(r["n"])), f1(r["before_mean"]), pc(r["share_any"]), f1(r["regular_mean"])] for r in R["h_rows"]]
tex += table("lrrrr", "\\textbf{Off-season activity} & \\textbf{Workers} & \\textbf{Tasks done before (avg)} & \\textbf{Any before (\\%)} & \\textbf{Regular tasks (avg)}", rows)
tex += fig("3_6_hidden.png", "Average number of tasks done before elsewhere, by off-season activity.", "0.65")
tex += r"""
\textbf{Note.} This pattern is built into the test data on purpose (Part 2, step 3). Real data may not show it. If the real answer 2 does not vary with off-season work,
either the question is not working or the assumption is wrong. That is a useful test in the field.

\section*{8. What we learn for the survey}
\begin{enumerate}[leftmargin=1.4em,itemsep=2pt]
\item The 27-task list separates jobs reasonably well. Keep it.
\item Guides and ``Other'' need more workers, or must be pooled. With 3 or 4 workers nothing can be said.
\item Answer 2 gives new information for most workers. Keep it, but check in the pilot that people understand ``done before''.
\item Some tasks are rare (engine, electrical work, teaching, carrying a passenger). A count alone would drop them, but we keep them because ropeway jobs may need them.
\item The job-by-job overlap will change once real data are in. All code here can be run again unchanged.
\end{enumerate}

\section*{9. Files}
\begin{itemize}[leftmargin=1.2em,itemsep=1pt]
\item \texttt{03\_analysis/general\_analysis.py}: the code. \texttt{03\_analysis/results\_general.json}: all numbers.
\item \texttt{03\_analysis/outputs/}: tables (\texttt{3\_1} to \texttt{3\_6}, \texttt{.csv}) and pictures (\texttt{.png}).
\end{itemize}
\end{document}
"""
out = os.path.join(HERE, "W3_general_results.tex")
open(out, "w", encoding="utf-8").write(tex)
print(compile_tex(out))
