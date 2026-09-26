*=============================================================================
* SMALL WORKED EXAMPLE: Lyons, Kass-Hanna & Montoya Castano (2023, J. Int. Dev.
* 35:2014-2045) "A multidimensional approach to measuring vulnerability to
* poverty among refugee populations" -- same procedure as their VASyR analysis:
*   (1) Alkire-Foster multidimensional livelihood index (MLI), 5 dimensions,
*       21 indicators, cutoffs and weights exactly as their Table 2;
*   (2) Chaudhuri et al. (2002) 3-stage FGLS applied to the deprivation score
*       instead of log-consumption (their Section 5.2, eqs. 1-8).
*
* DATA CAVEAT: the real 2018 VASyR microdata is restricted -- it requires a
* licensed application through the UNHCR Microdata Library (microdata.unhcr.org)
* and was not obtainable in this session. What follows is a SYNTHETIC dataset
* built to the same structure, with each indicator's marginal prevalence
* calibrated to the percentages reported in Lyons et al.'s Table 2, and a
* single latent household "poverty risk" factor (function of education,
* employment, dependents, expenditure group and governorate) driving
* correlation across indicators and with the covariates -- so the FGLS step
* has something real to estimate. It demonstrates the METHOD, not VASyR data.
*=============================================================================
clear all
set more off
set seed 71923
cd "D:\OneDrive\Desktop\vulnerability-2-poverty\replication\vasyr_example"   // <-- change to your working folder
set obs 600

*-----------------------------------------------------------------------------
* Household covariates (shares follow Lyons et al. Table 1)
*-----------------------------------------------------------------------------
gen double u = runiform()
gen byte governorate = 1 + (u>=.097) + (u>=.173) + (u>=.264) + (u>=.379) + (u>=.509) + (u>=.711) + (u>=.902)
label define gov 1 "Akkar" 2 "Baalbek-Hermel" 3 "Beirut" 4 "Bekaa" 5 "El Nabatieh" ///
    6 "Mount Lebanon" 7 "North Lebanon" 8 "South Lebanon"
label values governorate gov
drop u

gen double age_head = round(max(18, min(80, rnormal(38,10))))
gen byte female_head = runiform() < 0.16
gen byte married = runiform() < 0.86
gen byte worked_last_week = runiform() < 0.53
gen int hhsize = max(1, round(rnormal(4.9,1.8)))
gen double dependent_share = rbeta(4,5.1)          // mean ~0.44
gen byte borrowed = runiform() < 0.82

gen double u = runiform()
gen byte educ_head = 1 + (u>=.121) + (u>=.732) + (u>=.902) + (u>=.957)
label define educ 1 "Illiterate" 2 "Less than primary" 3 "Primary" 4 "Secondary+" 5 "University"
label values educ_head educ
replace u = runiform()
gen byte income_source = 1 + (u>=.399) + (u>=.617) + (u>=.772)
label define incsrc 1 "Employment" 2 "Assistance" 3 "Borrowing" 4 "Other"
label values income_source incsrc
replace u = runiform()
gen byte smeb_cat = 1 + (u>=.506) + (u>=.672) + (u>=.782)
label define smeb 1 "Below SMEB (<$87)" 2 "SMEB-MEB ($87-113)" 3 "MEB-125%MEB ($114-142)" 4 "125%+MEB (>=$143)"
label values smeb_cat smeb
drop u

*-----------------------------------------------------------------------------
* Latent household poverty-risk factor: drives correlation among the 21
* deprivation indicators AND their correlation with the covariates in X below.
* Governorate shifts follow Lyons et al.'s regional gradient (Table 3):
* Baalbek-Hermel and Bekaa poorer, Beirut and Mount Lebanon better off.
*-----------------------------------------------------------------------------
gen double gov_effect = 0
replace gov_effect =  .30 if governorate==2
replace gov_effect =  .20 if governorate==4
replace gov_effect = -.30 if governorate==3
replace gov_effect = -.20 if governorate==6

gen double poverty_risk = -.5*(educ_head-3)/1.5 - .4*worked_last_week - .3*(income_source==1) ///
    + .5*dependent_share + .4*(smeb_cat==1) - .3*(smeb_cat==4) - .2*married + .3*female_head ///
    + gov_effect + rnormal(0,0.8)
egen double risk_z = std(poverty_risk)

*-----------------------------------------------------------------------------
* 21 binary deprivation indicators, 5 dimensions (Lyons et al. Table 2:
* deprivation cutoffs, reported prevalence, indicator-loading on risk_z)
*-----------------------------------------------------------------------------
local names "special_needs healthcare_access food_coping diet_diversity child_school adult_schooling electricity sanitation drinking_water cooking_fuel basic_assets crowding shelter_conditions housing_stability unemployment underemployment legal_residency area_settlement communications movement_mobility community_interaction"
local prev  "0.5195 0.0929 0.3738 0.3171 0.1962 0.1563 0.4013 0.3164 0.1159 0.1553 0.7045 0.3212 0.3050 0.1730 0.2269 0.4644 0.5500 0.1606 0.1028 0.2476 0.2093"
local loads ".5 .6 .7 .6 .7 .8 .5 .5 .6 .5 .4 .4 .5 .4 .9 .8 .3 .4 .4 .3 .3"
forvalues i = 1/21 {
    local nm : word `i' of `names'
    local p  : word `i' of `prev'
    local b  : word `i' of `loads'
    gen byte `nm' = runiform() < invlogit(logit(`p') + `b'*risk_z)
}

*-----------------------------------------------------------------------------
* Multidimensional livelihood index (MLI = H x A), baseline equal-dimension
* weights: 0.05 x 4 health/food, 0.10 x 2 education, 0.025 x 8 living
* standards, 0.10 x 2 employment, 0.04 x 5 security/social -- Table 2.
*-----------------------------------------------------------------------------
gen double dep_score = .05*(special_needs+healthcare_access+food_coping+diet_diversity) ///
    + .10*(child_school+adult_schooling) ///
    + .025*(electricity+sanitation+drinking_water+cooking_fuel+basic_assets+crowding+shelter_conditions+housing_stability) ///
    + .10*(unemployment+underemployment) ///
    + .04*(legal_residency+area_settlement+communications+movement_mobility+community_interaction)

gen byte poor_mdim = dep_score >= 0.33          // Alkire-Santos (2014) cutoff, used by Lyons et al.
quietly summarize poor_mdim
scalar H = r(mean)
quietly summarize dep_score if poor_mdim==1
scalar A = r(mean)
di as result "Headcount H = " %5.3f H "   Intensity A = " %5.3f A "   MLI = H*A = " %5.3f (H*A)

*=============================================================================
* Three-stage FGLS (Chaudhuri et al. 2002, as used in Lyons et al. Section
* 5.2 / Table 4): welfare = dep_score, poverty cutoff = 0.33, vulnerable if
* Pr(dep_score > 0.33 | X) >= 0.5.
*=============================================================================
gen byte below_smeb     = smeb_cat==1
gen byte smeb_meb        = smeb_cat==2
gen byte meb_125         = smeb_cat==3
gen byte inc_employment  = income_source==1
gen byte inc_assistance  = income_source==2
gen byte inc_borrowing   = income_source==3

global X age_head female_head married i.educ_head worked_last_week hhsize dependent_share ///
    inc_employment inc_assistance inc_borrowing borrowed below_smeb smeb_meb meb_125 i.governorate

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
gen byte vulnerable = Vh >= 0.5 if !missing(Vh)   // Chaudhuri et al. (2002) / Lyons et al. eq. (8) cutoff

gen vtp_group = .
label define vtplbl 1 "Chronic poor" 2 "Transient poor" 3 "Escaped poverty" 4 "Non-poor"
replace vtp_group = 1 if poor_mdim==1 & vulnerable==1
replace vtp_group = 2 if poor_mdim==0 & vulnerable==1
replace vtp_group = 3 if poor_mdim==1 & vulnerable==0
replace vtp_group = 4 if poor_mdim==0 & vulnerable==0
label values vtp_group vtplbl

di as result "=============================================================="
di as result " Vulnerability-to-poverty groups"
tabulate vtp_group
quietly summarize vulnerable
di as result "Overall vulnerability rate: " %5.2f (100*r(mean)) "%"
di as result "=============================================================="
tabstat dep_score poor_mdim vulnerable, by(governorate) stat(mean n)

save "vasyr_synthetic_example.dta", replace
di as result "Saved vasyr_synthetic_example.dta -- N = " _N
