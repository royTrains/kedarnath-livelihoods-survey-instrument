"""One-off: updates build_questionnaire.py text for v2 (calendar, Apablaza mapping, consumption review)."""
s = open("build_questionnaire.py", encoding="utf-8").read()
i0 = s.index('tex += r"""\n\\section*{5. What changed')
i1 = s.index('\\section*{7. Code lists}')
NEW = r'''tex += r"""
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
\item \textbf{Food is asked in three parts} (bought, home-grown or in-kind, eaten outside or given by an employer), following the components in the consumption reviews in section 8. The three add up to the earlier food total, so all consumption results are unchanged.
\item \textbf{One medical-spending question.} The earlier draft asked medical spending twice (in the consumption list and as out-of-pocket spending) and the two answers did not agree; only the consumption-list item is kept.
\item \textbf{Two new consumption variables for robustness:} a narrow measure (30-day items only, as in Dercon and Krishnan 2000) and a per-adult-equivalent measure (needs the count of children under 15, now asked).
\item \textbf{Four opinion questions on a 1 to 5 scale were removed}, in line with the no-rating rule. Only the three-way ropeway view remains.
\item \textbf{Dropped for length:} remittance frequency and \texttt{prev\_offseason\_work}. The season start, end and length, and the main off-season activity, are now built from the calendar instead of being asked.
\item \textbf{Added:} sex, social group, earners, children under 15 and school-age children, the way the household coped with a shock, direct exposure to the trek, and the Apablaza questions.
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

\section*{8. The consumption list against the Chaudhuri-framework literature}
I read the data sections of the vulnerability-to-poverty papers in the project folder. Most use an existing national survey and report only how consumption was totalled, not the question list.
The item lists themselves are in the source questionnaires (HCES, IHDS, Nigeria GHS-Panel), which are not in the folder. What the papers do show:
"""
CR = [("Sethu et al. 2024 (India, HCES 2022-23)", "Quantity and value for a list of items; a modified mixed reference period (7, 30 and 365 days); food, essential non-food and other non-food groups.", "Our list follows the mixed-period logic: 30 days for frequent items, 12 months for infrequent ones."),
      ("Eze and Iheonu 2025 (Nigeria GHS-Panel)", "Seven components: purchased food; non-purchased food (own production, gifts); meals outside the home; schooling; health care; housing; other non-food (transport, fuel, electricity, household items, clothing).", "The food split follows this list. Our transport is inside routine goods."),
      ("Calvo and Dercon 2007 (Ethiopia)", "Total value of food and non-food consumption, from purchases, own harvest and gifts, deflated by a local food price index.", "Home-grown and gifted food is asked separately."),
      ("Dercon and Krishnan 2000 (Ethiopia)", "Monthly consumption in each round: food plus a deliberately narrow non-food list, to avoid seasonal swings from large expenditures.", "The source of the narrow measure we add as a robustness check."),
      ("Azeem et al. 2016 (Punjab, MICS)", "Quantities of foods consumed and monetary non-food spending; foods valued with weekly prices; total = food + non-food.", "We ask values, not quantities, to keep the interview short."),
      ("Azeem et al. 2018 (Pakistan)", "Food intake converted to kilocalories per adult equivalent per day (adult-equivalent scale from Claro et al. 2010).", "Adult-equivalent version added; needs children under 15."),
      ("Awuni et al. 2023 (Ghana panel)", "Per adult-equivalent consumption expenditure against adjusted national poverty lines.", "Same reason."),
      ("Lyons et al. 2023 (VASyR, Lebanon)", "Total monthly expenditure per person against a survival minimum basket (food quantities plus non-food items, one month). The 2025 file in the folder holds total food expenditure, monthly rent, water payments and 30-day income.", "Shows a short expenditure module can work at scale."),
      ("Khosla and Jena 2022 (IHDS); Jha et al. 2018 (rural India)", "Monthly per capita consumption expenditure; item list not reported in the papers.", "Confirms the outcome is per-capita monthly consumption."),
      ("Ding 2022; Wei et al. 2023; Ceesay and Morelli 2026", "Income-based or income and consumption used interchangeably in small samples.", "Not comparable; we keep consumption as the outcome."),
      ("Zheng and Ma 2023 (China)", "Ten food groups in the reference week, for dietary diversity, not for value.", "A food-group count could be added later if diet is a topic; it is not in this list.")]
rows = [[esc(a), esc(b), esc(c)] for a, b, c in CR]
tex += table(rows, "\\textbf{Source} & \\textbf{Consumption measure} & \\textbf{Use in our list}", "p{3.6cm}p{7.6cm}p{5.1cm}")
tex += r"""
\textbf{Not yet done.} To see the actual item lists, the HCES 2022-23, IHDS-II and Nigeria GHS-Panel questionnaires should be read directly; then the grouping used here can be compared item by item.

\section*{9. Code lists}'''
s = s[:i0] + NEW + "\n" + s[i1 + len("\\section*{7. Code lists}"):]
# need DD (final data) loaded near the top
s = s.replace("asked = [r for r in ROWS", "import warnings; warnings.filterwarnings('ignore')\nDD = pd.read_stata(os.path.join(HERE, '..', 'data', 'kedarnath_final_n200_full.dta'), convert_categoricals=False)\nasked = [r for r in ROWS", 1)
open("build_questionnaire.py", "w", encoding="utf-8").write(s)
print("patched")
