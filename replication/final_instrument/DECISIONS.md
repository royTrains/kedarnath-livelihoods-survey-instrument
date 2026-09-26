# Decision register — what actually needs editing, and why

Consolidates `FUJII_2016_GAPS.md` (analysis vs. the VtP literature) and `INSTRUMENT_GAPS.md`
(questionnaire vs. the research goal) into a single ranked judgment. Nothing here is applied;
every line is a proposal awaiting sign-off.

Status key: `[ ]` proposed · `[x]` approved+done · `[-]` rejected · `[?]` needs a decision

---

## Part 1 — Skill distance: method re-verification (2026-09-24)

Re-derived from source, not from memory.

**The current implementation is correct.** `tasks_module/03_analysis/general_analysis.py:106-116`
builds `M = S[occ==j].mean(0)` — the fraction of workers in occupation *o* who perform task *j* —
then takes the cosine between occupation vectors and uses `1 - sim` as distance. That is exactly
Gathmann & Schönberg (2010, §III): their `q_oj` is defined as "the fraction of workers in an
occupation performing task *j*", the distance is the angular separation (uncentered correlation)
of `q_o` and `q_o′`, and their reported measure is `Dis_oo′ = 1 − AngSep_oo′`, bounded [0,1].
No change needed to the estimator itself.

**The three-answer, no-scale grid is not a compromise — it is precisely G&S's input.** G&S build
`q_oj` from binary per-worker task incidence aggregated within occupation; they never use an
intensity rating. The "no 1–5 scales" commitment therefore costs nothing here and should be
written up as a design strength, not a limitation. (G&S fn. 9: angular separation is insensitive
to vector length, unlike Euclidean — the right property when occupations differ in how many
tasks they use at all.)

### REFRAMED 2026-09-24 (user): the question is structural displacement, not ropeway hiring

The object is **not** "how many can be ropeway operators." It is: how many workers can transfer
their skills to *any* viable line of work **in the region** — including but not limited to the jobs
the government claims the ropeway will create, and including each respondent's **own stated target
occupation**. The quantity of interest is the complement: how many are **structurally displaced**,
i.e. have no viable regional destination.

This is a named, peer-reviewed construct, and it is a better fit than a single-destination distance.
**Martins-Neto et al.**, following Eggenberger et al. (2022), define the **Occupational Commonality
Index**: `OCI_im = Σ_j JSI_ij · L_jm`, the average skill distance from occupation *i* to every other
occupation *j*, **weighted by the relative employment of *j* in region *m*** — explicitly "to weight
the skill distances by the number of alternative jobs available to a worker." They validate it:
workers in occupations with a stronger commonality network have shorter unemployment spells and are
more likely to switch occupations after displacement.

Adopting OCI dissolves M2. We no longer need one authoritative ropeway-operator vector; we need the
**regional destination set with employment weights**, in which ropeway jobs are simply one entry —
carrying the government's *claimed* employment weight, which is precisely the claim under test:

- `OCI_before` — commonality against the current regional employment mix.
- `OCI_after`  — the same, with the claimed ropeway jobs added at their claimed weights and
  trek-dependent employment reduced.
- `ΔOCI` per worker — the policy's effect on that worker's structural position. Directly testable,
  directly falsifiable, and it is the government's own number doing the work.

Weights come from district employment data (Census / PLFS at NCO codes for Rudraprayag), the
project's own Yatra-workforce enumeration (already planned for the quota recalibration), and the
ropeway DPR / tender documents for the claimed jobs.

### What is *not* settled

- [?] **M1. The measure is symmetric; the research question is not.** G&S distance is symmetric by
      construction. Nawakitphaitoon & Ormiston (2016) show the skills approach (Ormiston 2014) is
      deliberately **asymmetric**: `t_ij = shared / total-used-in-i`, so `t_ij ≠ t_ji`, and
      "occupational switches from complex to simple jobs result in the obsolescence of previously
      applicable skills, reflecting lower transferability rates." Our question — *can a porter take
      a ropeway job?* — is directional. A symmetric number cannot distinguish "a porter already has
      most of what a ropeway operator needs" from "a ropeway operator has most of what a porter
      needs." **Proposal: report Ormiston-style directional transferability as the headline and keep
      G&S angular distance as the symmetric robustness measure.** Both run off the same task matrix;
      no new questions.

- [?] **M2. The destination task vector has no established source.** This is the biggest hole in the
      whole transferability strand. No respondent is a ropeway operator, so `q_oj` for the
      destination **cannot come from our survey**. `dictionary.py` cites NCO 8343.1700 for
      `tk_engine`, `tk_safety` and `tk_coord`, but NCO gives narrative job descriptions, not
      task-incidence fractions, so it cannot produce a comparable 12-dimensional vector on its own.
      Options: (a) crosswalk to O*NET's Generalized Work Activities for the analogous SOC code and
      rescale; (b) structured expert coding of the 12 tasks against the ropeway job descriptions;
      (c) both, and report the distance under each. **Until this is resolved there is no displacement
      estimate, only an abstract distance matrix.**

- [?] **M3. Shaw's market approach is structurally impossible here — say so explicitly.** N&O note the
      market approach "must be driven by demand. If there is little demand for a given occupation,
      there will be little movement into it (i.e. low transferability), even from very similar
      occupations." The ropeway does not exist, so observed mobility into ropeway work is zero and
      the market measure would return ~zero transferability for the one destination that matters.
      The skills approach is therefore **forced, not preferred** — a point worth making in the
      write-up, since it pre-empts the obvious referee question.

- [?] **M4. Answer code 2 is being discarded, and it is the most valuable answer we have.** The strict
      matrix uses only code 1 (`general_analysis.py:24`). Code 2 — "not in my main work, but done
      before elsewhere" — is *revealed prior capability outside the current job*, which G&S's
      occupation-level data cannot observe at all. Bächli et al. (2024) is the worker-level analogue:
      they build a **worker profile** `c_ij` and obtain "a worker-specific distance for every possible
      occupation," weighting the measured profile against the previous occupation. Our question is
      "how many *workers* are displaced", which is a per-worker quantity; the current code gives every
      worker in an occupation the same distance. **Proposal: build worker-level vectors from codes
      1+2 and compute per-worker distance to the destination. Analysis-only change, no new questions.**

- [?] **M5. Precision: `q_oj` will be noisy at our n.** G&S had 30,000 employees. We expect ~250–320
      across 13 occupations, so ~20–25 per cell; the standard error of a proportion at p≈0.5, n=20 is
      about 0.11, and cosines between noisy vectors are biased. **Proposal: bootstrap the distance
      matrix and report CIs; collapse the 13 occupations to ~5–6 groups for the distance work
      specifically** (keeping 13 for everything else). This is a reporting honesty issue, not a fix.

- [?] **M6. Which 12 of the 27 tasks get fielded is doing a lot of unexamined work.** The fielded 12
      lean toward the destination (NCO 8343.1700 appears three times) but drop several items that
      strongly discriminate among *source* occupations — `t1_05` lead/control pack animals, `t1_13`
      judge whether weather or route is safe, `t1_15` bargain over prices, `t1_23` keep order among
      crowds, `t1_26` supervise or hire. A distance matrix needs to separate the sources as well as
      reach the destination. **Proposal: re-pick the 12 against both criteria before fielding.**
      The block stays 12 items and stays short.

---

## Part 2 — Necessary edits (the research question fails without these)

- [ ] **N1. Destination task vector.** See M2. Methods blocker for the entire ropeway strand.
- [ ] **N2. Module J rework.** 2 items / 2.2% of an instrument built to study a ropeway. Needs the
      destination-and-intention side (pilot's `opp_*` battery + `willing_to_learn_skills`, compressed).
      Without it Module L is skill supply with no demand or intention side. `INSTRUMENT_GAPS.md` G1a/G1b.
- [ ] **N3. Retrospective covariate-shock block.** The 2013 floods and the COVID closures are the only
      covariate shocks this workforce has actually lived through, and the only empirical basis for
      calibrating a ropeway scenario in a single cross-section. Also unblocks Fujii A1 (covariate vs.
      idiosyncratic decomposition) and A11 (scenario simulation). `INSTRUMENT_GAPS.md` G3b / Fujii B1.
- [ ] **N4. Savings and debt stock.** Adaptive capacity is currently four binaries and a year count
      with no stock measure of anything. `credit_source` records who lent, not what is owed. Core to
      the Azeem structure the analysis claims to use. `INSTRUMENT_GAPS.md` G2a/G2b.
- [ ] **N5. `vtp_group` chronic/transient relabel.** A correctness bug, not an addition: our axis is
      vulnerability status, Suryahadi & Sumarto's is *expected* consumption. `ln_c_hat` already exists.
      Fujii A4.
- [ ] **N6. Disability item.** Needed for the Lyons et al. MPI-VEP arm (Washington Group), which is an
      explicitly wanted output; also in Apablaza's demographic preamble. Dropped in Stage 11.

## Part 3 — Strongly recommended (cheap, high value)

- [ ] **R1. `dist_to_ropeway` constructed from GPS.** Free; zero interview time; better than the pilot's
      question, which returned 43% "don't know". `INSTRUMENT_GAPS.md` G1c.
- [ ] **R2. `hh_members_in_yatra_work`.** One item. Household-level exposure concentration, which
      `yatra_income_share` (a respondent share) cannot express. G3c.
- [ ] **R3. Location and origin into the covariate set.** Free — both already collected, neither enters
      `$Xvars`/`$Xemp`. Fujii names location and education as the two consistently significant
      covariates in the whole empirical literature. Fujii A12.
- [ ] **R4. τ sensitivity sweep + an explicit time horizon.** We sweep γ and φ but hard-code τ=0.5 with
      no citation, and never state the horizon. Fujii A7/A8.
- [ ] **R5. Worker-level task vectors from codes 1+2.** See M4. Analysis-only.

## Part 4 — Optional, after the above

- [ ] O1. Expected FGT₁/FGT₂ (depth and severity of future poverty) — Fujii A5, closed form.
- [ ] O2. Calvo–Dercon aggregate vulnerability (A2) · expected Watts (A6) · Calvo 2008 multidimensional
      (A9) · Chiwaula structural/stochastic decomposition (A10). Each ≈ one paper section.
- [ ] O3. Dercon–Krishnan scenario simulation (A11) — blocked on N3.
- [ ] O4. Asset resale/replacement value (G2c) · shock magnitude (G3a).
- [ ] O5. Apablaza Q25 (why previous job was lost) — see rejection note below; may not be coherent here.
- [ ] O6. MGNREGA / public-works item (Fujii B2).

## Part 5 — Recommend against

- [-] **X1. Welfarist VEP arm (Ligon–Schechter / Elbers–Gunning).** Needs a utility function and a
      relative-risk-aversion estimate; Fujii names this as the approach's main drawback. Document the
      exclusion; do not implement. The L&S *decomposition* is separable and is covered by N3/Fujii A1.
- [-] **X2. Townsend-style risk-sharing tests.** Fujii, citing Klasen & Povel (2013), says these are
      "at odds with the concept of vulnerability to poverty… not an *ex ante* measure". Correct to
      exclude; state it once rather than leaving a silent omission.
- [-] **X3. Shaw market-approach transferability.** Structurally impossible here — see M3.
- [-] **X4. `ropeway_stance`.** The weakest item in the instrument: an attitude with no role in any of
      the three VEP arms. Cut it if Module J is rebuilt.

---

## Open questions for the user

1. **M2** — where should the destination (ropeway job) task vector come from?
2. **N2/N6/O5** — approve the Module J rework, the disability item, and a ruling on Apablaza Q25.
3. **M6** — re-pick which 12 of the 27 tasks are fielded, or leave the current set?
