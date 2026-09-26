"""W1 - plain-language write-up of the task questions. Built from 01_questions/task_items.csv."""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from latex_helpers import esc, header, compile_tex

HERE = os.path.dirname(os.path.abspath(__file__))
ITEMS = list(csv.DictReader(open(os.path.join(HERE, "..", "01_questions", "task_items.csv"), encoding="utf-8-sig")))

G3 = {"analytical": "Thinking and counting", "manual": "Hands-on", "interactive": "Dealing with people"}
C5 = {"non-routine manual": "hands-on, varied", "routine manual": "hands-on, repeated",
      "routine cognitive": "checking and counting, repeated", "non-routine analytic": "judging, varied",
      "non-routine interactive": "dealing with people, varied"}
LEAD = {"DIRECT": "Taken from", "ADAPTED": "Adapted from", "NEW": "New."}

def src_cell(it):
    lead = LEAD[it["grounding"]]
    return "\\textbf{" + lead + "} " + esc(it["source"])

def table(spec, head, rows, size="\\footnotesize"):
    s = "{" + size + "\n\\begin{longtable}{" + spec + "}\n\\toprule\n" + head + " \\\\\n\\midrule\n\\endfirsthead\n"
    s += "\\toprule\n" + head + " \\\\\n\\midrule\n\\endhead\n"
    for r in rows:
        s += " & ".join(r) + " \\\\\n"
    s += "\\bottomrule\n\\end{longtable}\n}\n"
    return s

def n(mod): return sum(1 for i in ITEMS if i["module"] == mod)
tasks = [i for i in ITEMS if i["variable"].startswith("t1_") and i["variable"] != "t1_28"]
main = [i for i in ITEMS if i["variable"] == "t1_28"][0]
t2 = [i for i in ITEMS if i["module"] == "T2"]
t3 = [i for i in ITEMS if i["module"] == "T3"]
cnt = {g: sum(1 for i in ITEMS if i["grounding"] == g) for g in ("DIRECT", "ADAPTED", "NEW")}
new_items = [i for i in ITEMS if i["grounding"] == "NEW"]

def clean_resp(s): return esc(s.replace(" | ", "; "))

tex = header("Tasks Module, Part 1: The Questions", "What we ask, why we ask it, and where each question comes from")

tex += r"""
\section*{1. What this part of the survey is for}
The ropeway may take away some of the work people do today. It may also bring new jobs.
To know who could move into a new job, we first need to know what work people really do,
and what work they have done before.

So we ask about \textbf{tasks}. A task is one small piece of work, such as ``carry a load'' or ``give change''.
Two jobs that share many tasks are close to each other. A person can move more easily
into a job that uses tasks they already know.

\section*{2. The rules we followed}
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item We ask what people \textbf{do}. We do not ask how good they are.
\item \textbf{No rating questions.} There are no scales and no numbers to pick. Answers are yes or no, a count, or a choice from a short list.
\item Questions are read aloud by the enumerator, with picture cards. Nobody needs to read.
\item Every question rests on a published survey or on the national list of occupations. Where a question has no published source, we say so.
\end{itemize}

\section*{3. How a task question works}
The enumerator reads each task and the person gives one of three answers:
\plainbox{\textbf{1} = Yes, I do this regularly in my main Yatra work.\par
\textbf{2} = Not in my main work, but I have done it before (another job, off-season work, or at home, for more than a few days in total).\par
\textbf{3} = I have never done it.}
Answer 2 matters. It shows skills that a job title hides. A porter who once worked on a building site
already knows how to build. Two other answers are recorded but not counted: \textbf{97} = does not know, and \textbf{98} = refused.

\section*{4. The 27 tasks}

Each task is read aloud with the same three-answer grid. The ``group'' column shows the broad group
we will use later in the analysis, and whether the work is done the same way each time (repeated) or
changes from case to case (varied). See section 7. The last column shows where the task comes from.

\textbf{Key to the short source names.} \emph{GS 2010} = Gathmann and Sch\"onberg (2010), a survey of 19 job tasks in Germany.
\emph{Spitz-Oener 2006} = a German study of job tasks over time. \emph{Autor-Levy-Murnane 2003} and \emph{Autor-Handel 2013} = United States task studies.
\emph{STEP} = the World Bank skills survey for developing countries (we hold the Philippines file). \emph{NCO} = India's National Classification of Occupations 2015, with the code and title of the job.
\emph{Pal et al. 2026} = a survey of Indian coal workers facing job change. \emph{Sengupta et al. 2021} = a survey of informal workers in Bangalore.
\emph{Apablaza et al. 2026} = a paper on measuring poor-quality work.
"""

rows = []
for i in tasks:
    num = i["variable"].split("_")[1]
    rv = "varied" if i["class5"].startswith("non-routine") else "repeated"
    rows.append([num, esc(i["wording"]), esc(G3[i["group3"]]) + " / " + rv, src_cell(i)])
tex += table("p{0.7cm}p{4.2cm}p{2.7cm}p{6.9cm}", "\\textbf{No.} & \\textbf{What we read aloud} & \\textbf{Group} & \\textbf{Where it comes from}", rows)

tex += "\\textbf{Main task.} After the list, one more question: ``" + esc(main["wording"]) + "'' " \
       "The answer must be a task the person coded 1. Source: " + esc(main["source"]) + "\n"

tex += r"""
\section*{5. Questions about the job itself}
These eight questions describe how the work is done. None of them is a rating.
"""
rows = [[esc(i["variable"].replace("t2_", "")), esc(i["wording"].replace(" | ", ", ")), clean_resp(i["response"]), src_cell(i)] for i in t2]
tex += table("p{0.7cm}p{4.5cm}p{3.0cm}p{6.4cm}", "\\textbf{No.} & \\textbf{Question} & \\textbf{Answers} & \\textbf{Where it comes from}", rows)

tex += r"""
\section*{6. Questions about general skills and papers held}
These sixteen questions cover reading, counting, languages, phones, courses, and licences.
They matter because some jobs need a licence or a certificate, however many tasks a person already knows.
"""
rows = [[esc(i["variable"].replace("t3_", "")), esc(i["wording"].replace(" | ", ", ")), clean_resp(i["response"]), src_cell(i)] for i in t3]
tex += table("p{0.7cm}p{4.5cm}p{2.8cm}p{6.6cm}", "\\textbf{No.} & \\textbf{Question} & \\textbf{Answers} & \\textbf{Where it comes from}", rows)

tex += r"""
\section*{7. The groups we will use later}
To see the big picture, we sort the 27 tasks into groups. We do this in two steps, general first.
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item \textbf{Three broad groups} (the same split used by Gathmann and Sch\"onberg, 2010): \emph{thinking and counting} (4 tasks), \emph{hands-on} (16 tasks), and \emph{dealing with people} (7 tasks).
\item \textbf{Five finer groups} (following Autor, Levy and Murnane, 2003, and Spitz-Oener, 2006). These also ask whether the work is repeated the same way each time or varies. The five are: hands-on varied (13 tasks), hands-on repeated (3), checking and counting repeated (3), judging varied (1), and dealing with people varied (7).
\end{itemize}
The three broad groups follow the published paper. The finer five-way sorting is our own judgement,
using the examples in the papers. We will record it before the survey goes to the field.

\section*{8. How solid is each question}
There are """ + str(len(ITEMS)) + r""" questions in all. """ + str(cnt["DIRECT"]) + r""" are \textbf{taken from} a published survey or the national occupation list,
""" + str(cnt["ADAPTED"]) + r""" are \textbf{adapted} (the same idea, changed for spoken use or to remove a rating scale),
and """ + str(cnt["NEW"]) + r""" are \textbf{new}. The new ones are:
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
"""
for i in new_items:
    tex += "\\item \\textbf{" + esc(i["variable"]) + "}: " + esc(i["wording"].replace(" | ", ", ")) + " \\textit{Why it is new:} " + esc(i["source"]) + "\n"
tex += r"""\end{itemize}

\section*{9. What is still to be checked before the survey}
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item \textbf{Talk to the unions} (pony, palki-kandi, jeep) to add or drop tasks. Palki and dandi work has no code in the national list.
\item \textbf{Check the exact weight and wording} of the lifting and repetition questions against the original STEP questionnaire. Our file only shows shortened labels.
\item \textbf{Ask workers in their own words first.} A short round (30 to 40 workers) asking ``what do you know how to do that helps you earn?'' follows the method of Sengupta and colleagues (2021). It will show if the task list is missing something.
\item \textbf{Make picture cards}, translate into Hindi, Garhwali and Nepali, and test with about 10 interviews.
\end{itemize}
\end{document}
"""

out = os.path.join(HERE, "W1_task_questions.tex")
open(out, "w", encoding="utf-8").write(tex)
print(compile_tex(out))


