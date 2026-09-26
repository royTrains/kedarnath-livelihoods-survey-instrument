*=============================================================================
* VASyR worked example -- built ENTIRELY IN STATA from the original UNHCR
* 2025 VASyR (Lebanon) microdata CSVs, no Python step. Replicates the method
* of Lyons, Kass-Hanna & Montoya Castano (2023, J. Int. Dev. 35:2014-2045):
* a 5-dimension, 21-indicator Alkire-Foster multidimensional livelihood index
* (MLI) from VASyR, fed into Chaudhuri et al. (2002)'s 3-stage FGLS to get
* vulnerability to future poverty. Their paper uses the 2018 VASyR wave; the
* files here are the 2025 wave, so several indicators are DOCUMENTED PROXIES
* where the 2025 questionnaire doesn't carry the exact 2018 item -- flagged
* at each block below and in this folder's README.
*
* Inputs (unpacked, original UNHCR files, untouched):
*   vasyr/UNHCR_LBN_2025_VASYR_data_main_v2.1.csv    (3,546 households, 975 cols)
*   vasyr/UNHCR_LBN_2025_VASYR_data_member_v2.1.csv  (16,006 rows, individual roster)
*=============================================================================
clear all
set more off
cd "D:\OneDrive\Desktop\vulnerability-2-poverty"   // <-- change to your working folder

*=============================================================================
* PART 1 -- MEMBER FILE: individual roster -> household-level aggregates.
* age is a BAND (00-04/05-11/12-17/18-24/25-49/50-59/60+), not a single year,
* so all age cutoffs below are proxies: working-age (Lyons: 15-64) -> 18-59;
* "adult" (Lyons: 10+) -> 18+; "child 6-14" -> the 05-11/12-17 bands.
*=============================================================================
import delimited "vasyr\UNHCR_LBN_2025_VASYR_data_member_v2.1.csv", varnames(1) case(preserve) clear

gen byte wg        = inlist(age, "18 - 24", "25 - 49", "50 - 59")            // working-age proxy
gen byte adultband  = inlist(age, "18 - 24", "25 - 49", "50 - 59", "60+")    // adult proxy
gen byte childband  = inlist(age, "05 - 11", "12 - 17")                     // child 6-14 proxy
gen byte is_head    = rel_to_hoh_s == "a. Head of Household"

gen double age_mid = .
replace age_mid = 2    if age=="00 - 04"
replace age_mid = 8    if age=="05 - 11"
replace age_mid = 14.5 if age=="12 - 17"
replace age_mid = 21   if age=="18 - 24"
replace age_mid = 37   if age=="25 - 49"
replace age_mid = 54.5 if age=="50 - 59"
replace age_mid = 65   if age=="60+"

* household head covariates (missing for every row of a household with no head row)
gen double age_head_i    = age_mid if is_head
gen byte   female_head_i = (gender_s=="b. Female") if is_head
gen byte   married_head_i= (marital_status_s=="b. Married") if is_head

* indicator 1 (Health & food security dim.): special needs = chronic illness OR a
* Washington-Group disability domain at "a lot of difficulty"/"cannot do at all"
* for ANY member (5 of 6 WG domains on file: seeing/hearing/walking/remembering/
* self-care; "communicating" is not asked in this wave)
gen byte wg_dep = 0
foreach v in dis_dif_seeing_s dis_dif_hearing_s dis_dif_walking_s dis_dif_remembering_s dis_dif_self_care_s {
    replace wg_dep = 1 if inlist(`v', "c.A lot of difficulty", "d.Cannot do at all")
}
gen byte special_i = (chronic_illness_yn=="a. Yes") | wg_dep==1

* indicator 5 (Education dim.): any child (6-14 proxy) not attending school this year
gen byte child_noschool_i = childband==1 & attend_school_current_yr_yn=="b. No"

* indicator 6 (Education dim.): PROXY. No grade-to-years crosswalk on file, so this
* uses "ALL adults (18+ proxy) never attended school" in place of Lyons' "all
* members 10+ have under 6 years of schooling" -- coarser, likely understates
* deprivation next to the real Table 2 cutoff
gen byte adult_never_i  = adultband==1 & attended_school_ever_yn=="b. No"
gen byte adult_attend_i = adultband==1 & attended_school_ever_yn=="a. Yes"

* indicator 9 (Employment dim.): share of working-age (18-59 proxy) members not
* working for pay >= 50%; households with no working-age member asked this
* question are coded not-deprived, not missing
gen byte wg_asked_i   = wg==1 & work_for_pay_yn!=""
gen byte wg_notwork_i = wg_asked_i==1 & work_for_pay_yn=="b. No"

* indicator 10 (Employment dim.): PROXY. No "days worked last month" item on file;
* uses job_opp_avail_yn ("are job opportunities available?", asked of working-age
* members without a full paid job) as a labour-market-slack proxy for underemployment
gen byte jo_asked_i = wg==1 & job_opp_avail_yn!=""
gen byte jo_no_i    = jo_asked_i==1 & job_opp_avail_yn=="b. No"

* indicator 16 (Security & social inclusion dim.): no adult (18+ proxy) holds legal
* residency -- direct match to Lyons' "no household members >=15 are legal residents"
gen byte adult_legal_i = adultband==1 & legal_res_yn=="a. Yes"

bysort id: gen int hhsize_mem = _N
egen int n_wg = total(wg), by(id)

* collapse the individual flags to one row per household
collapse (max) age_head_i female_head_i married_head_i special_i child_noschool_i ///
    (sum) n_adult_never=adult_never_i n_adult_attend=adult_attend_i ///
          n_wg_asked=wg_asked_i n_wg_notwork=wg_notwork_i ///
          n_jo_asked=jo_asked_i n_jo_no=jo_no_i n_adult_legal=adult_legal_i ///
    (mean) hhsize_mem n_wg, ///
    by(id)

rename age_head_i age_head
rename female_head_i female_head
rename married_head_i married_head
rename special_i special_needs
rename child_noschool_i child_school

gen byte adult_schooling = (n_adult_never>0 & n_adult_attend==0)
gen byte unemployment    = (n_wg_asked>0)  & (n_wg_notwork/n_wg_asked >= 0.5)
gen byte underemployment = (n_jo_asked>0)  & (n_jo_no/n_jo_asked >= 0.5)
gen byte legal_residency = (n_adult_legal==0)
gen double dependent_share = 1 - n_wg/hhsize_mem

keep id hhsize_mem age_head female_head married_head dependent_share ///
    special_needs child_school adult_schooling unemployment underemployment legal_residency
tempfile member_agg
save `member_agg'

*=============================================================================
* PART 2 -- MAIN (household) FILE. Two column names exceed Stata's 32-character
* limit and get silently truncated/renamed on import, so they are captured by
* their exact CSV column position (verified against the raw header) rather
* than typed out -- the only way to reference them safely.
*=============================================================================
import delimited "vasyr\UNHCR_LBN_2025_VASYR_data_main_v2.1.csv", varnames(1) case(preserve) clear
* the raw CSV has a handful of stray, unmatched quote characters in free-text write-in
* answers (Stata flags rows 572/574/2586/2590 on import); its default quote-binding
* merges a few of those rows together, leaving 5 of 3,549 imported rows with a blank
* id. Dropping them (not re-parsing with bindquote(nobind), which misaligns far more
* rows elsewhere in the file) is the smallest fix -- 5 of 3,549 households, 0.14%.
quietly drop if missing(id)
unab allv : _all
local v_burn : word 384 of `allv'          // energy_src_cooking_m_burning_trash
local v_hcbar : word 440 of `allv'         // ..._phc_m_..._opt_1 ("no barrier" to primary health care)
rename `v_burn' energy_burn_trash
rename `v_hcbar' hc_no_barrier

destring total_income_usd_dec living_space_dec num_ppl_sharing_space_i total_num_hh_i ///
    num_hh_using_facility_i less_expensive_i borrowed_food_i reduced_meals_i reduced_portion_i ///
    restrict_consumption_i num_days_cereal_cons_i num_days_tubers_cons_i num_days_veg_i ///
    num_days_fruits_i num_days_flesh_meat_i num_days_organ_meat_i num_days_fish_i num_days_egg_i ///
    num_days_legumes_i num_days_milk_i num_days_oil_i num_days_sugar_i num_days_condiments_i ///
    assets_owned_mattresses assets_owned_blankets assets_owned_winter_clothing ///
    assets_owned_small_gas_stove assets_owned_refrigerator assets_owned_heater ///
    energy_src_cooking_m_wood energy_src_cooking_m_charcoal energy_burn_trash hc_no_barrier, ///
    replace force

* indicator 2 (Health & food security dim.): did NOT report "no barrier" to primary
* health care access in the last 3 months (missing = not applicable -> not deprived)
gen byte healthcare_access = hc_no_barrier==0

* indicator 3: reduced Coping Strategy Index (rCSI), standard WFP weights 1/2/1/1/3;
* deprived if >20, matching Lyons et al.'s cutoff
foreach v in less_expensive_i borrowed_food_i reduced_meals_i reduced_portion_i restrict_consumption_i {
    replace `v' = 0 if missing(`v')
}
gen double rcsi = less_expensive_i + 2*borrowed_food_i + reduced_meals_i + reduced_portion_i + 3*restrict_consumption_i
gen byte food_coping = rcsi>20

* indicator 4: dietary diversity, 13 food groups eaten (>0 days) over the last 7
* days; deprived if fewer than 9, matching Lyons et al.'s <9 cutoff
gen int diet_groups = 0
foreach v in num_days_cereal_cons_i num_days_tubers_cons_i num_days_veg_i num_days_fruits_i ///
    num_days_flesh_meat_i num_days_organ_meat_i num_days_fish_i num_days_egg_i ///
    num_days_legumes_i num_days_milk_i num_days_oil_i num_days_sugar_i num_days_condiments_i {
    replace diet_groups = diet_groups + 1 if `v'>0 & !missing(`v')
}
gen byte diet_diversity = diet_groups<9

* indicators 7-14 (Living standards dim.)
gen byte electricity = electricity_access_yn=="b. No"
* unimproved sanitation/water facility types: matched on the stable leading letter
* code, since punctuation/encoding varies category to category in the raw file
gen byte sanitation = regexm(trim(type_of_toilet_s), "^[deijk]\.")
replace  sanitation = 1 if num_hh_using_facility_i>1 & !missing(num_hh_using_facility_i)
gen byte drinking_water = regexm(trim(drink_water_m_src_s), "^[iqmr]\.")
gen byte cooking_fuel = energy_src_cooking_m_wood==1 | energy_src_cooking_m_charcoal==1 | energy_burn_trash==1
egen byte assets6 = rowtotal(assets_owned_mattresses assets_owned_blankets assets_owned_winter_clothing ///
    assets_owned_small_gas_stove assets_owned_refrigerator assets_owned_heater)
gen byte basic_assets = assets6<6
gen double crowd_denom = num_ppl_sharing_space_i
replace crowd_denom = total_num_hh_i if missing(crowd_denom)
gen byte crowding = (living_space_dec/crowd_denom) < 4.5 if !missing(living_space_dec, crowd_denom)
gen byte shelter_conditions = type_of_housing_s != "c. Apartment/house/room"
gen byte housing_stability = changed_accom_yn=="a. Yes"

* indicators 17-21 (Security & social inclusion dim.)
* 17: PROXY -- reported shelter/infrastructure damage as evidence of poor site
* conditions (Lyons' own definition already folds in "poor sanitation conditions"
* and "low standard living conditions")
gen byte area_settlement = damaged_shelter_yn=="a. Yes" | san_pipes_not_func_yn=="a. Yes" | latrine_not_usable=="a. Yes"
gen byte communications = smart_phone_yn=="b. No" & (have_internet_wifi_yn=="b. No" | missing(have_internet_wifi_yn)) ///
    & (have_internet_phone_yn=="b. No" | missing(have_internet_phone_yn))
gen byte movement_mobility = curfew_imposed_yn=="a. Yes"          // exact match: curfew on the community
gen byte community_interaction = inlist(rel_refugees_s, "e. Never", "d. Rarely")   // exact match

* household resources (FGLS covariates, not MLI indicators)
gen byte inc_employment = inlist(main_income_src_s, "b. Agriculture","g. Construction", ///
        "r. Other services: hotel, restaurant, transport, personal services", ///
        "h. Craft Work (blacksmith, plumber, mechanic, etc.)","f. Concierge") ///
    | inlist(main_income_src_s, "m. Home based work / skill","s. Other types of sales", ///
        "n. Manufacturing","p. Office work (finance, admin, secretary)","aa Wholesale and retail trade")
gen byte inc_assistance = inlist(main_income_src_s, ///
        "c. ATM- cards used in ATM machines / BOB Finance from UN or humanitarian organizations", ///
        "k. E-cards used in WFP FOOD SHOPS")
gen byte inc_borrowing = inlist(main_income_src_s, ///
        "j. Credit/debts (informal)shops, friends hosts)","i. Credit/debts (formal banks)")
gen byte borrowed = borrow_money_credit_yn=="a. Yes"
encode district_s, gen(district_n)
* economic-status proxy: the ~40-item SMEB/MEB expenditure basket Lyons et al. use
* isn't reconstructed here; 30-day household income is split into quartiles instead
xtile income_q = total_income_usd_dec, nq(4)
gen byte inc_q1 = income_q==1 if !missing(income_q)
gen byte inc_q2 = income_q==2 if !missing(income_q)
gen byte inc_q3 = income_q==3 if !missing(income_q)

merge 1:1 id using `member_agg'
keep if _merge==3
drop _merge
gen double hhsize = total_num_hh_i
replace hhsize = hhsize_mem if missing(hhsize)
drop if missing(age_head)          // households with no identifiable head row

*=============================================================================
* PART 3 -- MLI (Alkire-Foster, Table 2 dimension weights) and 3-stage FGLS
* (Chaudhuri et al. 2002 / Lyons et al. Section 5.2).
*=============================================================================
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
gen byte vulnerable = Vh >= 0.5 if !missing(Vh)   // Chaudhuri et al. (2002) / Lyons et al. eq. (8) cutoff

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

save "replication\vasyr_example\vasyr_stata_only.dta", replace
di as result "Saved vasyr_stata_only.dta -- N = " _N
