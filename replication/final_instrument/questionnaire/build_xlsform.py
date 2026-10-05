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
from dictionary import ROWS, LSETS, MODULES, INTROS, HINTS, CONSENT_SCRIPT, BUILD
from translations_hi import HI, HI_LSETS, INTROS_HI, HINTS_HI, CONSENT_SCRIPT_HI

# The module introduction notes are looked up by row name like any other label, so register their
# Hindi under the same key the note row will carry.
HI.update({f"intro_{_c}": _t for _c, _t in INTROS_HI.items()})
HI["consent_script"] = CONSENT_SCRIPT_HI

OUT = os.path.join(HERE, "Kedarnath_final_kobo.xlsx")

# paradata items dropped in favour of a Kobo-native equivalent (see module docstring)
DROP_PARADATA = {"resp_id", "interview_date", "interview_duration_min", "dur_tasks_min", "gps_lat", "gps_lon", "gps_accuracy_m", "gps_fix_s", "gps_error"}

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
RELEVANT = {
    # Refusals only (consent = 0). Written 2026-10-03 with the refusal record.
    "obs_environment": "${consent} = 0",
    "home_state": "${origin} = 3",
    "came_here_reason_other": "${came_here_reason} = 8",
    # Only the OUTWARD off-season amount. A respondent who goes home at closure is living with the
    # people he would be remitting to, so the question has no referent and his truthful 0 is
    # indistinguishable from a migrant who genuinely sends nothing. Inward is deliberately not
    # gated: money can still arrive from someone else working away.
    "remit_out_offseason_pm": "${remit_differs_by_season} = 1",
    "remit_in_offseason_pm": "${remit_differs_by_season} = 1",
    # Module J names the Gaurikund-Kedarnath ropeway, so it is asked only on that route. A Hemkund
    # respondent was being read a question about a proposal that does not concern him. If the Hemkund
    # route gets its own ropeway question later it needs its own wording and its own gate, not this
    # one widened -- the two proposals are different projects.
    "earnings_range": "not(${income_annual_total} > 0)",
    "wage_employer": "${employment_type} = 3 or ${employment_type} = 4",
    "land_cultivable_acres": "${land_unit} != 5",
    "main_income_earner": "${n_earners} > 1",
    "prev_occ": "${prev_occ_change} = 1",
    "prev_occ_reason": "${prev_occ_change} = 1",
    "prev_occ": "${prev_occ_change} = 1",
    "years_schooling": "${knows_years_schooling} = 1",
    "education_level_cat": "${knows_years_schooling} = 0",
    "contract_status": "${employment_type} = 3 or ${employment_type} = 4",
    # Gated to WAGE WORKERS as of 2026-10-01, the same way contract_status already was. All three ask
    # about something an employer provides -- a pension deduction, insurance through work, paid leave --
    # and an own-account pony owner has no employer. He was being asked all three.
    "pension_contrib": "${employment_type} = 3 or ${employment_type} = 4",
    "work_health_ins": "${employment_type} = 3 or ${employment_type} = 4",
    "leave_rights": "${employment_type} = 3 or ${employment_type} = 4",
    # Added 2026-10-03 for the weighted employment table. All are asked of working respondents only,
    # the same as every other job-quality item; the employment-table indicators are blank for anyone
    # they were not asked of rather than being scored as secure.
    "more_hours_day": "${wants_more_work} = 1",
    "months_looked_for_work": "${months_no_paid_work} > 0",
    "pct_income_yatra": "${income_annual_total} > 0",
    "drove_twowheeler": "${tk_drive} = 1 or ${tk_drive} = 2",
    "drove_car": "${tk_drive} = 1 or ${tk_drive} = 2",
    "drove_heavy": "${tk_drive} = 1 or ${tk_drive} = 2",
    "morbidity_coping_15d": "${morbidity_15d} = 1",
    "morbidity_cost_15d": "${morbidity_15d} = 1",
    # Module D. NOT gated on origin: the pilot found 11 of 20 seasonal movers inside this district,
    # so an origin gate would skip most of the people who move. Only the two genuinely
    # origin-specific items (why you first came) and the two verbatim follow-ups are gated.
    "years_coming_here": "${resp_returns_at_closure} = 1",
    "came_here_reason": "${origin} != 1",
    "closure_work_detail": "${worked_away_in_closure} = 1",
    "native_language_other": "${native_language} = 96 or ${native_language} = 97",
    "credit_source": "${took_loan_12m} = 1",
    "loan_purpose": "${took_loan_12m} = 1",
    "loan_amount_borrowed": "${took_loan_12m} = 1",
    "loan_amount": "${took_loan_12m} = 1",
    "loan_interest_per100_pm": "${pays_interest} = 1",
    "pays_interest": "${took_loan_12m} = 1",
    "loan_collateral": "${took_loan_12m} = 1",
    "has_crop_insurance": "${land_cultivable_acres} > 0",
    "govt_schemes_detail": "${govt_any_benefit} = 1",
    "shock_work_lost_weeks": "not(selected(${distress_event_last365d}, '9')) and count-selected(${distress_event_last365d}) > 0",
    "shock_money_spent": "not(selected(${distress_event_last365d}, '9')) and count-selected(${distress_event_last365d}) > 0",
    # The respondent is himself a household member aged 10 or over, so his own six years settle the
    # household indicator by entailment. The bracket route can only settle it at "completed
    # secondary or higher": "completed primary but not secondary" spans 5 to 9 years and straddles
    # the six-year threshold, so it does not, and the question is still asked. Written as two
    # disjoint branches rather than one expression over both variables, because only one of the two
    # is ever answered and a comparison against the blank one must not be what decides the gate.
    "any_member_6yr_schooling":
        "${knows_years_schooling} = 1 and ${years_schooling} < 6"
        " or ${knows_years_schooling} = 0 and ${education_level_cat} != 4",
    "shock_month": "not(selected(${distress_event_last365d}, '9')) and count-selected(${distress_event_last365d}) > 0",
    "work_equipment_detail": "${owns_work_equipment} = 1",
    "migration_referral_other": "${migration_referral} = 7",
    "remit_mode": "${remit_out_yatra_pm} > 0 or ${remit_out_offseason_pm} > 0",
    "shock_coping": "not(selected(${distress_event_last365d}, '9')) and count-selected(${distress_event_last365d}) > 0",
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
    "hours_day_offseason": "12 - ${months_worked_yatra} - ${months_no_paid_work} > 0",
    "days_week_offseason": "12 - ${months_worked_yatra} - ${months_no_paid_work} > 0",
}

# a few cheap, high-value range constraints (kept short on purpose -- not every item)
CONSTRAINT = {
    # Code 9 is "nothing of this kind happened" -- the escape option on a required check-all. Ticking
    # it alongside a real shock is a contradiction, so the form refuses it rather than letting the
    # build flag it afterwards. Enforceable in XLSForm and in the web form alike, which keeps the two
    # saying the same thing.
    # Coping code 6 is "paid it out of normal earnings, nothing given up" -- the explicit NO-coping
    # answer, split out of the old "did nothing/other" box. Ticking it beside borrowing or selling
    # is a contradiction in exactly the way code 9 is on the shock list, and replaces the scheme
    # exclusivity rule that went when the scheme check-all became a yes/no plus free text.
    "shock_coping": ("not(selected(., '6') and count-selected(.) > 1)",
                     "'Paid it out of normal earnings' cannot be ticked with another answer. Choose one or the other."),
    "distress_event_last365d": ("not(selected(., '9') and count-selected(.) > 1)",
                                "'Nothing of this kind happened' cannot be ticked with a shock. Choose one or the other."),
    "age": (". >= 10 and . <= 90", "Age must be between 10 and 90."),
    # ---- caught by the stress test: values the form accepted that cannot be true ----------------
    # Money and land cannot be negative. Obvious, and absent until a reviewer typed a minus sign.
    "land_cultivable_acres": (". >= 0", "Land cannot be negative."),
    "loan_amount": (". >= 0", "An amount cannot be negative."),
    "loan_amount_borrowed": (". >= 0", "An amount cannot be negative."),
    "shock_money_spent": (". >= 0", "An amount cannot be negative."),
    # A year has 52 weeks and the shock sits inside a 12-month recall.
    "shock_work_lost_weeks": (". >= 0 and . <= 52", "Weeks of work lost must be between 0 and 52."),
    "other_activity_income_pm": (". >= 0", "Earnings cannot be negative."),
    # Schooling cannot exceed a life. Four is the earliest a child starts class 1 here.
    "years_schooling": (". >= 0 and . <= ${age} - 4",
                        "Years of schooling cannot be more than the respondent's age allows."),
    # Nor can Yatra seasons. Ten is the youngest this instrument will record as working.
    "years_current_job": (". >= 0 and . <= ${age} - 10",
                            "More Yatra seasons than the respondent's age allows."),
    # Extra hours wanted, on top of hours already worked, cannot exceed a day.
    "more_hours_day": (". >= 0 and . + ${hours_day_yatra} <= 18",
                       "Hours wanted plus hours already worked cannot exceed 18 in a day."),
    "hours_day_yatra": (". >= 1 and . <= 18", "Hours a day must be between 1 and 18."),
    "days_week_yatra": (". >= 1 and . <= 7", "Days a week must be between 1 and 7."),
    "hhsize": (". >= 1 and . <= 30", "Household size must be between 1 and 30."),
    "pct_income_yatra": (". >= 0 and . <= 100", "Must be between 0 and 100 out of every 100 rupees."),
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
    # Two disjoint bands now, so the pair is constrained against the HOUSEHOLD rather than against
    # each other: under-6 plus 6-to-14 cannot exceed the household size minus the respondent. The
    # old pair constrained 6-to-14 <= under-15, which let a respondent report more children than he
    # had household members at all, and needed a data-quality flag to catch it afterwards.
    "n_children_u6": (". >= 0 and . <= ${hhsize} - 1", "Cannot be more than the household size minus the respondent."),
    "n_children_6_14": (". >= 0 and . + ${n_children_u6} <= ${hhsize} - 1",
                        "The two groups of children together cannot exceed the household size minus the respondent."),
}

# the three month counts, which replaced the twelve-cell calendar, and the new household counts
CONSTRAINT["months_worked_yatra"] = (". >= 0 and . <= 12", "Must be between 0 and 12 months.")
CONSTRAINT["months_no_paid_work"] = (". >= 0 and . + ${months_worked_yatra} <= 12",
    "The Yatra months and the months with no work cannot add up to more than 12.")
CONSTRAINT["n_hh_same_business"] = (". >= 0 and . <= ${hhsize}",
    "Cannot be more than the number of people in the household.")
CONSTRAINT["employers_in_season"] = (". >= 1 and . <= 30", "Must be between 1 and 30.")
CONSTRAINT["n_children_in_school"] = (". >= 0 and . <= ${n_children_6_14}",
    "Cannot be more than the number of children aged 6 to 14.")
CONSTRAINT["years_current_job"] = (". >= 0 and . <= ${age} - 5",
    "More years in this work than the respondent's age allows.")

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
    "n_children_u6": "घर के लोगों में से आपको छोड़कर, उससे ज़्यादा नहीं हो सकता।",
    "n_children_6_14": "दोनों मिलाकर, घर के लोगों में से आपको छोड़कर, उससे ज़्यादा नहीं हो सकते।",
    "shock_work_lost_weeks": "हफ़्ते 0 से 52 के बीच होने चाहिए।",
    "n_children_out_school": "6 से 14 साल के बच्चों से ज़्यादा नहीं हो सकता।",
    "days_week_offseason": "हफ़्ते के दिन 1 से 7 के बीच होने चाहिए।",
    "months_worked_yatra": "0 से 12 महीने के बीच होना चाहिए।",
    "months_no_paid_work": "यात्रा के महीने और बिना काम के महीने मिलाकर 12 से ज़्यादा नहीं हो सकते।",
    "n_hh_same_business": "घर के लोगों की संख्या से ज़्यादा नहीं हो सकता।",
    "employers_in_season": "1 से 30 के बीच होना चाहिए।",
    "n_children_in_school": "6 से 14 साल के बच्चों से ज़्यादा नहीं हो सकता।",
    "years_current_job": "उम्र के हिसाब से इतने साल नहीं हो सकते।",
    "hours_day_offseason": "दिन के घंटे 1 से 18 के बीच होने चाहिए।",
}

# ---------------------------------------------------------------------------------------------
# Money bounds, added 2026-10-05 after the first field test. 32 of the 48 money questions had NO
# constraint at all -- the whole consumption module, all four remittance figures and the annual
# total -- and one interview came back with monthly perishables of Rs 33, transport of Rs 6,
# annual clothing of Rs 36 and a rent field reading "00", which together put the household at
# about Rs 137 per capita per month against a poverty line of 2,515. Every one of those values
# was accepted silently and would have reached the FGLS.
#
# The two food items get a FLOOR, because that is the failure that actually happened: a household
# of any size buys more than a couple of hundred rupees of cereals and pulses in a month, so a
# smaller figure is a typo or a different recall period, not a poor household. Everything else
# gets a ceiling only -- a zero is a real answer for rent, tobacco or hospital costs.
# Ceilings are deliberately absurd rather than merely unlikely: this is a hard block in the form,
# and the job of catching the merely-implausible belongs to the evening check, not to a dialog
# the enumerator has to argue with in front of the respondent.
_MONEY_BOUNDS = {
    "cons_staples":        (200, 60000,  "Cereals, pulses, sugar and salt for a whole month. Check the figure."),
    "cons_perishables":    (100, 60000,  "Milk, vegetables, fruit, egg or meat, oil and spices for a whole month. Check the figure."),
    "cons_food_own":       (0,   60000,  "Check the figure."),
    "cons_food_out":       (0,   60000,  "Check the figure."),
    "cons_fuel":           (0,   30000,  "Check the figure."),
    "cons_routine_misc":   (0,   30000,  "Check the figure."),
    "cons_transport_comm": (0,   30000,  "Check the figure."),
    "cons_rent":           (0,   60000,  "Check the figure."),
    "cons_med_nonhosp":    (0,   60000,  "Check the figure."),
    "cons_packaged_food":  (0,   30000,  "Check the figure."),
    "cons_pan_tobacco":    (0,   30000,  "Check the figure."),
}
for _b, (_lo, _hi, _msg) in _MONEY_BOUNDS.items():
    for _suf in ("_yatra_pm", "_offseason_pm"):
        CONSTRAINT[_b + _suf] = (". >= %d and . <= %d" % (_lo, _hi),
                                 "Must be between Rs %s and Rs %s a month. %s" % (_lo, _hi, _msg))
        CMSG_HI[_b + _suf] = "यह रकम महीने के %s से %s रुपये के बीच होनी चाहिए। आँकड़ा जाँच लें।" % (_lo, _hi)

_ANNUAL_BOUNDS = {
    "cons_clothing_12m":   (0, 500000),
    "cons_education_12m":  (0, 500000),
    "cons_medical_hosp_12m": (0, 1000000),
    "cons_durables_12m":   (0, 500000),
    "morbidity_cost_15d":  (0, 500000),
    "remit_out_yatra_pm":  (0, 300000),
    "remit_out_offseason_pm": (0, 300000),
    "remit_in_yatra_pm":   (0, 300000),
    "remit_in_offseason_pm": (0, 300000),
    "other_activity_income_pm": (0, 500000),
    "shock_money_spent":   (0, 2000000),
    "loan_amount_borrowed": (0, 5000000),
    "loan_amount":         (0, 5000000),
}
for _n, (_lo, _hi) in _ANNUAL_BOUNDS.items():
    CONSTRAINT[_n] = (". >= %d and . <= %d" % (_lo, _hi),
                      "Must be between Rs %s and Rs %s." % (_lo, _hi))
    CMSG_HI[_n] = "यह रकम %s से %s रुपये के बीच होनी चाहिए।" % (_lo, _hi)

# The annual earnings figure is now the ONLY earnings question, so it carries the whole income
# side of the study. A floor of Rs 1,000 a year rejects a per-month figure typed into an annual
# field, which is the error the field test made four times out of twelve in the old calendar.
CONSTRAINT["income_annual_total"] = (". >= 1000 and . <= 10000000",
    "Must be between Rs 1,000 and Rs 1 crore for the whole year. If they gave a monthly figure, multiply it.")
CMSG_HI["income_annual_total"] = "पूरे साल के लिए यह 1,000 से 1,00,00,000 रुपये के बीच होना चाहिए। अगर उन्होंने महीने का बताया है तो उसे गुणा करें।"

# The one numeric question that had no bound at all.
CONSTRAINT["loan_interest_per100_pm"] = (". >= 0 and . <= 50",
    "Interest must be between 0 and 50 rupees per hundred per month.")
CMSG_HI["loan_interest_per100_pm"] = "सौ रुपये पर महीने का ब्याज 0 से 50 रुपये के बीच होना चाहिए।"

CONSTRAINT["years_coming_here"] = (". >= 0 and . <= ${age} - 5",
    "More years coming here than the respondent's age allows.")
CMSG_HI["years_coming_here"] = "उम्र के हिसाब से इतने साल नहीं हो सकते।"
CONSTRAINT["months_looked_for_work"] = (". >= 0 and . <= 12", "Must be between 0 and 12 months.")
CMSG_HI["months_looked_for_work"] = "0 से 12 महीने के बीच होना चाहिए।"

# 18 hours a day was the old ceiling and the field test used all of it -- one respondent at 18 x 7
# gives 126 hours a week, which then drives Apablaza's excessive-hours limb off the ceiling rather
# than off the work. 16 still admits a dhaba open from dawn to midnight.
CONSTRAINT["hours_day_yatra"] = (". >= 1 and . <= 16", "Hours a day must be between 1 and 16.")
CONSTRAINT["hours_day_offseason"] = (". >= 1 and . <= 16", "Hours a day must be between 1 and 16.")
CMSG_HI["hours_day_yatra"] = "दिन के घंटे 1 से 16 के बीच होने चाहिए।"
CMSG_HI["hours_day_offseason"] = "दिन के घंटे 1 से 16 के बीच होने चाहिए।"
CONSTRAINT["more_hours_day"] = (". >= 0 and . + ${hours_day_yatra} <= 16",
    "Hours wanted plus hours already worked cannot exceed 16 in a day.")
CMSG_HI["more_hours_day"] = "जो घंटे वे चाहते हैं और जो पहले से काम करते हैं, मिलाकर दिन में 16 से ज़्यादा नहीं हो सकते।"

# choice_filter: drop options from a list depending on an earlier answer. Only one list needs it --
# other_activity_types shares the 14-option occupation list with `occupation`, so without this a pony
# owner is offered "Pony/mule owner" again as a SECOND activity. The filter compares against a `code`
# column added to the choices sheet, which is XLSForm's mechanism for exactly this.
CHOICE_FILTER = {
    # other_activity_types shares the 14-option occupation list with `occupation`, so without this a
    # pony owner is offered "Pony/mule owner" again as a second activity.
    "other_activity_types": "code != ${occupation}",
}

MODULE_TITLE = {m[0]: m[1] for m in MODULES}
used_lsets = {r["lset"] for r in ROWS if r["origin"] in ("asked", "paradata") and r["name"] not in DROP_PARADATA and r["lset"]}

survey_rows = []   # (type, name, label, required, relevant, constraint, constraint_message, calculation, trigger)

def add(type_, name, label, required="", relevant="", constraint="", constraint_msg="", calc="",
        trigger="", appearance=""):
    survey_rows.append((type_, name, label, required, relevant, constraint, constraint_msg, calc, trigger,
                        CHOICE_FILTER.get(name, ""), appearance))

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
# Refusal fields and the browser-written GPS fields are not asked of everyone, so they are handled
# below (refusal fields) or left to Kobo's own geopoint metadata (GPS fields).
REFUSAL_FIELDS = ("obs_environment",)
WEB_ONLY_GPS = ("gps_accuracy_m", "gps_fix_s", "gps_error")
p_rows = [r for r in ROWS if r["module"] == "P" and r["name"] not in DROP_PARADATA
          and r["name"] not in WEB_ONLY_GPS]
# enumerator first: set before approaching anyone, and captured even if consent is then refused
enum_row = next(r for r in p_rows if r["name"] == "enum_id")
add("select_one enum", "enum_id", enum_row["question"], required="yes")
# The consent script as a note directly above the question, so it is on screen when it is needed.
# A note, not a hint: our hint:: convention is labelled "do not read out", which is the opposite of
# what this block is for.
add("note", "consent_script", CONSENT_SCRIPT)
site_row = next(r for r in p_rows if r["name"] == "site")
add("select_one site", "site", site_row["question"], required="yes")
consent_row = next(r for r in p_rows if r["name"] == "consent")
add("select_one yn", "consent", consent_row["question"], required="yes")
# background-geopoint: silent capture, no on-screen question; fires once consent is answered
# Location only after consent is given. trigger="${consent}" fired on a refusal too, so the trigger is "= 1".
add("background-geopoint", "gps_location", "GPS location of the interview (captured silently).", trigger="${consent} = 1")
# form_build is a hidden CALCULATE carrying dictionary.BUILD, not a question. It reached this loop
# as an ordinary paradata row and came out as a REQUIRED TEXT FIELD labelled "Recorded
# automatically." -- an unanswerable required question that would have stopped the Kobo form dead,
# which is the exact failure the last field review hit. The web form always set it in code; this is
# the Kobo equivalent.
add("calculate", "form_build", "", calc="'%s'" % BUILD)
for r in p_rows:
    if r["name"] in ("consent", "enum_id", "site", "form_build"):
        continue
    if r["name"] in REFUSAL_FIELDS:
        # asked only when consent is refused, so outside the consent-gated survey group below
        add(xlsform_type(r), r["name"], r["question"], required="yes", relevant="${consent} = 0")
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
    # field-list = the whole module on one screen, matching the web form. One question per screen was
    # ~210 taps per interview before anyone had answered anything twice.
    add("begin_group", f"grp_{mod}", f"Module {mod}: {MODULE_TITLE[mod]}", appearance="field-list")
    # Read-aloud introduction, as an unrequired note ahead of the module's first question. A note
    # carries no value into the export, so this adds a screen the enumerator reads and nothing to
    # the data. It is not marked required: a note cannot be, and forcing a tap here would only add
    # one per module for no record of anything.
    if mod in INTROS:
        add("note", f"intro_{mod}", INTROS[mod])
    for r in mod_rows:
        name = r["name"]
        type_ = xlsform_type(r)
        relevant = RELEVANT.get(name, "")
        constraint, cmsg = CONSTRAINT.get(name, ("", ""))
        # a dictionary skip note ending "may be left blank" marks a genuinely optional field --
        # usually a verbatim "other, specify". Forcing those would make enumerators invent answers.
        # Case-insensitive: see the note on the same test in build_webform.py.
        req = "" if "may be left blank" in r["skip"].lower() else "yes"
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
# hint:: is the standard XLSForm column for text shown under the question and never read out. It is
# where an enumerator instruction belongs -- putting it in the label would have the enumerator read
# coding guidance aloud to the respondent.
ws_survey.append(["type", "name", "label::English (en)", "label::हिन्दी (hi)",
                  "hint::English (en)", "hint::हिन्दी (hi)", "required",
                  "relevant", "constraint", "constraint_message::English (en)", "constraint_message::हिन्दी (hi)",
                  "calculation", "trigger", "choice_filter", "appearance"])
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
    ws_survey.append([type_, name, label, hi or label,
                      HINTS.get(name, ""), HINTS_HI.get(name, HINTS.get(name, ""))]
                     + r3[:3] + [r3[3], CMSG_HI.get(name, r3[3])] + r3[4:])

ws_choices = wb.create_sheet("choices")
ws_choices.append(["list_name", "name", "label::English (en)", "label::हिन्दी (hi)", "code"])
for lset in sorted(used_lsets):
    hi_set = HI_LSETS.get(lset, {})
    if not hi_set:
        _missing_hi.append(f"[choices] {lset}")
    for code, label in LSETS[lset].items():
        # `code` duplicates `name` so a choice_filter has something to compare against; harmless on
        # every other list, and required on the one that filters.
        ws_choices.append([lset, code, label, hi_set.get(code, label), code])
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
