"""W5 - plain-language wrap-up: what the test showed about the questions, and what is still needed."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from latex_helpers import header, compile_tex

HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "..", "03_analysis", "results_general.json")))
S = json.load(open(os.path.join(HERE, "..", "03_analysis", "results_specific.json")))
pc = lambda x: f"{100 * x:.0f}"
b = S["base"]

tex = header("Tasks Module, Part 5: Wrap-up", "What the test showed about the questions, and what we still need before the field")
tex += r"""
\plainbox{Everything here rests on \textbf{made-up} answers. The test checks the \emph{questions and the method}. It says nothing yet about real workers.}

\section*{1. What was done}
\begin{tabular}{@{}p{2.2cm}p{7.5cm}p{4.6cm}@{}}
\toprule
\textbf{Part} & \textbf{What it covers} & \textbf{File} \\
\midrule
Part 1 & The 52 questions and where each comes from & \texttt{W1\_task\_questions.pdf} \\
Part 2 & The made-up data and its checks & \texttt{W2\_test\_data.pdf} \\
Part 3 & General results: tasks, jobs, overlap, hidden experience & \texttt{W3\_general\_results.pdf} \\
Part 4 & The ropeway analysis: jobs, gates, count without work & \texttt{W4\_ropeway\_results.pdf} \\
Part 5 & This wrap-up & \texttt{W5\_wrapup.pdf} \\
\bottomrule
\end{tabular}

The working list of steps is in \texttt{CHECKLIST.md}. All steps are ticked.

\section*{2. What the test showed about the questions}
\subsection*{Keep}
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item \textbf{The 27-task grid with three answers.} It separates the jobs (job title explains about """ + pc(G["r2"]["r2"]) + r""" in 100 of the differences between workers) and it also shows differences \emph{inside} a job, which titles hide.
\item \textbf{Answer 2 (``done before elsewhere'').} """ + pc(G["counts"]["share_any_before"]) + r""" in 100 workers gave at least one, most of them new to their job. It lowered the share of exposed workers who could take no job from """ + pc(S["no_option_strict"]) + r""" to """ + pc(S["no_option_broad"]) + r""" in 100. The change is modest but real.
\item \textbf{Licence and certificate questions (T3).} For driver, guard, guide and technical jobs, the paper decides more than the tasks. Very few workers held an ITI, guard or guide paper, so these jobs were closed to nearly everyone.
\item \textbf{Rare tasks} (engine, electrical, teaching, carrying a passenger). They look unimportant by count, but they are what technical ropeway jobs need.
\end{itemize}
\subsection*{Change or add}
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item \textbf{Add direct questions on exposure (module D).} Exposure by job title gave """ + str(S["E_base"]) + r""" workers, by main task """ + str(S["E_main"]) + r""", and by any carrying task """ + str(S["E_any"]) + r""". They cannot be swapped for each other.
\item \textbf{Add a short employer or ropeway-operator questionnaire.} It must give (a) the number and kind of new jobs, (b) a full task list for each job (10 or more tasks), and (c) the papers each job needs. Without it the ``unused skills'' measure cannot be used and the result cannot be read.
\item \textbf{Pilot the meaning of ``done before''.} Ask about 10 people to explain the question back, then check that answer 2 rises with off-season work and past jobs. If it does not, the question is not working.
\item \textbf{Plan for the small groups.} Guides and ``Other'' had 3 and 4 workers. The exposed jobs together gave """ + str(S["E_base"]) + r""" workers. That is too few for stable results; the real quota needs enough in each exposed job.
\end{itemize}

\section*{3. What we still need from outside the survey}
\begin{tabular}{@{}p{4.3cm}p{5.6cm}p{4.5cm}@{}}
\toprule
\textbf{Input} & \textbf{Why} & \textbf{Where it may come from} \\
\midrule
Number and kind of new jobs & The count without work depends on it more than on anything else & Ropeway project plan, developer, employer questionnaire \\
Totals of workers in each job & To scale from the sample to the region (the test only fixes drop-out) & Union and registration lists, tourism board counts \\
Full task lists for the new jobs & The national list gives only 1 to 3 tasks per job & Ropeway operator, hotel owners, existing ropeway sites \\
Papers each job requires & Gates decide many outcomes; three are our assumption (operator, mechanic, guide) & Uttarakhand tourism rules, ITI and NSQF bodies, operator \\
Union check of the 27 tasks & Palki and dandi work has no national code & Pony, palki and porter unions \\
Exact wording of STEP lifting and repetition questions & Our file shows only shortened labels & Original STEP questionnaire \\
Open round with 30 to 40 workers & To find tasks the list is missing (Sengupta et al. 2021) & Field team \\
Translation and picture cards & Questions are read aloud, and nobody needs to read & Field team, 10 test interviews \\
\bottomrule
\end{tabular}

\section*{4. Results that must be shown as ranges}
The count of workers without a job, in the middle case, was """ + f"{b['best_per100']:.0f}" + r""" in 100 (best case) or """ + f"{b['lottery_per100']:.0f}" + r""" in 100 (lottery), against """ + f"{b['min_per100']:.0f}" + r""" in 100 when only numbers are counted.
It moves a lot with the shortage cut, the gate rules, the job supply and the job mix (Part 4, sections 7 and 8).
Any real report should show a table like those, and not one number.

\section*{5. Decisions still open (yours)}
\begin{enumerate}[leftmargin=1.4em,itemsep=2pt]
\item Add the employer or ropeway-operator mini-module to the survey plan?
\item Test reading and counting directly (a few simple tasks) instead of asking, or keep questions T3\_01 to T3\_05 as they are?
\item Confirm the list of destination jobs, or replace it after the union and employer checks.
\item The parts on \emph{readiness for a new job} and \emph{preferences and barriers} (T4 and T5) are not written yet. They involve asking about future or hypothetical situations, so we need to decide how far to go with them.
\item Employment-poverty questions (the Apablaza core) are ready to be added when you want them.
\end{enumerate}
\end{document}
"""
out = os.path.join(HERE, "W5_wrapup.tex")
open(out, "w", encoding="utf-8").write(tex)
print(compile_tex(out))
