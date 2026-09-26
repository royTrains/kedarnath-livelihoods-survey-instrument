*=============================================================================
* KEDARNATH YATRA LIVELIHOODS -- VULNERABILITY TO POVERTY ANALYSIS
*
* Two parallel VtP estimations on the same n~125 as-fielded sample:
*   (A) MONETARY   -- Chaudhuri et al. (2002) VEP, welfare = ln(cons_pc_pm),
*                      threshold = Rs.2,515/month (Sethu et al. 2024, Review
*                      of Agrarian Studies -- Rangarajan Expert Group (2014)
*                      method re-implemented directly on HCES 2022-23 rural
*                      microdata). Rs.1,850/month (Rangarajan & Dev 2024,
*                      CPI-adjusted) kept as `poor_sensitivity_cpi` for a
*                      poverty-line robustness check -- see generation do-file.
*   (B) MULTIDIMENSIONAL -- Alkire-Foster MPI deprivation score (NITI Aayog
*                      National MPI structure: Health/Education/Standard of
*                      Living, 1/3 weight each), VEP applied via the FM
*                      (Feeny & McDonald 2016) approach: same Chaudhuri
*                      mean-variance machinery, run on the deprivation score
*                      instead of log-consumption, with the inequality
*                      flipped (vulnerable = Pr(score EXCEEDS the cutoff)).
*
* Then THREE robustness checks:
*   1. Multi-criterion comparison on the monetary arm (Chaudhuri / Chiwaula
*      mean-deviation / Gallardo downside mean-semi-deviation) -- same
*      mean/variance, three different vulnerability thresholds.
*   2. Pritchett et al. (2000) / Azeem et al. (2016) measurement-error
*      perturbation: re-estimate assuming up to 50% of the estimated
*      variance is measurement error, not real risk.
*   3. Inverse probability weighting (IPW) for the non-random attrition
*      built into the as-fielded sample -- only feasible here because the
*      data is synthetic and we retained covariates for the dropped
*      observations too; a real fieldwork refusal would not offer this.
*
* Everything below is SYNTHETIC data. Every number this do-file produces is
* a demonstration of the pipeline, not an empirical finding about Kedarnath.
*=============================================================================

clear all
set more off
cd "D:\OneDrive\Desktop\vulnerability-2-poverty\replication"          // <-- change to your working folder
capture log close
log using "kedarnath_vtp_analysis_log.log", replace text

* esttab (for the two summary tables below) needs the estout package:
*   ssc install estout
* if you don't have it, comment out the two "esttab ... using" blocks --
* nothing else in this do-file depends on it.

use "kedarnath_synthetic_v2_n125_asfielded.dta", clear

*=============================================================================
* PART 1 -- DERIVED COVARIATES, ORGANIZED IN THE ADAPTIVE CAPACITY /
* SENSITIVITY / EXPOSURE FRAMEWORK (following Azeem, Mugera & Schilizzi
* 2016, Table 2 -- the same three-part structure used in the paper whose
* Chaudhuri-method replication this extends).
*=============================================================================

* -- income seasonality (Exposure): coefficient of variation across the 12
* monthly income figures -- ties back to the Khandker (2012) seasonality
* discussion; a household whose Yatra income swings hardest month to month
* is, by construction, more exposed. --
egen income_mean12 = rowmean(income_m1 income_m2 income_m3 income_m4 income_m5 income_m6 ///
    income_m7 income_m8 income_m9 income_m10 income_m11 income_m12)
egen income_sd12   = rowsd(income_m1 income_m2 income_m3 income_m4 income_m5 income_m6 ///
    income_m7 income_m8 income_m9 income_m10 income_m11 income_m12)
gen income_seasonality_cv = income_sd12/income_mean12
drop income_mean12 income_sd12

* -- simple binary recodes needed as regressors --
gen byte credit_inst = (credit_source=="Institutional (bank/co-op/SHG-linked)")
gen byte distress_any = (distress_event_last365d!="None")

encode employment_type, gen(employment_type_n)
encode health_access_tier, gen(health_access_n)

* -- the covariate set used in BOTH FGLS arms below --
global Xvars_adapt education_years has_bank_account credit_inst training_received smartphone_owned
global Xvars_sens  age hhsize i.employment_type_n years_in_yatra_work
global Xvars_expo  migrant distress_any yatra_income_share income_seasonality_cv i.health_access_n
global Xvars $Xvars_adapt $Xvars_sens $Xvars_expo

di as result "=============================================================="
di as result " Covariate groups (Azeem et al. 2016 structure):"
di as result "  Adaptive capacity: $Xvars_adapt"
di as result "  Sensitivity:       $Xvars_sens"
di as result "  Exposure:          $Xvars_expo"
di as result "=============================================================="

*=============================================================================
* PART 2 -- MULTIDIMENSIONAL POVERTY (Alkire-Foster / NITI Aayog National
* MPI structure). Three dimensions, 1/3 weight each.
*=============================================================================

* -- HEALTH (1/3 weight, 2 indicators @ 1/6 each) --
* Deliberately geography-driven (health_access_deprived), not income-driven
* -- see the generation do-file's design logic.
gen h1_dep = health_access_deprived
gen h2_dep = (health_insurance_covered==0)
gen health_dep_score = (1/6)*h1_dep + (1/6)*h2_dep

* -- EDUCATION (1/3 weight, 1 indicator @ 1/3) --
* LIMITATION: Rule 1 means no household roster, so only the respondent's
* own schooling is observed -- the standard National MPI also tests
* children's school attendance, which cannot be constructed here. "Prefer
* not to say" is conservatively treated as deprived (a real fieldwork
* choice, not a neutral one -- worth flagging in the write-up).
gen e1_dep = (education_years<6) if !missing(education_years)
replace e1_dep = 1 if education_level=="Prefer not to say"
gen edu_dep_score = (1/3)*e1_dep

* -- STANDARD OF LIVING (1/3 weight, 7 indicators @ 1/21 each) --
* Matches the National MPI's 7 living-standard indicators. These are the
* variables deliberately wired to income_tier in the generation do-file.
gen s1_dep = (cooking_fuel_lpg==0)
gen s2_dep = (electricity==0)
gen s3_dep = (toilet_facility==0)
gen s4_dep = (drinking_water=="Other (spring/tanker)")
gen s5_dep = (house_type=="Kaccha")
gen s6_dep = (durables_count<2)
gen s7_dep = (has_bank_account==0)
gen sol_dep_score = (1/21)*(s1_dep+s2_dep+s3_dep+s4_dep+s5_dep+s6_dep+s7_dep)

gen mpi_score = health_dep_score + edu_dep_score + sol_dep_score
* GUARD: Stata treats missing as +infinity in comparisons, so an unguarded
* "(x>=cutoff)" silently marks any missing x as 1 rather than leaving it
* missing. mpi_score should never actually be missing (education_years
* missingness is patched via education_level=="Prefer not to say" above),
* but every threshold indicator in this do-file is guarded uniformly so
* the pattern cannot silently reappear if an upstream component changes.
gen byte mpi_poor = (mpi_score >= 1/3) if !missing(mpi_score)     // Alkire-Foster k=33% cutoff

di as result "MPI headcount (share MPI-poor): "
quietly summarize mpi_poor
di as result %5.2f (100*r(mean)) "%"
di as result "Monetary poverty headcount (Rangarajan line): "
quietly summarize poor
di as result %5.2f (100*r(mean)) "%"

*=============================================================================
* PART 3 -- MONETARY VtP (Chaudhuri et al. 2002), welfare = ln(cons_pc_pm)
*=============================================================================
gen ln_cons_pc_pm = ln(cons_pc_pm)

* -- Step 1: OLS --
regress ln_cons_pc_pm $Xvars
predict resid1, residual
gen resid1_sq = resid1^2
estimates store mon_step1

* -- Step 2: squared residuals on X -> predicted variance --
regress resid1_sq $Xvars
predict sigma2_hat, xb
replace sigma2_hat = 0.0001 if sigma2_hat <= 0
estimates store mon_step2

* -- Step 3: FGLS = WLS with weight 1/sigma2_hat --
gen wt = 1/sigma2_hat
regress ln_cons_pc_pm $Xvars [aweight=wt]
estimates store mon_fgls

esttab mon_step1 mon_fgls using "table1_monetary_FGLS.rtf", replace ///
    b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("OLS (Step 1)" "FGLS (Step 3)") ///
    title("Monetary VtP: factors influencing ln(per-capita monthly consumption)")

predict ln_c_hat, xb
gen sd_c = sqrt(sigma2_hat)
scalar ln_z = ln(2515)
gen Vh = normal((ln_z - ln_c_hat)/sd_c)          // Chaudhuri Criterion 5/6
* GUARD: 3 households drop out of the FGLS regression sample (missing
* education_years for "Prefer not to say" respondents -> ln_c_hat/Vh
* missing for them). Without "if !missing(Vh)", Stata's missing-as-
* +infinity comparison rule would silently code these 3 as vulnerable=1
* rather than leaving them correctly excluded (missing).
gen byte vulnerable = (Vh >= 0.5) if !missing(Vh)

* POVERTY-LINE SENSITIVITY CHECK -- same Vh machinery, alternative CPI-
* adjusted line (Rangarajan & Dev 2024, ~Rs.1,850/month) instead of the
* Sethu et al. (2024) direct-recomputation line used above. Neither figure
* is an official GoI-notified line, so report both rather than picking one.
scalar ln_z_cpi = ln(1850)
gen Vh_cpi = normal((ln_z_cpi - ln_c_hat)/sd_c)
gen byte vulnerable_cpi_sensitivity = (Vh_cpi >= 0.5) if !missing(Vh_cpi)
di as result "=============================================================="
di as result " POVERTY-LINE SENSITIVITY: monetary vulnerability under two lines"
di as result "=============================================================="
quietly summarize vulnerable
di as result "Rs.2,515/month (Sethu et al. 2024, primary): " %5.2f (100*r(mean)) "%"
quietly summarize vulnerable_cpi_sensitivity
di as result "Rs.1,850/month (Rangarajan & Dev 2024, CPI-adjusted): " %5.2f (100*r(mean)) "%"
di as result "=============================================================="

gen byte currently_poor = poor
gen vtp_group = .
label define vtplbl 1 "Chronic poor" 2 "Transient poor" 3 "Escaped poverty" 4 "Non-poor"
replace vtp_group = 1 if currently_poor==1 & vulnerable==1
replace vtp_group = 2 if currently_poor==0 & vulnerable==1
replace vtp_group = 3 if currently_poor==1 & vulnerable==0
replace vtp_group = 4 if currently_poor==0 & vulnerable==0
label values vtp_group vtplbl

di as result "=============================================================="
di as result " MONETARY VtP GROUPS"
tabulate vtp_group
quietly summarize vulnerable
di as result "Overall monetary VtP: " %5.2f (100*r(mean)) "%"
di as result "=============================================================="

mlogit vtp_group $Xvars, base(4) iterate(200)
* NOTE: as in the earlier pilot replication, near-perfect separation is
* possible here because "vulnerable" is itself a threshold function of the
* same X's -- inspect e(sample) if Stata drops observations.
estimates store mon_mlogit

*=============================================================================
* PART 4 -- MULTIDIMENSIONAL VtP (FM approach: Feeny & McDonald 2016),
* welfare = mpi_score. NOT log-transformed -- the deprivation score is
* bounded [0,1] and can be exactly zero, so a log-normal assumption (fine
* for consumption) doesn't apply here; FGLS runs on the raw score.
*=============================================================================
regress mpi_score $Xvars
predict mpi_resid1, residual
gen mpi_resid1_sq = mpi_resid1^2
estimates store mpi_step1

regress mpi_resid1_sq $Xvars
predict mpi_sigma2_hat, xb
replace mpi_sigma2_hat = 0.0001 if mpi_sigma2_hat <= 0
estimates store mpi_step2

gen mpi_wt = 1/mpi_sigma2_hat
regress mpi_score $Xvars [aweight=mpi_wt]
estimates store mpi_fgls

esttab mpi_step1 mpi_fgls using "table2_MPI_FGLS.rtf", replace ///
    b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("OLS (Step 1)" "FGLS (Step 3)") ///
    title("Multidimensional VtP: factors influencing the MPI deprivation score")

predict mpi_score_hat, xb
gen mpi_sd = sqrt(mpi_sigma2_hat)
scalar mpi_k = 1/3
* FLIPPED vs the monetary case: vulnerable = Pr(score EXCEEDS the cutoff),
* not Pr(falling below it) -- higher deprivation score is worse, not lower.
gen Vh_mpi = normal((mpi_score_hat - mpi_k)/mpi_sd)
gen byte mpi_vulnerable = (Vh_mpi >= 0.5) if !missing(Vh_mpi)

gen mpi_vtp_group = .
label define mpivtplbl 1 "Chronic MPI-poor" 2 "Transient MPI-poor" 3 "Escaped MPI-poor" 4 "Non-MPI-poor"
replace mpi_vtp_group = 1 if mpi_poor==1 & mpi_vulnerable==1
replace mpi_vtp_group = 2 if mpi_poor==0 & mpi_vulnerable==1
replace mpi_vtp_group = 3 if mpi_poor==1 & mpi_vulnerable==0
replace mpi_vtp_group = 4 if mpi_poor==0 & mpi_vulnerable==0
label values mpi_vtp_group mpivtplbl

di as result "=============================================================="
di as result " MULTIDIMENSIONAL VtP GROUPS"
tabulate mpi_vtp_group
quietly summarize mpi_vulnerable
di as result "Overall multidimensional VtP: " %5.2f (100*r(mean)) "%"
di as result "=============================================================="

mlogit mpi_vtp_group $Xvars, base(4) iterate(200)
* same separation caveat as the monetary mlogit above applies here too
estimates store mpi_mlogit

* -- cross-tab: does monetary and multidimensional vulnerability identify
* the SAME households, or different ones? This is a genuine finding, not
* a formality -- the whole point of running both. --
di as result "=============================================================="
di as result " Monetary vulnerable x Multidimensional vulnerable cross-tab"
tabulate vulnerable mpi_vulnerable, row
di as result "=============================================================="

*=============================================================================
* ROBUSTNESS 1 -- VULNERABILITY BY MEAN RISK (VMR), Gallardo (2018) Sec. 3.4
*
* The VEP estimate above (Chaudhuri et al. 2002) belongs to a paradigm that
* ASSUMES ln(consumption) is conditionally normal and reads a probability
* off the normal CDF. Gallardo (2018) reviews a genuinely different
* paradigm -- Vulnerability by Mean Risk (VMR) -- which drops that
* distributional assumption and instead orders households by a mean-risk
* trade-off computed directly on consumption LEVELS, algebraically compared
* against the poverty line z: no CDF, no normality.
*
* Both VMR criteria below are estimated from their OWN two-step FGLS run on
* cons_pc_pm (levels), NOT derived from the log-space VEP model's ln_c_hat/
* sd_c. Reusing the log-space moments here would silently reintroduce the
* log-normality assumption that VMR exists specifically to avoid -- that
* was the (methodologically incorrect) shortcut used in earlier versions of
* this do-file, kept here as a documented correction, not a silent fix.
*=============================================================================

* -- Step 1: OLS in LEVELS --
regress cons_pc_pm $Xvars
predict resid_lvl1, residual
gen resid_lvl1_sq = resid_lvl1^2
estimates store vmr_step1

* -- Step 2: squared residuals on X -> predicted variance (levels) --
regress resid_lvl1_sq $Xvars
predict sigma2_lvl_hat, xb
replace sigma2_lvl_hat = 1 if sigma2_lvl_hat <= 0
estimates store vmr_step2

* -- Step 3: FGLS = WLS with weight 1/sigma2_lvl_hat --
gen wt_lvl = 1/sigma2_lvl_hat
regress cons_pc_pm $Xvars [aweight=wt_lvl]
estimates store vmr_fgls
predict c_hat_lvl, xb
gen sd_lvl = sqrt(sigma2_lvl_hat)

*-----------------------------------------------------------------------------
* Criterion 11 (Chiwaula et al. 2011, per Gallardo 2018 p.1098): vulnerable
* if E(y) - sd(y) < z. Distribution-free MEAN-DEVIATION rule -- a symmetric
* risk penalty, no distributional shape assumed. GUARD applied throughout:
* Stata reads a missing value as +infinity in comparisons, so an unguarded
* "(x < z)" would silently mark any missing x as vulnerable=1.
*-----------------------------------------------------------------------------
gen byte vmr_meandev_vulnerable = (c_hat_lvl - sd_lvl < 2515) if !missing(c_hat_lvl, sd_lvl)

*-----------------------------------------------------------------------------
* Criterion 12 (Gallardo 2013, per Gallardo 2018 p.1099): vulnerable if
* E(y) - gamma*sd_down(y) <= z, gamma in (0,1]. The DOWNSIDE SEMI-DEVIATION
* counts only adverse (below-mean) deviations, so unlike Criterion 11 (or
* Chaudhuri's log-normal VEP) it can tell apart two households with the
* same mean and variance but different downside risk exposure -- Gallardo's
* own motivating example (his Figure 2).
*-----------------------------------------------------------------------------
gen resid_lvl_neg = min(resid_lvl1,0)
gen resid_lvl_neg_sq = resid_lvl_neg^2
regress resid_lvl_neg_sq $Xvars
predict sigma2_lvl_down_hat, xb
replace sigma2_lvl_down_hat = 1 if sigma2_lvl_down_hat <= 0
gen sd_lvl_down = sqrt(sigma2_lvl_down_hat)

* primary trade-off coefficient: gamma = 0.5 (mid-point of Gallardo's
* admissible range; see the gamma-sensitivity sweep below)
scalar gamma_gallardo = 0.5
gen byte vmr_downside_vulnerable = (c_hat_lvl - gamma_gallardo*sd_lvl_down <= 2515) if !missing(c_hat_lvl, sd_lvl_down)

di as result "=============================================================="
di as result " ROBUSTNESS 1: Vulnerability by Mean Risk (Gallardo 2018, Sec. 3.4)"
di as result " VEP (Chaudhuri, log-normal) vs. VMR (Chiwaula/Gallardo, level,"
di as result " distribution-free) -- two different paradigms, same question"
di as result "=============================================================="
foreach v of varlist vulnerable vmr_meandev_vulnerable vmr_downside_vulnerable {
    quietly summarize `v'
    di as result "`v': " %5.2f (100*r(mean)) "% (N=" r(N) ")"
}

di as result "--- VEP (Chaudhuri) x VMR mean-deviation (Chiwaula) cross-tab ---"
tabulate vulnerable vmr_meandev_vulnerable, row
di as result "--- VEP (Chaudhuri) x VMR downside semi-deviation (Gallardo) cross-tab ---"
tabulate vulnerable vmr_downside_vulnerable, row

di as result "Households where VEP (Chaudhuri) and VMR-downside (Gallardo) DISAGREE:"
gen byte disagree_gallardo = (vulnerable != vmr_downside_vulnerable) if !missing(vulnerable, vmr_downside_vulnerable)
quietly summarize disagree_gallardo
di as result %5.2f (100*r(mean)) "%"

*-----------------------------------------------------------------------------
* ROBUSTNESS 1b -- gamma sensitivity. Gallardo (2018, p.1100) is explicit
* that gamma is the approach's main point of arbitrariness: "gamma should
* be reasonably valued in the interval (0,1]" -- a range, not a point
* estimate. Sweep across that full range rather than reporting only the
* gamma=0.5 figure as if it were uncontested.
*-----------------------------------------------------------------------------
di as result "=============================================================="
di as result " ROBUSTNESS 1b: gamma sensitivity, VMR downside semi-deviation"
di as result "=============================================================="
foreach g in 25 50 75 100 {
    local gamma = `g'/100
    quietly gen byte vmr_downside_g`g' = (c_hat_lvl - `gamma'*sd_lvl_down <= 2515) if !missing(c_hat_lvl, sd_lvl_down)
    quietly summarize vmr_downside_g`g'
    di as result "gamma=`gamma': vulnerability rate = " %5.2f (100*r(mean)) "%"
}

*=============================================================================
* ROBUSTNESS 2 -- Pritchett et al. (2000) / Azeem et al. (2016) measurement-
* error perturbation. Re-estimate Vh assuming up to 50% of sigma2_hat is
* measurement error, not real risk.
* NOTE: if the vulnerability rate barely moves across phi, that itself
* replicates Azeem's own robustness finding -- it does not necessarily mean
* the loop is broken; check how many households sit near the Vh=0.5 margin
* before assuming an error.
*=============================================================================
di as result "=============================================================="
di as result " ROBUSTNESS 2: measurement-error perturbation (monetary arm)"
di as result "=============================================================="
forvalues p = 0(10)50 {
    local phi = `p'/100
    quietly gen sd_c_phi`p' = sqrt(sigma2_hat*(1-`phi'))
    quietly gen Vh_phi`p' = normal((ln_z - ln_c_hat)/sd_c_phi`p')
    quietly gen byte vulnerable_phi`p' = (Vh_phi`p' >= 0.5) if !missing(Vh_phi`p')
    quietly summarize vulnerable_phi`p'
    di as result "phi=`phi': vulnerability rate = " %5.2f (100*r(mean)) "%"
}

*=============================================================================
* ROBUSTNESS 3 -- IPW correction for non-random attrition. Only feasible
* here because the data is synthetic and the FULL n=200 (including dropped
* observations) with the retention flag was preserved -- a real fieldwork
* refusal would not offer this; flag this limitation explicitly if adapting
* this code to real data.
*=============================================================================
preserve
    use "kedarnath_synthetic_v2_n200_retention_flag.dta", clear

    gen byte credit_inst = (credit_source=="Institutional (bank/co-op/SHG-linked)")
    encode employment_type, gen(employment_type_n)

    * selection model on the SAME risk factors used to generate dropout in
    * the first place (occupation/education/age/migrant)
    probit retained education_years age migrant i.employment_type_n
    predict p_retained, pr
    gen ipw = 1/p_retained

    keep if retained==1
    egen income_mean12 = rowmean(income_m1 income_m2 income_m3 income_m4 income_m5 income_m6 ///
        income_m7 income_m8 income_m9 income_m10 income_m11 income_m12)
    egen income_sd12   = rowsd(income_m1 income_m2 income_m3 income_m4 income_m5 income_m6 ///
        income_m7 income_m8 income_m9 income_m10 income_m11 income_m12)
    gen income_seasonality_cv = income_sd12/income_mean12
    encode health_access_tier, gen(health_access_n)
    gen byte distress_any = (distress_event_last365d!="None")
    gen ln_cons_pc_pm = ln(cons_pc_pm)

    global Xvars_ipw education_years has_bank_account credit_inst training_received ///
        smartphone_owned age hhsize i.employment_type_n years_in_yatra_work ///
        migrant distress_any yatra_income_share income_seasonality_cv i.health_access_n

    * IPW-weighted FGLS Step 1 & 3 (skipping Step 2 re-estimation for brevity
    * -- reuses unweighted variance shape, weights only the mean equation)
    regress ln_cons_pc_pm $Xvars_ipw [pweight=ipw]
    predict ln_c_hat_ipw, xb

    scalar ln_z_ipw = ln(2515)
    gen byte poor_ipw = (cons_pc_pm < 2515)
    di as result "=============================================================="
    di as result " ROBUSTNESS 3: IPW-corrected vs. unweighted monetary poverty rate"
    di as result "=============================================================="
    quietly summarize poor_ipw [aweight=ipw]
    di as result "IPW-weighted poverty rate: " %5.2f (100*r(mean)) "%"
    quietly summarize poor_ipw
    di as result "Unweighted (as-fielded) poverty rate: " %5.2f (100*r(mean)) "%"
restore

*=============================================================================
* SAVE
*=============================================================================
save "kedarnath_vtp_analysis_results.dta", replace
di as error "=============================================================="
di as error " Analysis complete. Tables: table1_monetary_FGLS.rtf,"
di as error " table2_MPI_FGLS.rtf. Full results in"
di as error " kedarnath_vtp_analysis_results.dta"
di as error "=============================================================="
log close
