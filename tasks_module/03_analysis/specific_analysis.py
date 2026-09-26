"""Stage 4 - specific analysis: ropeway-related destination jobs, task gap, entry gates, who can be placed, displacement count.
Reads the 104 'fielded' test workers (and the 200 pool for drop-out weights). Writes 03_analysis/outputs/4_*.csv/png and results_specific.json.

Notation (all counts of tasks out of the 27):
  O   = tasks the worker does regularly (answer 1)                       ("origin tasks")
  H   = tasks the worker can do: strict view H = O ; broad view H = O + done before (answer 2)
  D   = tasks the destination job requires (from the NCO text)
  shortage   = |D not in H| / |D|      share of the new job's tasks the worker lacks
  redundancy = |O not in D| / |O|      share of the worker's current tasks the new job does not use
Rules fixed before looking at results: eligible when shortage <= 1/3 and any entry gate is met; base view = broad.
Sensitivity: shortage cut 0 and 1/2; strict view; gates off; exposure definition."""
import csv, json, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs"); os.makedirs(OUT, exist_ok=True)
D = os.path.join(HERE, "..", "02_data")
df = pd.read_csv(os.path.join(D, "tasks_synth_fielded.csv"))
full = pd.read_csv(os.path.join(D, "tasks_synth_full.csv"))
TC = [f"t1_{k:02d}" for k in range(1, 28)]
n = len(df)
S = (df[TC] == 1).astype(int).values
B = df[TC].isin([1, 2]).astype(int).values
occ = df["occupation"].values
rng = np.random.default_rng(20260921)
LAB = {int(i["variable"].split("_")[1]): i["label"] for i in csv.DictReader(open(os.path.join(HERE, "..", "01_questions", "task_items.csv"), encoding="utf-8-sig")) if i["variable"].startswith("t1_") and i["variable"] != "t1_28"}

# ---------------- 4.1 destination jobs (provisional, from NCO-2015 text) ----------------
# gate: column of the test data that must equal 1 (None = no formal gate found in NCO)
DEST = [
 # id, family, title, NCO code/source, required, optional, gate column, gate note
 ("RW1", "Ropeway", "Aerial ropeway operator", "NCO 8343.1700", [8, 12, 24], [9, 25], None, "No licence or level given in NCO; a technical certificate is likely (sensitivity)"),
 ("RW2", "Ropeway", "Electrician / wireman (ropeway plant)", "NCO 7411.0301 (QP ELE/Q7302, NSQF 3)", [10, 12], [9], "t3_15_iti", "ITI or NSQF-3 electrical certificate"),
 ("RW3", "Ropeway", "Mechanic / fitter (ropeway plant)", "NCO 7231.0500 (nearest entry)", [8, 9], [12], "t3_15_iti", "ITI or technical certificate (assumed)"),
 ("RW4", "Ropeway", "Station loading and crowd attendant", "NCO 9333 loader + 8343.1700 attendant; judgement", [3, 23, 24], [1], None, "None"),
 ("RW5", "Ropeway", "Ticket and information counter clerk", "NCO 4224.0100 / 4221 (nearest); judgement", [16, 25, 21], [24], None, "None"),
 ("SEC", "Other", "Security guard / gateman", "NCO 5414 Gateman/Unarmed Security Guard (QP SKS/Q0101, NSQF 4)", [23, 21, 25], [], "t3_15_security", "NSQF-4 guard certificate"),
 ("HOS1", "Hospitality", "Room attendant / housekeeping", "NCO 5151.0202", [20], [19, 3], None, "None"),
 ("HOS2", "Hospitality", "Waiter / food and beverage steward", "NCO 5131.0401 (NSQF 3, training-linked)", [19, 16], [18], None, "None (course is common but not required)"),
 ("HOS3", "Hospitality", "Cook", "NCO 5120.0300 / 5122", [18], [20, 26], None, "None"),
 ("TRA", "Transport", "Light motor vehicle (car) driver", "NCO 8322.0100", [7, 12, 16], [24], "t3_15_car", "Car (LMV) licence"),
 ("SHP", "Station shop", "Shop assistant", "NCO 5223.0200", [14, 4], [15, 16, 20], None, "None"),
 ("GDE", "Guiding", "Tourist guide", "NCO 5113.0200", [21], [14, 22, 13], "t3_15_guide", "Guide or trekking permit (assumed; not in NCO)"),
 ("CON", "Other", "Construction labourer (build phase)", "NCO 9313.9900", [11, 1, 3], [], None, "None"),
]
NJ = len(DEST)
J = [d[0] for d in DEST]
dcsv = pd.DataFrame([dict(id=d[0], family=d[1], title=d[2], source=d[3], required=";".join(map(str, d[4])), optional=";".join(map(str, d[5])), gate=d[6] or "", gate_note=d[7]) for d in DEST])
dcsv.to_csv(os.path.join(OUT, "4_1_destination_jobs.csv"), index=False)
Dvec = np.zeros((NJ, 27), int); Dopt = np.zeros((NJ, 27), int)
for k, d in enumerate(DEST):
    for t in d[4]: Dvec[k, t - 1] = 1
    for t in d[5]: Dopt[k, t - 1] = 1
GATE = np.ones((n, NJ), int)
for k, d in enumerate(DEST):
    if d[6]: GATE[:, k] = df[d[6]].values.astype(int)
gate_share = {d[0]: float(GATE[:, k].mean()) for k, d in enumerate(DEST)}

def measures(H, O, Dm):
    """returns shortage (n x NJ), redundancy (n x NJ), cosine, jaccard"""
    sh = np.zeros((n, NJ)); rd = np.zeros((n, NJ)); cs = np.zeros((n, NJ)); jc = np.zeros((n, NJ))
    for k in range(NJ):
        d = Dm[k]
        sh[:, k] = ((d[None, :] == 1) & (H == 0)).sum(1) / d.sum()
        rd[:, k] = ((O == 1) & (d[None, :] == 0)).sum(1) / O.sum(1)
        inter = (H * d[None, :]).sum(1)
        cs[:, k] = inter / (np.sqrt(H.sum(1)) * np.sqrt(d.sum()))
        jc[:, k] = inter / (H.sum(1) + d.sum() - inter)
    return sh, rd, cs, jc

shS, rdS, csS, jcS = measures(S, S, Dvec)
shB, rdB, csB, jcB = measures(B, S, Dvec)
shBo, _, _, _ = measures(B, S, np.maximum(Dvec, Dopt))   # with optional tasks required as well

# ---------------- exposure ----------------
main = df["t1_28"].values
E_main = np.isin(main, [1, 2, 5])            # main task is carrying, passenger or pack animals
E_narrow = np.isin(occ, ["Porter", "Palki", "Pony worker", "Pony business"])   # base: trek-carrying jobs
E_broad = (S[:, [0, 1, 4]].sum(1) > 0)     # any regular carrying / passenger / pack-animal task
R = {"n": n, "gate_share": gate_share, "E_base": int(E_narrow.sum()), "E_main": int(E_main.sum()), "E_any": int(E_broad.sum()),
     "E_base_by_job": pd.Series(occ[E_narrow]).value_counts().to_dict(), "E_main_by_job": pd.Series(occ[E_main]).value_counts().to_dict(), "E_any_by_job": pd.Series(occ[E_broad]).value_counts().to_dict()}

# drop-out weights: pool share / fielded share by job (corrects the drop-out only; real stratum totals still needed)
pool = full["occupation"].value_counts(); fld = df["occupation"].value_counts()
wj = (pool / pool.sum()) / (fld / fld.sum())
w = np.array([wj[o] for o in occ])
w = w / w.mean()
R["weights_range"] = [float(w.min()), float(w.max())]

# ---------------- 4.2-4.5 eligibility ----------------
def eligible(sh, cut=1 / 3, gates=True):
    e = (sh <= cut + 1e-9)
    return e & (GATE == 1) if gates else e

BASE = dict(view="broad", cut=1 / 3, gates=True)
def elig(view="broad", cut=1 / 3, gates=True, optional=False):
    sh = {"strict": shS, "broad": shBo if optional else shB}[view]
    return eligible(sh, cut, gates)
EB = elig()
ES = elig("strict")

def share(mask, m): return float(m[mask].mean())
def wshare(mask, m): return float(np.average(m[mask], weights=w[mask]))

# who can take which job
rows = []
for k, d in enumerate(DEST):
    rows.append(dict(id=d[0], family=d[1], title=d[2], n_required=int(Dvec[k].sum()),
                     gate_share_all=gate_share[d[0]],
                     strict_no_gate=float(elig("strict", gates=False)[E_narrow, k].mean()),
                     strict_gate=float(ES[E_narrow, k].mean()),
                     broad_no_gate=float(elig("broad", gates=False)[E_narrow, k].mean()),
                     broad_gate=float(EB[E_narrow, k].mean())))
t45 = pd.DataFrame(rows); t45.to_csv(os.path.join(OUT, "4_5_eligible_by_destination.csv"), index=False)
R["elig_rows"] = rows
R["no_option_strict"] = float((ES[E_narrow].sum(1) == 0).mean()); R["no_option_broad"] = float((EB[E_narrow].sum(1) == 0).mean())
R["no_option_broad_w"] = float(np.average((EB[E_narrow].sum(1) == 0), weights=w[E_narrow]))
R["n_options_broad_mean"] = float(EB[E_narrow].sum(1).mean())
R["no_option_by_job"] = {j: float((EB[E_narrow & (occ == j)].sum(1) == 0).mean()) for j in np.unique(occ[E_narrow])}

# ---------------- 4.3 type of move (Neffke-style) ----------------
R["mean_D"] = float(Dvec.sum(1).mean()); R["mean_O"] = float(S.sum(1).mean())
R["share_pairs_redundancy_high"] = float((rdB[E_narrow] > 1 / 3).mean())
R["share_pairs_shortage_high"] = float((shB[E_narrow] > 1 / 3).mean())
CUT = 1 / 3
def types(sh, rd):
    T = np.full(sh.shape, "", dtype=object)
    T[(sh <= CUT) & (rd <= CUT)] = "close match"
    T[(sh <= CUT) & (rd > CUT)] = "downskill (surplus skills)"
    T[(sh > CUT) & (rd <= CUT)] = "upskill (tasks to add)"
    T[(sh > CUT) & (rd > CUT)] = "reskill (start over)"
    return T
TB = types(shB, rdB)
lev = ["close match", "downskill (surplus skills)", "upskill (tasks to add)", "reskill (start over)"]
# each exposed worker, each destination
allpairs = pd.Series(TB[E_narrow].ravel()).value_counts(normalize=True).reindex(lev).fillna(0)
R["types_all_pairs"] = allpairs.to_dict()
# best destination = smallest shortage, then smallest redundancy, among all destinations (gates ignored for the type)
bi = []
for i in np.where(E_narrow)[0]:
    k = min(range(NJ), key=lambda k: (shB[i, k], rdB[i, k]))
    bi.append(k)
bi = np.array(bi)
tb_best = np.array([TB[i, k] for i, k in zip(np.where(E_narrow)[0], bi)])
R["types_best"] = pd.Series(tb_best).value_counts(normalize=True).reindex(lev).fillna(0).to_dict()
jobs_e = pd.Series(occ[E_narrow])
tt = pd.crosstab(jobs_e.values, tb_best, normalize="index").reindex(columns=lev).fillna(0)
tt.round(3).to_csv(os.path.join(OUT, "4_3_types_by_job.csv"))
R["types_by_job"] = tt.reset_index().rename(columns={"index": "job"}).to_dict("records")
R["best_dest_counts"] = pd.Series([J[k] for k in bi]).value_counts().to_dict()
# agreement of the ranking across measures
def best_by(m, minimize):
    return np.array([(np.argmin(m[i]) if minimize else np.argmax(m[i])) for i in np.where(E_narrow)[0]])
bs = best_by(shB + 1e-6 * rdB, True); bc = best_by(csB, False); bj = best_by(jcB, False)
R["agree_shortage_cosine"] = float((bs == bc).mean()); R["agree_shortage_jaccard"] = float((bs == bj).mean())
R["agree_cosine_jaccard"] = float((bc == bj).mean())

# ---------------- 4.6 displacement accounting ----------------
GROUP = {"tech": ["RW1", "RW2", "RW3"], "service": ["HOS1", "HOS2", "HOS3", "RW5"]}
def vacancies(total, mix):
    wts = np.ones(NJ)
    if mix == "technical-heavy":
        for k in range(NJ):
            if J[k] in GROUP["tech"]: wts[k] = 3
    if mix == "service-heavy":
        for k in range(NJ):
            if J[k] in GROUP["service"]: wts[k] = 3
    raw = total * wts / wts.sum()
    v = np.floor(raw).astype(int)
    rem = int(round(total)) - v.sum()
    if rem > 0:
        order = np.argsort(-(raw - v))
        v[order[:rem]] += 1
    return v

def max_placed(el, v):
    """maximum number of workers placed: bipartite matching between workers and job slots"""
    if el.shape[0] == 0 or v.sum() == 0: return 0
    cols = np.repeat(np.arange(NJ), v)
    M = csr_matrix(el[:, cols].astype(int))
    m = maximum_bipartite_matching(M, perm_type="column")
    return int((m >= 0).sum())

def lottery_placed(el, v, draws=300):
    vals = []
    for _ in range(draws):
        left = v.copy(); placed = 0
        for i in rng.permutation(el.shape[0]):
            opts = [k for k in np.where(el[i])[0] if left[k] > 0]
            if opts:
                k = opts[rng.integers(len(opts))]; left[k] -= 1; placed += 1
        vals.append(placed)
    return float(np.mean(vals))

def account(mask, el, total, mix, lot=True):
    e = int(mask.sum()); v = vacancies(total, mix); em = el[mask]
    mp = max_placed(em, v)
    return dict(E=e, V=int(v.sum()), displaced_min=max(0, e - int(v.sum())), displaced_skill_best=e - mp,
                displaced_skill_lottery=(e - lottery_placed(em, v)) if lot else np.nan)

scen = []
for tot_share in (0.25, 0.5, 1.0):
    for mix in ("equal", "technical-heavy", "service-heavy"):
        tot = tot_share * E_narrow.sum()
        a = account(E_narrow, EB, tot, mix)
        scen.append(dict(vacancies_per_100_exposed=int(tot_share * 100), mix=mix, **{k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in a.items()}))
S9 = pd.DataFrame(scen)
for c in ("displaced_min", "displaced_skill_best", "displaced_skill_lottery"): S9[c + "_per100"] = (100 * S9[c] / S9["E"]).round(1)
S9.to_csv(os.path.join(OUT, "4_6_scenarios.csv"), index=False)
R["scenarios"] = S9.to_dict("records")

# curve: displaced per 100 exposed as vacancies grow
xs = np.arange(0, 1.51, 0.1)
curve = {"min": [], "best": [], "lottery": []}
for x in xs:
    a = account(E_narrow, EB, x * E_narrow.sum(), "equal")
    curve["min"].append(100 * a["displaced_min"] / a["E"]); curve["best"].append(100 * a["displaced_skill_best"] / a["E"]); curve["lottery"].append(100 * a["displaced_skill_lottery"] / a["E"])
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.plot(xs * 100, curve["min"], "--", c="grey", label="Numbers only (jobs minus workers)")
ax.plot(xs * 100, curve["best"], c="#4C72B0", label="Skills, best possible matching")
ax.plot(xs * 100, curve["lottery"], c="#C44E52", label="Skills, jobs given by lottery")
ax.set_xlabel("New jobs per 100 exposed workers"); ax.set_ylabel("Workers without a job per 100 exposed"); ax.set_ylim(0, 105)
ax.legend(frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "4_6_curve.png"), dpi=200); plt.close(fig)
R["curve_x"] = (xs * 100).tolist(); R["curve"] = curve
R["floor_no_option"] = 100 * R["no_option_broad"]

# ---------------- 4.7 sensitivity + uncertainty ----------------
sens = []
base_tot = 0.5
for expo, mask in (("title", E_narrow), ("main task", E_main), ("any carrying", E_broad)):
    for view in ("strict", "broad"):
        for cut in (0.0, 1 / 3, 0.5):
            for gates in (True, False):
                el = elig(view, cut, gates)
                a = account(mask, el, base_tot * mask.sum(), "equal", lot=False)
                sens.append(dict(exposure=expo, view=view, cut=round(cut, 2), gates=gates, E=a["E"], no_option=100 * float((el[mask].sum(1) == 0).mean()),
                                 displaced_min=100 * a["displaced_min"] / a["E"], displaced_skill_best=100 * a["displaced_skill_best"] / a["E"]))
sens = pd.DataFrame(sens); sens.round(1).to_csv(os.path.join(OUT, "4_7_sensitivity.csv"), index=False)
R["sens"] = sens.round(1).to_dict("records")
# optional tasks also required
elo = elig("broad", optional=True)
a = account(E_narrow, elo, base_tot * E_narrow.sum(), "equal", lot=False)
R["sens_optional"] = dict(no_option=100 * float((elo[E_narrow].sum(1) == 0).mean()), displaced_skill_best=100 * a["displaced_skill_best"] / a["E"])
# ropeway operator/technician gate = any certificate
cert = df["t3_13"].values == 1
GATE_save = GATE.copy()
for k, d in enumerate(DEST):
    if d[0] in ("RW1", "RW2", "RW3"): GATE[:, k] = np.where(cert, 1, 0) if d[0] == "RW1" else GATE[:, k]
elc = elig()
a = account(E_narrow, elc, base_tot * E_narrow.sum(), "equal", lot=False)
R["sens_rw1_cert"] = dict(no_option=100 * float((elc[E_narrow].sum(1) == 0).mean()), displaced_skill_best=100 * a["displaced_skill_best"] / a["E"])
GATE = GATE_save

# bootstrap: resample exposed workers within job, keep group sizes
B_N = 1000
idx_e = np.where(E_narrow)[0]
res = {"no_option": [], "best": []}
for _ in range(B_N):
    pick = []
    for j in np.unique(occ[idx_e]):
        ii = idx_e[occ[idx_e] == j]
        pick += list(rng.choice(ii, size=len(ii), replace=True))
    pick = np.array(pick)
    em = EB[pick]
    v = vacancies(base_tot * len(pick), "equal")
    mp = max_placed(em, v)
    res["no_option"].append(100 * float((em.sum(1) == 0).mean())); res["best"].append(100 * (len(pick) - mp) / len(pick))
R["boot"] = {k: [float(np.percentile(v, 2.5)), float(np.median(v)), float(np.percentile(v, 97.5))] for k, v in res.items()}
R["boot_n"] = B_N
a0 = account(E_narrow, EB, base_tot * E_narrow.sum(), "equal")
R["base"] = dict(E=a0["E"], V=a0["V"], min_per100=100 * a0["displaced_min"] / a0["E"], best_per100=100 * a0["displaced_skill_best"] / a0["E"],
                 lottery_per100=100 * a0["displaced_skill_lottery"] / a0["E"], no_option=100 * R["no_option_broad"])

# ---------------- pictures ----------------
fig, ax = plt.subplots(figsize=(7, 4.2))
y = np.arange(NJ); h = 0.38
ax.barh(y - h / 2, 100 * t45.strict_gate, h, color="#8DA0CB", label="Regular tasks only")
ax.barh(y + h / 2, 100 * t45.broad_gate, h, color="#4C72B0", label="Regular plus done before")
ax.set_yticks(y); ax.set_yticklabels([f"{r.title}" for r in t45.itertuples()], fontsize=7); ax.invert_yaxis()
ax.set_xlabel("Exposed workers who could take the job (%)"); ax.legend(frameon=False, fontsize=7, loc="lower right")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "4_5_eligible.png"), dpi=200); plt.close(fig)
fig, ax = plt.subplots(figsize=(6.6, 3.4))
bottom = np.zeros(len(tt)); colors = ["#55A868", "#8172B2", "#DD8452", "#C44E52"]
for c, col in zip(lev, colors):
    ax.barh(range(len(tt)), 100 * tt[c].values, left=bottom, color=col, label=c, edgecolor="white"); bottom += 100 * tt[c].values
ax.set_yticks(range(len(tt))); ax.set_yticklabels(tt.index, fontsize=8); ax.invert_yaxis()
ax.set_xlabel("Share of workers (%): type of move to their closest job"); ax.legend(fontsize=6.5, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "4_3_types.png"), dpi=200); plt.close(fig)

R["dest"] = dcsv.to_dict("records")
R["labels"] = LAB
json.dump(R, open(os.path.join(HERE, "results_specific.json"), "w"), indent=1, default=float)

# ---------------- console summary ----------------
print("E base", R["E_base"], R["E_base_by_job"]); print("E main", R["E_main"], R["E_main_by_job"]); print("E any", R["E_any"])
print("gate share", {k: round(v, 2) for k, v in gate_share.items()})
print(t45.round(2).to_string())
print("no option strict/broad", R["no_option_strict"], R["no_option_broad"], "mean options", R["n_options_broad_mean"], R["no_option_by_job"])
print("types all pairs", R["types_all_pairs"]); print("types best", R["types_best"]); print(tt.round(2).to_string())
print("best dest", R["best_dest_counts"]); print("agree", R["agree_shortage_cosine"], R["agree_shortage_jaccard"], R["agree_cosine_jaccard"])
print(S9.to_string())
print("base", R["base"]); print("boot", R["boot"]); print("optional", R["sens_optional"], "rw1cert", R["sens_rw1_cert"])
print(sens.round(1).to_string())
