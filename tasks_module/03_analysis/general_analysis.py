"""Stage 3 - general analysis of the task answers (whole task space, no ropeway yet).
Reads the 104 'fielded' test workers. Writes tables and pictures to 03_analysis/outputs/ and results_general.json.
Strict view = only answer 1 (regular in main work). Broad view = answer 1 or 2 (regular, or done before)."""
import csv, json, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
from scipy.spatial.distance import squareform

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs"); os.makedirs(OUT, exist_ok=True)
D = os.path.join(HERE, "..", "02_data")
df = pd.read_csv(os.path.join(D, "tasks_synth_fielded.csv"))
items = list(csv.DictReader(open(os.path.join(HERE, "..", "01_questions", "task_items.csv"), encoding="utf-8-sig")))
tinfo = {int(i["variable"].split("_")[1]): i for i in items if i["variable"].startswith("t1_") and i["variable"] != "t1_28"}
TC = [f"t1_{k:02d}" for k in range(1, 28)]
LABEL = {f"t1_{k:02d}": tinfo[k]["label"] for k in range(1, 28)}
G3 = {f"t1_{k:02d}": tinfo[k]["group3"] for k in range(1, 28)}
C5 = {f"t1_{k:02d}": tinfo[k]["class5"] for k in range(1, 28)}
assert df[TC].isin([1, 2, 3]).all().all()

S = (df[TC] == 1).astype(int).values          # strict
B = (df[TC].isin([1, 2])).astype(int).values  # broad
occ = df["occupation"].values
jobs = sorted(df["occupation"].unique())
R = {"n": int(len(df)), "n_jobs": len(jobs)}

def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na > 0 and nb > 0 else np.nan

# ---- 3.1 counts per worker -------------------------------------------------
df["n_reg"] = S.sum(1); df["n_prev"] = (df[TC] == 2).sum(1); df["n_any"] = B.sum(1)
c1 = df.groupby("occupation").agg(n=("resp_id", "size"), regular_mean=("n_reg", "mean"), regular_min=("n_reg", "min"),
                                  regular_max=("n_reg", "max"), before_mean=("n_prev", "mean"), any_mean=("n_any", "mean")).round(2)
c1 = c1.sort_values("regular_mean", ascending=False)
c1.to_csv(os.path.join(OUT, "3_1_task_counts_by_job.csv"))
R["counts"] = dict(regular_mean=float(df.n_reg.mean()), regular_sd=float(df.n_reg.std()), before_mean=float(df.n_prev.mean()),
                   any_mean=float(df.n_any.mean()), share_any_before=float((df.n_prev > 0).mean()),
                   regular_min=int(df.n_reg.min()), regular_max=int(df.n_reg.max()))
fig, ax = plt.subplots(figsize=(6.5, 3.4))
ax.hist(df.n_reg, bins=range(0, 17), color="#4C72B0", edgecolor="white", align="left", label="Done regularly")
ax.set_xlabel("Number of tasks (out of 27)"); ax.set_ylabel("Workers"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "3_1_hist.png"), dpi=200); plt.close(fig)

# ---- 3.2 job x task table --------------------------------------------------
P = pd.DataFrame({j: S[occ == j].mean(0) for j in jobs}, index=TC).T
order = c1.index.tolist()
P = P.loc[order]
P.round(2).to_csv(os.path.join(OUT, "3_2_job_by_task_regular_share.csv"))
Pb = pd.DataFrame({j: B[occ == j].mean(0) for j in jobs}, index=TC).T.loc[order]
Pb.round(2).to_csv(os.path.join(OUT, "3_2_job_by_task_broad_share.csv"))
fig, ax = plt.subplots(figsize=(9, 5))
im = ax.imshow(P.values, aspect="auto", cmap="Blues", vmin=0, vmax=1)
ax.set_yticks(range(len(order))); ax.set_yticklabels([f"{o} (n={int((occ == o).sum())})" for o in order], fontsize=7)
ax.set_xticks(range(27)); ax.set_xticklabels([str(k) for k in range(1, 28)], fontsize=7)
ax.set_xlabel("Task number (see W1 for wording)")
cb = fig.colorbar(im, ax=ax, fraction=0.025); cb.set_label("Share of workers doing the task regularly", fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "3_2_heatmap.png"), dpi=200); plt.close(fig)
prev_all = S.mean(0)
R["task_prev"] = {t: float(p) for t, p in zip(TC, prev_all)}
R["task_prev_top"] = [(t, LABEL[t], float(prev_all[i])) for i, t in sorted(enumerate(TC), key=lambda x: -prev_all[x[0]])[:5]]
R["task_prev_bottom"] = [(t, LABEL[t], float(prev_all[i])) for i, t in sorted(enumerate(TC), key=lambda x: prev_all[x[0]])[:5]]
# how "job-specific" each task is: share of its variation explained by job (eta squared)
def eta2(x, g):
    gm = x.mean(); sst = ((x - gm) ** 2).sum()
    if sst == 0: return np.nan
    ssb = sum(((x[g == j] - x[g == j].mean()).size) * (x[g == j].mean() - gm) ** 2 for j in np.unique(g))
    return ssb / sst
task_eta = {t: float(eta2(S[:, i].astype(float), occ)) for i, t in enumerate(TC)}
R["task_eta"] = task_eta

# ---- 3.3 task groups by job ------------------------------------------------
def shares(mat, groups, labels):
    out = np.zeros((len(mat), len(labels)))
    for k, lab in enumerate(labels):
        cols = [i for i, t in enumerate(TC) if groups[t] == lab]
        out[:, k] = mat[:, cols].sum(1)
    tot = out.sum(1, keepdims=True); tot[tot == 0] = 1
    return out / tot
g3l = ["analytical", "manual", "interactive"]
c5l = ["non-routine manual", "routine manual", "routine cognitive", "non-routine analytic", "non-routine interactive"]
sh3 = shares(S, G3, g3l); sh5 = shares(S, C5, c5l)
t33 = pd.DataFrame(sh3, columns=g3l); t33["occupation"] = occ
t33 = t33.groupby("occupation").mean().loc[order].round(3)
t33.to_csv(os.path.join(OUT, "3_3_group3_share_by_job.csv"))
t35 = pd.DataFrame(sh5, columns=c5l); t35["occupation"] = occ
t35 = t35.groupby("occupation").mean().loc[order].round(3)
t35.to_csv(os.path.join(OUT, "3_3_class5_share_by_job.csv"))
R["group3_overall"] = {g: float(v) for g, v in zip(g3l, sh3.mean(0))}
R["class5_overall"] = {g: float(v) for g, v in zip(c5l, sh5.mean(0))}
fig, ax = plt.subplots(figsize=(7.5, 4))
cols = {"analytical": "#DD8452", "manual": "#4C72B0", "interactive": "#55A868"}
names = {"analytical": "Thinking and counting", "manual": "Hands-on", "interactive": "Dealing with people"}
left = np.zeros(len(order))
for g in g3l:
    ax.barh(range(len(order)), t33[g].values, left=left, color=cols[g], label=names[g], edgecolor="white")
    left += t33[g].values
ax.set_yticks(range(len(order))); ax.set_yticklabels(order, fontsize=7); ax.invert_yaxis()
ax.set_xlabel("Share of the tasks the job does regularly"); ax.legend(fontsize=7, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "3_3_groups.png"), dpi=200); plt.close(fig)

# ---- 3.4 similarity between jobs ------------------------------------------
M = np.array([S[occ == j].mean(0) for j in jobs])
sim = pd.DataFrame([[cos(M[a], M[b]) for b in range(len(jobs))] for a in range(len(jobs))], index=jobs, columns=jobs)
sim.round(2).to_csv(os.path.join(OUT, "3_4_job_similarity.csv"))
nn = []
for j in jobs:
    s = sim.loc[j].drop(j).sort_values(ascending=False)
    nn.append((j, s.index[0], float(s.iloc[0]), s.index[-1], float(s.iloc[-1])))
R["nearest"] = nn
iu = np.triu_indices(len(jobs), 1)
R["job_sim_mean"] = float(sim.values[iu].mean())
Z = linkage(squareform(1 - sim.values, checks=False), method="average")
CUT = 0.5   # fixed in advance: jobs join a cluster while average cosine is at least 0.5
cl = fcluster(Z, t=CUT, criterion="distance")
R["cluster_cut"] = CUT
R["clusters"] = {int(k): [jobs[i] for i in range(len(jobs)) if cl[i] == k] for k in sorted(set(cl))}
CUT2 = 0.3  # tighter cut, also fixed in advance, shown next to the first
cl2 = fcluster(Z, t=CUT2, criterion="distance")
R["cluster_cut2"] = CUT2
R["clusters2"] = {int(k): [jobs[i] for i in range(len(jobs)) if cl2[i] == k] for k in sorted(set(cl2))}
CUT2 = 0.3
fig, ax = plt.subplots(figsize=(7, 3.8))
dendrogram(Z, labels=jobs, orientation="left", ax=ax, color_threshold=0.3, leaf_font_size=7)
ax.set_xlabel("Distance between jobs (1 minus overlap)"); ax.axvline(CUT, ls="--", c="grey", lw=0.8); ax.axvline(CUT2, ls=":", c="grey", lw=0.8)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "3_4_dendrogram.png"), dpi=200); plt.close(fig)
ordj = [jobs[i] for i in dendrogram(Z, no_plot=True)["leaves"]]
fig, ax = plt.subplots(figsize=(6.4, 5.2))
im = ax.imshow(sim.loc[ordj, ordj].values, cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(len(ordj))); ax.set_xticklabels(ordj, rotation=90, fontsize=7)
ax.set_yticks(range(len(ordj))); ax.set_yticklabels(ordj, fontsize=7)
fig.colorbar(im, ax=ax, fraction=0.04).set_label("Task overlap (1 = identical)", fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "3_4_similarity.png"), dpi=200); plt.close(fig)

# ---- 3.5 differences inside a job -----------------------------------------
Sf = S.astype(float)
sst = ((Sf - Sf.mean(0)) ** 2).sum()
ssb = sum(((Sf[occ == j].mean(0) - Sf.mean(0)) ** 2).sum() * (occ == j).sum() for j in jobs)
r2 = ssb / sst
k, n = len(jobs), len(occ)
r2_adj = 1 - (1 - r2) * (n - 1) / (n - k)
rng = np.random.default_rng(20260921)
null = []
for _ in range(2000):
    pj = rng.permutation(occ)
    b = sum(((Sf[pj == j].mean(0) - Sf.mean(0)) ** 2).sum() * (pj == j).sum() for j in jobs)
    null.append(b / sst)
null = np.array(null)
R["r2"] = dict(r2=float(r2), r2_adj=float(r2_adj), null_mean=float(null.mean()), null_p95=float(np.quantile(null, 0.95)),
               p=float((1 + (null >= r2).sum()) / (1 + len(null))), n_perm=int(len(null)))
# worker-to-worker overlap: same job vs different job
W = np.array([[cos(S[a], S[b]) for b in range(n)] for a in range(n)])
same = (occ[:, None] == occ[None, :]); off = ~np.eye(n, dtype=bool)
R["pair_cos"] = dict(same=float(W[same & off].mean()), diff=float(W[~same].mean()))
# share of workers whose own job is their closest job (leave-one-out)
own_closest = 0; ranks = []
for a in range(n):
    sc = {}
    for j in jobs:
        m = (occ == j) & (np.arange(n) != a)
        if m.sum() == 0: continue
        sc[j] = cos(S[a], S[m].mean(0))
    best = sorted(sc, key=lambda z: -sc[z])
    own_closest += (best[0] == occ[a]); ranks.append(best.index(occ[a]) + 1 if occ[a] in best else np.nan)
R["own_closest"] = float(own_closest / n)
R["own_rank_median"] = float(np.nanmedian(ranks))
own = np.array([cos(S[a], S[(occ == occ[a]) & (np.arange(n) != a)].mean(0)) if ((occ == occ[a]).sum() > 1) else np.nan for a in range(n)])
t5 = pd.DataFrame({"occupation": occ, "cos_to_own_job": own}).groupby("occupation").cos_to_own_job.agg(["count", "mean", "min"]).round(2).loc[order]
t5.to_csv(os.path.join(OUT, "3_5_fit_to_own_job.csv"))
R["fit_to_own_job_mean"] = float(np.nanmean(own))
fig, ax = plt.subplots(figsize=(6.2, 3.4))
ax.hist([W[same & off & np.triu(np.ones((n, n), bool), 1)], W[~same & np.triu(np.ones((n, n), bool), 1)]], bins=np.linspace(0, 1, 21),
        density=True, label=["Same job", "Different jobs"], color=["#4C72B0", "#C44E52"], alpha=0.8)
ax.set_xlabel("Task overlap between two workers (1 = identical)"); ax.set_ylabel("Density"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "3_5_pairs.png"), dpi=200); plt.close(fig)

# ---- 3.6 hidden experience -------------------------------------------------
prev = (df[TC] == 2).values
job_prev_reg = {j: S[occ == j].mean(0) for j in jobs}
new_to_job = 0; tot_prev = 0
for a in range(n):
    for i in np.where(prev[a])[0]:
        tot_prev += 1
        if job_prev_reg[occ[a]][i] < 0.20: new_to_job += 1
R["hidden"] = dict(share_new_to_job=float(new_to_job / tot_prev), total_code2=int(tot_prev))
h = df.groupby("offseason_primary").agg(n=("resp_id", "size"), before_mean=("n_prev", "mean"), share_any=("n_prev", lambda s: (s > 0).mean()),
                                        regular_mean=("n_reg", "mean")).round(2).sort_values("before_mean", ascending=False)
h.to_csv(os.path.join(OUT, "3_6_hidden_by_offseason.csv"))
# does adding 'done before' bring a worker closer to some other job's regular pattern?
Mfull = {j: S[occ == j].mean(0) for j in jobs}
gain = []; switch = 0
for a in range(n):
    others = [j for j in jobs if j != occ[a]]
    s_strict = max(cos(S[a], Mfull[j]) for j in others)
    s_broad = max(cos(B[a], Mfull[j]) for j in others)
    gain.append(s_broad - s_strict)
    best_s = max(others, key=lambda j: cos(S[a], Mfull[j])); best_b = max(others, key=lambda j: cos(B[a], Mfull[j]))
    switch += (best_s != best_b)
R["hidden"].update(mean_gain_closest_other=float(np.mean(gain)), share_gain_positive=float((np.array(gain) > 0.005).mean()),
                   share_switch_nearest=float(switch / n))
# Jaccard version of strict vs broad overlap, worker to own job
fig, ax = plt.subplots(figsize=(6.2, 3.3))
ax.bar(h.index, h.before_mean, color="#55A868")
ax.set_ylabel("Tasks done before (average)"); ax.tick_params(axis="x", rotation=40, labelsize=7)
plt.setp(ax.get_xticklabels(), ha="right")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "3_6_hidden.png"), dpi=200); plt.close(fig)

# ---- tables for the write-up ----------------------------------------------
R["c1_rows"] = c1.reset_index().to_dict("records")
R["t33_rows"] = t33.reset_index().to_dict("records")
R["t5_rows"] = t5.reset_index().to_dict("records")
R["h_rows"] = h.reset_index().to_dict("records")
R["labels"] = LABEL
json.dump(R, open(os.path.join(HERE, "results_general.json"), "w"), indent=1, default=float)

# ---- console summary -------------------------------------------------------
print("counts", R["counts"])
print(c1.to_string())
print("top", R["task_prev_top"]); print("bottom", R["task_prev_bottom"])
print("group3", R["group3_overall"]); print("class5", R["class5_overall"])
print("nearest", *[(a, b, round(c, 2), d, round(e, 2)) for a, b, c, d, e in nn], sep="\n")
print("mean sim", R["job_sim_mean"]); print("clusters", R["clusters"]); print("clusters2", R["clusters2"])
print("R2", R["r2"]); print("pair", R["pair_cos"]); print("own closest", R["own_closest"], "median rank", R["own_rank_median"])
print(t5.to_string()); print("hidden", R["hidden"]); print(h.to_string())
print("task eta top", sorted(task_eta.items(), key=lambda x: -x[1])[:5], "bottom", sorted(task_eta.items(), key=lambda x: x[1])[:5])
