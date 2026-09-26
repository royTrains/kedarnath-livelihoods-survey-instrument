*=============================================================================
* REAL-DATA VERSION: same procedure as vasyr_synthetic_example.do, run on the
* actual VASyR 2025 (Lebanon) microdata in vasyr/, built to household level by
* build_vasyr_real.py (run that first -- it writes vasyr_real_raw.csv).
*
* Lyons, Kass-Hanna & Montoya Castano (2023) use the 2018 VASyR wave; the file
* here is the 2025 wave, whose questionnaire has moved on in places, so several
* of the 21 indicators are DOCUMENTED PROXIES rather than exact matches to
* their Table 2 wording -- see the comments in build_vasyr_real.py and the
* README. This is a real analysis of real (if not the original-paper) data,
* not a demonstration dataset.
*=============================================================================
clear all
set more off
cd "D:\OneDrive\Desktop\vulnerability-2-poverty\replication\vasyr_example"   // <-- change to your working folder
import delimited "vasyr_real_raw.csv", clear varnames(1) case(preserve) encoding("utf-8")

encode district, gen(district_n)
gen byte inc_employment = income_source=="employment"
gen byte inc_assistance = income_source=="assistance"
gen byte inc_borrowing  = income_source=="borrowing"
* income proxy for Lyons' SMEB/MEB expenditure groups: the full ~40-item consumption
* basket isn't reconstructed here, so household-reported 30-day income (USD) is used
* instead, split into quartiles the same way SMEB/MEB split expenditure into bands
xtile income_q = total_income_usd_dec, nq(4)
gen byte inc_q1 = income_q==1 if !missing(income_q)
gen byte inc_q2 = income_q==2 if !missing(income_q)
gen byte inc_q3 = income_q==3 if !missing(income_q)

*-----------------------------------------------------------------------------
* MLI: same 5-dimension, equal-weight construction as Table 2 (0.05 x 4 health/
* food, 0.10 x 2 education, 0.025 x 8 living standards, 0.10 x 2 employment,
* 0.04 x 5 security/social); indicators are the 0/1 columns from Python above.
*-----------------------------------------------------------------------------
gen double dep_score = .05*(special_needs+healthcare_access+food_coping+diet_diversity) ///
    + .10*(child_school+adult_schooling) ///
    + .025*(electricity+sanitation+drinking_water+cooking_fuel+basic_assets+crowding+shelter_conditions+housing_stability) ///
    + .10*(unemployment+underemployment) ///
    + .04*(legal_residency+area_settlement+communications+movement_mobility+community_interaction)

gen byte poor_mdim = dep_score >= 0.33
quietly summarize poor_mdim
scalar H = r(mean)
quietly summarize dep_score if poor_mdim==1
scalar A = r(mean)
di as result "N = " _N
di as result "Headcount H = " %5.3f H "   Intensity A = " %5.3f A "   MLI = H*A = " %5.3f (H*A)

*=============================================================================
* Three-stage FGLS (Chaudhuri et al. 2002 / Lyons et al. Section 5.2): welfare
* = dep_score, poverty cutoff = 0.33, vulnerable if Pr(dep_score>0.33|X) >= 0.5.
*=============================================================================
global X age_head female_head married_head hhsize dependent_share ///
    inc_employment inc_assistance inc_borrowing borrowed inc_q1 inc_q2 inc_q3 i.district_n

* Stage 1: OLS of the deprivation score on X
regress dep_score $X
predict e1, residual
gen double e1_sq = e1^2

* Stage 2: OLS of squared residuals on X -> predicted variance
regress e1_sq $X
predict sigma2_hat, xb
replace sigma2_hat = 0.0001 if sigma2_hat <= 0

* Stage 3: FGLS = WLS of the deprivation score on X, weight 1/sigma2_hat
gen double wt = 1/sigma2_hat
regress dep_score $X [aweight=wt]
predict dep_score_hat, xb
gen double sd_dep = sqrt(sigma2_hat)

gen double Vh = normal((dep_score_hat - 0.33)/sd_dep)
gen byte vulnerable = Vh >= 0.5 if !missing(Vh)

gen vtp_group = .
label define vtplbl 1 "Chronic poor" 2 "Transient poor" 3 "Escaped poverty" 4 "Non-poor"
replace vtp_group = 1 if poor_mdim==1 & vulnerable==1
replace vtp_group = 2 if poor_mdim==0 & vulnerable==1
replace vtp_group = 3 if poor_mdim==1 & vulnerable==0
replace vtp_group = 4 if poor_mdim==0 & vulnerable==0
label values vtp_group vtplbl

di as result "=============================================================="
di as result " Vulnerability-to-poverty groups (real 2025 VASyR households)"
tabulate vtp_group
quietly summarize vulnerable
di as result "Overall vulnerability rate: " %5.2f (100*r(mean)) "%"
di as result "=============================================================="

di as result "MLI and vulnerability by district:"
tabstat dep_score poor_mdim vulnerable, by(district_n) stat(mean n)

save "vasyr_real_example.dta", replace
di as result "Saved vasyr_real_example.dta -- N = " _N
