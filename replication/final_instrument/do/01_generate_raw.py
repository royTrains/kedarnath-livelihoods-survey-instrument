"""Step 1: build the worked-example RAW file (only what the questionnaire asks or records, as numeric codes).
Starts from the existing synthetic pool (replication/kedarnath_synthetic_v2_n200_retention_flag.dta) so all earlier draws
(monthly calendar, consumption totals, assets, health, shocks) are kept exactly. The food total is split into the three
questionnaire items; the Apablaza-based job-quality answers, the driving-experience items and a few household counts are drawn
new, with their own seed. Task answers come from tasks_module (same 200 respondents). Constructed variables are NOT made
here: Stata does that in 02_build_final_dataset.do."""
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "questionnaire"))
from dictionary import ROWS, LSETS, TASKS

d = pd.read_stata(os.path.join(ROOT, "replication", "kedarnath_synthetic_v2_n200_retention_flag.dta"))
t = pd.read_csv(os.path.join(ROOT, "tasks_module", "02_data", "tasks_synth_full.csv"))
assert (d.resp_id.values == t.resp_id.values).all()
n = len(d)
rng = np.random.default_rng(20260921 + 12)
expit = lambda x: 1 / (1 + np.exp(-x))

def code(series, mapping):
    out = []
    for v in series.astype(str):
        v = v.strip(); hit = np.nan
        for k, c in mapping.items():
            if v.startswith(k) and v != "":
                hit = c; break
        out.append(hit)
    return np.array(out, dtype=float)

o = pd.DataFrame(index=d.index)
o["resp_id"] = d.resp_id
# ---- P: paradata ---------------------------------------------------------
o["enum_id"] = rng.permutation(np.repeat([1, 2, 3, 4], n // 4))
day = np.zeros(n, int)
for e in (1, 2, 3, 4):
    idx = np.where(o.enum_id == e)[0]
    day[idx] = np.arange(len(idx)) // 5          # about 5 interviews per enumerator per day
o["interview_date"] = (pd.Timestamp("2026-06-15") + pd.to_timedelta(day, unit="D")).strftime("%Y-%m-%d")
# location_cluster dropped 2026-09-24: the GPS below already carries the site, and health_access_tier
# is now banded from gps_lat in Stata rather than from a hand-coded cluster.
o["gps_lat"] = d.gps_lat.round(5); o["gps_lon"] = d.gps_lon.round(5)
o["consent"] = 1

# ---- A ------------------------------------------------------------------------
o["age"] = d.age
# remapped 2026-09-24 to the NCO-rebuilt 14-group list. The old synthetic pool has no
# dhaba/food-stall WORKER (the old list had no such code), so a share of the food-stall owners is
# reassigned to it -- otherwise the newly added category would never be exercised by the pipeline.
occ = code(d.occupation, {"Pony worker": 1, "Pony business": 2, "Porter": 3, "Palki": 4, "Shopkeeper": 7, "Shop owner": 8,
                          "Hotel/lodging worker": 9, "Hotel/lodging owner": 10, "Wage labourer": 13, "Driver": 11,
                          "Dhaba": 6, "Guide": 12, "Other": 14}).astype(int)
occ = np.where((occ == 6) & (rng.random(n) < 0.45), 5, occ)
FEM = {1: 0, 2: .01, 3: .01, 4: 0, 5: .20, 6: .20, 7: .05, 8: .08, 9: .15, 10: .10, 11: 0, 12: .02, 13: .10, 14: .15}
o["female"] = (rng.random(n) < np.array([FEM[k] for k in occ])).astype(int)
# hoh_relation now carries the head's SEX in the category itself (husband/wife, father/mother,
# son/daughter, brother/sister), so no separate male/female question is asked; Stata derives
# hoh_female from this. Codes: 1 self, 2 husband, 3 wife, 4 father, 5 mother, 6 son, 7 daughter,
# 8 brother, 9 sister, 10/11 other male/female relative, 12/13 non-relative male/female.
o["hoh_relation"] = rng.choice(range(1, 14), size=n,
    p=[.550, .100, .005, .150, .020, .020, .005, .080, .005, .040, .010, .010, .005])
orig = code(d.origin, {"Local": 1, "Other Uttarakhand": 2, "Other Indian": 3, "Nepal": 4})
# native language follows origin: locals mostly Garhwali, other-Uttarakhand a Garhwali/Kumaoni/Hindi mix,
# other-Indian-state migrants mostly Hindi/Bhojpuri-Maithili/Bengali, Nepal migrants mostly Nepali
LANG_P = {1: ([1, 2, 3], [.88, .02, .10]), 2: ([1, 2, 3], [.35, .40, .25]),
          3: ([3, 5, 14, 7, 96], [.40, .25, .10, .10, .15]), 4: ([4, 3], [.95, .05])}
nlang = np.zeros(n, int)
for o_code, (vals, p_) in LANG_P.items():
    idx = orig == o_code
    nlang[idx] = rng.choice(vals, size=idx.sum(), p=p_)
o["native_language"] = nlang
# free-text write-in, asked only when the list did not hold their language
OTHER_LANGS = ["Kumaoni-Jaunsari mix", "Awadhi", "Magahi", "Chhattisgarhi", "Haryanvi", "Marwari",
               "Tharu", "Doteli", "Tibetan", "Bhotiya"]
o["native_language_other"] = [str(rng.choice(OTHER_LANGS)) if v in (96, 97) else "" for v in nlang]
# home state/UT: locals and other-Uttarakhand code to Uttarakhand (27); other-Indian-state migrants
# draw from the states that actually supply labour to this route; Nepal codes to "Outside India" (99)
MIG_STATES = ([26, 4, 28, 10, 13, 21, 19], [.42, .26, .09, .08, .06, .05, .04])
hstate = np.full(n, 27)
_m = orig == 3
hstate[_m] = rng.choice(MIG_STATES[0], size=_m.sum(), p=MIG_STATES[1])
hstate[orig == 4] = 99
o["home_state"] = hstate
# rural/urban of the USUAL home -- decides which poverty line applies to this respondent, and now
# ASKED rather than derived from a village/town/city tier the respondent could not reliably classify
o["home_rural_urban"] = rng.choice([1, 2], n, p=[.81, .19])
o["marital_status"] = code(d.marital_status, {"Currently": 1, "Never": 2, "Widowed": 3})
# education: ask years directly; only respondents who can't recall an exact number get a fallback
# bracket. true_years/prefer_not come straight from the old pool's own already-built education_years
# (documented there as "missing for 98" -- i.e. missing exactly for "prefer not to say").
true_years = d.education_years.values.astype(float)
prefer_not = np.isnan(true_years)
knows_years = (rng.random(n) < 0.85) & ~prefer_not
o["knows_years_schooling"] = np.where(prefer_not, 0, knows_years.astype(int))
o["years_schooling"] = np.where(knows_years, np.round(true_years), np.nan)
edu_bracket = np.select([true_years < 1, true_years < 5, true_years < 10], [1, 2, 3], default=4)
o["education_level_cat"] = np.where(prefer_not, 98, np.where(knows_years, np.nan, edu_bracket))
o["hhsize"] = d.hhsize
# NITI's Years of Schooling is a HOUSEHOLD indicator: has ANY member aged 10+ finished 6 years?
# More likely true than the respondent's own schooling, since it takes only one educated member.
_p_any6 = expit(0.55 + 0.30 * (np.nan_to_num(true_years, nan=4.0) - 5) + 0.22 * (d.hhsize.values - 4))
o["any_member_6yr_schooling"] = (rng.random(n) < np.clip(_p_any6, .04, .985)).astype(int)
fam = np.where(d.hhsize.values == 1, 3, rng.choice([1, 2], size=n, p=[.58, .42]))
o["family_structure"] = fam
n_earn = np.minimum(1 + rng.poisson(0.7, n), d.hhsize.values)
o["n_earners"] = n_earn
# main income earner: automatic =1 if the respondent is the only earner; otherwise a coin flip
# weighted slightly toward the respondent (they are the one being interviewed at the worksite)
# blank when the respondent is the only earner -- the form hides the question there (a sole earner is
# the main earner by definition), so Kobo returns an empty cell and Stata fills it. Same reasoning as
# hoh_female above: the raw file must match what the form can actually produce.
o["main_income_earner"] = np.where(n_earn > 1, (rng.random(n) < 0.55).astype(float), np.nan)
lam = np.where((o.marital_status == 1) & (d.age.between(27, 50)), 1.0, 0.15)
n_u15 = np.minimum(d.hhsize.values - 1, rng.poisson(lam))
o["n_children_u15"] = n_u15
n_6_14 = rng.binomial(n_u15, 0.55)
o["n_children_6_14"] = n_6_14
o["n_children_out_school"] = np.where(n_6_14 > 0, rng.binomial(n_6_14, 0.05 + 0.10 * d.poor.values), np.nan)

# ---- B ------------------------------------------------------------------------
o["occupation"] = occ
# verbatim description of the real job -- the coarse group above cannot carry it
OCC_TEXT = {1: ["doosre ka ghoda chalata hoon", "ghoda hankta hoon, malik ka hai"],
            2: ["apne 3 ghode kiraye pe dete hain", "khachar ke malik hain, 5 janwar"],
            3: ["yatriyon ka saman upar le jata hoon", "pith par saman dhota hoon"],
            4: ["dandi uthata hoon", "palki mein buzurg yatri le jate hain"],
            5: ["dhabe mein roti banata hoon", "chai ki dukan par kaam karta hoon"],
            6: ["apna chai-pakoda ka khokha hai", "dhaba chalata hoon, khana banate hain"],
            7: ["prasad ki dukan par baithta hoon", "kambal-jacket ki dukan mein kaam"],
            8: ["apni puja saman ki dukan hai", "parchoon ki dukan, apni hai"],
            9: ["lodge mein kamre saaf karta hoon", "hotel mein helper hoon"],
            10: ["apna 8 kamre ka lodge hai", "guest house ka malik hoon"],
            11: ["jeep chalata hoon Sonprayag tak", "taxi driver hoon"],
            12: ["yatriyon ko mandir aur rasta dikhata hoon", "guide ka kaam"],
            13: ["dihadi par jo mile", "construction mein mazdoori"],
            14: ["photo khichta hoon yatriyon ki", "mobile recharge aur photocopy"]}
o["occupation_detail"] = [str(rng.choice(OCC_TEXT[int(k)])) for k in occ]
o["employment_type"] = code(d.employment_type, {"Self-employed - own": 1, "Self-employed - employer": 2, "Regular": 3, "Casual": 4})
et = o.employment_type.values.astype(int)
o["years_in_yatra_work"] = d.years_in_yatra_work
# hours asked as hours/day x days/week (decomposed, easier to recall than one weekly figure);
# hours_week_yatra is built from these two in Stata
HRS = {1: 11, 2: 11, 3: 10, 4: 10, 5: 12, 6: 13, 7: 12, 8: 13, 9: 11, 10: 13, 11: 10, 12: 9, 13: 9, 14: 10}
hours_day = np.clip(np.round(rng.normal([HRS[k] for k in occ], 1.3)), 6, 16).astype(int)
owner = np.isin(occ, [2, 6, 8, 10])
days_week = np.where(owner, rng.choice([6, 7], n, p=[.25, .75]), rng.choice([5, 6, 7], n, p=[.10, .60, .30]))
o["hours_day_yatra"] = hours_day; o["days_week_yatra"] = days_week
# secondary work: recorded directly (what the other work is, "none" if there isn't one), not via a
# preliminary yes/no gate. More common among business owners (e.g. a shop owner who also rents out a
# pony) -- undercounted by the single main-occupation code. Income asked right after, when present.
# Multiple work-holding: a COUNT first, then a check-all list (the old version allowed exactly one
# other activity, which undercounts a shop owner who also rents a pony and drives in the off-season).
# Owners hold more activities than workers. The count is drawn first and the list is sampled to match
# it, so the two agree by construction here; in real data they need not, which is why the Stata build
# flags mismatches rather than assuming consistency.
_lam = np.where(owner, 0.75, 0.40)
n_other = rng.poisson(_lam, n).clip(0, 6)
o["n_other_activities"] = n_other
_types = []
for i in range(n):
    if n_other[i] == 0:
        _types.append("")
        continue
    pool = [k for k in range(1, 15) if k != occ[i]]
    pick = rng.choice(pool, size=min(n_other[i], len(pool)), replace=False)
    _types.append(" ".join(str(int(v)) for v in sorted(pick)))   # Kobo's space-separated export
o["other_activity_types"] = _types
# income scales with how many activities are held, but sub-linearly (the extra ones are smaller)
_sec_income = np.round(rng.gamma(2.0, 800, n) * np.sqrt(np.maximum(n_other, 1)) / 50) * 50
o["other_activity_income_pm"] = np.where(n_other > 0, _sec_income, np.nan)

o["prev_occ_change"] = d.prev_occ_change
PO_CODE = {"Pony worker": 1, "Pony business": 2, "Porter": 3, "Palki": 4, "Shopkeeper": 7, "Shop owner": 8,
           "Hotel/lodging worker": 9, "Hotel/lodging owner": 10, "Wage labourer": 13, "Driver": 11,
           "Dhaba/food-stall owner": 6, "Guide": 12, "Other": 14}
# prev_occ and target_occ are now FREE TEXT, office-coded to NCO-2015 afterwards. The synthetic
# version writes plausible verbatim strings rather than codes, so the pipeline is exercised the way
# the real one will be: the raw file carries text, and nothing downstream may assume a numeric code.
PHRASE = {1: "pony wala", 2: "rented out ponies", 3: "porter, carried loads", 4: "palki carrying",
          5: "dhabe mein kaam karta tha", 6: "chai ki dukan chalayi", 7: "dukan par kaam karta tha",
          8: "apni dukan thi", 9: "hotel mein kaam", 10: "lodge chalaya", 11: "gaadi chalayi",
          12: "guide ka kaam", 13: "dihadi mazdoori", 14: "farming at home"}
# a slice of previous work sits OUTSIDE the 13 Yatra groups -- which is the whole reason this is text
OUTSIDE = ["farming on own land", "construction labour in Dehradun", "army, then retired",
           "shop work in Delhi", "driving a tempo in Rishikesh", "worked in a factory in Punjab"]
_prev = []
for i in range(n):
    if d.prev_occ_change.iloc[i] != 1:
        _prev.append("")
    elif rng.random() < 0.30:
        _prev.append(str(rng.choice(OUTSIDE)))
    else:
        _prev.append(PHRASE[int(t.prev_occ_borrowed_from.map(PO_CODE).iloc[i])])
o["prev_occ"] = _prev
# stated target if this work ended. "Don't know" and "nothing" are substantive answers, not missing.
TARGETS = ["farming at home", "daily wage labour", "drive a jeep or taxi", "open a small shop",
           "hotel or dhaba work", "construction labour", "go back to the village", "work on the ropeway",
           "portering somewhere else", "don't know", "there is no other work for me"]
o["target_occ"] = [str(rng.choice(TARGETS, p=[.13, .16, .09, .10, .09, .08, .07, .06, .05, .10, .07]))
                   for _ in range(n)]
mig = (orig > 1)
reason = np.where(d.prev_occ_change == 1, rng.choice([1, 2, 3, 4, 5], n, p=[.35, .25, .20, .15, .05]), np.nan)
reason = np.where((d.prev_occ_change == 1) & mig & (rng.random(n) < .35), 4, reason)
o["prev_occ_reason"] = reason
o["training_received"] = d.training_received
# training type widened from 2 categories to 9 + write-in: the old pair could not hold driving,
# repair, tailoring or animal handling, which is most of what this workforce actually trains in
_tt_old = code(d.training_type, {"Vocational": 1, "Tourism": 2})
_tt = np.where(_tt_old == 2, 2, rng.choice([1, 3, 4, 5, 6, 7, 8, 9], n, p=[.30, .18, .12, .10, .10, .12, .05, .03]))
TT_OTHER = ["yoga sikhaya", "photography ka course", "band party mein baja"]

# ---- C: monthly calendar (kept exactly from the earlier file) -----------------------------
# "Migrated for work" now maps to 4 (casual wage labour), not 5: code 5 is Construction work since the
# activity list stopped encoding location. A share of casual-wage months is then reassigned to 5 below,
# so the new code is populated -- construction is the commonest off-season destination work here.
ACT = {"Yatra work": 1, "Agriculture": 2, "Animal husbandry": 3, "Wage labour elsewhere": 4, "Migrated for work": 4,
       "Petty trade/other": 6, "Salaried job": 7, "No work": 8}
status = np.zeros((n, 12), int)
for m in range(12):
    status[:, m] = [ACT[v] for v in d[f"status_m{m+1}"].astype(str)]
    _to_constr = (status[:, m] == 4) & (rng.random(n) < 0.34)
    status[_to_constr, m] = 5

# The pool lays every respondent's Yatra block on the same months, so status_m5, m6 and m7 came out
# CONSTANT at 1 and yatra_start_month was 5 for all 200 rows. Nothing then exercised the season
# boundary -- the mid-month start problem, yatra_start_month/yatra_end_month, or the 3-9 month
# data-quality band. Each respondent now gets his own start and end. Activity code 1 covers preparing
# for the season as well as working it, so an owner can start in March; the Yatra itself runs to Bhai
# Dooj, so the close is October or November.
_start = rng.choice([3, 4, 5, 6], n, p=[.08, .27, .46, .19])
_end   = rng.choice([9, 10, 11], n, p=[.31, .44, .25])
_offdist = np.array([2, 3, 4, 5, 6, 7, 8])
_offp = np.array([.17, .07, .19, .11, .13, .05, .28])
for i in range(n):
    for m in range(12):
        inside = _start[i] <= m + 1 <= _end[i]
        if inside:
            status[i, m] = 1
        elif status[i, m] == 1:            # pool said Yatra outside this worker's own season
            status[i, m] = int(rng.choice(_offdist, p=_offp))
for m in range(12):
    o[f"status_m{m+1}"] = status[:, m]
inc = d[[f"income_m{m}" for m in range(1, 13)]].values.astype(float)
months_no_work = (status == 8).sum(1)
yatra_months_v = (status == 1).sum(1)
# off-season hours: asked only of those with any non-Yatra paid month. Shorter and more marginal
# than the season -- which is the whole reason Apablaza's under-20-hours limb needed them.
_off_works = np.array([((status[i] >= 2) & (status[i] <= 7)).any() for i in range(n)])
_hd_off = np.clip(np.round(rng.normal(7.0, 2.6, n)), 2, 14).astype(float)
_dw_off = rng.choice([3, 4, 5, 6, 7], n, p=[.14, .16, .26, .30, .14]).astype(float)
o["hours_day_offseason"] = np.where(_off_works, _hd_off, np.nan)
o["days_week_offseason"] = np.where(_off_works, _dw_off, np.nan)


# ---- C: month-by-month recall vs. the annual-total fallback (Apablaza Q14 -> Q15) --------------
# A respondent who cannot produce twelve separate figures gives one annual total plus the share of
# it that came from Yatra work; Stata reweights that back onto the calendar. Recall is modelled as
# worse for older respondents, those with less schooling, and those whose year is more fragmented
# (more distinct activities = more figures to hold), which is the direction the survey-methods
# literature reports; the coefficients themselves are invented, like everything else in this file.
_n_distinct_act = np.array([len(set(row)) for row in status])
_recall_x = (-0.35 * (d.age.values - 40) / 15
             + 0.30 * (d.education_years.values - 6) / 4
             - 0.45 * (_n_distinct_act - 2))
_p_knows = 1 / (1 + np.exp(-(1.15 + _recall_x)))
knows_monthly = (rng.random(n) < _p_knows).astype(int)
o["knows_monthly_income"] = knows_monthly

# the true underlying annual figures, used both to fill the calendar and to build the fallback
_yatra_true = np.where(status == 1, inc, 0).sum(1)
_other_true = np.where(status != 1, inc, 0).sum(1)
_total_true = _yatra_true + _other_true

for m in range(12):
    # Blank on BOTH skip routes, because that is what Kobo actually returns: the form hides this
    # question when the respondent took the annual-total route (knows_monthly_income = 0) AND when
    # the month was idle (status = 8). A hidden question exports an empty cell, never a zero, so the
    # raw file must be empty in both cases too. Stata fills the idle months with 0 during the build.
    o[f"income_m{m+1}"] = np.where((knows_monthly == 1) & (status[:, m] != 8), inc[:, m], np.nan)

# the fallback pair. Respondents who take it report a rounded total (people answer round numbers to
# a whole-year question) and a Yatra share rounded to the nearest 5 out of 100, with a little noise
# -- so the reconstruction is close to, but not identical with, the calendar truth.
_annual_rep = np.where(_total_true > 0, np.round(_total_true * rng.normal(1.0, 0.07, n) / 500) * 500, 0)
_share_true = np.divide(_yatra_true, _total_true, out=np.full(n, 0.5), where=_total_true > 0)
_share_rep = np.clip(np.round((_share_true * 100 + rng.normal(0, 4, n)) / 5) * 5, 0, 100)
o["income_annual_total"] = np.where(knows_monthly == 0, _annual_rep, np.nan)
o["pct_income_yatra"] = np.where(knows_monthly == 0, _share_rep, np.nan)
# off-season dominant activity, for building plausible on/off-season splits below (mirrors the
# Stata-built offseason_primary, computed here in python since it is not yet available at this stage)
off_counts = np.stack([(status == k).sum(1) for k in range(2, 9)], axis=1)
off_dom = 2 + off_counts.argmax(1)  # ties go to the lower code, matching the Stata tie-break

# ---- C: remittances, split into Yatra-season and off-season usual monthly amounts --------------
# Assumption (not empirical): outward remittances are mostly sent while earning away at the Yatra
# site; inward remittances (family supporting the worker) run a little more off-season. The OLD
# annual totals (d.remittance_outward/inward) are kept as the annual anchor; only the season split
# is new.
out_yatra_share = np.clip(rng.normal(0.72, 0.10, n), 0.4, 0.95)
out_off_months = np.maximum(12 - yatra_months_v, 1)
remit_out_yatra_pm = np.round(d.remittance_outward.values * out_yatra_share / yatra_months_v / 10) * 10
remit_out_off_pm = np.round(d.remittance_outward.values * (1 - out_yatra_share) / out_off_months / 10) * 10
in_yatra_share = np.clip(rng.normal(0.45, 0.10, n), 0.15, 0.75)
remit_in_yatra_pm = np.round(d.remittance_inward.values * in_yatra_share / yatra_months_v / 10) * 10
remit_in_off_pm = np.round(d.remittance_inward.values * (1 - in_yatra_share) / out_off_months / 10) * 10
o["remit_out_yatra_pm"] = remit_out_yatra_pm.astype(int); o["remit_out_offseason_pm"] = remit_out_off_pm.astype(int)
o["remit_in_yatra_pm"] = remit_in_yatra_pm.astype(int); o["remit_mode"] = np.where(
    (remit_out_yatra_pm + remit_out_off_pm) > 0, rng.choice([1, 2, 3, 4, 5, 6], n, p=[.34, .28, .08, .16, .12, .02]), np.nan)
o["remit_in_offseason_pm"] = remit_in_off_pm.astype(int)

# ---- D ------------------------------------------------------------------------
o["origin"] = orig
# closure regime. Proportions follow the pilot's own residency_pattern (n=46): 23 year-round
# resident, 20 seasonal migrant, 3 working here with family elsewhere. Deliberately NOT conditioned
# on origin -- 11 of those 20 seasonal migrants were from this same district, so drawing the closure
# regime from origin would rebuild exactly the error the module was rewritten to remove.
# closure regime, as the two plain binaries that replaced the four-way closure_base. Proportions
# follow the pilot's own residency_pattern (n=46): 23 year-round resident, 20 seasonal migrant, 3
# working here with family elsewhere. Deliberately NOT conditioned on origin -- 11 of those 20
# seasonal migrants were from this same district, so drawing the regime from origin would rebuild
# exactly the error the module was rewritten to remove.
o["resp_returns_at_closure"] = (rng.random(n) < 0.52).astype(int)
_moves = o["resp_returns_at_closure"].values == 1
o["hh_at_home_place"] = (rng.random(n) < 0.26).astype(int)
_split = o["hh_at_home_place"].values == 1
# how many people the on-site figure covers, asked only of split households. Usually the respondent
# alone or with one or two others; never more than the household.
o["n_here_season"] = np.where(_split, np.minimum(1 + rng.poisson(0.7, n), d.hhsize.values), np.nan)

# the absence spell, which replaced twelve loc_m items. The Yatra closes in November and reopens in
# April or May, so the spell straddles the new year and returned < left is the NORMAL case.
_left = np.where(_moves, rng.choice([11, 12, 1], n, p=[.62, .26, .12]), np.nan)
_back = np.where(_moves, rng.choice([3, 4, 5, 6], n, p=[.10, .44, .34, .12]), np.nan)
o["left_here_month"] = _left
o["returned_here_month"] = _back
# months in the spell, wrapping the year the same way Stata does
_span = np.where(_moves, np.mod(_back - _left, 12), 0)
_away = np.where(_moves, (rng.random(n) < .34).astype(int), (rng.random(n) < .06).astype(int))
o["worked_away_in_closure"] = _away
# months of that absence spent working elsewhere rather than at the home place; never more than the
# spell itself, which is the one cross-field rule the form enforces here
o["months_away_for_work"] = np.where(_away == 1,
                                     np.maximum(1, np.minimum(_span, rng.poisson(2.2, n) + 1)), np.nan)
o["years_coming_here"] = np.where(
    _moves, np.minimum(d.years_in_yatra_work.values + rng.poisson(2.0, n),
                       (d.age.values - 14).clip(1)), np.nan)
o["came_here_reason"] = np.where(orig > 1, rng.choice([1, 2, 3, 4, 5, 6, 7, 8], n,
                                 p=[.34, .22, .15, .11, .06, .07, .03, .02]), np.nan)
AWAY_PLACES = ["Delhi mein construction", "Dehradun mein hotel ka kaam", "Punjab mein kheti",
               "Mumbai mein security guard", "Haridwar mein dukan par"]
o["closure_work_detail"] = [str(rng.choice(AWAY_PLACES)) if v == 1 else "" for v in _away]
o["worked_other_places"] = (rng.random(n) < 0.33).astype(int)
OTHER_PLACES = ["Shimla mein dhaba", "Delhi mein factory", "Ludhiana mein mazdoori",
                "Rishikesh mein raft ka kaam", "Nepal mein kheti"]
o["other_places_detail"] = [str(rng.choice(OTHER_PLACES)) if v == 1 else ""
                            for v in o["worked_other_places"].values]
o["would_move_for_work"] = np.where(rng.random(n) < .04, 97, (rng.random(n) < .56).astype(int))
# who placed the respondent in this work. Ungated as of 2026-09-28: it is a question about the
# employment relationship, not about migration, so a local worker gets it too.
REF_P = [.35, .30, .15, .05, .10, .03, .02]   # family / friend-villager / contractor / leader / self / employer / other
o["migration_referral"] = rng.choice([1, 2, 3, 4, 5, 6, 7], size=n, p=REF_P)
REF_OTHER = ["gaon ka pradhan", "mandir samiti ke through", "purane malik ne bheja",
             "sena ke dost ne bataya", "NGO wale ne"]
o["migration_referral_other"] = [str(rng.choice(REF_OTHER)) if v == 7 else "" for v in np.nan_to_num(o.migration_referral.values)]
# years_since_migration dropped: redundant with years_in_yatra_work for this study's purposes

# ---- E: consumption, on/off-season pairs (workers are migrants; see dictionary.py Module E) -----
# The OLD totals (d.cons_food_30d etc.) were originally calibrated as an on-site, Yatra-season figure
# (fieldwork happens in the season), so they are kept as the YATRA-SEASON baseline. Off-season figures
# are the baseline times a factor that is our own assumption (NOT taken from any source survey),
# varying by the worker's off-season activity: lower for purchased/cash items when idle or away with
# no other work, higher for home-grown food when farming or keeping animals, and much lower for rent
# for anyone not local (an owned or rent-free home away from the Yatra site).
food = d.cons_food_30d.values.astype(float)
own_share = np.where(d.land_acres.values > 0, rng.uniform(0.05, 0.25, n), rng.uniform(0, 0.04, n)) + np.where(d.livestock_count.values > 0, rng.uniform(0, 0.08, n), 0)
OUT = {1: .10, 2: .10, 3: .12, 4: .12, 5: .15, 6: .12, 7: .10, 8: .08, 9: .25, 10: .10, 11: .12, 12: .10, 13: .12, 14: .10}
out_share = np.clip(np.array([OUT[k] for k in occ]) + rng.uniform(-.03, .05, n), 0, .45)
own_yatra = np.round(food * own_share / 10) * 10
out_yatra = np.round(food * out_share / 10) * 10
bought = food - own_yatra - out_yatra
assert (bought >= 0.35 * food).all()
staples_share = np.clip(rng.normal(0.32, 0.06, n), 0.15, 0.55)
staples_yatra = np.round(bought * staples_share / 10) * 10
perish_yatra = np.round((bought - staples_yatra) / 5) * 5
transport_share = np.clip(rng.normal(0.38, 0.07, n), 0.15, 0.65)
routine_old = d.cons_routine_misc_30d.values.astype(float)
transport_yatra = np.round(routine_old * transport_share / 5) * 5
routine_yatra = routine_old - transport_yatra
med_old = d.cons_medical_12m.values.astype(float)
hosp_share = np.where(d.hospitalization_365d.values == 1, rng.uniform(0.55, 0.85, n), rng.uniform(0.05, 0.25, n))
med_hosp = np.round(med_old * hosp_share / 50) * 50
med_nonhosp_yatra = np.maximum(np.round((med_old - med_hosp) / 12 / 10) * 10, 0)
o["cons_medical_hosp_12m"] = med_hosp.astype(int)
# worksite subsistence: porters and pony workers are on the route all day and mostly buy food;
# shop, dhaba and lodge OWNERS have premises and mostly cook. PERSONAL spending -- never added
# into cons_pc_pm, which stays household consumption per capita.
_p_cook = np.where(np.isin(occ, [6, 8, 10]), .72, np.where(np.isin(occ, [1, 2, 3, 4]), .28, .46))
_cooks = (rng.random(n) < _p_cook).astype(int)
# cooks_own_meals_here and meal_spend_day_self are gone from the instrument (2026-09-30): the spend
# item never entered any consumption aggregate and duplicated cons_food_out_yatra_pm, and the cooks
# item existed only to gate it. _cooks survives here because packaged-food spending below genuinely
# does depend on whether someone is buying their food on the route.
# HCES S7.2 packaged processed food and S12 pan/tobacco/intoxicants -- both inside the total-MPCE
# concept the poverty line is calibrated on, both previously missing from the aggregate. Packaged
# snacks skew toward workers buying food on the route; pan/tobacco skews male and manual.
_pk_y = np.round(rng.gamma(2.0, 130, n) * np.where(_cooks == 0, 1.35, 1.0) / 10) * 10
o["cons_packaged_food_yatra_pm"] = _pk_y.astype(int)
o["cons_packaged_food_offseason_pm"] = np.round(_pk_y * rng.normal(0.72, 0.10, n) / 10).clip(0) * 10
_uses = (rng.random(n) < np.where(o.female.values == 1, .18, .62))
_pt_y = np.where(_uses, np.round(rng.gamma(2.2, 240, n) / 10) * 10, 0)
o["cons_pan_tobacco_yatra_pm"] = _pt_y.astype(int)
o["cons_pan_tobacco_offseason_pm"] = np.round(_pt_y * rng.normal(0.85, 0.12, n) / 10).clip(0) * 10
for v in ["cons_clothing_12m", "cons_education_12m", "cons_durables_12m"]:
    o[v] = d[v]

# off-season multiplier for purchased/cash items, by off-season dominant activity (assumed, not empirical)
CASH_FACTOR = {2: .75, 3: .70, 4: .90, 5: .85, 6: .80, 7: 1.00, 8: .55}
cash_f = np.clip(np.array([CASH_FACTOR[k] for k in off_dom]) + rng.uniform(-.08, .08, n), 0.20, 1.15)
# off-season multiplier for home-grown/in-kind food: higher when farming or keeping animals off-season
OWN_FACTOR = {2: 1.8, 3: 1.6, 4: 0.6, 5: 0.4, 6: 0.7, 7: 0.6, 8: 1.1}
own_f = np.clip(np.array([OWN_FACTOR[k] for k in off_dom]) + rng.uniform(-.15, .15, n), 0.2, 2.5)
# off-season rent: near zero for a non-local migrant (an owned or rent-free home elsewhere)
rent_f = np.where(orig > 1, rng.uniform(0.0, 0.15, n), rng.uniform(0.4, 0.9, n))

def season_pair(name, yatra_vals, factor, rnd=10):
    off = np.maximum(np.round(yatra_vals * factor / rnd) * rnd, 0)
    o[name + "_yatra_pm"] = yatra_vals.astype(int)
    o[name + "_offseason_pm"] = off.astype(int)

season_pair("cons_staples", staples_yatra, cash_f)
season_pair("cons_perishables", perish_yatra, cash_f, rnd=5)
season_pair("cons_food_own", own_yatra, own_f)
season_pair("cons_food_out", out_yatra, cash_f, rnd=5)
season_pair("cons_fuel", d.cons_fuel_30d.values.astype(float), cash_f)
season_pair("cons_routine_misc", routine_yatra, cash_f, rnd=5)
season_pair("cons_transport_comm", transport_yatra, cash_f, rnd=5)
season_pair("cons_rent", d.cons_rent_30d.values.astype(float), rent_f)
season_pair("cons_med_nonhosp", med_nonhosp_yatra, cash_f)

# most migrant households DO spend differently across the two seasons; the gate exists for the
# minority who do not, and the take-up rate is exactly what the pilot needs to check
_differs = (rng.random(n) < 0.82).astype(int)
o["spend_differs_by_season"] = _differs
for _c in ["staples","perishables","food_own","food_out","packaged_food","pan_tobacco","fuel",
           "routine_misc","transport_comm","rent","med_nonhosp"]:
    _col = f"cons_{_c}_offseason_pm"
    if _col in o: o[_col] = np.where(_differs == 1, o[_col].values, np.nan)

# ---- F ------------------------------------------------------------------------
o["floor_material"] = code(d.floor_material, {"Mud": 1, "Cement": 2, "Tile": 3})
o["roof_material"] = code(d.roof_material, {"Thatch": 1, "Tin": 2, "Concrete": 3})
o["electricity"] = d.electricity
# toilet: the old pool holds only an own-toilet yes/no. NITI needs improved-vs-unimproved AND
# shared-vs-not, so the binary is expanded: "has a toilet" splits into improved-unshared and
# improved-shared, "no toilet" into open defecation and an unimproved pit.
_t = d.toilet_facility.values.astype(int)
o["toilet_type"] = np.where(_t == 1, rng.choice([3, 4], n, p=[.22, .78]),
                            rng.choice([1, 2], n, p=[.45, .55]))
# wall material was never asked before; it tracks house_type closely but not perfectly
_ht = code(d.house_type, {"Kaccha": 1, "Semi": 2, "Pucca": 3}).astype(int)
o["wall_material"] = np.where(_ht == 1, rng.choice([1, 2], n, p=[.72, .28]),
                     np.where(_ht == 2, rng.choice([1, 2, 3], n, p=[.18, .52, .30]),
                              rng.choice([2, 3], n, p=[.14, .86])))
# WATER: the old pool holds only a 3-way source code, so it is expanded into the JMP/NFHS taxonomy
# the NITI MPI indicator actually needs. Piped splits into in-house vs public standpipe; handpump
# carries over; the old catch-all "Other" splits across protected/unprotected/surface/tanker.
_w_old = code(d.drinking_water, {"Piped": 1, "Handpump": 2, "Other": 3})
_w = np.where(_w_old == 1, rng.choice([1, 2], n, p=[.62, .38]),
     np.where(_w_old == 2, 3,
              rng.choice([4, 5, 7, 8, 9], n, p=[.30, .06, .26, .30, .08])))
o["drinking_water"] = _w
# on-premises is near-certain for in-house piping and rare for surface sources
_p_prem = np.select([_w == 1, np.isin(_w, [3, 5, 6]), np.isin(_w, [2, 4])], [.97, .55, .18], default=.06)
_on_prem = (rng.random(n) < _p_prem).astype(int)
o["water_on_premises"] = _on_prem
# round-trip minutes, heavier-tailed for unimproved sources; NITI's threshold is 30
_mins = np.where(np.isin(_w, [7, 8, 9]), rng.gamma(3.0, 12, n), rng.gamma(2.2, 7, n))
o["water_fetch_minutes"] = np.where(_on_prem == 0, np.round(_mins).clip(2, 180), np.nan)

# COOKING FUEL: the old pool holds only an LPG yes/no, so non-LPG is spread over the dirty fuels
# NITI names (and a little clean electricity/biogas, which the old binary wrongly called deprived).
_lpg = d.cooking_fuel_lpg.values.astype(int)
o["cooking_fuel"] = np.where(_lpg == 1, 1,
                             rng.choice([3, 4, 5, 6, 7, 8], n, p=[.04, .05, .06, .62, .15, .08]))

for v in ["owns_tv", "owns_radio", "owns_bicycle", "owns_motorcycle", "owns_car", "owns_fridge"]:
    o[v] = d[v]
# land is now explicitly CULTIVABLE land, excluding the homestead plot
o["land_cultivable_acres"] = d.land_acres
# three assets NITI counts that the instrument was not asking for at all
o["owns_phone"] = (rng.random(n) < np.clip(.82 + .12 * d.smartphone_owned.values, 0, .99)).astype(int)
o["owns_computer"] = (rng.random(n) < .04).astype(int)
o["owns_animal_cart"] = (rng.random(n) < np.where(np.isin(occ, [1, 2]), .16, .05)).astype(int)
# productive assets as a list of binaries instead of counts (a goat and a buffalo, or a jeep and a
# hand-cart, are not equally valuable, so a plain count is a poor value proxy); derived from the old
# pool's aggregate livestock/pony/business-asset flags, split into asset types
has_lstk = d.livestock_count.values > 0
o["owns_cow_buffalo"] = np.where(has_lstk, (rng.random(n) < 0.70).astype(int), (rng.random(n) < 0.03).astype(int))
o["owns_goat_sheep"] = np.where(has_lstk, (rng.random(n) < 0.45).astype(int), (rng.random(n) < 0.05).astype(int))
o["owns_pony_mule"] = (d.pony_count.values > 0).astype(int)
has_biz = d.business_asset_owned.values == 1
shop_biased = np.isin(occ, [5, 6, 7, 8, 11])   # shop/hotel/dhaba-type occupations
veh_biased = np.isin(occ, [10])                 # driver
o["owns_shop_stall"] = np.where(has_biz, (rng.random(n) < np.where(shop_biased, 0.75, 0.25)).astype(int), 0)
o["owns_work_vehicle"] = np.where(has_biz, (rng.random(n) < np.where(veh_biased, 0.70, 0.20)).astype(int), (rng.random(n) < 0.02).astype(int))
o["owns_work_equipment"] = np.where(has_biz, (rng.random(n) < 0.40).astype(int), (rng.random(n) < 0.03).astype(int))
EQ = ["saddle aur rassi", "chai banane ka saman", "gas chulha aur bartan", "auzar ka box",
      "silai machine", "generator", "", "thela"]
o["work_equipment_detail"] = [str(rng.choice(EQ)) if v == 1 else "" for v in o.owns_work_equipment.values]

# ---- G ------------------------------------------------------------------------
o["has_bank_account"] = d.has_bank_account
# Jan Dhan is now gated on having an account at all -- previously asked of everyone

# ---- credit block: lender type, debt stock, price, security -----------------------------------
_old_cred = code(d.credit_source, {"No credit": 0, "Institutional": 1, "Non-institutional": 2})
o["took_loan_12m"] = (_old_cred > 0).astype(int)
# the old binary splits into lender TYPES: institutional across bank/coop/MFI, non-institutional
# across moneylender/relative/contractor advance
_inst = rng.choice([1, 2, 3, 4], n, p=[.44, .10, .18, .28])
_noninst = rng.choice([5, 6, 7, 8], n, p=[.46, .34, .18, .02])
o["credit_source"] = np.where(_old_cred == 1, _inst, np.where(_old_cred == 2, _noninst, np.nan))
# outstanding stock, fatter for informal lenders; rounded the way people report
_amt = np.round(rng.gamma(1.9, 14000, n) * np.where(_old_cred == 2, 0.55, 1.0) / 500) * 500
o["loan_amount"] = np.where(_old_cred > 0, _amt, np.nan)
# rupees per 100 per month: institutional roughly 1, moneylenders 3-6
_rate = np.where(_old_cred == 1, rng.normal(1.0, 0.3, n), rng.normal(4.2, 1.4, n)).clip(0, 12)
_knows_rate = rng.random(n) < 0.82
# interest is not universal -- borrowing from relatives is often interest-free, which is why
# the rate question is gated rather than asking everyone to enter 0
_pays = np.where(_old_cred > 0, (rng.random(n) < np.where(_old_cred == 2, .82, .97)).astype(float), np.nan)
o["pays_interest"] = _pays
o["loan_interest_per100_pm"] = np.where((np.nan_to_num(_pays) == 1) & _knows_rate, np.round(_rate, 1), np.nan)
_secured = np.where(_old_cred > 0, (rng.random(n) < np.where(_old_cred == 2, .38, .52)).astype(float), np.nan)
o["loan_against_asset"] = _secured
# what was pledged: jewellery and animals dominate for informal lenders, business stock for formal
o["loan_collateral"] = [int(rng.choice([1,2,3,4,5,6,7], p=[.34,.14,.20,.10,.14,.04,.04])) if v == 1 else np.nan for v in np.nan_to_num(_secured)]

# ---- insurance as COUNTS, not a single categorical ---------------------------------------------
_ins_old = code(d.insurance_coverage, {"None": 0, "Health": 1, "Life": 2, "Crop": 3, "Multiple": 4})
_hh = d.hhsize.values
_health_any = np.isin(_ins_old, [1, 4])
o["n_health_insured"] = np.where(_health_any,
                                 np.minimum(_hh, 1 + rng.poisson(1.6, n)), 0).astype(float)
_life_any = np.isin(_ins_old, [2, 4])
o["n_life_insured"] = np.where(_life_any, np.minimum(_hh, 1 + rng.poisson(0.4, n)), 0).astype(float)
_has_land = d.land_acres.values > 0
o["has_crop_insurance"] = np.where(_has_land,
                                   ((np.isin(_ins_old, [3, 4])) & (rng.random(n) < .7)).astype(float), np.nan)

# named schemes, as a check-all. The old pool carried only a yes/no, so the named pattern is drawn
# here: ration is near-universal among those receiving anything, the rest taper. Code 10 (None of
# these) is the explicit negative and is exclusive -- it cannot be ticked alongside a scheme.
# Per-scheme rates drawn for EVERYONE, not conditioned on the old pool's govt_scheme_beneficiary
# binary. That binary asked "did you get anything from any government scheme", and the named list
# replaced it precisely because a category question like that under-reports -- people who draw PDS
# grain every month routinely say no to it. Conditioning the named list on the binary would rebuild
# the undercount the change was made to remove, and it did: ration-card coverage came out at 19%
# against a real Uttarakhand figure far above that, leaving the portability indicator 95% constant.
_SCH_P = {1: .71, 2: .26, 3: .14, 4: .12, 5: .49, 6: .05, 7: .33, 8: .09, 9: .04}
_gs = []
for _ in range(n):
    picked = [str(k) for k, pr in _SCH_P.items() if rng.random() < pr]
    _gs.append(" ".join(picked) if picked else "10")
o["govt_schemes"] = _gs
SCHEME_OTHER = ["gaon ki samiti se", "mandir trust se madad", "kisan credit card"]
o["govt_scheme_other"] = [str(rng.choice(SCHEME_OTHER)) if "9" in g.split() else "" for g in _gs]
o["smartphone_owned"] = d.smartphone_owned
_dig_old = code(d.digital_payment_use, {"Never": 0, "Sometimes": 1, "Often": 2})
o["uses_digital_payment"] = (_dig_old > 0).astype(int)
# how many in the household can move money themselves -- deeper than the respondent's own use
o["n_can_transact_online"] = np.minimum(
    d.hhsize.values, np.where(_dig_old > 0, rng.poisson(1.3, n) + 1, rng.poisson(0.35, n))).astype(float)

# ---- H, I, J ---------------------------------------------------------------------
# NITI health indicators: child/adolescent mortality and maternal care. Both are rare events and
# both are raised for poorer households -- the gradient the indicators exist to pick up.
_p_death = np.clip(.035 + .045 * d.poor.values, 0, .2)
o["child_death_5y"] = (rng.random(n) < _p_death).astype(int)
_p_birth = np.clip(.16 + .34 * (o.n_children_u15.values > 0), 0, .8)
_birth = (rng.random(n) < _p_birth).astype(int)
o["birth_last_5y"] = _birth
o["anc_4_visits"] = np.where(_birth == 1, (rng.random(n) < np.clip(.78 - .20*d.poor.values, .2, .97)).astype(float), np.nan)
o["skilled_birth_attendant"] = np.where(_birth == 1, (rng.random(n) < np.clip(.86 - .18*d.poor.values, .3, .99)).astype(float), np.nan)
for v in ["morbidity_15d", "hospitalization_365d"]: o[v] = d[v]
ill = d.morbidity_15d.values == 1
copeP = np.array([.28, .30, .10, .15, .12, .05])
o["morbidity_coping_15d"] = np.where(ill, [rng.choice([1, 2, 3, 4, 5, 6], p=copeP) for _ in range(n)], np.nan)
o["morbidity_cost_15d"] = np.where(ill, np.round(rng.gamma(1.5, 500, n) / 10) * 10, np.nan)
o["health_access_barrier_3m"] = (rng.random(n) < np.clip(0.05 + 0.15 * d.health_access_deprived.values + 0.10 * d.poor.values, 0, 1)).astype(int)
# reduced Coping Strategy Index items, Yatra-season/off-season pairs (workers are migrants
# interviewed on-site, so a single 7-day recall would miss the off-season household pattern --
# see dictionary.py Module I). Poorer households cope more often and lean harder on the more
# severe items (borrowing food, restricting adults); off-season is the leaner period for most
# non-Yatra work options, so its lambda runs 30% higher than the Yatra-season one.
RCSI_LAM = {"cope_less_pref_food": (1.0, 3.0), "cope_borrow_food": (0.3, 1.5), "cope_reduce_meals": (0.3, 1.8),
            "cope_reduce_portion": (0.4, 2.0), "cope_restrict_adult": (0.1, 0.9)}
for v, (base, poor_add) in RCSI_LAM.items():
    lam_yatra = base + poor_add * d.poor.values
    o[v + "_yatra_wk"] = np.minimum(7, rng.poisson(lam_yatra))
    o[v + "_offseason_wk"] = np.minimum(7, rng.poisson(1.3 * lam_yatra))
# ---- shocks: check-all, with the covariate codes the old list never had -------------------------
# The old pool holds one idiosyncratic shock per household. That is carried over, and covariate
# shocks (5-8) are drawn on top -- they hit the whole route, so they are strongly correlated across
# respondents rather than independent. A shared "bad year" draw is what produces that correlation.
dis = code(d.distress_event_last365d, {"None": 0, "Major illness": 1, "Crop": 2, "Natural": 3, "Business": 4})
_bad_year = rng.random() < 0.55          # ONE draw for the whole sample, not one per household
_shock_sets = []
for i in range(n):
    picks = set()
    if dis[i] > 0:
        picks.add(int(dis[i]))
    trek_i = bool(TREK[i]) if "TREK" in dir() else False
    p_route = (.34 if _bad_year else .07) * (1.5 if trek_i else 1.0)
    if rng.random() < p_route:
        picks.add(5)
    if rng.random() < (.22 if _bad_year else .04):
        picks.add(6)
    if rng.random() < (.26 if _bad_year else .11):
        picks.add(7)
    if rng.random() < .09:
        picks.add(8)
    _shock_sets.append(picks)
o["distress_event_last365d"] = [" ".join(str(v) for v in sorted(p)) for p in _shock_sets]
cred = o.credit_source.values
coping = np.full(n, np.nan)
for i in np.where(dis > 0)[0]:
    p = np.array([.28, .30, .10, .15, .12, .05])
    if cred[i] == 2: p = np.array([.10, .55, .10, .12, .08, .05])
    if d.poor.values[i] == 1: p = p * np.array([.8, 1.1, 1.0, 1.4, 1.0, 1.0])
    coping[i] = rng.choice([1, 2, 3, 4, 5, 6], p=p / p.sum())
# coping is check-all too: selling assets and cutting consumption are no longer mutually exclusive,
# which is the whole point -- a household may do both, or cut consumption precisely to avoid selling
_cope_sets = []
for i in range(n):
    if not _shock_sets[i]:
        _cope_sets.append("")
        continue
    picks = {int(coping[i])} if not np.isnan(coping[i]) else set()
    for c, pr in ((1, .30), (2, .34), (3, .18), (4, .40), (5, .26), (6, .10)):
        if rng.random() < pr:
            picks.add(c)
    _cope_sets.append(" ".join(str(v) for v in sorted(picks)) if picks else "6")
o["shock_coping"] = _cope_sets
o["ropeway_stance"] = code(d.ropeway_stance, {"Support": 1, "Neutral": 2, "Oppose": 3, "Don't": 98})
TREK = np.isin(occ, [1, 2, 3, 4])
# Open follow-up to the stance. Reasons are drawn conditional on the stance so the two agree, the
# way they would in a real interview; recorded as romanised Hindi the way an enumerator would type it.
_OPIN = {1: ["kaam badhega, yatri zyada aayenge", "sabko subidha hogi", "vikas hai, hona chahiye",
             "buzurg yatri aaram se darshan kar payenge", "naye kaam milenge"],
         2: ["pata nahi kya hoga", "dekhte hain kya hota hai", "kuch keh nahi sakte"],
         3: ["hamara kaam chala jayega", "ghoda-khachar bekaar ho jayega",
             "paidal yatri kam honge to dukan nahi chalegi", "bade logon ko fayda hoga, humko nahi",
             "pahad kat jayega, nuksan hoga", "hum kahan jayenge phir"],
         98: ["", "pata nahi"]}
o["trek_dependent"] = np.where(TREK, 1, np.where(occ == 12, (rng.random(n) < .7).astype(int), (rng.random(n) < np.where(occ == 9, .03, 0)).astype(int)))

# ---- K: Apablaza et al. (2026) Appendix 2 questions, read directly with its own skip logic --------
HZ = {1: .92, 2: .85, 3: .92, 4: .92, 5: .20, 6: .20, 7: .12, 8: .10, 9: .18, 10: .12, 11: .80, 12: .60, 13: .85, 14: .30}
hz = np.array([HZ[k] for k in occ])
wage = np.isin(et, [3, 4])
hours_week = hours_day * days_week   # not asked as such -- built in Stata from hours_day_yatra x days_week_yatra
# job_situation: Apablaza Q5's full ELEVEN categories. The sample is recruited at the Yatra worksite,
# so it is overwhelmingly full-time/part-time; the rest get a small residual probability each, purely
# so the three-way routing is actually exercised, not because the sampling design would produce them.
JS_CODES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 97]
JS_FT = [.930, .030, .010, .004, .004, .004, .006, .006, .003, .002, .001]
JS_PT = [.100, .820, .025, .008, .006, .008, .012, .012, .005, .003, .001]
o["job_situation"] = [rng.choice(JS_CODES, p=(JS_FT if hw >= 35 else JS_PT)) for hw in hours_week]
job_sit = np.array(o["job_situation"])
working = np.isin(job_sit, [1, 2, 3])      # codes 1-3 -> the whole job-quality block
tail    = np.isin(job_sit, range(1, 8))    # codes 1-7 -> Apablaza routes these to Q21 as well
seeking = job_sit == 8                     # code 8  -> routed straight to Q22/Q23
# employer_type is gone (2026-09-30): it asked employment status a second time in Apablaza's Q8
# taxonomy, and Q8 crosses status with institutional sector, so a worker employed by an individual --
# a thekedar, a shop owner -- had no true option. employment_type in Module B carries this.
PERM = {1: [.10, .75, .10, .03, .02], 2: [.25, .60, .05, .05, .05], 3: [.20, .55, 0, .10, .15], 4: [0, .12, .78, .05, .05]}
o["job_permanence"] = np.where(working, [rng.choice([1, 2, 3, 4, 5], p=PERM[e]) for e in et], np.nan)
CON = {3: [.30, .10, .60], 4: [.02, .03, .95]}
o["contract_status"] = [rng.choice([1, 2, 3], p=CON[e]) if (e in (3, 4) and w) else np.nan for e, w in zip(et, working)]
regp = np.where(et == 1, np.where(TREK, .85, .60), np.where(et == 2, .55, np.where(et == 3, .60, .25)))
o["workplace_registered"] = np.where(working, (rng.random(n) < regp).astype(float), np.nan)
o["pension_contrib"] = np.where(working, [rng.choice([1, 2, 3], p=[.10, .05, .85]) if e == 3 else rng.choice([2, 3], p=[.04, .96]) for e in et], np.nan)
wi = []
for i in range(n):
    pw = {3: .25, 4: .02}.get(et[i], .03)
    u = rng.random()
    if u < pw: wi.append(1)
    elif u < pw + .03: wi.append(4)
    else: wi.append(2 if (d.health_insurance_covered.values[i] == 1 and rng.random() < .8) else 3)
o["work_health_ins"] = np.where(working, wi, np.nan)
# leave rights: asked of everyone still in the block, not only wage workers (Apablaza Q18 has no
# wage-only skip) -- self-employed mostly answer no, with a small yes/don't-know tail
LEA = {3: [.35, .60, .05], 4: [.02, .93, .05], 1: [.03, .90, .07], 2: [.08, .85, .07]}
o["leave_rights"] = np.where(working, [ [1, 0, 97][rng.choice(3, p=LEA[e])] for e in et], np.nan)
inj = np.where(working, np.where(rng.random(n) < .01, 97, (rng.random(n) < (.05 + .30 * hz)).astype(int)), np.nan)
o["injured_ever"] = inj
p12 = .04 + .18 * hz + .15 * (inj == 1)
o["workplace_injury_12m"] = np.where(working, np.where(rng.random(n) < .02, 97, (rng.random(n) < p12).astype(int)), np.nan)
wants = np.where(tail, np.where(rng.random(n) < .02, 97, (rng.random(n) < expit(-1.8 + 0.30 * months_no_work)).astype(int)), np.nan)
o["wants_more_work"] = wants
HR = [5, 8, 10, 10, 12, 15, 20, 20, 21, 28, 30, 35, 40]
o["more_hours_day"] = [int(rng.choice([1,2,2,3,3,4,5])) if (w == 1 or sk) else np.nan for w, sk in zip(wants, seeking)]
# weeks spent looking for work across idle months (Apablaza's own unit, Q23), not a plain yes/no --
# search intensity scales with whether the worker wanted more work, over the idle months in the calendar
search_intensity = np.where(wants == 1, rng.uniform(0.3, 0.8, n), rng.uniform(0.0, 0.3, n))
o["months_looked_for_work"] = np.where((months_no_work > 0) | seeking, np.round(months_no_work * search_intensity), np.nan)
# first job ever: less likely the longer someone has worked in the Yatra economy
p_first = np.clip(0.35 - 0.03 * d.years_in_yatra_work.values, 0.02, 0.35)
o["first_job_ever"] = np.where(rng.random(n) < 0.02, 97, (rng.random(n) < p_first).astype(int))

# ---- L: tasks (12), driving experience without reference to licences, reading and counting --------------
for nm, lab, no, src in TASKS:
    o[nm] = t[f"t1_{int(no):02d}"]
drives = t.t1_07.isin([1, 2]).values
reg_drv = (t.t1_07 == 1).values
d2 = np.where(drives, ((rng.random(n) < .93) | (t.t3_15_twowheeler.values == 1)).astype(float), np.nan)
d4 = np.where(drives, ((t.t3_15_car.values == 1) | (rng.random(n) < np.where(reg_drv, .55, .25))).astype(float), np.nan)
dh = np.where(drives, ((t.t3_15_heavy.values == 1) | (rng.random(n) < np.where(reg_drv, .15, .03))).astype(float), np.nan)
o["drove_twowheeler"] = d2; o["drove_car"] = d4; o["drove_heavy"] = dh
o["read_at_work"] = (t.t3_01 == 1).astype(int); o["calc_at_work"] = (t.t3_03 == 1).astype(int)

# ---- paradata that depends on the answers -----------------------------------
tkc = [x[0] for x in TASKS]
n_prior = (o[tkc] == 2).sum(1).values
# Interview duration is NOT simulated. The old code set it to an invented intercept of 42 minutes
# plus noise, which measured nothing and was then quoted as if it were evidence. Kobo records real
# start/end timestamps, so these two columns get their values at the pretest and stay empty here.
o["dur_tasks_min"] = np.nan
o["interview_duration_min"] = np.nan

for v in ["flagged_contradiction", "dropout_score", "dropout_prob", "flagged_dropout", "retained"]:
    o[v] = d[v]


# ---- variables added 2026-09-30 for the four analysis arms --------------------------------------
# site: paradata the enumerator sets. Kedarnath is the larger route of the two.
o["site"] = rng.choice([1, 2], n, p=[.72, .28])

# where they sleep in season (Lyons et al. security/settlement dimension). Someone who lives here all
# year sleeps at home; a seasonal worker is the one on a workplace floor, under canvas, or in the open.
_ACC = {True:  [.62, .18, .07, .05, .02, .04, .01, .01],   # never leaves at closure
        False: [.04, .22, .26, .24, .10, .08, .05, .01]}   # comes for the season
o["accom_type_here"] = [int(rng.choice(range(1, 9), p=_ACC[bool(v)]))
                        for v in (o["resp_returns_at_closure"].values == 0)]

# Washington Group mobility item. Prevalence rises with age, and this workforce self-selects on being
# able to climb, so serious difficulty is rare among those still working the route.
_wg_p = np.clip((d.age.values - 25) / 220.0, .01, .30)
o["func_limitation"] = [int(rng.choice([1, 2, 3, 4], p=[1 - q - q * .45, q, q * .33, q * .12]
                                       / np.sum([1 - q - q * .45, q, q * .33, q * .12])))
                        for q in _wg_p]

# ration portability, asked only of households that named a ration card (code 1 in govt_schemes)
_has_ration = np.array(["1" in str(g).split() for g in o["govt_schemes"].values])
o["ration_portable_here"] = np.where(
    _has_ration, rng.choice([1, 2, 3, 97], n, p=[.31, .46, .17, .06]), np.nan)

# shock magnitude and timing, asked only of households reporting at least one shock. The worst shock
# is drawn from the ones they actually reported, never from the whole list.
_shk = [str(v).split() for v in o["distress_event_last365d"].values]
o["shock_worst"] = [int(rng.choice(v)) if v and v != [""] and v != ["nan"] else np.nan for v in _shk]
_any_shock = np.array([not (np.isnan(x) if isinstance(x, float) else False)
                       for x in o["shock_worst"].values])
o["shock_loss_amount"] = np.where(
    _any_shock, (np.round(rng.gamma(1.9, 9000, n) / 500) * 500).clip(500, 200000), np.nan)
# shocks cluster in the Yatra months, when there is income to lose and crowds to be disrupted
o["shock_month"] = np.where(
    _any_shock, rng.choice(range(1, 13), n,
                           p=[.04, .03, .04, .09, .13, .13, .12, .11, .10, .08, .07, .06]), np.nan)

keep = [r["name"] for r in ROWS if r["origin"] != "constructed"]
missing = [k for k in keep if k not in o.columns]
assert not missing, missing
raw = o[keep]
raw.to_csv(os.path.join(HERE, "..", "data", "raw_asked.csv"), index=False)

keepchk = d[["resp_id", "cons_pc_pm", "poor", "poor_sensitivity_cpi", "durables_count", "health_access_deprived", "education_years",
             "total_cons_pm", "yatra_income", "non_yatra_income", "total_annual_income", "yatra_income_share", "yatra_months",
             "yatra_start_month", "yatra_end_month", "cons_food_30d"]].copy()
keepchk["cv12"] = inc.std(1, ddof=1) / inc.mean(1)
keepchk["offseason_primary_code"] = code(d.offseason_primary, {"No other": 8, "Agriculture": 2, "Animal": 3, "Wage labour": 4, "Migrated": 5, "Petty": 6, "Salaried": 7})
keepchk.to_csv(os.path.join(HERE, "..", "checks", "original_values_for_check.csv"), index=False)
print("raw written:", raw.shape, "| variables =", len(keep))
print("interview duration: not simulated (Kobo start/end timestamps supply it at the pretest)")
print("max interviews per enumerator-day:", pd.crosstab(raw.enum_id, raw.interview_date).values.max())
