"""Single source of truth for the final Kedarnath survey instrument.
Every variable appears once: module, name, Stata label (<=80 chars), question wording, description,
type, value-label set, skip rule, literature source, origin (paradata / asked / constructed / synthetic).
The questionnaire PDF, the variable_dictionary.csv and the Stata label file are all built from this list."""

MODULES = [  # code, title, minutes (my estimate from item counts and read-aloud speed; to be timed in the pretest)
    ("P", "Cover page, consent and paradata", 1.5),
    ("A", "Respondent and household", 3.5),
    ("B", "Work, season and work history", 4.0),
    ("C", "Income and remittances", 3.0),
    ("D", "Migration", 1.5),
    ("E", "Household consumption", 6.0),
    ("F", "Housing, amenities and assets", 4.0),
    ("G", "Finance, insurance and schemes", 3.0),
    ("H", "Health", 2.5),
    ("I", "Shocks and coping", 1.5),
    ("J", "Ropeway", 1.0),
    ("K", "Job quality", 3.5),
    ("L", "Tasks and papers (short block)", 5.5),
]

LSETS = {
    "yn": {0: "No", 1: "Yes"},
    "sex": {0: "Male", 1: "Female"},
    "lang": {1: "Hindi", 2: "Garhwali", 3: "Nepali"},
    "enum": {1: "Enumerator 1", 2: "Enumerator 2", 3: "Enumerator 3", 4: "Enumerator 4"},
    "cluster": {1: "Gaurikund", 2: "Sonprayag", 3: "Guptkashi/Phata", 4: "Kedarnath town"},
    "social": {1: "Scheduled Caste", 2: "Scheduled Tribe", 3: "Other Backward Class", 4: "General", 5: "Other / not applicable"},
    "marital": {1: "Currently married", 2: "Never married", 3: "Widowed/divorced/separated"},
    "edu": {0: "No formal education", 1: "Primary (up to 5th)", 2: "Middle (up to 8th)", 3: "Secondary (up to 10th)",
            4: "Higher secondary (12th)", 5: "Graduate or above", 98: "Prefer not to say"},
    "occ": {1: "Pony worker", 2: "Pony business owner", 3: "Porter", 4: "Palki/dandi bearer", 5: "Shop worker", 6: "Shop owner",
            7: "Hotel/lodging worker", 8: "Hotel/lodging owner", 9: "Wage labourer", 10: "Driver", 11: "Dhaba/food-stall owner",
            12: "Guide", 13: "Other"},
    "emptype": {1: "Own-account (self-employed, no hired workers)", 2: "Employer/business owner (self-employed)",
                3: "Regular wage or salary", 4: "Casual wage labour"},
    "month": {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August",
              9: "September", 10: "October", 11: "November", 12: "December"},
    "offseason": {1: "No other work", 2: "Agriculture", 3: "Animal husbandry", 4: "Wage labour elsewhere",
                  5: "Migrated for work", 6: "Petty trade/other", 7: "Salaried job"},
    "prevreason": {1: "Better income", 2: "Lost the previous work", 3: "Family or seasonal reasons", 4: "Moved to this area", 5: "Other"},
    "trtype": {1: "Vocational/trade", 2: "Tourism/hospitality"},
    "origin": {1: "Local (same district)", 2: "Other Uttarakhand district", 3: "Other Indian state", 4: "Nepal"},
    "migreason": {1: "Employment", 2: "Family movement", 3: "Marriage", 4: "Displacement/other"},
    "floor": {1: "Mud/kaccha", 2: "Cement/mud-cement", 3: "Tile/mosaic/marble"},
    "roof": {1: "Thatch/wood/mud", 2: "Tin/GI sheet", 3: "Concrete/RCC"},
    "house": {1: "Kaccha", 2: "Semi-pucca", 3: "Pucca"},
    "water": {1: "Piped", 2: "Handpump/borewell", 3: "Other (spring/tanker)"},
    "digital": {0: "Never", 1: "Sometimes", 2: "Often"},
    "credit": {0: "No credit taken", 1: "Institutional (bank/co-op/SHG-linked)", 2: "Non-institutional (moneylender/relative)"},
    "insurance": {0: "None", 1: "Health", 2: "Life", 3: "Crop", 4: "More than one"},
    "distress": {0: "None", 1: "Major illness/death of earning member", 2: "Crop failure or livestock loss",
                 3: "Natural disaster damage", 4: "Business/asset loss"},
    "coping": {1: "Used savings", 2: "Borrowed money", 3: "Sold or pawned assets", 4: "Cut consumption",
               5: "Help from relatives/community", 6: "Did nothing/other"},
    "stance": {1: "Support", 2: "Neutral", 3: "Oppose", 98: "Don't know / prefer not to say"},
    "task3": {1: "Yes, regularly in my main Yatra work", 2: "Not in my main work, but done before elsewhere", 3: "Never done"},
    "tier": {1: "Poor", 2: "Moderate", 3: "Good"},
}

SRC_STD = "Standard household-survey item"
ROWS = []

def R(module, name, label, question, desc, kind, lset=None, skip="", source=SRC_STD, origin="asked", formula=""):
    assert len(label) <= 80, (name, len(label))
    ROWS.append(dict(module=module, name=name, label=label, question=question, desc=desc, kind=kind, lset=lset,
                     skip=skip, source=source, origin=origin, formula=formula))

# ------------------------------------------------------------------ P  cover and paradata
R("P", "resp_id", "Respondent ID", "Assigned by the tablet.", "Unique respondent number.", "id", origin="paradata", source="Design")
R("P", "enum_id", "Enumerator", "Selected by the enumerator at login.", "Which of the four enumerators did the interview.", "cat", "enum", origin="paradata", source="Design")
R("P", "interview_date", "Interview date", "Recorded automatically.", "Date of interview.", "date", origin="paradata", source="Design")
R("P", "location_cluster", "Interview site (Yatra-route cluster)", "Enumerator selects the site where the interview is held.", "One of four route clusters; also sets the health-access tier.", "cat", "cluster", origin="paradata", source="Design")
R("P", "interview_lang", "Language of interview", "Enumerator records the language used.", "Language in which the interview was carried out.", "cat", "lang", origin="paradata", source="Design")
R("P", "gps_lat", "GPS latitude of interview", "Recorded automatically.", "Latitude of the interview location.", "num", origin="paradata", source="Design")
R("P", "gps_lon", "GPS longitude of interview", "Recorded automatically.", "Longitude of the interview location.", "num", origin="paradata", source="Design")
R("P", "consent", "Respondent gave informed consent", "Read the consent script. Do you agree to take part? (1 yes, 0 no; stop if no)", "Consent given after the script was read.", "bin", "yn", origin="paradata", source="Design")
R("P", "interview_duration_min", "Interview length (minutes)", "Recorded automatically (start to end).", "Total interview time; the target is 45 minutes or less.", "num", origin="paradata", source="Design")
R("P", "dur_tasks_min", "Time spent on tasks block L (minutes)", "Recorded automatically (module timestamps).", "Time for the short task and papers block; tracks the burden of the transferability add-on.", "num", origin="paradata", source="Design")

# ------------------------------------------------------------------ A  respondent and household
R("A", "age", "Age in completed years", "How old are you? (completed years)", "Respondent age; 18 to 70 covered.", "num", source="Standard; sensitivity covariate in the VEP model (Azeem et al. 2016 structure)")
R("A", "female", "Female (1) or male (0)", "Record sex; ask if unsure: are you male or female?", "Sex of the respondent.", "bin", "sex")
R("A", "social_group", "Social group", "Which social group do you belong to? Show card: SC, ST, OBC, General.", "Caste category as reported.", "cat", "social", skip="Code 5 for non-Indian nationals")
R("A", "marital_status", "Marital status", "Are you currently married, never married, or widowed/divorced/separated?", "Marital status of the respondent.", "cat", "marital")
R("A", "education_level", "Highest level of school completed", "What is the highest level of school you completed? Show card. (98 if the respondent prefers not to say.)", "Highest completed schooling; feeds the MPI education indicator.", "cat", "edu", source="NITI Aayog National MPI (years of schooling); Chaudhuri et al. 2002 covariate")
R("A", "hhsize", "Household size (people eating from the same kitchen)", "How many people usually eat from the same kitchen as you, including you?", "Household size in the usual place of living. Aggregate count; no household roster.", "count", source="Chaudhuri et al. 2002; used to get per-capita consumption")
R("A", "n_earners", "Number of household members who earn money", "How many of them, including you, earn money?", "Earners in the household, including the respondent.", "count", source="Dependency measure used in VEP studies (Azeem et al. 2016)")
R("A", "n_children_6_14", "Household children aged 6 to 14", "How many of them are children aged 6 to 14?", "Count of school-age children.", "count", source="NITI Aayog National MPI school-attendance indicator")
R("A", "n_children_out_school", "Children aged 6 to 14 not attending school", "How many of these children do not go to school now?", "Count of school-age children not attending.", "count", skip="Ask only if n_children_6_14 > 0", source="NITI Aayog National MPI school-attendance indicator")

# ------------------------------------------------------------------ B  work, season, history
R("B", "occupation", "Main work in the Yatra season (13 groups)", "What is your main work during the Yatra season? Show card. Choose the closest group.", "Quota variable: 13 occupation groups.", "cat", "occ", source="Project quota design; palki/dandi treated as self-employed wage work")
R("B", "employment_type", "Employment status in main work (4 groups)", "In this main work, are you: working on your own account without hired workers; running a business with hired workers; a regular monthly wage-earner; or a daily/casual wage-earner?", "PLFS-style status: own-account, employer, regular wage, casual wage.", "cat", "emptype", source="PLFS / NSS employment status classification")
R("B", "years_in_yatra_work", "Years worked in Yatra work", "How many Yatra seasons have you worked in this kind of work?", "Experience in the Yatra economy.", "count", source="Chaudhuri et al. 2002 sensitivity covariate; Apablaza et al. 2026 stability domain")
R("B", "yatra_months", "Months the Yatra work lasts in a normal year", "In a normal year, for how many months does your Yatra work last?", "Length of the working season, 3 to 6 months.", "count")
R("B", "yatra_start_month", "Month the season started", "In which month did the Yatra season start for you last year?", "Start month of the working season.", "cat", "month")
R("B", "yatra_end_month", "Month the season ended", "In which month did it end?", "End month of the working season.", "cat", "month")
R("B", "hours_day_yatra", "Hours worked per day in the Yatra season", "In the Yatra season, on a working day, how many hours do you work in total?", "Usual daily hours, all jobs.", "count", source="Apablaza et al. 2026: hours (access and conditions domains)")
R("B", "days_week_yatra", "Days worked per week in the Yatra season", "How many days a week do you usually work in the season?", "Usual working days per week.", "count", source="Apablaza et al. 2026: hours (access and conditions domains)")
R("B", "offseason_primary", "Main activity when Yatra is closed", "What is your main way of earning or spending time when the Yatra is closed?", "Main off-season activity.", "cat", "offseason")
R("B", "offseason_months_worked", "Months of paid work outside the Yatra season", "In how many of the other months of the year do you earn any money?", "Off-season months with earnings (0 to 8).", "count", source="Replaces the 12-month status grid (see section 5 of the questionnaire document)")
R("B", "prev_occ_change", "Changed main kind of work in the last 10 years", "In the last ten years, did you change your main kind of work?", "Occupational change flag.", "bin", "yn", source="Occupational mobility check; job-history item")
R("B", "prev_occ", "Previous main work", "What was your previous main work? Show card.", "Occupation before the change.", "cat", "occ", skip="Ask only if prev_occ_change = 1", source="Gathmann and Schonberg 2010 (validate task distance with observed moves)")
R("B", "prev_occ_reason", "Main reason for changing work", "What was the main reason you changed?", "Reason for the last change.", "cat", "prevreason", skip="Ask only if prev_occ_change = 1", source="Job-history item")
R("B", "training_received", "Ever completed a training course or apprenticeship", "Have you ever completed a training course or apprenticeship, not counting school?", "Formal skills training received.", "bin", "yn", source="STEP module 2; Chaudhuri et al. 2002 adaptive-capacity covariate")
R("B", "training_type", "Type of training received", "What kind of course was it?", "Type of training.", "cat", "trtype", skip="Ask only if training_received = 1", source="STEP module 2")

# ------------------------------------------------------------------ C  income and remittances
R("C", "inc_yatra_pm", "Usual monthly earnings in Yatra months (Rs)", "In the Yatra season, how much do you usually earn in a month from all your work, after paying your costs (fodder, rent, goods, hired help)? (Rs)", "Net monthly earnings in the season; the seasonal calendar replaces 12 monthly income questions.", "money", source="Seasonal calendar; income seasonality as Exposure covariate (Azeem et al. 2016; Khandker 2012)")
R("C", "inc_offseason_pm", "Usual monthly earnings in off-season months worked (Rs)", "In the other months when you do earn, how much do you usually earn in a month? (Rs)", "Net monthly earnings in off-season months that were worked.", "money", skip="Ask only if offseason_months_worked > 0", source="Seasonal calendar")
R("C", "remittance_inward", "Money received from family or others, last 12 months (Rs)", "In the last 12 months, how much money in total did family or others send to you or your household? (Rs, 0 if none)", "Annual inward remittances.", "money", source="NSS 64th Round practice (amount); frequency dropped for length")
R("C", "remittance_outward", "Money sent to family elsewhere, last 12 months (Rs)", "In the last 12 months, how much money in total did you send to family or others living elsewhere? (Rs, 0 if none)", "Annual outward remittances.", "money", source="NSS 64th Round practice (amount); frequency dropped for length")

# ------------------------------------------------------------------ D  migration
R("D", "origin", "Place of permanent home", "Where is your permanent home?", "Origin of the respondent.", "cat", "origin", source="NSS migration classification")
R("D", "short_term_migrant_nss", "Away from usual home for work 15 days to 6 months a year", "Do you stay away from your usual home for work for between 15 days and 6 months in a year?", "NSS short-term migrant flag.", "bin", "yn", source="NSS 64th Round short-term migrant definition")
R("D", "migration_reason", "Main reason for coming here", "What was the main reason you came to live or work here?", "Reason for migration.", "cat", "migreason", skip="Ask only if origin is not 'Local'", source="NSS migration module")
R("D", "years_since_migration", "Years since first coming here", "How many years ago did you first come here?", "Years since migration.", "count", skip="Ask only if origin is not 'Local'", source="NSS migration module")

# ------------------------------------------------------------------ E  consumption
E_NOTE = "Report for the household's usual place of living, including home-produced items valued at market price."
R("E", "cons_food_30d", "Food spending, last 30 days (Rs)", "In the last 30 days, how much did your household spend on food: cereals, pulses, vegetables, milk, oil, sugar, tea, snacks and eating out? Include home-grown food at market value. (Rs)", "Household food spending. " + E_NOTE, "money", source="HCES/NSS-style consumption; welfare measure of Chaudhuri et al. 2002")
R("E", "cons_fuel_30d", "Fuel and light spending, last 30 days (Rs)", "In the last 30 days, how much on fuel and light: cooking fuel, firewood, electricity, candles/batteries? (Rs)", "Household fuel and light spending. " + E_NOTE, "money", source="HCES/NSS-style consumption")
R("E", "cons_routine_misc_30d", "Routine goods and services, last 30 days (Rs)", "In the last 30 days, how much on other regular items: soap, toiletries, local transport, phone recharge, entertainment, small repairs? (Rs)", "Household routine miscellaneous spending. " + E_NOTE, "money", source="HCES/NSS-style consumption")
R("E", "cons_rent_30d", "Rent paid, last 30 days (Rs)", "In the last 30 days, how much rent did your household pay for its home? (0 if owned)", "Household rent. " + E_NOTE, "money", source="HCES/NSS-style consumption")
R("E", "cons_clothing_12m", "Clothing and footwear spending, last 12 months (Rs)", "In the last 12 months, how much did your household spend on clothes and footwear? (Rs)", "Annual clothing spending; converted to monthly by dividing by 12.", "money", source="HCES/NSS-style consumption (longer recall for infrequent items)")
R("E", "cons_education_12m", "Education spending, last 12 months (Rs)", "In the last 12 months, how much on education: fees, books, uniforms, tuition? (Rs)", "Annual education spending.", "money", source="HCES/NSS-style consumption")
R("E", "cons_medical_12m", "Medical spending, last 12 months (Rs)", "In the last 12 months, how much on medical care for household members? (Rs)", "Annual medical spending as reported in the consumption list.", "money", source="HCES/NSS-style consumption")
R("E", "cons_durables_12m", "Durable goods spending, last 12 months (Rs)", "In the last 12 months, how much on durable goods: furniture, utensils, appliances, phone, bicycle or motorcycle parts? (Rs)", "Annual durables spending.", "money", source="HCES/NSS-style consumption")

# ------------------------------------------------------------------ F  housing and assets
R("F", "floor_material", "Main floor material", "Enumerator observes: main floor material.", "Observed floor material.", "cat", "floor", source="NITI Aayog National MPI housing indicator")
R("F", "roof_material", "Main roof material", "Enumerator observes: main roof material.", "Observed roof material.", "cat", "roof", source="NITI Aayog National MPI housing indicator")
R("F", "house_type", "House type (enumerator-coded)", "Enumerator codes the house as kaccha, semi-pucca or pucca from the floor, roof and walls.", "Observed house type; kaccha counts as deprived.", "cat", "house", source="NITI Aayog National MPI housing indicator")
R("F", "electricity", "Home has an electricity connection", "Does your home have an electricity connection?", "Electricity in the home.", "bin", "yn", source="NITI Aayog National MPI")
R("F", "toilet_facility", "Household has its own toilet", "Does your household have its own toilet or latrine?", "Own sanitation facility.", "bin", "yn", source="NITI Aayog National MPI sanitation indicator")
R("F", "drinking_water", "Main source of drinking water", "What is your main source of drinking water?", "Drinking-water source; 'spring/tanker' counts as deprived.", "cat", "water", source="NITI Aayog National MPI")
R("F", "cooking_fuel_lpg", "Cooks mainly with LPG", "Does your household cook mainly with LPG?", "Clean cooking fuel.", "bin", "yn", source="NITI Aayog National MPI cooking-fuel indicator")
R("F", "owns_tv", "Owns a television", "Does your household own: a television?", "Durable asset.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "owns_radio", "Owns a radio", "... a radio?", "Durable asset.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "owns_bicycle", "Owns a bicycle", "... a bicycle?", "Durable asset.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "owns_motorcycle", "Owns a motorcycle or scooter", "... a motorcycle or scooter?", "Durable asset.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "owns_car", "Owns a car", "... a car?", "Durable asset.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "owns_fridge", "Owns a refrigerator", "... a refrigerator?", "Durable asset.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "land_acres", "Agricultural land owned or cultivated (acres)", "How much agricultural land does your household own or cultivate, in acres? (0 if none)", "Land holding.", "num", source="Chaudhuri et al. 2002 asset covariate")
R("F", "livestock_count", "Cows, buffaloes or goats owned", "How many cows, buffaloes or goats does your household own?", "Livestock count.", "count", source="Chaudhuri et al. 2002 asset covariate")
R("F", "pony_count", "Ponies or mules owned", "How many ponies or mules do you own?", "Ponies owned (livelihood asset).", "count", source="Project design (pilot livelihood survey)")
R("F", "business_asset_owned", "Owns a shop, stall, vehicle or equipment used for earning", "Does your household own a shop, stall, vehicle or equipment that you use to earn?", "Productive asset.", "bin", "yn", source="Chaudhuri et al. 2002 asset covariate")

# ------------------------------------------------------------------ G  finance, insurance, schemes, phone
R("G", "has_bank_account", "Household has a bank account", "Does anyone in your household have a bank account?", "Bank account in the household.", "bin", "yn", source="NITI Aayog National MPI bank-account indicator; VEP adaptive-capacity covariate")
R("G", "has_jandhan_account", "Has a Jan Dhan account", "Is any of these a Jan Dhan account?", "Jan Dhan account.", "bin", "yn")
R("G", "credit_source", "Main source of any loan, last 12 months", "In the last 12 months, did you borrow money? If yes, who was the main lender?", "Credit access and its type.", "cat", "credit", source="VEP adaptive-capacity covariate (institutional credit)")
R("G", "insurance_coverage", "Type of insurance held", "Does anyone in your household have: health insurance, life insurance, crop insurance, or more than one?", "Insurance held.", "cat", "insurance")
R("G", "govt_scheme_beneficiary", "Received a government scheme benefit, last 12 months", "In the last 12 months, did your household receive benefits from any government scheme (for example ration, pension, cash transfer)?", "Scheme benefit received.", "bin", "yn")
R("G", "pension_coverage", "Covered by any pension scheme", "Are you covered by any pension scheme?", "Pension coverage of the respondent.", "bin", "yn", source="Apablaza et al. 2026 Table 3: conditions domain (no health insurance and no pension)")
R("G", "smartphone_owned", "Owns a smartphone", "Do you own a smartphone?", "Smartphone ownership.", "bin", "yn", source="VEP adaptive-capacity covariate; STEP digital items")
R("G", "digital_payment_use", "Uses digital payment (UPI)", "How often do you use UPI or another digital payment: never, sometimes, often?", "Digital payment use.", "cat", "digital")

# ------------------------------------------------------------------ H  health
R("H", "morbidity_15d", "Anyone ill in the last 15 days", "In the last 15 days, was anyone in your household ill?", "Illness in the last 15 days.", "bin", "yn", source="NSS health module (15-day recall)")
R("H", "hospitalization_365d", "Anyone admitted to hospital in the last 12 months", "In the last 12 months, was anyone in your household admitted to hospital overnight?", "Hospital admission.", "bin", "yn", source="NSS health module (365-day recall)")
R("H", "oope_amount", "Out-of-pocket health spending, last 12 months (Rs)", "In the last 12 months, how much did your household pay out of pocket for medical care? (Rs, 0 if none)", "Out-of-pocket health spending; reported separately from the consumption list, not added to it.", "money", source="NSS health module")
R("H", "health_insurance_covered", "Household covered by health insurance or a health scheme", "Is your household covered by any health insurance or health scheme (including government schemes)?", "Health cover, including scheme cover.", "bin", "yn", source="NITI Aayog National MPI health-insurance indicator (project version)")

# ------------------------------------------------------------------ I  shocks
R("I", "distress_event_last365d", "Main shock in the last 12 months", "In the last 12 months, did your household suffer any of these: serious illness or death of an earning member; crop failure or livestock loss; damage from a natural disaster; loss of business or assets? Record the most serious one.", "Main shock, one answer.", "cat", "distress", source="VEP exposure covariate (Azeem et al. 2016)")
R("I", "shock_coping", "Main way the household coped with the shock", "How did your household mainly cope with it? Show card.", "Main coping response.", "cat", "coping", skip="Ask only if a shock was reported", source="Coping strategies in VEP studies")

# ------------------------------------------------------------------ J  ropeway
R("J", "ropeway_stance", "View on the proposed Kedarnath ropeway", "A ropeway is proposed between Gaurikund and Kedarnath. Are you in favour, neutral, or against?", "Stated stance; no rating scale.", "cat", "stance", source="Project design")
R("J", "trek_dependent", "Main work is carrying or guiding on the trek", "Is your main Yatra work carrying, transporting or guiding people or goods on the Gaurikund to Kedarnath trek?", "Direct exposure flag (factual); not inferred from job title.", "bin", "yn", source="Project design (see tasks_module W4: exposure must be asked directly)")

# ------------------------------------------------------------------ K  job quality (Apablaza core)
K_SRC = "Apablaza et al. 2026, Table 3 (five-domain core)"
R("K", "wants_more_work", "Wanted more work in last 12 months and could not get it", "In the last 12 months, were there times when you wanted more work or more hours and could not find it?", "Involuntary underemployment or unemployment.", "bin", "yn", source=K_SRC + ": access domain")
R("K", "written_contract", "Has a written contract", "Do you have a written contract or appointment letter for this work?", "Written contract, wage workers only.", "bin", "yn", skip="Ask only if employment_type is 3 or 4 (wage workers)", source=K_SRC + ": security domain")
R("K", "work_registered", "Work is registered (union, board or trade licence)", "Is your work registered, for example with a union, the Yatra registration, or a trade or shop licence?", "Registration, self-employed workers only.", "bin", "yn", skip="Ask only if employment_type is 1 or 2 (self-employed)", source=K_SRC + ": security domain, self-employment analogue")
R("K", "hazard_exposed", "Regularly exposed to a physical hazard at work", "In your work, are you regularly exposed to any of these: carrying heavy loads on the steep trail; working at heights or on unprotected edges; handling large animals; long driving on hill roads; landslide or rockfall; extreme cold without shelter?", "Any red-list hazard.", "bin", "yn", source=K_SRC + ": conditions domain (red-list hazards)")
R("K", "injury_work_12m", "Injured or fell ill because of work, last 12 months", "In the last 12 months, were you injured or made ill by your work in a way that stopped you working for a day or more?", "Work injury or illness.", "bin", "yn", source=K_SRC + ": conditions domain")
R("K", "safety_equipment", "Uses protective equipment at work", "Do you have and use any protective equipment for this work (for example shoes, gloves, helmet, rain gear, harness)?", "Protective equipment.", "bin", "yn", skip="Ask only if hazard_exposed = 1", source=K_SRC + ": conditions domain (fallback: no equipment)")

# ------------------------------------------------------------------ L  tasks and papers (short block)
TASKS = [
 ("tk_load", "Load, unload, stack or count goods", "3", "Gathmann and Schonberg 2010; NCO 9333.0100 loader"),
 ("tk_drive", "Drive a motor vehicle", "7", "Spitz-Oener 2006 / STEP; NCO 8322.0100"),
 ("tk_engine", "Operate an engine or machine", "8", "Gathmann and Schonberg 2010; NCO 8343.1700 ropeway operator"),
 ("tk_electric", "Do electrical or wiring work", "10", "Spitz-Oener 2006; NCO 7411.0301 wireman"),
 ("tk_safety", "Check equipment or the route for safety", "12", "Gathmann and Schonberg 2010; NCO 8343.1700"),
 ("tk_sell", "Sell goods or services", "14", "Gathmann and Schonberg 2010; NCO 5223.0200"),
 ("tk_cash", "Handle cash and payments", "16", "Autor and Handel 2013; NCO 5131.0401"),
 ("tk_cook", "Cook or prepare food or drink", "18", "NCO 5120.0300 cook"),
 ("tk_serve", "Serve guests or customers", "19", "NCO 5131.0401 waiter; Pal et al. 2026"),
 ("tk_clean", "Clean rooms or public areas", "20", "NCO 5151.0202 room attendant; Autor-Levy-Murnane 2003 (janitorial)"),
 ("tk_guide", "Guide or explain things to visitors", "21", "Gathmann and Schonberg 2010; NCO 5113.0200"),
 ("tk_coord", "Coordinate work by phone, radio or signals", "24", "NCO 8343.1700 ropeway operator"),
]
for nm, lab, no, src in TASKS:
    R("L", nm, lab[:70] + " (task grid)" if len(lab) <= 62 else lab[:80], f"Do you {lab[0].lower() + lab[1:]}? Card: 1 regularly in my main Yatra work; 2 not in my main work, but I have done it before elsewhere; 3 never.",
      f"Task {no} of the full 27-task list (tasks_module). Three answers: regular now / done before / never; not a rating.", "cat", "task3", source=src)
R("L", "lic_twowheeler", "Holds a two-wheeler licence", "Do you hold a two-wheeler driving licence? Ask to see it.", "Licence held.", "bin", "yn", source="Entry gate: NCO 8322 / RTO")
R("L", "lic_car", "Holds a car (light motor vehicle) licence", "... a car licence?", "Licence held; gate for driver jobs.", "bin", "yn", source="Entry gate: NCO 8322.0100")
R("L", "lic_heavy", "Holds a heavy vehicle licence", "... a heavy vehicle licence?", "Licence held.", "bin", "yn", source="Entry gate: NCO 8322 / RTO")
R("L", "permit_guide", "Holds a guide or trekking permit", "... a guide or trekking permit?", "Permit held; gate for guide jobs (assumed).", "bin", "yn", source="Entry gate assumed; not in NCO (needs check with the tourism board)")
R("L", "cert_iti", "Holds an ITI or technical trade certificate", "... an ITI or other technical trade certificate?", "Certificate held; gate for electrician and mechanic jobs.", "bin", "yn", source="Entry gate: NCO 7411.0301 (QP ELE/Q7302, NSQF 3)")
R("L", "cert_security", "Holds a security guard certificate", "... a security guard certificate?", "Certificate held; gate for guard jobs.", "bin", "yn", source="Entry gate: NCO 5414 (QP SKS/Q0101, NSQF 4)")
R("L", "read_at_work", "Reads anything at work", "In your work, do you read anything (notes, rate lists, tickets, messages)?", "Reading used at work (factual).", "bin", "yn", source="STEP module 6A")
R("L", "calc_at_work", "Works out prices or costs at work", "In your work, do you work out prices or costs?", "Arithmetic used at work (factual).", "bin", "yn", source="STEP module 6A")

# ------------------------------------------------------------------ CONSTRUCTED (built in Stata from the asked variables)
def C(name, label, desc, formula, kind="num", lset=None, source="Constructed"):
    R("X", name, label, "Not asked. Constructed.", desc, kind, lset, origin="constructed", formula=formula, source=source)

C("education_years", "Years of schooling (from education_level)", "Years of schooling implied by the highest level completed; missing if the respondent declined.",
  "0/5/8/10/12/15 for levels 0-5; missing for 98", source="NITI Aayog National MPI")
C("migrant", "Migrant: permanent home is outside the district", "1 if origin is not Local (same district).", "origin > 1", "bin", "yn")
C("health_access_tier", "Health-access tier of the site", "Route-cluster remoteness: Guptkashi/Phata Good; Sonprayag Moderate; Gaurikund and Kedarnath town Poor.",
  "from location_cluster", "cat", "tier", source="Project design; VEP exposure covariate")
C("health_access_deprived", "Health-access deprived (MPI health indicator)", "1 if the site tier is Poor, or Moderate and the household has no health cover.",
  "tier==1 | (tier==2 & health_insurance_covered==0)", "bin", "yn", source="Project version of NITI Aayog health indicators")
C("yatra_income", "Annual work income from the Yatra season (Rs)", "Yatra-season months times usual monthly Yatra earnings.", "yatra_months * inc_yatra_pm", "money")
C("non_yatra_income", "Annual work income from off-season months (Rs)", "Off-season months worked times usual monthly earnings in those months.", "offseason_months_worked * inc_offseason_pm", "money")
C("total_annual_income", "Total annual income (Rs)", "Work income plus inward remittances. Outward remittances are not subtracted.", "yatra_income + non_yatra_income + remittance_inward", "money")
C("yatra_income_share", "Share of annual income from the Yatra season", "Yatra income divided by total annual income (an Exposure covariate in the VEP model).", "yatra_income / total_annual_income")
C("months_no_work", "Months in the year without any paid work", "12 minus Yatra months minus off-season months worked.", "12 - yatra_months - offseason_months_worked", "count")
C("income_seasonality_cv", "Income seasonality: CV of the 12-month pattern", "Coefficient of variation across a 12-month vector: Yatra months at the Yatra level, worked off-season months at their level, other months at zero. Replaces the CV of 12 monthly answers.",
  "sd / mean of the 12-month vector (n-1 divisor)", source="Azeem et al. 2016; Khandker 2012")
C("cons_clothing_12m_pm", "Clothing spending per month (Rs)", "Annual figure divided by 12, rounded.", "round(cons_clothing_12m/12)", "money")
C("cons_education_12m_pm", "Education spending per month (Rs)", "Annual figure divided by 12, rounded.", "round(cons_education_12m/12)", "money")
C("cons_medical_12m_pm", "Medical spending per month (Rs)", "Annual figure divided by 12, rounded.", "round(cons_medical_12m/12)", "money")
C("cons_durables_12m_pm", "Durables spending per month (Rs)", "Annual figure divided by 12, rounded.", "round(cons_durables_12m/12)", "money")
C("total_cons_pm", "Household consumption per month (Rs)", "Sum of the four 30-day items and the four monthly-equivalent annual items.",
  "food + fuel + routine + rent + clothing_pm + education_pm + medical_pm + durables_pm", "money", source="Chaudhuri et al. 2002 welfare measure")
C("cons_pc_pm", "Per-capita monthly consumption (Rs)", "Household consumption per month divided by household size, rounded. This is the VEP outcome (its log).", "round(total_cons_pm / hhsize)", "money", source="Chaudhuri et al. 2002")
C("poor", "Poor: consumption below Rs 2,515 per month", "1 if per-capita monthly consumption is below the Sethu et al. 2024 rural line.", "cons_pc_pm < 2515", "bin", "yn", source="Sethu, Surya and Ruthu 2024 (Rangarajan method, HCES 2022-23)")
C("poor_sensitivity_cpi", "Poor on the Rs 1,850 line (sensitivity)", "1 if below the Rangarajan and Dev 2024 CPI-adjusted line; robustness only.", "cons_pc_pm < 1850", "bin", "yn", source="Rangarajan and Dev 2024")
C("durables_count", "Number of durables owned (0-6)", "Sum of the six durable-ownership items.", "owns_tv + owns_radio + owns_bicycle + owns_motorcycle + owns_car + owns_fridge", "count")
C("child_school_dep", "MPI: school-age child not attending", "1 if any child aged 6 to 14 is not attending school; missing if no such child.", "n_children_out_school > 0 if n_children_6_14 > 0", "bin", "yn", source="NITI Aayog National MPI")
C("hours_week_yatra", "Hours worked per week in the Yatra season", "Hours per day times days per week.", "hours_day_yatra * days_week_yatra", "count")
C("work_income_pm", "Average monthly work income over the year (Rs)", "(Yatra income + off-season income) divided by 12.", "(yatra_income + non_yatra_income)/12", "money")
C("emp_dep_access", "Employment deprivation: access", "1 if wanting work and idle more than 6 months, or wanting more work with under 20 hours a week.", "(wants_more_work==1 & months_no_work>6) | (wants_more_work==1 & hours_week_yatra<20)", "bin", "yn", source=K_SRC)
C("emp_dep_comp", "Employment deprivation: compensation", "1 if average monthly work income is below 67 percent of the sample median (Apablaza fallback threshold).", "work_income_pm < 0.67 * median(work_income_pm)", "bin", "yn", source=K_SRC)
C("emp_dep_sec", "Employment deprivation: security", "1 if a wage worker has no written contract, or a self-employed worker is not registered.", "written_contract==0 (wage) or work_registered==0 (self-employed)", "bin", "yn", source=K_SRC)
C("emp_dep_stab", "Employment deprivation: stability", "1 if in casual wage labour, or with under 1 year in this work (fallback: temporary or casual).", "employment_type==4 | years_in_yatra_work<1", "bin", "yn", source=K_SRC)
C("emp_dep_cond", "Employment deprivation: working conditions", "1 if exposed to a red-list hazard, or has neither health cover nor a pension.", "hazard_exposed==1 | (health_insurance_covered==0 & pension_coverage==0)", "bin", "yn", source=K_SRC)
C("emp_dep_count", "Employment deprivations (count of 5)", "Number of the five employment indicators in which the worker is deprived.", "sum of the five emp_dep_ indicators", "count", source=K_SRC)
C("emp_dep_score", "Employment deprivation score (equal weights, 0-1)", "Count divided by 5.", "emp_dep_count / 5", "num", source=K_SRC)
C("emp_poor_k2", "Employment-poor: deprived in 2 or more of 5", "1 if two or more indicators; k = 2 of 5 is our choice, to be varied in robustness.", "emp_dep_count >= 2", "bin", "yn", source=K_SRC + "; cut-off is the project's choice")
C("tk_regular_n", "Number of the 12 tasks done regularly", "Count of task answers equal to 1.", "count of tk_* == 1", "count")
C("tk_prior_n", "Number of the 12 tasks done before elsewhere", "Count of task answers equal to 2.", "count of tk_* == 2", "count")

# ------------------------------------------------------------------ SYNTHETIC-ONLY
def S(name, label, desc, kind="bin", lset=None):
    R("Z", name, label, "Not collected. Exists only in the synthetic file.", desc, kind, lset, origin="synthetic", source="Synthetic design")
S("flagged_contradiction", "[SYNTHETIC] Record flagged for a logical contradiction", "Used only to test cleaning rules in the synthetic pipeline.", "bin", "yn")
S("dropout_score", "[SYNTHETIC] Drop-out risk score", "Used only to build the drop-out mechanism.", "num")
S("dropout_prob", "[SYNTHETIC] Drop-out probability", "Used only to build the drop-out mechanism and IPW check.", "num")
S("flagged_dropout", "[SYNTHETIC] Flagged as a drop-out", "Used only in the synthetic pipeline.", "bin", "yn")
S("retained", "[SYNTHETIC] Retained in the as-fielded sample", "1 if the synthetic respondent stayed in the fielded sample.", "bin", "yn")

NAMES = [r["name"] for r in ROWS]
assert len(NAMES) == len(set(NAMES)), [n for n in NAMES if NAMES.count(n) > 1]
if __name__ == "__main__":
    from collections import Counter
    print(len(ROWS), Counter(r["origin"] for r in ROWS))
