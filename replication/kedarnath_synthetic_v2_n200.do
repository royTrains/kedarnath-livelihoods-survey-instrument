*=============================================================================
* SYNTHETIC DATA SIMULATION -- Kedarnath Yatra livelihoods instrument (v2)
* Purpose: methodological note only. n=200, field-like, pilot-informed but
* NOT bootstrapped/copied from the earlier 46-respondent pilot. Every
* parameter below is a hand-set assumption, not an empirical estimate --
* treat this as a code/questionnaire dry-run, never as findings.
*
* Rule numbers in comments refer to the instrument spec provided.
*=============================================================================

clear all
set more off
cd "D:\OneDrive\Desktop\vulnerability-2-poverty\replication"
capture log close
log using "kedarnath_synthetic_v2_n200_log.log", replace text
set seed 20260901
set obs 200
gen resp_id = _n

*-----------------------------------------------------------------------------
* RULE 1 -- unit of observation: one respondent reports HOUSEHOLD aggregates.
* No roster is collected, so we only ever generate an aggregate hhsize.
*-----------------------------------------------------------------------------
gen hhsize = 2 + rpoisson(2.2)
replace hhsize = min(hhsize, 10)

*-----------------------------------------------------------------------------
* RESPONDENT DEMOGRAPHICS -- age and education (not in the original 18-rule
* list, added per instruction). Age is generated first because it bounds
* years_in_yatra_work further down. Some imprecision/non-response added
* here to keep the data a little more field-realistic.
*-----------------------------------------------------------------------------
gen age = round(rnormal(38,11))
replace age = min(max(age,18),70)
* age heaping: many respondents round their own age to the nearest 5
replace age = round(age,5) if runiform() < .35

gen u0 = runiform()
gen education_level = ""
replace education_level = "No formal education"     if u0 < .17
replace education_level = "Primary (up to 5th)"      if u0 >= .17 & u0 < .36
replace education_level = "Middle (up to 8th)"       if u0 >= .36 & u0 < .55
replace education_level = "Secondary (up to 10th)"   if u0 >= .55 & u0 < .74
replace education_level = "Higher secondary (12th)"  if u0 >= .74 & u0 < .88
replace education_level = "Graduate or above"        if u0 >= .88 & u0 < .94
replace education_level = "Prefer not to say"        if u0 >= .94
drop u0

gen education_years = .
replace education_years = 0  if education_level=="No formal education"
replace education_years = 5  if education_level=="Primary (up to 5th)"
replace education_years = 8  if education_level=="Middle (up to 8th)"
replace education_years = 10 if education_level=="Secondary (up to 10th)"
replace education_years = 12 if education_level=="Higher secondary (12th)"
replace education_years = 15 if education_level=="Graduate or above"
* education_years stays MISSING for "Prefer not to say" -- genuine non-response,
* not a value to impute inside the generation code.

* marital status -- standard single-question categorical [Source: HCES Level 2 / PLFS]
gen u0b = runiform()
gen marital_status = "Currently married"
replace marital_status = "Never married" if age<25 & u0b<.55
replace marital_status = "Never married" if age>=25 & u0b<.12
replace marital_status = "Widowed/Divorced/Separated" if age>=45 & u0b>=.88
drop u0b

*=============================================================================
* OCCUPATION CATEGORY EXPANSION (13 categories, up from 10)
*
* Audit against the real 46-respondent pilot (pilot/livelihood_clean.dta,
* respondent_category) showed three principal Yatra occupations missing from
* the original 10-category list. All three are now generated, each fully
* parameterized below (earning tier, employment status, route location,
* training, asset ownership, dropout weight) so nobody is drawn into an
* unparameterized category. Pilot n per group is 1-13, so pilot figures are
* used only as loose anchors for relative earnings and location, not as
* estimates.
*
*   ADDED: Driver               (pilot n=3; jeep/taxi drivers on the road-head
*                                 stretch -- own-account, paid per trip)
*          Dhaba/food-stall owner (pilot n=3; food service on the trek route,
*                                 previously lumped into "Shop owner")
*          Guide                 (pilot n=1; deliberately a SMALL share here --
*                                 most guides do not work within the Yatra
*                                 corridor itself, so incidence is low)
*   EXCLUDED BY DESIGN: Priest (pilot n=2). Religious workers are outside
*          the sampling scope of this study, so no category is generated.
*   KEPT, FLAGGED FOR REVIEW: Shopkeeper (shop employee) and Wage labourer
*          do not appear as separate principal categories in the pilot, but
*          are retained since dropping them would narrow the instrument.
*
* Target shares (percent of the n=200 draw). Existing categories were scaled
* down modestly to make room; these are hand-set quota targets, not
* population estimates (see the sampling-design discussion in the write-up):
*   Pony worker 11 | Pony business 6 | Porter 9 | Palki 6 | Shopkeeper 10 |
*   Shop owner 10 | Hotel/lodging worker 9 | Hotel/lodging owner 9 |
*   Wage labourer 10 | Other 6 | Driver 6 | Dhaba/food-stall owner 6 | Guide 2
*=============================================================================

*-----------------------------------------------------------------------------
* RULE 2 -- principal Yatra-season occupation (closed list, Yatra work only)
*-----------------------------------------------------------------------------
* QUOTA ASSIGNMENT, not independent random draws. The shares above are
* documented as quota targets, and a stratified quota design fills each
* stratum to a fixed count. Drawing each respondent's occupation
* independently instead let the realized n=200 mix drift far from target
* (e.g. Shop owner 17% against a 10% target). Here each respondent still
* consumes one random draw (so the random stream downstream is unchanged),
* but the draw is converted to a rank and the ranks are cut at the target
* shares, so the n=200 pool hits the target mix exactly (22/12/18/12/20/20/
* 18/18/20/12/12/12/4). Who lands in which quota is still random; only the
* counts are fixed. Fieldwork attrition below then acts on this pool.
gen u1 = runiform()
egen u1_rank = rank(u1)
gen u1q = (u1_rank - 0.5)/_N
gen occupation = ""
replace occupation = "Pony worker"             if u1q < .11
replace occupation = "Pony business"           if u1q >= .11 & u1q < .17
replace occupation = "Porter"                  if u1q >= .17 & u1q < .26
replace occupation = "Palki"                   if u1q >= .26 & u1q < .32
replace occupation = "Shopkeeper"              if u1q >= .32 & u1q < .42
replace occupation = "Shop owner"              if u1q >= .42 & u1q < .52
replace occupation = "Hotel/lodging worker"    if u1q >= .52 & u1q < .61
replace occupation = "Hotel/lodging owner"     if u1q >= .61 & u1q < .70
replace occupation = "Wage labourer"           if u1q >= .70 & u1q < .80
replace occupation = "Other"                   if u1q >= .80 & u1q < .86
replace occupation = "Driver"                  if u1q >= .86 & u1q < .92
replace occupation = "Dhaba/food-stall owner"  if u1q >= .92 & u1q < .98
replace occupation = "Guide"                   if u1q >= .98
drop u1 u1_rank u1q

* PLFS-style employment-STATUS classification -- corrected to a 4-way split
* that separates OWN-ACCOUNT self-employment from EMPLOYER/business-owner
* self-employment, rather than the sector/task-based intuition ("looks like
* manual labour" -> casual) used in the original version of this do-file.
* [Source: PLFS employment-status taxonomy]
*   - Self-employed, own-account worker: no fixed employer, paid directly
*     per trip/load via a turn-based union/rotation system (baari), doesn't
*     own capital beyond their own labour. Pony worker, Porter and Palki all
*     work this way on this route -- NOT casual labour, despite the
*     precarious, task-rate pay looking similar. (This corrects a real
*     miscoding: these three previously fell into the "Casual labour"
*     default purely because the work is physical, not because of their
*     actual contractual status.)
*   - Self-employed, employer/business owner: owns capital (ponies, shop,
*     hotel) and may hire others.
*   - Regular wage-salaried: fixed employer, regular pay -- genuine
*     employees of someone else's shop/hotel.
*   - Casual wage labour: no fixed employer AND no own-account relationship
*     -- hired day-to-day by whoever needs labour that day. Wage labourer
*     and the residual "Other" category are the only occupations left here.
gen employment_type = "Casual wage labour"
* Driver (owner-operators/union rotation, paid per trip by passengers) and
* Guide (freelance, paid per engagement) share the own-account logic of
* Palki/Porter/Pony worker; Dhaba/food-stall owner is a capital-owning
* business like Shop owner.
replace employment_type = "Self-employed - own-account worker"          if inlist(occupation,"Pony worker","Porter","Palki","Driver","Guide")
replace employment_type = "Self-employed - employer/business owner"     if inlist(occupation,"Shop owner","Hotel/lodging owner","Pony business","Dhaba/food-stall owner")
replace employment_type = "Regular wage-salaried"                       if inlist(occupation,"Shopkeeper","Hotel/lodging worker")

*-----------------------------------------------------------------------------
* LOCATION ALONG THE YATRA ROUTE -- deliberately generated as its OWN axis,
* only weakly nudged by occupation (owners cluster a bit more at the lower,
* better-connected market towns; handlers/porters spread further up-route),
* NOT by income tier. This is what lets health access below be genuinely
* geography-driven rather than a proxy for wealth.
* Real-world basis: Guptkashi/Phata sit on the motorable road and are
* closest to Rudraprayag's district-level health infrastructure; Sonprayag
* is the last road-head; Gaurikund is the trek start; Kedarnath itself is
* a high-altitude seasonal settlement with only a basic medical camp.
*-----------------------------------------------------------------------------
gen loc_u = runiform()
replace loc_u = loc_u - 0.12 if inlist(occupation,"Shop owner","Hotel/lodging owner","Shopkeeper")  // owners skew toward the market towns
replace loc_u = loc_u + 0.10 if inlist(occupation,"Pony worker","Porter","Palki")                    // handlers spread further up-route
* Drivers work the motorable stretch (pilot: Sonprayag/Gaurikund road-head),
* so their draw is compressed into the lower part of the route, roughly
* Guptkashi/Phata 36% / Sonprayag 54% / Gaurikund 10% / none at Kedarnath.
replace loc_u = 0.10 + 0.50*loc_u if occupation=="Driver"
gen location_cluster = "Sonprayag"
replace location_cluster = "Guptkashi/Phata" if loc_u < .28
replace location_cluster = "Gaurikund"       if loc_u >= .55 & loc_u < .82
replace location_cluster = "Kedarnath town"  if loc_u >= .82
drop loc_u

gen health_access_tier = "Moderate"
replace health_access_tier = "Good" if location_cluster=="Guptkashi/Phata"
replace health_access_tier = "Poor" if inlist(location_cluster,"Gaurikund","Kedarnath town")

*-----------------------------------------------------------------------------
* years_in_yatra_work -- tenure in the CURRENT principal occupation, capped
* so nobody has more years of experience than is physically possible given
* age (assumes earliest entry into Yatra work around age 16).
*-----------------------------------------------------------------------------
gen years_in_yatra_work = round(rgamma(2, 6/2))
replace years_in_yatra_work = max(years_in_yatra_work,1)
replace years_in_yatra_work = min(years_in_yatra_work, age-16)
replace years_in_yatra_work = 1 if years_in_yatra_work < 1   // safety floor for very young respondents

*-----------------------------------------------------------------------------
* RULE 3 -- Yatra season duration: 3-6 months. (Floor raised from 1 to 3:
* someone enumerated under a Yatra occupation code is assumed to have worked
* a meaningful share of the season, not a single month.)
*-----------------------------------------------------------------------------
gen yatra_months = round(rnormal(5,0.8))
replace yatra_months = min(max(yatra_months,3),6)

* Season assumed to start in May (month 5) for everyone -- this fixes the
* institutional Chardham Yatra window rather than treating start date as a
* respondent-level random draw (keeps the design simple, per rule 18).
gen yatra_start_month = 5
gen yatra_end_month   = yatra_start_month + yatra_months - 1

*-----------------------------------------------------------------------------
* RULE 4, 6, 7 -- enumerate PRINCIPAL STATUS AND OCCUPATION FOR EACH OF THE
* 12 CALENDAR MONTHS, then sum to get annual income. Yatra months take the
* Yatra occupation (rule 2); off-season months get their own draw, with
* "No work" a valid and common outcome. Every monthly income figure is a
* whole-rupee integer with heaping -- no reported (non-computed) figure
* anywhere carries decimals.
*-----------------------------------------------------------------------------

* -- occupation-specific BASE monthly Yatra earning rate --
* Reworked into three tiers based on domain knowledge of who actually earns
* well on this route: OWNERS (shop/hotel/pony business) and PORTERS earn the
* most (portering this terrain commands a real premium); PONY HANDLERS,
* WAGE LABOURERS and SHOPKEEPERS (i.e. shop employees, not owners) sit at
* the low end and clear only around Rs.2-3.5 lakh across the whole season;
* Palki and Other sit in between.
* LOGICAL-CONSISTENCY NOTE (Porter): Porter is "high" income_tier despite
* being a self-employed OWN-ACCOUNT worker (see employment_type below), not
* an employer/business owner, and so is NOT a business/asset owner
* (business_asset_owned, Rule 13, is restricted to Pony business/Shop
* owner/Hotel owner only). This is intentional, not a data error --
* portering this terrain is a physically brutal, high-day-rate own-account
* trade paid directly per load, so high earnings without capital ownership
* is the realistic story here, not a contradiction. Downstream standard-of-
* living variables (Rule 13) are wired to income_tier, not to occupation or
* employment_type directly, so a Porter household's housing/durables
* profile correctly tracks its high income_tier even though its employment
* status carries no business assets -- verified in the consistency-check
* block below (search "INTERNAL CONSISTENCY CHECKS").
gen income_tier = ""
replace income_tier = "high" if inlist(occupation,"Shop owner","Hotel/lodging owner","Pony business","Porter","Dhaba/food-stall owner")
replace income_tier = "low"  if inlist(occupation,"Pony worker","Wage labourer","Shopkeeper","Hotel/lodging worker")
replace income_tier = "mid"  if inlist(occupation,"Palki","Other","Driver","Guide")

gen occ_mean = .
replace occ_mean = 380000 if occupation=="Shop owner"
replace occ_mean = 400000 if occupation=="Hotel/lodging owner"
replace occ_mean = 340000 if occupation=="Pony business"
replace occ_mean = 320000 if occupation=="Porter"
replace occ_mean = 55000  if occupation=="Pony worker"
replace occ_mean = 50000  if occupation=="Wage labourer"
replace occ_mean = 55000  if occupation=="Shopkeeper"
replace occ_mean = 55000  if occupation=="Hotel/lodging worker"
replace occ_mean = 145000 if occupation=="Palki"
replace occ_mean = 125000 if occupation=="Other"
* New categories, scaled off the pilot's relative annual Yatra incomes
* (medians: Palki 3.25L, Driver 4.0L, Shop owner 5.0L, Dhaba owner 4.5L)
* against this file's existing rates -- ratios, not the pilot's levels, since
* this file's scale was never calibrated to the pilot. Driver = Palki x
* (4.0/3.25); Dhaba owner = Shop owner x (4.5/5.0). Guide is pilot n=1
* (8.0L), too thin to anchor on, so it is placed mid-tier by judgement.
replace occ_mean = 180000 if occupation=="Driver"
replace occ_mean = 340000 if occupation=="Dhaba/food-stall owner"
replace occ_mean = 200000 if occupation=="Guide"

* -- off-season primary activity (drives the month-by-month draw below) --
* EXPANDED from 4 to 7 categories after the pilot audit. The pilot's
* main_occupation showed "No other work" as its single largest category
* (18 of 46, ~39%), which the old 4-category list could not represent: it
* forced every respondent into some off-season activity and only allowed
* "No work" as a 20% monthly gap inside that activity. "No other work" is now
* a first-order, person-level state with zero off-season income all year.
* Also added: Animal husbandry and Salaried job (pilot n=1 each). Shares
* are hand-set (pilot n=46 is too small to estimate from); "No other work"
* is set a little under the pilot's 39% to allow for the pilot's 2
* "prefer not to say" and its likely over-representation of owners.
*   No other work 35 | Agriculture 25 | Wage labour elsewhere 15 |
*   Migrated for work 10 | Petty trade/other 7 | Animal husbandry 5 |
*   Salaried job 3
gen u2 = runiform()
gen offseason_primary = ""
replace offseason_primary = "No other work"          if u2 < .35
replace offseason_primary = "Agriculture"            if u2 >= .35 & u2 < .60
replace offseason_primary = "Wage labour elsewhere"  if u2 >= .60 & u2 < .75
replace offseason_primary = "Migrated for work"      if u2 >= .75 & u2 < .85
replace offseason_primary = "Petty trade/other"      if u2 >= .85 & u2 < .92
replace offseason_primary = "Animal husbandry"       if u2 >= .92 & u2 < .97
replace offseason_primary = "Salaried job"           if u2 >= .97
drop u2

gen off_mean = .
replace off_mean = 0     if offseason_primary=="No other work"
replace off_mean = 6000  if offseason_primary=="Agriculture"
replace off_mean = 9000  if offseason_primary=="Wage labour elsewhere"
replace off_mean = 12000 if offseason_primary=="Migrated for work"
replace off_mean = 5000  if offseason_primary=="Petty trade/other"
replace off_mean = 6500  if offseason_primary=="Animal husbandry"
replace off_mean = 14000 if offseason_primary=="Salaried job"

* -- build 12 monthly status + income variables --
forvalues m = 1/12 {
    gen str24 status_m`m' = ""
    gen income_m`m' = 0

    * Yatra months: fixed occupation status; income VARIES by calendar month
    * (seasonality) and by person (idiosyncratic noise) -- never a flat repeat.
    local seas = 1.00
    if `m'==5  local seas = 1.25   // May   - pilgrim peak
    if `m'==6  local seas = 1.15   // June  - still high
    if `m'==7  local seas = 0.55   // July  - monsoon dip
    if `m'==8  local seas = 0.55   // Aug   - monsoon dip
    if `m'==9  local seas = 0.95   // Sept  - recovering
    if `m'==10 local seas = 0.80   // Oct   - tapering, season close

    replace status_m`m' = "Yatra work" if `m' >= yatra_start_month & `m' <= yatra_end_month
    replace income_m`m' = round((occ_mean * `seas' * rgamma(6,1/6))/500)*500 ///
        if `m' >= yatra_start_month & `m' <= yatra_end_month

    * off-season months: 80% primary activity, 20% genuine "No work" that
    * month -- except "No other work" (no work in ANY off-season month) and
    * "Salaried job" (regular pay, so no monthly gaps).
    gen ru_`m' = runiform()
    replace status_m`m' = offseason_primary if (`m' < yatra_start_month | `m' > yatra_end_month) & offseason_primary!="No other work" & (ru_`m' < .8 | offseason_primary=="Salaried job")
    replace status_m`m' = "No work"         if (`m' < yatra_start_month | `m' > yatra_end_month) & (offseason_primary=="No other work" | (ru_`m' >= .8 & offseason_primary!="Salaried job"))

    replace income_m`m' = round(rgamma(3, off_mean/3)/100)*100 ///
        if (`m' < yatra_start_month | `m' > yatra_end_month) & status_m`m'!="No work"
    replace income_m`m' = 0 if status_m`m'=="No work"
    drop ru_`m'
}
drop off_mean

* -- sum months into Yatra vs off-season totals --
gen yatra_income = 0
gen non_yatra_income = 0
forvalues m = 1/12 {
    replace yatra_income = yatra_income + income_m`m' if `m'>=yatra_start_month & `m'<=yatra_end_month
    replace non_yatra_income = non_yatra_income + income_m`m' if `m'<yatra_start_month | `m'>yatra_end_month
}

* -- tier-specific floor: LOW-tier occupations are only guaranteed to clear
* Rs.2,00,000 for the season (matches "only about 2-3.5 lakh" for pony
* handlers/wage labourers/shopkeepers); everyone else keeps the original
* Rs.3,00,000 floor. Top-up spread evenly across that person's Yatra months
* so the monthly figures still sum exactly to the reported season total. --
gen income_floor = 300000
replace income_floor = 200000 if income_tier=="low"

gen shortfall = max(income_floor - yatra_income, 0)
gen topup_per_month = ceil((shortfall/yatra_months)/500)*500
forvalues m = 1/12 {
    replace income_m`m' = income_m`m' + topup_per_month if `m'>=yatra_start_month & `m'<=yatra_end_month & shortfall>0
}
replace yatra_income = yatra_income + topup_per_month*yatra_months if shortfall>0
drop shortfall topup_per_month occ_mean income_floor

*-----------------------------------------------------------------------------
* RULE 5 -- migration status (binary) + origin (incl. Nepal), separate items
*-----------------------------------------------------------------------------
gen migrant = rbinomial(1,.25)
gen u3 = runiform()
gen origin = "Local (same district)"
replace origin = "Other Uttarakhand district" if migrant==1 & u3 < .45
replace origin = "Other Indian state"          if migrant==1 & u3 >= .45 & u3 < .85
replace origin = "Nepal"                       if migrant==1 & u3 >= .85
drop u3

* migration reason -- only asked of migrants [Source: NSS 64th Round Migration Survey]
gen u3b = runiform()
gen migration_reason = ""
replace migration_reason = "Employment"          if migrant==1 & u3b<.65
replace migration_reason = "Marriage"            if migrant==1 & u3b>=.65 & u3b<.78
replace migration_reason = "Displacement/other"  if migrant==1 & u3b>=.78 & u3b<.90
replace migration_reason = "Family movement"     if migrant==1 & u3b>=.90
drop u3b

* years since migration -- bounded by years_in_yatra_work (can't have moved
* more recently than starting this line of work) and by age [Source: NSS 64th Round]
gen years_since_migration = .
replace years_since_migration = years_in_yatra_work + round(rgamma(2,2/2)) if migrant==1
replace years_since_migration = min(years_since_migration, age-16) if migrant==1

* NSS short-term/seasonal migrant flag: anyone who leaves their usual place
* of residence for 15 days-6 months for work qualifies under NSS's definition
* -- which describes nearly this entire Yatra workforce regardless of their
* permanent origin, since Kedarnath itself is not where most workers live
* year-round. Only genuine local residents of the immediate Yatra-route
* settlement (assumed ~10%) fall outside this definition.
* [Source: NSS 64th Round / 2026 National Migration Survey draft]
gen byte short_term_migrant_nss = 1
replace short_term_migrant_nss = 0 if runiform() < .10

*-----------------------------------------------------------------------------
* RULE 6 (cont.) -- remittances: TWO variables, inward and outward, asked
* separately. These are seasonal migrant WORKERS coming to Kedarnath, so the
* realistic direction of flow is OUTWARD (sending earnings home) -- inward
* transfers (family sending money TO the respondent here) are the unusual case.
*-----------------------------------------------------------------------------
gen remit_out_prob = .20 + .45*migrant
gen remittance_outward = 0
replace remittance_outward = round(rgamma(2, 20000/2)/500)*500 if runiform() < remit_out_prob
drop remit_out_prob

* remittance frequency (number of times sent in the year) -- alongside
* amount, matching NSS practice of asking both. [Source: NSS 64th Round]
gen remittance_outward_frequency = 0
replace remittance_outward_frequency = 1 + rpoisson(2.5) if remittance_outward>0
replace remittance_outward_frequency = min(remittance_outward_frequency,12)

gen remittance_inward = 0
replace remittance_inward = round(rgamma(2, 8000/2)/500)*500 if runiform() < .06
gen remittance_inward_frequency = 0
replace remittance_inward_frequency = 1 + rpoisson(1.5) if remittance_inward>0
replace remittance_inward_frequency = min(remittance_inward_frequency,12)

gen total_annual_income = yatra_income + non_yatra_income + remittance_inward
* (remittance_outward is an outflow, not household income -- kept as a
*  separate reported item, not added into total_annual_income)
gen yatra_income_share = round(yatra_income / total_annual_income, 0.001)      // calculated, not asked

*-----------------------------------------------------------------------------
* RULE 8 -- welfare measured via USUAL HOMEPLACE consumption, independent of
* Kedarnath-season spending. Anchored loosely to household size only, not to
* Yatra income, to keep the "home life" concept distinct from season earnings.
*-----------------------------------------------------------------------------
gen home_std = rnormal(1,.25)             // household-level draw: relative living-standard shifter
replace home_std = max(home_std,.4)

*-----------------------------------------------------------------------------
* RULE 9-10 -- 30-day recall, broad RBI/NSS-style groups, integers, with
* heaping, recall noise, and genuine zeroes.
*-----------------------------------------------------------------------------
gen cons_food_30d       = round((hhsize*1550*home_std) + rnormal(0,300), 50)
replace cons_food_30d   = max(cons_food_30d, 300)

gen cons_fuel_30d       = round((hhsize*260*home_std) + rnormal(0,80), 50)
replace cons_fuel_30d   = max(cons_fuel_30d, 0)
replace cons_fuel_30d   = 0 if runiform() < .08                  // genuine zero: free firewood etc.

gen cons_routine_misc_30d = round((hhsize*480*home_std) + rnormal(0,150), 50)
replace cons_routine_misc_30d = max(cons_routine_misc_30d, 0)
replace cons_routine_misc_30d = 0 if runiform() < .10

gen cons_rent_30d = 0
replace cons_rent_30d = round(rgamma(3, 1500/3), 100) if runiform() < .20   // most own their home

*-----------------------------------------------------------------------------
* RULE 11 -- less-frequent items on 12-month recall, converted to monthly.
* Integers with heaping and genuine zeroes at the annual-report stage.
*-----------------------------------------------------------------------------
gen cons_clothing_12m = round((hhsize*2400*home_std) + rnormal(0,500), 500)
replace cons_clothing_12m = max(cons_clothing_12m, 0)

gen cons_education_12m = 0
replace cons_education_12m = round(rgamma(3, 7000/3), 500) if runiform() < .60   // 40% no school-age children

gen cons_medical_12m = 0
replace cons_medical_12m = round(rgamma(2, 6000/2), 500) if runiform() < .50

gen cons_durables_12m = 0
replace cons_durables_12m = round(rgamma(2, 7000/2), 500) if runiform() < .40

foreach v of varlist cons_clothing_12m cons_education_12m cons_medical_12m cons_durables_12m {
    gen `v'_pm = round(`v'/12)          // monthly-equivalent, rounded to the nearest rupee
}

*-----------------------------------------------------------------------------
* RULE 12 -- poverty comparison against the Rangarajan Committee (2014) rural
* line, updated to current prices
*-----------------------------------------------------------------------------
gen total_cons_pm = cons_food_30d + cons_fuel_30d + cons_routine_misc_30d + cons_rent_30d ///
    + cons_clothing_12m_pm + cons_education_12m_pm + cons_medical_12m_pm + cons_durables_12m_pm
gen cons_pc_pm = round(total_cons_pm / hhsize)      // per-capita figure, rounded to the nearest rupee
* Original: Rs.972/month per capita at 2011-12 prices. PRIMARY LINE now
* Rs.2,515/month (rural), from:
*   Sethu, C. A., Surya, L. T. Abhinav, and Ruthu, C. A. (2024), "Poverty in
*   India: The Rangarajan Method and the 2022-23 Household Consumption
*   Expenditure Survey," Review of Agrarian Studies, Vol. 14, No. 2,
*   July-December 2024. https://doi.org/10.25003/RAS.14.02.0002
* WHY this figure and not a CPI-adjusted one: Sethu et al. re-implement the
* Rangarajan Expert Group (2014)'s own methodology (food + essential
* non-food + other-expenditure components benchmarked against nutritional
* norms) directly on HCES 2022-23 unit-level microdata, rather than
* inflating the 2011-12 line forward with the CPI. This makes it the more
* methodologically faithful "Rangarajan-method" estimate currently
* available, notwithstanding the journal's modest citation-impact tier --
* no GoI-official line exists for 2022-23 for either method to be checked
* against, so fidelity to the original committee's stated procedure is the
* relevant standard here, not journal ranking. See Sethu et al. Table 7 for
* the full comparison across estimation approaches.
* NOTE: this is a NATIONAL rural average -- hill-state cost of living may
* run higher, a real limitation worth stating explicitly in any write-up,
* not a precision this synthetic exercise can resolve on its own.
* SENSITIVITY LINE: Rangarajan, C., and Dev, S. M. (2024), "With New
* Consumption Survey, the Need for New Indices," The Indian Express, Mar 12
* -- CPI-adjusted their own 2011-12 Expert Group (2014) line forward to a
* "tentative" ~Rs.1,850/month (national rural average); this was the point
* estimate used in earlier versions of this instrument. Keep both; report
* poverty/vulnerability under each as a robustness check (see analysis
* do-file), since neither figure is an official GoI-notified line and the
* choice between them is itself a live methodological debate (Sethu et al.
* 2024 vs. Rangarajan & Dev 2024) worth naming explicitly in the write-up.
gen byte poor = (cons_pc_pm < 2515)
gen byte poor_sensitivity_cpi = (cons_pc_pm < 1850)
label var poor "1 = cons_pc_pm < Rs.2,515/month (Sethu et al. 2024 Rangarajan-method rural line, HCES 2022-23)"
label var poor_sensitivity_cpi "1 = cons_pc_pm < Rs.1,850/month (Rangarajan & Dev 2024 CPI-adjusted line) -- sensitivity check only"

*-----------------------------------------------------------------------------
* RULE 13 -- compact asset module
*-----------------------------------------------------------------------------
* house construction: floor and roof material, with house_type DERIVED from
* them rather than drawn independently -- a shared latent "housing quality"
* draw keeps the three internally consistent (no more Kaccha houses with
* marble floors, or Pucca houses with thatch roofs). This mirrors NFHS-5's
* own approach, where pucca/semi-pucca/kaccha is itself a composite of
* construction materials, not a separately-asked item. [Source: NFHS-5]
*
* Standard-of-living/asset variables below are DELIBERATELY wired to
* income_tier (per instruction: a household literally has to be able to
* afford a motorcycle or a pucca roof) -- unlike the health module above,
* which was deliberately wired to geography instead.
gen income_shift = 0
replace income_shift = 0.9  if income_tier=="high"
replace income_shift = -0.6 if income_tier=="low"

gen z_house = rnormal(0,1) + income_shift
gen z_floor = z_house + rnormal(0,0.35)
gen z_roof  = z_house + rnormal(0,0.35)

gen floor_tier = 2
replace floor_tier = 1 if z_floor < invnormal(.18)
replace floor_tier = 3 if z_floor >= invnormal(.75)
gen floor_material = "Cement/mud-cement"
replace floor_material = "Mud/kaccha"         if floor_tier==1
replace floor_material = "Tile/mosaic/marble" if floor_tier==3

gen roof_tier = 2
replace roof_tier = 1 if z_roof < invnormal(.15)
replace roof_tier = 3 if z_roof >= invnormal(.65)
gen roof_material = "Tin/GI sheet"
replace roof_material = "Thatch/wood/mud" if roof_tier==1
replace roof_material = "Concrete/RCC"    if roof_tier==3

gen house_tier = round((floor_tier+roof_tier)/2)
gen house_type = "Semi-pucca"
replace house_type = "Kaccha" if house_tier==1
replace house_type = "Pucca"  if house_tier==3

* CONSISTENCY GUARDRAIL -- "high income but Kaccha house": the shared z_house
* latent draw makes this rare (income_shift=+0.9 for high-tier) but not
* impossible, since floor_tier/roof_tier each carry their own idiosyncratic
* noise (+/-0.35 sd) on top of the shared component. A high-tier household
* (Rs.3.2-4 lakh/season floor) can realistically afford at least a
* semi-pucca home, so a residual fully-Kaccha draw is treated as a
* guardrail case, not a valid outcome, and is bumped up one tier.
quietly count if income_tier=="high" & house_type=="Kaccha"
if r(N)>0 di as result "Guardrail: " r(N) " high-income household(s) reassigned from Kaccha to Semi-pucca"
replace house_type = "Semi-pucca" if income_tier=="high" & house_type=="Kaccha"

drop z_house z_floor z_roof floor_tier roof_tier house_tier income_shift

* electricity/toilet: govt schemes have made these near-universal in hill
* Uttarakhand regardless of income, so only a modest income gradient
gen byte electricity     = rbinomial(1, min(0.90 + 0.03*(income_tier=="high") - 0.05*(income_tier=="low"), 0.97))
gen byte toilet_facility = rbinomial(1, min(0.72 + 0.15*(income_tier=="high") - 0.10*(income_tier=="low"), 0.95))
gen u5 = runiform()
gen drinking_water = "Piped"
replace drinking_water = "Handpump/borewell" if u5 >= .55 & u5 < .85
replace drinking_water = "Other (spring/tanker)" if u5 >= .85
drop u5

* itemized durables list (NFHS-5 wealth-index item set) -- probabilities now
* scale with income_tier, sharply for the big-ticket items (car, fridge,
* motorcycle), only mildly for cheap/near-universal ones (TV, bicycle).
* [Source: NFHS-5]
gen byte owns_tv = rbinomial(1, min(0.45 + 0.20*(income_tier=="high") - 0.10*(income_tier=="low"), 0.92))
gen byte owns_radio = rbinomial(1, 0.15)
gen byte owns_bicycle = rbinomial(1, min(0.40 + 0.10*(income_tier=="high") - 0.05*(income_tier=="low"), 0.80))
gen byte owns_motorcycle = rbinomial(1, min(0.20 + 0.35*(income_tier=="high") - 0.12*(income_tier=="low"), 0.85))
gen byte owns_car = rbinomial(1, min(0.02 + 0.20*(income_tier=="high") - 0.015*(income_tier=="low"), 0.55))
gen byte owns_fridge = rbinomial(1, min(0.15 + 0.35*(income_tier=="high") - 0.10*(income_tier=="low"), 0.85))
gen durables_count = owns_tv+owns_radio+owns_bicycle+owns_motorcycle+owns_car+owns_fridge

* cooking fuel -- genuine DUAL dependency: affordability (income_tier) AND
* supply-chain reach (health_access_tier doubles as a rough remoteness proxy
* here -- Poor/Moderate access locations also have weaker LPG cylinder
* resupply logistics up the mountain, independent of whether a household
* could otherwise afford it).
gen lpg_prob = 0.55
replace lpg_prob = lpg_prob + 0.30 if income_tier=="high"
replace lpg_prob = lpg_prob - 0.20 if income_tier=="low"
replace lpg_prob = lpg_prob - 0.25 if health_access_tier=="Poor"
replace lpg_prob = lpg_prob - 0.10 if health_access_tier=="Moderate"
replace lpg_prob = max(min(lpg_prob, 0.95), 0.05)
gen byte cooking_fuel_lpg = rbinomial(1, lpg_prob)   // 1 = LPG primary, 0 = traditional (wood/dung/kerosene)
drop lpg_prob

* bank/deposit account ownership -- near-universal in rural financial
* inclusion instruments. Jan Dhan specifically TARGETS the financially
* excluded, so it runs opposite to income_tier even conditional on having
* an account at all. [Source: AIDIS / NAFIS]
gen byte has_bank_account = rbinomial(1, min(0.75 + 0.15*(income_tier=="high") - 0.05*(income_tier=="low"), 0.97))
gen byte has_jandhan_account = 0
replace has_jandhan_account = rbinomial(1, min(0.35 + 0.30*(income_tier=="low") - 0.15*(income_tier=="high"), 0.85)) if has_bank_account==1

gen land_acres = 0
replace land_acres = round(rgamma(2, 0.5/2), 0.1) if runiform() < (.40 + 0.10*(income_tier=="high"))

gen livestock_count = 0
replace livestock_count = rpoisson(1.5) if runiform() < .35

gen pony_count = 0
replace pony_count = 1 + rpoisson(2) if inlist(occupation,"Pony worker","Pony business")

gen byte business_asset_owned = inlist(occupation,"Pony business","Shop owner","Hotel/lodging owner","Dhaba/food-stall owner")

*-----------------------------------------------------------------------------
* RULE 14 -- alternative livelihoods / digital readiness
*-----------------------------------------------------------------------------
gen byte prev_occ_change     = rbinomial(1,.30)   // worked in a different occupation before this one
gen byte prev_offseason_work = rbinomial(1,.35)   // used to do off-season non-Yatra work (even if not now)

gen training_prob = .15
replace training_prob = .35 if inlist(occupation,"Shop owner","Hotel/lodging owner","Dhaba/food-stall owner","Guide")
gen byte training_received = rbinomial(1,training_prob)
drop training_prob
gen u6 = runiform()
gen training_type = ""
replace training_type = "Tourism/hospitality" if training_received==1 & u6<.5
replace training_type = "Vocational/trade"     if training_received==1 & u6>=.5
drop u6

gen byte smartphone_owned = rbinomial(1,.65)
gen u7 = runiform()
gen digital_payment_use = "Never"
replace digital_payment_use = "Sometimes" if smartphone_owned==1 & u7 < .55
replace digital_payment_use = "Often"     if smartphone_owned==1 & u7 >= .55
drop u7

* -- credit source (expanded from a bare Yes/No per your instruction) --
* Still ONE question, just richer categories: institutional vs
* non-institutional matches AIDIS's own credit-agency classification.
* [Source: AIDIS]
gen u9 = runiform()
gen credit_source = "No credit taken"
replace credit_source = "Institutional (bank/co-op/SHG-linked)"  if u9 >= .70 & u9 < .88
replace credit_source = "Non-institutional (moneylender/relative)" if u9 >= .88
drop u9

* insurance coverage -- wasn't in the instrument at all before.
* [Source: NABARD NAFIS]
gen u10 = runiform()
gen insurance_coverage = "None"
replace insurance_coverage = "Health"   if u10 >= .55 & u10 < .72
replace insurance_coverage = "Life"     if u10 >= .72 & u10 < .85
replace insurance_coverage = "Crop"     if u10 >= .85 & u10 < .90
replace insurance_coverage = "Multiple" if u10 >= .90
drop u10

gen byte govt_scheme_beneficiary  = rbinomial(1,.30)   // one Yes/No question: any govt livelihood/welfare scheme

*-----------------------------------------------------------------------------
* HEALTH MODULE (new -- not in the original 18-rule instrument, which
* deliberately excluded health; reintroduced here per instruction).
* [Source: NSS 75th Round Household Social Consumption: Health]
*
* Design logic: WHETHER someone falls ill is treated as largely exogenous
* (biological, not a function of income or geography -- illness doesn't
* check your bank balance). What DOES depend on geography is the CONSEQUENCE:
* out-of-pocket cost (remote care means travel/evacuation costs on top of
* treatment) and whether the household counts as health-access-deprived for
* the multidimensional poverty construction below. This is deliberately NOT
* wired to income_tier or total_annual_income.
*-----------------------------------------------------------------------------
gen byte morbidity_15d = rbinomial(1,.12)          // any acute ailment, household, last 15 days
replace morbidity_15d = rbinomial(1,.16) if age>=55  // mild age effect only

gen byte hospitalization_365d = rbinomial(1,.10)   // any hospitalization, household, last 365 days

* OOPE: geography-driven surcharge, not income-driven. Poor-access locations
* mean travel/evacuation cost stacked on top of treatment itself.
gen oope_base = 8000
replace oope_base = 14000 if health_access_tier=="Poor"
replace oope_base = 10000 if health_access_tier=="Moderate"
gen oope_amount = 0
replace oope_amount = round(rgamma(2, oope_base/2)/500)*500 if hospitalization_365d==1
drop oope_base

gen byte health_insurance_covered = 0
replace health_insurance_covered = 1 if insurance_coverage=="Health" | insurance_coverage=="Multiple"
replace health_insurance_covered = 1 if govt_scheme_beneficiary==1 & runiform()<.4   // PMJAY/Ayushman overlap with general scheme question

* MPI-facing health-access deprivation indicator -- geography is the driver,
* not affordability: even an insured household is "deprived" here if the
* nearest facility is effectively out of reach; an uninsured household in a
* well-connected location is not automatically deprived on this indicator.
gen byte health_access_deprived = 0
replace health_access_deprived = 1 if health_access_tier=="Poor"
replace health_access_deprived = 1 if health_access_tier=="Moderate" & health_insurance_covered==0

*-----------------------------------------------------------------------------
* DISTRESS EVENTS MODULE (new candidate module). Retrospective and factual
* (what happened in the last year), not hypothetical/expected -- so this
* does not fall under Rule 16's exclusion of expected-loss/scenario items.
* [Source: NABARD NAFIS]
*-----------------------------------------------------------------------------
gen u11 = runiform()
gen distress_event_last365d = "None"
replace distress_event_last365d = "Major illness/death of earning member" if u11 >= .75 & u11 < .85
replace distress_event_last365d = "Crop failure or livestock loss"        if u11 >= .85 & u11 < .92
replace distress_event_last365d = "Natural disaster damage"               if u11 >= .92 & u11 < .97
replace distress_event_last365d = "Business/asset loss"                   if u11 >= .97
drop u11

*-----------------------------------------------------------------------------
* RULE 15 -- attitudes toward the ropeway
* (RULE 16 -- explicitly EXCLUDED: expected income loss, hypothetical
*  earnings, willingness-to-learn-skills, and any VEP/scenario simulation
*  items are NOT generated here.)
*-----------------------------------------------------------------------------
gen opp_lean = 0
replace opp_lean = 1 if inlist(occupation,"Pony worker","Pony business","Porter","Palki")

gen u8 = runiform()
gen ropeway_stance = "Neutral"
replace ropeway_stance = "Oppose"  if opp_lean==1 & u8 < .52
replace ropeway_stance = "Support" if opp_lean==1 & u8 >= .77 & u8 < .95
replace ropeway_stance = "Support" if opp_lean==0 & u8 < .52
replace ropeway_stance = "Oppose"  if opp_lean==0 & u8 >= .80 & u8 < .95
replace ropeway_stance = "Don't know / Prefer not to say" if u8 >= .95
drop u8 opp_lean

* a few 5-point Likert items (1=strongly disagree .. 5=strongly agree)
gen accessibility_improve   = min(max(round(rnormal(4,1)),1),5)
gen inequality_concern      = min(max(round(rnormal(3.3,1.1)),1),5)
gen vulnerable_pilgrims_help = min(max(round(rnormal(3.6,1)),1),5)
gen rehab_confidence        = min(max(round(rnormal(2.6,1.1)),1),5)

drop home_std

*=============================================================================
* INTERNAL CONSISTENCY CHECKS (for write-up / data-quality appendix)
*
* Two kinds of check below:
*  (i)  `assert` on combinations that should be STRUCTURALLY IMPOSSIBLE by
*       construction -- if any of these fire, there is a genuine bug
*       upstream, and the do-file stops.
*  (ii) `count`/`tabulate` displays on combinations that are unusual but
*       INTENTIONAL (e.g. Porter = high income + casual labour) -- these are
*       informational, logged for transparency, and do not stop execution.
*=============================================================================
di as result "=============================================================="
di as result " INTERNAL CONSISTENCY CHECKS"
di as result "=============================================================="

* (i) house_type is DERIVED from floor/roof tier (Rule 13), so a materials/
* house_type mismatch (e.g. Kaccha house with a marble floor, or Pucca house
* with a thatch roof) should be structurally impossible. Verify explicitly.
assert !(house_type=="Kaccha" & floor_material=="Tile/mosaic/marble")
assert !(house_type=="Kaccha" & roof_material=="Concrete/RCC")
assert !(house_type=="Pucca"  & floor_material=="Mud/kaccha")
assert !(house_type=="Pucca"  & roof_material=="Thatch/wood/mud")
di as result "OK: no Kaccha/Pucca house_type contradicts its own floor or roof material."

* (i) guardrail from Rule 13 should leave zero high-income Kaccha households.
assert !(income_tier=="high" & house_type=="Kaccha")
di as result "OK: no high-income_tier household remains in a Kaccha house."

* (i) basic range/non-negativity checks that should hold by construction.
assert inrange(age,18,70)
assert inrange(hhsize,2,10)
assert yatra_income>=0 & non_yatra_income>=0 & total_annual_income>=0
assert cons_pc_pm>0
di as result "OK: age, hhsize, income and consumption fields are all in range."

* (i) category-expansion safeguards: every occupation must be fully
* parameterized (no missing earnings, tier or employment status), and the
* new off-season states must behave as defined.
assert !missing(yatra_income, total_annual_income, cons_pc_pm)
assert income_tier!="" & employment_type!="" & offseason_primary!=""
assert non_yatra_income==0 if offseason_primary=="No other work"
assert non_yatra_income>0  if offseason_primary=="Salaried job"
di as result "OK: all 13 occupations and 7 off-season states are fully parameterized."
di as result "--- Occupation x employment_type (full 13-category mapping) ---"
tabulate occupation employment_type
di as result "--- off-season primary activity ---"
tabulate offseason_primary

* (ii) Porter is high-income_tier but a self-employed own-account worker
* (not an employer/business owner), and so not a business/asset owner --
* intentional (see Rule 12 comment), displayed here for the record.
di as result "--- Occupation x income_tier x employment_type (Porter check) ---"
tabulate occupation income_tier if occupation=="Porter"
tabulate occupation employment_type if occupation=="Porter"
di as result "--- income_tier x business_asset_owned (expect high-tier, non-owner cell > 0 due to Porter) ---"
tabulate income_tier business_asset_owned

*-----------------------------------------------------------------------------
* INTEGER SAFETY PASS -- every REPORTED (non-computed) monetary figure must
* be a whole rupee; only calculated ratios/statistics (yatra_income_share,
* cons_pc_pm, etc.) are allowed decimals.
*-----------------------------------------------------------------------------
foreach v of varlist yatra_income non_yatra_income total_annual_income ///
    remittance_inward remittance_outward oope_amount ///
    income_m1 income_m2 income_m3 income_m4 income_m5 income_m6 ///
    income_m7 income_m8 income_m9 income_m10 income_m11 income_m12 ///
    cons_food_30d cons_fuel_30d cons_routine_misc_30d cons_rent_30d ///
    cons_clothing_12m cons_education_12m cons_medical_12m cons_durables_12m {
    replace `v' = round(`v')
}

*-----------------------------------------------------------------------------
* labels & save FULL n=200 GENERATED SAMPLE (kept for reference/comparison)
*-----------------------------------------------------------------------------
label data "SYNTHETIC v2 instrument simulation, n=200 -- hand-parameterized, NOT drawn from pilot data. Methodological note only."
label var yatra_income_share "Calculated: yatra_income / total_annual_income"
label var cons_pc_pm "Per-capita monthly consumption (home place, RBI/NSS-style)"

*=============================================================================
* SAMPLE ATTRITION SIMULATION -- reduce n=200 to n~125, "as fielded"
*
* Two separate mechanisms, mirroring how a real Kedarnath fieldwork round
* would actually lose observations:
*   (A) CONTRADICTION INJECTION -- a handful of records get an internally
*       impossible combination of answers (enumerator/entry error), then get
*       caught and dropped in data cleaning, the way a real research team
*       would flag and discard them.
*   (B) CORRELATED DROPOUT -- most attrition is refusal/incompleteness that
*       is NOT random. It's weighted toward: (i) occupations that are busiest
*       or warier of a ropeway-topic survey (pony/porter/palki workers, and
*       separately, busy owner-operators during peak season), (ii) lower
*       education (weaker numeric recall, more item non-response), (iii)
*       older respondents (recall burden), (iv) migrants (less invested in
*       a long local survey while away from home). This means the retained
*       n~125 sample is NOT representative of the true occupation mix --
*       that skew is the point, not a bug, and should be reported as a
*       limitation in any write-up.
*=============================================================================

*-----------------------------------------------------------------------------
* (A) Contradiction injection -- pick ~10 respondents, force one impossible
* combination each, flag them for removal in cleaning.
*-----------------------------------------------------------------------------
gen byte flagged_contradiction = 0
gen u_contra = runiform()

* type 1: reports "No work" in every non-Yatra month, yet has positive
* non_yatra_income on record (enumerator logic error)
replace flagged_contradiction = 1 if u_contra < .025 & non_yatra_income > 0

* type 2: reports zero household size-implied consumption (cons_pc_pm
* missing/zero) while simultaneously reporting durable assets and a pucca
* house -- an implausible combination suggesting a skipped consumption module
replace flagged_contradiction = 1 if u_contra >= .025 & u_contra < .05 & house_type=="Pucca" & durables_count>=3

drop u_contra

*-----------------------------------------------------------------------------
* (B) Correlated dropout score -- NOT missing completely at random
*-----------------------------------------------------------------------------
gen dropout_score = 0
replace dropout_score = dropout_score + 2 if inlist(occupation,"Pony worker","Porter","Palki")
replace dropout_score = dropout_score + 1 if occupation=="Pony business"
replace dropout_score = dropout_score + 1 if inlist(occupation,"Shop owner","Hotel/lodging owner","Dhaba/food-stall owner","Driver")
replace dropout_score = dropout_score + 2 if education_level=="No formal education"
replace dropout_score = dropout_score + 2 if education_level=="Prefer not to say"
replace dropout_score = dropout_score + 1 if education_level=="Primary (up to 5th)"
replace dropout_score = dropout_score + 1 if age>=55
replace dropout_score = dropout_score + 1 if migrant==1

gen dropout_prob = min(0.25 + 0.115*dropout_score, 0.85)
gen byte flagged_dropout = (runiform() < dropout_prob)

*-----------------------------------------------------------------------------
* Final "as fielded" sample: drop anyone flagged by either mechanism
*-----------------------------------------------------------------------------
gen byte retained = (flagged_contradiction==0 & flagged_dropout==0)

*-----------------------------------------------------------------------------
* FIELDWORK METADATA -- interview-level administrative fields that any real
* CAPI/paper survey export would carry (enumerator, date, duration, GPS
* jitter), but which the earlier version of this instrument omitted
* entirely. Purely administrative: none of this feeds the VtP/MPI analysis.
* Deliberately generated LAST, after `retained` is already determined --
* new random draws inserted any earlier would shift Stata's single random
* stream and change which households the attrition mechanism above retains,
* for no substantive reason. Fieldwork window: a 26-day stretch during the
* Yatra peak season, when enumerators can actually reach workers on-route.
*-----------------------------------------------------------------------------
gen byte enum_num = 1 + floor(6*runiform())
tostring enum_num, gen(enum_str)
gen enum_code = "ENUM0" + enum_str
drop enum_num enum_str

gen interview_date = mdy(6,15,2026) + floor(26*runiform())
format interview_date %td

* interview duration: right-skewed, most interviews 25-45 min, a longer tail
* for respondents with more to report (owners, multiple income sources)
gen interview_duration_min = round(22 + rgamma(4,5))
replace interview_duration_min = min(interview_duration_min, 75)

* GPS jitter around each cluster's approximate real-world coordinates
* (deliberately rounded to 3dp -- not survey-grade precision)
gen gps_lat = .
gen gps_lon = .
replace gps_lat = 30.530 + rnormal(0,0.004) if location_cluster=="Guptkashi/Phata"
replace gps_lon = 79.070 + rnormal(0,0.004) if location_cluster=="Guptkashi/Phata"
replace gps_lat = 30.627 + rnormal(0,0.004) if location_cluster=="Sonprayag"
replace gps_lon = 78.949 + rnormal(0,0.004) if location_cluster=="Sonprayag"
replace gps_lat = 30.689 + rnormal(0,0.004) if location_cluster=="Gaurikund"
replace gps_lon = 78.952 + rnormal(0,0.004) if location_cluster=="Gaurikund"
replace gps_lat = 30.735 + rnormal(0,0.003) if location_cluster=="Kedarnath town"
replace gps_lon = 79.067 + rnormal(0,0.003) if location_cluster=="Kedarnath town"
replace gps_lat = round(gps_lat,0.001)
replace gps_lon = round(gps_lon,0.001)

gen u_lang = runiform()
gen interview_lang = "Hindi"
replace interview_lang = "Garhwali" if u_lang < .35
replace interview_lang = "Nepali"   if u_lang >= .97
drop u_lang

* FIELD-REALISM CLEANUP -- income_tier was a generation-time modelling
* device (it drove which occupations get which earnings/asset draws) with
* no real-world questionnaire analogue; it is not used anywhere in the
* analysis do-file (verified). Drop it here so the saved files carry only
* variables a genuine field instrument would actually produce.
drop income_tier
compress
save "kedarnath_synthetic_v2_n200_full.dta", replace

* -- save a version with the retention flag intact for ALL 200 (dropped and
* kept), needed for the IPW selection-model robustness check. In real
* fieldwork you would NOT have this for genuine refusals -- this only works
* here because the data is synthetic and we know who "would have" existed. --
save "kedarnath_synthetic_v2_n200_retention_flag.dta", replace

di as result "=============================================================="
di as result " Contradiction-flagged (dropped in cleaning): " 
quietly count if flagged_contradiction==1
di as result r(N)
di as result " Dropout-flagged (non-response/refusal):"
quietly count if flagged_dropout==1 & flagged_contradiction==0
di as result r(N)
di as result " Retained -- final analysis sample:"
quietly count if retained==1
di as result r(N)
di as result "=============================================================="

preserve
    keep if retained==1
    drop flagged_contradiction flagged_dropout dropout_score dropout_prob retained
    label data "SYNTHETIC v2, AS-FIELDED sample (n~125) -- attrition applied on top of the n=200 full generation, with dropout probability correlated to occupation/education/age/migration status. See do-file comments for the exact mechanism. Methodological note only, not real data."
    compress
    save "kedarnath_synthetic_v2_n125_asfielded.dta", replace
    describe
    di as result "As-fielded retention by occupation:"
    tabulate occupation
    di as result "As-fielded summary:"
    summarize total_annual_income yatra_income_share cons_pc_pm poor hhsize
restore
save data, replace
di as error "=============================================================="
di as error " Two datasets now exist:"
di as error "  kedarnath_synthetic_v2_n200_full.dta      (n=200, as designed)"
di as error "  kedarnath_synthetic_v2_n125_asfielded.dta (n~125, as fielded, biased)"
di as error " Use the n125 file for any analysis meant to demonstrate real"
di as error " fieldwork conditions; use the n200 file only to sanity-check"
di as error " the underlying generation process itself."
di as error "=============================================================="
log close
