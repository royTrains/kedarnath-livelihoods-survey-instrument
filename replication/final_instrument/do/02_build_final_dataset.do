*=============================================================================
* KEDARNATH YATRA WORKERS -- FINAL INSTRUMENT, WORKED-EXAMPLE DATASET (v2)
*
* Step 2 of 3. Input : data/raw_asked.csv (made by do/01_generate_raw.py; only
*                      what the questionnaire asks or records, as numeric codes)
*              Output: data/kedarnath_final_n200_full.dta    (200 recruited)
*                      data/kedarnath_final_n200_fielded.dta (retained==1)
*
* What this file does
*   1. reads the raw answers and turns the interview date into a Stata date
*   2. CONSTRUCTS every derived variable from the asked ones (dictionary group X)
*      -- income and months of work come from the 12-month calendar; the five
*         employment deprivations come from the Apablaza et al. (2026) Appendix 2
*         questions; consumption from the questionnaire's item list
*   3. checks the data against the questionnaire's skip rules and ranges
*   4. applies variable labels, value labels, notes and variable order
*      (do/labels.do, written from questionnaire/dictionary.py)
*
* EVERYTHING HERE IS SYNTHETIC. It tests the instrument and the pipeline;
* it is not a finding about Kedarnath workers.
*
* Stata gotcha kept from the earlier pipeline: missing is +infinity in
* comparisons, so every threshold on a variable that can be missing is guarded.
*=============================================================================
version 17
clear all
set more off
cd "D:\OneDrive\Desktop\vulnerability-2-poverty\replication\final_instrument"     // <-- change to your folder
capture log close
log using "checks/build_final_log.log", replace text

import delimited "data/raw_asked.csv", clear varnames(1) case(preserve)

* ---- 1. dates -------------------------------------------------------------------
gen interview_date_n = date(interview_date, "YMD")
drop interview_date
rename interview_date_n interview_date
format interview_date %tdDD-Mon-CCYY

*=============================================================================
* 2. CONSTRUCTED VARIABLES  (dictionary group X)
*=============================================================================
* education: the direct year count when known; otherwise the midpoint of the fallback bracket
* (education_level_cat), asked only of respondents who could not recall an exact number. Missing
* only for "prefer not to say" (education_level_cat==98).
gen double education_years = years_schooling
replace education_years = 0  if missing(education_years) & education_level_cat==1
replace education_years = 2  if missing(education_years) & education_level_cat==2
replace education_years = 7  if missing(education_years) & education_level_cat==3
replace education_years = 11 if missing(education_years) & education_level_cat==4

*-----------------------------------------------------------------------------
* AUTOMATIC FILLS for questions the form deliberately hides.
* Both of these are skipped on the tablet because the answer is already known,
* which means Kobo returns an EMPTY cell, not the implied value. Filling them
* here is what turns the form's silence into data; without it, the household
* head's sex is lost for every self-headed household (over half the sample).
*-----------------------------------------------------------------------------
replace main_income_earner = 1 if n_earners==1 & missing(main_income_earner)

* Head's sex is no longer asked: it is carried by the gendered relationship categories
* (husband/wife, father/mother, son/daughter, brother/sister, other male/female), and when the
* respondent IS the head it is simply their own sex. One question instead of two.
gen byte hoh_female = .
replace hoh_female = female if hoh_relation==1
replace hoh_female = 0 if inlist(hoh_relation,2,4,6,8,10,12)
replace hoh_female = 1 if inlist(hoh_relation,3,5,7,9,11,13)

* migration and site
gen byte migrant = (origin>1) if !missing(origin)
* rural/urban is now DERIVED from the administrative tier rather than asked separately: a
* gram-panchayat village is rural, everything above it urban. This is what picks the rural or
* urban poverty line for this respondent.
gen byte home_rural_urban = cond(home_admin_level==1, 1, 2)
* credit_source is gated behind took_loan_12m, so it is MISSING for non-borrowers. These two are
* defined for everyone, which is what the VEP regressions need -- using credit_source directly
* would drop every non-borrowing household from the FGLS sample.
gen byte credit_institutional = (took_loan_12m==1 & inrange(credit_source,1,4))
gen byte credit_informal      = (took_loan_12m==1 & inrange(credit_source,5,8))
gen byte health_access_tier = 2
* Health-access tier from the interview GPS, not from a hand-coded cluster (location_cluster was
* dropped 2026-09-24). The route runs from the road-head and its hospital up to the shrine, so
* position along it is what determines how reachable care is. Bands from the research team's route
* crosswalk; only the band enters the analysis, so no named site reaches the exported data.
replace health_access_tier = 3 if gps_lat <  30.58
replace health_access_tier = 1 if gps_lat >= 30.66 & !missing(gps_lat)
* health_insurance_covered was removed: "is your household covered" does not name a group a split
* migrant household can answer for. n_health_insured (a count of covered members) replaces it.
* NOTE this is no longer an MPI indicator -- the health dimension now uses NITI's own mortality and
* maternal indicators -- it survives only as a VEP exposure covariate.
gen byte health_access_deprived = (health_access_tier==1) | (health_access_tier==2 & n_health_insured==0)

* ---- monthly calendar: months of work, start/end of the Yatra work, incomes ----
gen byte yatra_months = 0
gen byte offseason_months_worked = 0
gen byte months_no_work = 0
gen byte yatra_start_month = .
gen byte yatra_end_month   = .
* Idle months: the form hides the earnings question when the month is coded "no paid work", so Kobo
* returns an empty cell. Fill it with the zero it means BEFORE anything sums these columns --
* otherwise a worker with any idle month gets a missing annual income instead of a correct one.
forvalues m = 1/12 {
    replace income_m`m' = 0 if status_m`m'==8 & knows_monthly_income==1 & missing(income_m`m')
}

gen double yatra_income = 0
gen double non_yatra_income = 0
forvalues m = 1/12 {
    replace yatra_months            = yatra_months + 1            if status_m`m'==1
    replace offseason_months_worked = offseason_months_worked + 1 if inrange(status_m`m',2,7)
    replace months_no_work          = months_no_work + 1          if status_m`m'==8
    replace yatra_income     = yatra_income + income_m`m'         if status_m`m'==1 & knows_monthly_income==1
    replace non_yatra_income = non_yatra_income + income_m`m'     if status_m`m'!=1 & knows_monthly_income==1
}

*-----------------------------------------------------------------------------
* ANNUAL-TOTAL FALLBACK (Apablaza Q15 route). Respondents who could not give
* twelve monthly figures gave one annual total plus the share of it earned in
* Yatra work; that pair is reweighted back onto the calendar here so every
* downstream variable has the same definition on both paths.
*-----------------------------------------------------------------------------
gen byte income_from_fallback = (knows_monthly_income==0)
replace yatra_income     = income_annual_total * pct_income_yatra/100       if income_from_fallback==1
replace non_yatra_income = income_annual_total * (100-pct_income_yatra)/100 if income_from_fallback==1

* per-month equivalents on the fallback path, used for the seasonality CV below.
* GUARD: a respondent whose calendar is all Yatra months (or no Yatra months) would divide by
* zero, so each side is only defined where its own month count is positive.
gen double income_pm_yatra_eq = .
gen double income_pm_other_eq = .
replace income_pm_yatra_eq = yatra_income/yatra_months          if income_from_fallback==1 & yatra_months>0
replace income_pm_other_eq = non_yatra_income/(12-yatra_months) if income_from_fallback==1 & yatra_months<12
forvalues m = 12(-1)1 {
    replace yatra_start_month = `m' if status_m`m'==1
}
forvalues m = 1/12 {
    replace yatra_end_month = `m' if status_m`m'==1
}
* main activity outside the Yatra work: modal status among the non-Yatra months
forvalues k = 2/8 {
    gen byte _c`k' = 0
    forvalues m = 1/12 {
        replace _c`k' = _c`k' + 1 if status_m`m'==`k'
    }
}
egen byte _maxc = rowmax(_c2 _c3 _c4 _c5 _c6 _c7 _c8)
gen byte offseason_primary = 8
forvalues k = 7(-1)2 {
    replace offseason_primary = `k' if _c`k'==_maxc
}
drop _c2-_c8 _maxc

gen double remittance_outward_annual = yatra_months*remit_out_yatra_pm + (12-yatra_months)*remit_out_offseason_pm
gen double remittance_inward_annual  = yatra_months*remit_in_yatra_pm  + (12-yatra_months)*remit_in_offseason_pm
gen double total_annual_income = yatra_income + non_yatra_income + remittance_inward_annual
gen double yatra_income_share  = round(yatra_income/total_annual_income, 0.001)

* income seasonality: coefficient of variation of the 12 monthly earnings (n-1 divisor).
* Calendar path uses the twelve reported figures. Fallback path uses the two-level series implied
* by the annual total and its Yatra share -- income_pm_yatra_eq in each Yatra month and
* income_pm_other_eq in each other month -- computed in closed form rather than by materialising
* twelve columns. Same mean, same n-1 divisor, so the two paths are on the same scale.
*
* CAVEAT, carried into the analysis: the fallback series has NO within-season variation by
* construction, so its CV measures only the between-season swing and is a LOWER BOUND on true
* seasonality. income_seasonality_cv is an Exposure covariate in all three VEP arms, so always
* split or interact on income_from_fallback -- the two paths are not the same measurement.
egen double _mean12 = rowmean(income_m1-income_m12)
egen double _sd12   = rowsd(income_m1-income_m12)
gen double income_seasonality_cv = _sd12/_mean12 if income_from_fallback==0
drop _mean12 _sd12

gen double _fbmean = (yatra_income + non_yatra_income)/12 if income_from_fallback==1
gen double _fbss = yatra_months*(cond(missing(income_pm_yatra_eq),0,income_pm_yatra_eq) - _fbmean)^2 ///
                 + (12-yatra_months)*(cond(missing(income_pm_other_eq),0,income_pm_other_eq) - _fbmean)^2 ///
                 if income_from_fallback==1
replace income_seasonality_cv = sqrt(_fbss/11)/_fbmean if income_from_fallback==1 & _fbmean>0
drop _fbmean _fbss

*-----------------------------------------------------------------------------
* SEASONAL GATE. Households that said their spending does not differ between
* the seasons were not asked the off-season figures at all; the Yatra-season
* figure is carried across for them. Done BEFORE any season weighting, so
* everything downstream sees a complete pair either way.
* WATCH THIS SHARE: a gate that saves nine questions is attractive to a tired
* respondent, and over-use would pull measured consumption toward the
* Yatra-season level, which runs about a third higher.
*-----------------------------------------------------------------------------
foreach v in staples perishables food_own food_out packaged_food pan_tobacco fuel ///
             routine_misc transport_comm rent med_nonhosp {
    replace cons_`v'_offseason_pm = cons_`v'_yatra_pm if spend_differs_by_season==0
}

* ---- consumption (Chaudhuri welfare measure), narrow and adult-equivalent versions ----
* Workers are migrants, so a module fielded during the Yatra season cannot stand for the whole year.
* Every seasonal item (9 pairs in Module E) is asked as a usual monthly amount for the Yatra season
* and for the off-season, then combined the same way as income: Yatra months at the Yatra-season
* rate, the rest of the year at the off-season rate, divided by 12 for an annual-average monthly
* figure. Recall periods within each season follow HCES 2022-23 / IHDS-II; see the questionnaire PDF
* section 8. Medical spending is split by HCES/IHDS-II into non-hospitalisation and hospitalisation.
foreach v in staples perishables food_own food_out packaged_food pan_tobacco fuel routine_misc transport_comm rent med_nonhosp {
    gen double cons_`v'_pm = (yatra_months*cons_`v'_yatra_pm + (12-yatra_months)*cons_`v'_offseason_pm)/12
}
* packaged food is inside HCES's own food block (Section 7), so it joins the food aggregate.
* pan/tobacco/intoxicants is a SEPARATE MPCE category in HCES and is added to the total below, not here.
gen double cons_food_pm = cons_staples_pm + cons_perishables_pm + cons_food_own_pm + cons_food_out_pm + cons_packaged_food_pm
gen long cons_medical_12m = round(cons_med_nonhosp_pm*12) + cons_medical_hosp_12m
foreach v in clothing education durables {
    gen int cons_`v'_12m_pm = round(cons_`v'_12m/12)
}
gen double cons_medical_12m_pm = cons_med_nonhosp_pm + round(cons_medical_hosp_12m/12)
gen double total_cons_pm = cons_food_pm + cons_pan_tobacco_pm + cons_fuel_pm + cons_routine_misc_pm + cons_transport_comm_pm + cons_rent_pm ///
    + cons_clothing_12m_pm + cons_education_12m_pm + cons_medical_12m_pm + cons_durables_12m_pm
gen int cons_pc_pm = round(total_cons_pm/hhsize)
gen double cons_pc_pm_narrow = (cons_food_pm + cons_pan_tobacco_pm + cons_fuel_pm + cons_routine_misc_pm + cons_transport_comm_pm + cons_rent_pm)/hhsize
gen double cons_pc_ae_pm = total_cons_pm/(hhsize - n_children_u15 + 0.5*n_children_u15)
* Sethu et al. (2024) give TWO Rangarajan-method lines for 2022-23: Rs 2,515 rural, Rs 3,639 urban.
* home_rural_urban picks the applicable one from the respondent's USUAL residence, not the worksite.
* Before that variable existed this applied the rural line to everyone, measuring urban-resident
* workers against a line 31 percent too low.
gen int poverty_line = cond(home_rural_urban==1, 2515, 3639)
gen byte poor = (cons_pc_pm < poverty_line)
gen byte poor_sensitivity_cpi = (cons_pc_pm < 1850) if !missing(cons_pc_pm)  // Rangarajan & Dev 2024, sensitivity

* assets and MPI school attendance
gen byte durables_count = owns_tv + owns_radio + owns_bicycle + owns_motorcycle + owns_car + owns_fridge
*=============================================================================
* SHOCKS AND COPING: split the two check-all exports into binaries
* Kobo exports a select_multiple as a space-separated string of chosen codes.
* The " k " padding stops code 5 matching inside code 15.
*=============================================================================
gen str _sh = " " + trim(distress_event_last365d) + " "
forvalues k = 1/8 {
    gen byte shock_`k' = strpos(_sh, " `k' ") > 0
}
drop _sh
gen str _cp = " " + trim(shock_coping) + " "
forvalues k = 1/6 {
    gen byte cope_`k' = strpos(_cp, " `k' ") > 0
}
drop _cp
egen byte shock_count = rowtotal(shock_1-shock_8)
gen byte shock_any = shock_count > 0
* COVARIATE shocks hit the whole route at once -- a bad-weather year, a blocked road, a curtailed
* Yatra, a collapse in pilgrim numbers. IDIOSYNCRATIC shocks hit one household. Separating them is
* what makes the covariate/idiosyncratic decomposition identifiable; the old single-answer item,
* whose every code was idiosyncratic, could not support it at all.
gen byte shock_covariate     = (shock_3 | shock_5 | shock_6 | shock_7)
gen byte shock_idiosyncratic = (shock_1 | shock_2 | shock_4 | shock_8)
* kept as their own variables because the asset-smoothing test compares them directly, and they
* are no longer forced to be mutually exclusive
gen byte coped_sold_assets     = cope_3
gen byte coped_cut_consumption = cope_4


gen byte productive_assets_count = owns_cow_buffalo + owns_goat_sheep + owns_pony_mule + owns_shop_stall + owns_work_vehicle + owns_work_equipment
*-----------------------------------------------------------------------------
* MPI LIVING-STANDARD INDICATORS, to NITI Aayog's actual rules.
* All three were previously mis-specified: water had no distance limb, fuel was
* an LPG yes/no rather than NITI's list of dirty fuels, and assets were a plain
* six-item count rather than NITI's "more than one of eight, plus car/truck".
*-----------------------------------------------------------------------------
* water: unimproved source (7-9), OR improved but over a 30-minute round trip
gen byte water_deprived = inrange(drinking_water,7,9) | ///
    (water_on_premises==0 & water_fetch_minutes>30 & !missing(water_fetch_minutes))
* fuel: NITI names firewood, dung, crop residue/shrubs, charcoal, coal. Kerosene (5) is NOT on
* that list and so is not counted here; the global MPI does count it, hence the raw code is kept.
gen byte cooking_fuel_deprived = inlist(cooking_fuel,6,7,8,9,10)
* assets: NITI's eight small assets, with car/truck as a separate limb
egen byte mpi_asset_count = rowtotal(owns_radio owns_tv owns_phone owns_computer ///
    owns_animal_cart owns_bicycle owns_motorcycle owns_fridge)
gen byte mpi_asset_deprived = (mpi_asset_count <= 1) & owns_car==0

*=============================================================================
* NITI AAYOG NATIONAL MPI -- the indicators at NITI's own weights.
*   Health   1/3 = Nutrition 1/6 + Child & Adolescent Mortality 1/12 + Maternal 1/12
*   Educ     1/3 = Years of Schooling 1/6 + School Attendance 1/6
*   Living   1/3 = seven indicators at 1/21 each
* NUTRITION IS NOT COLLECTED: NITI defines it on measured height/weight, which a read-aloud
* worksite interview cannot produce. Its 1/6 is redistributed proportionally over the other ten.
* Report the result as a TEN-of-twelve adaptation, never as the National MPI.
*=============================================================================
gen byte mpi_mortality_dep   = (child_death_5y==1)
gen byte mpi_maternal_dep    = (birth_last_5y==1 & (anc_4_visits!=1 | skilled_birth_attendant!=1))
gen byte mpi_schooling_dep   = (any_member_6yr_schooling==0)
gen byte mpi_housing_dep     = (floor_material==1 | roof_material==1 | wall_material==1)
gen byte mpi_sanitation_dep  = inlist(toilet_type,1,2,3)
gen byte mpi_electricity_dep = (electricity==0)
gen byte mpi_bank_dep        = (has_bank_account==0)

* school attendance: not deprived where there is no child in the class-1-to-8 age range
gen byte mpi_attendance_dep = cond(n_children_6_14>0, n_children_out_school>0, 0)
gen double mpi_score = ( (1/12)*mpi_mortality_dep + (1/12)*mpi_maternal_dep ///
    + (1/6)*mpi_schooling_dep + (1/6)*mpi_attendance_dep ///
    + (1/21)*(cooking_fuel_deprived + mpi_sanitation_dep + water_deprived + mpi_electricity_dep ///
              + mpi_housing_dep + mpi_asset_deprived + mpi_bank_dep) ) / (1 - 1/6)
gen byte mpi_poor = (mpi_score >= 1/3) if !missing(mpi_score)

gen byte child_school_dep = (n_children_out_school>0) if n_children_6_14>0 & !missing(n_children_out_school)

* ---- reduced Coping Strategy Index (rCSI), standard WFP weights 1/2/1/1/3, Yatra-season/off-season
* pairs weighted into an annual average the same way as income and consumption ----
gen int rcsi_yatra_wk = cope_less_pref_food_yatra_wk + 2*cope_borrow_food_yatra_wk + cope_reduce_meals_yatra_wk ///
    + cope_reduce_portion_yatra_wk + 3*cope_restrict_adult_yatra_wk
gen int rcsi_offseason_wk = cope_less_pref_food_offseason_wk + 2*cope_borrow_food_offseason_wk + cope_reduce_meals_offseason_wk ///
    + cope_reduce_portion_offseason_wk + 3*cope_restrict_adult_offseason_wk
gen double rcsi_score = (yatra_months*rcsi_yatra_wk + (12-yatra_months)*rcsi_offseason_wk)/12
gen byte food_coping_deprived = (rcsi_score > 20) if !missing(rcsi_score)   // Lyons et al. 2023 / VASyR cutoff

* ---- employment quality: five Apablaza et al. (2026) core domains, equal weights ----
gen int hours_week_yatra = hours_day_yatra*days_week_yatra
gen double hours_week_offseason = hours_day_offseason * days_week_offseason
* averaged over the months actually WORKED, so idle months do not drag it toward zero -- idleness is
* already measured by months_no_work, and counting it here as well would penalise it twice.
gen double hours_week_annual = .
replace hours_week_annual = (yatra_months*hours_week_yatra + ///
    offseason_months_worked*cond(missing(hours_week_offseason),0,hours_week_offseason)) ///
    / (yatra_months + offseason_months_worked) if (yatra_months + offseason_months_worked) > 0

gen double work_income_pm = (yatra_income + non_yatra_income)/12
quietly summarize work_income_pm, detail
local med = r(p50)
* access: unemployed >6 months (and spent time searching) OR under 20 h/week and wanting more
gen byte emp_dep_access = (months_no_work>6 & months_looked_for_work>0) | (wants_more_work==1 & hours_week_yatra<20)
* compensation: fallback threshold (67% of the sample median)
gen byte emp_dep_comp   = (work_income_pm < 0.67*`med') if !missing(work_income_pm)
* security: wage workers = no signed contract; self-employed = business not registered
gen byte emp_dep_sec    = .
replace  emp_dep_sec    = (contract_status!=1)       if inlist(employment_type,3,4) & !missing(contract_status)
replace  emp_dep_sec    = (workplace_registered==0)  if inlist(employment_type,1,2)
* stability: under 1 year in this work, or occasional/casual job
* Apablaza Table 3 sets two tenure thresholds, not one: wage workers under 6 months, self-employed
* under 12. Tenure here is in Yatra SEASONS and a season is roughly six months of work, so that maps
* to under 1 season for wage workers and under 2 for the self-employed. Applying a single under-1-year
* rule to both, as this previously did, overstated deprivation among wage workers.
gen byte emp_dep_stab = ((inlist(employment_type,3,4) & years_in_yatra_work < 1) | ///
                         (inlist(employment_type,1,2) & years_in_yatra_work < 2) | ///
                         job_permanence==3)
* conditions: workplace injury or death in the last 12 months, or neither work health insurance nor a pension
gen byte emp_dep_cond   = (workplace_injury_12m==1) | (work_health_ins==3 & pension_contrib==3)
egen byte emp_dep_count = rowtotal(emp_dep_access emp_dep_comp emp_dep_sec emp_dep_stab emp_dep_cond)
gen double emp_dep_score = emp_dep_count/5
gen byte emp_poor_k2    = (emp_dep_count>=2)

* task block summaries
local tkl tk_load tk_drive tk_engine tk_electric tk_safety tk_sell tk_cash tk_cook tk_serve tk_clean tk_guide tk_coord
egen byte tk_regular_n = anycount(`tkl'), values(1)
egen byte tk_prior_n   = anycount(`tkl'), values(2)

*=============================================================================
* MULTIPLE WORK-HOLDING: split the check-all export into one binary per choice
* Kobo exports a select_multiple as a space-separated string of the chosen
* codes. " 5 " padding means code 5 never matches code 15 by accident.
*=============================================================================
gen str _oat = " " + trim(other_activity_types) + " "
forvalues k = 1/14 {
    gen byte other_act_`k' = strpos(_oat, " `k' ") > 0
}
drop _oat
egen byte n_other_act_checked = rowtotal(other_act_1-other_act_14)
* the respondent's own count vs. the boxes actually ticked. Not an assertion: in real data these
* WILL sometimes disagree, and the disagreement is the signal -- if it is common the item needs
* rewording before scale-up.
gen byte other_act_mismatch = (n_other_act_checked != n_other_activities)

*=============================================================================
* EX-ANTE DIRECTION OF THE REQUIRED SKILL MOVE (Nawakitphaitoon & Ormiston 2016)
*
* Ormiston transferability is asymmetric: the share of a worker's skills usable
* at a destination is not the share of the destination's requirements the worker
* already has, and N&O read that asymmetry as direction -- moves up are not moves
* down. Both sides come from the task grid already asked, so this classifies what
* KIND of retraining a move needs before anyone has moved.
*
* Worker profile uses codes 1 AND 2 (does it now, or has done it before
* elsewhere): prior capability outside the current job is precisely what a
* transfer question is about. Destination profiles are q_oj, the share of workers
* in occupation j who do task j regularly (Gathmann & Schonberg's definition).
*=============================================================================
foreach v of local tkl {
    gen byte _w_`v' = inlist(`v',1,2)          // worker can do it (now or before)
    gen byte _r_`v' = (`v'==1)                 // does it regularly now -> feeds q_oj
}
* q_oj: mean of _r_ within each occupation
foreach v of local tkl {
    bysort occupation: egen double _q_`v' = mean(_r_`v')
}
* for every candidate destination j, the worker's coverage of j and retention in j
gen double task_cover_best = .
gen double task_retain_best = .
gen byte   best_alt_occupation = .
quietly forvalues j = 1/14 {
    * destination j's task profile, broadcast to every row
    foreach v of local tkl {
        summarize _q_`v' if occupation==`j', meanonly
        scalar _qj_`v' = cond(r(N)>0, r(mean), 0)
    }
    gen double _num = 0
    gen double _den_j = 0
    gen double _den_w = 0
    foreach v of local tkl {
        replace _num   = _num   + _qj_`v' * _w_`v'
        replace _den_j = _den_j + _qj_`v'
        replace _den_w = _den_w + _w_`v'
    }
    gen double _cov = cond(_den_j>0, _num/_den_j, .)     // share of j's requirements already held
    gen double _ret = cond(_den_w>0, _num/_den_w, .)     // share of own skills j would use
    * keep the best alternative occupation the respondent is not already in
    replace best_alt_occupation = `j' if occupation!=`j' & !missing(_cov) ///
        & (missing(task_cover_best) | _cov > task_cover_best)
    replace task_retain_best    = _ret if occupation!=`j' & !missing(_cov) ///
        & (missing(task_cover_best) | _cov > task_cover_best)
    replace task_cover_best     = _cov if occupation!=`j' & !missing(_cov) ///
        & (missing(task_cover_best) | _cov > task_cover_best)
    drop _num _den_j _den_w _cov _ret
}
* direction, both sides split at 0.5
gen byte skill_move_type = .
replace skill_move_type = 1 if task_cover_best >= .5 & task_retain_best >= .5 & !missing(task_cover_best)
replace skill_move_type = 2 if task_cover_best <  .5 & task_retain_best >= .5 & !missing(task_cover_best)
replace skill_move_type = 3 if task_cover_best <  .5 & task_retain_best <  .5 & !missing(task_cover_best)
replace skill_move_type = 4 if task_cover_best >= .5 & task_retain_best <  .5 & !missing(task_cover_best)
drop _w_* _r_* _q_*

*=============================================================================
* 3. CHECKS AGAINST THE QUESTIONNAIRE (skip rules, ranges, logic)
*=============================================================================
isid resp_id
assert consent==1
assert inrange(occupation,1,14) & inrange(employment_type,1,4)
assert inlist(enum_id,1,2,3,4)
* Apablaza Q5 routes its eleven categories three ways, so Module K has three gates, not one.
gen byte k_working = inlist(job_situation,1,2,3)        // 1-3: the whole job-quality block
gen byte k_tail    = inrange(job_situation,1,7)         // 1-7: also routed to Q21 (wants_more_work)
gen byte k_seeking = (job_situation==8)                 // 8:   routed straight to Q22/Q23
* skip rules: answered exactly when the filter says so
assert missing(contract_status)   == !(k_working==1 & inlist(employment_type,3,4))
assert missing(leave_rights)      == (k_working!=1)   // asked of everyone still working, not wage-only
foreach v in employer_type workplace_registered pension_contrib work_health_ins injured_ever workplace_injury_12m {
    assert missing(`v') == (k_working!=1)
}
* wants_more_work is gated at codes 1-7, not 1-3: Apablaza routes the studying, in-training,
* retired and unpaid-care categories straight to it, and dropping them would lose exactly the
* respondents an underemployment question exists to reach.
assert missing(wants_more_work) == (k_tail!=1)
assert missing(job_permanence)    == (k_working!=1)
* more_hours_day also fires for code 8 (unemployed and seeking), which Apablaza routes here directly
assert missing(more_hours_day)   == !(wants_more_work==1 | k_seeking==1)
assert (loan_collateral==.) == !(loan_against_asset==1)
assert (pays_interest==.)   == (took_loan_12m==0)
assert missing(months_looked_for_work) == !(months_no_work>0 | k_seeking==1)
* prev_occ is free text now, so "missing" means an empty string, not a system missing
assert (prev_occ=="")             == (prev_occ_change!=1)
assert inrange(home_admin_level,1,4)
assert inrange(toilet_type,1,4)
assert inrange(wall_material,1,3)
assert (anc_4_visits==.)            == (birth_last_5y==0)
assert (skilled_birth_attendant==.) == (birth_last_5y==0)
assert inrange(mpi_score,0,1)
assert (credit_source==.)            == (took_loan_12m==0)
assert (loan_amount==.)              == (took_loan_12m==0)
assert (loan_against_asset==.)       == (took_loan_12m==0)
assert (has_jandhan_account==.)      == (has_bank_account==0)
assert (has_crop_insurance==.)       == (land_cultivable_acres==0)
assert (meal_spend_day_self==.)      == (cooks_own_meals_here==1)   // 1 = cooks own
assert n_health_insured    <= hhsize
assert n_life_insured      <= hhsize
assert n_can_transact_online <= hhsize
assert inrange(drinking_water,1,9)
assert inlist(cooking_fuel,1,2,3,4,5,6,7,8,9,10)
assert missing(water_fetch_minutes) == (water_on_premises==1)
assert missing(water_fetched_by)    == (water_on_premises==1)
assert missing(hours_day_offseason) == (offseason_months_worked==0)
assert missing(days_week_offseason) == (offseason_months_worked==0)
assert (occupation_detail!="")  // verbatim job description, asked of everyone
assert (native_language_other=="") == !inlist(native_language,96,97)
assert missing(prev_occ_reason)   == (prev_occ_change!=1)
assert !missing(n_other_activities)          // count, asked of everyone (0 = none)
assert (other_activity_types=="") == (n_other_activities==0)
assert missing(other_activity_income_pm) == (n_other_activities==0)
assert missing(training_type)     == (training_received!=1)
assert (shock_coping=="")         == (distress_event_last365d=="")
assert missing(morbidity_coping_15d) == (morbidity_15d==0)
assert missing(morbidity_cost_15d)   == (morbidity_15d==0)
assert missing(migration_referral) == (migrant!=1)
assert missing(usual_residence_differs) == (migrant!=1)
assert missing(years_schooling)   == (knows_years_schooling==0)
assert missing(education_level_cat) == (knows_years_schooling==1)
assert hoh_female==female if hoh_relation==1   // self-headed: head's sex is the respondent's own
assert !missing(hoh_female)                    // derived for every row, never asked
assert main_income_earner==1 if n_earners==1   // automatic fill: sole earner is the main earner
assert missing(n_children_out_school) == (n_children_6_14==0)
foreach v in drove_twowheeler drove_car drove_heavy {
    assert missing(`v') == !inlist(tk_drive,1,2)
}
* calendar logic
* The "earnings are 0 exactly when the month was idle" rule only applies on the calendar path:
* fallback respondents are never asked the monthly figures, so theirs are missing, not zero.
assert missing(income_m1) if income_from_fallback==1
assert !missing(income_annual_total) & !missing(pct_income_yatra) if income_from_fallback==1
assert missing(income_annual_total) & missing(pct_income_yatra)   if income_from_fallback==0
assert inrange(pct_income_yatra,0,100) if income_from_fallback==1
assert !missing(income_seasonality_cv) | (yatra_income+non_yatra_income)==0
forvalues m = 1/12 {
    assert inrange(status_m`m',1,8)
    assert (income_m`m'==0) == (status_m`m'==8) if income_from_fallback==0
}
assert yatra_months>=3 & yatra_months<=6
assert yatra_end_month - yatra_start_month + 1 == yatra_months
assert yatra_months + offseason_months_worked + months_no_work == 12
* logic
assert n_children_out_school <= n_children_6_14 if !missing(n_children_out_school)
assert n_children_6_14 <= n_children_u15 & n_children_u15 <= hhsize-1
assert n_earners >= 1 & n_earners <= hhsize
assert inrange(hours_day_yatra,1,18) & inrange(days_week_yatra,1,7)
assert inrange(n_other_activities,0,6)
assert inlist(job_permanence,1,2,3,4,5) if k_working==1
assert inlist(employer_type,1,2,3,4,5,6,7) if k_working==1
foreach v in cope_less_pref_food cope_borrow_food cope_reduce_meals cope_reduce_portion cope_restrict_adult {
    assert inrange(`v'_yatra_wk,0,7) & inrange(`v'_offseason_wk,0,7)
}
assert inrange(family_structure,1,2) | hhsize==1   // single-member code (3) only valid when hhsize==1
assert (family_structure==3) == (hhsize==1)
assert inrange(rcsi_score,0,7+14+7+7+21)   // max possible: 7*(1+2+1+1+3)
foreach v in injured_ever workplace_injury_12m wants_more_work {
    assert inlist(`v',0,1,97) if k_working==1
}
assert inlist(first_job_ever,0,1,97)
foreach v of local tkl {
    assert inlist(`v',1,2,3)
}
assert tk_regular_n + tk_prior_n <= 12
assert total_annual_income>0 & cons_pc_pm>0
foreach v in staples perishables food_own food_out packaged_food pan_tobacco fuel routine_misc transport_comm rent med_nonhosp {
    assert cons_`v'_yatra_pm >= 0 & cons_`v'_offseason_pm >= 0
}
assert cons_medical_hosp_12m >= 0
foreach v in remit_out remit_in {
    assert `v'_yatra_pm >= 0 & `v'_offseason_pm >= 0
}
* no duration assertion: interview_duration_min is empty until Kobo supplies real timestamps
assert interview_date >= mdy(6,15,2026)
* soft checks: counts reported, not asserted
count if occupation==11 & tk_drive!=1
di as text "Drivers not doing driving regularly (should be rare): " r(N)
count if trek_dependent==1 & !inlist(occupation,1,2,3,4,12)
di as text "Trek-dependent outside trek occupations (should be 0): " r(N)
count if tk_drive==3 & occupation==11
di as text "Drivers who say they never drive (should be 0): " r(N)
drop k_working k_tail k_seeking   // helpers only, not part of the questionnaire's variable list

*=============================================================================
* 4. LABELS, NOTES, ORDER
*=============================================================================
do "do/labels.do"

compress
sort resp_id
save "data/kedarnath_final_n200_full.dta", replace
preserve
* The "fielded" subset. In the SYNTHETIC pool that means retained==1, the simulated non-response
* flag. Real field data -- from Kobo or from the web form -- has no such variable, so there it means
* what it should mean: everyone who consented. Guarded so one do-file serves both.
capture confirm variable retained
if !_rc {
    keep if retained==1
}
else {
    keep if consent==1
}
save "data/kedarnath_final_n200_fielded.dta", replace
di as result "Fielded n = " _N
restore

di as result "======== SUMMARY OF THE FINAL FILE ========"
describe, short
summarize poor poor_sensitivity_cpi emp_poor_k2 income_seasonality_cv cons_pc_pm cons_pc_pm_narrow cons_pc_ae_pm
log close
