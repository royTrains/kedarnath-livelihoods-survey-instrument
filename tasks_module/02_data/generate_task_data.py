"""Makes a TEST dataset of answers to the task questions (T1-T3).

Purpose: check that the questions can be analysed. Every pattern here comes from the assumptions written
below, so nothing in it is a finding about real workers.

Starting point: the existing synthetic 200-person quota pool in ../../replication (read only; nothing there is changed).
"""
import os, sys, json
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.join(HERE, "..", "..", "replication", "kedarnath_synthetic_v2_n200_retention_flag.dta")
SEED = 20260921
rng = np.random.default_rng(SEED)

def logit(p): p = np.clip(p, 1e-6, 1 - 1e-6); return np.log(p / (1 - p))
def expit(x): return 1 / (1 + np.exp(-x))

# ---------- 1. who does which task, by job ----------
# Four levels of "regularly does this in the main Yatra work". Levels are our assumption.
LEVEL_P = {"core": 0.90, "common": 0.55, "occasional": 0.20, "rare": 0.03}

# core = tasks in the NCO-2015 description of the job (or, where NCO has no code, our judgement, marked *)
PROFILES = {
 "Pony worker": dict(core=[5, 3, 6], common=[4, 12, 14, 15, 16, 20, 23], occasional=[1, 9, 13, 17, 21, 22, 24],
                     evidence="NCO 9332.0400 Pack Animal Driver: loads and unloads animals, leads them, feeds them, cleans stables."),
 "Pony business": dict(core=[5, 14, 15, 16, 26], common=[3, 4, 6, 12, 17, 25], occasional=[1, 9, 13, 20, 21, 23, 24],
                     evidence="NCO 9332.0400 plus owner tasks (selling rides, cash, hiring handlers) from NCO 1120.2000 retail proprietor logic."),
 "Porter": dict(core=[1, 3], common=[4, 12, 13, 14, 15, 16, 23], occasional=[5, 9, 20, 21, 22, 24],
                     evidence="NCO 9621.9900 luggage porters and 9333.0100 loader and unloader."),
 "Palki": dict(core=[2, 1], common=[12, 13, 14, 15, 16, 22, 23], occasional=[3, 4, 9, 20, 21, 24],
                     evidence="*No NCO code. Judgement: carries passengers and loads; needs union check."),
 "Shopkeeper": dict(core=[14, 4, 20], common=[1, 15, 16, 17, 25], occasional=[3, 19, 21, 24, 26],
                     evidence="NCO 5223.0100 Shop Assistant: measures and packs goods, delivers, keeps shop tidy, sells."),
 "Shop owner": dict(core=[14, 15, 16, 17, 25], common=[4, 20, 24, 26], occasional=[1, 3, 13, 18, 21, 27],
                     evidence="NCO 1120.2000 Working Proprietor, Retail Trade: buys merchandise and sells it for profit."),
 "Hotel/lodging worker": dict(core=[19, 20], common=[1, 14, 16, 18, 24, 25], occasional=[3, 4, 9, 10, 15, 21, 22],
                     evidence="NCO 5131.0200 Steward Hotel, 5151.0800 Room Bearer, 9112.9900 hotel cleaners."),
 "Hotel/lodging owner": dict(core=[14, 16, 17, 25, 26], common=[15, 18, 19, 20, 24], occasional=[9, 10, 13, 21, 22, 27],
                     evidence="NCO 5151.0600 Hotel and Restaurant Keeper: buys supplies, appoints staff, serves guests, collects money."),
 "Wage labourer": dict(core=[1, 3, 11], common=[4, 8, 9, 20], occasional=[5, 6, 7, 10, 12, 23],
                     evidence="NCO 9313.9900 Building Construction Labourers: simple routine tasks in construction."),
 "Other": dict(core=[], common=[1, 4, 14, 16, 20], occasional=[3, 9, 11, 15, 17, 19, 24, 25],
                     evidence="Mixed group; no single NCO code."),
 "Driver": dict(core=[7, 16], common=[9, 12, 13, 14, 15, 24], occasional=[1, 3, 4, 8, 20, 21, 22, 23, 25],
                     evidence="NCO 8322.0501 Light Motor Vehicle Driver: drives safely on an assigned route; fares from NCO cashier logic."),
 "Dhaba/food-stall owner": dict(core=[14, 16, 17, 18], common=[15, 19, 20, 25, 26], occasional=[1, 3, 4, 21, 24],
                     evidence="NCO 5212.9900 Street Food Vendors (Dhabawala) and 5151.0600 Hotel and Restaurant Keeper."),
 "Guide": dict(core=[21], common=[13, 14, 15, 16, 22, 24], occasional=[1, 17, 20, 23, 25, 27],
                     evidence="NCO 5113.0200 Tourist Guide: guides visitors, explains sites, answers questions, may assist shopping."),
}
PRIMARY = {"Pony worker": 5, "Pony business": 5, "Porter": 1, "Palki": 2, "Shopkeeper": 14, "Shop owner": 14,
           "Hotel/lodging worker": 19, "Hotel/lodging owner": 26, "Wage labourer": 11, "Other": None,
           "Driver": 7, "Dhaba/food-stall owner": 18, "Guide": 21}
TASKS = list(range(1, 28))

def base_matrix():
    """occupation x task matrix of base probabilities"""
    M = {}
    for occ, pr in PROFILES.items():
        row = {t: LEVEL_P["rare"] for t in TASKS}
        for lvl in ("occasional", "common", "core"):
            for t in pr[lvl]:
                row[t] = LEVEL_P[lvl]
        M[occ] = row
    return M
BASE = base_matrix()

# ---------- 2. "done before elsewhere": boosts (logit units) by off-season activity ----------
ACT_BOOST = {
 "Agriculture": {6: 1.6, 1: 1.0, 3: 0.8, 11: 0.5, 5: 0.6, 9: 0.4},
 "Wage labour elsewhere": {1: 1.2, 3: 1.4, 4: 1.0, 11: 1.6, 8: 0.8, 9: 0.8, 10: 0.4, 20: 0.4},
 "Migrated for work": {7: 0.8, 18: 1.0, 19: 1.0, 20: 1.0, 9: 0.8, 16: 0.8, 14: 0.8, 8: 0.8, 10: 0.5, 25: 0.5, 24: 0.6},
 "Petty trade/other": {14: 1.6, 15: 1.6, 16: 1.6, 17: 1.4, 4: 0.8, 25: 0.6},
 "Animal husbandry": {6: 2.0, 5: 1.0, 1: 0.6},
 "Salaried job": {25: 1.4, 16: 1.0, 24: 1.0, 26: 0.8, 14: 0.6, 12: 0.6},
 "No other work": {},
}
EDU_TASKS = {12, 13, 16, 25, 26, 27}      # tasks that lean on schooling

def main():
    df = pd.read_stata(POOL)
    n = len(df)
    edu = df["education_years"].fillna(6.0).to_numpy()      # 'prefer not to say' -> 6 for generation only
    yrs = df["years_in_yatra_work"].to_numpy(); age = df["age"].to_numpy()
    occ = df["occupation"].to_numpy(); act = df["offseason_primary"].to_numpy()
    v = rng.normal(0, 0.6, n)                              # 'does more of everything' latent

    # previous different occupation: borrows tasks from one other job
    prev = df["prev_occ_change"].to_numpy() == 1
    occs = list(PROFILES)
    prev_occ = np.array([rng.choice([o for o in occs if o != occ[i]]) if prev[i] else "" for i in range(n)], dtype=object)

    T1 = np.zeros((n, 27), dtype=int)
    for i in range(n):
        for t in TASKS:
            p = expit(logit(BASE[occ[i]][t]) + v[i] + 0.05 * (yrs[i] - 5.8) + (0.08 * (edu[i] - 7.6) if t in EDU_TASKS else 0))
            if rng.random() < p:
                T1[i, t - 1] = 1
        if T1[i].sum() == 0:                              # everybody does at least one regular task
            best = max(TASKS, key=lambda t: BASE[occ[i]][t]); T1[i, best - 1] = 1
    regular = T1.copy()

    T1code = np.where(regular == 1, 1, 3)
    for i in range(n):
        boost = ACT_BOOST.get(act[i], {})
        pb = {}
        if prev_occ[i]:
            pr = PROFILES[prev_occ[i]]
            for t in pr["core"]: pb[t] = 1.8
            for t in pr["common"]: pb[t] = max(pb.get(t, 0), 1.0)
        for t in TASKS:
            if regular[i, t - 1] == 0:
                q = expit(logit(0.06) + boost.get(t, 0) + pb.get(t, 0) + 0.03 * (age[i] - 38) + 0.8 * v[i])
                if rng.random() < q:
                    T1code[i, t - 1] = 2

    # main task
    main_task = np.zeros(n, dtype=int)
    for i in range(n):
        reg = [t for t in TASKS if T1code[i, t - 1] == 1]
        pt = PRIMARY[occ[i]]
        if pt is not None and pt in reg:
            main_task[i] = pt
        else:
            main_task[i] = max(reg, key=lambda t: BASE[occ[i]][t] + rng.random() * 0.01)

    out = df[["resp_id", "occupation", "employment_type", "offseason_primary", "age", "education_years", "migrant", "origin",
              "location_cluster", "years_in_yatra_work", "prev_occ_change", "retained"]].copy()
    for t in TASKS:
        out[f"t1_{t:02d}"] = T1code[:, t - 1]
    out["t1_28"] = main_task
    out["prev_occ_borrowed_from"] = prev_occ

    # ---------- T2 ----------
    LIFT = {"Porter": .95, "Palki": .80, "Pony worker": .70, "Pony business": .50, "Wage labourer": .60, "Shopkeeper": .25,
            "Shop owner": .20, "Hotel/lodging worker": .30, "Hotel/lodging owner": .10, "Driver": .15, "Dhaba/food-stall owner": .20,
            "Guide": .05, "Other": .30}
    OWNERS = {"Pony business", "Shop owner", "Hotel/lodging owner", "Dhaba/food-stall owner"}
    OWN_ACC = OWNERS | {"Pony worker", "Porter", "Palki", "Driver", "Guide"}
    CUST = {"Palki": .95, "Porter": .85, "Pony worker": .85, "Pony business": .85, "Shopkeeper": .95, "Shop owner": .95,
            "Hotel/lodging worker": .85, "Hotel/lodging owner": .85, "Wage labourer": .10, "Driver": .98,
            "Dhaba/food-stall owner": .98, "Guide": .99, "Other": .50}
    LEARN_MONTHS = {"Porter": 2, "Palki": 3, "Pony worker": 6, "Pony business": 12, "Shopkeeper": 4, "Shop owner": 12,
                    "Hotel/lodging worker": 4, "Hotel/lodging owner": 24, "Wage labourer": 1, "Driver": 12,
                    "Dhaba/food-stall owner": 12, "Guide": 18, "Other": 3}
    carry = (out["t1_01"] == 1) | (out["t1_02"] == 1) | (out["t1_05"] == 1)
    trips = np.where(carry, 1 + np.minimum(rng.poisson(0.6, n), 2), np.nan)
    out["t2_01"] = trips
    out["t2_02"] = [1 if rng.random() < LIFT[o] else 2 for o in occ]
    out["t2_03"] = [1 if rng.random() < (0.45 if o in OWNERS else 0.30 if o == "Guide" else 0.75) else 2 for o in occ]
    out["t2_04"] = [1 if rng.random() < (0.50 if o in OWNERS else 0.60 if o == "Guide" else 0.30) else 2 for o in occ]
    def decide(o):
        if o in OWN_ACC: pr = [.65, .30, .05]
        elif o in ("Shopkeeper", "Hotel/lodging worker"): pr = [.05, .20, .75]
        elif o == "Wage labourer": pr = [.15, .15, .70]
        else: pr = [.35, .30, .35]
        return int(rng.choice([1, 2, 3], p=pr))
    out["t2_05"] = [decide(o) for o in occ]
    out["t2_06"] = [1 if rng.random() < CUST[o] else 2 for o in occ]
    mean_dir = {"Shop owner": 1.5, "Hotel/lodging owner": 3.0, "Pony business": 2.0, "Dhaba/food-stall owner": 1.0}
    out["t2_07"] = [max(1, 1 + rng.poisson(mean_dir.get(o, 0.5))) if T1code[i, 25] == 1 else 0 for i, o in enumerate(occ)]
    out["t2_08"] = [max(1, int(round(rng.lognormal(np.log(LEARN_MONTHS[o]), 0.5)))) for o in occ]

    # ---------- T3 ----------
    edu_c = edu - 7.6
    boost = np.array([0.8 if o in OWNERS | {"Shopkeeper", "Hotel/lodging worker", "Guide", "Driver"} else 0.0 for o in occ])
    read = rng.random(n) < expit(-1.5 + 0.35 * edu + boost - 1.0 * 0)   # more schooling, more reading at work
    write = np.where(read, rng.random(n) < expit(0.6 + 0.10 * edu_c), rng.random(n) < 0.10)
    sells = (out["t1_14"] == 1) | (out["t1_16"] == 1)
    calc = np.where(out["t1_16"] == 1, rng.random(n) < 0.92, np.where(out["t1_14"] == 1, rng.random(n) < 0.80, rng.random(n) < 0.35))
    calc = calc & (rng.random(n) < expit(1.5 + 0.15 * edu_c))
    mult = np.where(calc, rng.random(n) < expit(-0.5 + 0.2 * edu + 0.3), rng.random(n) < 0.10)
    lack = rng.random(n) < np.clip(expit(-2.2 - 0.25 * edu_c) + 0.10 * (edu < 5), 0, 1)
    out["t3_01"] = np.where(read, 1, 2); out["t3_02"] = np.where(write, 1, 2)
    out["t3_03"] = np.where(calc, 1, 2); out["t3_04"] = np.where(mult, 1, 2); out["t3_05"] = np.where(lack, 1, 2)

    origin = df["origin"].to_numpy()
    def lang(o_origin, o_occ, e):
        hind = 0.70 if o_origin == "Nepal" else 0.97
        garh = {"Local (same district)": .98, "Other Uttarakhand district": .65, "Other Indian state": .25, "Nepal": .10}[o_origin]
        nep = .99 if o_origin == "Nepal" else .06
        eng = expit(-3.4 + 0.22 * e + (1.5 if o_occ == "Guide" else 0.8 if o_occ in ("Hotel/lodging owner", "Hotel/lodging worker", "Dhaba/food-stall owner", "Driver") else 0))
        return hind, garh, nep, eng, 0.05
    sp = np.zeros((n, 5), dtype=int); rw = np.zeros((n, 5), dtype=int)
    for i in range(n):
        ps = lang(origin[i], occ[i], edu[i])
        for k, p in enumerate(ps):
            sp[i, k] = int(rng.random() < p)
        hrw = expit(-1.8 + 0.4 * edu[i]) * sp[i, 0]
        rw[i, 0] = int(rng.random() < hrw)
        rw[i, 1] = int(sp[i, 1] and rng.random() < 0.25 * expit(-1.8 + 0.4 * edu[i]))
        rw[i, 2] = int(sp[i, 2] and rng.random() < 0.5 * expit(-1.8 + 0.4 * edu[i]))
        rw[i, 3] = int(sp[i, 3] and rng.random() < expit(-1.0 + 0.25 * edu[i]))
        rw[i, 4] = int(sp[i, 4] and rng.random() < 0.3)
    for k, name in enumerate(["hindi", "garhwali", "nepali", "english", "other"]):
        out[f"t3_06_{name}"] = sp[:, k]; out[f"t3_07_{name}"] = rw[:, k]

    smart = df["smartphone_owned"].to_numpy() == 1
    phone = np.where(smart, "smartphone_own", np.where(rng.random(n) < 0.08, "smartphone_shared", np.where(rng.random(n) < 0.90, "basic", "none")))
    out["t3_08"] = phone
    has_phone = phone != "none"; has_smart = np.isin(phone, ["smartphone_own", "smartphone_shared"])
    dp = df["digital_payment_use"].astype(str).to_numpy()
    out["t3_09_calls"] = has_phone.astype(int)
    out["t3_09_msg"] = np.where(has_smart, (rng.random(n) < 0.95).astype(int), (rng.random(n) < 0.05).astype(int) * has_phone)
    net = np.where(has_smart, (rng.random(n) < 0.75).astype(int), 0)
    upi = np.where(has_smart & (dp != "Never"), 1, 0)
    out["t3_09_net"] = np.maximum(net, upi); out["t3_09_upi"] = upi
    owner_like = np.array([o in OWNERS | {"Guide", "Hotel/lodging worker"} for o in occ])
    out["t3_10"] = np.where(rng.random(n) < expit(-3.0 + 0.25 * edu + 0.7 * owner_like), 1, 2)

    trained = df["training_received"].to_numpy() == 1
    ttype = df["training_type"].astype(str).to_numpy()
    out["t3_11"] = np.where(trained, 1, 2)
    def course_type(i):
        o = occ[i]
        if o == "Driver" and rng.random() < 0.7: return "driving"
        if o == "Guide": return "guiding or trekking"
        if o in ("Hotel/lodging worker", "Hotel/lodging owner", "Dhaba/food-stall owner") and rng.random() < 0.7: return "cooking or hospitality"
        if o == "Wage labourer" and rng.random() < 0.6: return "building trades"
        if o in ("Pony worker", "Pony business") and rng.random() < 0.5: return "animal care"
        pool = ["cooking or hospitality", "guiding or trekking", "first aid or safety"] if ttype[i] == "Tourism/hospitality" else \
               ["driving", "electrical or technical", "building trades", "animal care", "other"]
        return rng.choice(pool)
    out["t3_12"] = [course_type(i) if trained[i] else "" for i in range(n)]
    cert = np.where(trained, (rng.random(n) < np.where(ttype == "Tourism/hospitality", .7, .6)).astype(int), 0)
    out["t3_13"] = np.where(trained, np.where(cert == 1, 1, 2), np.nan)
    prov = rng.choice(["government scheme", "NGO", "private", "union or association", "employer"], size=n, p=[.45, .20, .20, .05, .10])
    out["t3_14"] = np.where(trained, prov, "")

    def lic(p_by_occ, default):
        return np.array([int(rng.random() < p_by_occ.get(o, default)) for o in occ])
    out["t3_15_twowheeler"] = np.where(age < 25, (rng.random(n) < .15).astype(int), lic({"Driver": .90}, .30))
    out["t3_15_car"] = lic({"Driver": .90, "Shop owner": .25, "Hotel/lodging owner": .25, "Pony business": .20}, .12)
    out["t3_15_heavy"] = lic({"Driver": .12}, .01)
    out["t3_15_guide"] = lic({"Guide": .75}, .01)
    out["t3_15_food"] = lic({"Dhaba/food-stall owner": .50, "Hotel/lodging owner": .50}, .02)
    voc_cert = (ttype == "Vocational/trade") & (cert == 1)
    out["t3_15_iti"] = np.where(voc_cert, (rng.random(n) < .35).astype(int), lic({"Hotel/lodging worker": .10, "Wage labourer": .08}, .04))
    out["t3_15_firstaid"] = lic({"Guide": .35, "Pony worker": .05, "Porter": .05, "Palki": .05}, .04)
    out["t3_15_security"] = lic({}, .02)
    lic_cols = [c for c in out.columns if c.startswith("t3_15_")]
    out["t3_15_none"] = (out[lic_cols].sum(axis=1) == 0).astype(int)
    anyl = out[lic_cols].sum(axis=1) > 0
    out["t3_15_seen"] = np.where(anyl, (rng.random(n) < .6).astype(int), np.nan)

    FAM = {"Pony business": .6, "Palki": .4, "Shop owner": .4, "Hotel/lodging owner": .4, "Pony worker": .3, "Porter": .2}
    out["t3_16_family"] = [int(rng.random() < FAM.get(o, .15)) for o in occ]
    out["t3_16_watching"] = (rng.random(n) < .75).astype(int)
    out["t3_16_onjob"] = (rng.random(n) < .90).astype(int)
    out["t3_16_own"] = (rng.random(n) < .20).astype(int)
    out["t3_16_course"] = np.where(trained, 1, 0)
    lcols = [c for c in out.columns if c.startswith("t3_16_")]
    none_l = out[lcols].sum(axis=1) == 0
    out.loc[none_l, "t3_16_onjob"] = 1

    # ---------- checks ----------
    log = []
    def check(name, ok):
        log.append((name, bool(ok))); assert ok, name
    t1cols = [f"t1_{t:02d}" for t in TASKS]
    check("all 27 task answers are 1, 2 or 3 with no missing", out[t1cols].isin([1, 2, 3]).all().all())
    check("every worker has at least one regular task", (out[t1cols] == 1).sum(axis=1).min() >= 1)
    check("main task is a task coded 1", all(out.loc[i, f"t1_{int(out.loc[i, 't1_28']):02d}"] == 1 for i in out.index))
    check("people directed (t2_07) is at least 1 exactly when 'supervise or hire' (t1_26) is coded 1",
          ((out["t2_07"] >= 1) == (out["t1_26"] == 1)).all())
    check("trips per day is asked only when a carrying or animal task is coded 1",
          (out["t2_01"].notna() == ((out["t1_01"] == 1) | (out["t1_02"] == 1) | (out["t1_05"] == 1))).all())
    check("course type recorded exactly when a course was taken", ((out["t3_12"] != "") == (out["t3_11"] == 1)).all())
    check("digital payments imply a smartphone and internet", ((out["t3_09_upi"] == 0) | ((out["t3_09_net"] == 1) & out["t3_08"].isin(["smartphone_own", "smartphone_shared"]))).all())
    check("read/write in a language implies speaking it", all(((rw[:, k] == 0) | (sp[:, k] == 1)).all() for k in range(5)))
    check("writing at work implies more than chance of reading (no writer without reader more than 12%)", ((out["t3_02"] == 1) & (out["t3_01"] == 2)).mean() < 0.12)
    check("palki bearers do the 'carry a passenger' task regularly (most of them)", (out.loc[out.occupation == "Palki", "t1_02"] == 1).mean() > 0.7)
    check("drivers hold a car licence (most of them)", out.loc[out.occupation == "Driver", "t3_15_car"].mean() > 0.7)

    out.to_csv(os.path.join(HERE, "tasks_synth_full.csv"), index=False, encoding="utf-8")
    fld = out[out["retained"] == 1].copy()
    fld.to_csv(os.path.join(HERE, "tasks_synth_fielded.csv"), index=False, encoding="utf-8")
    try:
        out.to_stata(os.path.join(HERE, "tasks_synth_full.dta"), write_index=False, version=118)
        fld.to_stata(os.path.join(HERE, "tasks_synth_fielded.dta"), write_index=False, version=118)
    except Exception as e:
        print("dta export skipped:", e)

    prof = pd.DataFrame([dict(occupation=k, core=",".join(map(str, v_["core"])), common=",".join(map(str, v_["common"])),
                              occasional=",".join(map(str, v_["occasional"])), evidence=v_["evidence"]) for k, v_ in PROFILES.items()])
    prof.to_csv(os.path.join(HERE, "occupation_profiles.csv"), index=False, encoding="utf-8")
    json.dump(dict(seed=SEED, n_full=int(len(out)), n_fielded=int(len(fld)), level_p=LEVEL_P, checks=log),
              open(os.path.join(HERE, "generation_log.json"), "w"), indent=1)
    print(f"full n={len(out)}, fielded n={len(fld)}; checks passed: {sum(ok for _, ok in log)}/{len(log)}")

if __name__ == "__main__":
    main()
