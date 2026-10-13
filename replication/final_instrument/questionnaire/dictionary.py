"""Single source of truth for the final Kedarnath survey instrument.
Every variable appears once: module, name, Stata label (<=80 chars), question wording, description,
type, value-label set, skip rule, literature source, origin (paradata / asked / constructed / synthetic).
The questionnaire PDF, the variable_dictionary.csv and the Stata label file are all built from this list."""

# Module list. There is deliberately NO minutes column any more: the old one was twelve hand-typed
# constants that never recomputed when items changed, and the generator's "simulated" duration was an
# invented intercept of 42 minutes plus noise. Neither measured anything, and between them they put
# three different durations (46.4, 47, 40) into documents that go to the field and to ethics. Real
# timing comes from Kobo's own start/end metadata at the pretest. Until then we make no claim.
MODULES = [  # code, title
    ("P", "Cover page, consent and paradata"),
    ("A", "Respondent and household"),
    ("B", "Work and work history"),
    ("C", "Monthly calendar of work and income"),
    ("D", "Migration, home place and remittances"),
    ("E", "Household consumption"),
    ("F", "Housing, amenities and assets"),
    ("G", "Finance, insurance and schemes"),
    ("H", "Health"),
    ("I", "Food security, shocks and coping"),
    ("J", "Ropeway"),
    ("K", "Job quality (Apablaza et al. 2026 questions)"),
    ("L", "Tasks and skills (short block)"),
    ("M", "Access to common resources (short block)"),
]

# The consent script, read verbatim before anything else is asked. This lives here, with the rest of
# the instrument, because it was previously duplicated: build_scripts.py held the full version and
# build_webform.py a shorter paraphrase of it, and NEITHER reached the tablet — the consent question's
# own text said "Read the consent script" while the script itself appeared only in the printed script.
# An enumerator holding a phone had nothing to read. Informed consent is the one thing in this
# instrument that cannot be left to memory, so it is now rendered on the consent screen itself.
CONSENT_SCRIPT = """We are doing a study on the livelihoods of people who work on the Yatra route. I would like to ask you some questions about your work, your household and your spending.

Taking part is your choice. You can stop at any time, and you can skip any question you do not want to answer. Nothing you tell me will be linked to your name, and nothing you say will affect your work here or any government benefit.

If you say no, I will not ask you any questions. I will write down only that you said no, the date and time, and what was happening at the time, such as crowding or weather. I will not write down your name, your sex, your age, or where you are. No answers are recorded."""


# The plain-language description of the study, shown on the landing screen before the consent
# script and reachable afterwards from the menu. Distinct from CONSENT_SCRIPT and not a substitute
# for it: consent is the short statement that must be read verbatim and answered, while this is the
# longer "what is this and who is asking" that a respondent may want before agreeing to anything,
# and that an enumerator needs a fixed form of words for. It names the ropeway explicitly, because
# the first question anyone on the route actually asks is whether we are from the ropeway company.
STUDY_BRIEF = """The Kedarnath and Hemkund Sahib Yatra corridors are planned to receive ropeways in the coming years. This study aims to understand how the ropeway may affect the livelihoods of people working along these corridors, including mule and horse riders, palki and pitthu carriers, small shop owners, hotel workers, and others whose income depends on Yatra traffic.

This study is for academic research only and all findings will remain strictly confidential.

Your participation is voluntary. You may skip any question and stop the interview at any time. Your answers will be kept confidential and will never be linked to your name or identity."""

# Read-aloud module introductions. The enumerator reads these before the module's first question.
# They exist because this instrument asks the same thing twice (two seasons) or twelve times (the
# calendar) in several places, and a respondent who does not know that is coming reads the repetition
# as the enumerator not having listened. Each one says what is about to be asked, how long it runs,
# and — where it matters — that rough figures are acceptable. Module P is excluded: consent is its
# own script and must not be prefaced by anything that sounds like persuasion.
INTROS = {
    "A": "First, a few things about you and the people who live in your household.",
    "B": "Now about the work you do here on the Yatra route, and the work you did before this.",
    "C": "Now I want to go through the last twelve months, one month at a time. For each month I will "
         "ask what work you were mainly doing, and then what you usually earned. It is easiest to "
         "start with the Yatra months and fill the rest afterwards.",
    "D": "Now a few questions about where your home is, and what you do when the Yatra closes for the season.",
    "E": "Now about what your household usually spends in a month. For each thing I will ask twice — "
         "once for a normal month during the Yatra season, and once for a normal month when the Yatra "
         "is closed — because spending is often quite different in the two. Rough figures are fine.",
    "F": "Now some questions about your house and the things your household has.",
    "G": "Now about savings, loans, insurance and government schemes.",
    "H": "Now a few questions about health in your household. You may leave out any of these.",
    "I": "Now about food, and about any difficult times in the last year and how your household managed.",
    "J": "Now a few questions about the ropeway that has been proposed for this route. It is only a "
         "proposal — nothing has been built. There is no right answer and nothing you say here goes to "
         "anyone but us.",
    "K": "Now a set of questions about the conditions of your work — hours, pay, contract and so on. "
         "These come from a standard list used in many countries, so one or two may not fit your "
         "situation. Say so and we will move on.",
    "L": "Now I will read out some kinds of work-tasks and ask whether you do them. There is no right "
         "or wrong answer — we are trying to understand what skills the work here actually uses.",
    "M": "Last, a few questions about the forest and common land around where you work — firewood, "
         "fodder, grazing and water. Some of this is not allowed in some places, and that is a "
         "perfectly good answer: we only want to know what is possible and what is not. Nothing you "
         "say goes to the Forest Department or to anyone else, and you can leave any of these out.",
}

# Enumerator hints: shown on the tablet UNDER the question, printed in the scripts and on the paper
# form. These are NOT read to the respondent — they are the definition the enumerator needs at the
# moment of coding, for the handful of items where two options are genuinely easy to confuse and the
# confusion changes a result. Distinct from build_scripts.PROBE, which is what to SAY next on an
# open-ended item; a hint is how to CODE. Keep them short: a hint nobody reads is worse than none.
HINTS = {
    "other_activity_types": "ENUMERATOR: hauling luggage or goods on the back, shoulders or a head-load, for pilgrims or shops, is code 3 (porter). Carrying a person in a kandi is also code 3; carrying a person on a palanquin as part of a team is code 4. Hauling luggage or goods on a pony or mule is code 1 if the respondent works the animal for someone else, and code 2 if they own it.",
    "wage_employer": "ENUMERATOR: private company = a registered firm or hotel chain; government or public body = a government department, Yatra board, PWD or other public office; household = a family that hires them for domestic work; contractor or agent = a thekedar or agent who arranged and pays for the work; individual employer = one person who pays them directly, such as a shop or dhaba owner. If the respondent says 'the owner' or 'the boss' without more, ask who arranged the job. If they came through an agent (see the migration referral question), code 4. If unsure, code 97 and write the words in the notes.",
    "tenure_under_1": "ENUMERATOR: tick Yes if the person has been in this job for less than one year. Do not ask for months. If Yes, skip the years question.",
    "years_current_job": "ENUMERATOR: only if the person has been in this job one year or more. Write the number of years; use a decimal for part years (1.5 = one year and six months). The next question is about years at this WORKSITE, not this job -- most people give the same number for both, which is fine.",
    "pension_any": "ENUMERATOR: if the person is clearly informally or casually employed (daily wage, no fixed employer), you may skip this and leave it blank -- the answer is almost always No for this group.",
    "n_children_in_school": "ENUMERATOR: this counts only children aged 6 to 14. If the respondent mentions a younger child attending anganwadi or preschool, note it but do not count that child here.",
    "years_coming_here": "ENUMERATOR: if the respondent already told you this with the last question (most people who have not changed trade here), write the same number or leave this blank -- do not re-ask it as if it were new.",
    # emp_dep_stab counts code 3 (occasional/casual) as unstable and code 2 (seasonal) as not, so
    # confusing the two moves the employment-deprivation rate directly. And the default error here is
    # predictable: on this route every job is seasonal in the ordinary sense, because the Yatra
    # closes, so both enumerator and respondent will reach for code 2 unless told otherwise.
    # The sample is recruited at the worksite, so almost everyone is 1 or 2 and the risk is not
    # that a rare code is missed but that the common pair is split wrongly. "Full-time" here is not
    # a contract or an hours threshold -- it is whether the work was their main occupation for the
    # month, which is how Apablaza's own routing treats it.
    "job_situation":
        "Code what they were MAINLY doing, by time, over the last month. Work for pay = full-time "
        "if it was their main activity on most working days, part-time or occasional if it was "
        "picked up here and there around something else. Seasonal preparation (buying stock, "
        "repairing tack, bringing animals up) IS working for pay — it is their trade — "
        "so code 1 or 2, not 10. Unemployed (8) means looking for work and not finding it; "
        "between seasons with work expected is not unemployed. Code 10 is the genuine none: not "
        "working, not studying, not looking.",

    "job_permanence":
        "Both will sound seasonal here — the Yatra closes for everyone. Ask about WITHIN the season. "
        "One employer keeps them on for a stretch = Seasonal or temporary. They take work day by day "
        "from whoever offers it = Occasional or casual. Self-employed: answer for how their own work "
        "runs. On probation and Fixed-term are rare here; do not reach for them.",

    # The year COUNT is what the MPI education indicator and the Chaudhuri covariate want; the
    # bracket under it is a lossy fallback kept only for people who genuinely cannot say. The
    # predictable error is that respondents answer in LEVELS — "12th pass", "BA" — and the
    # enumerator hears that as "does not know the years" and codes No, throwing away a number the
    # respondent has in fact just given, in a different unit.
    "knows_years_schooling":
        "A level is NOT a No. If they answer '8th', '12th pass', 'ITI', 'BA', 'MA' — code YES and "
        "convert it on the next screen. Code No only if they cannot say how far they went at all.",
    "years_schooling":
        "Enter a NUMBER counted from class 1, never a level. Class 1 to 12 = that class number. "
        "ITI or diploma after 10th = 12. Bachelors = 15, or 16 if the course ran four years — ASK "
        "how long it ran. Masters = 17, or 18 after a four-year bachelors. If they dropped out part "
        "way through a year, count the completed years only.",
    "any_member_6yr_schooling":
        "The respondent is himself a household member. If HE has six years or more the answer is "
        "Yes — do not send him looking for someone else. The screen is skipped automatically "
        "wherever his own answer already settles it.",
    # Dropping "Don't know" from the two maternal-health items (2026-10-01) moves the burden onto
    # the probe: the enumerator now has to get an answer rather than record that nobody knew.
    "ropeway_stance":
        "Name the alignment for the route you are on: on the Kedarnath side it is the ropeway "
        "proposed between Gaurikund and Kedarnath, on the Hemkund side between Govindghat and "
        "Hemkund. Both are proposed, and the four ropeway questions are asked on BOTH routes -- they "
        "used to be asked only on the Kedarnath side, which left the Hemkund interviews with no "
        "ropeway data at all. If the respondent has not heard of it, say that it is proposed and not "
        "yet built, then take the answer; do not explain what it would do.",
    "child_death_5y":
        "Say the lead-in before you ask: \"The next question is about a death in the family. You do "
        "not have to answer it.\" Then ask it once. Do NOT probe, do not ask for details, and do not "
        "ask again if they go quiet -- leave it blank and move on. A blank here is a correct and "
        "complete answer; NITI's own rule treats an unanswered mortality item as not deprived.",
    "anc_4_visits":
        "Ask the mother herself if she is there. If not, probe: did she go for check-ups before the "
        "birth, and about how many times? Four or more is Yes; two or three is No. Do not accept a "
        "shrug — ask how many times she went.",
    "skilled_birth_attendant":
        "Code who CONDUCTED the delivery, not who was in the room. An ASHA or Anganwadi worker "
        "accompanying a birth is code 3, not a nurse: NITI counts only a doctor, nurse, ANM or LHV "
        "as skilled. A dai is code 4. If an ANM conducted it and an ASHA brought her, that is 2.",
    # The scheme list stopped being a set of options on 2026-10-01 and became this probe list: the
    # answer is written down in the respondent's words and coded in the office.
    "govt_any_benefit":
        "READ THE LIST OUT; do not ask the bare question, because people fail to recall the "
        "category and say no. Ration card or PDS grain; MGNREGA work or job card; old-age, widow "
        "or disability pension; PM-KISAN; Ujjwala LPG; PM-SYM or Atal Pension; Ayushman Bharat or a "
        "health card; a housing scheme (PMAY or state). Any one of them is a Yes.",
    "govt_schemes_detail":
        "Write the scheme names in their own words, all of them, including any not on the list you "
        "just read. Office-coded afterwards, so do not try to fit the answer to a category.",
}

LSETS = {
    "yn": {0: "No", 1: "Yes"},
    "ropexp": {1: "More work for me", 2: "Less work for me", 3: "About the same", 97: "Don't know"},
    "ropjobs": {1: "People from these villages", 2: "People from outside the area", 3: "Nobody will get jobs", 97: "Don't know"},
    "obsenv": {1: "Normal crowd, normal weather", 2: "High crowd or peak hours", 3: "Rain or extreme weather", 4: "Both high crowd and bad weather"},
    # Code 3 added 2026-10-05. A 50 km "accuracy" is an IP geolocation, not a GPS fix: two
    # interviews in the first field test arrived with gps_accuracy_m = 50000, recorded 200 km
    # off-route, and nothing in the instrument distinguished that from a 14 m fix.
    # Off-season activity, asked directly since 2026-10-05 in place of the modal non-Yatra
    # calendar cell. Codes 2-7 carry the same labels they had in `activity` so the two are
    # readable against each other; 96 is the write-in-less "other", and 0 is the genuine none --
    # a respondent whose Yatra months and idle months already fill the year.
    # The nine NITI durables and the three livestock classes, as check-all lists (2026-10-05).
    # Codes are the order NITI lists the assets in; Stata splits them back into the nine
    # owns_* binaries the indicator is defined on and the field rows already hold.
    # Common-property use, with a prohibition code (2026-10-05). No/Yes/Don't know conflated
    # "we do not" with "we are not permitted to", which on the Hemkund side -- where the Forest
    # Department bans collection outright -- is the only answer there is.
    "permdk": {1: "Yes, it is allowed", 0: "No, it is not allowed", 2: "Allowed only with a permit or a fee", 97: "Don't know"},
    "cpruse": {0: "No", 1: "Yes", 2: "No, it is not allowed here", 97: "Don't know"},
    "assets": {1: "Television", 2: "Radio", 3: "Bicycle", 4: "Motorcycle or scooter",
               5: "Car, jeep or truck", 6: "Telephone of any kind (mobile or landline)",
               7: "Computer or laptop", 8: "Cart pulled by an animal", 9: "Refrigerator"},
    "livestock": {1: "Cows or buffaloes", 2: "Goats or sheep", 3: "Ponies or mules"},
    "offact": {2: "Farming (crops)", 3: "Livestock (animals)", 4: "Casual or daily wage labour",
               5: "Construction work", 6: "Own small shop, stall or trade", 7: "Salaried job",
               96: "Some other work", 0: "There were no such months"},
    "gpserr": {1: "Location not allowed in the browser", 2: "No fix obtained",
               3: "Coarse fix only, over 200 m -- network or IP location, not GPS"},
    "wageemp": {1: "Private company", 2: "Government or public body", 3: "A household (domestic work)", 4: "A contractor or agent", 5: "An individual employer", 97: "Don't know"},
    "earnrange": {1: "Under Rs 5,000", 2: "Rs 5,000 to 10,000", 3: "Rs 10,000 to 20,000", 4: "Rs 20,000 to 35,000", 5: "Rs 35,000 to 50,000", 6: "Rs 50,000 or more", 97: "Don't know"},
    "instypes": {1: "Health insurance or scheme (incl. government)", 2: "Life insurance", 3: "Crop insurance"},
    "fies5": {1: "Had to skip a meal", 2: "Ate less than you thought you should", 3: "Your household ran out of food", 4: "Were hungry but did not eat", 5: "Went a whole day without eating", 96: "None of these happened"},
    "cprwater": {1: "Yes, free to use", 2: "A source exists but we must pay", 3: "No source nearby", 97: "Don't know"},
    "cprgov": {1: "Village head or panchayat", 2: "Forest department", 3: "Local committee or community group", 4: "Nobody decides; it is open to all", 97: "Don't know"},
    "sex": {0: "Male", 1: "Female"},
    "enum": {1: "Raman", 2: "Rishit", 3: "Tanmay", 4: "Anuj"},
    # "cluster" removed 2026-09-24: the enumerator-coded route cluster duplicated what the silently
    # captured GPS already records. health_access_tier is now derived from the GPS instead (see below),
    # which is both one less question and a finer input than four hand-coded categories.
    # Major Indian languages (the 22 scheduled languages) plus the three that actually matter on this
    # route and are not scheduled: Garhwali, Kumaoni, Bhojpuri. Nepali is scheduled and is kept.
    # The first five are the high-frequency ones for this workforce, so the enumerator finds them
    # without scrolling; the rest are alphabetical.
    "nativelang": {1: "Garhwali", 2: "Kumaoni", 3: "Hindi", 4: "Nepali", 5: "Bhojpuri",
                   6: "Assamese", 7: "Bengali", 8: "Bodo", 9: "Dogri", 10: "Gujarati", 11: "Kannada",
                   12: "Kashmiri", 13: "Konkani", 14: "Maithili", 15: "Malayalam", 16: "Manipuri (Meitei)",
                   17: "Marathi", 18: "Odia", 19: "Punjabi", 20: "Sanskrit", 21: "Santali", 22: "Sindhi",
                   23: "Tamil", 24: "Telugu", 25: "Urdu",
                   96: "Other Indian language", 97: "Other / foreign language"},
    # All 28 states and 8 union territories, alphabetical, plus one out-of-India code. Replaces the
    # four-way origin bucket for the "where is home" question: a state is what the respondent can
    # actually name, and it is also the level at which India's rural/urban poverty lines are set.
    "state": {1: "Andhra Pradesh", 2: "Arunachal Pradesh", 3: "Assam", 4: "Bihar", 5: "Chhattisgarh",
              6: "Goa", 7: "Gujarat", 8: "Haryana", 9: "Himachal Pradesh", 10: "Jharkhand",
              11: "Karnataka", 12: "Kerala", 13: "Madhya Pradesh", 14: "Maharashtra", 15: "Manipur",
              16: "Meghalaya", 17: "Mizoram", 18: "Nagaland", 19: "Odisha", 20: "Punjab",
              21: "Rajasthan", 22: "Sikkim", 23: "Tamil Nadu", 24: "Telangana", 25: "Tripura",
              26: "Uttar Pradesh", 28: "West Bengal",
              29: "Andaman and Nicobar Islands", 30: "Chandigarh",
              31: "Dadra and Nagar Haveli and Daman and Diu", 32: "Delhi",
              33: "Jammu and Kashmir", 34: "Ladakh", 35: "Lakshadweep", 36: "Puducherry"},
    # 27 (Uttarakhand) and 99 (Outside India) were removed 2026-10-03. home_state is asked ONLY on
    # origin = 3, "another Indian state", so both were answers that contradicted the question's own
    # gate. The codes are left unused rather than renumbered: 28 is West Bengal in the pilot file
    # and in every export so far, and shifting 27 onto a live code to close a gap would silently
    # rewrite those.
    "ruralurban": {1: "Village (rural)", 2: "Town or city (urban)"},
    # Hill households in Uttarakhand hold land in NALI, not acres, and converting in their head is a
    # source of error the form should not ask for. The unit is recorded and Stata converts: 1 nali is
    # about 1/50 of an acre locally, 1 bigha about 1/5. Record the unit they use, not ours.
    "landunit": {1: "Nali", 2: "Bigha", 3: "Acres", 4: "Hectares", 5: "No land"},
    "loanpurpose": {1: "Medical or hospital costs", 2: "Buying an animal, vehicle or equipment for work",
                    3: "Shop stock or business", 4: "Food or daily household needs",
                    5: "A wedding, funeral or ceremony", 6: "House building or repair",
                    7: "Education", 8: "Repaying another loan", 9: "Something else"},
    "collat": {0: "Nothing was given as security", 1: "Jewellery or ornaments", 2: "Land", 3: "Animals", 4: "A vehicle",
               5: "Shop stock or business goods", 6: "House or building", 7: "Something else"},
    # A two-way CHOICE, not a yes/no. Codes keep 1 = month-by-month and 0 = annual total so every
    # downstream ==1 / ==0 test still holds; only the labels change, because "No / Yes" is not an
    # answer to "month by month, or one total?".
    "recall": {1: "Month by month", 0: "One total for the whole year"},
    "hohrel": {1: "Self (respondent is the head)", 2: "Husband", 3: "Wife", 4: "Father", 5: "Mother",
               6: "Son", 7: "Daughter", 8: "Brother", 9: "Sister", 10: "Other male relative",
               11: "Other female relative", 12: "Other, non-relative (male)",
               13: "Other, non-relative (female)"},
    "famstruct": {1: "Nuclear (you, spouse and unmarried children only)",
                  2: "Joint (living with parents, married siblings or other extended family)",
                  3: "Single-member household"},
    "marital": {1: "Currently married", 2: "Never married", 3: "Widowed/divorced/separated"},
    "edu2": {1: "No formal education", 2: "Some schooling, did not complete primary", 3: "Completed primary but not secondary",
             4: "Completed secondary or higher", 98: "Prefer not to say"},   # fallback bracket only, when years aren't known
    # Occupation groups, rebuilt 2026-09-24 against NCO-2015 (Vol II-A/II-B, read directly).
    # Two faults were fixed. (1) ASYMMETRY: shop and hotel each had a worker AND an owner code, but
    # food had only "Dhaba/food-stall owner" — a dhaba cook or tea-stall helper had nowhere to go and
    # was being pushed into "shop worker" or "Other". (2) AMBIGUITY between shop and dhaba: the real
    # line, and the one NCO draws, is RETAIL GOODS versus PREPARED FOOD, so the labels now say so.
    #   NCO anchors — 9332 Drivers of Animal-Drawn Vehicles and Machinery (9332.0100 Horse Carriage
    #   Driver, 9332.0300 Mahout) for pony work; 9621 Messengers, Package Deliverers and Luggage
    #   Porters + 9333 Freight Handlers for porters; 5211 Stall and Market Salespersons, 5212 Street
    #   Food Salespersons, 5246 Food Service Counter Attendants, 9411 Fast Food Preparers, 9412
    #   Kitchen Helpers, 5120 Cooks, 1412 Restaurant Managers for the food trades; 5221 Shopkeepers
    #   and 5223 Shop Sales Assistants for retail goods; 1411 Hotel Managers, 4224 Hotel
    #   Receptionists, 5151.0800 Room Bearer/Bell Boy, 9112 Cleaners and Helpers in Hotels for
    #   lodging; 8322 Car, Taxi and Van Drivers; 5113 Travel Guides; 9211/9313 labourers.
    # Codes 1-4 and 12 are unchanged from the previous list so the trek-dependent set still reads
    # inlist(1,2,3,4,12); everything else renumbered.
    "occ": {1: "Pony/mule worker (works the animals, does not own them)",
            2: "Pony/mule owner (owns the animals)",
            3: "Porter (carries on own back/shoulders - goods, luggage, or a person in a kandi)",
            4: "Palki / dandi bearer (carries a person on a palanquin, as part of a team)",
            5: "Dhaba, tea stall or food stall WORKER (prepared food or tea)",
            6: "Dhaba, tea stall or food stall OWNER (prepared food or tea)",
            7: "Shop WORKER (goods: prasad, puja items, clothes, general store)",
            8: "Shop OWNER (goods, not prepared food)",
            9: "Hotel / lodge WORKER",
            10: "Hotel / lodge OWNER",
            11: "Driver (any motor vehicle)",
            12: "Guide",
            13: "Wage labourer (construction, loading, odd jobs)",
            14: "Other"},
    # Code 5 added 2026-09-30, taking over the one useful category from Apablaza's Q8 as employer_type
    # was dropped: a son minding the family stall is a contributing family worker, and this list had
    # nowhere to put him. The rest of Q8's categories were status crossed with institutional sector
    # (private company, public sector, armed forces, domestic service), which left every worker
    # employed by an INDIVIDUAL — a thekedar, a shop owner, a dhaba owner, i.e. most of this sample --
    # with no true option but "employee of a private company".
    "emptype": {1: "Own-account (self-employed, no hired workers)",
                2: "Employer/business owner (self-employed)", 3: "Regular wage or salary",
                4: "Casual or daily wage labour", 5: "Unpaid family worker"},
    # Two pilgrimage routes now, so every estimate can be stratified and the site can carry a fixed
    # effect. GPS does the rest of the locating, which is why this is one question and not a place list.
    "site": {1: "Kedarnath (Gaurikund to Kedarnath)", 2: "Hemkund Sahib (Govindghat to Hemkund)"},
    # Where the worker actually sleeps during the season. The rest of Module F describes the USUAL
    # home, which for a seasonal migrant is not where he spends six months of the year. Lyons et al.
    # (2023) carry settlement conditions in their security dimension for the same reason: for a
    # migrant population the accommodation at the destination is its own deprivation, and the
    # home-place house says nothing about it.
    "accomhere": {1: "At my own usual home (I live here)", 2: "Rented room or house",
                  3: "Room or dormitory the employer provides",
                  4: "Sleeps at the shop, dhaba or workplace", 5: "Tent or temporary shelter",
                  6: "Lodge, dharamshala or ashram", 7: "In the open, or a verandah",
                  8: "Somewhere else"},
    # Washington Group Short Set response scale, verbatim. Standard deprivation cutoff is
    # "a lot of difficulty" or "cannot do it at all".
    "wgdiff": {1: "No difficulty", 2: "Some difficulty", 3: "A lot of difficulty",
               4: "Cannot do it at all"},
    # One Nation One Ration Card portability — the closest real analogue to the legal-residency
    # indicator in Lyons et al.: an internal migrant whose entitlement works only at his home place is
    # outside the food safety net for the half of the year he is actually earning.
    "portable": {1: "Yes, can draw it here", 2: "No, only at the home place",
                 3: "Has never tried", 4: "We have no ration card", 97: "Does not know"},
    "month": {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August",
              9: "September", 10: "October", 11: "November", 12: "December"},
    # "Moved to this area" is gone. It answered a different question — why you MIGRATED, not why
    # you changed work — so a migrant who took a new job on arrival had two true answers and the
    # item silently became a migration question for some respondents and an occupation question for
    # others. Migration reason now has its own item in Module D.
    "prevreason": {1: "Better income", 2: "Lost the previous work", 3: "Work ended with the season",
                   4: "Family reasons", 5: "Health or injury", 6: "Other"},
    "origin": {1: "Local (same district)", 2: "Other Uttarakhand district", 3: "Other Indian state", 4: "Nepal"},
    "referral": {1: "A family member already working here", 2: "A friend or someone from the village",
                 3: "A thekedar or contractor I now work for",
                 4: "An agent or middleman who placed me (usually for a fee)",
                 5: "No one; I found it myself", 6: "The employer called me directly",
                 7: "Someone else"},
    "floor": {1: "Mud/kaccha", 2: "Cement/mud-cement", 3: "Tile/mosaic/marble"},
    "roof": {1: "Thatch/wood/mud", 2: "Tin/GI sheet", 3: "Concrete/RCC"},
    "wall": {1: "Mud, thatch, bamboo or other natural material", 2: "Unburnt brick, wood or tin",
             3: "Burnt brick, cement, concrete or stone"},
    "toilet": {1: "No toilet / open defecation", 2: "Pit latrine without slab or open pit",
               3: "Improved toilet, but shared with other households",
               4: "Improved toilet, used only by this household"},
    # JMP/NFHS improved-vs-unimproved taxonomy, which is what NITI Aayog's MPI water indicator
    # actually rests on. Codes 1-6 are improved, 7-9 unimproved. The old three-option list
    # ("Piped / Handpump / Other (spring/tanker)") could not express that split, and had no way to
    # record distance — NITI counts an improved source as deprived anyway if it is more than a
    # 30-minute round trip from home, which the old item simply could not detect.
    "water": {1: "Piped into the house or yard", 2: "Public tap or standpipe",
              3: "Handpump, tubewell or borewell", 4: "Protected well or protected spring",
              5: "Rainwater collection", 6: "Bottled, packaged or community RO",
              7: "Unprotected well or unprotected spring", 8: "River, stream, pond or canal",
              9: "Tanker truck or cart with drum"},
    # NITI Aayog's cooking-fuel indicator is a LIST OF DIRTY FUELS — "a household cooks with dung,
    # agricultural crops, shrubs, wood, charcoal or coal" — not "LPG or not". The old binary
    # misclassified electricity and biogas users, who cook clean, as deprived.
    "fuel": {1: "LPG or cylinder gas", 2: "Piped natural gas", 3: "Electricity",
             4: "Biogas (gobar gas plant)", 5: "Kerosene", 6: "Firewood", 7: "Dung cakes (gobar)",
             8: "Crop residue, straw or shrubs", 9: "Charcoal", 10: "Coal or lignite"},
    # adminlevel (village / town / city) was dropped 2026-09-28. It asked the respondent to perform an
    # administrative classification that is a Census status, not a folk category: whether a place is a
    # statutory town, a census town or a village is not something a resident knows, so two people from
    # the same place answered differently and the variable's variance was mostly self-presentation. It
    # was also selecting the poverty line — Rs 2,515 against Rs 3,639, a 45% swing — off a subjective
    # answer. home_rural_urban is now asked directly as the binary the line actually needs.

    # Reason for first coming to work here. Kept apart from prevreason, which is about changing WORK:
    # a migrant who took a new job on arrival had two true answers to the old combined item.
    "comereason": {1: "No work at home", 2: "Pay is better here",
                   3: "Family or people from my village were already here",
                   4: "Land at home is too little to live on", 5: "Debt to repay",
                   6: "A contractor or agent brought me", 7: "Married into / moved with family",
                   8: "Some other reason"},
    # Location row on the monthly calendar. This is the item that turns the Yatra-season/off-season
    # split from an assumption the whole instrument rests on into a measurement, respondent by
    # respondent — and it fixes the mid-month season boundary, because the boundary is now wherever
    # each person's own row changes rather than a constant we chose.
    # Two pilgrimage routes now, so every estimate can be stratified and the site can carry a fixed
    # effect. GPS does the rest of the locating, which is why this is one question and not a place list.
    "site": {1: "Kedarnath (Gaurikund to Kedarnath)", 2: "Hemkund Sahib (Govindghat to Hemkund)"},
    # Where the worker actually sleeps during the season. The rest of Module F describes the USUAL
    # home, which for a seasonal migrant is not where he spends six months of the year. Lyons et al.
    # (2023) carry settlement conditions in their security dimension for the same reason: for a
    # migrant population the accommodation at the destination is its own deprivation, and the
    # home-place house says nothing about it.
    "accomhere": {1: "At my own usual home (I live here)", 2: "Rented room or house",
                  3: "Room or dormitory the employer provides",
                  4: "Sleeps at the shop, dhaba or workplace", 5: "Tent or temporary shelter",
                  6: "Lodge, dharamshala or ashram", 7: "In the open, or a verandah",
                  8: "Somewhere else"},
    # Washington Group Short Set response scale, verbatim. Standard deprivation cutoff is
    # "a lot of difficulty" or "cannot do it at all".
    "wgdiff": {1: "No difficulty", 2: "Some difficulty", 3: "A lot of difficulty",
               4: "Cannot do it at all"},
    # One Nation One Ration Card portability — the closest real analogue to the legal-residency
    # indicator in Lyons et al.: an internal migrant whose entitlement works only at his home place is
    # outside the food safety net for the half of the year he is actually earning.
    "portable": {1: "Yes, can draw it here", 2: "No, only at the home place",
                 3: "Has never tried", 4: "We have no ration card", 97: "Does not know"},
    "month": {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July",
              8: "August", 9: "September", 10: "October", 11: "November", 12: "December"},
    # Named schemes, not "any government scheme". A category prompt makes the respondent recall a
    # class ("did you get a benefit?") and people reliably fail at that; a named list is recognition,
    # not recall. The levels also differ — ration is per household, pensions are per person, MGNREGA
    # is a job card, PM-KISAN follows the landholding — which is why this is a check-all rather than
    # a count of recipients: a count across these levels is not a coherent quantity.
    "govtscheme": {1: "Ration card / PDS food grain", 2: "MGNREGA work or job card",
                   3: "Old-age, widow or disability pension", 4: "PM-KISAN (farmer cash transfer)",
                   5: "Ujjwala LPG connection", 6: "PM-SYM or Atal Pension Yojana",
                   7: "Ayushman Bharat / health insurance card", 8: "Housing scheme (PMAY or state)",
                   9: "Some other scheme", 10: "None of these"},
    "remitmode": {1: "From my own phone (UPI or net banking)",
                  2: "In person at a bank branch or bank mitra / CSP",
                  3: "Money order or post office", 4: "Sent with someone going home",
                  5: "Carried it myself", 6: "Through an agent or middleman", 7: "Other"},
    "credit": {1: "Nationalised or public-sector bank", 2: "Private bank", 3: "Cooperative bank or RRB",
               4: "Microfinance institution or SHG", 5: "Moneylender", 6: "Relative or friend",
               7: "Employer or contractor (advance)", 8: "Other"},
    # Multi-select from 2026-09-25. Two changes. (1) "Record the most serious one" asked the
    # enumerator to rank other people's misfortunes, which they cannot do and should not be asked to.
    # (2) Every code in the old list was household-IDIOSYNCRATIC; codes 5-8 are COVARIATE shocks that
    # hit the whole route at once, and without them the covariate/idiosyncratic decomposition
    # (Gunther & Harttgen, via Fujii) is not identifiable from this data at all.
    # Code 9 added 2026-10-01. This list was a REQUIRED select_multiple with no way to say nothing
    # happened — a household with no shock in twelve months had nothing it could legitimately tick,
    # and the form would not advance. Every other multi-select here already had its escape (govt_schemes
    # code 10, shock_coping "did nothing"); this one did not. Code 9 is exclusive: ticking it alongside
    # a shock is a contradiction, and the build flags it.
    "distress": {9: "Nothing of this kind happened", 1: "Serious illness or death of an earning member", 2: "Crop failure or livestock loss",
                 3: "Damage from a natural disaster (flood, landslide, fire)",
                 4: "Loss of business, goods or assets", 5: "Road or bridge blocked, route closed",
                 6: "Yatra stopped early or badly disrupted", 7: "Sharp fall in customers or prices",
                 8: "Lost the work or the work stopped"},
    # Code 6 used to read "Did nothing/other", which is two opposite answers in one box. "Did
    # nothing" means the household absorbed the cost out of normal earnings and gave nothing up --
    # evidence it was NOT stressed. "Other" means it was stressed in a way this list does not hold.
    # Collapsed together, a household that shrugged off a cost and one that did something drastic
    # and unlisted were the same code, and the coping analysis could not separate them. Split.
    # Code 6 is EXCLUSIVE in the check-all version: "nothing special was needed" alongside
    # "borrowed money" is a contradiction, and the form refuses it.
    "coping": {1: "Used savings", 2: "Borrowed money", 3: "Sold or pawned assets", 4: "Cut consumption",
               5: "Help from relatives/community", 6: "Paid it out of normal earnings, nothing given up",
               7: "Something else (say what)"},
    # Who CONDUCTED the delivery. Replaces a yes/no/don't-know on "a doctor, nurse or trained
    # midwife", which was wrong twice over for India. "Trained midwife" is not a cadre anybody here
    # names — the real ones are ANM and LHV — and an ASHA or Anganwadi worker, who very often does
    # accompany a birth in these districts, would have been heard as a yes. NFHS and NITI both count
    # only a doctor, nurse, ANM, LHV or qualified midwife as SKILLED; an ASHA, an Anganwadi worker
    # and a dai are explicitly NOT. So the cadres are now the options and the deprivation rule reads
    # codes 1 and 2 only. "Don't know" is gone with it, for the reason given on anc_4_visits.
    "birthattend": {1: "Doctor", 2: "Nurse, ANM or LHV", 3: "ASHA or Anganwadi worker only",
                    4: "Dai (traditional birth attendant)", 5: "Nobody trained; family only"},
    "stance": {1: "Support", 2: "Neutral", 3: "Oppose", 98: "Prefer not to say"},
    "task3": {1: "Yes, regularly in my main Yatra work", 2: "Not in my main work, but done before elsewhere", 3: "Never done"},
    "tier": {1: "Poor", 2: "Moderate", 3: "Good"},
    # Codes 4 and 5 used to read "wage labour, staying at home" and "went away from home for work" --
    # one activity (wage labour) split across two codes on a LOCATION criterion, which no labour-force
    # classification does: ILO keeps status in employment, occupation, industry and place of work as
    # separate variables, and Apablaza's own Q5 list carries no location at all. It also destroyed the
    # activity information, since "went away" says nothing about the work done. Location is now the
    # left_here_month / returned_here_month spell, and code 5 is spent on construction — the commonest
    # off-season destination occupation for this workforce, which previously had nowhere to go.
    # Codes 1 and 9 USED TO BE ONE CODE, "Yatra work, or getting ready for the season". Splitting
    # them 2026-10-03: the two months are not the same month. Preparation is buying stock, repairing
    # tack, bringing animals up, opening a lodge -- outlay, with little or no income against it --
    # while a working month is the earning one. Lumped together they put prep months into the
    # denominator of yatra_income/yatra_months and pulled the implied monthly wage down for exactly
    # the respondents who prepare longest, which is the owners rather than the day workers. They are
    # also substantively different exposures to a ropeway: a season that opens late costs a worker
    # his earning months and costs an owner his sunk preparation either way.
    # Prep is coded 9, not 1.5, so no existing status code shifts meaning; it is listed second so it
    # still sits next to Yatra work in the picker.
    # The old reasoning for merging them, kept because it still holds for why prep needs a code AT
    # ALL rather than being left to fall into "No paid work": without it, a lodge owner
    # repairing rooms in March, a pony owner feeding animals through February, a shopkeeper buying
    # stock in April had no true option and would land on 8 (no paid work) — which is wrong, and wrong
    # in a way that reads as idleness. With the split, yatra_months is back to months of Yatra
    # EARNINGS (status 1 only) and preparation is carried separately as yatra_prep_months (status 9),
    # so the two can be added when months of Yatra livelihood is what is wanted and kept apart when
    # it is not. The consumption season weight is unaffected either way: that uses months_here, from
    # the absence spell, not this calendar.
    "activity": {1: "Yatra work (working the season)",
                 9: "Getting ready for the season (not earning from it yet)",
                 2: "Farming (crops)", 3: "Livestock (animals)",
                 4: "Casual or daily wage labour", 5: "Construction work",
                 6: "Own small shop, stall or trade", 7: "Salaried job", 8: "No paid work"},
    "yndk": {0: "No", 1: "Yes", 97: "Don't know"},
    # Apablaza Appendix 2 Q5, all eleven categories, in their order — the routing differs by code
    # (1-3 continue; 4-7 jump to the underemployment tail; 8 jumps to job search; 9-11 end the module),
    # so collapsing them loses the routing, not just the detail. Codes 4-6 are near-impossible in a
    # Yatra-worksite intercept sample; they are kept anyway so the skip logic is Apablaza's own.
    "jobsit": {1: "Works for pay full-time", 2: "Works for pay part-time or occasional jobs",
               3: "Studies and works", 4: "Only studies", 5: "Being trained for work only",
               6: "Retired or pensioned", 7: "Unpaid household tasks or caring for others",
               8: "Unemployed, actively seeking work", 9: "Sick or disabled, cannot work",
               10: "Neither studying, working nor seeking work", 97: "Does not know"},
    "jobperm": {1: "Permanent", 2: "Seasonal or temporary", 3: "Occasional or casual", 4: "On probation", 5: "Fixed-term"},
    "contract": {1: "Yes, signed", 2: "Yes, but not yet signed", 3: "No contract"},
    "pension": {1: "Yes, employer deducts it", 2: "Yes, contributes voluntarily", 3: "No"},  # orphaned 2026-10-07 by pension_any (see RETIRED)
    "workins": {1: "Yes, through work", 2: "Only private or other insurance", 3: "None", 4: "Don't know"},
    "movetype": {1: "Lateral (little retraining needed)", 2: "Upskilling (destination needs skills the worker lacks)",
                 3: "Reskilling (skill sets barely overlap)", 4: "Downskilling (worker's skills would go unused)"},
}

SRC_STD = "Standard household-survey item"
# Questions the form fills in by itself and never puts on screen. They are still real columns and
# still exported — they are simply not asked, because asking them wastes an enumerator's taps on
# something the device already knows and can get wrong:
#   enum_id    the tablet's own device id. Was a four-name picker, and the predictable failure was
#              an enumerator tapping the previous person's name, which is invisible in the data.
#   site       set once per tablet in Sheet settings, because a device stays on one route all season.
#   consent    recorded by the landing screen's Agree / Do not agree buttons, so the consent answer
#              is the act of starting the interview rather than a question asked after it.
#   form_build stamped from the build id.
# Listed here rather than flagged on each R() call so the whole set is visible in one place: a
# question quietly becoming invisible is exactly the change that needs to be easy to audit.
HIDDEN_ON_FORM = {"enum_id", "site", "consent", "form_build", "obs_environment"}

ROWS = []

# =================================================================================================
# RETIRED VARIABLES
# =================================================================================================
# Questions that were asked in a build that went to the field and are no longer asked. Their columns
# STAY in the Google Sheet and in any export already taken -- deleting them would strand the records
# that hold them. This registry is what makes those records readable afterwards, and what
# checks/14_sheet_vs_dictionary.py tests the live sheet against.
#
# The rule this registry exists to enforce: a variable whose MEANING changes gets a NEW NAME. A
# variable that is only reworded or moved keeps its name. Where a response code was ADDED to an
# existing set, the old data is less precise but not wrong, and the conflation is written down here.
RETIRED = {
    # name: (last build that asked it, what it held, what replaced it)
    "n_health_insured": ("2026-10-07", "count of health-insured household members", "health_insured_any (binary, from insurance_held) -- the count is dropped, not recoverable"),
    "n_life_insured": ("2026-10-07", "count of life-insured household members", "life_insured_any (binary, from insurance_held) -- the count is dropped, not recoverable"),
    "pension_contrib": ("2026-10-07", "3-way pension contribution: employer-deducts / voluntary / no", "pension_any -- collapsed to a binary; see dictionary note on the row"),
    "status_m1": ("2026-10-05.4b87e5", "main activity in each of 12 months, `activity` codes", "months_worked_yatra + months_no_paid_work + offseason_activity"),
    "knows_monthly_income": ("2026-10-05.4b87e5", "gate: month-by-month earnings or one annual total", "retired; everyone now gives the annual total"),
    "income_m1": ("2026-10-05.4b87e5", "net earnings in each of 12 months (Rs)", "income_annual_total + pct_income_yatra"),
    "left_here_month": ("2026-10-05.4b87e5", "month the respondent last left the route", "retired; months_here now comes off months_worked_yatra"),
    "returned_here_month": ("2026-10-05.4b87e5", "month the respondent came back", "retired, as above"),
    "n_here_season": ("2026-10-05.4b87e5", "people fed and spent on at the worksite, in season", "n_hh_same_business (a different quantity); the consumption denominator is now hhsize"),
    "family_structure": ("2026-10-05.4b87e5", "nuclear / joint / single-member", "retired; inferable from hhsize and hoh_relation if needed"),
    "n_children_out_school": ("2026-10-05.4b87e5", "children 6-14 NOT attending school", "n_children_in_school, which is the COMPLEMENT -- do not read one as the other"),
    "n_other_activities": ("2026-10-05.4b87e5", "count of other paid activities", "other_activity_types, asked directly; the count was only ever a cross-check on the list"),
    "tenure_under_1": ("2026-10-05.4b87e5", "under one year in this job (yes/no)", "years_current_job, now asked of everyone as a decimal"),
    "job_situation": ("2026-10-05.4b87e5", "Apablaza Q5, 11 categories, last month's main activity", "retired; the sample is recruited at the worksite"),
    "job_permanence": ("2026-10-05.4b87e5", "permanent / seasonal / casual / probation / fixed-term", "employers_in_season, a count of employers rather than a job type"),
    "ration_portable_here": ("2026-10-05.4b87e5", "can draw the ration here or only at the home place", "retired"),
    "uses_digital_payment": ("2026-10-05.4b87e5", "ever uses UPI or phone payment (yes/no)", "n_can_transact_online, which carries the same information and a count"),
    "loan_against_asset": ("2026-10-05.4b87e5", "loan secured against an asset (yes/no)", "loan_collateral, which gained code 0 for 'nothing given'"),
    "cope_less_pref_food_yatra_wk": ("2026-10-05.4b87e5", "rCSI day-counts, 5 items x 2 seasons, 0-7", "the five fies_* items; see the Module I note"),
    "years_in_yatra_work": ("2026-10-05.696592", "years coming to the Yatra for work -- NOT in dictionary.py at the time it was asked, and holds real values (8, 22, 15) in the first field test", "years_coming_here"),
    "obs_sex": ("pre-4b87e5", "enumerator's observation of a refuser's sex -- NEVER POPULATED, and contrary to the consent script, which promises not to record it", "nothing; delete the column"),
    "obs_age": ("pre-4b87e5", "enumerator's observation of a refuser's age -- never populated, same problem", "nothing; delete the column"),
    "obs_setting": ("pre-4b87e5", "what was happening at a refusal -- never populated", "obs_environment, which is the live one"),
    "refusal_reason": ("pre-4b87e5", "why the person refused -- never populated", "nothing; delete the column"),
}
# The three retired FAMILIES, registered in full rather than by one representative. Twelve calendar
# cells, twelve monthly earnings cells and ten rCSI day-counts are 34 columns standing in the sheet
# with real answers in them; checks/14 fails on any column it cannot account for, which is how this
# omission was caught.
for _m in range(1, 13):
    RETIRED["status_m%d" % _m] = (
        "2026-10-05.4b87e5",
        "main activity in month %d of the past year, `activity` codes 1-9" % _m,
        "months_worked_yatra + months_no_paid_work + offseason_activity")
    RETIRED["income_m%d" % _m] = (
        "2026-10-05.4b87e5",
        "net earnings in month %d, after costs (Rs). PARTIAL BY DESIGN: the calendar was made "
        "optional on 2026-10-01, and in the one field test that used it four cells of twelve were "
        "filled, with values of 1, 1, 100 and 10,000 -- do not sum these without checking how many "
        "are present" % _m,
        "income_annual_total + pct_income_yatra")
for _b in ("cope_less_pref_food", "cope_borrow_food", "cope_reduce_meals",
           "cope_reduce_portion", "cope_restrict_adult"):
    for _s in ("_yatra_wk", "_offseason_wk"):
        RETIRED[_b + _s] = (
            "2026-10-05.4b87e5",
            "rCSI day-count 0-7 for a USUAL week, not an actual one -- the WFP > 20 cutoff does "
            "not apply to it; see the Module I note",
            "the five fies_* binaries")
# Response codes ADDED to existing sets. Old records keep their meaning; they are simply coarser.
CODE_ADDITIONS = {
    "cpr_firewood": "Code 2 'No, it is not allowed here' added 2026-10-05. In rows collected before that, code 0 'No' CONFLATES not doing it with not being permitted to -- which on the Hemkund route is the only answer there was.",
    "cpr_fodder": "As cpr_firewood.",
    "cpr_forest_produce": "As cpr_firewood.",
    "cpr_grazing": "As cpr_firewood.",
    "loan_collateral": "Code 0 'Nothing was given as security' added 2026-10-05 when loan_against_asset was merged in. Before that the question was gated on that yes/no, so an absent value means 'nothing pledged' and a present value means the same thing it means now.",
    "gps_error": "Code 3 'coarse fix only' added 2026-10-05. Before that a 50 km network fix was stored with a blank gps_error, indistinguishable from a 14 m GPS fix.",
}

def R(module, name, label, question, desc, kind, lset=None, skip="", source=SRC_STD, origin="asked", formula=""):
    assert len(label) <= 80, (name, len(label))
    ROWS.append(dict(module=module, name=name, label=label, question=question, desc=desc, kind=kind, lset=lset,
                     skip=skip, source=source, origin=origin, formula=formula))

# ------------------------------------------------------------------ P  cover and paradata
R("P", "resp_id", "Respondent ID", "Assigned by the tablet.", "Unique respondent number.", "id", origin="paradata", source="Design")
R("P", "enum_id", "Enumerator", "Set automatically from the device ID.", "Which of the four enumerators did the interview. Asked as the FIRST question on the form, ahead of consent, so it is recorded even when consent is refused — a refusal is data, and which enumerator collected it is part of that data. Kept alongside Kobo's own `_submitted_by` rather than replaced by it: `_submitted_by` only separates the four if every enumerator has their own login and always uses it, while this item also works under a shared login. Where they disagree (wrong name tapped, or a device signed in as someone else) that is a data-quality flag neither could raise alone — check it on the real export.", "cat", "enum", origin="paradata", source="Design")
R("P", "site", "Pilgrimage route being surveyed", "Set automatically from the device route setting.", "Set by the enumerator before approaching anyone, alongside enum_id and ahead of consent, so it is recorded even when consent is refused. The study covers two routes now; GPS fixes the position within a route, so this one question is all that is needed to separate them. Enters the analysis as a stratifier and a fixed effect — the two routes differ in season length, altitude, employer mix, and in whether the ropeway proposal applies at all.", "cat", "site", origin="paradata", source="Project design (two-route stratification)")
R("P", "form_build", "Build stamp of the form that produced this record", "Recorded automatically.", "Which build of the form collected this interview: the date plus a short hash of the question set. A service worker can serve a stale copy of the page indefinitely, and a stale build is indistinguishable from the current one once it is on a tablet — three issues in one field review had already been fixed and the reviewer had no way to know. Stamped into every exported row so a report can be matched to a build.", "text", origin="paradata", source="Project design (build provenance)")
R("P", "interview_date", "Interview date", "Recorded automatically.", "Date of interview.", "date", origin="paradata", source="Design")
# location_cluster dropped 2026-09-24: it asked the enumerator to hand-code the interview site into
# one of four route clusters, which the silently captured GPS below already records more precisely.
# health_access_tier is now derived from gps_lat in Stata. Net effect: one fewer action per interview,
# a continuous rather than categorical location input, and no named site in the exported data either way.
R("P", "gps_lat", "GPS latitude of interview", "Recorded automatically.", "Latitude of the interview location.", "num", origin="paradata", source="Design")
R("P", "gps_lon", "GPS longitude of interview", "Recorded automatically.", "Longitude of the interview location.", "num", origin="paradata", source="Design")
R("P", "consent", "Respondent gave informed consent", "Recorded from the landing screen's consent buttons.", "Consent given after the script was read.", "bin", "yn", origin="paradata", source="Design")

# Refusals. A person who says no is still recorded, with only what the enumerator can see. Their
# refusal is data: the people who decline are systematically different, and without a record of
# them the interviewed sample cannot be corrected for who was missing (see the selection note in
# do/02_build_final_dataset.do). Asked ONLY when consent = 0.
R("P", "obs_environment", "Conditions where the person was approached (refusals only)", "Pick what was happening at the time. Do not ask the person.", "Recorded by the enumerator when consent is refused, with the timestamp, the enumerator and the route. Only the conditions at the time are recorded (crowding, weather). No personal characteristics and no location of the person are recorded for a refusal.", "cat", "obsenv", skip="Ask only if consent = 0", origin="paradata", source="Design: refusal record, limited to environmental conditions")
# Precise location. Written by the tablet from the best GPS fix obtained, not from a coarse network fix.
R("P", "gps_accuracy_m", "GPS accuracy of the location fix (metres)", "Recorded automatically.", "The accuracy the device reports for the fix that was kept. The form keeps refining the fix for up to 90 seconds and stops at 15 metres. A fix of 50 metres or worse is flagged in the export so it can be checked.", "num", origin="paradata", source="Design")
R("P", "gps_fix_s", "Seconds taken to get the location fix", "Recorded automatically.", "How long the device took to produce the fix that was kept. A long fix is a sign of a weak signal.", "num", origin="paradata", source="Design")
R("P", "gps_error", "Location problem, if no fix was obtained", "Recorded automatically.", "1 = the browser was not allowed to use location; 2 = no fix was obtained. Blank when a fix was obtained.", "cat", "gpserr", origin="paradata", source="Design")
R("P", "interview_duration_min", "Interview length (minutes)", "Recorded automatically (start to end).", "Total interview time, from the tablet's own start and end timestamps. Recorded for analysis; no time limit is set.", "num", origin="paradata", source="Design")
R("P", "dur_tasks_min", "Time spent on tasks block L (minutes)", "Recorded automatically (module timestamps).", "Time for the short task and papers block; tracks the burden of the transferability add-on.", "num", origin="paradata", source="Design")

# ------------------------------------------------------------------ A  respondent and household
R("A", "age", "Age in completed years", "How old are you? (completed years)", "Respondent age; 18 to 70 covered.", "num", source="Standard; sensitivity covariate in the VEP model (Azeem et al. 2016 structure)")
R("A", "female", "Female (1) or male (0)", "Record sex; ask if unsure: are you male or female?", "Sex of the respondent.", "bin", "sex")
R("A", "hoh_relation", "Respondent's relationship to the head of household", "Who is the head of your household — is it you, or someone else? If someone else, how are they related to you?", "Who the head of household is, relative to the respondent. The categories are GENDERED (husband/wife, son/daughter, father/mother, brother/sister), so the head's sex falls out of this answer and no separate male/female question is asked — one question instead of two, and it matches how people actually answer: nobody says 'my parent', they say 'my father'. Hindi kinship terms are gendered too, so the Hindi wording needs no adjustment. Asked openly and coded from the answer, not read off a list.", "cat", "hohrel")
R("A", "native_language", "Native language / mother tongue", "What is your native language, the language you first learned at home?",
  "Mother tongue, used in place of a caste/social-group question: caste is sensitive to ask directly and does not classify non-Indian migrants (Nepali workers) in any comparable way. Language instead captures regional origin, which correlates with the class variation caste would have picked up, and applies to every respondent.",
  "cat", "nativelang", source="Project design (language proxy for regional/socioeconomic origin; avoids a sensitive caste question and covers out-of-country migrants)")
R("A", "native_language_other", "Native language, written in (not on the list)", "Which language is it? Write down exactly what they say.", "Free-text catch-all for the two 'other' codes. IMPORTANT ITEM: this is the only proxy the instrument has for regional and social origin — it replaced the caste question — so an answer left as bare 'other' loses that information for that respondent. The list is long but India is longer; enumerators must type the actual language rather than settle for the catch-all code.", "text", skip="Ask only if native_language is 96 (other Indian language) or 97 (other / foreign language)", source="Project design (the language item stands in for caste; an uncoded 'other' is a real loss)")
R("A", "origin", "Place of permanent home", "Where is your permanent home?", "Origin of the respondent, as four buckets. Note what it does NOT measure: the pilot found 11 of 20 seasonal movers inside this same district, so this is a distance variable, not a mobility one. closure_base and the Module C location row carry mobility.", "cat", "origin", source="Project design (distance bucket); NOT an NSS classification — the earlier citation to one was withdrawn 2026-09-28, no NSS schedule is held by this project")
R("A", "home_state", "State or union territory of the permanent home", "Which state or union territory is your permanent home in?", "State/UT of the permanent home, asked of EVERYONE as of 2026-10-05 and placed next to the native-language question. It was gated on origin = 3 and filled in Stata for the other three codes, on the reasoning that local, other-Uttarakhand and Nepal each entail their own answer. They do, but the gate also made home_state missing for 178 of 200 rows while it sat in a covariate vector, and the enumerator was being asked to infer a state from a language, which Hindi and Garhwali do not settle. Asked directly it is one tap and it is measured. The state is the level at which India sets its rural and urban poverty lines, which is why it is here at all.", "cat", "state", source="Standard state/UT classification; needed to apply the right poverty line per respondent")
R("A", "home_rural_urban", "Usual home is in a village (1) or a town/city (2)", "Is that home in a village, or in a town or city?", "Rural/urban status of the permanent home, asked directly as the binary the poverty line actually needs. Replaces home_admin_level, a three-way village/town/city item that asked the respondent to perform a Census classification they have no way of making, and then selected a Rs 2,515 or Rs 3,639 line off the answer. Also stops being a constructed variable: it was derived from home_admin_level, which meant a 45% swing in the threshold rested on a derivation from a subjective tier.", "cat", "ruralurban", source="Rural and urban poverty lines (Sethu et al. 2024)")
R("A", "marital_status", "Marital status", "Are you currently married, never married, or widowed/divorced/separated?", "Marital status of the respondent.", "cat", "marital")
R("A", "knows_years_schooling", "Knows exact years of schooling completed", "Do you know exactly how many years of schooling you completed, counting from class 1?", "Gates whether years_schooling or the fallback bracket (education_level_cat) is asked. Minimises categorical questions: a direct year count is asked first, and only respondents who cannot recall get a category.", "bin", "yn")
R("A", "years_schooling", "Years of schooling completed", "How many years of schooling did you complete in total? (0 if none)", "Direct year count; feeds the MPI education indicator. Preferred over a level/category, which loses information a plain number does not.", "count", skip="Ask only if knows_years_schooling = 1", source="NITI Aayog National MPI (years of schooling); Chaudhuri et al. 2002 covariate")
R("A", "education_level_cat", "Highest level of school completed (bracket, if years not recalled)", "Which is closest: no formal education; some schooling but did not finish primary; finished primary but not secondary; or finished secondary or higher?", "Fallback bracket, asked only when the respondent cannot give an exact year count. Kept to four categories (plus prefer-not-to-say) to minimise categoricals.", "cat", "edu2", skip="Ask only if knows_years_schooling = 0", source="NITI Aayog National MPI (years of schooling); Chaudhuri et al. 2002 covariate")
R("A", "training_received", "Ever completed a training course or apprenticeship", "Apart from school and college, have you ever completed any training course or apprenticeship?", "Vocational or on-the-job training, explicitly EXCLUDING school AND college. The old wording said only \"not counting school\", which left it ambiguous whether a degree counted — some respondents would have reported a BA here. Formal education is already measured in years by years_schooling (a graduate reports about 15), so counting it again here would double-count it.", "bin", "yn", source="STEP module 2; Chaudhuri et al. 2002 adaptive-capacity covariate")
R("A", "hhsize", "Household size (number of members)", "How many members live in your household, including you?", "Household size in the usual place of living. Aggregate count; no household roster.", "count", source="Chaudhuri et al. 2002; used to get per-capita consumption")
R("A", "any_member_6yr_schooling", "Any household member aged 10+ has completed 6 years of schooling", "Counting everyone in your household aged 10 or above, has at least one of them finished six years of schooling or more?", "NITI's Years of Schooling indicator is defined on the HOUSEHOLD — 'not even one member aged 10 years or older has completed six years of schooling' — not on the respondent. Using the respondent's own education_years in its place, as this instrument previously did, measures a different thing and is not comparable to any published National MPI figure. NOT ASKED where the respondent's own schooling already settles it: the respondent is himself a member aged 10 or over, so six years or more of his own is a Yes by entailment and Stata fills it. The bracket route can only settle it at 'completed secondary or higher' — 'completed primary but not secondary' spans 5 to 9 years and straddles the threshold, so it does not, and the question is asked.", "bin", "yn", skip="Ask only if the respondent's own schooling does not already settle it: years_schooling < 6, or the bracket is not 'completed secondary or higher'", source="NITI Aayog National MPI, Years of Schooling (weight 1/6)")
# Split at 6 and 14, not at 15 and 6-14. The old pair asked "how many under 15" and then "how many
# aged 6 to 14", which is the same children counted twice with the under-6s left implicit — the
# respondent has to subtract to answer the second, and the two can contradict each other (a dq flag
# existed purely to catch that). Two disjoint bands instead: under-6 and 6-to-14 partition the
# under-15s exactly, so n_children_u15 is now CONSTRUCTED as their sum and the adult-equivalent
# scale is unchanged. The under-6 band is also the age range NITI's Nutrition indicator is defined
# on (children 0-59 months), so it is the denominator for the nutrition discussion rather than a
# number nothing uses.
R("A", "n_children_u6", "Household children under 6", "How many of them are children under 6 years old?", "Count of children under 6. With n_children_6_14 this partitions the under-15s into two disjoint bands, so neither question asks the respondent to subtract one from the other. Also the age band NITI's Nutrition indicator covers (0-59 months), which is why the band is drawn at 6 rather than 5.", "count", source="Adult-equivalent scales (Claro et al. 2010; Awuni et al. 2023); NITI Aayog National MPI nutrition age range")
R("A", "n_children_6_14", "Household children aged 6 to 14", "And how many are aged 6 to 14?", "Count of school-age children. Disjoint from n_children_u6 above, so the two add to the under-15 count rather than overlapping it.", "count", source="NITI Aayog National MPI school-attendance indicator")

# ------------------------------------------------------------------ B  work, season, history
R("A", "n_children_in_school", "Children aged 6 to 14 attending school", "How many of these children go to school now?", "Count of school-age children who DO attend. Asked as the positive, replacing n_children_out_school (retired 2026-10-05) which asked how many do NOT: a negative count is the harder of the two to answer and the easier to mis-hear, and a respondent who says \"all of them go\" has to be talked into reporting a zero. mpi_attendance_dep is built from the complement, n_children_6_14 - n_children_in_school, so the NITI indicator is unchanged. The name is new BECAUSE the quantity is inverted -- the 2026-10-05 field rows hold the old variable and must not be read as this one.", "count", skip="Ask only if n_children_6_14 > 0", source="NITI Aayog National MPI school-attendance indicator")
R("A", "n_earners", "Number of household members who earn money", "How many of them, including you, earn money?", "Earners in the household, including the respondent.", "count", source="Dependency measure used in VEP studies (Azeem et al. 2016)")
R("A", "main_income_earner", "Respondent is the main income earner in the household", "Among those who earn money, are you the main income earner in your household?", "Whether the respondent is the household's main earner.", "bin", "yn", skip="Ask only if n_earners > 1 (if the respondent is the only earner, this is automatic)", source="Apablaza et al. 2026, Appendix 2 Q4 (adapted to a single-respondent report: 'who is the main contributor' becomes 'are you the main contributor')")
R("B", "occupation", "Main work in the Yatra season (14 groups)", "What is your main work during the Yatra season? Ask what they do and code the closest group; do not read the list aloud unless needed.", "Quota variable: 14 occupation groups, rebuilt against NCO-2015 (see the occ list). Deliberately a COARSE grouping — it exists to manage sampling quotas and to be stable across the fieldwork, not to describe the job. The precise occupation is captured verbatim in occupation_detail below and coded to NCO afterwards, so nothing is lost by this list being broad.", "cat", "occ", source="Project quota design, mapped to NCO-2015 families")
R("B", "occupation_detail", "Main work, in the respondent's own words (NCO-coded later)", "In your own words, what exactly is your main work here? Write down what they say — what they actually do, and who for. Do not tick a box for this one.", "Verbatim description of the primary livelihood, office-coded to NCO-2015. IMPORTANT ITEM: the 14 groups above are deliberately coarse, so this is the ONLY place the real occupation is recorded, and it is what the task-distance and structural-displacement analysis is coded from. 'Shop owner' could be a man selling prasad from a plank or a family running a three-storey general store; only this field tells them apart. Same treatment as prev_occ and target_occ, so all three code into one classification.", "text", source="Project design (coarse quota group + verbatim detail, coded to NCO-2015 in the office)")
R("B", "employment_type", "Employment status in main work (4 groups)", "In this main work, are you: working on your own account without hired workers; running a business with hired workers; a regular monthly wage-earner; or a daily/casual wage-earner?", "PLFS-style status: own-account, employer, regular wage, casual wage.", "cat", "emptype", source="PLFS / NSS employment status classification [source not held by this project; citation unverified as of 2026-09-28]")
R("B", "wage_employer", "Who employs the wage worker", "Who employs you? A private company; a government or public body; a household (domestic work); a contractor or agent; or an individual employer?", "Employer type for wage workers only, kept in case the sample needs it. Replaces the full Apablaza Q8 list, which crosses status with sector. Enumerator definitions are in HINTS.", "cat", "wageemp", skip="Ask only if employment_type is 3 or 4 (regular or casual wage worker)", source="Apablaza et al. 2026, Appendix 2 Q8 (shortened to wage workers); categories ours")
MULTIWORK = ("Multiple work-holding, asked as a count first and then as a check-all list. The previous "
             "version allowed ONE other activity, which undercounts by construction: a shop owner who "
             "also rents out a pony and drives in the off-season has three, and only one was recorded. "
             "The count is asked before the list so it can be checked against the number of boxes "
             "ticked — a mismatch is a data-quality flag, not a silent loss.")
R("B", "other_activity_types", "Which other paid activities (check all that apply)", "Besides your main work, what other paid work do you do during the Yatra season? Check every one that applies; leave blank if there is none. Ask and code the closest group for each; do not read the list aloud unless needed.", "Check-all list of the other activities. " + MULTIWORK + " Exported by Kobo as a space-separated string plus one binary column per choice; Stata splits it into other_act_1 to other_act_13.", "multi", "occ", skip="May be left blank", source="Project design (multiple job-holding, common in the Yatra economy)")
R("B", "other_activity_income_pm", "Usual monthly income from all other paid activities (Rs)", "Taking all of that other work together, about how much do you usually earn from it in a month? (Rs; leave blank if there is no other work)", "Combined monthly income from all the other activities. Asked as one combined figure rather than per activity: per-activity amounts would multiply the question count for a quantity that enters the analysis only as a total.", "money", skip="May be left blank", source="Project design (multiple job-holding)")
R("B", "owns_shop_stall", "Owns a shop or stall used for work", "Does your household own a shop or stall that you use to earn?", "Productive asset. Moved from Module F to Module B on 2026-10-05: asked here, beside the other-activities list, it tells the enumerator early what kind of secondary activity the respondent has, which is exactly the coding decision the other-activities list needs and which arriving 100 questions later could not inform.", "bin", "yn", source="Chaudhuri et al. 2002 asset covariate")
R("B", "employers_in_season", "Different employers or businesses worked in, one Yatra season", "During one Yatra season, how many different employers or businesses do you work in? (1 if you stay with the same one, or run the same one, all season)", "Within-season churn, asked as a count of employers or businesses rather than as a job TYPE. Replaces job_permanence (retired 2026-10-05), Apablaza's permanent/seasonal/casual/probation/fixed-term item, which could not work here: every job on this route is seasonal in the ordinary sense because the Yatra closes, so both enumerator and respondent reached for \"seasonal\" regardless, and the distinction the indicator needed -- one employer for a stretch versus work taken day by day -- was lost. It also had no sensible answer for own-account workers, who are most of the sample. A count of employers answers the same question factually and for both: 1 means a stretch, several means day-to-day. Asked here, beside the occupation block, rather than in Module K.", "count", source="Apablaza et al. 2026 Appendix 2 Q7 (concept: job stability within the engagement); asked as a count per this project's no-scale rule")
R("B", "years_current_job", "Years in the current job (one year or more)", "How many years have you been in this current job? Write it as a decimal if needed, for example 1.5 for one year and six months, or 0.5 for six months.", "Tenure in the current job in years, as Apablaza et al. (2026) Q10 asks. Asked only when the respondent is NOT under one year (tenure_under_1 = 0). Decimals allowed, so the Table 3 thresholds apply directly to values of one year or more. Placed next to years_coming_here (2026-10-07) so the two tenure questions, which read as the same question to most respondents, sit together with a shared note instead of fourteen rows apart.", "num", source="Apablaza et al. 2026, Appendix 2 Q10; Table 3 (stability)", skip="")
R("B", "years_coming_here", "Years the respondent has been coming here for Yatra-related work", "And in total, how many years have you been coming here for Yatra-related work?", "Duration of the relationship with this worksite, which years_current_job does not give on its own: that counts seasons in the CURRENT kind of work, so a porter who spent six years portering and then four running a stall reads as four, while this counts all ten. For a respondent who never changed trade at this site the two answers are the same number, which is why they are asked right after each other with a shared enumerator note rather than apart, as they were through 2026-10-06 (then Module D, gated on resp_returns_at_closure). The gate is dropped along with the move: it excluded a worker who stays at the worksite all year, who has a years-here answer just as real as a seasonal worker's. A first-year worker has neither the network nor the savings of a fifteen-year one, and that is an exposure term the VEP model wants.", "count", skip="May be left blank -- most respondents will give the same number as years_current_job just above; the enumerator does not need to re-ask if the respondent already said so", source="Project design (duration of the seasonal relationship)")
R("B", "first_job_ever", "Current/most recent work was the respondent's first job ever", "Was your current work the first paid job you ever had?", "Ever had a prior job at all — a coarse mobility/entry marker. Moved next to the two tenure questions (2026-10-07): it is a work-history bio item asked of everyone, like them, not a job-quality item, so it belongs with years_current_job and years_coming_here rather than in the job-quality block.", "cat", "yndk", source="Apablaza et al. 2026, Appendix 2 " + "Q24")
R("B", "hours_day_yatra", "Hours worked per day in the Yatra season", "In the Yatra season, on a normal working day, how many hours do you work in total, across all your work?", "Usual daily hours, all jobs. Asked as hours/day and days/week separately (not as one 'hours a week' figure) and multiplied in Stata: a normal day is easier to picture than a whole week at once.", "count", source="Apablaza et al. 2026 Q13 (decomposed into hours/day x days/week rather than asked as one weekly figure, for ease of recall)")
R("B", "days_week_yatra", "Days worked per week in the Yatra season", "How many days a week do you usually work in the season?", "Usual working days per week.", "count", source="Apablaza et al. 2026 Q13 (decomposed into hours/day x days/week rather than asked as one weekly figure, for ease of recall)")
OFFH = ("Apablaza's access-deprivation test has an under-20-hours-a-week limb, but asking hours only "
        "for the Yatra season made that limb unfireable: in season this workforce runs 60-90 hours a "
        "week, so nobody ever cleared it and the whole indicator collapsed onto the months-without-work "
        "limb. Off-season hours are where marginal, part-week work actually shows up for a seasonal "
        "workforce.")
R("B", "prev_occ_change", "Changed main kind of work in the last 10 years", "In the last ten years, did you change your main kind of work?", "Occupational change flag.", "bin", "yn", source="Occupational mobility check; job-history item")
NCONOTE = ("Recorded as free text in the respondent's own words, NOT coded to a list in the field. The "
           "13-group Yatra occupation list cannot hold work done outside this economy — farming in Bihar, "
           "driving in Dehradun — and those are exactly the moves the analysis needs to see. Office-coded "
           "to NCO-2015 afterwards, which also puts these answers in the same classification as the "
           "regional employment weights. Enumerator writes what the respondent says, including the "
           "industry if given (e.g. 'drove a tempo for a hotel', not just 'driver').")
R("B", "prev_occ", "Previous main work (verbatim, NCO-coded later)", "What was your previous main work? Write down exactly what they say, in their words — do not pick from a list.", "Occupation before the change. " + NCONOTE + " Gives the observed occupational moves that validate the task-distance measure against the random-mobility benchmark.", "text", skip="Ask only if prev_occ_change = 1", source="Gathmann and Schonberg 2010 (observed moves are systematically shorter than random moves — the validation test for a task-distance measure); coded to NCO-2015 in the office")
R("B", "target_occ", "Work the respondent wants to move to in a few years (verbatim, NCO-coded)", "Looking ahead a few years, what work would you like to be doing? Write down exactly what they say, in their words — do not pick from a list, and do not prompt with examples. If they want to carry on exactly as they are, write that.", "Stated ASPIRATION occupation. " + NCONOTE + " Reworded 2026-10-05 from a counterfactual (\"if you could not continue this work, what would you move to\") to a forward-looking intention. The counterfactual was answered with the off-season occupation the respondent already has, which Module C records anyway, so it measured nothing new; and a hypothetical about losing one's livelihood, put to someone whose livelihood a ropeway may end, is a question people answer defensively. WRITE-UP CONSEQUENCE: this is now stated intent, not a revealed alternative, so the task-distance comparison is an aspiration-versus-capability gap and must be labelled that way -- it is no longer a displacement destination. 'Don't know' and 'carry on as I am' are both substantive answers; record them as said.", "text", source="Project design (stated destination, for the structural-displacement analysis); coded to NCO-2015 in the office")
R("B", "prev_occ_reason", "Main reason for changing work", "What was the main reason you changed?", "Reason for the last change.", "cat", "prevreason", skip="Ask only if prev_occ_change = 1", source="Job-history item")

# ------------------------------------------------------------------ C  income and remittances
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
# Presentation order, NOT variable order. status_m1 is still January and every downstream month
# calculation is unchanged — what moves is the sequence the enumerator is walked through. The
# calendar used to open on January and then instruct "fill the Yatra months first, then the others",
# which is an instruction the form cannot obey: it shows one question per screen in dictionary order.
# Opening at the season instead makes the instruction unnecessary, because the order IS the
# instruction, and it starts recall at the months the respondent remembers best. May is the opening:
# the Yatra runs from Akshaya Tritiya to Bhai Dooj, so late April or May through November.
# The twelve-month activity calendar and the twelve monthly earnings questions were both cut on
# 2026-10-05. Twenty-four questions, and the first field test showed why they could not stand: of
# seven real interviews, three took the annual-total route rather than answer month by month, and
# one of the four who tried the calendar filled four cells of twelve -- with values of 1, 1, 100 and
# 10,000 rupees. A calendar answered a third of the way is worse than an annual total, because
# yatra_income is then summed over whichever cells happened to be filled.
#
# What replaces them is three questions for the calendar and one for earnings. Nothing that the
# downstream construction needs is lost: yatra_months, months_no_work, offseason_months_worked and
# offseason_primary were each a single count or mode over the twelve cells, and are now asked
# directly. See REBUILD_2026-10-05.md for income_seasonality_cv, which survives because its
# fallback path was already a closed form in the annual total and the Yatra share.
R("C", "months_worked_yatra", "Months worked in the Yatra season in the past year",
  "In the past year, how many months did you work here in the Yatra season? Count the months you "
  "spent getting ready for it as well.",
  "Length of the respondent's OWN season, asked rather than counted off a twelve-cell calendar. "
  "Preparation months are deliberately INSIDE this count: buying stock, repairing tack and bringing "
  "animals up is the trade, the old calendar gave it its own code 9, and separating it bought one "
  "constructed variable (yatra_prep_months) that no analysis read. This is the season weight -- it "
  "carries every consumption and income figure in the study -- so it is asked first and asked plainly.",
  "count", source="Project design (replaces the twelve-cell status calendar, 2026-10-05)")
R("C", "months_no_paid_work", "Months in the past year with no paid work at all",
  "And in the past year, how many months did you have no paid work at all?",
  "Idle months, asked directly. Was counted as the number of calendar cells coded 8. Feeds "
  "months_no_work, which gates the job-search question and is the Apablaza unemployment limb.",
  "count", source="Project design (replaces the twelve-cell status calendar, 2026-10-05)")
R("C", "offseason_activity", "Main work in the months that are neither Yatra nor idle",
  "In the remaining months — not the Yatra season, and not the months with no work — what was your "
  "main work? Code the closest one.",
  "Principal off-season activity, asked rather than taken as the mode of the non-Yatra calendar "
  "cells. Replaces the constructed offseason_primary, which is now this variable. Code 0 is the "
  "genuine none: a respondent whose Yatra months and idle months already account for all twelve.",
  "cat", "offact",
  skip="May be left blank if the Yatra months and the idle months already account for all twelve",
  source="Project design (replaces the modal non-Yatra calendar cell, 2026-10-05)")
R("C", "income_annual_total", "Total earnings from all work in the past year (Rs)",
  "Thinking of the whole past year, about how much did you earn in total from all your work, after "
  "costs? (Rs)",
  "The single earnings question. Was the fallback route behind the knows_monthly_income gate, taken "
  "by three of seven respondents in the first field test; it is now the only route, because the "
  "twelve-month version was not answerable in the time available and a partly-filled calendar is "
  "not recoverable. MAY BE LEFT BLANK: earnings are a covariate in the vulnerability models, not an "
  "identifying variable, so a refusal costs a control rather than the case, and a required earnings "
  "question would have ended interviews.",
  "money", skip="May be left blank if the respondent declines to discuss earnings",
  source="Apablaza et al. 2026 Q15 (annual-total fallback), adapted to a seasonal workforce and now the only earnings route")
R("C", "pct_income_yatra", "Share of the year's earnings that came from Yatra work (out of 100)",
  "Out of every 100 rupees of that, how many came from your Yatra work? (The rest is counted as "
  "coming from your other work.)",
  "Yatra / non-Yatra split of the annual total. Asked as 'out of every 100 rupees of that' rather "
  "than as a percentage: the same number, in a form that does not ask the respondent to hold an "
  "abstract scale, and worded to refer back to the total just given. Together with "
  "months_worked_yatra this is what rebuilds a monthly earnings profile, and it is also what makes "
  "income_seasonality_cv computable without a calendar -- the CV of the implied two-level series is "
  "a closed form in this share and the season length, with the rupee amount cancelling out.",
  "count", skip="Ask only if income_annual_total was given; may be left blank",
  source="Project design (the Yatra / non-Yatra split needed to reweight an annual total onto the season)")
R("C", "earnings_range", "Range of monthly earnings (only where no annual figure was given)",
  "Which range is closest to what you usually earn in a month from work? Under Rs 5,000; Rs 5,000 "
  "to 10,000; Rs 10,000 to 20,000; Rs 20,000 to 35,000; Rs 35,000 to 50,000; Rs 50,000 or more; or "
  "don't know?",
  "Apablaza et al. (2026) Q15 range, now gated on the annual total being left blank -- it is the "
  "last resort for a respondent who will not give a figure but will accept a band. Two bands added "
  "2026-10-07: the open top band flattened a shop or lodge owner's earnings against a porter's, "
  "which lost real variation and mattered more once this item became the refusal fallback.",
  "cat", "earnrange",
  skip="Ask only if income_annual_total was left blank; may be left blank",
  source="Apablaza et al. 2026, Appendix 2 Q15; bands to check")
SEAS = ("Most workers here are migrants, so a single recent-recall figure would describe only the season in which the interview happens to fall. Asked as a usual monthly amount for each of the two seasons instead, matched to the Yatra-season/off-season split already used for the work calendar.")
R("C", "hours_day_offseason", "Hours worked per day outside the Yatra season", "In the months when the Yatra is closed and you are doing other work, on a normal working day, how many hours do you work in total?", OFFH, "count", skip="Ask only if there are months that are neither Yatra nor idle (12 - months_worked_yatra - months_no_paid_work > 0)", source="Apablaza et al. 2026 Q13, asked a second time for the off-season (decomposed as hours/day x days/week, as in the Yatra-season pair)")
R("C", "days_week_offseason", "Days worked per week outside the Yatra season", "In those months, how many days a week do you usually work?", OFFH, "count", skip="Ask only if there are months that are neither Yatra nor idle (12 - months_worked_yatra - months_no_paid_work > 0)", source="Apablaza et al. 2026 Q13, asked a second time for the off-season")

# ------------------------------------------------------------------ D  migration

# ---- what happens at closure -----------------------------------------------------------------
# NOT gated on origin. The gate this block originally carried — "ask only if origin is not Local" --
# was wrong in the direction that destroyed the module: 11 of the 20 seasonal migrants in the pilot
# were from this same district (pilot/livelihood_clean.dta, residency_pattern x local), so gating on
# non-local would have skipped most of the people who actually move. Seasonal movement here is mostly
# LOCAL movement, up-valley for the season and down-valley at closure, and a migrant dummy built on
# district boundaries measures almost none of it.
# closure_base was one question doing two jobs. Its stem — "do you and your household stay here, or
# go to your home place?" — named two subjects in a single breath and offered a binary while the
# options were four, so a respondent had to parse a compound before answering. Split into the two
# facts it was compressing. The same four cells come out, in Stata, from two plain yes/no answers.
R("D", "resp_returns_at_closure", "Respondent goes to the home place when the Yatra closes", "When the Yatra closes for the season, do YOU go to your home place?", "Whether the RESPONDENT moves. This is the assumption the whole two-season design rests on: every consumption, remittance and coping item in Modules C, E and I is asked twice on the premise that he is somewhere else once the Yatra shuts. The pilot suggests it is false for a large minority — 23 of 46 respondents lived here year-round.", "bin", "yn", source="Project design; categories from the pilot's own residency_pattern distribution (n=46)")
R("D", "hh_at_home_place", "The rest of the household lives at the home place year-round", "For most of the year, do the rest of your household live in your home village or town?", "Whether the household normally lives at the home place or away from it. The wording used to be \"do they live at your home place all year, or are they here with you during the season\", which forces a binary between two options that neither exhaust the cases nor oppose each other — a household can be at the home place for most of the year and at neither pole of that question. Asked now as the plain fact the design needs: is the rest of the household usually at the hometown. Everything else (here with him, a third place, split between two) falls into No and is picked up by n_here_season. Module E's Yatra-season wording (\"you and anyone staying with you here\") is written for exactly the split case and until now had nothing to key off; the pilot found 3 of 46 working here with family elsewhere. Also fixes a real error in the consumption aggregate — see n_here_season.", "bin", "yn", source="Project design (split-household measurement, underpinning Module E)")
# ---- remittances. MOVED here from Module C on 2026-10-03. They were asked in the income module,
# which reads naturally but put them ahead of the questions they depend on: whether the respondent
# goes home when the season closes, and whether his household is at the home place at all. A gate
# cannot look forward, so the off-season item could not be gated where it stood. Asked here they
# follow directly on from establishing where the family actually is, which is also the better
# interview -- you have just talked about who is at home, and now you ask what he sends them.
R("D", "remit_differs_by_season", "Amount sent home differs between the seasons", "Is the money you send home different in the Yatra season from when the Yatra is closed?", "Gate for the off-season remittance figure, on the pattern already used for consumption (spend_differs_by_season). An obligation to a household at home does not usually move with the season -- it is a fixed claim on whatever is earned -- so asking the same amount twice spent a question to collect a repeat of the first answer in most interviews. Where it does differ the second figure is asked, and where it does not Stata carries the Yatra-season figure across. Replaces the old gate on resp_returns_at_closure, which was the wrong test twice over: it asked the off-season figure only of respondents who do NOT go home, although a man who goes home may still send money to a wife elsewhere, and it hid the figure from everyone who does.", "bin", "yn", source="Project design (mirrors spend_differs_by_season, Module E)")
R("D", "remit_out_yatra_pm", "Money usually sent home in a month, Yatra season (Rs)", "In a normal month during the Yatra season, how much money do you usually send to family or others living elsewhere? (Rs, 0 if none)", "Outward remittances, Yatra-season month. " + SEAS, "money", source="Project design (amount only; frequency dropped for length). A previous citation to NSS 64th Round practice was withdrawn 2026-09-28: no NSS schedule is held by this project and it could not be checked")
R("D", "remit_out_offseason_pm", "Money usually sent home in a month, off-season (Rs)", "In a normal month when the Yatra is closed, how much do you usually send? (Rs, 0 if none)", "Outward remittances, off-season month. GATED from 2026-10-03 on the respondent still being away: someone who goes home when the Yatra closes is living with the people he would be sending to, so “how much do you send home in a normal closed-season month” has no referent and the honest answer, 0, is indistinguishable in the data from a migrant who sends nothing. " + SEAS, "money", skip="Ask only if remit_differs_by_season = 1", source="Project design (amount only; frequency dropped for length). A previous citation to NSS 64th Round practice was withdrawn 2026-09-28: no NSS schedule is held by this project and it could not be checked")
R("D", "remit_mode", "How money is usually sent home", "How do you usually send it?", "Channel, not just amount. Bank and UPI transfers are near-costless and traceable; money orders and hand-carrying cost a fee, a trip, or both, and hand-carrying ties the transfer to someone physically travelling. Two households sending the same rupees are not equally well served.", "cat", "remitmode", skip="Ask only if remit_out_yatra_pm > 0 or remit_out_offseason_pm > 0", source="Project design (remittance channel as a financial-inclusion and cost measure)")
R("D", "remit_in_yatra_pm", "Money usually received in a month, Yatra season (Rs)", "In a normal month during the Yatra season, how much money do you usually receive from family or others? (Rs, 0 if none)", "Inward remittances, Yatra-season month. " + SEAS, "money", source="Project design (amount only; frequency dropped for length). A previous citation to NSS 64th Round practice was withdrawn 2026-09-28: no NSS schedule is held by this project and it could not be checked")
R("D", "remit_in_offseason_pm", "Money usually received in a month, off-season (Rs)", "In a normal month when the Yatra is closed, how much do you usually receive? (Rs, 0 if none)", "Inward remittances, off-season month. NOT gated, unlike its outward twin: money can arrive from a son or brother working elsewhere whether or not the respondent himself has gone home, so there is no case in which the question stops making sense. " + SEAS, "money", skip="Ask only if remit_differs_by_season = 1", source="Project design (amount only; frequency dropped for length). A previous citation to NSS 64th Round practice was withdrawn 2026-09-28: no NSS schedule is held by this project and it could not be checked")
R("D", "smartphone_owned", "Owns a smartphone", "Do you own a smartphone?", "Smartphone ownership. Moved next to remittances (2026-10-07): this is the first place money-movement comes up in the interview, which is where a digital-capability question reads most naturally.", "bin", "yn", source="VEP adaptive-capacity covariate; STEP digital items")
R("D", "n_can_transact_online", "Household members who can pay by phone unaided", "How many people in your household can make a payment by phone themselves, without help? (0 if none)", "Household digital capability rather than the respondent's own use: it says who in the household can actually move money, and therefore something about who controls it. Moved next to remittances and smartphone ownership (2026-10-07) for the same reason.", "count", source="Project design (intra-household financial capability)")
# NOTE the module: these are hours questions and belong with the others in B, but they are gated
# on the work calendar, which is asked HERE in C. A question placed before its own gate can
# never be shown — so they live where the gate is answered, not where they read best.

R("D", "n_hh_same_business", "Household members working in the same business or establishment", "How many people from your household work in the same business or establishment as you, counting yourself?", "Household labour concentrated in one enterprise, which is the exposure that matters for a ropeway: a household with four members on one dhaba loses four incomes to one shock, and a household with four in four trades loses one. Replaces n_here_season (retired 2026-10-05), which asked how many people the respondent feeds here and served as the per-capita denominator for in-season consumption. That denominator is now hhsize for both seasons, matching the household-level wording Module E moved to on the same date -- one reference unit on both limbs instead of a split one. n_here_season also drew a 58 against a household of 4 in the first field test, being unconstrained.", "count", source="Project design (enterprise concentration of household labour, 2026-10-05)")
R("D", "came_here_reason", "Main reason for first coming here to work", "What was the main reason you first came here to work?", "Push or pull, kept separate from prev_occ_reason, which is about changing WORK — the old combined item gave a migrant who took a new job on arrival two true answers. Someone driven here by debt or by land too small to live on is in a different position from someone drawn by better pay, at identical current earnings.", "cat", "comereason", skip="Ask only if origin is not Local (same district)", source="Project design (push/pull as a vulnerability covariate)")
R("D", "came_here_reason_other", "Main reason for coming, written in (not on the list)", "What was that reason? Write down what they say.", "Free text behind code 8, “some other reason”. OPTIONAL: left blank it codes as missing, and a blank is not an error. The eight coded reasons were written from the pilot and will not cover everyone — the point of this box is that the ninth reason gets recorded in the respondent’s words instead of disappearing into a catch-all, not that the enumerator is made to fill something in. Same treatment as native_language_other.", "text", skip="Ask only if came_here_reason = 8 (some other reason). May be left blank.", source="Project design (catch-all codes lose the case they catch)")

# ---- off-season labour migration: the real mobility variable -----------------------------------
# Type B in the closure-regime typology. Where closure_base says where the household goes in a normal
# year, this asks whether the respondent himself worked at a THIRD location during the last closure --
# the plains, another state, a city. That is the behaviour that matters: a household already selling
# labour away from both bases each winter has demonstrably lower migration costs than one that does
# not, which is precisely what the structural-displacement question is trying to establish. It is the
# respondent-level version of the item; a member-level version would need a household roster, which
# this instrument deliberately does not have.
R("D", "worked_away_in_closure", "Worked away from both bases during the last closure", "Last year, in the months when the Yatra was closed, did you work away from your home place?", "Off-season labour migration, asked of everyone. Revealed rather than stated mobility, and the ONLY thing in the instrument that says so: the work calendar (status_m1-m12) records the ACTIVITY in each month and not the place, and the absence spell (left_here_month, returned_here_month) says the respondent went to the home place, not past it. Without this item a winter spent labouring in Dehradun and a winter spent idle at home are the same twelve rows. Reworded 2026-10-01: 'did you go somewhere else for work' left 'somewhere else' than WHAT ambiguous when it followed the spell questions, which are about coming and going from HERE. Carries closure_labour_migrant, which is in the VEP exposure vector.", "bin", "yn", source="Project design (off-season labour migration)")
R("D", "closure_work_detail", "Where, and what work, during the closure (verbatim, optional)", "Where did you go, and what work did you do there? Write what they say.", "Free text, NOT required. Office-coded to NCO-2015 alongside prev_occ, occupation_detail and target_occ, so the off-season destination occupation enters the same classification as everything else and can be given a task vector.", "text", skip="Ask only if worked_away_in_closure = 1; may be left blank", source="Project design; coded to NCO-2015 in the office")
# Module D, not C: these are gated on resp_returns_at_closure and worked_away_in_closure, which are
# asked in this module. They sat in Module C at first and 06_form_fill_check.py caught it — a gate
# that is answered AFTER the question it controls can never open, so all three were unreachable.
# ---- where the respondent was living, as a spell rather than twelve questions ------------------
# This replaces loc_m1..loc_m12. The job is the same — stop the instrument assuming its own key
# fact, that people are somewhere else once the Yatra shuts — but twelve select_ones to establish
# what is almost always a single contiguous absence was a sixth of the interview for one variable.
# Asked as the spell instead: the month they left and the month they came back. months_here,
# months_home_base and months_third_place are all still derived, in Stata, from these three items.
# Dropped 2026-10-01, three questions, each traced to its consumers before it went:
#   months_away_for_work  the INTENSIVE margin of off-season migration, in months. Nothing
#         regressed on it. It built months_third_place and months_home_base, which appear in no
#         covariate vector and in no deprivation indicator — the mobility term the VEP models
#         actually use is closure_labour_migrant, and that is built from the yes/no above, not from
#         the months. months_here, the season weight on consumption and income, comes from the
#         absence SPELL (left_here_month, returned_here_month) and is untouched. The proposed
#         replacement — "is your usual residence different from your hometown" — was NOT added:
#         origin, resp_returns_at_closure and hh_at_home_place already answer it between them.
#   worked_other_places   prior mobility over the whole working life. It was in the VEP adaptive-
#   other_places_detail   capacity vector and nowhere else, and it is the weakest member of it:
#         "have you ever worked elsewhere" over a lifetime is answered Yes by most of this sample
#         (22 of 45 in the pilot had changed occupation at all), so it carries little variance, and
#         prev_occ plus target_occ already give the occupational-mobility history the
#         transferability analysis reads. Removed from X_adapt rather than kept for completeness.
R("D", "would_move_for_work", "Would go away for work in the coming year if this ended", "If this work here ended, would you go away from your home place to look for work in the coming year?", "Stated mobility, which is the constraint the task-distance measure cannot see: a worker whose skills fit a destination perfectly but who will not leave is structurally displaced just the same. Pairs with target_occ — that asks WHAT they would do, this asks whether they would move to do it — and is read against worked_away_in_closure, the revealed version. Given a concrete horizon (\"in the coming year\") rather than left as an open hypothetical, following the VASyR 2025 practice of horizoning intention items; an unbounded \"would you ever\" is answered on disposition rather than on circumstance.", "cat", "yndk", source="Project design; horizoned intention item after VASyR 2025 (move_accom_yesno, asked over a stated 6-month horizon)")
R("D", "migration_referral", "Who arranged or helped get this work", "Who mainly helped you get this work, or arranged it for you?", "The old list mixed two different things — who TOLD you about the work and who EMPLOYS or places you — and put a thekedar and an agent in one box although they are different relationships: a thekedar is who you work for, an agent is a middleman who places you and is usually paid for it. Splitting them is the point: an agent-placed worker has a debt or fee relationship an informally referred worker does not. \"Political or community leader\" is dropped; it was an analyst's category, not one a respondent would recognise as describing how they got their job. Ungated as of 2026-09-28: it used to be asked only of non-local respondents, but who placed you is a question about the employment relationship, not about migration — a local worker placed by an agent carries the same fee or debt relationship a Nepali one does, and gating it on a district boundary meant we could never see that.", "cat", "referral", source="Project design (referral channel as a proxy for social capital and for placement debt)")
R("D", "migration_referral_other", "Who helped, if not on the list (verbatim, optional)", "Who was it? Write what they say.", "Free text, NOT required, for referral channels the seven codes do not hold. The item is a proxy for social and political capital in getting access to work here, so a channel we failed to anticipate is exactly the one worth recording.", "text", skip="Ask only if migration_referral = 7 (Other); may be left blank")
# years_since_migration was dropped: redundant with years_current_job (Module B) for this study's
# purposes — "how long have you been doing this work" is the more analytically useful duration, and
# asking both a migration-duration and a work-tenure figure was asking the same thing twice in most cases.

# ------------------------------------------------------------------ E  consumption
E_NOTE = "Report for the household's usual place of living, including home-produced items valued at market price."
HC = "HCES 2022-23, MoSPI Appendix A"  # https://www.mospi.gov.in/.../HCES-22-23/AppendixA.pdf
IH = "IHDS-II Income and Social Capital Questionnaire, Q14"  # ihds.umd.edu
GH = "Nigeria GHS-Panel Wave 3, Household Questionnaire, Sections 10B/11"
SEASE = ("Workers here are migrants: the on-site figure at the time of interview would not represent a whole year, and asking about the 'usual homeplace' alone would miss on-site spending during the Yatra season. So each item is asked as a usual monthly amount for each of the two seasons, matched to the Yatra-season/off-season split already used for the work calendar (Module B/C). This replaces a single-point 30-day or 7-day actual recall with two 'usual month' figures, following the usual/typical recall approach used where recall decay or seasonal change is the bigger concern (Beegle et al. 2012; Deaton and Grosh 2000).")
YSPLIT = ("REFERENCE UNIT, changed 2026-10-05: both limbs now ask about 'your household'. The Yatra-season limb used to ask about 'you and anyone staying with you here' because the household is often split during the season, which is true and was a real fix for a real problem — but it made the two halves of one pair measure two different units, the on-site group in one and the whole household in the other, which the annual weighting then averaged together and divided by a single per-capita denominator. The denominator is now hhsize on both sides and the unit is the same on both sides. Where part of the household is elsewhere the respondent is reporting with less certainty about those members, which is a recall limitation to carry in the write-up, not a reason to measure a different population in each season. Enumerators in the first field test also read the two stems as two different questions, which they were.")
def EP(name, label, item_text, note, src):
    R("E", name + "_yatra_pm", label + ", Yatra-season month (Rs)", "In a normal month during the Yatra season, how much does your household spend on " + item_text + "? (Rs)", note + " " + SEASE + " " + YSPLIT, "money", source=src)
    R("E", name + "_offseason_pm", label + ", off-season month (Rs)", "In a normal month when the Yatra is closed, how much does your household spend on " + item_text + "? (Rs)", note + " " + SEASE, "money", skip=SEASGATE, source=src)

SEASGATE = "Ask only if spend_differs_by_season = 1"
R("E", "spend_differs_by_season", "Household spending differs between the two seasons", "Leaving aside money you send home — is what your household spends in a normal month during the Yatra season different from what it spends when the Yatra is closed?", "Gate for the off-season half of every seasonal pair. Where a household says spending is the same, the off-season figures are not asked and Stata copies the Yatra-season figure across, halving this module for those respondents. NOTE the risk this carries: a gate that saves nine questions is an invitation to answer \"same\", and the short branch is more attractive to a tired respondent and a hurrying enumerator. If a large share take it, check that share against the pilot before trusting the consumption aggregate — an over-used gate would bias measured consumption toward the Yatra-season level, which is about a third higher.", "bin", "yn", source="Project design (respondent-gated seasonal recall); the underlying two-season design follows Beegle et al. 2012 and Deaton and Grosh 2000 on usual-period recall")
EP("cons_staples", "Cereals, pulses, sugar and salt", "cereals (rice, wheat, other grains), pulses, sugar and salt, bought or from your own stock",
   "Staple foods bought less often.", HC + ", Sections 5.1-5.3 (30-day); " + IH + " 14.1-14.6 (30-day, same items)")
EP("cons_perishables", "Milk, vegetables, fruit, meat, oil, spices, tea", "milk and milk products, vegetables, fruit, egg/fish/meat, cooking oil, spices, and tea or coffee, bought or from your own stock",
   "Perishables bought often.", HC + ", Sections 6.1-6.8 (7-day actual recall in HCES; asked here as a usual monthly figure instead, for the reason above)")
FOODOWN_NOTE = ("Non-purchased food, one aggregate figure (HCES/IHDS record the source per item, too long for this interview). Framed as 'if you had to buy it' rather than telling the respondent to value it 'at market price': that phrase assumes a precision (knowing the exact market worth of one's own produce) most respondents would not have; asking what it would have cost to buy is the same imputation, in a question an actual person can answer.")
R("E", "cons_food_own_yatra_pm", "Home-grown or gifted food, Yatra-season month (Rs)", "If your household had not grown, raised or been given any of your food, about how much would it have cost to buy in a normal month during the Yatra season? (Rs, 0 if you buy everything)", FOODOWN_NOTE + " " + SEASE + " " + YSPLIT, "money", source="Calvo and Dercon 2007; Eze and Iheonu 2025 (non-purchased food, aggregate approach)")
R("E", "cons_food_own_offseason_pm", "Home-grown or gifted food, off-season month (Rs)", "If your household had not grown, raised or been given any of your food, about how much would it have cost to buy in a normal month when the Yatra is closed? (Rs, 0 if you buy everything)", FOODOWN_NOTE + " " + SEASE, "money", skip=SEASGATE, source="Calvo and Dercon 2007; Eze and Iheonu 2025 (non-purchased food, aggregate approach)")
EP("cons_food_out", "Meals eaten outside or given by employer", "meals, tea and snacks eaten outside the home, including any an employer gave free, at their market value",
   "Meals outside the home.", HC + ", Section 7.1 'served processed food' (7-day in HCES; usual monthly here)")
EP("cons_fuel", "Fuel and light", "fuel and light: cooking fuel, firewood, electricity, kerosene, candles", "Household fuel and light spending.",
   HC + ", Section 8.1 (30-day). " + IH + " 14.21-14.22. " + GH + " (30-day tier)")
EP("cons_routine_misc", "Toiletries and consumables", "soap, toiletries, cleaning goods and other small household items", "Routine consumables (transport and communication asked separately).",
   HC + ", Sections 9.1-9.2 (30-day). " + IH + " 14.25-14.27. " + GH + " (30-day tier)")
EP("cons_transport_comm", "Local transport, phone/internet", "local transport (bus, shared jeep, auto) and phone or internet charges", "Transport fares and communication charges.",
   HC + ", Sections 11.1-11.2 (30-day). " + IH + " 14.24/14.28. " + GH + " (30-day tier)")
EP("cons_rent", "Rent", "rent for the home (0 if owned, and 0 for any period spent living for free)", "Household rent. May differ sharply by season for a migrant worker (paid lodging at the Yatra site, an owned or rent-free home elsewhere).",
   HC + ", Section 11.4 (30-day). " + IH + " 14.30. " + GH + " (30-day tier)")
EP("cons_med_nonhosp", "Medical spending, not hospital", "medicine, doctor's or clinic fees and tests, not counting a hospital stay", "Routine, non-hospitalisation medical spending.",
   HC + ", Section 10.3 (30-day). " + IH + " 14.33 (30-day, out-patient)")

SITEMEALS = ("Worksite subsistence. The consumption module asks what the HOUSEHOLD usually spends, but during the season the respondent lives at the worksite, often apart from that household, and his own subsistence there has a different cost structure: paid lodging, bought meals, no home production. cons_rent catches the lodging; nothing caught the meals. SCOPE: this pair is PERSONAL, not household, spending. It is descriptive of the worksite economy and must NOT be added into cons_pc_pm — the VEP welfare measure stays household consumption per capita, and adding this would double-count against cons_food_out.")
EP("cons_packaged_food", "Biscuits, namkeen, packaged snacks and drinks", "biscuits, namkeen, chips, packaged snacks, cold drinks or bottled water",
   "HCES Section 7.2, packaged processed food — the other half of Section 7. cons_food_out covers 7.1, SERVED processed food (a meal or tea bought and eaten out); this covers packaged items bought and eaten anywhere, which on a trek route is a real and separate category. Omitting it put our consumption aggregate below the total-MPCE concept the poverty line is calibrated against, which biased poverty UPWARD.",
   HC + ", Section 7.2 (7-day in HCES; usual monthly here, as for every other seasonal item)")
EP("cons_pan_tobacco", "Pan, tobacco and intoxicants", "pan, gutka, bidi, cigarettes, tobacco or alcohol",
   "HCES Section 12 (12.1 pan, 12.2 tobacco, 12.3 intoxicants), asked here as ONE item rather than three: the three-way split serves HCES's item-code detail, not a poverty aggregate, and one figure is easier to answer and harder to double-count. NOT counted as food — HCES keeps pan/tobacco/intoxicants as its own MPCE category, so it enters total_cons_pm directly and not cons_food_pm. A sensitive item: the enumerator records what is offered and does not press.",
   HC + ", Sections 12.1-12.3 (7-day in HCES; usual monthly here, and combined into one figure)")
# DELIBERATELY NOT ASKED, having checked them against the source rather than leaving them silent:
#   HCES S11.3 entertainment (30-day) — for a worker living at the worksite through the season this
#     is close to zero, and it is a small share of rural MPCE. Documented exclusion, not an oversight.
#   HCES S13.3 bedding (365-day) — small, annual, and mostly incurred by the home household rather
#     than by the worker here. Documented exclusion.
# Both understate consumption slightly and therefore overstate poverty slightly; the direction is
# stated in the write-up rather than silently absorbed.
R("E", "cons_clothing_12m", "Clothing and footwear spending, last 12 months (Rs)", "In the last 12 months, how much did your household spend on clothes and footwear? (Rs)", "Annual clothing and footwear spending; already spans both seasons, so asked once, not split. Converted to monthly by dividing by 12.", "money", source=HC + ", Sections 13.1-13.2 (365-day). " + IH + " 14.38-14.39 (365-day). " + GH + " instead uses a 6-month recall for clothing (items 401-441); we follow the two India sources, since one of them (HCES) underlies our poverty line")
R("E", "cons_education_12m", "Education spending, last 12 months (Rs)", "In the last 12 months, how much on education: fees, books, uniforms, tuition? (Rs)", "Annual education spending; already spans both seasons, so asked once.", "money", source=HC + ", Section 10.1 (365-day). " + IH + " 14.35-14.37 (365-day, same items). " + GH + " asks school fees inside its education/roster module, per child, not as a household total, so it is not directly comparable")
R("E", "cons_durables_12m", "Durable goods spending, last 12 months (Rs)", "In the last 12 months, how much on durable goods: furniture, utensils, cooking appliances, phone, jewellery or ornaments, bicycle or vehicle parts? (Rs)", "Annual durables spending; already spans both seasons, so asked once.", "money", source=HC + ", Section 14 (365-day, 10 sub-groups). " + IH + " 14.40-14.48 (365-day). " + GH + " (12-month tier: durables, appliances, building materials). All three agree on the 12-month recall; insurance premiums, which IHDS (14.50) and the Nigeria survey (items 510-513) count here, are excluded, following HCES and standard national-accounts practice (insurance is a financial item, not consumption) — premiums are covered instead by the insurance items in Module G")

# cooks_own_meals_here and meal_spend_day_self were dropped 2026-09-30. meal_spend_day_self existed
# to capture a migrant's own cost of living here, but it never entered cons_food_pm or any other
# aggregate — it appeared in the do-files only inside an assert — while cons_food_out_yatra_pm asks
# the same thing as a monthly figure and does feed the aggregate. Adding it in would have
# double-counted. cooks_own_meals_here existed only to gate it. The asymmetry a reviewer spotted --
# buying meals led to a follow-up and cooking them did not — was the symptom: someone who cooks here
# has their ingredient spending in cons_staples and cons_perishables already.

# ------------------------------------------------------------------ F  housing and assets
HOMENOTE = "Self-reported, not enumerator-observed: by design the interview happens away from the respondent's usual home (Kedarnath route sites, not their native place), so the enumerator cannot see it."
R("F", "floor_material", "Main floor material at usual home", "What is the main material of the floor at your usual home?", HOMENOTE, "cat", "floor", source="NITI Aayog National MPI housing indicator")
R("F", "roof_material", "Main roof material at usual home", "What is the main material of the roof at your usual home?", HOMENOTE, "cat", "roof", source="NITI Aayog National MPI housing indicator")
R("F", "wall_material", "Main wall material at usual home", "What are the walls of your usual home mainly made of?", HOMENOTE + " NITI's housing indicator is deprived if the FLOOR is natural material OR the ROOF OR THE WALL is rudimentary. Wall material was simply not asked before, so one of the three limbs could not be evaluated at all.", "cat", "wall", source="NITI Aayog National MPI housing indicator (wall limb)")
R("F", "accom_type_here", "Where the respondent sleeps during the season", "While you are here for the season, where do you sleep?", "Accommodation at the WORKSITE, which nothing else in this module describes — floor_material, roof_material and the rest are about the usual home, and for a seasonal migrant that is not where he spends six months of the year. Feeds the security and social inclusion dimension of the Lyons et al. (2023) MLI, whose settlement-conditions indicator exists for exactly this case. Deprived at codes 4, 5 and 7: sleeping at the workplace, under canvas, or in the open.", "cat", "accomhere", source="Lyons et al. 2023, Table 2 (area/settlement conditions), adapted to a labour-migrant setting")
R("F", "electricity", "Usual home has an electricity connection", "Does your usual home have an electricity connection?", HOMENOTE, "bin", "yn", source="NITI Aayog National MPI")
R("F", "toilet_type", "Type of toilet at usual home", "What kind of toilet does your household use at your usual home?", HOMENOTE + " NITI counts a household deprived if the facility is unimproved OR improved but SHARED with other households, so a plain own-toilet yes/no cannot decide the indicator: it misses an unshared but unimproved pit latrine, and it misses a flush toilet shared between four families.", "cat", "toilet", source="NITI Aayog National MPI sanitation indicator (improved/unimproved and shared/not)")
R("F", "drinking_water", "Main source of drinking water at usual home", "What is your main source of drinking water at your usual home?", HOMENOTE + " Codes 1-6 are improved sources, 7-9 unimproved, following the JMP/NFHS taxonomy NITI Aayog's MPI indicator rests on.", "cat", "water", source="NITI Aayog National MPI drinking-water indicator (JMP improved/unimproved taxonomy)")
R("F", "water_on_premises", "Drinking water is available on the premises", "Is the drinking water available at the house itself?", "On-premises vs. fetched. NITI counts even an IMPROVED source as deprived when it is more than a 30-minute round trip away, so source alone cannot decide the indicator — this and the next item supply the missing limb.", "bin", "yn", source="NITI Aayog National MPI drinking-water indicator (30-minute round-trip rule)")
R("F", "water_fetch_minutes", "Minutes for a round trip to fetch water", "How long does it take to go there, get the water and come back? (minutes, round trip)", "Round-trip fetching time. The 30-minute threshold is NITI's own; asked as a duration rather than a yes/no so the cutoff can be varied in robustness checks instead of being baked into the question.", "count", skip="Ask only if water_on_premises = 0", source="NITI Aayog National MPI drinking-water indicator (30-minute round-trip rule)")
R("F", "cooking_fuel", "Main cooking fuel at usual home", "What does your household mainly use to cook at your usual home?", HOMENOTE + " Replaces a yes/no LPG question. NITI Aayog's indicator names the dirty fuels explicitly — dung, agricultural crops, shrubs, wood, charcoal or coal — so a fuel LIST is required to apply it; a binary cannot. NOTE on kerosene: NITI's list does not name it, so it is NOT counted as deprived here, although the global MPI does count it. Recorded separately so either rule can be applied later.", "cat", "fuel", source="NITI Aayog National MPI cooking-fuel indicator (its own list of dirty fuels)")
R("F", "land_unit", "Unit the household measures its land in", "In what unit do you count your land — nali, bigha, acres or hectares?", "Asked before the amount because a hill household thinks in nali and converting to acres in their head is an error the instrument should absorb, not create. Stata converts to acres for the asset index.", "cat", "landunit", source="Project design (local land units, Uttarakhand)")
R("F", "land_cultivable_acres", "Cultivable land owned or cultivated (in the unit given)", "And how much CULTIVABLE land is that? Do not count the land the house stands on.", "Cultivable land only. The old wording said \"agricultural land\" without excluding the homestead, so a landless household with a house on a tenth of an acre could report land it cannot farm — and this variable now gates the crop-insurance question and stands in for productive capacity.", "num", source="Chaudhuri et al. 2002 asset covariate")
PRODNOTE = "A count would treat a goat and a buffalo, or a jeep and a hand-cart, as equally valuable productive assets, which they are not; a list of binaries at least separates asset types, even without a value weight."
# ---- the nine NITI durables and the three livestock classes, each as ONE check-all --------------
# Nine consecutive yes/no screens reading "... a radio?", "... a bicycle?" is nine taps, nine Next
# presses and an invitation to straight-line: one respondent in the first field test answered Yes to
# all nine while reporting a mud floor and mud walls. As a single check-all it is one screen and the
# enumerator reads the list once.
#
# The NINE BINARIES STILL EXIST, as constructed variables split out of the multi-select in Stata --
# exactly the pattern other_activity_types already uses. That matters for two reasons: NITI's asset
# rule is defined on the individual items ("does not own more than one of radio, TV, telephone,
# computer, animal cart, bicycle, motorbike or refrigerator, and does not own a car or truck"), and
# the interviews already collected on build 4b87e5 hold the binaries as asked columns. Those columns
# stay in the sheet and Stata reads whichever of the two shapes a row has, so no record is stranded.
R("F", "assets_owned", "Durable assets the household owns (check all)",
  "Which of these does your household own? Read the list out and check every one they say: "
  "television, radio, bicycle, motorcycle or scooter, car/jeep/truck, telephone of any kind, "
  "computer or laptop, animal cart, refrigerator.",
  "The nine assets NITI's Assets indicator is defined on, asked as one check-all instead of nine "
  "yes/no screens (changed 2026-10-05). Split back into owns_tv, owns_radio, owns_bicycle, "
  "owns_motorcycle, owns_car, owns_phone, owns_computer, owns_animal_cart and owns_fridge in Stata, "
  "so mpi_asset_count and mpi_asset_deprived are computed on exactly the same items as before and "
  "the rows already collected as nine separate columns remain readable.",
  "multi", "assets", skip="May be left blank if the household owns none of them",
  source="NITI Aayog National MPI, Assets (weight 1/21)")
R("F", "livestock_owned", "Livestock the household owns (check all)",
  "And which of these animals does your household own? Cows or buffaloes, goats or sheep, ponies or "
  "mules.",
  "Three livestock classes as one check-all (changed 2026-10-05), split back into owns_cow_buffalo, "
  "owns_goat_sheep and owns_pony_mule in Stata. Kept as three CLASSES and not as head counts: a "
  "count treats a goat and a buffalo as the same unit of wealth, which they are not, and the pony "
  "class is the one that matters here because it is the asset a ropeway devalues.",
  "multi", "livestock", skip="May be left blank if the household owns no animals",
  source="Chaudhuri et al. 2002 asset covariate; pony/mule class is this project's exposure variable")
R("F", "owns_work_vehicle", "Uses a vehicle to earn money", "Do you use a vehicle to earn money — for example hauling goods, transporting people, or running a taxi? It does not have to be yours.", PRODNOTE, "bin", "yn", source="Chaudhuri et al. 2002 asset covariate")
R("F", "owns_work_equipment", "Owns equipment or tools used for work", "Does your household own equipment or tools that you use to earn?", PRODNOTE, "bin", "yn", source="Chaudhuri et al. 2002 asset covariate")
R("F", "work_equipment_detail", "What equipment or tools (verbatim, optional)", "What are they? Write what they say. Leave blank if they cannot say.", "Free text, NOT required. A binary cannot separate a set of hand tools from a generator or a chai urn, and the transferability analysis reads capital alongside tasks.", "text", skip="Ask only if owns_work_equipment = 1; may be left blank")

# Dropped 2026-09-30 after tracing every asked question to an analysis (checks/10):
#   water_fetched_by      who fetches the water. NITI's water indicator is source and distance; the
#                         gender of the fetcher is an equity descriptor that fed nothing.
#   has_jandhan_account   has_bank_account already carries financial inclusion, and nothing used the
#                         Jan Dhan subtype.
#   training_type         training_received (the binary) is what the analysis uses; the type and its
#   training_type_other   verbatim fed nothing. Two questions.
#   house_type            kaccha / semi-pucca / pucca is a summary of floor, roof and wall, and
#                         mpi_housing_dep is built from those three directly.

# ------------------------------------------------------------------ G  finance, insurance, schemes, phone
R("G", "has_bank_account", "Household has a bank or post office account", "Does anyone in your household have a bank account or a post office account?", "NITI's wording is \"no household member has a bank account OR A POST OFFICE ACCOUNT\". Post office accounts are common in hill districts and were previously excluded by the question wording, which would have marked some covered households as deprived.", "bin", "yn", source="NITI Aayog National MPI bank-account indicator; VEP adaptive-capacity covariate")
R("G", "took_loan_12m", "Borrowed money in the last 12 months", "In the last 12 months, did you or anyone in your household borrow money?", "Gate for the credit block.", "bin", "yn", source="VEP adaptive-capacity covariate")
R("G", "credit_source", "Main lender", "Who was the main lender?", "Lender TYPE, replacing the old institutional/non-institutional binary: a moneylender, an SHG and a contractor advance are three different things for vulnerability, and collapsing them hid which one a household actually depends on.", "cat", "credit", skip="Ask only if took_loan_12m = 1", source="VEP adaptive-capacity covariate (lender type)")
R("G", "loan_purpose", "What the loan was taken for", "What did you take it for?", "Purpose separates a loan that buys a pony — an investment in the livelihood — from one that covers a hospital bill or a wedding, which is distress borrowing. The same outstanding balance means opposite things in the two cases, and nothing in the instrument could tell them apart.", "cat", "loanpurpose", skip="Ask only if took_loan_12m = 1", source="Project design (investment against distress borrowing)")
R("G", "loan_amount_borrowed", "Amount originally borrowed (Rs)", "How much did you borrow in total? (Rs)", "The principal. The instrument asked only what was still outstanding, so a household that had repaid most of a large loan and one that took a small loan looked identical, and the repayment burden could not be computed at all.", "money", skip="Ask only if took_loan_12m = 1", source="Project design (loan size, for the debt-burden measures)")
R("G", "loan_amount", "Total amount still owed (Rs)", "How much of that loan is still left to repay? (Rs)", "Outstanding DEBT STOCK, not the amount borrowed. The instrument previously recorded who lent but never how much is owed — which is the quantity that decides whether a shock turns into poverty.", "money", skip="Ask only if took_loan_12m = 1", source="Islam and Chowdhury 2025 (financial distress and household vulnerability to poverty)")
R("G", "pays_interest", "Pays interest on the loan", "Do you pay interest on it?", "Gate for the rate question. The rate item previously read \"0 if none, leave blank if not known\" — two different \"if not\" branches in one instruction — which is unanswerable. Interest-free borrowing from relatives is common, so this is a real branch, not a formality.", "bin", "yn", skip="Ask only if took_loan_12m = 1", source="Project design (informal lending is often interest-free)")
R("G", "loan_interest_per100_pm", "Interest per Rs 100 borrowed, per month", "On every 100 rupees you borrowed, about how much interest do you pay in a month? (Rs; 0 if none, leave blank if not known)", "Interest as rupees per hundred per month, which is how informal lending is actually quoted here. ENUMERATOR RULE, because people answer in whichever unit they think in: rupees per 100 per month and PERCENT PER MONTH are the same number, so a \"3 percent\" answer is entered as 3. If they give an ANNUAL rate, divide by 12 before entering (36 percent a year becomes 3). If they quote a flat amount on the whole loan, work it back per 100 first. An annual percentage rate is not asked directly because most respondents would have to compute it, and would compute it badly.", "num", skip="Ask only if took_loan_12m = 1; may be left blank", source="Project design (informal-credit pricing as locally quoted)")
R("G", "loan_collateral", "What was pledged as security, if anything", "Did you have to give anything as security for it? If so, what — jewellery, land, animals, a vehicle, shop stock, a house, or something else?", "WHAT was pledged, not merely whether something was. A binary cannot tell a shop pledging its stock — ordinary commerce — from a household pledging its jewellery or its only buffalo, which is distress. The type is the signal; the fact of collateral is not.", "cat", "collat", skip="Ask only if took_loan_12m = 1", source="Carter and Zimmerman 2000; Zimmerman and Carter 2003 (asset-based coping)")
R("G", "insurance_held", "Types of insurance or scheme cover the household holds", "Which of these does anyone in your household have? Health insurance or scheme (including government ones); life insurance; crop insurance. Check every one that applies.", "Check-all 2026-10-07, replacing three near-identical screens (count of health-insured members, count of life-insured members, yes/no on crop insurance). Trades the per-member headcount for one simpler screen; health_insured_any and life_insured_any below are now household-level binaries, not counts. Crop insurance needs no land gate here: a household with no land simply does not tick it.", "multi", "instypes", skip="May be left blank if the household holds none of these", source="NITI Aayog National MPI health-insurance indicator; Lyons et al. 2023")
# Restructured 2026-10-01. The ten named schemes were OPTIONS; they are now a PROBE LIST in the
# enumerator hint, and what gets recorded is what the respondent says, coded in the office like the
# occupation fields. The reason the list existed is unchanged and still honoured — a bare "did you
# get a government benefit?" is a recall task people fail, so the names must be read out — but a
# fixed ten-item list decides in advance which benefits count, and the list was ours, not
# Uttarakhand's: a state scheme, a pension paid under a name the respondent actually uses, or a new
# transfer would all have landed in "some other scheme" and lost its identity. Free text keeps the
# name. The cost is that the scheme categories now come out of the office coding step rather than
# off the tablet, which GETTING_THE_DATASET.md states as its own step.
R("G", "govt_any_benefit", "Household received from any government scheme, last 12 months", "In the last 12 months, did your household get anything from any government scheme? Read the list out before you take an answer.", "Whether the household touched the public safety net at all. The enumerator hint carries the eight-scheme probe list that is read out; the names themselves go in the free-text item below. A No here, AFTER the list has been read, is a real No — which is the job the old code 10 was doing.", "bin", "yn", source="Project design; scheme names as administered in Uttarakhand")
R("G", "govt_schemes_detail", "Which schemes, in the respondent's words (coded in the office)", "Which ones? Write down every scheme they name, in their own words.", "Verbatim scheme names, office-coded afterwards against the Uttarakhand scheme list. IMPORTANT ITEM: this is now the ONLY place the identity of a benefit is recorded, so an answer left at 'a government scheme' loses the distinction between a ration card, a widow pension and MGNREGA wages — which protect against entirely different things. Required when govt_any_benefit = 1, unlike the other verbatim fields, for that reason.", "text", skip="Ask only if govt_any_benefit = 1", source="Project design; coded in the office against the Uttarakhand scheme list")

# ------------------------------------------------------------------ H  health
R("H", "morbidity_15d", "Anyone ill in the last 15 days", "In the last 15 days, was anyone in your household ill?", "Illness in the last 15 days.", "bin", "yn", skip="May be left blank", source="NSS health module (15-day recall) [source not held by this project; citation unverified as of 2026-09-28]")
R("H", "morbidity_coping_15d", "How the household coped with the cost of this illness", "How did the household mainly cope with the cost of this: used savings; borrowed money; sold or pawned assets; cut other consumption; got help from relatives or community; or something else?", "Coping response to the illness reported above; same coping list as the Module I shock question.", "cat", "coping", skip="Ask only if morbidity_15d = 1. May be left blank", source="Project design (a reported illness with no cost/coping follow-up said nothing about its burden)")
R("H", "morbidity_cost_15d", "Amount spent on this illness, last 15 days (Rs)", "About how much did the household spend on this in the last 15 days (medicine, doctor or clinic fees, travel for care)? (Rs)", "Out-of-pocket cost of the illness reported above.", "money", skip="Ask only if morbidity_15d = 1. May be left blank", source="Project design")
R("H", "func_limitation", "Difficulty walking or climbing steps (Washington Group)", "Do you have difficulty walking or climbing steps?", "Washington Group Short Set item 3, asked verbatim with its own four-point scale and deprived at the standard cutoff of a lot of difficulty or cannot do it at all. One item rather than the full six, and the mobility one on purpose: this workforce carries loads and people up a 16-kilometre climb, so walking and climbing is both the function that matters most to the livelihood and the one most likely to be lost. Gives the Lyons et al. health dimension a disability indicator, which the NITI MPI has none of, and enters the VEP models as a sensitivity covariate. State the limit in the write-up: one item is not the WG-SS and cannot carry its prevalence estimate.", "cat", "wgdiff", skip="May be left blank", source="Washington Group on Disability Statistics, Short Set item 3 (mobility), verbatim; Lyons et al. 2023 health dimension")
R("H", "hospitalization_365d", "Anyone admitted to hospital in the last 12 months", "In the last 12 months, was anyone in your household admitted to hospital overnight?", "Hospital admission.", "bin", "yn", skip="May be left blank", source="NSS health module (365-day recall) [source not held by this project; citation unverified as of 2026-09-28]")
R("H", "cons_medical_hosp_12m", "Medical spending, hospital stays, last 12 months (Rs)", "In the last 12 months, how much did your household pay for any hospital admission or stay? (Rs, 0 if none)", "Hospitalisation spending; the lumpy, infrequent part of medical spending, at a 12-month recall that already spans both seasons. Together with the non-hospitalisation item in Module E, this is the out-of-pocket health measure. Moved next to hospitalization_365d (2026-10-07), which it belongs with on the interview screen; the consumption total it feeds is unchanged, since that total reads from the dictionary's formulas, not from module order.", "money", source=HC + ", Section 10.2 (365-day, hospitalisation). " + IH + " 14.34 (365-day, in-patient). " + GH + " instead uses one combined 6-month medical item (less detail); we follow the matching HCES/IHDS split")
R("H", "health_access_barrier_3m", "Unable to get needed medical care, last 3 months", "In the last 3 months, was there a time when someone in your household needed medical care but could not get it?", "Healthcare-access barrier (unmet need), distinct from having insurance cover.", "bin", "yn", skip="May be left blank", source="VASyR 2025 barriers_health_case_access_phc_m (primary-care access barriers); Lyons et al. 2023 Table 2 indicator 2 'healthcare access'")
NITIH = ("NITI Aayog's Health dimension is three indicators — Nutrition (1/6), Child and Adolescent "
         "Mortality (1/12) and Maternal Health (1/12) — and this instrument previously had NONE of "
         "them, substituting a project-built health-access measure. Two of the three need no "
         "household roster and are added here. NUTRITION CANNOT BE COLLECTED: NITI defines it on "
         "anthropometry (measured height, weight, BMI) and a read-aloud interview at a worksite "
         "cannot produce that, so the MPI built from this instrument is a TEN-of-twelve-indicator "
         "index and must be reported as such, never as the National MPI.")
R("H", "child_death_5y", "A child or adolescent under 18 died in the household, last 5 years", "In the last five years, has any child or young person under 18 in your household died?", "NITI's Child and Adolescent Mortality indicator, verbatim in its own terms. One question, no roster needed. " + NITIH, "bin", "yn", skip="May be left blank", source="NITI Aayog National MPI, Child and Adolescent Mortality (weight 1/12)")
R("H", "birth_last_5y", "A woman in the household gave birth in the last 5 years", "In the last five years, did any woman in your household give birth?", "Gate for the two maternal-health questions. " + NITIH, "bin", "yn", skip="May be left blank", source="NITI Aayog National MPI, Maternal Health (weight 1/12)")
R("H", "anc_4_visits", "Mother had at least 4 antenatal check-ups for the most recent birth", "For the most recent birth, did she have at least four check-ups before the delivery?", "First limb of NITI's Maternal Health indicator. \"Don't know\" was REMOVED 2026-10-01. The old reasoning was that a don't-know is conservative because the indicator tests anc != 1, so it counts as deprived — but that is exactly the danger: a male respondent who cannot recall is then recorded as a deprived household, and a sample with many such respondents reports a maternal-health deprivation rate built out of ignorance rather than out of care not received. The item is now a plain yes/no and the burden moves to the probe (see the hint): ask the mother if she is there, and otherwise ask how many times she went and code four or more.", "cat", "yn", skip="Ask only if birth_last_5y = 1. May be left blank", source="NITI Aayog National MPI, Maternal Health (antenatal care limb)")
R("H", "skilled_birth_attendant", "Who conducted the most recent delivery", "Who conducted that delivery — a doctor, a nurse or ANM, an ASHA or Anganwadi worker, a dai, or nobody trained?", "Second limb of NITI's Maternal Health indicator; NITI counts the household deprived if EITHER limb fails. Asked as the CADRE rather than as yes/no: \"a doctor, nurse or trained midwife\" named no cadre anybody here uses, and an ASHA or Anganwadi worker — who commonly does accompany a birth in these districts — would have been heard as a yes. NFHS and NITI count only a doctor, nurse, ANM, LHV or qualified midwife as skilled; an ASHA, an Anganwadi worker and a dai are explicitly NOT, so putting them in the list as their own codes is what keeps the indicator correct. Deprived unless code 1 or 2.", "cat", "birthattend", skip="Ask only if birth_last_5y = 1. May be left blank", source="NITI Aayog National MPI, Maternal Health (assisted delivery limb); skilled-provider definition per NFHS")

# ------------------------------------------------------------------ I  shocks
R("I", "distress_event_last365d", "Shocks in the last 12 months (check all that apply)", "In the last 12 months, did any of these happen — to your household, or to the Yatra route you work on? Check every one that applies.", "Check-all, replacing \"record the most serious one\". That instruction asked the enumerator to rank another household's misfortunes against each other, which they are in no position to do and which threw away every shock but one. The list also gains four COVARIATE shocks (codes 5-8) that hit the whole route at once; every code in the old list was household-idiosyncratic, so the covariate-versus-idiosyncratic decomposition could not be identified from this data at all.", "multi", "distress", source="VEP exposure covariate (Azeem et al. 2016); shock inventory following Gunther and Harttgen 2009, via Fujii 2016 section 4")
# Shock MAGNITUDE, for whichever event the respondent names as the hardest. Incidence alone cannot
# support a vulnerability-as-uninsured-exposure-to-risk analysis: VER asks how far consumption moves
# per unit of shock, and without a size there is no per unit.
# Split in two on 2026-10-01. The single item asked for "earnings lost AND money spent, in all",
# which is two quantities in different kinds and asks the respondent to add them — and to value his
# own forgone work, which he can only do by guessing at a wage we have already measured. Asked as
# the two facts instead: how much work was lost, and how much money went out. shock_loss_total then
# values the lost work at the respondent's OWN measured weekly earnings in Stata, which is both more
# accurate than his estimate and a quantity the two limbs can be reported separately against.
R("I", "shock_work_lost_weeks", "Weeks of work lost because of the worst shock", "Thinking of whichever of those hit you hardest — about how many weeks of work did you lose because of it? (0 if none)", "The TIME limb of the shock. Asked in weeks rather than months because this is a six-month earning season: three weeks lost at the peak is a large shock and would round to zero months, while weeks divide cleanly into the monthly calendar afterwards. Valued at the respondent's own measured earnings in shock_loss_total rather than at his estimate of them.", "count", skip="Ask only if distress_event_last365d names a real shock (not code 9, nothing happened)", source="Ligon and Schechter 2003; Dercon and Krishnan 2000 (VER needs shock magnitude, not only incidence)")
R("I", "shock_money_spent", "Money the household had to spend because of the worst shock (Rs)", "And about how much money did your household have to spend because of it — treatment, repairs, replacing what was lost? (Rs, 0 if nothing)", "The CASH limb of the shock: money that actually left the household, separate from earnings it never received. A rough figure is expected — the quantity of interest is the order of magnitude against household consumption, not the rupee.", "money", skip="Ask only if distress_event_last365d names a real shock (not code 9, nothing happened)", source="Ligon and Schechter 2003; Dercon and Krishnan 2000 (VER needs shock magnitude, not only incidence)")
R("I", "shock_month", "Month the worst shock happened", "And in which month did that one happen?", "Shock TIMING, which is what matches the event to the monthly income calendar in Module C and to the season the household was in. A shock during the Yatra season and the same shock during the closure are different events for a household earning its whole year in six months.", "cat", "month", skip="Ask only if distress_event_last365d names a real shock (not code 9, nothing happened)", source="Dercon and Krishnan 2000 (seasonal timing of shocks); project design")
R("I", "shock_coping", "How the household coped (check all that apply)", "How did your household manage? Check every one they used.", "Check-all. The single-answer version forced a choice between \"sold or pawned assets\" and \"cut consumption\" — which are precisely the two responses asset-smoothing theory (Carter and Zimmerman) says to compare, since a household facing a survival constraint may cut consumption specifically to defend its assets. Made mutually exclusive, the test was impossible.", "multi", "coping", skip="Ask only if any shock was reported", source="Coping strategies in VEP studies; Carter and Zimmerman 2000 on asset versus consumption smoothing")
# ---- food security: FIES, replacing the ten rCSI day-counts (2026-10-05) -----------------------
# The rCSI block was five WFP items asked twice, once per season, as 0-7 day counts. It went to the
# field on 2026-10-05 and did not survive it. Of seven real interviews: three answered all ten items
# zero, one answered every one of the ten with exactly 2 (straight-lining), one gave a directionally
# incoherent pattern (more meal-skipping IN the earning season than out of it), and the only
# respondent to cross the rCSI > 20 cutoff was the one interview that is visibly fabricated -- nine
# minutes long, GPS 200 km off-route on a 50 km accuracy fix. Two of seven carried any signal.
#
# The response format was the fault. WFP's item is a census of a week that actually happened ("in
# the past 7 days, how many days did your household..."); ours asked for an integer out of 7 about a
# NORMAL week, which is not a week that happened, so the respondent has to average six months in his
# head and the enumerator ends up converting "when there is no money" into a number. Worse, the word
# "normal" inverts the construct: the rCSI measures coping, meaning departure from the household's
# own baseline, and a household whose baseline IS cheaper food every day answers 7 and is scored as
# being in crisis. On top of that, the stems said "your household" on both limbs while the household
# is 500 km away during the season -- the reference-unit problem Module E was reworded to fix and
# this block never was. And the > 20 threshold was Lyons et al.'s, set on Lebanese refugee
# households answering the original 7-day form; it was never calibrated on anything we were asking.
#
# FIES instead: the behavioural tail of the Food Insecurity Experience Scale, SDG indicator 2.1.2,
# validated across 150+ countries and in use in India. Eight items in full; the five here are the
# severe end, dropping the three ("worried", "unable to eat healthy food", "ate only a few kinds of
# foods") that are experiential rather than behavioural. Why it fits this instrument where the rCSI
# did not: every item is yes/no, so it respects the standing rule against frequency and rating
# scales; the reference period is the last 12 months, so it reaches the lean season while the
# interview happens in the earning season, and the season doubling disappears with it; and the items
# are personally referenced, which a split migrant can answer for himself without speaking for a
# household elsewhere. Ten day-counts become five binaries.
FIES = ("Food Insecurity Experience Scale (FIES), the five behavioural items, asked over a 12-month "
        "reference period as FAO specifies. Replaces the ten rCSI day-counts retired 2026-10-05 (see "
        "the note above this block for why). Scored as a raw 0-5 count; fies_mod_sev marks 2 or more, "
        "the conventional moderate-or-severe line on the behavioural items. Do NOT apply the rCSI's "
        "> 20 cutoff or any weighting to these -- FIES is an unweighted count with an ordered "
        "severity structure, which is the point of using it.")
R("I", "fies_items", "Which FIES behavioural items happened, last 12 months (check-all)",
  "In the last 12 months, was there a time when, because of a lack of money or other resources, any "
  "of the following happened to you or your household? Read out each one and check every one that "
  "applies, or check 'none of these' if none did.",
  "One check-all screen 2026-10-07, replacing five separately-worded yes/no questions that read as "
  "the same question five times. 'None of these' (code 96) is a real answer, ticked by the "
  "enumerator, and is what tells fies_skipped_meal etc. below to read as 0 rather than missing -- an "
  "empty answer (nothing ticked, screen skipped) stays missing on all five. " + FIES,
  "multi", "fies5", skip="May be left blank",
  source="FAO Food Insecurity Experience Scale (FIES), SDG indicator 2.1.2; behavioural items only")

# ------------------------------------------------------------------ J  ropeway
R("J", "ropeway_stance", "View on the proposed ropeway for this route", "A ropeway is proposed for this route. Are you in favour, neutral, or against?", "Stated stance; no rating scale. Asked only on the Kedarnath route (site = 1): the question names a specific proposal, and reading it to a Hemkund respondent asks him about a project that is not his.", "cat", "stance", source="Project design")
R("J", "ropeway_expect_work", "Expected effect of the ropeway on your own work", "If the ropeway is built, what do you think will happen to your own work? More work for you; less work; about the same; or don't know?", "Anticipated effect on own work, parsimonious and factual. Asked on the Kedarnath route only, with the stance question. Wording is ours; the concept (perceived effect on livelihoods of a nearby large project) is from Pelz et al. 2024, which measures perceived benefits and trust in the coal company's effect on local livelihoods (their Fig. 4B) and perceived importance of the sector (Fig. 3).", "cat", "ropexp", skip="", source="Pelz et al. 2024, Energy Policy 186:113973 (concept: perceived effect on livelihoods; wording ours)")
R("J", "ropeway_expect_jobs", "Who will get the ropeway jobs", "Who do you think will get most of the jobs the ropeway creates? People from these villages; people from outside the area; nobody will get jobs; or don't know?", "Expected distribution of new jobs, which is what decides whether the ropeway helps the people in this sample. Concept from Pelz et al. 2024 (perceived benefits of the coal sector limited to those nearby, their Fig. 4 and the conclusion); wording ours.", "cat", "ropjobs", skip="", source="Pelz et al. 2024, Energy Policy 186:113973 (concept: local vs outside benefit; wording ours)")
R("J", "ropeway_trust", "Do you think the ropeway will improve local livelihoods", "Do you think the ropeway will improve the livelihoods of people here? Yes; no; or don't know?", "Trust in the project to improve local livelihoods, yes/no, no scale (the population is not used to rating scales). Pelz et al. 2024 measure trust in the coal company to improve local livelihoods (their Fig. 4B) and find it far below trust in the state.", "cat", "yndk", skip="", source="Pelz et al. 2024, Energy Policy 186:113973 (Fig. 4B, trust in the company; wording ours)")
R("J", "trek_dependent", "Main work is carrying or guiding on the trek", "Is your main work carrying, transporting or guiding people or goods on foot along the pilgrimage trek?", "Direct exposure flag (factual); not inferred from job title.", "bin", "yn", source="Project design (see tasks_module W4: exposure must be asked directly)")

# ------------------------------------------------------------------ K  job quality (Apablaza et al. 2026, Appendix 2, read
# directly and used with its own skip logic. Not reproduced: Q1-Q4 (household-roster demographics --
# ours is a no-roster, aggregate-report design; Q4 itself is adapted as main_income_earner in Module A)
# and the open-text Q6/Q7 (occupation/workplace sector — already covered by occupation's 13 groups,
# which blend occupation and workplace type for this specific economy). Q14/Q15 (single-point earnings
# + a fallback range if unknown) are not reproduced either: the 12-month calendar (Module C) already
# asks earnings, month by month, which is more information than one point-in-time figure or its range.
KA = "Apablaza et al. 2026, Appendix 2 "
KSKIP = ""   # job_situation retired 2026-10-05; everyone recruited at the worksite is working
# Apablaza Q5 routes three ways, so the module has three gates, not one:
#   1-3 (working)          -> the whole job-quality block below (KSKIP)
#   4-7 (studying/trained/retired/unpaid care) -> skip to Q21 wants_more_work (KTAIL)
#   8   (unemployed, seeking)                  -> skip to Q22/Q23 (hours wanted, job search)
#   9-11 (sick/inactive/don't know)            -> end the module entirely
KTAIL = ""   # same: of Apablaza's three-way routing only one branch was ever live here
# employer_type was dropped 2026-09-30. It asked employment status a SECOND time, in Apablaza's Q8
# taxonomy, minutes after employment_type asked it in Module B — two overlapping lists, no check that
# they agreed, and only the Module B answer ever reached the analysis. Q8 is also the worse instrument
# here: its codes cross status with institutional sector (private company / public sector / armed
# forces / domestic service), so a porter paid by a thekedar or a shop worker paid by the shop owner --
# employed by an individual, not a firm, which is most of this sample — had no true option but
# "employee of a private company". The one category Q8 had that Module B lacked, unpaid family worker,
# has been added to emptype instead.
R("K", "contract_status", "Has a signed contract", "Do you have a signed contract? Yes, signed; yes but not yet signed; no contract.", "Contract status, wage workers only.", "cat", "contract", skip="Ask only if employment_type is 3 or 4 (wage workers) — self-employed skip to the next question", source=KA + "Q11")
R("K", "workplace_registered", "Workplace or business is registered", "Is your workplace or business registered, for example with a taxpayer or GST number, a shop or trade licence, the Yatra registration, or a union?", "Registered enterprise (Apablaza asks about a taxpayer number).", "bin", "yn", skip=KSKIP, source=KA + "Q12 (widened to local registrations)")
# Gated to wage workers as of 2026-10-01. An own-account pony owner was being asked whether his
# EMPLOYER deducts a pension, provides health insurance, and grants paid leave. He has no employer;
# the questions have no answer for him and reading them out costs the enumerator credibility.
# contract_status was already gated this way; these three were not.
R("K", "pension_any", "Contributes to any pension system", "Do you contribute to any pension system, through your work or on your own?", "Pension contribution, collapsed to a binary 2026-10-07 (was a 3-way employer-deducts/voluntary/no split): most of this population is informally employed and the three-way split rarely separated anything beyond 'no'. Employer-deducted and voluntary contribution are no longer distinguished.", "bin", "yn", skip=KSKIP, source=KA + "Q16")
R("K", "work_health_ins", "Has health insurance through work", "Do you have health insurance through your work? Yes; only private or other insurance; none; don't know.", "Work-related health insurance.", "cat", "workins", skip=KSKIP, source=KA + "Q17")
R("K", "leave_rights", "Has right to paid leave (holiday, sick or maternity)", "Do you have the right to paid holiday, sick or maternity leave?", "Leave rights. Apablaza asks this of everyone still in the block, not only wage workers (a self-employed respondent can simply answer no), so the wage-worker-only skip used earlier is dropped to match.", "cat", "yndk", skip=KSKIP, source=KA + "Q18")
R("K", "injured_ever", "Ever physically injured at work", "Have you ever been physically injured at your workplace?", "Injury history.", "cat", "yndk", skip=KSKIP, source=KA + "Q19")
R("K", "workplace_injury_12m", "Anyone injured at your workplace, last 12 months", "In the last 12 months, was anyone physically injured at your workplace because of work?", "Recent workplace injury. SPLIT from a single “injured or killed” item on 2026-10-03. The two cannot share one yes/no: a Yes could mean a cut hand or a death, which are not the same hazard and are not the same answer, and a respondent whose colleague died has to answer a question that also asks about sprains. On this route the distinction is live — falls and rockfall on the Gaurikund–Kedarnath path kill people most seasons — so collapsing it loses the severe tail precisely where it matters. Asked first because it is the common case and the easier question; the death item follows it.", "cat", "yndk", skip=KSKIP, source=KA + "Q20 (split into injury and death)")
R("K", "workplace_death_12m", "Anyone killed at your workplace, last 12 months", "And in the last 12 months, did anyone die at your workplace because of work?", "Recent workplace death. The severe limb of the old combined item. Kept as its own yes/no rather than as a severity follow-up to the injury question, because a death can occur in a year with no injury the respondent counts as one, and gating it on workplace_injury_12m would then never ask it.", "cat", "yndk", skip=KSKIP, source=KA + "Q20 (split into injury and death)")
R("K", "wants_more_work", "Would like to work more", "Would you like to work more hours than you do?", "Involuntary underemployment. Gated at codes 1-7, not 1-3: Apablaza routes the studying, in-training, retired and unpaid-care categories (4-7) directly to this question, so gating it on 'currently working' would drop exactly the respondents it is meant to reach.", "cat", "yndk", skip=KTAIL, source=KA + "Q21")
R("K", "more_hours_day", "Additional hours per DAY wanted", "On a working day, how many MORE hours would you like to work?", "Extra hours wanted.", "count", skip="Ask only if wants_more_work = 1", source=KA + "Q22")
R("K", "months_looked_for_work", "Months spent looking for work", "Across the months when you had no paid work, about how many MONTHS in total were you looking for work?", "Job-search duration in weeks — Apablaza's own unit (Q23) — rather than a plain yes/no, tied to the idle months already identified in the work calendar (Module C) rather than to a single point in time. Fires on the calendar OR on job_situation = 8: the calendar gate is this project's own improvement (it anchors the recall to months the respondent has already named), but on its own it would miss a respondent who is unemployed and seeking right now, which is the case Apablaza routes here.", "count", skip="Ask only if months_no_paid_work > 0", source=KA + "Q23 (duration in weeks, tied to the calendar instead of a single point in time)")
R("K", "higher_ed", "Completed a college, diploma or university course", "Have you completed any college, diploma or university course?", "Higher education, for the occupational-status limb of the employment table (self-employed without higher education). Asked of every working respondent, because the limb applies to the self-employed too.", "cat", "yndk", skip=KSKIP, source=KA + "employment table, occupational status (1/8)")
R("K", "social_security_any", "Enrolled in any social-security scheme", "Are you enrolled in any pension, insurance or social-security scheme? For example, EPFO or PM-SYM pension, or Ayushman Bharat health cover.", "Social-security affiliation for EVERY worker. The pension and health-insurance items above are gated to wage workers because they ask about an employer; this one asks about the person, so the self-employed are measured too.", "cat", "yndk", skip=KSKIP, source=KA + "employment table, employment security (1/8)")
R("K", "intens_speed", "Works at very high speed for over half the day", "For more than half of your working day, do you work at very high speed?", "Work intensity, demand 1 of 3. Two of the three demands together count as high intensity.", "cat", "yndk", skip=KSKIP, source=KA + "employment table, work intensity (1/16)")
R("K", "intens_deadline", "Works to tight deadlines for over half the day", "For more than half of your working day, do you work to tight deadlines?", "Work intensity, demand 2 of 3.", "cat", "yndk", skip=KSKIP, source=KA + "employment table, work intensity (1/16)")
R("K", "intens_time", "Not enough time to finish tasks for over half the day", "For more than half of your working day, do you not have enough time to finish your tasks?", "Work intensity, demand 3 of 3.", "cat", "yndk", skip=KSKIP, source=KA + "employment table, work intensity (1/16)")
R("K", "posture_position", "Tiring or painful position for over half the day", "For more than half of your working day, do you work in a tiring or painful position?", "Posture-related risk, demand 1 of 3. Two of three together count as high posture risk.", "cat", "yndk", skip=KSKIP, source=KA + "employment table, posture risk (1/16)")
R("K", "posture_loads", "Carries or moves heavy loads for over half the day", "For more than half of your working day, do you carry or move heavy loads?", "Posture-related risk, demand 2 of 3.", "cat", "yndk", skip=KSKIP, source=KA + "employment table, posture risk (1/16)")
R("K", "posture_repetitive", "Repetitive movements for over half the day", "For more than half of your working day, do you make the same movements again and again?", "Posture-related risk, demand 3 of 3.", "cat", "yndk", skip=KSKIP, source=KA + "employment table, posture risk (1/16)")
R("K", "phys_noise", "Exposed to loud noise for over half the day", "For more than half of your working day, are you exposed to loud noise?", "Physical risk from the working environment. EITHER this OR the temperature item counts as high physical risk.", "cat", "yndk", skip=KSKIP, source=KA + "employment table, physical risk (1/16)")
R("K", "phys_temperature", "Exposed to extreme heat or cold for over half the day", "For more than half of your working day, are you exposed to extreme heat or cold?", "Physical risk from the working environment, second item.", "cat", "yndk", skip=KSKIP, source=KA + "employment table, physical risk (1/16)")

# ------------------------------------------------------------------ L  tasks and papers (short block)
TASKS = [
 # Tasks 1, 2, 5, 6 added 2026-10-07: the fielded 12 had no item that separates a porter, a
 # palki-bearer or a pony handler from general goods handling (tk_load), which left the task-space
 # profile of trek_dependent's own occupations thin for a reason that has nothing to do with their
 # actual skills. These four are the defining tasks of that population.
 ("tk_carry", "Carry loads or luggage on foot", "1", "GS 2010 'pack, ship or transport'; NCO 9621.9900 / 9621.0500 porters"),
 ("tk_passenger", "Carry a passenger (palki, dandi or kandi)", "2", "No NCO-2015 code for palki/dandi bearers; nearest NCO 9331.0100"),
 ("tk_load", "Load, unload, stack or count goods", "3", "Gathmann and Schonberg 2010; NCO 9333.0100 loader"),
 ("tk_lead_animals", "Lead, load or control pack animals such as ponies or mules", "5", "NCO 9332.0400 pack animal driver"),
 ("tk_animal_care", "Feed, groom or care for animals", "6", "NCO 9332.0400 (feeds animals, cleans stables)"),
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
    R("L", nm, lab[:70] + " (task grid)" if len(lab) <= 62 else lab[:80], f"Do you {lab[0].lower() + lab[1:]}? ",
      f"Task {no} of the full 27-task list (tasks_module). Three answers: regular now / done before / never; not a rating.", "cat", "task3", source=src)
R("L", "drove_twowheeler", "Has driven a motorcycle or scooter (licence or not)", "Have you ever driven a motorcycle or scooter, with or without a licence?", "Factual driving experience by vehicle class.", "bin", "yn", skip="Ask only if tk_drive is 1 or 2", source="Level ladder without licences: people drive without holding a licence")
R("L", "drove_car", "Has driven a car or jeep (licence or not)", "... a car or jeep?", "Factual driving experience by vehicle class.", "bin", "yn", skip="Ask only if tk_drive is 1 or 2", source="Level ladder without licences")
R("L", "drove_heavy", "Has driven a truck or bus (licence or not)", "... a truck or bus?", "Factual driving experience by vehicle class.", "bin", "yn", skip="Ask only if tk_drive is 1 or 2", source="Level ladder without licences")
R("L", "read_at_work", "Reads anything at work", "In your work, do you read anything (notes, rate lists, tickets, messages)?", "Reading used at work (factual).", "bin", "yn", source="STEP module 6A")
R("L", "calc_at_work", "Works out prices or costs at work", "In your work, do you work out prices or costs?", "Arithmetic used at work (factual).", "bin", "yn", source="STEP module 6A")

# ------------------------------------------------------------------ M  access to common resources (short block)
# Krantz (2001): natural capital and claims/access are two of the livelihood asset categories;
# Lax & Krug: firewood and forest produce are the indicators a natural-resource-dependence assessment
# starts from. Factual items only, no rating scales. The governance item asks WHO decides, because a
# restriction on a common resource is only interpretable against its authority.
R("M", "cpr_permitted", "Collection from the forest or common land is allowed here", "Where you work, is it allowed to take firewood, fodder or forest produce from the forest or common land? Ask what they understand the rule to be; do not correct them.", "The DE JURE baseline, asked separately from use because the two are different quantities and this route spans both. On the Govindghat-Hemkund side the Forest Department prohibits collection; on the Gaurikund-Kedarnath side grazing is visibly tolerated. Without this, a No on the use items is uninterpretable -- it could be a household with no need for the forest or a household barred from it, and those are opposite findings for a livelihood-vulnerability study. Asked as what the respondent UNDERSTANDS the rule to be, not what the rule is: a prohibition nobody knows about does not constrain behaviour, and a believed prohibition does even where none exists. Pairs with cpr_governance, which asks who decides.", "cat", "permdk", skip="May be left blank", source="Project design (de jure access, 2026-10-05); Ostrom 1990 on the distinction between rule in form and rule in use")
R("M", "cpr_firewood", "Collected firewood or dead wood from common land or forest", "In this Yatra season or last Yatra season, did you or anyone staying with you here collect firewood or dead wood from common land or forest in the Yatra region or workplace region?", "Natural-capital use, the first of four factual use items.", "cat", "cpruse", skip="May be left blank", source="Krantz 2001, natural capital: resource stocks from which resource flows are derived (definitions list); item wording is ours")
R("M", "cpr_fodder", "Collected grass or fodder from common land", "In this Yatra season or last Yatra season, did you or anyone staying with you here cut grass or fodder from common land in the Yatra region or workplace region?", "Natural-capital use, fodder.", "cat", "cpruse", skip="May be left blank", source="Krantz 2001, natural capital: resource stocks from which resource flows are derived; item wording is ours")
R("M", "cpr_forest_produce", "Collected herbs, mushrooms or wild fruit from the forest", "In this Yatra season or last Yatra season, did you or anyone staying with you here collect herbs, mushrooms or wild fruit from the forest in the Yatra region or workplace region?", "Natural-capital use, non-timber forest produce.", "cat", "cpruse", skip="May be left blank", source="Krantz 2001, natural capital (resource flows from stocks); item wording is ours")
R("M", "cpr_grazing", "Animals grazed on common pasture", "In this Yatra season or last Yatra season, did any animal of yours or of anyone staying with you here graze on common pasture in the Yatra region or workplace region?", "Asked of all. A respondent with no animals answers No; that is an answer, not a skip.", "cat", "cpruse", skip="May be left blank", source="Krantz 2001, natural capital: resource stocks from which resource flows are derived; item wording is ours")
R("M", "cpr_restricted", "Stopped, or asked to pay, for using a common resource", "In this Yatra season or last Yatra season, has anyone you or someone staying with you here been stopped from using a common forest, pasture or path, or been asked to pay to use it, in the Yatra region or workplace region?", "Access restriction, the claims side of the common-resource asset. Asked as one event question rather than a list, so the enumerator does not have to name the authority.", "cat", "yndk", skip="May be left blank", source="Krantz 2001, access ('the opportunity in practice to use a resource') and claims ('demands and appeals'); item wording is ours")
R("M", "cpr_lost_access", "Lost a common place used before, because of building or road work", "In this Yatra season or last Yatra season, has a common place you used to collect from or graze on been closed, because of a landslide, flood, road or bridge damage, or construction work, in the Yatra region or workplace region?", "Access lost to construction. Tied to the ropeway question in Module J but asked on every route, because road and bridge works also close common land.", "cat", "yndk", skip="May be left blank", source="Krantz 2001, access (as above); the ropeway link is the project's own")
R("M", "cpr_water_route", "Common water source on the route or near the worksite", "On your route or near your worksite, can you use a common water source (spring, tap or stream) without paying?", "Shared water access on the route. Three answers, because no source and a source you must pay for are different situations.", "cat", "cprwater", skip="May be left blank", source="Krantz 2001, natural capital (water) and access ('the opportunity in practice to use a resource'); item wording is ours")
R("M", "cpr_governance", "Who decides who may use the common land here", "In the Yatra region or workplace region, who decides who may use the common land and forest? Ask and code what they name; do not read the list.", "Governance of the common resource. ENUMERATOR NOTE: a village head or panchayat is code 1; code 3 only for a formal local committee or community group.", "cat", "cprgov", skip="May be left blank", source="NO SOURCE ON DISK YET: Krantz does not address governance of common land. To be sourced from Agrawal 2001 or Ostrom 1990 once read on disk")

# ------------------------------------------------------------------ CONSTRUCTED (built in Stata from the asked variables)
def C(name, label, desc, formula, kind="num", lset=None, source="Constructed"):
    R("X", name, label, "Not asked. Constructed.", desc, kind, lset, origin="constructed", formula=formula, source=source)

C("education_years", "Years of schooling completed", "The direct year count (years_schooling) when the respondent knew it; otherwise the midpoint of the fallback bracket (education_level_cat: 0/2/7/11 for no-formal/some-primary/primary-complete/secondary-plus); missing if the respondent preferred not to say.",
  "years_schooling if knows_years_schooling==1, else bracket midpoint from education_level_cat", source="NITI Aayog National MPI")
C("hoh_female", "Sex of the household head", "Derived from the gendered relationship categories: husband/father/son/brother/other-male imply a male head, wife/mother/daughter/sister/other-female a female head, and when the respondent IS the head it is their own sex. Replaces a separate male/female question.", "from hoh_relation; = female if hoh_relation==1", "bin", "sex")
# home_rural_urban stopped being constructed on 2026-09-28 and is now asked directly in Module D.
# It was derived from home_admin_level (village -> rural, town or city -> urban), which put a 45%
# swing in the poverty line — Rs 2,515 against Rs 3,639 — behind a three-way tier the respondent
# was in no position to classify. The binary is what the line needs and what a respondent can answer.

# ---- measured seasonal base, from the Module C location row -----------------------------------
C("months_here", "Months living on the Yatra route in the past year", "Derived from the absence spell: 12 minus the months between left_here_month and returned_here_month, or 12 for a respondent who never leaves. This is the measured length of the respondent OWN season, in place of a constant applied to everyone, and it is what the mid-month Yatra-start problem resolves to — the boundary is the month they reported, not one we chose. Built straight from the spell as of 2026-10-01; it used to be 12 minus months_home_base minus months_third_place, which routed the season weight — the weight on every consumption and income figure in the study — through the months_away_for_work answer. It no longer depends on it.", "12 - months_away_total", "count", source="Project design (measured from the absence spell, Module C)")
# months_home_base and months_third_place dropped 2026-10-01 with months_away_for_work, the only
# question either was built from. Neither appeared in a covariate vector or a deprivation
# indicator. The absence spell still gives months_away_total and months_here.
C("closure_labour_migrant", "Sold labour away from both bases during the closure", "1 if the respondent reported working away during the closure. Type B in the closure-regime typology and the mobility variable that actually carries information in this population, in place of a migrant dummy built on district boundaries — which the pilot shows would classify 11 of 20 seasonal movers as non-movers.", "worked_away_in_closure==1", "bin", "yn", source="Project design (off-season labour migration)")
C("cons_pc_denom_season", "People the Yatra-season consumption figures cover", "n_here_season for a split household, hhsize for everyone else. This is the fix for a real error in the poverty headcount: per-capita consumption divided the Yatra-season figure — which covers only \"you and anyone staying with you here\" — by the FULL household size, so a man supporting himself here for six months while a family of five lived at the home place was recorded at a fraction of his true per-capita consumption and counted as poor by arithmetic. The off-season half keeps hhsize, because by then the household is reunited.", "hhsize", "count", source="Project design (season-specific denominator)")
C("stays_all_year", "Does not move at all when the Yatra closes", "1 if the respondent does not go to the home place at closure. The case the two-season design of this instrument does NOT fit: for these respondents the Yatra-season and off-season questions describe the same place, and the pair should be checked for a suspiciously high identical-answer rate at the pilot.", "resp_returns_at_closure==0", "bin", "yn", source="Project design (assumption check on the two-season recall design)")
C("split_household", "Respondent and household are in different places during the season", "1 if the rest of the household lives at the home place year-round. The case Module E Yatra-season wording was written for, and the case whose per-capita consumption was being computed wrongly until n_here_season existed.", "hh_at_home_place==1", "bin", "yn", source="Project design (split-household measurement, underpinning Module E)")
C("credit_institutional", "Borrowed from an institutional lender", "1 if the household borrowed in the last 12 months from a bank, cooperative, RRB, microfinance institution or SHG (credit_source 1-4); 0 otherwise, INCLUDING households that did not borrow at all. Defined for every respondent on purpose: credit_source itself is now gated behind took_loan_12m, so using it directly as a VEP covariate would drop every non-borrower from the regression.", "took_loan_12m==1 & inrange(credit_source,1,4)", "bin", "yn", source="VEP adaptive-capacity covariate")
C("credit_informal", "Borrowed from an informal lender", "1 if the household borrowed from a moneylender, relative, friend, employer or contractor (credit_source 5-8); 0 otherwise, including non-borrowers. Separated from institutional credit because the two have opposite signs for vulnerability.", "took_loan_12m==1 & inrange(credit_source,5,8)", "bin", "yn", source="VEP adaptive-capacity covariate")
C("migrant", "Migrant: permanent home is outside the district", "1 if origin is not Local (same district).", "origin > 1", "bin", "yn")
C("health_access_tier", "Health-access tier of the site", "Remoteness of the interview site along the route, derived from the interview GPS rather than from an enumerator-coded cluster: the route runs from the road-head and its hospital up to the shrine, so position along it is what determines how reachable care is. Latitude bands (research team's route crosswalk): below 30.58 Good, 30.58 to 30.66 Moderate, 30.66 and above Poor. Bands, not coordinates, enter the analysis, so the exported data still carries no named site.",
  "from gps_lat: 3 if <30.58; 2 if 30.58-30.66; 1 if >=30.66", "cat", "tier", source="Project design; VEP exposure covariate")
C("health_access_deprived", "Health-access deprived (project measure, NOT an MPI indicator)", "1 if the site tier is Poor, or Moderate and nobody in the household has health cover. health_insurance_covered was REMOVED: it asked whether \"your household\" is covered, which for a split migrant household — the worker here, the family elsewhere — does not name a group the respondent can answer for. n_health_insured, a count of covered members, replaces it and is strictly more informative. This variable is also no longer part of the MPI: the health dimension now uses NITI's own mortality and maternal indicators, so this is kept only as a VEP exposure covariate.", "tier==1 | (tier==2 & n_health_insured==0)", "bin", "yn", source="Project design (health-access exposure covariate; not a NITI indicator)")

C("yatra_months", "Months of Yatra EARNINGS in the past year", "Count of calendar months coded 1, Yatra work proper. Preparation months (status 9) are NOT counted: this is the denominator for earnings per Yatra month, and a month spent buying stock and repairing tack is not a month that produced the income being divided.", "months_worked_yatra, asked directly", "count")
C("yatra_months_liv", "Months of Yatra LIVELIHOOD (work plus preparation)", "yatra_months + yatra_prep_months, i.e. exactly what yatra_months counted before the 2026-10-03 split. Every season-weighted annual figure below uses THIS, not yatra_months, so those figures are numerically unchanged by the split: the respondent is tied to the route during preparation as much as during the season, and it is that, not whether he was earning, that decides which spending and coping regime he is in.", "yatra_months + yatra_prep_months", "count")
C("offseason_months_worked", "Months of paid work outside the Yatra work", "Months coded 2 to 7 (any paid activity other than Yatra work).", "12 - months_worked_yatra - months_no_paid_work, floored at 0", "count")
C("months_no_work", "Months in the year without any paid work", "Months coded 8.", "months_no_paid_work, asked directly", "count")
C("offseason_primary", "Main activity outside the Yatra season", "The activity that fills most of the non-Yatra months (ties go to the lower code; all months idle gives 8).", "offseason_activity, asked directly", "cat", "activity")
C("yatra_income", "Annual work income from Yatra months (Rs)", "Calendar path: sum of monthly earnings in the months coded Yatra work. Fallback path: the annual total times the respondent's own Yatra share.",
  "income_annual_total * pct_income_yatra/100", "money")
C("non_yatra_income", "Annual work income from other months (Rs)", "Calendar path: sum of monthly earnings in the other months. Fallback path: the annual total times the remaining share.",
  "income_annual_total * (100-pct_income_yatra)/100", "money")
C("income_pm_yatra_eq", "Earnings per Yatra-season month, fallback path (Rs)", "Yatra earnings spread evenly across the months the calendar codes as Yatra work. Defined for fallback respondents only; for calendar respondents the actual monthly figures are used instead.",
  "yatra_income / yatra_months if income_from_fallback==1", "money")
C("income_pm_other_eq", "Earnings per non-Yatra month, fallback path (Rs)", "Non-Yatra earnings spread evenly across the remaining months. Defined for fallback respondents only.",
  "non_yatra_income / (12 - yatra_months_liv) if income_from_fallback==1", "money")
C("remittance_outward_annual", "Total outward remittances, annual (Rs)", "Yatra-season months at the Yatra-season usual amount, other months at the off-season usual amount.",
  "yatra_months_liv*remit_out_yatra_pm + (12-yatra_months_liv)*remit_out_offseason_pm", "money", source="NSS 64th Round practice, applied to the calendar [source not held by this project; citation unverified as of 2026-09-28]")
C("remittance_inward_annual", "Total inward remittances, annual (Rs)", "Yatra-season months at the Yatra-season usual amount, other months at the off-season usual amount.",
  "yatra_months_liv*remit_in_yatra_pm + (12-yatra_months_liv)*remit_in_offseason_pm", "money", source="NSS 64th Round practice, applied to the calendar [source not held by this project; citation unverified as of 2026-09-28]")
C("total_annual_income", "Total annual income (Rs)", "Work income plus inward remittances. Outward remittances are not subtracted.", "yatra_income + non_yatra_income + remittance_inward_annual", "money")
C("yatra_income_share", "Share of annual income from Yatra months", "Yatra income divided by total annual income (an Exposure covariate in the VEP model).", "yatra_income / total_annual_income")
C("income_seasonality_cv", "Income seasonality: CV of the 12 monthly earnings", "Calendar path: coefficient of variation across the twelve reported monthly earnings (n-1 divisor). Fallback path: the same CV computed on a two-level series — income_pm_yatra_eq in each Yatra month, income_pm_other_eq in each other month — so the variable is never missing and no respondent silently drops out of the FGLS for want of it. IMPORTANT: the fallback series has no within-season variation by construction, so its CV captures only the between-season swing and is a LOWER BOUND on true seasonality. Always run the VEP arms with income_from_fallback interacted or split; do not treat the two paths as the same measurement.",
  "calendar: rowsd(income_m1..12)/rowmean(income_m1..12); fallback: CV of the two-level series built from income_pm_yatra_eq and income_pm_other_eq over yatra_months and 12-yatra_months",
  source="Azeem et al. 2016; Khandker 2012; Dercon and Krishnan 2000")
CSEAS = ("Workers are migrants, so a consumption module fielded during the Yatra season cannot be treated as "
         "representative of the whole year. Every seasonal item (module E, 9 pairs) is combined the same way: "
         "Yatra-season months at the Yatra-season usual amount, other months at the off-season usual amount, "
         "then divided by 12 for a monthly-equivalent figure — the same weighting already used for income.")
for _nm, _lab in [("staples", "Staples"), ("perishables", "Perishables"), ("food_own", "Home-grown/gifted food"),
                  ("food_out", "Food eaten outside"), ("fuel", "Fuel and light"), ("routine_misc", "Toiletries/consumables"),
                  ("transport_comm", "Transport/communication"), ("rent", "Rent"), ("med_nonhosp", "Medical, non-hospital"), ("packaged_food", "Packaged snacks and drinks"), ("pan_tobacco", "Pan, tobacco and intoxicants")]:
    C(f"cons_{_nm}_pm", f"{_lab}, annual-average month (Rs)", f"{_lab} spending, weighted by the length of the Yatra season and the rest of the year.",
      f"(yatra_months_liv*cons_{_nm}_yatra_pm + (12-yatra_months_liv)*cons_{_nm}_offseason_pm)/12", "money", source=CSEAS)
C("cons_food_pm", "Total food, annual-average month (Rs)", "Staples + perishables + home-grown/gifted + eaten outside + packaged snacks and drinks, each already weighted by season. Packaged food is inside HCES's own food block (Section 7), so it belongs here; pan, tobacco and intoxicants are a separate MPCE category in HCES and are added to total_cons_pm instead.",
  "cons_staples_pm + cons_perishables_pm + cons_food_own_pm + cons_food_out_pm + cons_packaged_food_pm", "money", source=HC + " mixed reference period; Eze and Iheonu 2025 (food components); Calvo and Dercon 2007")
C("cons_clothing_12m_pm", "Clothing spending per month (Rs)", "Annual figure divided by 12, rounded.", "round(cons_clothing_12m/12)", "money")
C("cons_education_12m_pm", "Education spending per month (Rs)", "Annual figure divided by 12, rounded.", "round(cons_education_12m/12)", "money")
C("cons_medical_12m", "Total medical spending, last 12 months (Rs)", "Non-hospitalisation (annual-average month x 12) + hospitalisation (12-month).", "cons_med_nonhosp_pm*12 + cons_medical_hosp_12m", "money", source=HC + " Sections 10.2-10.3; " + IH + " 14.33-14.34")
C("cons_medical_12m_pm", "Medical spending per month (Rs)", "Non-hospitalisation (already an annual-average month) + hospitalisation divided by 12, rounded.", "cons_med_nonhosp_pm + round(cons_medical_hosp_12m/12)", "money")
C("cons_durables_12m_pm", "Durables spending per month (Rs)", "Annual figure divided by 12, rounded.", "round(cons_durables_12m/12)", "money")
C("total_cons_pm", "Household consumption per month (Rs)", "Food (annual-average month above) + fuel + toiletries + transport/communication + rent (each annual-average) + the four monthly-equivalent annual items. This is a true annual-average monthly figure, not a single-season snapshot.",
  "food_pm (now incl. packaged) + pan_tobacco_pm + fuel_pm + routine_misc_pm + transport_comm_pm + rent_pm + clothing_pm + education_pm + medical_pm + durables_pm", "money", source="Chaudhuri et al. 2002 welfare measure; season-weighting added for a migrant population")
C("cons_pc_pm", "Per-capita monthly consumption (Rs)", "Household consumption per month divided by household size, rounded. This is the VEP outcome (its log).", "round(total_cons_pm / hhsize)", "money", source="Chaudhuri et al. 2002")
C("cons_pc_pm_narrow", "Per-capita monthly consumption, narrow (Rs)", "Only the non-lumpy items (food incl. packaged, pan/tobacco, fuel, toiletries, transport/communication, rent), each already an annual-average month, per person. Leaves out the annual items, as in Dercon and Krishnan 2000. For robustness of the variance model; not comparable with the poverty line.",
  "(food_pm + pan_tobacco_pm + fuel_pm + routine_misc_pm + transport_comm_pm + rent_pm) / hhsize", "money", source="Dercon and Krishnan 2000 (narrow non-food to avoid seasonal lumps)")
C("n_children_u15", "Household children under 15", "The two asked bands added: children under 6 plus children aged 6 to 14. Asked directly until 2026-10-01, alongside the 6-to-14 count that is a subset of it — which made the respondent subtract one from the other and let the two contradict. Two disjoint bands partition it exactly, so this is now arithmetic and the contradiction cannot arise.", "n_children_u6 + n_children_6_14", "count", source="Adult-equivalent scales (Claro et al. 2010; Awuni et al. 2023)")
C("cons_pc_ae_pm", "Consumption per adult equivalent per month (Rs)", "Household consumption divided by (adults + 0.5 x children under 15), where adults = household size minus children under 15. One simple scale; the choice of scale is a sensitivity check.",
  "total_cons_pm / (hhsize - n_children_u15 + 0.5*n_children_u15)", "money", source="Adult-equivalent practice (Awuni et al. 2023; Claro et al. 2010 on per-capita versus adult-equivalent)")
C("poverty_line", "Poverty line applying to this respondent (Rs per capita per month)", "Sethu, Surya and Ruthu (2024) construct TWO lines for 2022-23 by the Rangarajan method: Rs 2,515 per capita per month rural and Rs 3,639 urban. Which applies is decided by home_rural_urban — the respondent's USUAL place of residence, not the Yatra worksite. Until this variable existed the build applied the rural line to everyone, which measured urban-resident workers against a line 31 percent too low and understated their poverty.", "2515 if home_rural_urban==1, else 3639", "money", source="Sethu, Surya and Ruthu 2024 (Rangarajan method on HCES 2022-23), both lines")
C("poor", "Poor: consumption below the applicable line", "1 if per-capita monthly consumption is below the rural or urban line that applies to this respondent.", "cons_pc_pm < poverty_line", "bin", "yn", source="Sethu, Surya and Ruthu 2024")
C("poor_sensitivity_cpi", "Poor on the Rs 1,850 line (sensitivity)", "1 if below the Rangarajan and Dev 2024 CPI-adjusted line; robustness only.", "cons_pc_pm < 1850", "bin", "yn", source="Rangarajan and Dev 2024")
C("durables_count", "Number of durables owned (0-6, legacy)", "Legacy six-item count kept only so earlier outputs stay reproducible. DO NOT use for the MPI: the asset indicator is mpi_asset_deprived, which applies NITI's actual rule to its actual eight-item list.", "owns_tv + owns_radio + owns_bicycle + owns_motorcycle + owns_car + owns_fridge", "count")
C("productive_assets_count", "Number of productive/livelihood assets owned (0-6)", "Sum of the six productive-asset binaries (livestock, pony/mule, shop/stall, work vehicle, work equipment).",
  "owns_cow_buffalo + owns_goat_sheep + owns_pony_mule + owns_shop_stall + owns_work_vehicle + owns_work_equipment", "count")
C("water_deprived", "MPI: deprived on drinking water", "NITI rule, BOTH limbs: deprived if the source is unimproved (codes 7-9), OR the source is improved but the round trip to fetch it takes over 30 minutes. The second limb could not be evaluated at all before water_on_premises and water_fetch_minutes existed.", "inrange(drinking_water,7,9) | (water_on_premises==0 & water_fetch_minutes>30)", "bin", "yn", source="NITI Aayog National MPI drinking-water indicator")
C("cooking_fuel_deprived", "MPI: deprived on cooking fuel", "NITI rule: deprived if the household cooks with firewood, dung, crop residue/shrubs, charcoal or coal (codes 6-10). Kerosene (5) is NOT counted, because NITI's own list does not name it; the global MPI does count it, so this is a documented departure and the raw fuel code is retained so either rule can be applied later.", "inlist(cooking_fuel,6,7,8,9,10)", "bin", "yn", source="NITI Aayog National MPI cooking-fuel indicator")
C("mpi_asset_count", "Number of the eight NITI small assets owned (0-8)", "Radio, TV, telephone, computer, animal cart, bicycle, motorbike, refrigerator — NITI's own list. Car or truck is NOT in this count; it is a separate limb of the indicator.", "owns_radio + owns_tv + owns_phone + owns_computer + owns_animal_cart + owns_bicycle + owns_motorcycle + owns_fridge", "count", source="NITI Aayog National MPI assets indicator")
C("mpi_asset_deprived", "MPI: deprived on assets", "NITI rule exactly: deprived if the household does not own MORE THAN ONE of the eight small assets AND does not own a car or truck. The previous version summed six assets into a plain count, which is not NITI's rule and is not comparable to any published National MPI figure.", "mpi_asset_count <= 1 & owns_car == 0", "bin", "yn", source="NITI Aayog National MPI assets indicator")
# ---- shocks and coping: the check-all exports split into binaries ---------------------------
# Code 9 is "nothing of this kind happened" — the escape option on a required multi-select, not a
# shock. It gets no shock_* dummy; the build carries it as no_shock_reported instead, which keeps
# shock_count a count of shocks rather than of ticks.
for _k, _lab in sorted(LSETS["distress"].items()):
    if _k == 9:
        continue
    C(f"shock_{_k}", f"Shock: {_lab}"[:80], f"1 if '{_lab}' was ticked.", f"distress_event_last365d contains {_k}", "bin", "yn", source="Split from the select_multiple export")
C("no_shock_reported", "Explicitly reported that nothing of this kind happened", "1 if code 9 was ticked. Distinct from an empty list, which the form can no longer produce: the item is required and code 9 is how a household with no shock answers it.", "distress_event_last365d contains 9", "bin", "yn", source="Project design (escape option on a required check-all)")
for _k, _lab in sorted(LSETS["coping"].items()):
    C(f"cope_{_k}", f"Coping: {_lab}"[:80], f"1 if '{_lab}' was ticked.", f"shock_coping contains {_k}", "bin", "yn", source="Split from the select_multiple export")
C("shock_count", "Number of distinct shocks reported (0-8)", "Count of shock types ticked. The old single-answer item could only ever be 0 or 1.", "sum of shock_1..8", "count")
C("shock_any", "Suffered any shock in the last 12 months", "1 if any shock was ticked.", "shock_count > 0", "bin", "yn")
C("shock_covariate", "Suffered a COVARIATE shock", "1 if any of: natural disaster, road or bridge blocked, Yatra stopped or disrupted, sharp fall in customers or prices (codes 3, 5, 6, 7). These hit the whole route at once, so they are the shocks a ropeway — or a flood year — delivers to everyone simultaneously. Separating them from idiosyncratic shocks is what makes the covariate/idiosyncratic variance decomposition identifiable.", "any of shock_3 shock_5 shock_6 shock_7", "bin", "yn", source="Gunther and Harttgen 2009, via Fujii 2016 section 2.2")
C("shock_idiosyncratic", "Suffered an IDIOSYNCRATIC shock", "1 if any of: illness or death of an earning member, crop or livestock loss, loss of business or assets, lost the work (codes 1, 2, 4, 8). These hit one household at a time.", "any of shock_1 shock_2 shock_4 shock_8", "bin", "yn", source="Gunther and Harttgen 2009, via Fujii 2016 section 2.2")
C("coped_sold_assets", "Coped by selling or pawning assets", "1 if selling or pawning assets was among the responses. Kept as its own variable because the asset-smoothing test compares it directly against cutting consumption, and the two are no longer mutually exclusive.", "cope_3", "bin", "yn", source="Carter and Zimmerman 2000")
C("coped_cut_consumption", "Coped by cutting consumption", "1 if cutting consumption was among the responses. See coped_sold_assets — a household doing BOTH, or cutting consumption precisely in order to avoid selling, is the case the single-answer item could not represent.", "cope_4", "bin", "yn", source="Carter and Zimmerman 2000; Zimmerman and Carter 2003")
# ---- NITI Aayog National MPI: the indicators, at NITI's own weights -------------------------
# Health 1/3 = Nutrition 1/6 + Child & Adolescent Mortality 1/12 + Maternal Health 1/12
# Education 1/3 = Years of Schooling 1/6 + School Attendance 1/6
# Standard of Living 1/3 = seven indicators at 1/21 each
# NUTRITION IS NOT COLLECTED — it requires anthropometry. Its 1/6 is therefore redistributed
# across the remaining eleven in proportion to their own weights, and the resulting index MUST be
# reported as an ELEVEN-of-twelve-indicator adaptation, not as the National MPI. See
# mpi_nutrition_proxy_dep and mpi_score_lyons below for the substituted companion score.
C("mpi_mortality_dep", "MPI: child or adolescent mortality", "NITI: a child or adolescent under 18 died in the household in the last five years.", "child_death_5y == 1", "bin", "yn", source="NITI Aayog National MPI (1/12)")
C("mpi_maternal_dep", "MPI: maternal health", "NITI: a woman who gave birth in the last five years did not have at least four antenatal visits for the most recent birth, OR was not assisted by trained personnel at that birth. Households with no birth in the window are NOT deprived, per NITI's own treatment.", "birth_last_5y==1 & (anc_4_visits!=1 | !inlist(skilled_birth_attendant,1,2))", "bin", "yn", source="NITI Aayog National MPI (1/12)")
C("mpi_schooling_dep", "MPI: years of schooling", "NITI: not even one household member aged 10 or older has completed six years of schooling.", "any_member_6yr_schooling == 0", "bin", "yn", source="NITI Aayog National MPI (1/6)")
C("mpi_attendance_dep", "MPI: school attendance", "NITI: any school-aged child is not attending school up to the age at which they would complete class 8. Not deprived where the household has no child in that range.", "(n_children_6_14 - n_children_in_school) > 0 if n_children_6_14 > 0", "bin", "yn", source="NITI Aayog National MPI (1/6)")
C("mpi_housing_dep", "MPI: housing", "NITI: the floor is natural material, OR the roof OR the wall is rudimentary. All three limbs are now collected; the wall limb was previously missing entirely.", "floor_material==1 | roof_material==1 | wall_material==1", "bin", "yn", source="NITI Aayog National MPI (1/21)")
C("mpi_sanitation_dep", "MPI: sanitation", "NITI: unimproved or no facility, OR improved but shared with other households.", "inlist(toilet_type,1,2,3)", "bin", "yn", source="NITI Aayog National MPI (1/21)")
C("mpi_electricity_dep", "MPI: electricity", "NITI: the household has no electricity.", "electricity == 0", "bin", "yn", source="NITI Aayog National MPI (1/21)")
C("mpi_bank_dep", "MPI: bank account", "NITI: no household member has a bank account or a post office account.", "has_bank_account == 0", "bin", "yn", source="NITI Aayog National MPI (1/21)")
C("mpi_score", "MPI deprivation score (11 of NITI's 12 indicators, reweighted)", "Weighted sum of the eleven collected indicators — mortality, maternal health, years of schooling, school attendance, cooking fuel, sanitation, drinking water, electricity, housing, assets and bank account. Nutrition (1/6) cannot be collected without anthropometry, so the remaining weights are scaled up proportionally to sum to 1. REPORT THIS AS AN ADAPTATION, never as the National MPI, and name the absent indicator. mpi_score_lyons is the companion that substitutes rather than omits. (The label said TEN until 2026-10-01; eleven of the twelve are collected, and the formula always summed eleven.)",
  "(1/12*mortality + 1/12*maternal + 1/6*schooling + 1/6*attendance + 1/21*(fuel+sanitation+water+electricity+housing+assets+bank)) / (1 - 1/6)", "num", source="NITI Aayog National MPI structure, nutrition omitted")
C("mpi_poor", "MPI-poor (deprivation score at or above 1/3)", "Alkire-Foster identification at the standard k = 33.3 percent cutoff.", "mpi_score >= 1/3", "bin", "yn", source="Alkire and Foster 2011; NITI Aayog National MPI")
C("shock_earnings_lost", "Earnings lost to the worst shock, at measured wages (Rs)", "Weeks of work lost times the respondent's own weekly earnings in the season the shock fell in — Yatra-season weekly earnings if shock_month is inside the measured season, off-season weekly earnings otherwise. The respondent is never asked to value his own forgone work: he reports the weeks, and the wage is the one this instrument already measured from him.", "shock_work_lost_weeks * (season-matched weekly earnings)", "money", source="Project design (the time limb of shock magnitude, valued at measured earnings)")
C("shock_loss_total", "Total cost of the worst shock: earnings lost plus money spent (Rs)", "The two limbs added. This is what shock_loss_amount used to ask the respondent to add up in his head — including valuing his own lost work — and it replaces it everywhere, including in shock_loss_share. Report the limbs separately too: a shock that costs only time and a shock that costs only cash are different events for a household with no savings.", "shock_earnings_lost + shock_money_spent", "money", source="Ligon and Schechter 2003; Dercon and Krishnan 2000")

# ---- NITI Nutrition: the one indicator this instrument cannot collect, and the substitute ----
# NITI defines Nutrition (weight 1/6) on ANTHROPOMETRY — measured height, weight and BMI for
# children 0-59 months, women 15-49 and men 15-54. A read-aloud interview at a roadside worksite
# cannot produce that, and no proxy makes it the National MPI's indicator. Two scores are therefore
# built and BOTH are reported:
#   mpi_score        the strict version. Eleven of twelve indicators, Nutrition absent, its 1/6
#                    redistributed proportionally over the eleven. Conservative and transparent:
#                    it claims nothing about nutrition at all.
#   mpi_score_lyons  the substituted version. The food-coping indicator takes Nutrition's 1/6
#                    slot, so all twelve weights are filled and no reweighting happens. This is a
#                    SUBSTITUTION, not a measurement of undernourishment: rCSI measures what the
#                    household did because food or money for food ran short, which is the
#                    food-insecurity route INTO undernutrition rather than undernutrition itself.
#                    It is the indicator Lyons et al. (2023) use for the same dimension in a
#                    survey that likewise could not weigh anybody, at the same cutoff.
# The difference between the two scores is the sensitivity of the headcount to that substitution,
# and it belongs in the robustness table.
# ---- the asset binaries, split out of the two check-alls (2026-10-05) --------------------------
# assets_owned and livestock_owned are single multi-selects on screen; these twelve are what the
# rest of the build reads, and they are the same twelve names the interviews already collected on
# build 4b87e5 hold as ASKED columns. Stata takes the multi-select where it exists and the old
# asked column where it does not, so neither shape of record is stranded.
C("health_insured_any", "Household has any health insurance or scheme", "Replaces n_health_insured (a count). Split out of insurance_held.", "insurance_held contains 1", "bin", "yn", source="NITI Aayog National MPI health-insurance indicator; Lyons et al. 2023")
C("life_insured_any", "Household has any life insurance", "Replaces n_life_insured (a count). Split out of insurance_held.", "insurance_held contains 2", "bin", "yn")
C("has_crop_insurance", "Household has crop insurance", "Was asked directly through 2026-10-06 (gated on land); now split out of insurance_held, which needs no land gate since a landless household will not tick it.", "insurance_held contains 3", "bin", "yn")
C("fies_skipped_meal", "FIES: had to skip a meal, last 12 months", "FIES item 4, the least severe of the five. Split out of fies_items; missing only if fies_items itself was left entirely blank.", "fies_items contains 1", "bin", "yn")
C("fies_ate_less", "FIES: ate less than you thought you should, last 12 months", "FIES item 5. Split out of fies_items.", "fies_items contains 2", "bin", "yn")
C("fies_ran_out", "FIES: the household ran out of food, last 12 months", "FIES item 6, the one household-referenced item of the five. Split out of fies_items.", "fies_items contains 3", "bin", "yn")
C("fies_hungry", "FIES: was hungry but did not eat, last 12 months", "FIES item 7. Split out of fies_items.", "fies_items contains 4", "bin", "yn")
C("fies_whole_day", "FIES: went a whole day without eating, last 12 months", "FIES item 8, the most severe. Split out of fies_items.", "fies_items contains 5", "bin", "yn")
C("owns_tv", "Owns a television", "Split out of assets_owned; falls back to the asked column on records collected before 2026-10-05.", "assets_owned contains 1", "bin", "yn", source="NITI Aayog National MPI, Assets")
C("owns_radio", "Owns a radio", "Split out of assets_owned; falls back to the asked column on records collected before 2026-10-05.", "assets_owned contains 2", "bin", "yn", source="NITI Aayog National MPI, Assets")
C("owns_bicycle", "Owns a bicycle", "Split out of assets_owned; falls back to the asked column on records collected before 2026-10-05.", "assets_owned contains 3", "bin", "yn", source="NITI Aayog National MPI, Assets")
C("owns_motorcycle", "Owns a motorcycle or scooter", "Split out of assets_owned; falls back to the asked column on records collected before 2026-10-05.", "assets_owned contains 4", "bin", "yn", source="NITI Aayog National MPI, Assets")
C("owns_car", "Owns a car, jeep or truck", "Split out of assets_owned; falls back to the asked column on records collected before 2026-10-05.", "assets_owned contains 5", "bin", "yn", source="NITI Aayog National MPI, Assets")
C("owns_phone", "Household owns any telephone (mobile or landline)", "Split out of assets_owned; falls back to the asked column on records collected before 2026-10-05.", "assets_owned contains 6", "bin", "yn", source="NITI Aayog National MPI, Assets")
C("owns_computer", "Owns a computer or laptop", "Split out of assets_owned; falls back to the asked column on records collected before 2026-10-05.", "assets_owned contains 7", "bin", "yn", source="NITI Aayog National MPI, Assets")
C("owns_animal_cart", "Owns an animal cart", "Split out of assets_owned; falls back to the asked column on records collected before 2026-10-05.", "assets_owned contains 8", "bin", "yn", source="NITI Aayog National MPI, Assets")
C("owns_fridge", "Owns a refrigerator", "Split out of assets_owned; falls back to the asked column on records collected before 2026-10-05.", "assets_owned contains 9", "bin", "yn", source="NITI Aayog National MPI, Assets")
C("owns_cow_buffalo", "Owns any cows or buffaloes", "Split out of livestock_owned; falls back to the asked column on records collected before 2026-10-05.", "livestock_owned contains 1", "bin", "yn", source="Chaudhuri et al. 2002 asset covariate")
C("owns_goat_sheep", "Owns any goats or sheep", "Split out of livestock_owned; falls back to the asked column on records collected before 2026-10-05.", "livestock_owned contains 2", "bin", "yn", source="Chaudhuri et al. 2002 asset covariate")
C("owns_pony_mule", "Owns any ponies or mules", "Split out of livestock_owned; falls back to the asked column on records collected before 2026-10-05.", "livestock_owned contains 3", "bin", "yn", source="Chaudhuri et al. 2002 asset covariate")

# ---- food security: FIES raw score and the moderate-or-severe line ---------------------------
C("fies_raw", "FIES raw score, 0 to 5 behavioural items", "Count of yes answers across the five FIES behavioural items. Unweighted, by design: FIES is an ordered severity scale, not a frequency-by-severity index like the rCSI it replaces, so applying weights to it would be a category error. Missing only where all five were left blank.",
  "fies_skipped_meal + fies_ate_less + fies_ran_out + fies_hungry + fies_whole_day", "count",
  source="FAO Food Insecurity Experience Scale (SDG 2.1.2), behavioural items")
C("fies_mod_sev", "Food insecure, moderate or severe (FIES 2 or more)", "1 if two or more of the five behavioural items were answered yes. Replaces food_coping_deprived (rCSI > 20), whose threshold was Lyons et al.'s, calibrated on Lebanese refugee households answering the original 7-day rCSI -- a cutoff on a quantity this instrument was not measuring. Two or more behavioural items is the conventional moderate-or-severe line.",
  "fies_raw >= 2", "bin", "yn", source="FAO FIES; moderate-or-severe on the behavioural items")
C("mpi_nutrition_proxy_dep", "MPI nutrition SUBSTITUTE: food-coping deprived (not anthropometry)", "fies_mod_sev, standing in for NITI's Nutrition indicator in mpi_score_lyons only. NOT a measure of undernourishment and must never be labelled as one: it is moderate-or-severe food insecurity on the FAO FIES behavioural items, occupying the 1/6 weight NITI gives to a measurement this instrument cannot take (anthropometry). Rewired from food_coping_deprived (rCSI > 20) on 2026-10-05 with the rest of the food-security block. FIES is the better occupant of the slot on its own terms -- it measures experience of insufficient food, which is one step from undernourishment, where the rCSI measured coping acts, which is two -- but it is still a substitution and must be reported as one.", "fies_mod_sev == 1", "bin", "yn", source="Lyons et al. 2023 Table 2 indicator 3, substituted for NITI Aayog Nutrition (1/6); Alkire and Foster 2011 on indicator substitution")
C("mpi_score_lyons", "MPI deprivation score, 12 of 12 with the Lyons food-coping substitute", "All twelve NITI weights filled, with the food-coping indicator in the Nutrition slot at 1/6 and no reweighting. Report alongside mpi_score, never instead of it, and state the substitution.", "mpi_score with (1/6)*mpi_nutrition_proxy_dep in place of the reweighting", "num", source="NITI Aayog National MPI structure; Lyons et al. 2023 nutrition substitute")
C("mpi_poor_lyons", "MPI-poor under the substituted score (score at or above 1/3)", "Alkire-Foster identification at k = 33.3 percent on mpi_score_lyons. The gap between this headcount and mpi_poor is the sensitivity of the result to the nutrition substitution.", "mpi_score_lyons >= 1/3", "bin", "yn", source="Alkire and Foster 2011; NITI Aayog National MPI")
C("hours_week_yatra", "Hours worked per week in the Yatra season", "Hours per day times days per week.", "hours_day_yatra * days_week_yatra", "count", source="Apablaza et al. 2026 Q13 (decomposed into hours/day x days/week when asked, for ease of recall)")
C("hours_week_offseason", "Hours worked per week outside the Yatra season", "Hours per day times days per week, off-season. Missing for respondents with no off-season paid work at all.", "hours_day_offseason * days_week_offseason", "count", source="Apablaza et al. 2026 Q13")
C("hours_week_annual", "Average weekly hours across the months actually worked", "Yatra-season and off-season weekly hours, weighted by how many months of each the calendar records. Averaged over WORKED months only, so idle months do not drag the figure to zero — idleness is measured by months_no_work, and counting it here too would penalise it twice.", "(yatra_months*hours_week_yatra + offseason_months_worked*hours_week_offseason) / (yatra_months + offseason_months_worked)", "num", source="Apablaza et al. 2026 Q13, weighted onto the work calendar")
C("work_income_pm", "Average monthly work income over the year (Rs)", "(Yatra income + other work income) divided by 12.", "(yatra_income + non_yatra_income)/12", "money", source="Apablaza et al. 2026 Q14")
KS = "Apablaza et al. 2026, employment table (weights as supplied 2026-10-03)"
# The one input the employment table needs that this project does not hold: the national basic food
# basket (the table cites ECLAC; no Indian figure is in the literature folder). Left None on purpose.
# The labour-income limb and the composite score stay blank until a value is entered, rather than a
# number being guessed. Enter the monthly rupee value here and rebuild.
EMP_BASKET_PM = None
C("emp_inc_dep", "Employment deprivation: low earnings", "1 if average monthly work income is below six times the national basic food basket (EMP_BASKET_PM). Until that is set, the fallback is 67 percent of the median work income of working respondents, the Apablaza fallback.", "work_income_pm < 6*EMP_BASKET_PM", "bin", "yn", source=KS + ": labour income, weight 1/4")
C("emp_stab_dep", "Employment deprivation: tenure", "1 if under 36 months (3 years) in the current job, from the years question.", "years_current_job < 3", "bin", "yn", source=KS + ": tenure (36 months), weight 1/8")
C("emp_unemp_dep", "Employment deprivation: unemployment risk", "1 if the respondent looked for work at least once in the last 12 months. Set to 0 where the question was not asked, because it is asked only where there were idle months.", "months_looked_for_work > 0 (0 where not asked)", "bin", "yn", source=KS + ": unemployed at least once in 12 months, weight 1/8")
C("emp_sec_dep", "Employment deprivation: social security", "1 if not enrolled in any social-security scheme.", "social_security_any == 0", "bin", "yn", source=KS + ": no affiliation to social security, weight 1/8")
C("emp_occ_dep", "Employment deprivation: occupational status", "1 if self-employed without higher education, or wage-employed without a contract (contract code 3 only).", "(inlist(employment_type,1,2) & higher_ed==0) | (inlist(employment_type,3,4) & contract_status==3)", "bin", "yn", source=KS + ": occupational status, weight 1/8")
C("emp_hours_dep", "Employment deprivation: excessive hours", "1 if the average weekly hours across worked months exceed 48.", "hours_week_annual > 48", "bin", "yn", source=KS + ": excessive working hours, weight 1/16")
C("emp_intens_dep", "Employment deprivation: work intensity", "1 if at least two of the three intensity demands hold for more than half the working day.", "(intens_speed==1) + (intens_deadline==1) + (intens_time==1) >= 2", "bin", "yn", source=KS + ": high work intensity, weight 1/16")
C("emp_posture_dep", "Employment deprivation: posture-related risk", "1 if at least two of the three posture demands hold for more than half the working day.", "(posture_position==1) + (posture_loads==1) + (posture_repetitive==1) >= 2", "bin", "yn", source=KS + ": high posture-related risk, weight 1/16")
C("emp_phys_dep", "Employment deprivation: physical risk", "1 if exposed to loud noise OR extreme heat or cold for more than half the working day.", "phys_noise==1 | phys_temperature==1", "bin", "yn", source=KS + ": high physical risk, weight 1/16")
C("emp_score", "Employment vulnerability score (modified index, 0-1)", "Apablaza weights: low earnings 1/4; tenure, unemployment risk, social security and occupational status 1/8 each; the four conditions items 1/16 each. Blank while EMP_BASKET_PM is unset.", "(1/4)*emp_inc_dep + (1/8)*(emp_stab_dep+emp_unemp_dep+emp_sec_dep+emp_occ_dep) + (1/16)*(emp_hours_dep+emp_intens_dep+emp_posture_dep+emp_phys_dep)", "num", source=KS)
C("emp_poor", "Employment-poor: modified score at or above 1/3", "The cut-off of 1/3 is a convention carried over from the MPI, not a figure in the employment table. Check it against Apablaza's own cut-off before reporting.", "emp_score >= 1/3", "bin", "yn", source="Project choice (cut-off not in the table)")
C("tk_regular_n", "Number of the 12 tasks done regularly", "Count of task answers equal to 1.", "count of tk_* == 1", "count")
C("tk_prior_n", "Number of the 12 tasks done before elsewhere", "Count of task answers equal to 2.", "count of tk_* == 2", "count")

# ---- multiple work-holding: the check-all list, split into binaries -------------------------
for _k, _lab in sorted(LSETS["occ"].items()):
    C(f"other_act_{_k}", f"Other activity: {_lab}"[:80], f"1 if '{_lab}' was ticked in the check-all list of other paid activities.",
      f"other_activity_types contains {_k}", "bin", "yn", source="Split from the select_multiple export")

# ---- ex-ante direction of the required skill move (Nawakitphaitoon and Ormiston 2016) --------
# Ormiston transferability is ASYMMETRIC: t_ij (share of i's skills usable in j) is not t_ji (share
# of j's requirements i already has), and N&O read the asymmetry as direction — "higher
# transferability rates should accompany worker movement from entry-level jobs to more advanced
# positions. In contrast, occupational switches from complex to simple jobs result in the
# obsolescence of previously applicable skills." So the pair (coverage, retention) classifies what
# KIND of retraining a move needs, before anyone moves. No extra question: both come from the task
# grid already asked. Computed here against the closest of the 13 occupations in this survey; the
# tasks_module repeats it against the wider regional destination set and the ropeway jobs.
TRANSNOTE = ("Worker's own task profile uses codes 1 AND 2 (does it now, or has done it before "
             "elsewhere) — prior capability outside the current job is exactly what a transfer "
             "question is about. Destination profiles are the occupation-level share of workers "
             "doing each task (Gathmann and Schonberg's q_oj).")
C("best_alt_occupation", "Closest alternative occupation in task space", "Of the 13 occupations, the one (other than the respondent's own) whose task profile is closest to the respondent's. " + TRANSNOTE,
  "argmax over j != own occupation of cosine(worker profile, q_j)", "cat", "occ", source="Gathmann and Schonberg 2010")
C("task_cover_best", "Share of the closest alternative's tasks the worker already does", "Coverage: of the tasks that alternative occupation requires, the share this worker can already perform. Ormiston's t_ji direction — can the worker step in?",
  "sum(q_best * worker) / sum(q_best)", source="Nawakitphaitoon and Ormiston 2016 (Ormiston 2014 transferability)")
C("task_retain_best", "Share of the worker's own tasks the closest alternative uses", "Retention: of the tasks this worker can perform, the share that alternative occupation would actually use. Ormiston's t_ij direction — how much of their skill survives the move?",
  "sum(q_best * worker) / sum(worker)", source="Nawakitphaitoon and Ormiston 2016 (Ormiston 2014 transferability)")
C("skill_move_type", "Ex-ante type of skill move required", "Direction of the move implied by the coverage/retention pair, both split at 0.5: high-high lateral (move needs little retraining); low coverage but high retention means the destination needs skills the worker lacks while their own still count, i.e. UPSKILLING; high coverage but low retention means the worker has more than the destination uses and much of it goes idle, i.e. DOWNSKILLING; low-low means the skill sets barely overlap, i.e. RESKILLING. " + TRANSNOTE,
  "from (task_cover_best, task_retain_best), each split at 0.5", "cat", "movetype", source="Nawakitphaitoon and Ormiston 2016, section 2.2 (asymmetry of T_ij read as direction)")

# ------------------------------------------------------------------ BUILD STAMP
# The build stamp: today's date plus a short hash of the asked question set. Shown in the web form's
# header and written into every exported row as form_build, so a field report can be matched to the
# form that produced it — a service worker can serve a stale copy of the page indefinitely, and a
# stale build is otherwise indistinguishable from the current one.
# It lives HERE, not in build_webform.py, because the Kobo form has to stamp the same value: two
# builders each computing their own stamp would give the same interview two different build ids
# depending on which form collected it, which defeats the point of having one.
def _build_stamp():
    import datetime, hashlib, json
    names = sorted(r["name"] for r in ROWS if r["origin"] == "asked")
    return (datetime.date.today().isoformat() + "." +
            hashlib.sha1(json.dumps(names).encode()).hexdigest()[:6])

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

BUILD = _build_stamp()
