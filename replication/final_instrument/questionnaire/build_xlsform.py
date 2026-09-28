"""Build a KoboToolbox-ready XLSForm (.xlsx) from dictionary.py -- the same single source of
truth the Stata build and the PDF questionnaire already use. Only ROWS with origin in
("asked", selected paradata) become real form fields; constructed/synthetic variables are never
asked, so they're built in Stata after export (02_build_final_dataset.do), not here.

Kobo-native substitutions for paradata (documented, not literal 1:1 with dictionary.py):
  resp_id            -> dropped; Kobo's own submission _uuid/_id serves this on export
  enum_id            -> RESTORED 2026-09-24 as a real question, asked first, before consent.
                        Kobo's `_submitted_by` still identifies the account that submitted, but that
                        only separates the four enumerators if each has their own login AND always
                        uses it. Asking directly costs one tap, works under a shared login, and is
                        recorded even when consent is refused -- a refusal is data, and which
                        enumerator collected it is part of that data. The two are kept side by side
                        on purpose: `enum_id != _submitted_by` is a data-quality flag (wrong name
                        tapped, or a device signed in as someone else), which neither alone can give.
  interview_date,
  interview_duration_min -> dropped; replaced by standard XLSForm `start`/`end` meta questions
                             (Kobo auto-timestamps these); duration = end-start, computed in Stata
  dur_tasks_min      -> dropped; timing a sub-block needs extra mid-form calculate fields for
                        marginal value, left out to keep the form simple (documented limitation)
  gps_lat / gps_lon  -> merged into one `background-geopoint` field (`gps_location`): captured
                        silently the moment consent is given, no enumerator interaction, no
                        separate question shown on screen. Kobo splits it into
                        _geolocation / latitude / longitude / altitude / accuracy on export
  location_cluster   -> dropped 2026-09-24; the silent background-geopoint already records the
                        site, and health_access_tier is banded from latitude in Stata instead
  interview_lang, consent -> real select_one questions, unchanged

Skip logic: dictionary.py's `skip` field is free English text (not machine-parseable), so the
relevant-column expressions below are hand-built from the actual variable coding, not parsed
from that text.
"""
import os
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, HERE)
from dictionary import ROWS, LSETS, MODULES
from translations_hi import HI, HI_LSETS

OUT = os.path.join(HERE, "Kedarnath_final_kobo.xlsx")

# paradata items dropped in favour of a Kobo-native equivalent (see module docstring)
DROP_PARADATA = {"resp_id", "interview_date", "interview_duration_min", "dur_tasks_min", "gps_lat", "gps_lon"}

TYPE_MAP = {"num": "decimal", "count": "integer", "money": "integer"}

# hand-built relevant expressions -- see module docstring on why these aren't auto-parsed
#
# Apablaza Appendix 2 Q5 routes its eleven categories three different ways, so Module K needs two
# gates, not one:
#   K_WORKING (codes 1-3)  -- currently working: the whole job-quality block
#   K_TAIL    (codes 1-7)  -- adds studying / in-training / retired / unpaid-care, which Apablaza
#                             sends straight to Q21 (would you like to work more)
#   code 8 (unemployed, actively seeking) is routed by Apablaza to the Q22/Q23 pair directly, so it
#   is OR-ed into those two items rather than into either gate above.
#   codes 9-11 (sick or disabled / inactive / does not know) end the module.
K_WORKING = "${job_situation} <= 3"
K_TAIL = "${job_situation} <= 7"
K_SEEKING = "${job_situation} = 8"
RELEVANT = {
    "n_children_out_school": "${n_children_6_14} > 0",
    "main_income_earner": "${n_earners} > 1",
    "prev_occ": "${prev_occ_change} = 1",
    "prev_occ_reason": "${prev_occ_change} = 1",
    "other_activity_types": "${n_other_activities} > 0",
    "other_activity_income_pm": "${n_other_activities} > 0",
    "prev_occ": "${prev_occ_change} = 1",
    "training_type": "${training_received} = 1",
    "years_schooling": "${knows_years_schooling} = 1",
    "education_level_cat": "${knows_years_schooling} = 0",
    "migration_referral": "${origin} != 1",
    "employer_type": K_WORKING,
    "job_permanence": K_WORKING,
    "contract_status": f"({K_WORKING}) and (${{employment_type}} = 3 or ${{employment_type}} = 4)",
    "workplace_registered": K_WORKING,
    "pension_contrib": K_WORKING,
    "work_health_ins": K_WORKING,
    "leave_rights": K_WORKING,
    "injured_ever": K_WORKING,
    "workplace_injury_12m": K_WORKING,
    "wants_more_work": K_TAIL,
    "more_hours_day": f"${{wants_more_work}} = 1 or {K_SEEKING}",
    "months_looked_for_work": f"${{calc_months_no_work}} > 0 or {K_SEEKING}",
    "income_annual_total": "${knows_monthly_income} = 0",
    "pct_income_yatra": "${knows_monthly_income} = 0",
    "drove_twowheeler": "${tk_drive} = 1 or ${tk_drive} = 2",
    "drove_car": "${tk_drive} = 1 or ${tk_drive} = 2",
    "drove_heavy": "${tk_drive} = 1 or ${tk_drive} = 2",
    "morbidity_coping_15d": "${morbidity_15d} = 1",
    "morbidity_cost_15d": "${morbidity_15d} = 1",
    "usual_residence_differs": "${origin} != 1",
    "native_language_other": "${native_language} = 96 or ${native_language} = 97",
    "has_jandhan_account": "${has_bank_account} = 1",
    "credit_source": "${took_loan_12m} = 1",
    "loan_amount": "${took_loan_12m} = 1",
    "loan_interest_per100_pm": "${pays_interest} = 1",
    "loan_against_asset": "${took_loan_12m} = 1",
    "pays_interest": "${took_loan_12m} = 1",
    "loan_collateral": "${loan_against_asset} = 1",
    "has_crop_insurance": "${land_cultivable_acres} > 0",
    "govt_scheme_which": "${govt_scheme_beneficiary} = 1",
    "work_equipment_detail": "${owns_work_equipment} = 1",
    "migration_referral_other": "${migration_referral} = 7",
    "remit_mode": "${remit_out_yatra_pm} > 0 or ${remit_out_offseason_pm} > 0",
    "meal_spend_day_self": "${cooks_own_meals_here} = 2 or ${cooks_own_meals_here} = 3",
    "training_type_other": "${training_type} = 9",
    "shock_coping": "count-selected(${distress_event_last365d}) > 0",
    "anc_4_visits": "${birth_last_5y} = 1",
    "skilled_birth_attendant": "${birth_last_5y} = 1",
    "cons_staples_offseason_pm": "${spend_differs_by_season} = 1",
    "cons_perishables_offseason_pm": "${spend_differs_by_season} = 1",
    "cons_food_own_offseason_pm": "${spend_differs_by_season} = 1",
    "cons_food_out_offseason_pm": "${spend_differs_by_season} = 1",
    "cons_packaged_food_offseason_pm": "${spend_differs_by_season} = 1",
    "cons_pan_tobacco_offseason_pm": "${spend_differs_by_season} = 1",
    "cons_fuel_offseason_pm": "${spend_differs_by_season} = 1",
    "cons_routine_misc_offseason_pm": "${spend_differs_by_season} = 1",
    "cons_transport_comm_offseason_pm": "${spend_differs_by_season} = 1",
    "cons_rent_offseason_pm": "${spend_differs_by_season} = 1",
    "cons_med_nonhosp_offseason_pm": "${spend_differs_by_season} = 1",
    "water_fetch_minutes": "${water_on_premises} = 0",
    "water_fetched_by": "${water_on_premises} = 0",
    "hours_day_offseason": "${calc_offseason_work} > 0",
    "days_week_offseason": "${calc_offseason_work} > 0",
}
for _n in range(1, 13):
    # two conditions: the respondent took the month-by-month route at all, AND that month was worked
    RELEVANT[f"income_m{_n}"] = f"${{knows_monthly_income}} = 1 and ${{status_m{_n}}} != 8"

# a few cheap, high-value range constraints (kept short on purpose -- not every item)
CONSTRAINT = {
    "age": (". >= 10 and . <= 90", "Age must be between 10 and 90."),
    "hours_day_yatra": (". >= 1 and . <= 18", "Hours a day must be between 1 and 18."),
    "days_week_yatra": (". >= 1 and . <= 7", "Days a week must be between 1 and 7."),
    "hhsize": (". >= 1 and . <= 30", "Household size must be between 1 and 30."),
    "pct_income_yatra": (". >= 0 and . <= 100", "Must be between 0 and 100 out of every 100 rupees."),
    "n_other_activities": (". >= 0 and . <= 6", "Must be between 0 and 6."),
    "hours_day_offseason": (". >= 1 and . <= 18", "Hours a day must be between 1 and 18."),
    "days_week_offseason": (". >= 1 and . <= 7", "Days a week must be between 1 and 7."),
    "water_fetch_minutes": (". >= 0 and . <= 300", "Minutes must be between 0 and 300."),
    # Cross-field constraints. These were previously asserted only in the Stata build, which meant
    # the build HALTED on data the form was perfectly happy to accept. Enforcing them at entry, where
    # the enumerator can still ask again, is the right place.
    "n_health_insured": (". >= 0 and . <= ${hhsize}", "Cannot be more than the number of people in the household."),
    "n_life_insured": (". >= 0 and . <= ${hhsize}", "Cannot be more than the number of people in the household."),
    "n_can_transact_online": (". >= 0 and . <= ${hhsize}", "Cannot be more than the number of people in the household."),
    "n_earners": (". >= 1 and . <= ${hhsize}", "Cannot be more than the number of people in the household."),
    "n_children_u15": (". >= 0 and . <= ${hhsize} - 1", "Cannot be more than the household size minus the respondent."),
    "n_children_6_14": (". >= 0 and . <= ${n_children_u15}", "Cannot be more than the number of children under 15."),
    "n_children_out_school": (". >= 0 and . <= ${n_children_6_14}", "Cannot be more than the number of children aged 6 to 14."),
}
for _n in ["cope_less_pref_food", "cope_borrow_food", "cope_reduce_meals",
           "cope_reduce_portion", "cope_restrict_adult"]:
    CONSTRAINT[_n + "_yatra_wk"] = (". >= 0 and . <= 7", "Must be between 0 and 7 days.")
    CONSTRAINT[_n + "_offseason_wk"] = (". >= 0 and . <= 7", "Must be between 0 and 7 days.")

CMSG_HI = {
    "age": "उम्र 10 से 90 के बीच होनी चाहिए।",
    "hours_day_yatra": "दिन के घंटे 1 से 18 के बीच होने चाहिए।",
    "days_week_yatra": "हफ़्ते के दिन 1 से 7 के बीच होने चाहिए।",
    "hhsize": "घर के लोग 1 से 30 के बीच होने चाहिए।",
    "pct_income_yatra": "हर 100 रुपये में से 0 से 100 के बीच होना चाहिए।",
    "n_other_activities": "0 से 6 के बीच होना चाहिए।",
    "water_fetch_minutes": "मिनट 0 से 300 के बीच होने चाहिए।",
    "n_health_insured": "घर के लोगों की संख्या से ज़्यादा नहीं हो सकता।",
    "n_life_insured": "घर के लोगों की संख्या से ज़्यादा नहीं हो सकता।",
    "n_can_transact_online": "घर के लोगों की संख्या से ज़्यादा नहीं हो सकता।",
    "n_earners": "घर के लोगों की संख्या से ज़्यादा नहीं हो सकता।",
    "n_children_u15": "घर के लोगों में से आपको छोड़कर, उससे ज़्यादा नहीं हो सकता।",
    "n_children_6_14": "15 साल से छोटे बच्चों से ज़्यादा नहीं हो सकता।",
    "n_children_out_school": "6 से 14 साल के बच्चों से ज़्यादा नहीं हो सकता।",
    "days_week_offseason": "हफ़्ते के दिन 1 से 7 के बीच होने चाहिए।",
    "hours_day_offseason": "दिन के घंटे 1 से 18 के बीच होने चाहिए।",
}
for _n in ["cope_less_pref_food", "cope_borrow_food", "cope_reduce_meals",
           "cope_reduce_portion", "cope_restrict_adult"]:
    CMSG_HI[_n + "_yatra_wk"] = "0 से 7 दिन के बीच होना चाहिए।"
    CMSG_HI[_n + "_offseason_wk"] = "0 से 7 दिन के बीच होना चाहिए।"

MODULE_TITLE = {m[0]: m[1] for m in MODULES}
used_lsets = {r["lset"] for r in ROWS if r["origin"] in ("asked", "paradata") and r["name"] not in DROP_PARADATA and r["lset"]}

survey_rows = []   # (type, name, label, required, relevant, constraint, constraint_message, calculation, trigger)

def add(type_, name, label, required="", relevant="", constraint="", constraint_msg="", calc="", trigger=""):
    survey_rows.append((type_, name, label, required, relevant, constraint, constraint_msg, calc, trigger))

def xlsform_type(r):
    """kind 'multi' -> select_multiple (Kobo exports a space-separated string plus one binary column
    per choice); any other row carrying an lset -> select_one; otherwise fall back on TYPE_MAP, whose
    default is a plain text box (which is what the verbatim occupation questions want)."""
    if r["kind"] == "multi":
        return f"select_multiple {r['lset']}"
    return f"select_one {r['lset']}" if r["lset"] else TYPE_MAP.get(r["kind"], "text")

# ---- form-level metadata (Kobo standard audit fields) --------------------------------------
add("start", "start", "start")
add("end", "end", "end")

# ---- Module P: consent gate first, then the paradata items that stay real questions --------
p_rows = [r for r in ROWS if r["module"] == "P" and r["name"] not in DROP_PARADATA]
# enumerator first: set before approaching anyone, and captured even if consent is then refused
enum_row = next(r for r in p_rows if r["name"] == "enum_id")
add("select_one enum", "enum_id", enum_row["question"], required="yes")
consent_row = next(r for r in p_rows if r["name"] == "consent")
add("select_one yn", "consent", consent_row["question"], required="yes")
# background-geopoint: silent capture, no on-screen question; fires once consent is answered
add("background-geopoint", "gps_location", "GPS location of the interview (captured silently).", trigger="${consent}")
for r in p_rows:
    if r["name"] in ("consent", "enum_id"):
        continue
    add(xlsform_type(r), r["name"], r["question"], required="yes")

# ---- everything else is gated on consent = yes ----------------------------------------------
add("begin_group", "main_survey", "Main survey", relevant="${consent} = 1")

# hidden calculate needed by the weeks_looked_for_work skip rule (months_no_work isn't a form
# field -- it's built in Stata from status_m1..12 -- so it needs its own in-form copy here)
MONTHS_NO_WORK_CALC = " + ".join(f"if(${{status_m{n}}}=8,1,0)" for n in range(1, 13))
# second hidden calculate: months of OTHER paid work (calendar codes 2-7). Gates the off-season
# hours pair, which must not be asked of someone whose non-Yatra months are all idle.
OFFSEASON_WORK_CALC = " + ".join(
    f"if(${{status_m{n}}}>=2 and ${{status_m{n}}}<=7,1,0)" for n in range(1, 13))

modules_in_order = [m[0] for m in MODULES if m[0] != "P"]
for mod in modules_in_order:
    mod_rows = [r for r in ROWS if r["module"] == mod and r["origin"] == "asked"]
    if not mod_rows:
        continue
    add("begin_group", f"grp_{mod}", f"Module {mod}: {MODULE_TITLE[mod]}")
    for r in mod_rows:
        name = r["name"]
        type_ = xlsform_type(r)
        relevant = RELEVANT.get(name, "")
        constraint, cmsg = CONSTRAINT.get(name, ("", ""))
        # a dictionary skip note ending "may be left blank" marks a genuinely optional field --
        # usually a verbatim "other, specify". Forcing those would make enumerators invent answers.
        req = "" if "may be left blank" in r["skip"] else "yes"
        add(type_, name, r["question"], required=req, relevant=relevant, constraint=constraint, constraint_msg=cmsg)
        if name == "status_m12":   # last month of the calendar -> insert the hidden calculate right after
            add("calculate", "calc_months_no_work", "months with no paid work (hidden)", calc=MONTHS_NO_WORK_CALC)
            add("calculate", "calc_offseason_work", "months of other paid work (hidden)", calc=OFFSEASON_WORK_CALC)
    add("end_group", "", "")

add("end_group", "", "")

# ---- write the workbook ----------------------------------------------------------------------
wb = openpyxl.Workbook()
ws_survey = wb.active
ws_survey.title = "survey"
ws_survey.append(["type", "name", "label::English (en)", "label::हिन्दी (hi)", "required",
                  "relevant", "constraint", "constraint_message::English (en)", "constraint_message::हिन्दी (hi)",
                  "calculation", "trigger"])
_missing_hi = []
for row in survey_rows:
    type_, name, label = row[0], row[1], row[2]
    hi = HI.get(name, "")
    # groups, the consent gate and the hidden calculates carry their own Hindi; real questions must
    # have a translation or the bilingual form would silently fall back to English mid-interview.
    if not hi and type_ not in ("begin_group", "end_group", "calculate", "start", "end",
                                "background-geopoint") and name:
        _missing_hi.append(name)
    r3 = list(row[3:])
    ws_survey.append([type_, name, label, hi or label] + r3[:3] + [r3[3], CMSG_HI.get(name, r3[3])] + r3[4:])

ws_choices = wb.create_sheet("choices")
ws_choices.append(["list_name", "name", "label::English (en)", "label::हिन्दी (hi)"])
for lset in sorted(used_lsets):
    hi_set = HI_LSETS.get(lset, {})
    if not hi_set:
        _missing_hi.append(f"[choices] {lset}")
    for code, label in LSETS[lset].items():
        ws_choices.append([lset, code, label, hi_set.get(code, label)])
        if code not in hi_set:
            _missing_hi.append(f"[choice] {lset}/{code}")

ws_settings = wb.create_sheet("settings")
ws_settings.append(["form_title", "form_id", "version", "default_language"])
ws_settings.append(["Kedarnath Yatra Worker Survey - Vulnerability to Poverty (v2)", "kedarnath_vtp_v2", "2", "हिन्दी (hi)"])

wb.save(OUT)
if _missing_hi:
    print(f"  !! {len(_missing_hi)} item(s) with no Hindi:", ", ".join(_missing_hi[:15]))
else:
    print("  Hindi: complete for every question and every choice")
n_fields = sum(1 for r in survey_rows if r[0] not in ("begin_group", "end_group"))
n_choice_rows = sum(len(LSETS[l]) for l in used_lsets)
print(f"{OUT}\n{n_fields} survey rows (incl. start/end/calc), {len(used_lsets)} choice lists ({n_choice_rows} choice rows)")
