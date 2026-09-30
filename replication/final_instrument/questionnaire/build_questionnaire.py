"""Builds variable_dictionary.csv and the questionnaire PDF from dictionary.py (the single source)."""
import csv, os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dictionary import ROWS, LSETS, MODULES, TASKS, INTROS, CONSENT_SCRIPT, HINTS
from latex_helpers import esc, compile_tex

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MODNAME = {m[0]: m[1] for m in MODULES}
KIND = {"id": "ID", "cat": "Choice", "bin": "Yes/No", "num": "Number", "count": "Count", "money": "Rs amount", "date": "Date"}

# ---------------- variable_dictionary.csv ----------------
with open(os.path.join(HERE, "variable_dictionary.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["order", "module", "variable", "label", "origin", "type", "value_labels", "question_or_formula", "meaning", "skip_rule", "source"])
    for i, r in enumerate(ROWS, 1):
        vals = "; ".join(f"{k}={v}" for k, v in LSETS[r["lset"]].items()) if r["lset"] else ""
        w.writerow([i, r["module"], r["name"], r["label"], r["origin"], r["kind"], vals,
                    r["formula"] if r["origin"] == "constructed" else r["question"], r["desc"], r["skip"], r["source"]])

def answers(r):
    if r["origin"] in ("paradata", "synthetic"): return "Automatic / enumerator"
    if r["kind"] == "bin" and r["lset"] in ("yn", None): return "1 Yes, 0 No"
    if r["lset"]:
        L = LSETS[r["lset"]]
        # no cards shown to the respondent, ever -- for long lists (occupation, activity, native
        # language) the enumerator asks openly and codes the answer, so the full code list is
        # printed here only as the enumerator's own coding reference, not something read aloud
        return "; ".join(f"{k} {v}" for k, v in L.items())
    return {"money": "Rupees (whole number)", "count": "Whole number", "num": "Number"}.get(r["kind"], "")

def table(rows, head, spec, size="\\scriptsize"):
    s = "{" + size + "\n\\begin{longtable}{" + spec + "}\n\\toprule\n" + head + " \\\\\n\\midrule\n\\endfirsthead\n\\toprule\n" + head + " \\\\\n\\midrule\n\\endhead\n"
    for r in rows: s += " & ".join(r) + " \\\\\n"
    return s + "\\bottomrule\n\\end{longtable}\n}\n"

import warnings; warnings.filterwarnings('ignore')
DD = pd.read_stata(os.path.join(HERE, '..', 'data', 'kedarnath_final_n200_full.dta'), convert_categoricals=False)

asked = [r for r in ROWS if r["origin"] == "asked"]
per_mod = {m[0]: sum(1 for r in ROWS if r["module"] == m[0] and r["origin"] in ("asked", "paradata")) for m in MODULES}

cons = [r for r in ROWS if r["origin"] == "constructed"]

# coverage of destination-job task lists by the 12 tasks
dest = pd.read_csv(os.path.join(ROOT, "tasks_module", "03_analysis", "outputs", "4_1_destination_jobs.csv"))
have = {int(x[2]) for x in TASKS}
cov = []
for _, j in dest.iterrows():
    req = [int(x) for x in str(j.required).split(";")]
    cov.append((j.title, sum(1 for t in req if t in have), len(req)))
full = [c for c in cov if c[1] == c[2]]

PRE = r"""\documentclass[10pt]{article}
\usepackage[a4paper,margin=0.75in]{geometry}
\usepackage{booktabs,longtable,array,enumitem}
\usepackage[hidelinks]{hyperref}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}
\renewcommand{\arraystretch}{1.12}
\newcommand{\plainbox}[1]{\par\vspace{2pt}\noindent\fbox{\parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule\relax}{#1}}\par\vspace{2pt}}
\begin{document}
"""
tex = PRE + r"""
{\Large\textbf{Kedarnath Yatra Workers Survey: Final Questionnaire and Variable List}}\par
{\large Version 2, worked example. Read-aloud interview, tablet-based, one visit, 45 minutes at most}\par\vspace{2pt}\hrule\vspace{6pt}

\plainbox{\textbf{What this is.} The final list of questions and variables for the survey of Yatra workers. The main aim is to measure
\textbf{vulnerability to poverty} (VEP and multidimensional poverty). A short employment-quality block and a short tasks block are added.
The tasks block only gathers the facts the later paper on job transfer needs. There are \textbf{""" + str(len(asked)) + r""" asked questions}, """ + str(sum(1 for r in ROWS if r['origin']=='paradata')) + r""" recorded automatically or by the enumerator,
and """ + str(len(cons)) + r""" variables built afterwards in Stata. The companion file \texttt{variable\_dictionary.csv} lists everything in one table.}

\section*{1. Rules the questions follow}
\begin{itemize}[leftmargin=1.2em,itemsep=1pt]
\item \textbf{No rating questions.} Every answer is a fact: yes or no, a count, an amount, or a choice from a card. Nobody is asked to score anything on a scale.
\item \textbf{Aggregate household questions}, no household roster. The respondent is the worker. Consumption is for the household's usual place of living.
\item \textbf{Codes.} 98 = prefers not to say (schooling, ropeway view). 97 = don't know (job-quality questions). Blank = the question was skipped by a rule shown in the table.
\item \textbf{Recall.} 30 days for frequent spending, 12 months for infrequent spending, health, income and shocks, 15 days for recent illness.
\item Questions are read aloud in Hindi, Garhwali or Nepali. Cards are used for long answer lists.
\end{itemize}

\section*{2. Time budget}
Interview length is NOT estimated here. The module list below gives item counts only; the pretest measures real durations from the tablet's own start and end timestamps.
"""
rows = [[esc(m[0]), esc(m[1]), str(per_mod[m[0]])] for m in MODULES]
rows.append(["", "\\textbf{Total}", "\\textbf{" + str(sum(per_mod.values())) + "}"])
tex += table(rows, "\\textbf{Module} & \\textbf{Name} & \\textbf{Items} & \\textbf{Minutes}", "llrr", "\\small")
tex += r"""
Interview length is measured from the tablet's own start and end timestamps at the pretest; no estimate is claimed here.
With 4 enumerators at 5 to 8 interviews a day, one round of about 10 days gives roughly 200 to 320 interviews.

\section*{3. Consent script (read before Module A)}
\textit{``We are doing a study on the livelihoods of people who work on the Yatra route. It takes about 40 minutes. You can stop at any time and you can skip any question. Nothing you say will be linked to your name.
Do you agree to take part?''} Record consent (variable \texttt{consent}); stop the interview if the answer is no.

"""
for m in MODULES:
    code = m[0]
    rr = [r for r in ROWS if r["module"] == code and r["origin"] in ("asked", "paradata")]
    tex += "\\subsection*{Module " + code + ": " + esc(m[1]) + "}\n"
    # Read-aloud introduction, set in a quote block so it is visibly not one of the numbered
    # questions. On paper the distinction has to carry itself: there is no interface to enforce it.
    if code in INTROS:
        tex += "\\begin{quote}\\small\\textit{Read aloud: " + esc(INTROS[code]) + "}\\end{quote}\n"
    # Module P carries the consent script, which is read verbatim rather than paraphrased -- so it is
    # printed in full on the paper form too, not referred to.
    if code == "P":
        paras = "\\\\[6pt]".join(esc(x) for x in CONSENT_SCRIPT.split("\n\n"))
        tex += ("\\begin{quote}\\small\\textbf{Read this out, word for word:}\\\\[4pt]\n\\textit{"
                + paras + "}\\end{quote}\n")
    rows = []
    for i, r in enumerate(rr, 1):
        q = esc(r["question"])
        var = "\\texttt{" + esc(r["name"]) + "}"
        note = ""
        if r["skip"]: note += "\\newline \\textit{Skip: " + esc(r["skip"]) + "}"
        note += "\\newline " + esc("Source: " + r["source"])
        rows.append([f"{code}{i}", q, esc(answers(r)), var + note])
    tex += table(rows, "\\textbf{No.} & \\textbf{Question or instruction} & \\textbf{Answers} & \\textbf{Variable, skip rule, source}", "p{0.8cm}p{6.4cm}p{3.6cm}p{5.8cm}")

tex += r"""
\section*{4. Variables built afterwards (not asked)}
All of these are computed in Stata (\texttt{do/02\_build\_final\_dataset.do}) from the asked answers, so the analysis starts from raw answers and every step can be checked.
"""
rows = [["\\texttt{" + esc(r["name"]) + "}", esc(r["desc"]), esc(r["formula"])] for r in cons]
tex += table(rows, "\\textbf{Variable} & \\textbf{Meaning} & \\textbf{How it is made}", "p{3.3cm}p{7.6cm}p{5.7cm}")

tex += r"""
\section*{5. Apablaza et al. (2026) questions: what we asked, changed or dropped}
Module K uses the questions in Appendix 2 of the paper. Their own skip logic is kept: wage workers only for the contract and leave questions; extra hours only if the worker wants more work; the search question only if some month had no work.
The paper asks every household member aged 5 or more. We ask the respondent only (no household roster), so an employment index for the whole household cannot be built.
"""
AP = [("Q1 household size; Q2 sex, age", "hhsize, female, age", "Module A"),
      ("Q3 disability", "not asked", "Respondents are working; not needed for the five domains"),
      ("Q4 birthplace, main earner", "origin, n_earners", "Modules A and D"),
      ("Q5 situation last month", "job_situation", "Shortened to categories that fit a working respondent"),
      ("Q6 occupation (open)", "occupation", "Card with 13 groups (the quota variable), not an open answer"),
      ("Q7 activity of the workplace", "not asked", "Implied by the occupation group"),
      ("Q8 status in the job", "employment_type", "PLFS four-way status instead of the paper's seven categories"),
      ("Q9 permanent / seasonal / casual", "job_permanence", "Probation and fixed-term merged"),
      ("Q10 years in this job", "years_in_yatra_work", "Whole years, so a test for under 6 months is not possible"),
      ("Q11 signed contract", "contract_status", "Wage workers only"),
      ("Q12 registered workplace", "workplace_registered", "Widened to local registrations (union, Yatra registration, trade licence, GST)"),
      ("Q13 hours in a normal week", "hours_day_yatra, days_week_yatra", "Two easier questions, multiplied afterwards"),
      ("Q14 monthly earnings", "income_m1 to income_m12", "Asked month by month (section 6)"),
      ("Q15 earnings range if unknown", "not asked", "Amounts are asked for every month, so no range is needed"),
      ("Q16 pension", "pension_contrib", "As in the paper"),
      ("Q17 health insurance through work", "work_health_ins", "As in the paper"),
      ("Q18 leave rights", "leave_rights", "Wage workers only"),
      ("Q19 ever injured; Q20 injury or death at workplace, last 12 months", "injured_ever, workplace_injury_12m", "The paper's evidence on hazards"),
      ("Q21 wants more work; Q22 how many hours", "wants_more_work, more_hours_week", "As in the paper"),
      ("Q23 weeks looking for work", "looked_for_work_idle", "Tied to the months with no work in the calendar"),
      ("Q24 first job; Q25 why lost the last job", "not asked", "Apply to the unemployed only; prev_occ_reason covers job changes")]
rows = [[esc(a), "\\texttt{" + esc(b) + "}", esc(c)] for a, b, c in AP]
tex += table(rows, "\\textbf{Apablaza question} & \\textbf{Our variable} & \\textbf{Note}", "p{5cm}p{4.6cm}p{6.7cm}")
cond = "%.0f" % (100 * DD.emp_dep_cond.mean()); k2 = "%.0f" % (100 * DD.emp_poor_k2.mean()); k3 = "%.0f" % (100 * (DD.emp_dep_count >= 3).mean())
tex += r"""
The five deprivation indicators (access, compensation, security, stability, working conditions) are built from these raw answers in Stata, using the thresholds in Table 3 of the paper.
Where the paper gives a choice, the fallback is used for pay (67 percent of the median) because the international-dollar version needs a conversion factor we have not verified.

\section*{6. What changed from the earlier draft, and why}
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item \textbf{The 12-month calendar is back.} The worker gives the main activity for each month and the earnings for each month with work. Earnings are asked month by month, so that a single typical figure is not rounded (heaping) and monthly earnings are not guessed from an annual total.
Because it is the original design, the constructed income, the months of work and the seasonality measure now reproduce the earlier pipeline exactly. Months with no work are filled with 0 by the tablet, so the calendar costs about 4.5 minutes.
\item \textbf{Licences and certificates are gone.} People drive, wire and guide without holding a licence, so holding one says little about what they can do. The block asks what people do (the three-answer grid) and adds three factual driving questions, asked only of those who have driven: motorcycle, car, truck or bus, with or without a licence. Entry papers can be studied in the second paper if needed.
\item \textbf{The consumption module now asks a Yatra-season figure AND an off-season figure for every routine item} (9 pairs: staples, perishables, home-grown/gifted food, eating out, fuel, toiletries, transport/communication, rent, non-hospital medical), instead of one ``last 30 days'' figure. Workers here are migrants: fieldwork happens during the Yatra season, so a single recent-recall question would describe only the season the interview happens to fall in, not the whole year. The item groupings and which items get a long (365-day) recall instead still follow HCES 2022-23, IHDS-II and the Nigeria GHS-Panel (read directly; see section 8).
\item \textbf{Remittances are split the same way} (Module C): a usual monthly amount sent and received, for the Yatra season and for the off-season, instead of one annual figure.
\item \textbf{The annual welfare measure is now a genuine annual average}, not an on-season snapshot: each seasonal item is weighted by the number of Yatra-season months and off-season months from the work calendar, exactly as income already was. In the test data this moves \texttt{cons\_pc\_pm} down and the poverty rate up, because the earlier design implicitly treated on-season spending as if it held all year; see the note in \texttt{checks/check\_report.txt}.
\item \textbf{Two new consumption variables for robustness:} a narrow measure (30-day items only, as in Dercon and Krishnan 2000) and a per-adult-equivalent measure (needs the count of children under 15, now asked).
\item \textbf{Four opinion questions on a 1 to 5 scale were removed}, in line with the no-rating rule. Only the three-way ropeway view remains.
\item \textbf{Dropped for length:} remittance frequency and \texttt{prev\_offseason\_work}. The season start, end and length, and the main off-season activity, are now built from the calendar instead of being asked.
\item \textbf{Added:} sex, native language, earners, children under 15 and school-age children, the way the household coped with a shock, direct exposure to the trek, and the Apablaza questions.
\item \textbf{Food security and disability are new} (Modules H and I): a long-term illness/disability flag and an unmet-healthcare-need question (VASyR 2025 / Washington Group short set), plus the standard WFP reduced Coping Strategy Index. This was a genuine gap: a vulnerability-to-poverty instrument with no food-security module. Modelled on the VASyR/Lyons, Kass-Hanna and Montoya Castano (2023) multidimensional livelihood index, read directly (see \texttt{replication/vasyr\_example/}); a full dietary-diversity count was left out to stay inside the 45-minute limit.
\item \textbf{The rCSI is a Yatra-season/off-season pair, like the consumption module}: the first version asked each of the five WFP coping items once, over ``the last 7 days'' -- fieldwork happens during the Yatra season, so that could only describe on-site coping at the work site, not the household's usual pattern (which may look different off-season, with different members present). Each item is now asked as a usual-week day-count for each season, combined into an annual-average rCSI the same way income and consumption already are.
\item \textbf{Household-head and family-structure items are new} (Module A): relationship to the household head and the head's sex (auto-filled with the respondent's own sex when they are the head), and whether the family is nuclear, joint or single-member. \texttt{hhsize} is now asked as household membership directly (``how many members live in your household'') rather than through a shared-kitchen framing.
\item \textbf{A direct residence-migration question is new} (Module D): apart from the seasonal Yatra-work absence, whether the respondent's usual place of residence for most of the year differs from their family's native/home place -- distinct from \texttt{origin} (where they are originally from) and from the NSS short-term-migrant item (a specific 15-day-to-6-month absence threshold). Asked only of non-local-origin respondents.
\item \textbf{The interview site is no longer named.} \texttt{location\_cluster} now has generic labels (Cluster 1-4) instead of the actual place names: enumerators read the site off a printed crosswalk card kept by the research team, not a name on the tablet, so no exported record carries a named interview site. The underlying codes and the health-access-tier logic built from them are unchanged. On the Kobo build (\texttt{questionnaire/build\_xlsform.py}), the enumerator-name question is dropped the same way -- each enumerator has their own Kobo login, which records who submitted automatically -- and GPS is captured silently in the background the moment consent is given, with no on-screen question.
\item \textbf{Tasks block: 12 tasks} (from 27), the ones the provisional destination jobs need most. They fully cover """ + str(len(full)) + r""" of the """ + str(len(cov)) + r""" destination jobs. The task-transfer paper will need a longer list and employer information.
\item \textbf{Field team is 4 enumerators} in the worked example (the earlier file used 6).
\end{itemize}

\section*{7. Points still open}
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item \textbf{Timing is untested.} The 12-month calendar and the 25-question Apablaza set are the two blocks most likely to run over their estimate. Time them in the pretest.
\item \textbf{The working-conditions indicator is high in the test data} (""" + cond + r""" in 100 deprived). It is driven by the social-protection route: almost nobody has a pension and most have no health insurance through work. That may well be true of Yatra workers, but check it against the pilot before treating it as a finding.
The cut-off of 2 of 5 gives """ + k2 + r""" in 100 employment-poor; a cut-off of 3 gives """ + k3 + r""".
\item \textbf{Tenure is asked in whole years,} so the paper's under-6-month test for wage workers is not possible; casual jobs supply the variation instead.
\item \textbf{Real quotas.} Occupation quotas must be reset against a real enumeration before fieldwork.
\end{itemize}

\section*{8. The consumption module, read against the three source questionnaires}
Most of the vulnerability-to-poverty papers in the project folder use an existing national survey and report only how consumption was totalled, not the question list itself.
So the three questionnaires were read directly: \textbf{HCES 2022-23} (MoSPI, Appendix A: the source of our poverty line), \textbf{IHDS-II} (the Income and Social Capital Questionnaire, question 14), and the \textbf{Nigeria GHS-Panel} (Wave 3 Household Questionnaire, Sections 10B and 11, the survey behind Eze and Iheonu 2025).
\subsection*{8.1 What each source does}
"""
QS = [("HCES 2022-23 (India)", "A 'modified mixed reference period': 30 days for cereals, pulses, sugar and salt (Sections 5.1-5.3); 7 days for milk, vegetables, fruit, meat/fish/egg, oil, spices and processed food eaten out (Sections 6-7); 30 days for fuel, toiletries, conveyance, phone and rent (Sections 8-11); 365 days for clothing, footwear, education, hospitalisation and durables (Sections 10, 13-14); 30 days for non-hospitalisation medical (Section 10.3). Insurance is not part of consumption."),
      ("IHDS-II (India)", "A flatter design: 30 days for all 33 food and routine items together (questions 14.1-14.33, including phone, transport and non-hospitalisation medical); 365 days for 19 further items (14.34-14.52: hospitalisation, education, clothing, footwear, durables, and also insurance premiums and vacations, which it counts as consumption)."),
      ("Nigeria GHS-Panel Wave 3", "Four recall tiers: 7 days for food and a short non-food list (tobacco, newspapers, transport); 30 days for fuel, electricity, toiletries, phone/internet, rent; 6 months for clothing, footwear and small household items (shorter than the two India surveys); 12 months for durables, insurance and ceremonies.")]
rows = [[esc(a), esc(b)] for a, b in QS]
tex += table(rows, "\\textbf{Source} & \\textbf{Recall design}", "p{3.6cm}p{13.6cm}")
tex += r"""
\subsection*{8.2 Where the three sources agree, and where they do not}
\begin{itemize}[leftmargin=1.2em,itemsep=2pt]
\item \textbf{All three agree on 30 days} for fuel and light, toiletries and household consumables, transport and phone charges, and rent.
\item \textbf{All three agree on 12 months} for durable goods (furniture, utensils, appliances).
\item \textbf{HCES and IHDS-II agree exactly} on splitting medical spending into non-hospitalisation (30 days) and hospitalisation (365 days), and on 365 days for clothing, footwear and education. The Nigeria survey instead asks one combined 6-month medical item, and 6 months (not 12) for clothing.
\item \textbf{HCES and IHDS-II disagree on food.} HCES uses 7 days for perishables (milk, vegetables, fruit, meat, oil, spices) to limit recall decay on frequent purchases; IHDS-II asks the same items at 30 days, in one simpler module. The Nigeria survey uses 7 days for all food.
\item \textbf{Only IHDS-II and the Nigeria survey treat insurance premiums as consumption.} HCES does not, which matches standard national-accounts practice (insurance is a financial item). We follow HCES: our insurance question sits in Module G, not in the consumption total.
\item \textbf{HCES and IHDS-II record the source of each food item} (purchased, home-grown, gift) as a column against every single item. That needs far more interview time than we have, so, following Calvo and Dercon (2007) and Eze and Iheonu (2025), home-grown and gifted food is asked as one aggregate question instead.
\end{itemize}
\subsection*{8.3 Our final choice, and why}
We follow \textbf{HCES 2022-23} for which items get a short recall and which get a 365-day recall (staples, fuel, toiletries, transport, rent and non-hospital medical at a routine recall; clothing, education, hospital and durables at 365 days), because HCES is also the source of our poverty line (Sethu et al. 2024). Within the routine group we do not copy HCES's actual-recall design (its 7-day window for perishables, versus 30 days for staples): our workers are migrants, so the bigger source of error is location and season, not recall decay on one item. Every routine item is instead asked as a usual monthly amount, once for the Yatra season and once for the off-season (section 6), which a single actual-recall question cannot give. Every item in Module E of this questionnaire (section 3) carries its exact source citation.
\subsection*{8.4 Other papers in the folder}
"""
CR = [("Calvo and Dercon 2007 (Ethiopia)", "Total value of food and non-food consumption, from purchases, own harvest and gifts.", "Source for asking home-grown and gifted food as one aggregate question."),
      ("Dercon and Krishnan 2000 (Ethiopia)", "Monthly consumption: food plus a deliberately narrow non-food list, to avoid seasonal swings from large expenditures.", "Source of the narrow (30-day only) consumption measure kept as a robustness check."),
      ("Azeem et al. 2016 (Punjab, MICS)", "Quantities of foods consumed and monetary non-food spending, valued at weekly prices.", "We ask values, not quantities, to keep the interview short."),
      ("Azeem et al. 2018 (Pakistan); Awuni et al. 2023 (Ghana)", "Food intake converted to an adult-equivalent basis (Claro et al. 2010 scale).", "Source of the adult-equivalent consumption measure kept as a robustness check; needs the count of children under 15."),
      ("Lyons et al. 2023 (VASyR, Lebanon)", "A short expenditure module (food total, rent, water, income) run at national scale.", "Shows a short module of this kind can work in the field."),
      ("Khosla and Jena 2022; Jha et al. 2018 (rural India, using IHDS/NSS)", "Monthly per capita consumption expenditure; item list not given in the paper (the source survey was read directly instead).", "Confirms the outcome variable is per-capita monthly consumption."),
      ("Ding 2022; Wei et al. 2023; Ceesay and Morelli 2026", "Income-based, or income and consumption used interchangeably, in small samples.", "Not comparable; we keep consumption, not income, as the welfare measure."),
      ("Zheng and Ma 2023 (China, CLES)", "Ten food groups counted over the reference week, for dietary diversity, not value.", "Not used; our aim is a value-based poverty line, not a diet-diversity score.")]
rows = [[esc(a), esc(b), esc(c)] for a, b, c in CR]
tex += table(rows, "\\textbf{Source} & \\textbf{Consumption measure} & \\textbf{Use in our list}", "p{3.6cm}p{7.6cm}p{5.1cm}")
tex += r"""
\section*{9. Code lists}
"""
rows = [["\\texttt{" + esc(k) + "}", esc("; ".join(f"{c} {v}" for c, v in v_.items()))] for k, v_ in LSETS.items()]
tex += table(rows, "\\textbf{List} & \\textbf{Codes}", "p{2cm}p{14cm}")
tex += "\\end{document}\n"
out = os.path.join(HERE, "Kedarnath_final_questionnaire.tex")
open(out, "w", encoding="utf-8").write(tex)
print(compile_tex(out))
print("asked", len(asked), "constructed", len(cons), "coverage full", len(full), "of", len(cov))
