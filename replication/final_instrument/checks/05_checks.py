"""Step 3: independent sanity checks on the Stata-built file (pandas)."""
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "questionnaire"))
from dictionary import ROWS
F = os.path.join(HERE, "..", "data", "kedarnath_final_n200_full.dta")
r = pd.io.stata.StataReader(F); d = r.read(convert_categoricals=False); lab = r.variable_labels(); vl = r.value_labels()
out = []
def rep(s): print(s); out.append(s)

rep(f"Rows {len(d)}, variables {d.shape[1]}; dictionary variables {len(ROWS)}")
rep("Every dictionary variable is in the file, in dictionary order: " + str(list(d.columns) == [x["name"] for x in ROWS]))
rep("Variables without a label: " + str([c for c in d.columns if not lab.get(c)]))
need = sorted({x["lset"] for x in ROWS if x["lset"]}); rep(f"Value-label sets defined: {len(vl)} of {len(need)} expected")

rep("Missing counts for always-asked variables (should be empty): " +
    str({c: int(d[c].isna().sum()) for c in [x['name'] for x in ROWS if x['origin'] == 'asked' and not x['skip']] if d[c].isna().sum() > 0}))

rep("Poverty and employment quality: poor %.2f, poor(sensitivity) %.2f, employment-poor (2 of 5) %.2f" % (
    d.poor.mean(), d.poor_sensitivity_cpi.mean(), d.emp_poor_k2.mean()))
rep("Consumption: cons_pc_pm mean %.0f (narrow %.0f, adult-equiv %.0f); income_seasonality_cv mean %.2f" % (
    d.cons_pc_pm.mean(), d.cons_pc_pm_narrow.mean(), d.cons_pc_ae_pm.mean(), d.income_seasonality_cv.mean()))

rep("On/off-season consumption ratio (off-season usual month / Yatra-season usual month), by item:")
for v in ["staples", "perishables", "food_own", "food_out", "fuel", "routine_misc", "transport_comm", "rent", "med_nonhosp"]:
    ratio = (d[f"cons_{v}_offseason_pm"] / d[f"cons_{v}_yatra_pm"].replace(0, np.nan)).mean()
    rep(f"  {v}: {ratio:.2f}")
rep("Off-season food_own > Yatra-season food_own (expected mainly for farming/animal-husbandry off-season workers): %.0f%% of respondents" %
    (100 * (d.cons_food_own_offseason_pm > d.cons_food_own_yatra_pm).mean()))
rep("Off-season rent near zero for non-local migrants: mean off-season rent, local origin=%.0f, non-local origin=%.0f" % (
    d.loc[d.origin == 1, "cons_rent_offseason_pm"].mean(), d.loc[d.origin > 1, "cons_rent_offseason_pm"].mean()))

rep("Remittances: mean annual outward Rs %.0f, inward Rs %.0f; outward Yatra-season share of annual %.2f" % (
    d.remittance_outward_annual.mean(), d.remittance_inward_annual.mean(),
    (d.remit_out_yatra_pm * d.yatra_months / d.remittance_outward_annual.replace(0, np.nan)).mean()))

rep("Employment deprivation rates (share): " + str({c: round(float(d[c].mean()), 2) for c in ["emp_dep_access", "emp_dep_comp", "emp_dep_sec", "emp_dep_stab", "emp_dep_cond"]}))

rep("Food security (VASyR/Lyons et al. 2023-style rCSI): mean rCSI %.1f, food_coping_deprived (rCSI>20) %.2f; "
    "unmet health-care need (3m) %.2f" % (
    d.rcsi_score.mean(), d.food_coping_deprived.mean(), d.health_access_barrier_3m.mean()))
rep("Education: knows exact years %.2f; mean years_schooling (of those who know) %.1f; education_level_cat used for %d respondents" % (
    d.knows_years_schooling.mean(), d.years_schooling.mean(), int((d.knows_years_schooling==0).sum())))
_has = d.n_other_activities > 0
rep("Multiple work-holding: %.2f hold at least one other activity; mean count among them %.2f (max %d); mean income Rs %.0f/mo; ticked-vs-stated mismatch %.3f" % (
    _has.mean(), d.loc[_has, "n_other_activities"].mean(), int(d.n_other_activities.max()),
    d.loc[_has, "other_activity_income_pm"].mean(), d.other_act_mismatch.mean()))
rep("Ex-ante skill-move direction (Nawakitphaitoon & Ormiston asymmetry): %s; mean coverage %.2f, mean retention %.2f" % (
    d.skill_move_type.value_counts().sort_index().to_dict(), d.task_cover_best.mean(), d.task_retain_best.mean()))
rep("Productive assets (mean count of 6, and migration referral distribution): count %.2f; referral %s" % (
    d.productive_assets_count.mean(), d.loc[d.migrant==1,'migration_referral'].value_counts().sort_index().to_dict()))
rep(f"Employment-poor count distribution: {d.emp_dep_count.value_counts().sort_index().to_dict()}")

rep("Interview minutes: not simulated -- measured from Kobo start/end at the pretest")
rep("Max interviews per enumerator per day: " + str(pd.crosstab(d.enum_id, d.interview_date).values.max()))
rep(f"Tasks: mean regular {d.tk_regular_n.mean():.1f} of 12, mean done-before {d.tk_prior_n.mean():.1f}; trek_dependent share {d.trek_dependent.mean():.2f}")
rep("Asked items with a skip rule: %d of %d asked" % (sum(1 for x in ROWS if x['origin'] == 'asked' and x['skip']), sum(1 for x in ROWS if x['origin'] == 'asked')))

open(os.path.join(HERE, "check_report.txt"), "w", encoding="utf-8").write("\n".join(out))
