"""Build a household-level analysis file from the REAL VASyR 2025 (Lebanon) microdata
in vasyr/ (UNHCR_LBN_2025_VASYR_data_main_v2.1.csv, ..._data_member_v2.1.csv), mapped
onto the 21 indicators / 5 dimensions in Lyons, Kass-Hanna & Montoya Castano (2023,
J. Int. Dev. 35:2014-2045), Table 2. Their paper uses the 2018 VASyR wave, which is not
available here; this is the same survey series' 2025 wave, whose questionnaire has moved
on in places, so several indicators are DOCUMENTED PROXIES, not exact matches -- see the
comment on each block and the README. Output: vasyr_real_raw.csv (one row per household)."""
import os, pandas as pd, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.abspath(os.path.join(HERE, "..", "..", "vasyr"))
VD = os.path.join(RAW, "UNHCR_LBN_2025_VASYR_data_main_v2.1.csv")
MD = os.path.join(RAW, "UNHCR_LBN_2025_VASYR_data_member_v2.1.csv")

# ---------------------------------------------------------------------------
# MEMBER FILE -> household-level aggregates. age_s is banded (00-04/05-11/12-17/
# 18-24/25-49/50-59/60+), not a single year, so age-based cutoffs below use these
# bands (documented deviation from Lyons' exact age-15/age-10 cutoffs).
# ---------------------------------------------------------------------------
mcols = ["id", "age", "gender_s", "rel_to_hoh_s", "marital_status_s", "chronic_illness_yn",
         "dis_dif_seeing_s", "dis_dif_hearing_s", "dis_dif_walking_s", "dis_dif_remembering_s",
         "dis_dif_self_care_s", "attend_school_current_yr_yn", "attended_school_ever_yn",
         "work_for_pay_yn", "job_opp_avail_yn", "legal_res_yn"]
m = pd.read_csv(MD, usecols=mcols, low_memory=False)

WORKING_AGE = {"18 - 24", "25 - 49", "50 - 59"}   # proxy for 15-64 (bands don't split at 15/64)
ADULT_BANDS = {"18 - 24", "25 - 49", "50 - 59", "60+"}   # proxy for 10+ (bands don't split at 10)
CHILD_6_14 = {"05 - 11", "12 - 17"}                       # proxy for 6-14 (bands don't split at 14)
WG_DEPRIVED = {"c.A lot of difficulty", "d.Cannot do at all"}

m["disab_any"] = m[["dis_dif_seeing_s", "dis_dif_hearing_s", "dis_dif_walking_s",
                     "dis_dif_remembering_s", "dis_dif_self_care_s"]].isin(WG_DEPRIVED).any(axis=1)
m["special_needs_i"] = (m.chronic_illness_yn == "a. Yes") | m.disab_any

g = m.groupby("id")
out = pd.DataFrame(index=g.size().index)
out["hhsize_mem"] = g.size()

head = m[m.rel_to_hoh_s == "a. Head of Household"].drop_duplicates("id").set_index("id")
AGE_MID = {"00 - 04": 2, "05 - 11": 8, "12 - 17": 14.5, "18 - 24": 21, "25 - 49": 37,
           "50 - 59": 54.5, "60+": 65}
out["age_head"] = head.age.map(AGE_MID)
out["female_head"] = (head.gender_s == "b. Female").astype("Int64")
out["married_head"] = (head.marital_status_s == "b. Married").astype("Int64")

# 1. special needs (Health&Food dim.): chronic illness OR a Washington-Group disability
#    domain at "a lot of difficulty"/"cannot do at all" for ANY member (5 of 6 WG domains
#    available: seeing/hearing/walking/remembering/self-care; "communicating" not on file)
out["special_needs"] = g["special_needs_i"].any().astype(int)

# 5. child school attendance (Education dim.): any member in the 6-14 proxy band not
#    attending school this year
child = m[m.age.isin(CHILD_6_14)]
out["child_school"] = child.groupby("id").apply(
    lambda x: (x.attend_school_current_yr_yn == "b. No").any(), include_groups=False).reindex(out.index).fillna(False).astype(int)

# 6. adult years of schooling (Education dim.): PROXY. The real item is a free-text/coded
#    grade level with no clean grade->years crosswalk available here, so this uses "never
#    attended school" for every member in the 18+ proxy band (coarser than Lyons' "<6
#    years", almost certainly a smaller deprived share since some who attended briefly
#    still count as attended)
adult = m[m.age.isin(ADULT_BANDS)]
out["adult_schooling"] = adult.groupby("id").apply(
    lambda x: (x.attended_school_ever_yn == "b. No").all() if len(x) else False, include_groups=False
    ).reindex(out.index).fillna(False).astype(int)

# 9. unemployment (Employment dim.): share of working-age (proxy 18-59) members not
#    working for pay in the reference period >= 50%; households with no working-age
#    member asked this question are coded not-deprived (0), not missing
wa = m[m.age.isin(WORKING_AGE) & m.work_for_pay_yn.notna()]
wa_share = wa.groupby("id").apply(lambda x: (x.work_for_pay_yn == "b. No").mean(), include_groups=False)
out["unemployment"] = (wa_share.reindex(out.index) >= 0.5).fillna(False).astype(int)

# 10. underemployment (Employment dim.): PROXY. The 2025 questionnaire on file has no
#     "days worked last month" item, so this uses job_opp_avail_yn ("are job opportunities
#     available?", asked of members without a full paid job) as a labour-market-slack
#     proxy -- deprived if half or more of working-age members report none available
jo = m[m.age.isin(WORKING_AGE) & m.job_opp_avail_yn.notna()]
jo_share = jo.groupby("id").apply(lambda x: (x.job_opp_avail_yn == "b. No").mean(), include_groups=False)
out["underemployment"] = (jo_share.reindex(out.index) >= 0.5).fillna(False).astype(int)

# 16. legal residency (Security & social inclusion dim.): no member in the 15+ proxy
#     band (18+ here) holds legal residency -- direct match to Lyons' definition
adult15 = m[m.age.isin(ADULT_BANDS) & m.legal_res_yn.notna()]
lr_any = adult15.groupby("id").apply(lambda x: (x.legal_res_yn == "a. Yes").any(), include_groups=False)
out["legal_residency"] = (~lr_any.reindex(out.index).fillna(False)).astype(int)

out["dependent_share"] = 1 - (g.apply(lambda x: x.age.isin(WORKING_AGE).sum(), include_groups=False) / out.hhsize_mem)

# ---------------------------------------------------------------------------
# MAIN (household) FILE
# ---------------------------------------------------------------------------
vcols = ["id", "district_s", "total_num_hh_i", "electricity_access_yn", "type_of_toilet_s",
         "num_hh_using_facility_i", "drink_water_m_src_s", "energy_src_cooking_m_wood",
         "energy_src_cooking_m_charcoal", "energy_src_cooking_m_burning_trash",
         "assets_owned_mattresses", "assets_owned_blankets", "assets_owned_winter_clothing",
         "assets_owned_small_gas_stove", "assets_owned_refrigerator", "assets_owned_heater",
         "living_space_dec", "num_ppl_sharing_space_i", "type_of_housing_s", "changed_accom_yn",
         "damaged_shelter_yn", "san_pipes_not_func_yn", "latrine_not_usable",
         "smart_phone_yn", "have_internet_wifi_yn", "have_internet_phone_yn",
         "curfew_imposed_yn", "rel_refugees_s", "main_income_src_s", "borrow_money_credit_yn",
         "total_income_usd_dec",
         "barriers_health_case_access_phc_m_barriers_health_case_access_opt_1",
         "less_expensive_i", "borrowed_food_i", "reduced_meals_i", "reduced_portion_i",
         "restrict_consumption_i",
         "num_days_cereal_cons_i", "num_days_tubers_cons_i", "num_days_veg_i", "num_days_fruits_i",
         "num_days_flesh_meat_i", "num_days_organ_meat_i", "num_days_fish_i", "num_days_egg_i",
         "num_days_legumes_i", "num_days_milk_i", "num_days_oil_i", "num_days_sugar_i",
         "num_days_condiments_i"]
v = pd.read_csv(VD, usecols=vcols, low_memory=False).set_index("id")

# 2. healthcare access: did NOT select "no barrier" for primary-care access in the last 3
#    months (missing = not asked / no barrier applicable -> not deprived)
v["healthcare_access"] = (v["barriers_health_case_access_phc_m_barriers_health_case_access_opt_1"] == 0).fillna(False).astype(int)

# 3. food coping (rCSI, standard WFP weights 1/2/1/1/3), 4. diet diversity (13 food
# groups over 7 days, <9 distinct groups eaten = deprived, matching Lyons' <9 cutoff)
v["rcsi"] = v.less_expensive_i.fillna(0) + 2*v.borrowed_food_i.fillna(0) + v.reduced_meals_i.fillna(0) \
    + v.reduced_portion_i.fillna(0) + 3*v.restrict_consumption_i.fillna(0)
v["food_coping"] = (v.rcsi > 20).astype(int)
fg = ["num_days_cereal_cons_i", "num_days_tubers_cons_i", "num_days_veg_i", "num_days_fruits_i",
      "num_days_flesh_meat_i", "num_days_organ_meat_i", "num_days_fish_i", "num_days_egg_i",
      "num_days_legumes_i", "num_days_milk_i", "num_days_oil_i", "num_days_sugar_i", "num_days_condiments_i"]
v["diet_groups"] = (v[fg].fillna(0) > 0).sum(axis=1)
v["diet_diversity"] = (v.diet_groups < 9).astype(int)

# 7-14. living standards
v["electricity"] = (v.electricity_access_yn == "b. No").astype(int)
# unimproved facility types (WHO/UNICEF JMP style): match on the stable leading letter
# code rather than the full string, since punctuation/encoding varies category to category
v["sanitation"] = (v.type_of_toilet_s.fillna("").str.strip().str.startswith(("d.", "e.", "i.", "j.", "k.")) |
                    (v.num_hh_using_facility_i.fillna(0) > 1)).astype(int)
v["drinking_water"] = v.drink_water_m_src_s.fillna("").str.strip().str.startswith(("i.", "q.", "m.", "r.")).astype(int)
v["cooking_fuel"] = ((v.energy_src_cooking_m_wood == 1) | (v.energy_src_cooking_m_charcoal == 1) |
                      (v.energy_src_cooking_m_burning_trash == 1)).astype(int)
ASSETS6 = ["assets_owned_mattresses", "assets_owned_blankets", "assets_owned_winter_clothing",
           "assets_owned_small_gas_stove", "assets_owned_refrigerator", "assets_owned_heater"]
v["basic_assets"] = (v[ASSETS6].fillna(0).sum(axis=1) < 6).astype(int)
crowd_denom = v.num_ppl_sharing_space_i.fillna(v.total_num_hh_i)
v["crowding"] = ((v.living_space_dec / crowd_denom) < 4.5).astype(int)
v["shelter_conditions"] = (v.type_of_housing_s != "c. Apartment/house/room").astype(int)
v["housing_stability"] = (v.changed_accom_yn == "a. Yes").astype(int)

# 17. area/settlement conditions: PROXY using reported shelter/infrastructure damage
# (collapsed shelter, non-functional sanitation pipes, unusable latrine) as evidence of
# poor physical site conditions -- Lyons' own definition already bundles "poor sanitation
# conditions" and "low standard living conditions" into this indicator
v["area_settlement"] = ((v.damaged_shelter_yn == "a. Yes") | (v.san_pipes_not_func_yn == "a. Yes") |
                         (v.latrine_not_usable == "a. Yes")).astype(int)
# 18. communications access: no smartphone AND no home/phone internet
v["communications"] = ((v.smart_phone_yn == "b. No") & (v.have_internet_wifi_yn.fillna("b. No") == "b. No") &
                        (v.have_internet_phone_yn.fillna("b. No") == "b. No")).astype(int)
# 19. movement and mobility: exact match -- curfew imposed on the household's community
v["movement_mobility"] = (v.curfew_imposed_yn == "a. Yes").astype(int)
# 20. community interaction: exact match -- "never" or "rarely" interact with host community
v["community_interaction"] = v.rel_refugees_s.isin(["e. Never", "d. Rarely"]).astype(int)

# household resources (FGLS covariates, not MLI indicators)
INCOME_MAP = {  # main_income_src_s bucketed the way Lyons' "main income source" is
    "b. Agriculture": "employment", "g. Construction": "employment",
    "r. Other services: hotel, restaurant, transport, personal services": "employment",
    "h. Craft Work (blacksmith, plumber, mechanic, etc.)": "employment", "f. Concierge": "employment",
    "m. Home based work / skill": "employment", "s. Other types of sales": "employment",
    "n. Manufacturing": "employment", "p. Office work (finance, admin, secretary)": "employment",
    "aa Wholesale and retail trade": "employment",
    "c. ATM- cards used in ATM machines / BOB Finance from UN or humanitarian organizations": "assistance",
    "k. E-cards used in WFP FOOD SHOPS": "assistance",
    "j. Credit/debts (informal)shops, friends hosts)": "borrowing", "i. Credit/debts (formal banks)": "borrowing",
}
v["income_source"] = v.main_income_src_s.map(INCOME_MAP).fillna("other")
v["borrowed"] = (v.borrow_money_credit_yn == "a. Yes").astype(int)

keep = ["district_s", "total_num_hh_i", "healthcare_access", "food_coping", "rcsi", "diet_groups",
        "diet_diversity", "electricity", "sanitation", "drinking_water", "cooking_fuel", "basic_assets",
        "crowding", "shelter_conditions", "housing_stability", "area_settlement", "communications",
        "movement_mobility", "community_interaction", "income_source", "borrowed", "total_income_usd_dec"]
final = out.join(v[keep], how="inner")
final["hhsize"] = final.total_num_hh_i.fillna(final.hhsize_mem)
final = final.drop(columns=["total_num_hh_i"]).reset_index().rename(columns={"index": "id", "district_s": "district"})
final = final.dropna(subset=["age_head"])   # households with no identifiable head row

final.to_csv(os.path.join(HERE, "vasyr_real_raw.csv"), index=False)
n = len(final)
print(f"vasyr_real_raw.csv written: {n} households (of {len(out)} with a member roster)")
ind = ["special_needs", "healthcare_access", "food_coping", "diet_diversity", "child_school",
       "adult_schooling", "electricity", "sanitation", "drinking_water", "cooking_fuel", "basic_assets",
       "crowding", "shelter_conditions", "housing_stability", "unemployment", "underemployment",
       "legal_residency", "area_settlement", "communications", "movement_mobility", "community_interaction"]
for c in ind:
    if c in final.columns:
        print(f"  {c:20s} deprived share = {final[c].mean():.3f}")
