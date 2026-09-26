# Gap check against Fujii (2016), "Concepts and measurement of vulnerability to poverty
# and other issues: a review of literature"

Source read: `vulnerability-to-poverty/.md/Fujii - 2016 - Concepts and measurement of
vulnerability to poverty and other issues a review of literature.md`, sections 1–4
(intro, §2 concepts/measurement + empirical studies, §3 other vulnerability areas,
§4 discussion). References and front matter skipped.

Files checked against it:
- `replication/kedarnath_vtp_analysis.do`      (monetary VEP + MPI VEP + 3 robustness arms)
- `replication/final_instrument/do/03_employment_vulnerability.do` (employment VEP)
- `replication/final_instrument/questionnaire/dictionary.py`       (instrument)

Status: nothing below is implemented yet. Ordered by value-per-unit-effort within each group.

---

## A. Analysis gaps (code)

- [ ] **A1. No covariate vs. idiosyncratic risk split.** (Fujii §2.1 Ligon & Schechter 2003;
      §2.2 Günther & Harttgen 2009, who find risk-induced vulnerability dominates in urban
      and poverty-induced in rural Madagascar, and that covariate risk matters more rurally.)
      Every arm we run pools all residual variance into one `sigma2_hat`. For a **single
      pilgrimage route** where all respondents share the same season, weather, route closures
      and footfall, the covariate share is the substantively interesting part and we currently
      cannot report it. Blocked on B1 — the instrument has no covariate-shock item, so this is
      not identifiable from the data as it stands.

- [ ] **A2. No aggregate (social) vulnerability measure.** (Calvo & Dercon 2013, Fujii eq. 3.12;
      Fujii §2.1 "Second direction of extension".) Fujii's motivating example — profile *a*
      where one of three is poor in every state vs. profile *b* where all three are poor in one
      catastrophic state — is **exactly Kedarnath**: 2013 floods, COVID 2020–21, any yatra
      cancellation. Individual vulnerability is identical in both profiles; social vulnerability
      is not. Averaging `Vh` across households, which is all we do, discards this by
      construction. Calvo–Dercon's aggregate measure requires *sensitivity to correlation*.

- [ ] **A3. No poverty-induced vs. risk-induced decomposition.** (Günther & Harttgen 2009.)
      Our `vtp_group` is a 4-cell categorical cross-tab, not a decomposition of the vulnerability
      *magnitude* into a low-mean component and a high-variance component. Fujii's eq. 3.6/3.7
      (chronic/transient split of expected FGT) gives the quantitative version and notes it
      "qualitatively relates to Table 3.1" — i.e. our table is the qualitative shadow of a
      decomposition we never compute. Cheap: we already have `ln_c_hat` and `sd_c`.

- [ ] **A4. `vtp_group` mislabels chronic vs. transient relative to Suryahadi & Sumarto (2003).**
      *(Correctness issue, not an addition.)* Fujii Table 3.1: the chronic/transient axis is
      **expected** consumption vs. the line (chronic = poor *and* `E[c] < z`; transient = poor
      but `E[c] ≥ z`), with vulnerability `v` vs. `τ` as a **separate** third axis, giving six
      cells (A–F). Our code in both `kedarnath_vtp_analysis.do:194-197` and
      `03_employment_vulnerability.do:98-101` instead uses
      `chronic = currently_poor & vulnerable`, `transient = !currently_poor & vulnerable` —
      the axis is vulnerability status, not expected consumption, so "Chronic poor" and
      "Transient poor" do not mean what the cited source means by those words. `ln_c_hat` is
      already computed, so the correct 6-cell A–F table costs a few lines.

- [ ] **A5. Only γ=0 expected poverty is computed.** (Christiaensen & Subbarao 2005, Fujii
      eq. 3.5.) We report the probability of falling below the line and nothing about **how far
      below** or **how severely**. Expected FGT₁ and FGT₂ have closed forms under the
      log-normality we already assume, so this is a few lines in the monetary arm and gives a
      depth/severity result the current output cannot produce.

- [ ] **A6. The axiomatic critique of our own core measure is unacknowledged.** (Calvo & Dercon
      2005, 2013; Fujii §2.1 "Axiomatic approach".) Fujii states plainly that the expected
      poverty **rate** — eq. 3.2, which is the measure all three of our arms use — **fails
      Axiom 4 (probability transfer)**, and that expected FGT fails **Axiom 5 (risk sensitivity)**
      for γ ≤ 1. Fujii §4 recommends Calvo & Dercon (2013) as "an excellent starting point"
      precisely because it satisfies Axioms 1–9, and their measure reduces to the expected
      **Watts** or expected **Chakravarty** index — the Watts form has a closed expression under
      log-normality, so it is implementable in the existing FGLS pipeline. Minimum action: state
      the limitation. Better: add the expected-Watts arm alongside the three we have.

- [ ] **A7. No sensitivity sweep on τ.** We sweep γ (Gallardo, `kedarnath_vtp_analysis.do:370`)
      and φ (measurement error, `:389`) but hard-code `τ = 0.5` in all three arms without a
      citation. Fujii gives us both the justification and the test we are missing: Pritchett
      et al. (2000)'s focal-point argument plus the "an individual exactly at the line facing a
      symmetric zero-mean shock has v = 0.5" argument, and **Zhang & Wan (2009)**, who validate
      τ = 0.5 empirically against realised later-round poverty and find precision depends on
      both τ *and* the poverty line. Add a τ ∈ {0.3, 0.4, 0.5, 0.6} sweep; cite the above for
      the headline choice. Note Zhang & Wan's poverty-line finding interacts with HANDOFF
      open item 1.

- [ ] **A8. No time horizon is ever stated.** Fujii: "the time horizon is inherently relevant in
      the expected poverty approach." Our `Vh` is an unlabelled "next period" while the
      consumption module is explicitly two-season and the work module is a 12-month calendar.
      For a workforce with a ~6-month season this is substantive, not cosmetic. Also add the
      Pritchett et al. (2000) n-period form, `1 − (1 − v)^n` (risk of poverty at least once in
      n periods), which Fujii flags as a genuinely different quantity from the single-period v.

- [ ] **A9. Calvo (2008) multidimensional vulnerability not implemented.** (Fujii §2.1, "first
      direction of extension".) Our MPI arm uses Feeny & McDonald — collapse the dimensions to
      one `mpi_score`, *then* run VEP — which permits a good outcome in one dimension to
      compensate a bad one **before** the vulnerability step. Calvo (2008) censors each
      dimension at its own threshold (`q_ij ≤ 1`) and CES-aggregates with elasticity ρ, so full
      cross-dimension compensation is impossible by construction; Fujii presents this as *the*
      multidimensional extension. Calvo's own finding — the rural/urban vulnerability gap widens
      as ρ falls because rural shocks are more negatively correlated across dimensions — is a
      live question for our MPI and employment arms. Good robustness arm with a ρ sweep.

- [ ] **A10. Chiwaula et al. (2011) is cited for the wrong contribution.** We use it only for
      the mean-deviation criterion, via Gallardo (`kedarnath_vtp_analysis.do:312-318`). Fujii
      §3.2 describes its actual contribution as a three-way decomposition —
      **structural-chronic / structural-transient / stochastic-transient** — keyed to whether the
      asset base is too low to support permanent escape even under favourable conditions. We
      have an unusually good productive-asset block (Module F: pony/mule, shop/stall, work
      vehicle, work equipment, land, cattle, goats), and pony ownership is a lumpy productive
      asset — Dercon's cattle case almost exactly. Implementable and directly on-theme.

- [ ] **A11. No scenario / counterfactual simulation.** (Dercon & Krishnan 2000, via Fujii §2.2:
      predicted poverty under combinations of safety-net on/off × normal vs. bad rainfall ×
      seasonal prices on/off.) We have the 12-month income calendar, `income_seasonality_cv`,
      and a whole ropeway module (J) — but produce no counterfactual at all. A
      yatra-disruption × ropeway × safety-net scenario grid is the natural policy output of this
      project and currently does not exist. Highest policy value of anything in list A.

- [ ] **A12. Location is omitted from the covariate set.** *(Free fix — data already collected.)*
      Fujii §2.2 closes by naming **education and location** as the two covariates that emerge
      consistently across the entire empirical literature. We have education_years in
      `$Xvars_adapt`, but neither `location_cluster` (4 route clusters, Module P) nor `origin`
      (local / other Uttarakhand district / other Indian state / Nepal, Module D) enters
      `$Xvars` or `$Xemp` — only the derived `health_access_tier` carries any geography.
      `origin` also interacts with HANDOFF open item 1 (one national line for Nepal-origin
      workers): if origin is not in X, we cannot show that the pooled-line choice is innocuous.

- [ ] **A13. No welfarist arm; record this as a deliberate exclusion.** (Ligon & Schechter 2003;
      Elbers & Gunning 2003.) Requires specifying a utility function and estimating relative
      risk aversion, which Fujii names as the approach's main drawback — a defensible reason to
      skip it, but it should be *stated*, not silently absent, since Fujii treats welfarist as
      one of the field's three canonical approaches and we claim to cover the space. Note the
      L&S **decomposition** (A1) is separable from its CRRA specification and is worth having
      on its own.

---

## B. Instrument gaps (`dictionary.py`)

- [ ] **B1. The shock module cannot support the analysis the literature asks for.**
      `distress_event_last365d` (`dictionary.py:254`) records **one** shock — "Record the most
      serious one" — from four types (illness/death, crop or livestock loss, natural disaster
      damage, business/asset loss), and `kedarnath_vtp_analysis.do` then collapses even that to
      a binary `distress_any`. Fujii §4 singles this out as the field's binding data constraint:
      *"current surveys often do not contain sufficient information about the shocks that
      households face"*, pointing to Günther & Harttgen (2009)'s long inventory (malaria, TB,
      typhoid, cholera, pest, flooding, **impassible bridge or road**, drought, cyclone) and
      adding "asset losses, labour market disturbances, harvest failure and civil unrest."
      Two distinct problems:
      1. **One shock only.** Multiple shocks in a year cannot be recorded.
      2. **No covariate/site-level shock in the list at all** — no landslide or road/bridge
         closure (literally on Fujii's list), no yatra disruption or early closure, no
         weather/rainfall shock, no price shock. Everything in the list is household-idiosyncratic.
         This is what blocks A1: with no covariate shock item, the covariate/idiosyncratic
         decomposition is not identifiable from our data at any level of analytical effort.
      Note: HANDOFF open item 2 already requires building a `select_multiple` mechanism for
      `secondary_work_type`. This item is the second natural consumer of that mechanism — plan
      them together, not separately.

- [ ] **B2. No employment-guarantee / MGNREGA item.** Fujii §4 lists employment guarantee
      schemes as one of four policies that *directly* reduce vulnerability, and explains why
      they are special: self-targeting makes them a fallback option workers take only when
      nothing better exists — which is exactly the off-season position of this sample.
      `govt_scheme_beneficiary` (`dictionary.py:241`) is a single yes/no naming "ration, pension,
      cash transfer" and cannot identify public works. The project's own literature folder holds
      Khosla & Jena (2022), "Analyzing vulnerability to poverty and assessing the role of
      universal public works and food security" — the argument is already in the library.
      Cost: roughly 20 seconds (job card y/n + days worked in last 12 months). Weigh against
      HANDOFF open item 3 (46.4 min vs. the 45-min cap).

- [ ] **B3. A climate-hazard site with no hazard framing.** Fujii §3.1 (Adger 2006 — PDF already
      in `vulnerability-to-poverty/`; Fussel 2007's four dimensions: system / attribute of
      concern / **hazard** / **temporal reference**). Fujii's criticism is that VtP studies
      "abstract from specific hazards and analyze vulnerability from the perspective of
      stochastic consumption," and that policy choice depends on *which* hazard is at issue.
      At Kedarnath — 2013 disaster, monsoon landslides, glacial risk — that criticism stops
      being generic. Minimum action: name the system, attribute, hazard and temporal reference
      explicitly in the write-up. Better: one perceived-risk item. Connects to A8 and A11.

- [ ] **B4. Asset-smoothing vs. consumption-smoothing cannot be tested.** Fujii §3.2 on Carter &
      Zimmerman (2000) / Zimmerman & Carter (2003): households facing a survival constraint may
      **cut consumption to defend assets**, inverting the usual assumption. `shock_coping`
      (`dictionary.py:255`) and `morbidity_coping_15d` (`:247`) each take **one** answer from a
      list containing both "Sold or pawned assets" and "Cut consumption" — forcing a choice
      between precisely the two responses the theory says to compare. Third consumer of the
      multi-select mechanism from HANDOFF open item 2.

---

## C. Already correct — cite, don't change

These need no code change, but Fujii supplies support we currently assert without:

- **Cross-sectional VEP is defensible.** Our single-round design (HANDOFF: "one round, no
  phased/screener design") is the obvious referee target — how do you estimate a variance from
  one cross-section? Fujii §2.2 gives two direct validations: **Jha & Dang (2010)** compared
  cross-sectionally estimated vulnerability in PNG against *realised* poverty in a later round
  and found the prediction reasonably good ("reassuring because vulnerability studies based on
  cross-sectional data may still be informative"), and **Zhang & Wan (2009)** do the same in
  rural PRC. Neither is cited anywhere in our files. This is the single most useful defensive
  citation in the paper.
- **τ = 0.5** — Pritchett et al. (2000) focal-point argument + Zhang & Wan (2009) precision
  validation (see A7).
- **Downside asymmetry** (Gallardo semi-deviation arm) — **Kurosaki (2006)** independently
  motivates asymmetric treatment of positive vs. negative shocks.
- **Excluding risk-sharing tests is correct, and should be stated as a choice.** We hold Cochrane
  (1991) and Bold & Broer (2021) PDFs but run no Townsend-style test. Fujii §2.2 *justifies*
  that: citing **Klasen & Povel (2013)**, he notes the Amin et al. (2003) style measure "is at
  odds with the concept of vulnerability to poverty in the literature, because it is not an
  *ex ante* measure and ignores the current consumption level and the likelihood of adverse
  idiosyncratic and covariate shocks." Say this once rather than leaving a silent omission.
- **Seasonal price deflation** — HANDOFF open item 1 already flags that consumption is not
  price-deflated between season and off-season. Fujii §2.2 (Dercon & Krishnan 2000, whose third
  scenario dimension *is* seasonal price fluctuation) gives that limitation a citation.

---

## Suggested order

1. **A4** (correctness bug — mislabelled chronic/transient) and **A12** (free, data in hand).
2. **A7, A8, A5** — cheap additions to the existing FGLS pipeline, all closed-form.
3. **B1** — decide it with HANDOFF open item 2, since both need the same `select_multiple`
   mechanism; B4 rides along for free once that exists.
4. **A11** — highest policy payoff; needs no new data.
5. **A1/A3** — after B1 lands (blocked until then).
6. **A2, A6, A9, A10** — genuine methodological extensions, each roughly a paper section.
7. **A13, B2, B3, C** — write-up and framing, plus one costed instrument decision (B2).
