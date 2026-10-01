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

*-----------------------------------------------------------------------------
* FORCE THE TEXT COLUMNS TO STRING.
* import delimited types a column from what it happens to contain. A
* select_multiple exports space-separated CODES, so if every respondent in a
* batch picked exactly one activity -- or none -- the column looks numeric and
* is imported as a number, and the strpos() split below dies with a type
* mismatch. The same applies to any verbatim field a batch happens to fill
* with digits. Cheap to force; expensive to discover mid-fieldwork.
*-----------------------------------------------------------------------------
foreach v in other_activity_types distress_event_last365d shock_coping ///
             occupation_detail prev_occ target_occ native_language_other ///
             govt_schemes govt_scheme_other work_equipment_detail migration_referral_other ///
             closure_work_detail other_places_detail {
    capture confirm variable `v'
    if !_rc {
        capture confirm string variable `v'
        if _rc {
            tostring `v', replace force
            replace `v' = "" if `v'=="." 
        }
    }
}

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
* home_rural_urban is ASKED now (Module D), not derived. It used to be built from home_admin_level,
* a village/town/city tier -- which put the choice between the Rs 2,515 and Rs 3,639 poverty lines,
* a 45% difference, behind a Census classification the respondent had no way of making.
assert inrange(home_rural_urban,1,2)
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
* ---- measured seasonal base, from the Module C location row ----
* This is what replaces a season length assumed for everyone. Each respondent's own boundary is
* wherever their location row turns over, which is also the answer to the mid-month Yatra-start
* problem: we no longer need a single cut-off, because we no longer impose one.

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

* Type B in the closure-regime typology: sold labour away from BOTH bases. Stated (Module D) or
* revealed (the location row) -- either establishes it, because a respondent who names the place he
* worked has told us as much as one whose calendar shows the month.
* ---- measured seasonal base, from the absence spell (left_here_month / returned_here_month) ----
* Twelve loc_m items were replaced by the spell on 2026-09-30: in this population the absence is
* almost always one contiguous stretch, so twelve select_ones were a sixth of the interview for a
* variable two questions can carry. The spell STRADDLES THE NEW YEAR -- the Yatra closes in November
* and reopens in April or May -- so returned < left is the normal case and the arithmetic must wrap.
* mod() does that: mod(4 - 11, 12) = 5 months away, which is right.
gen byte months_away_total = 0
replace  months_away_total = mod(returned_here_month - left_here_month, 12) if resp_returns_at_closure==1
* a full-year absence is not possible for someone interviewed here in season; guard the degenerate case
replace  months_away_total = 11 if months_away_total==0 & resp_returns_at_closure==1
gen byte months_third_place = cond(worked_away_in_closure==1, months_away_for_work, 0)
replace  months_third_place = months_away_total if months_third_place > months_away_total
gen byte months_home_base   = months_away_total - months_third_place
gen byte months_here        = 12 - months_away_total

gen byte closure_labour_migrant = (worked_away_in_closure==1)
gen byte stays_all_year   = (resp_returns_at_closure==0)

* ---- indicators added for the Lyons et al. MLI and for VER --------------------------------------
* Settlement conditions at the WORKSITE. Deprived on the three codes that are not shelter in any
* ordinary sense: sleeping at the shop or dhaba, under canvas, or in the open.
gen byte dep_accom_here = inlist(accom_type_here,4,5,7)
label var dep_accom_here "Sleeps at the workplace, in a tent, or in the open, during the season"
* Washington Group Short Set cutoff: a lot of difficulty, or cannot do it at all.
gen byte dep_func_limit = inlist(func_limitation,3,4)
label var dep_func_limit "Serious difficulty walking or climbing (WG-SS cutoff)"
* Entitlement portability. A household with no ration card at all is deprived here too -- it has no
* portable entitlement either -- which is why the missing case codes to 1 rather than to missing.
gen byte dep_ration_portability = 1
replace  dep_ration_portability = 0 if ration_portable_here==1
label var dep_ration_portability "Cannot draw the ration entitlement at the worksite"
* shock_loss_share is built further down, once total_cons_pm exists.
* Did the worst shock land inside the earning season? Same shock, very different consequence.
gen byte shock_in_season = .
replace  shock_in_season = inrange(shock_month,5,11) if !missing(shock_month)
label var shock_in_season "Worst shock fell in the Yatra season (May-November)"
gen byte split_household  = (hh_at_home_place==1)
* The denominator the Yatra-season consumption figures actually belong to. This corrects a real error
* in the poverty headcount: per-capita consumption divided the Yatra-season figure -- which covers
* only "you and anyone staying with you here" -- by the FULL household size, so a man supporting
* himself here for six months while a family of five lived at the home place was recorded at a
* fraction of his true per-capita consumption and counted as poor by arithmetic.
gen byte cons_pc_denom_season = cond(split_household==1 & !missing(n_here_season), n_here_season, hhsize)
replace  cons_pc_denom_season = hhsize if cons_pc_denom_season > hhsize
* dq_closure_mismatch is gone. It compared the stated off-season-migration item against the calendar
* location row as two independent reports; months_third_place is now DERIVED from that same stated
* item, so the two cannot disagree and the flag could only ever have read zero.
* The two-season design does not fit a respondent who never moves: for them the Yatra-season and
* off-season questions describe the same place. Check the identical-answer rate at the pilot.
label var stays_all_year "Does not move at all when the Yatra closes"

* The activity row still carries two codes that encode LOCATION as well as activity -- 4 "wage
* labour, staying at home" and 5 "went away from home for work". Since the location row now carries
* location properly, those two can contradict it, and one combination is genuinely impossible
* rather than merely unusual: code 5 says the respondent left home for work, so the month cannot
* also be coded at a base. Counted, not asserted: the form does not stop an enumerator entering it.
* dq_act_loc_conflict is gone too, because the conflict it caught cannot arise any more: activity
* codes 4 and 5 no longer encode location (4 is casual wage labour, 5 is construction work), so
* nothing in the activity row can contradict where the respondent was.
* New check in its place: the reported off-season work months cannot exceed the absence itself.
gen byte dq_away_exceeds_spell = (worked_away_in_closure==1 & months_away_for_work > months_away_total)
* These two are built here rather than in dictionary.py, so labels.do does not label them.
label var dq_away_exceeds_spell "Months worked away exceed the reported absence from the Yatra route"

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
* The season weight is months_here -- months physically on the Yatra route, from the absence spell --
* not yatra_months, which counts months of Yatra WORK. They are not the same: a worker can be here in
* a month he did no Yatra work. The Yatra-season consumption figure describes spending WHILE HERE, so
* the months-here count is the weight it belongs to. Before the spell existed there was nothing else
* to use and yatra_months stood in.
foreach v in staples perishables food_own food_out packaged_food pan_tobacco fuel routine_misc transport_comm rent med_nonhosp {
    gen double cons_`v'_pm = (months_here*cons_`v'_yatra_pm + (12-months_here)*cons_`v'_offseason_pm)/12
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
*-----------------------------------------------------------------------------
* PER CAPITA, WITH A SEASON-SPECIFIC DENOMINATOR.
* This block used to divide total_cons_pm by hhsize and stop. That was wrong for
* split households, and wrong in the direction that manufactures poverty. The
* Yatra-season figures are asked as "you and anyone staying with you here"; the
* off-season figures are asked of "your household". Dividing the blend of the
* two by the FULL household size charged a man's own six months of on-site
* spending against five people, so a split household was recorded at a fraction
* of its true per-capita consumption and fell below the line by arithmetic
* alone. 53 of 200 records in the synthetic run are split households.
* So each season is divided by the number of people that season's figure
* actually covers, and only then averaged: n_here_season while he is here,
* hhsize once the household is reunited. Annual items (clothing, education,
* hospitalisation, durables) are household-wide and keep hhsize throughout.
* Known limitation, documented rather than papered over: what the family spends
* AT THE HOME PLACE during the season is not observed. The respondent cannot
* reliably report it, so this measures his own per-capita consumption level
* rather than a whole-household one for the season half. remit_out_yatra_pm is
* the best available proxy for the home-side flow and is collected.
*-----------------------------------------------------------------------------
local SEASONAL cons_food_pm + cons_pan_tobacco_pm + cons_fuel_pm + cons_routine_misc_pm + cons_transport_comm_pm + cons_rent_pm
* rebuild the seasonal block at each season's own level, rather than from the already-blended figures
gen double _cons_seas_yatra = 0
gen double _cons_seas_off   = 0
foreach v in staples perishables food_own food_out packaged_food pan_tobacco fuel routine_misc transport_comm rent {
    replace _cons_seas_yatra = _cons_seas_yatra + cons_`v'_yatra_pm
    replace _cons_seas_off   = _cons_seas_off   + cons_`v'_offseason_pm
}
gen double cons_annual_pm = cons_clothing_12m_pm + cons_education_12m_pm + cons_medical_12m_pm + cons_durables_12m_pm
* Dividing the on-site figure by the people here (n_here_season) is NOT the fix on its own. Tried that
* first and it overcorrected hard: split households went from 55% poor to 5% poor, because a man's
* on-site spending over 1.6 people looks affluent while ignoring that the same earnings support 4.1
* people at the home place. Both constructions are biased, in opposite directions.
* What closes it is that the home-side flow IS observed, as the remittance he sends during the season.
* So for a split household the season numerator is on-site spending PLUS remittances out, over the
* full household -- total household resources consumed that month, from the two places they are spent
* in. No double count: the off-season half uses household spending directly, by when the household is
* reunited and remittances have stopped. hhsize stays the denominator throughout, which is also the
* concept the Rangarajan per-capita line is defined on.
gen double _seas_num = _cons_seas_yatra + cond(split_household==1, remit_out_yatra_pm, 0)
gen double cons_pc_seasonal_pm = (months_here*(_seas_num/hhsize) ///
                               + (12-months_here)*(_cons_seas_off/hhsize))/12
gen int cons_pc_pm = round(cons_pc_seasonal_pm + cons_annual_pm/hhsize)
* Shock magnitude as a share of annual household consumption -- the per-unit denominator VER needs.
* Built here rather than with the other shock variables because it needs the consumption aggregate.
gen double shock_loss_share = shock_loss_amount/((cons_pc_seasonal_pm*hhsize + cons_annual_pm)*12) ///
    if !missing(shock_loss_amount)
label var shock_loss_share "Worst shock's loss as a share of annual household consumption"

*=============================================================================
* VARIABLES THAT WERE BEING ASKED AND NOT USED.
* checks/10_every_question_earns_its_place.py traces every asked question to an
* analysis. It found 28 items reaching nothing but an assert on themselves --
* interview time spent to check itself. Where the question was worth asking, the
* fix belongs here rather than in the form. Where it was not, the question was
* dropped instead (see the note in dictionary.py, Module G).
*=============================================================================

* ---- debt burden. This is half of gap N4, and it turned out the data was already there: the loan
* amount, the interest rate, whether an asset was pledged, and what. None of it entered anything.
gen double debt_service_ratio = .
replace  debt_service_ratio = (loan_amount*loan_interest_per100_pm/100)/(total_annual_income/12) ///
    if took_loan_12m==1 & pays_interest==1 & total_annual_income>0
label var debt_service_ratio "Monthly interest as a share of monthly income"
gen byte debt_secured_on_asset = (loan_against_asset==1) if took_loan_12m==1
label var debt_secured_on_asset "Loan is secured on a household asset"
* Pledging a productive asset is the case that turns a loan into a livelihood risk: the collateral is
* the thing the income comes from. Codes 3, 4 and 5 are animals, a vehicle and shop stock.
gen byte debt_on_productive_asset = inlist(loan_collateral,3,4,5) if loan_against_asset==1
label var debt_on_productive_asset "Loan secured on the asset the livelihood depends on"
gen double debt_stock_months = loan_amount/(total_annual_income/12) if took_loan_12m==1 & total_annual_income>0
label var debt_stock_months "Outstanding loan, in months of household income"

* ---- health. Five items were collected and none reached an estimate, although morbidity and
* hospitalisation are the health shock that VER is about and Lyons carries healthcare access as an
* indicator of its own.
gen byte health_shock_any = (morbidity_15d==1 | hospitalization_365d==1)
label var health_shock_any "Illness in the last 15 days or a hospital admission in 12 months"
gen double health_cost_share = morbidity_cost_15d/(total_annual_income/12) if morbidity_15d==1 & total_annual_income>0
label var health_cost_share "Out-of-pocket cost of recent illness, share of monthly income"
* Coping with a health cost by borrowing or by selling something is distress financing -- the standard
* marker that a health event has done lasting damage rather than been absorbed.
gen byte health_distress_financing = inlist(morbidity_coping_15d,3,4) if morbidity_15d==1
label var health_distress_financing "Met the health cost by borrowing or selling an asset"
gen byte dep_health_access = (health_access_barrier_3m==1)
label var dep_health_access "Someone could not get health care when needed (Lyons D1)"

* ---- income composition. The monthly calendar asks for earnings from ALL work, so this does not go
* into the aggregate -- it would double-count. What it gives, and nothing else does, is the split
* between the main work and the rest, which is the multiple-jobholding gap Apablaza names and her own
* instrument does not fill.
gen double secondary_income_share = .
replace  secondary_income_share = (other_activity_income_pm*12)/total_annual_income ///
    if n_other_activities>0 & total_annual_income>0
replace  secondary_income_share = 0 if n_other_activities==0
label var secondary_income_share "Share of annual income from work other than the main occupation"

* ---- remaining adaptive-capacity and stratifier variables that fed nothing
gen byte has_cultivable_land = (land_cultivable_acres>0) if !missing(land_cultivable_acres)
label var has_cultivable_land "Household owns or cultivates any land"
gen byte insured_any = (n_health_insured>0 | n_life_insured>0 | has_crop_insurance==1)
label var insured_any "Household holds any insurance at all"
* Lyons D5 carries access to phones and digital services as a social-inclusion indicator.
gen byte dep_digital_excluded = (smartphone_owned==0 & uses_digital_payment==0)
label var dep_digital_excluded "Neither a smartphone nor any digital payment use (Lyons D5)"
* Remittance channel as cost and friction: codes 3 to 6 all require a trip, a fee, or a third party.
gen byte remit_costly_channel = inlist(remit_mode,3,4,5,6) if !missing(remit_mode)
label var remit_costly_channel "Sends money by a channel that costs a trip, a fee or a middleman"
* Which KIND of event the household found hardest, now that shock_worst names it.
gen byte worst_shock_covariate = inlist(shock_worst,3,5,6,7) if !missing(shock_worst)
label var worst_shock_covariate "The hardest shock was a covariate one, not idiosyncratic"

* ---- the last six, each collapsed to the one contrast that carries the information -------------
* 27 native-language categories cannot enter a regression on this sample. What matters is whether the
* respondent speaks a language of these hills: it proxies how long the family has been here and how
* easily he deals with employers, officials and pilgrims.
gen byte lang_local = inlist(native_language,1,2) if !missing(native_language)
label var lang_local "Native language is Garhwali or Kumaoni"
* Push against pull. Someone driven here by no work at home, land too small to live on, or a debt to
* repay is in a different position from someone drawn by better pay, at identical current earnings.
gen byte came_for_push = inlist(came_here_reason,1,4,5) if !missing(came_here_reason)
label var came_for_push "Came here pushed (no work, land too small, debt) rather than pulled"
* Placement by a contractor or agent, as distinct from a family or village referral. An agent-placed
* worker usually carries a fee or an advance, which is a debt relationship the wage alone does not show.
gen byte placed_by_agent = (migration_referral==3) if !missing(migration_referral)
label var placed_by_agent "Placed in this work by a contractor or agent"
gen byte home_outside_state = (home_state!=27) if !missing(home_state)
label var home_outside_state "Permanent home is outside Uttarakhand"
label var worked_other_places "Had gone elsewhere for work before coming here"
label var first_job_ever "This work is the first paid job the respondent ever had"

*=============================================================================
* REGRESSION-SAFE FORMS OF THE GATED VARIABLES.
* A skip-gated variable put into a regression raw deletes every row the gate
* excluded, and the deletions INTERSECT. Adding four of them to the covariate
* set -- years_coming_here missing for 44%, came_for_push for 73%,
* debt_stock_months for 70%, health_cost_share for 91% -- cut the FGLS
* estimation sample from 104 observations to 4. Stata does not error on that.
* It reports it, in a line nothing was reading.
* So each gated covariate gets a form defined for EVERY row: the quantity where
* it applies, a neutral zero where it does not, and the incidence dummy kept
* alongside so the zero is never confused with a measured zero.
*=============================================================================
gen double years_coming_here_r = cond(resp_returns_at_closure==1, years_coming_here, 0)
label var years_coming_here_r "Years coming here for the season (0 if he never leaves)"
gen byte came_for_push_r = cond(migrant==1, came_for_push, 0)
label var came_for_push_r "Came here pushed rather than pulled (0 for local workers)"
gen double debt_stock_months_r = cond(took_loan_12m==1 & !missing(debt_stock_months), debt_stock_months, 0)
label var debt_stock_months_r "Outstanding loan in months of income (0 if no loan)"
gen double health_cost_share_r = cond(morbidity_15d==1 & !missing(health_cost_share), health_cost_share, 0)
label var health_cost_share_r "Out-of-pocket health cost, share of monthly income (0 if no illness)"
gen double debt_service_ratio_r = cond(!missing(debt_service_ratio), debt_service_ratio, 0)
label var debt_service_ratio_r "Monthly interest as a share of income (0 if no interest-bearing loan)"

* Anything still carrying missings must not reach $X. Checked here rather than
* discovered in a regression line: this is the guard the n=4 collapse needed.
foreach v in years_coming_here_r came_for_push_r debt_stock_months_r health_cost_share_r ///
             debt_service_ratio_r secondary_income_share has_cultivable_land insured_any ///
             lang_local placed_by_agent home_outside_state worked_other_places first_job_ever ///
             dep_func_limit health_shock_any {
    quietly count if missing(`v')
    if r(N) > 0 {
        di as error "  COVARIATE NOT REGRESSION-SAFE: `v' is missing for " r(N) " row(s)"
    }
}
gen double cons_pc_pm_narrow = cons_pc_seasonal_pm
gen double cons_pc_ae_pm = (cons_pc_seasonal_pm*hhsize + cons_annual_pm) ///
                           / (hhsize - n_children_u15 + 0.5*n_children_u15)
* Sensitivity, and what n_here_season is actually for: the respondent's OWN per-capita consumption
* while on site, ignoring the home side entirely. It is the individual-welfare reading of the same
* data, and reporting the pair is how the split-household assumption gets shown rather than asserted.
gen double cons_pc_onsite_pm = _cons_seas_yatra/cons_pc_denom_season
drop _cons_seas_yatra _cons_seas_off _seas_num
label var cons_pc_denom_season "People the Yatra-season consumption figures cover"
label var cons_pc_seasonal_pm  "Per-capita monthly consumption, seasonal items, season-weighted"
label var cons_pc_onsite_pm    "Respondent's own per-capita consumption while on site (sensitivity)"
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
* Code 9 means nothing happened. It is an answer, not a shock, so it is stripped before the shock
* dummies are built -- otherwise shock_count would read 1 for a household that reported no shock.
gen str _sh = " " + trim(subinstr(distress_event_last365d, "9", "", .)) + " "
gen byte no_shock_reported = strpos(" " + trim(distress_event_last365d) + " ", " 9 ") > 0
label var no_shock_reported "Explicitly reported that nothing of this kind happened"
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
* ACCESS TO EMPLOYMENT. Apablaza's Table 3 threshold is unemployment, or under 20 hours a week while
* wanting more. The hours limb is structurally inert in this setting and the data says so: ZERO of 200
* respondents work under 20 hours a week in season, because this workforce works 60-hour weeks for a
* few months and then stops. Part-time underemployment is not how scarcity of work shows up here;
* MONTHS without work is. Keeping only her limbs would report an access deprivation of 4% for a
* workforce that is idle half the year.
* So both are computed. emp_dep_access_apablaza is her threshold exactly, kept for comparability, and
* emp_dep_access adds the seasonal limb -- wanting more work and idle for a quarter of the year --
* which is the same construct measured the way this labour market expresses it. The departure is
* reported, and the pair should be shown side by side in the paper.
gen byte emp_dep_access_apablaza = (months_no_work>6 & months_looked_for_work>0) ///
    | (wants_more_work==1 & hours_week_yatra<20)
label var emp_dep_access_apablaza "Access deprivation, Apablaza Table 3 threshold exactly"
gen byte emp_dep_access = emp_dep_access_apablaza | (wants_more_work==1 & months_no_work>=3)
* Underemployment GAP, from Apablaza Q22. more_hours_day was asked and unused, so the size of the
* shortfall was invisible: someone wanting one more hour and someone wanting six read identically.
gen double hours_wanted_gap = more_hours_day*days_week_yatra if wants_more_work==1
replace  hours_wanted_gap = 0 if wants_more_work!=1
label var hours_wanted_gap "Extra hours per week the respondent wants"
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
* Apablaza's working-conditions domain is injury PLUS access to labour rights, and she names three
* rights: work health insurance, a pension contribution, and PAID LEAVE. leave_rights was collected
* from the start and never entered the indicator, so a worker with insurance but no leave at all read
* as non-deprived. Deprived now on injury, or on having none of the three.
gen byte emp_dep_cond   = (workplace_injury_12m==1) ///
    | (work_health_ins==3 & pension_contrib==3 & leave_rights!=1)
egen byte emp_dep_count = rowtotal(emp_dep_access emp_dep_comp emp_dep_sec emp_dep_stab emp_dep_cond)
gen double emp_dep_score = emp_dep_count/5
quietly summarize hours_week_yatra
di as result "  access domain: hours_week_yatra ranges " r(min) "-" r(max) "; Apablaza's <20h limb fires for " ///
    cond(r(min)<20, "some", "NO") " respondents"
quietly summarize emp_dep_access_apablaza
local a = 100*r(mean)
quietly summarize emp_dep_access
di as result "  access deprivation: Apablaza threshold " %4.1f `a' "%, with the seasonal limb " %4.1f (100*r(mean)) "%"
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
foreach v in workplace_registered pension_contrib work_health_ins injured_ever workplace_injury_12m {
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
assert prev_occ=="" if prev_occ_change!=1                 // one-directional: see above
assert inrange(toilet_type,1,4)
assert inrange(wall_material,1,3)
assert (anc_4_visits==.)            == (birth_last_5y==0)
assert (skilled_birth_attendant==.) == (birth_last_5y==0)
assert inrange(mpi_score,0,1)
assert (credit_source==.)            == (took_loan_12m==0)
assert (loan_amount==.)              == (took_loan_12m==0)
assert (loan_against_asset==.)       == (took_loan_12m==0)
assert (has_crop_insurance==.)       == (land_cultivable_acres==0)

assert inrange(drinking_water,1,9)
assert inlist(cooking_fuel,1,2,3,4,5,6,7,8,9,10)
assert missing(water_fetch_minutes) == (water_on_premises==1)
assert missing(hours_day_offseason) == (offseason_months_worked==0)
assert missing(days_week_offseason) == (offseason_months_worked==0)
assert (occupation_detail!="")  // verbatim job description, asked of everyone
assert native_language_other=="" if !inlist(native_language,96,97)   // one-directional
assert missing(prev_occ_reason)   == (prev_occ_change!=1)
assert !missing(n_other_activities)          // count, asked of everyone (0 = none)
assert (other_activity_types=="") == (n_other_activities==0)
assert missing(other_activity_income_pm) == (n_other_activities==0)
* The shock follow-ups are gated on a REAL shock, so they are missing both when the list is empty
* and when it holds only code 9.
gen byte _has_real_shock = !(distress_event_last365d=="" | no_shock_reported==1)
assert (shock_coping=="") == !_has_real_shock
assert missing(morbidity_coping_15d) == (morbidity_15d==0)
assert missing(morbidity_cost_15d)   == (morbidity_15d==0)
* migration_referral and worked_other_places are ungated now -- asked of everyone, including local
* respondents, because who placed you in a job is not a question about migration.
assert inlist(site,1,2)
assert inrange(accom_type_here,1,8)
assert inrange(func_limitation,1,4)
assert missing(ration_portable_here) == !strpos(" " + govt_schemes + " ", " 1 ")
assert missing(shock_worst) == !_has_real_shock
assert missing(shock_loss_amount) == !_has_real_shock
assert missing(shock_month) == !_has_real_shock
* the worst shock must be one of the shocks actually reported, not any code from the list
assert strpos(" " + distress_event_last365d + " ", " " + string(shock_worst) + " ") if !missing(shock_worst)
* Code 9 is exclusive. Ticked with a real shock it is a contradiction the form permits, so it is a
* data-quality flag rather than an assert.
gen byte dq_shock_none_and_some = (no_shock_reported==1 & shock_count>0)
label var dq_shock_none_and_some "Ticked 'nothing happened' alongside a real shock"
assert !missing(migration_referral)
assert !missing(worked_other_places)
assert !missing(resp_returns_at_closure)
assert !missing(hh_at_home_place)
assert missing(n_here_season) == (hh_at_home_place!=1)
assert !missing(worked_away_in_closure)
assert missing(years_coming_here) == (resp_returns_at_closure!=1)
assert missing(left_here_month)     == (resp_returns_at_closure!=1)
assert missing(returned_here_month) == (resp_returns_at_closure!=1)
assert missing(months_away_for_work) == (worked_away_in_closure!=1)
assert inrange(left_here_month,1,12)     if resp_returns_at_closure==1
assert inrange(returned_here_month,1,12) if resp_returns_at_closure==1
assert missing(came_here_reason)  == (migrant!=1)
* ONE-DIRECTIONAL, and this matters. These three are verbatim "other, specify" fields marked
* "may be left blank" in the dictionary and therefore NOT required on the form. A respondent can
* open the gate and still decline to name the place, so "gate open implies text present" is a rule
* the form does not enforce -- asserting it would halt the build on data Kobo accepts. What IS
* enforceable is the other direction: the field cannot hold text when its gate is shut.
assert closure_work_detail=="" if worked_away_in_closure!=1
assert other_places_detail==""  if worked_other_places!=1
assert govt_scheme_other==""    if !strpos(" " + govt_schemes + " ", " 9 ")
* The absence spell replaced loc_m1..loc_m12 on 2026-09-30, and with it went the assert tying a
* Yatra-work month to being on the route -- which was unenforced by the form and substantively wrong
* anyway: a Guptkashi or Sonprayag worker commuting up the route daily does Yatra work while living at
* the home place, and that is a true answer. Nothing replaces it, deliberately. The one cross-field
* rule left here is that an absence cannot be shorter than the work done inside it, and that is a
* data-quality FLAG, not an assert, because the form does not enforce it either.
assert missing(years_schooling)   == (knows_years_schooling==0)
assert missing(education_level_cat) == (knows_years_schooling==1)
assert hoh_female==female if hoh_relation==1   // self-headed: head's sex is the respondent's own
assert !missing(hoh_female)                    // derived for every row, never asked
assert main_income_earner==1 if n_earners==1   // automatic fill: sole earner is the main earner
assert missing(n_children_out_school) == (n_children_6_14==0)
foreach v in drove_twowheeler drove_car drove_heavy {
    assert missing(`v') == !inlist(tk_drive,1,2)
}
*=============================================================================
* DATA-QUALITY REPORT (was a block of asserts).
* These are cross-variable plausibility conditions, not invariants the form
* guarantees. Asserting them HALTED the build on data the form accepts --
* useless in fieldwork, where you need the build to finish and tell you which
* records to query. The form now enforces what it can at entry (see the
* CONSTRAINT block in build_xlsform.py); whatever still gets through is
* counted here and reported, not fatal.
*=============================================================================
gen byte _dq_flag = 0
local dq_total = 0
quietly count if yatra_months<3 | yatra_months>9
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- Yatra season outside the expected 3-9 months"
    quietly replace _dq_flag = 1 if yatra_months<3 | yatra_months>9
    local dq_total = `dq_total' + r(N)
}
quietly count if yatra_end_month - yatra_start_month + 1 != yatra_months
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- Yatra months not a single unbroken block"
    quietly replace _dq_flag = 1 if yatra_end_month - yatra_start_month + 1 != yatra_months
    local dq_total = `dq_total' + r(N)
}
quietly count if n_children_out_school > n_children_6_14 & !missing(n_children_out_school)
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- more out-of-school children than children aged 6-14"
    quietly replace _dq_flag = 1 if n_children_out_school > n_children_6_14 & !missing(n_children_out_school)
    local dq_total = `dq_total' + r(N)
}
quietly count if n_children_6_14 > n_children_u15 | n_children_u15 > hhsize-1
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- child counts exceed their parent count"
    quietly replace _dq_flag = 1 if n_children_6_14 > n_children_u15 | n_children_u15 > hhsize-1
    local dq_total = `dq_total' + r(N)
}
quietly count if n_earners < 1 | n_earners > hhsize
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- earners outside 1..household size"
    quietly replace _dq_flag = 1 if n_earners < 1 | n_earners > hhsize
    local dq_total = `dq_total' + r(N)
}
quietly count if n_health_insured > hhsize
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- more health-insured members than household members"
    quietly replace _dq_flag = 1 if n_health_insured > hhsize
    local dq_total = `dq_total' + r(N)
}
quietly count if n_life_insured > hhsize
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- more life-insured members than household members"
    quietly replace _dq_flag = 1 if n_life_insured > hhsize
    local dq_total = `dq_total' + r(N)
}
quietly count if n_can_transact_online > hhsize
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- more digitally-capable members than household members"
    quietly replace _dq_flag = 1 if n_can_transact_online > hhsize
    local dq_total = `dq_total' + r(N)
}
quietly count if family_structure==3 & hhsize!=1
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- single-member family structure but household size is not 1"
    quietly replace _dq_flag = 1 if family_structure==3 & hhsize!=1
    local dq_total = `dq_total' + r(N)
}
quietly count if (family_structure==3) != (hhsize==1)
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- family structure and household size disagree"
    quietly replace _dq_flag = 1 if (family_structure==3) != (hhsize==1)
    local dq_total = `dq_total' + r(N)
}
* The stated off-season migration item against the calendar's location row. Two reports of the same
* fact, asked minutes apart; a real respondent can and will disagree with himself. Counted, never
* asserted -- an assert here would halt the build on data the form is perfectly happy to emit.
quietly count if dq_shock_none_and_some==1
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- ticked 'nothing happened' alongside a real shock"
    quietly replace _dq_flag = 1 if dq_shock_none_and_some==1
    local dq_total = `dq_total' + r(N)
}
quietly count if dq_away_exceeds_spell==1
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- months worked away exceed the reported absence from the route"
    quietly replace _dq_flag = 1 if dq_away_exceeds_spell==1
    local dq_total = `dq_total' + r(N)
}
quietly count if split_household==1 & n_here_season >= hhsize & hhsize > 1
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- household reported as split, but the on-site count equals household size"
    quietly replace _dq_flag = 1 if split_household==1 & n_here_season >= hhsize & hhsize > 1
    local dq_total = `dq_total' + r(N)
}
* Someone who says they go home at closure but whose reported absence is entirely spent working
* elsewhere -- possible, but it means "home place" never actually featured, which is worth querying.
quietly count if resp_returns_at_closure==1 & months_home_base==0
if r(N) > 0 {
    di as error "  DATA QUALITY: " r(N) " record(s) -- goes home at closure, but the whole absence was spent working elsewhere"
    quietly replace _dq_flag = 1 if resp_returns_at_closure==1 & months_home_base==0
    local dq_total = `dq_total' + r(N)
}
di as result "  data-quality flags raised: `dq_total'"
* Assumption check on the whole two-season design. Every consumption, remittance and coping item in
* this instrument is asked twice on the premise that the respondent is somewhere else once the Yatra
* shuts. Until the location row existed, nothing measured how often that premise holds.
quietly tabulate site, matcell(_sitec)
di as result "  route split: Kedarnath " _sitec[1,1] ", Hemkund " _sitec[2,1]
quietly summarize dep_accom_here
di as result "  sleeping at the workplace, in a tent or in the open: " %4.1f (100*r(mean)) "%"
quietly summarize dep_ration_portability
di as result "  cannot draw the ration entitlement here: " %4.1f (100*r(mean)) "%"
quietly summarize shock_loss_share if !missing(shock_loss_share)
di as result "  worst shock, mean loss as a share of annual consumption: " %5.3f r(mean)
quietly count if stays_all_year==1
di as result "  two-season design: " r(N) " of " _N " respondents never move at closure (their two seasonal answers describe the same place)"
quietly count if closure_labour_migrant==1
di as result "  off-season labour migration (type B): " r(N) " of " _N " respondents"
label variable _dq_flag "Flagged by at least one data-quality check"
rename _dq_flag dq_flag

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
    * ONE-directional on purpose. An idle month must report zero -- the form hides the question and
    * the build fills it. The converse is NOT true: a worker can genuinely earn nothing in a month
    * they worked (an unpaid stretch, a washed-out week), and asserting the biconditional would have
    * failed on the first real respondent who reported it.
    assert income_m`m'==0 if status_m`m'==8 & income_from_fallback==0
}

assert yatra_months + offseason_months_worked + months_no_work == 12
* logic

assert inrange(hours_day_yatra,1,18) & inrange(days_week_yatra,1,7)
assert inrange(n_other_activities,0,6)
assert inlist(job_permanence,1,2,3,4,5) if k_working==1
foreach v in cope_less_pref_food cope_borrow_food cope_reduce_meals cope_reduce_portion cope_restrict_adult {
    assert inrange(`v'_yatra_wk,0,7) & inrange(`v'_offseason_wk,0,7)
}

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
