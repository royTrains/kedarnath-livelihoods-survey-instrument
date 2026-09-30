*=============================================================================
* KEDARNATH YATRA WORKERS -- VULNERABILITY TO POVERTY
* Monetary and multidimensional arms, on the FINAL instrument's own dataset.
*
* Replaces replication/kedarnath_vtp_analysis.do, which ran on the older
* synthetic pool and carried three mis-specified MPI indicators:
*     s1_dep = (cooking_fuel_lpg==0)                  -- an LPG binary, where
*              NITI names a LIST of dirty fuels; overstated by ~10pp
*     s4_dep = (drinking_water=="Other (spring/tanker)") -- source only, with
*              no 30-minute round-trip limb at all
*     s6_dep = (durables_count<2)                     -- right threshold, wrong
*              list (6 assets, missing telephone/computer/animal cart, and car
*              folded into the count instead of NITI's separate limb)
* Those indicators are now built correctly in 02_build_final_dataset.do, so
* this file consumes them rather than rebuilding them. Retire the old file.
*
* Welfare measures
*   (A) MONETARY -- Chaudhuri, Jalan & Suryahadi (2002) three-stage FGLS on
*       ln(cons_pc_pm). The poverty line is now PER RESPONDENT: Sethu et al.
*       (2024) give Rs 2,515 rural and Rs 3,639 urban, and home_rural_urban
*       selects between them, so ln(z) varies across respondents rather than
*       being a scalar as it was in the old file.
*   (B) MULTIDIMENSIONAL -- the same machinery on the NITI-structured
*       mpi_score (Feeny & McDonald 2016; Lyons, Kass-Hanna & Montoya
*       Castano 2023), with the inequality FLIPPED: vulnerable means
*       Pr(deprivation score EXCEEDS the cutoff).
*
* EVERYTHING BELOW IS SYNTHETIC. It exercises the pipeline; it is not a
* finding about Kedarnath workers.
*=============================================================================
version 17
clear all
set more off
cd "D:\OneDrive\Desktop\vulnerability-2-poverty\replication\final_instrument"
capture log close
log using "do/04_vtp_analysis.log", replace text

use "data/kedarnath_final_n200_fielded.dta", clear

*=============================================================================
* 1. COVARIATES, in the Azeem, Mugera & Schilizzi (2016) adaptive-capacity /
*    sensitivity / exposure structure.
*
* Three changes from the old file, each forced by a correction upstream:
*   - credit_institutional replaces (credit_source==1). credit_source is now
*     gated behind took_loan_12m and is therefore MISSING for non-borrowers;
*     using it directly would silently drop every non-borrowing household
*     from the FGLS sample.
*   - shock_any replaces (distress_event_last365d!="None"). The shock item is
*     a select_multiple now, so the old string test is not even type-valid.
*   - LOCATION enters the model. Fujii (2016, section 2.2) closes his review
*     of the empirical literature by naming education and location as the two
*     covariates that emerge consistently; urban (rural/urban status of the
*     home place) and health_access_tier (GPS-derived position along the
*     route) are both collected and neither was previously used.
*   - MOBILITY enters as closure_labour_migrant, not as migrant. The migrant
*     dummy is a district boundary, and in this population the boundary is
*     not where the mobility is: the pilot put 11 of 20 seasonal movers
*     inside this same district, so migrant codes most movers as stayers.
*     closure_labour_migrant is whether the respondent sold labour away from
*     both bases during the closure -- the behaviour that actually separates
*     a household with a winter income from one without. migrant is kept
*     alongside it as a distance control, which is all it ever measured.
*=============================================================================
gen byte urban = (home_rural_urban==2)

global X_adapt  education_years has_bank_account credit_institutional training_received smartphone_owned insured_any has_cultivable_land debt_stock_months secondary_income_share
global X_sens   age hhsize i.employment_type years_in_yatra_work dep_func_limit i.marital_status health_shock_any lang_local first_job_ever
global X_expo   migrant closure_labour_migrant stays_all_year shock_any yatra_income_share income_seasonality_cv i.health_access_tier urban trek_dependent i.site years_coming_here ///
                came_for_push placed_by_agent worked_other_places home_outside_state
global X        $X_adapt $X_sens $X_expo

di as result "{hline 78}"
di as result " Covariate groups (Azeem et al. 2016 structure)"
di as result "   Adaptive capacity: $X_adapt"
di as result "   Sensitivity:       $X_sens"
di as result "   Exposure:          $X_expo"
quietly summarize poor
di as result "   Monetary poor (per-respondent line): " %5.1f (100*r(mean)) "%"
quietly summarize mpi_poor
di as result "   MPI-poor (k = 1/3):                  " %5.1f (100*r(mean)) "%"
di as result "{hline 78}"

* MEASUREMENT-MODE WARNING. Respondents who could not recall twelve monthly
* earnings gave an annual total instead, and their income_seasonality_cv is a
* two-level series with no within-season variation -- a LOWER BOUND, not the
* same measurement. It is an exposure covariate in both arms, so the split is
* reported and re-run below rather than assumed away.
quietly summarize income_from_fallback
di as result "Earnings via the annual-total fallback: " %4.1f (100*r(mean)) "% of the sample"

*=============================================================================
* 2. MONETARY VEP -- Chaudhuri et al. (2002), three-stage FGLS
*=============================================================================
gen double ln_c = ln(cons_pc_pm)
gen double ln_z = ln(poverty_line)          // per respondent, not a scalar

* -- Stage 1: OLS, to get the residuals --
regress ln_c $X
predict double resid1, residual
gen double resid1_sq = resid1^2
estimates store mon_ols

* -- Stage 2: squared residuals on X -> the predicted variance --
regress resid1_sq $X
predict double sigma2_hat, xb
replace sigma2_hat = 0.0001 if sigma2_hat <= 0     // variance cannot be negative
estimates store mon_var

* -- Stage 3: FGLS = WLS weighted by the inverse predicted variance --
gen double wt = 1/sigma2_hat
regress ln_c $X [aweight=wt]
estimates store mon_fgls
predict double ln_c_hat, xb
gen double sd_c = sqrt(sigma2_hat)

* vulnerability = Pr(consumption falls below this respondent's own line)
gen double Vh = normal((ln_z - ln_c_hat)/sd_c)
* GUARD: Stata reads missing as +infinity in comparisons, so an unguarded
* (Vh >= tau) would silently mark any missing Vh as vulnerable rather than
* leaving it missing.
gen byte vulnerable = (Vh >= 0.5) if !missing(Vh)

*-----------------------------------------------------------------------------
* 2a. Chronic / transient, to Suryahadi & Sumarto's ACTUAL definition.
*
* The old file had this wrong, and so did 03_employment_vulnerability.do:
*     chronic   = currently_poor & vulnerable
*     transient = !currently_poor & vulnerable
* In Suryahadi & Sumarto (2003, Table 3.1, reproduced in Fujii 2016) the
* chronic/transient axis is EXPECTED consumption against the line -- chronic
* means poor AND E[c] < z, transient means poor but E[c] >= z -- with
* vulnerability against tau as a SEPARATE third axis. Splitting on
* vulnerability instead measures something else and should not carry those
* names. E[c] has been available all along as exp(ln_c_hat).
*-----------------------------------------------------------------------------
gen double exp_c = exp(ln_c_hat + sigma2_hat/2)     // E[c] under log-normality
gen byte low_exp = (exp_c < poverty_line) if !missing(exp_c)

label define ssgrp 1 "A: poor, low E[c], vulnerable (chronic)" ///
                   2 "B: poor, high E[c], vulnerable (transient)" ///
                   3 "C: poor, high E[c], not vulnerable (transient)" ///
                   4 "D: non-poor, low E[c], vulnerable" ///
                   5 "E: non-poor, high E[c], vulnerable" ///
                   6 "F: non-poor, high E[c], not vulnerable"
gen byte ss_group = .
replace ss_group = 1 if poor==1 & low_exp==1 & vulnerable==1
replace ss_group = 2 if poor==1 & low_exp==0 & vulnerable==1
replace ss_group = 3 if poor==1 & low_exp==0 & vulnerable==0
replace ss_group = 4 if poor==0 & low_exp==1 & vulnerable==1
replace ss_group = 5 if poor==0 & low_exp==0 & vulnerable==1
replace ss_group = 6 if poor==0 & low_exp==0 & vulnerable==0
replace ss_group = 1 if poor==1 & low_exp==1 & vulnerable==0   // rare: low E[c] but not over tau
label values ss_group ssgrp

gen byte chronic_poor   = inlist(ss_group,1)
gen byte transient_poor = inlist(ss_group,2,3)

di as result "{hline 78}"
di as result " MONETARY VULNERABILITY (Suryahadi & Sumarto Table 3.1 cells)"
tabulate ss_group
quietly summarize vulnerable
di as result "   Vulnerable (Vh >= 0.5): " %5.1f (100*r(mean)) "%"
quietly summarize chronic_poor
di as result "   Chronic poor   (poor AND E[c] < z): " %5.1f (100*r(mean)) "%"
quietly summarize transient_poor
di as result "   Transient poor (poor BUT E[c] >= z): " %5.1f (100*r(mean)) "%"
di as result "{hline 78}"

*=============================================================================
* 3. MULTIDIMENSIONAL VEP -- same machinery on the NITI-structured mpi_score.
* NOT log-transformed: the deprivation score is bounded [0,1] and can be
* exactly zero, so log-normality does not apply. Inequality FLIPPED.
*=============================================================================
regress mpi_score $X
predict double mresid1, residual
gen double mresid1_sq = mresid1^2
estimates store mpi_ols

regress mresid1_sq $X
predict double msigma2_hat, xb
replace msigma2_hat = 0.0001 if msigma2_hat <= 0
estimates store mpi_var

gen double mwt = 1/msigma2_hat
regress mpi_score $X [aweight=mwt]
estimates store mpi_fgls
predict double mpi_hat, xb
gen double msd = sqrt(msigma2_hat)

scalar mpi_k = 1/3                                   // Alkire-Foster cutoff
gen double Vh_mpi = normal((mpi_hat - mpi_k)/msd)    // Pr(score EXCEEDS the cutoff)
gen byte mpi_vulnerable = (Vh_mpi >= 0.5) if !missing(Vh_mpi)

di as result "{hline 78}"
di as result " MULTIDIMENSIONAL VULNERABILITY"
quietly summarize mpi_vulnerable
di as result "   MPI-vulnerable: " %5.1f (100*r(mean)) "%"
di as result " Monetary-vulnerable x MPI-vulnerable -- do they find the SAME people?"
tabulate vulnerable mpi_vulnerable, row
di as result "{hline 78}"

*=============================================================================
* 4. ROBUSTNESS
*=============================================================================

*-----------------------------------------------------------------------------
* 4a. The vulnerability threshold tau. The old file swept gamma and the
* measurement-error share but fixed tau = 0.5 everywhere with no citation.
* Fujii (2016) supplies both the justification and the test: Pritchett et al.
* (2000) argue 0.5 is a focal point and is where a household exactly at the
* line facing a symmetric zero-mean shock sits; Zhang & Wan (2009) validate it
* empirically against realised later-round poverty and find precision depends
* on tau AND on the poverty line.
*-----------------------------------------------------------------------------
di as result "{hline 78}"
di as result " 4a. Sensitivity to the vulnerability threshold tau"
foreach tau in 0.3 0.4 0.5 0.6 0.7 {
    quietly gen byte _v = (Vh >= `tau') if !missing(Vh)
    quietly summarize _v
    di as result "     tau = `tau': monetary vulnerability " %5.1f (100*r(mean)) "%"
    drop _v
}

*-----------------------------------------------------------------------------
* 4b. Measurement error (Pritchett et al. 2000; Azeem et al. 2016): re-estimate
* assuming a share phi of the estimated variance is measurement error rather
* than real risk.
*-----------------------------------------------------------------------------
di as result " 4b. Measurement-error perturbation"
forvalues p = 0(10)50 {
    local phi = `p'/100
    quietly gen double _sd = sqrt(sigma2_hat*(1-`phi'))
    quietly gen double _V  = normal((ln_z - ln_c_hat)/_sd)
    quietly gen byte _v = (_V >= 0.5) if !missing(_V)
    quietly summarize _v
    di as result "     phi = `phi': vulnerability " %5.1f (100*r(mean)) "%"
    drop _sd _V _v
}

*-----------------------------------------------------------------------------
* 4c. Vulnerability by Mean Risk (Gallardo 2018, sec. 3.4). A different
* paradigm: no normality, no CDF -- order households by a mean-risk trade-off
* computed on consumption LEVELS and compared algebraically against the line.
* Estimated from its OWN levels FGLS; reusing the log-space moments would
* reintroduce exactly the log-normality VMR exists to avoid.
*-----------------------------------------------------------------------------
regress cons_pc_pm $X
predict double lresid, residual
gen double lresid_sq = lresid^2
regress lresid_sq $X
predict double lsig2, xb
replace lsig2 = 1 if lsig2 <= 0
gen double lwt = 1/lsig2
regress cons_pc_pm $X [aweight=lwt]
predict double c_hat_lvl, xb
gen double sd_lvl = sqrt(lsig2)

* Criterion 11 (Chiwaula et al. 2011): vulnerable if E(y) - sd(y) < z
gen byte vmr_meandev = (c_hat_lvl - sd_lvl < poverty_line) if !missing(c_hat_lvl, sd_lvl)

* Criterion 12 (Gallardo 2013): downside SEMI-deviation, which unlike the above
* can separate two households with the same mean and variance but different
* downside exposure.
gen double lres_neg = min(lresid,0)
gen double lres_neg_sq = lres_neg^2
regress lres_neg_sq $X
predict double lsig2_down, xb
replace lsig2_down = 1 if lsig2_down <= 0
gen double sd_down = sqrt(lsig2_down)

di as result " 4c. Vulnerability by Mean Risk, and the gamma sweep"
quietly summarize vmr_meandev
di as result "     Chiwaula mean-deviation: " %5.1f (100*r(mean)) "%"
foreach g in 0.25 0.50 0.75 1.00 {
    quietly gen byte _v = (c_hat_lvl - `g'*sd_down <= poverty_line) if !missing(c_hat_lvl, sd_down)
    quietly summarize _v
    di as result "     Gallardo downside, gamma = `g': " %5.1f (100*r(mean)) "%"
    drop _v
}

*-----------------------------------------------------------------------------
* 4d. The earnings measurement-mode split. Fallback respondents have a flatter
* seasonality measure by construction, so the two groups are compared rather
* than pooled silently.
*-----------------------------------------------------------------------------
di as result " 4d. By earnings measurement mode"
bysort income_from_fallback: summarize Vh income_seasonality_cv
di as result "{hline 78}"

*=============================================================================
* 5. WHAT PREDICTS VULNERABILITY
* Near-perfect separation is possible here, as elsewhere in this project,
* because `vulnerable' is itself a threshold function of the same X -- inspect
* e(sample) if Stata drops observations.
*=============================================================================
* Wrapped in capture on purpose. A logit dies outright when its outcome does not vary, and an
* outcome CAN legitimately be constant in a real sample -- every worker vulnerable in a bad year,
* or none in a small pilot. Killing the whole analysis at its last step over that would mean losing
* the FGLS results already estimated above, which is the wrong trade.
foreach out in vulnerable mpi_vulnerable {
    quietly summarize `out'
    if r(sd) == 0 | r(N) == 0 {
        di as error "  SKIPPED logit of `out': the outcome does not vary (mean " r(mean) ", N " r(N) ")"
    }
    else {
        capture noisily logit `out' $X, iterate(200)
        if _rc {
            di as error "  logit of `out' did not converge (rc " _rc "); FGLS results above are unaffected"
        }
        else {
            estimates store `out'_logit
        }
    }
}

capture which esttab
if _rc==0 {
    esttab mon_ols mon_fgls mpi_ols mpi_fgls using "do/table_vtp_FGLS.rtf", replace ///
        b(3) se(3) star(* 0.10 ** 0.05 *** 0.01) ///
        mtitles("Monetary OLS" "Monetary FGLS" "MPI OLS" "MPI FGLS") ///
        title("Vulnerability to poverty: three-stage FGLS, monetary and multidimensional arms")
}

save "data/kedarnath_final_vtp_results.dta", replace
di as result "Saved data/kedarnath_final_vtp_results.dta"
log close
