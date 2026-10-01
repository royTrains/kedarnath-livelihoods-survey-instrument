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
    ("C", "Monthly calendar of work and income; remittances"),
    ("D", "Migration"),
    ("E", "Household consumption"),
    ("F", "Housing, amenities and assets"),
    ("G", "Finance, insurance and schemes"),
    ("H", "Health"),
    ("I", "Food security, shocks and coping"),
    ("J", "Ropeway"),
    ("K", "Job quality (Apablaza et al. 2026 questions)"),
    ("L", "Tasks and skills (short block)"),
]

# The consent script, read verbatim before anything else is asked. This lives here, with the rest of
# the instrument, because it was previously duplicated: build_scripts.py held the full version and
# build_webform.py a shorter paraphrase of it, and NEITHER reached the tablet -- the consent question's
# own text said "Read the consent script" while the script itself appeared only in the printed script.
# An enumerator holding a phone had nothing to read. Informed consent is the one thing in this
# instrument that cannot be left to memory, so it is now rendered on the consent screen itself.
CONSENT_SCRIPT = """We are doing a study on the livelihoods of people who work on the Yatra route. I would like to ask you some questions about your work, your household and your spending.

Taking part is your choice. You can stop at any time, and you can skip any question you do not want to answer. Nothing you tell me will be linked to your name, and nothing you say will affect your work here or any government benefit."""

# Read-aloud module introductions. The enumerator reads these before the module's first question.
# They exist because this instrument asks the same thing twice (two seasons) or twelve times (the
# calendar) in several places, and a respondent who does not know that is coming reads the repetition
# as the enumerator not having listened. Each one says what is about to be asked, how long it runs,
# and -- where it matters -- that rough figures are acceptable. Module P is excluded: consent is its
# own script and must not be prefaced by anything that sounds like persuasion.
INTROS = {
    "A": "First, a few things about you and the people who live in your household.",
    "B": "Now about the work you do here on the Yatra route, and the work you did before this.",
    "C": "Now I want to go through the last twelve months, one month at a time. For each month I will "
         "ask what work you were mainly doing, and then what you usually earned. It is easiest to "
         "start with the Yatra months and fill the rest afterwards.",
    "D": "Now a few questions about where your home is, and what you do when the Yatra closes for the season.",
    "E": "Now about what your household usually spends in a month. For each thing I will ask twice -- "
         "once for a normal month during the Yatra season, and once for a normal month when the Yatra "
         "is closed -- because spending is often quite different in the two. Rough figures are fine.",
    "F": "Now some questions about your house and the things your household has.",
    "G": "Now about savings, loans, insurance and government schemes.",
    "H": "Now a few questions about health in your household. You may leave out any of these.",
    "I": "Now about food, and about any difficult times in the last year and how your household managed.",
    "J": "Now two questions about the ropeway that has been proposed between Gaurikund and Kedarnath.",
    "K": "Now a set of questions about the conditions of your work -- hours, pay, contract and so on. "
         "These come from a standard list used in many countries, so one or two may not fit your "
         "situation. Say so and we will move on.",
    "L": "Last, I will read out some kinds of work-tasks and ask whether you do them. There is no right "
         "or wrong answer -- we are trying to understand what skills the work here actually uses.",
}

# Enumerator hints: shown on the tablet UNDER the question, printed in the scripts and on the paper
# form. These are NOT read to the respondent -- they are the definition the enumerator needs at the
# moment of coding, for the handful of items where two options are genuinely easy to confuse and the
# confusion changes a result. Distinct from build_scripts.PROBE, which is what to SAY next on an
# open-ended item; a hint is how to CODE. Keep them short: a hint nobody reads is worse than none.
HINTS = {
    # emp_dep_stab counts code 3 (occasional/casual) as unstable and code 2 (seasonal) as not, so
    # confusing the two moves the employment-deprivation rate directly. And the default error here is
    # predictable: on this route every job is seasonal in the ordinary sense, because the Yatra
    # closes, so both enumerator and respondent will reach for code 2 unless told otherwise.
    "job_permanence":
        "Both will sound seasonal here -- the Yatra closes for everyone. Ask about WITHIN the season. "
        "One employer keeps them on for a stretch = Seasonal or temporary. They take work day by day "
        "from whoever offers it = Occasional or casual. Self-employed: answer for how their own work "
        "runs. On probation and Fixed-term are rare here; do not reach for them.",

    # The year COUNT is what the MPI education indicator and the Chaudhuri covariate want; the
    # bracket under it is a lossy fallback kept only for people who genuinely cannot say. The
    # predictable error is that respondents answer in LEVELS -- "12th pass", "BA" -- and the
    # enumerator hears that as "does not know the years" and codes No, throwing away a number the
    # respondent has in fact just given, in a different unit.
    "knows_years_schooling":
        "A level is NOT a No. If they answer '8th', '12th pass', 'ITI', 'BA', 'MA' -- code YES and "
        "convert it on the next screen. Code No only if they cannot say how far they went at all.",
    "years_schooling":
        "Enter a NUMBER counted from class 1, never a level. Class 1 to 12 = that class number. "
        "ITI or diploma after 10th = 12. Bachelors = 15, or 16 if the course ran four years -- ASK "
        "how long it ran. Masters = 17, or 18 after a four-year bachelors. If they dropped out part "
        "way through a year, count the completed years only.",
    "any_member_6yr_schooling":
        "The respondent is himself a household member. If HE has six years or more the answer is "
        "Yes -- do not send him looking for someone else. The screen is skipped automatically "
        "wherever his own answer already settles it.",
    # Dropping "Don't know" from the two maternal-health items (2026-10-01) moves the burden onto
    # the probe: the enumerator now has to get an answer rather than record that nobody knew.
    "anc_4_visits":
        "Ask the mother herself if she is there. If not, probe: did she go for check-ups before the "
        "birth, and about how many times? Four or more is Yes; two or three is No. Do not accept a "
        "shrug -- ask how many times she went.",
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
              26: "Uttar Pradesh", 27: "Uttarakhand", 28: "West Bengal",
              29: "Andaman and Nicobar Islands", 30: "Chandigarh",
              31: "Dadra and Nagar Haveli and Daman and Diu", 32: "Delhi",
              33: "Jammu and Kashmir", 34: "Ladakh", 35: "Lakshadweep", 36: "Puducherry",
              99: "Outside India"},
    "ruralurban": {1: "Village (rural)", 2: "Town or city (urban)"},
    # Hill households in Uttarakhand hold land in NALI, not acres, and converting in their head is a
    # source of error the form should not ask for. The unit is recorded and Stata converts: 1 nali is
    # about 1/50 of an acre locally, 1 bigha about 1/5. Record the unit they use, not ours.
    "landunit": {1: "Nali", 2: "Bigha", 3: "Acres", 4: "Hectares", 5: "No land"},
    "loanpurpose": {1: "Medical or hospital costs", 2: "Buying an animal, vehicle or equipment for work",
                    3: "Shop stock or business", 4: "Food or daily household needs",
                    5: "A wedding, funeral or ceremony", 6: "House building or repair",
                    7: "Education", 8: "Repaying another loan", 9: "Something else"},
    "collat": {1: "Jewellery or ornaments", 2: "Land", 3: "Animals", 4: "A vehicle",
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
    # food had only "Dhaba/food-stall owner" -- a dhaba cook or tea-stall helper had nowhere to go and
    # was being pushed into "shop worker" or "Other". (2) AMBIGUITY between shop and dhaba: the real
    # line, and the one NCO draws, is RETAIL GOODS versus PREPARED FOOD, so the labels now say so.
    #   NCO anchors -- 9332 Drivers of Animal-Drawn Vehicles and Machinery (9332.0100 Horse Carriage
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
    # employed by an INDIVIDUAL -- a thekedar, a shop owner, a dhaba owner, i.e. most of this sample --
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
    # One Nation One Ration Card portability -- the closest real analogue to the legal-residency
    # indicator in Lyons et al.: an internal migrant whose entitlement works only at his home place is
    # outside the food safety net for the half of the year he is actually earning.
    "portable": {1: "Yes, can draw it here", 2: "No, only at the home place",
                 3: "Has never tried", 4: "We have no ration card", 97: "Does not know"},
    "month": {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August",
              9: "September", 10: "October", 11: "November", 12: "December"},
    # "Moved to this area" is gone. It answered a different question -- why you MIGRATED, not why
    # you changed work -- so a migrant who took a new job on arrival had two true answers and the
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
    # record distance -- NITI counts an improved source as deprived anyway if it is more than a
    # 30-minute round trip from home, which the old item simply could not detect.
    "water": {1: "Piped into the house or yard", 2: "Public tap or standpipe",
              3: "Handpump, tubewell or borewell", 4: "Protected well or protected spring",
              5: "Rainwater collection", 6: "Bottled, packaged or community RO",
              7: "Unprotected well or unprotected spring", 8: "River, stream, pond or canal",
              9: "Tanker truck or cart with drum"},
    # NITI Aayog's cooking-fuel indicator is a LIST OF DIRTY FUELS -- "a household cooks with dung,
    # agricultural crops, shrubs, wood, charcoal or coal" -- not "LPG or not". The old binary
    # misclassified electricity and biogas users, who cook clean, as deprived.
    "fuel": {1: "LPG or cylinder gas", 2: "Piped natural gas", 3: "Electricity",
             4: "Biogas (gobar gas plant)", 5: "Kerosene", 6: "Firewood", 7: "Dung cakes (gobar)",
             8: "Crop residue, straw or shrubs", 9: "Charcoal", 10: "Coal or lignite"},
    # adminlevel (village / town / city) was dropped 2026-09-28. It asked the respondent to perform an
    # administrative classification that is a Census status, not a folk category: whether a place is a
    # statutory town, a census town or a village is not something a resident knows, so two people from
    # the same place answered differently and the variable's variance was mostly self-presentation. It
    # was also selecting the poverty line -- Rs 2,515 against Rs 3,639, a 45% swing -- off a subjective
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
    # respondent -- and it fixes the mid-month season boundary, because the boundary is now wherever
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
    # One Nation One Ration Card portability -- the closest real analogue to the legal-residency
    # indicator in Lyons et al.: an internal migrant whose entitlement works only at his home place is
    # outside the food safety net for the half of the year he is actually earning.
    "portable": {1: "Yes, can draw it here", 2: "No, only at the home place",
                 3: "Has never tried", 4: "We have no ration card", 97: "Does not know"},
    "month": {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July",
              8: "August", 9: "September", 10: "October", 11: "November", 12: "December"},
    # Named schemes, not "any government scheme". A category prompt makes the respondent recall a
    # class ("did you get a benefit?") and people reliably fail at that; a named list is recognition,
    # not recall. The levels also differ -- ration is per household, pensions are per person, MGNREGA
    # is a job card, PM-KISAN follows the landholding -- which is why this is a check-all rather than
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
    # happened -- a household with no shock in twelve months had nothing it could legitimately tick,
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
    # names -- the real ones are ANM and LHV -- and an ASHA or Anganwadi worker, who very often does
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
    # left_here_month / returned_here_month spell, and code 5 is spent on construction -- the commonest
    # off-season destination occupation for this workforce, which previously had nowhere to go.
    # Code 1 covers preparing for the season as well as working it. Without that, a lodge owner
    # repairing rooms in March, a pony owner feeding animals through February, a shopkeeper buying
    # stock in April had no true option and would land on 8 (no paid work) -- which is wrong, and wrong
    # in a way that reads as idleness. Consequence: yatra_months now counts preparation months too, so
    # it is months of Yatra LIVELIHOOD rather than months of Yatra earnings. The consumption season
    # weight does not use it (that is months_here, from the absence spell), and the data-quality band
    # on yatra_months was widened from 3-6 to 3-9 to match.
    "activity": {1: "Yatra work, or getting ready for the season", 2: "Farming (crops)", 3: "Livestock (animals)",
                 4: "Casual or daily wage labour", 5: "Construction work",
                 6: "Own small shop, stall or trade", 7: "Salaried job", 8: "No paid work"},
    "yndk": {0: "No", 1: "Yes", 97: "Don't know"},
    # Apablaza Appendix 2 Q5, all eleven categories, in their order -- the routing differs by code
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
    "pension": {1: "Yes, employer deducts it", 2: "Yes, contributes voluntarily", 3: "No"},
    "workins": {1: "Yes, through work", 2: "Only private or other insurance", 3: "None", 4: "Don't know"},
    "movetype": {1: "Lateral (little retraining needed)", 2: "Upskilling (destination needs skills the worker lacks)",
                 3: "Reskilling (skill sets barely overlap)", 4: "Downskilling (worker's skills would go unused)"},
}

SRC_STD = "Standard household-survey item"
ROWS = []

def R(module, name, label, question, desc, kind, lset=None, skip="", source=SRC_STD, origin="asked", formula=""):
    assert len(label) <= 80, (name, len(label))
    ROWS.append(dict(module=module, name=name, label=label, question=question, desc=desc, kind=kind, lset=lset,
                     skip=skip, source=source, origin=origin, formula=formula))

# ------------------------------------------------------------------ P  cover and paradata
R("P", "resp_id", "Respondent ID", "Assigned by the tablet.", "Unique respondent number.", "id", origin="paradata", source="Design")
R("P", "enum_id", "Enumerator", "Which enumerator is doing this interview? (Select your own name before you approach anyone.)", "Which of the four enumerators did the interview. Asked as the FIRST question on the form, ahead of consent, so it is recorded even when consent is refused -- a refusal is data, and which enumerator collected it is part of that data. Kept alongside Kobo's own `_submitted_by` rather than replaced by it: `_submitted_by` only separates the four if every enumerator has their own login and always uses it, while this item also works under a shared login. Where they disagree (wrong name tapped, or a device signed in as someone else) that is a data-quality flag neither could raise alone -- check it on the real export.", "cat", "enum", origin="paradata", source="Design")
R("P", "site", "Pilgrimage route being surveyed", "Which route is this interview on?", "Set by the enumerator before approaching anyone, alongside enum_id and ahead of consent, so it is recorded even when consent is refused. The study covers two routes now; GPS fixes the position within a route, so this one question is all that is needed to separate them. Enters the analysis as a stratifier and a fixed effect -- the two routes differ in season length, altitude, employer mix, and in whether the ropeway proposal applies at all.", "cat", "site", origin="paradata", source="Project design (two-route stratification)")
R("P", "form_build", "Build stamp of the form that produced this record", "Recorded automatically.", "Which build of the form collected this interview: the date plus a short hash of the question set. A service worker can serve a stale copy of the page indefinitely, and a stale build is indistinguishable from the current one once it is on a tablet -- three issues in one field review had already been fixed and the reviewer had no way to know. Stamped into every exported row so a report can be matched to a build.", "text", origin="paradata", source="Project design (build provenance)")
R("P", "interview_date", "Interview date", "Recorded automatically.", "Date of interview.", "date", origin="paradata", source="Design")
# location_cluster dropped 2026-09-24: it asked the enumerator to hand-code the interview site into
# one of four route clusters, which the silently captured GPS below already records more precisely.
# health_access_tier is now derived from gps_lat in Stata. Net effect: one fewer action per interview,
# a continuous rather than categorical location input, and no named site in the exported data either way.
R("P", "gps_lat", "GPS latitude of interview", "Recorded automatically.", "Latitude of the interview location.", "num", origin="paradata", source="Design")
R("P", "gps_lon", "GPS longitude of interview", "Recorded automatically.", "Longitude of the interview location.", "num", origin="paradata", source="Design")
R("P", "consent", "Respondent gave informed consent", "Do you agree to take part?", "Consent given after the script was read.", "bin", "yn", origin="paradata", source="Design")
R("P", "interview_duration_min", "Interview length (minutes)", "Recorded automatically (start to end).", "Total interview time; the target is 45 minutes or less.", "num", origin="paradata", source="Design")
R("P", "dur_tasks_min", "Time spent on tasks block L (minutes)", "Recorded automatically (module timestamps).", "Time for the short task and papers block; tracks the burden of the transferability add-on.", "num", origin="paradata", source="Design")

# ------------------------------------------------------------------ A  respondent and household
R("A", "age", "Age in completed years", "How old are you? (completed years)", "Respondent age; 18 to 70 covered.", "num", source="Standard; sensitivity covariate in the VEP model (Azeem et al. 2016 structure)")
R("A", "female", "Female (1) or male (0)", "Record sex; ask if unsure: are you male or female?", "Sex of the respondent.", "bin", "sex")
R("A", "hoh_relation", "Respondent's relationship to the head of household", "Who is the head of your household -- is it you, or someone else? If someone else, how are they related to you?", "Who the head of household is, relative to the respondent. The categories are GENDERED (husband/wife, son/daughter, father/mother, brother/sister), so the head's sex falls out of this answer and no separate male/female question is asked -- one question instead of two, and it matches how people actually answer: nobody says 'my parent', they say 'my father'. Hindi kinship terms are gendered too, so the Hindi wording needs no adjustment. Asked openly and coded from the answer, not read off a list.", "cat", "hohrel")
R("A", "native_language", "Native language / mother tongue", "What is your native language, the language you first learned at home?",
  "Mother tongue, used in place of a caste/social-group question: caste is sensitive to ask directly and does not classify non-Indian migrants (Nepali workers) in any comparable way. Language instead captures regional origin, which correlates with the class variation caste would have picked up, and applies to every respondent.",
  "cat", "nativelang", source="Project design (language proxy for regional/socioeconomic origin; avoids a sensitive caste question and covers out-of-country migrants)")
R("A", "native_language_other", "Native language, written in (not on the list)", "Which language is it? Write down exactly what they say.", "Free-text catch-all for the two 'other' codes. IMPORTANT ITEM: this is the only proxy the instrument has for regional and social origin -- it replaced the caste question -- so an answer left as bare 'other' loses that information for that respondent. The list is long but India is longer; enumerators must type the actual language rather than settle for the catch-all code.", "text", skip="Ask only if native_language is 96 (other Indian language) or 97 (other / foreign language)", source="Project design (the language item stands in for caste; an uncoded 'other' is a real loss)")
R("A", "marital_status", "Marital status", "Are you currently married, never married, or widowed/divorced/separated?", "Marital status of the respondent.", "cat", "marital")
R("A", "knows_years_schooling", "Knows exact years of schooling completed", "Do you know exactly how many years of schooling you completed, counting from class 1?", "Gates whether years_schooling or the fallback bracket (education_level_cat) is asked. Minimises categorical questions: a direct year count is asked first, and only respondents who cannot recall get a category.", "bin", "yn")
R("A", "years_schooling", "Years of schooling completed", "How many years of schooling did you complete in total? (0 if none)", "Direct year count; feeds the MPI education indicator. Preferred over a level/category, which loses information a plain number does not.", "count", skip="Ask only if knows_years_schooling = 1", source="NITI Aayog National MPI (years of schooling); Chaudhuri et al. 2002 covariate")
R("A", "education_level_cat", "Highest level of school completed (bracket, if years not recalled)", "Which is closest: no formal education; some schooling but did not finish primary; finished primary but not secondary; or finished secondary or higher?", "Fallback bracket, asked only when the respondent cannot give an exact year count. Kept to four categories (plus prefer-not-to-say) to minimise categoricals.", "cat", "edu2", skip="Ask only if knows_years_schooling = 0", source="NITI Aayog National MPI (years of schooling); Chaudhuri et al. 2002 covariate")
R("A", "hhsize", "Household size (number of members)", "How many members live in your household, including you?", "Household size in the usual place of living. Aggregate count; no household roster.", "count", source="Chaudhuri et al. 2002; used to get per-capita consumption")
R("A", "any_member_6yr_schooling", "Any household member aged 10+ has completed 6 years of schooling", "Counting everyone in your household aged 10 or above, has at least one of them finished six years of schooling or more?", "NITI's Years of Schooling indicator is defined on the HOUSEHOLD -- 'not even one member aged 10 years or older has completed six years of schooling' -- not on the respondent. Using the respondent's own education_years in its place, as this instrument previously did, measures a different thing and is not comparable to any published National MPI figure. NOT ASKED where the respondent's own schooling already settles it: the respondent is himself a member aged 10 or over, so six years or more of his own is a Yes by entailment and Stata fills it. The bracket route can only settle it at 'completed secondary or higher' -- 'completed primary but not secondary' spans 5 to 9 years and straddles the threshold, so it does not, and the question is asked.", "bin", "yn", skip="Ask only if the respondent's own schooling does not already settle it: years_schooling < 6, or the bracket is not 'completed secondary or higher'", source="NITI Aayog National MPI, Years of Schooling (weight 1/6)")
R("A", "family_structure", "Family structure: nuclear, joint or single-member", "Is your family nuclear -- just you, your spouse and unmarried children -- or joint, living with parents, married siblings or other extended family? (Say single-member if you live alone.)", "Household composition type.", "cat", "famstruct", source="Standard household-survey item")
R("A", "n_earners", "Number of household members who earn money", "How many of them, including you, earn money?", "Earners in the household, including the respondent.", "count", source="Dependency measure used in VEP studies (Azeem et al. 2016)")
R("A", "main_income_earner", "Respondent is the main income earner in the household", "Among those who earn money, are you the main income earner in your household?", "Whether the respondent is the household's main earner.", "bin", "yn", skip="Ask only if n_earners > 1 (if the respondent is the only earner, this is automatic)", source="Apablaza et al. 2026, Appendix 2 Q4 (adapted to a single-respondent report: 'who is the main contributor' becomes 'are you the main contributor')")
# Split at 6 and 14, not at 15 and 6-14. The old pair asked "how many under 15" and then "how many
# aged 6 to 14", which is the same children counted twice with the under-6s left implicit -- the
# respondent has to subtract to answer the second, and the two can contradict each other (a dq flag
# existed purely to catch that). Two disjoint bands instead: under-6 and 6-to-14 partition the
# under-15s exactly, so n_children_u15 is now CONSTRUCTED as their sum and the adult-equivalent
# scale is unchanged. The under-6 band is also the age range NITI's Nutrition indicator is defined
# on (children 0-59 months), so it is the denominator for the nutrition discussion rather than a
# number nothing uses.
R("A", "n_children_u6", "Household children under 6", "How many of them are children under 6 years old?", "Count of children under 6. With n_children_6_14 this partitions the under-15s into two disjoint bands, so neither question asks the respondent to subtract one from the other. Also the age band NITI's Nutrition indicator covers (0-59 months), which is why the band is drawn at 6 rather than 5.", "count", source="Adult-equivalent scales (Claro et al. 2010; Awuni et al. 2023); NITI Aayog National MPI nutrition age range")
R("A", "n_children_6_14", "Household children aged 6 to 14", "And how many are aged 6 to 14?", "Count of school-age children. Disjoint from n_children_u6 above, so the two add to the under-15 count rather than overlapping it.", "count", source="NITI Aayog National MPI school-attendance indicator")
R("A", "n_children_out_school", "Children aged 6 to 14 not attending school", "How many of these children do not go to school now?", "Count of school-age children not attending.", "count", skip="Ask only if n_children_6_14 > 0", source="NITI Aayog National MPI school-attendance indicator")

# ------------------------------------------------------------------ B  work, season, history
R("B", "occupation", "Main work in the Yatra season (14 groups)", "What is your main work during the Yatra season? Ask what they do and code the closest group; do not read the list aloud unless needed.", "Quota variable: 14 occupation groups, rebuilt against NCO-2015 (see the occ list). Deliberately a COARSE grouping -- it exists to manage sampling quotas and to be stable across the fieldwork, not to describe the job. The precise occupation is captured verbatim in occupation_detail below and coded to NCO afterwards, so nothing is lost by this list being broad.", "cat", "occ", source="Project quota design, mapped to NCO-2015 families")
R("B", "occupation_detail", "Main work, in the respondent's own words (NCO-coded later)", "In your own words, what exactly is your main work here? Write down what they say -- what they actually do, and who for. Do not tick a box for this one.", "Verbatim description of the primary livelihood, office-coded to NCO-2015. IMPORTANT ITEM: the 14 groups above are deliberately coarse, so this is the ONLY place the real occupation is recorded, and it is what the task-distance and structural-displacement analysis is coded from. 'Shop owner' could be a man selling prasad from a plank or a family running a three-storey general store; only this field tells them apart. Same treatment as prev_occ and target_occ, so all three code into one classification.", "text", source="Project design (coarse quota group + verbatim detail, coded to NCO-2015 in the office)")
R("B", "employment_type", "Employment status in main work (4 groups)", "In this main work, are you: working on your own account without hired workers; running a business with hired workers; a regular monthly wage-earner; or a daily/casual wage-earner?", "PLFS-style status: own-account, employer, regular wage, casual wage.", "cat", "emptype", source="PLFS / NSS employment status classification [source not held by this project; citation unverified as of 2026-09-28]")
MULTIWORK = ("Multiple work-holding, asked as a count first and then as a check-all list. The previous "
             "version allowed ONE other activity, which undercounts by construction: a shop owner who "
             "also rents out a pony and drives in the off-season has three, and only one was recorded. "
             "The count is asked before the list so it can be checked against the number of boxes "
             "ticked -- a mismatch is a data-quality flag, not a silent loss.")
R("B", "n_other_activities", "Number of other paid activities besides the main Yatra work", "Besides your main work, how many OTHER paid activities or income-generating activities do you have? (0 if none. For example, a shop owner who also rents out a pony and drives in the off-season would say 2.)", "Count of additional income-generating activities. " + MULTIWORK, "count", source="Project design (multiple job-holding, common in the Yatra economy)")
R("B", "other_activity_types", "Which other paid activities (check all that apply)", "Which ones are they? Check every one that applies. Ask and code the closest group for each; do not read the list aloud unless needed.", "Check-all list of the other activities. " + MULTIWORK + " Exported by Kobo as a space-separated string plus one binary column per choice; Stata splits it into other_act_1 to other_act_13.", "multi", "occ", skip="Ask only if n_other_activities > 0", source="Project design (multiple job-holding, common in the Yatra economy)")
R("B", "other_activity_income_pm", "Usual monthly income from all other paid activities (Rs)", "Taking all of that other work together, about how much do you usually earn from it in a month? (Rs)", "Combined monthly income from all the other activities. Asked as one combined figure rather than per activity: per-activity amounts would multiply the question count for a quantity that enters the analysis only as a total.", "money", skip="Ask only if n_other_activities > 0", source="Project design (multiple job-holding)")
R("B", "years_in_yatra_work", "Years worked in Yatra work", "How many Yatra seasons have you worked in this kind of work?", "Experience in the Yatra economy.", "count", source="Chaudhuri et al. 2002 sensitivity covariate; Apablaza et al. 2026 Q10 (tenure in this job)")
R("B", "hours_day_yatra", "Hours worked per day in the Yatra season", "In the Yatra season, on a normal working day, how many hours do you work in total, across all your work?", "Usual daily hours, all jobs. Asked as hours/day and days/week separately (not as one 'hours a week' figure) and multiplied in Stata: a normal day is easier to picture than a whole week at once.", "count", source="Apablaza et al. 2026 Q13 (decomposed into hours/day x days/week rather than asked as one weekly figure, for ease of recall)")
R("B", "days_week_yatra", "Days worked per week in the Yatra season", "How many days a week do you usually work in the season?", "Usual working days per week.", "count", source="Apablaza et al. 2026 Q13 (decomposed into hours/day x days/week rather than asked as one weekly figure, for ease of recall)")
OFFH = ("Apablaza's access-deprivation test has an under-20-hours-a-week limb, but asking hours only "
        "for the Yatra season made that limb unfireable: in season this workforce runs 60-90 hours a "
        "week, so nobody ever cleared it and the whole indicator collapsed onto the months-without-work "
        "limb. Off-season hours are where marginal, part-week work actually shows up for a seasonal "
        "workforce.")
R("B", "prev_occ_change", "Changed main kind of work in the last 10 years", "In the last ten years, did you change your main kind of work?", "Occupational change flag.", "bin", "yn", source="Occupational mobility check; job-history item")
NCONOTE = ("Recorded as free text in the respondent's own words, NOT coded to a list in the field. The "
           "13-group Yatra occupation list cannot hold work done outside this economy -- farming in Bihar, "
           "driving in Dehradun -- and those are exactly the moves the analysis needs to see. Office-coded "
           "to NCO-2015 afterwards, which also puts these answers in the same classification as the "
           "regional employment weights. Enumerator writes what the respondent says, including the "
           "industry if given (e.g. 'drove a tempo for a hotel', not just 'driver').")
R("B", "prev_occ", "Previous main work (verbatim, NCO-coded later)", "What was your previous main work? Write down exactly what they say, in their words -- do not pick from a list.", "Occupation before the change. " + NCONOTE + " Gives the observed occupational moves that validate the task-distance measure against the random-mobility benchmark.", "text", skip="Ask only if prev_occ_change = 1", source="Gathmann and Schonberg 2010 (observed moves are systematically shorter than random moves -- the validation test for a task-distance measure); coded to NCO-2015 in the office")
R("B", "target_occ", "Work the respondent would move to if this work ended (verbatim, NCO-coded later)", "If you could not continue this work at all, what work would you move to instead? Write down exactly what they say, in their words -- do not pick from a list, and do not prompt with examples.", "Stated destination occupation. " + NCONOTE + " Two uses: it is the respondent's own target, which no external classification can supply; and comparing it with the task-nearest feasible destination gives an aspiration-versus-capability gap that the occupational-commonality literature has no worker-stated benchmark for. 'Don't know' and 'nothing / I would have no work' are both substantive answers -- record them as said.", "text", source="Project design (stated destination, for the structural-displacement analysis); coded to NCO-2015 in the office")
R("B", "prev_occ_reason", "Main reason for changing work", "What was the main reason you changed?", "Reason for the last change.", "cat", "prevreason", skip="Ask only if prev_occ_change = 1", source="Job-history item")
R("B", "training_received", "Ever completed a training course or apprenticeship", "Apart from school and college, have you ever completed any training course or apprenticeship?", "Vocational or on-the-job training, explicitly EXCLUDING school AND college. The old wording said only \"not counting school\", which left it ambiguous whether a degree counted -- some respondents would have reported a BA here. Formal education is already measured in years by years_schooling (a graduate reports about 15), so counting it again here would double-count it.", "bin", "yn", source="STEP module 2; Chaudhuri et al. 2002 adaptive-capacity covariate")

# ------------------------------------------------------------------ C  income and remittances
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
# Presentation order, NOT variable order. status_m1 is still January and every downstream month
# calculation is unchanged -- what moves is the sequence the enumerator is walked through. The
# calendar used to open on January and then instruct "fill the Yatra months first, then the others",
# which is an instruction the form cannot obey: it shows one question per screen in dictionary order.
# Opening at the season instead makes the instruction unnecessary, because the order IS the
# instruction, and it starts recall at the months the respondent remembers best. May is the opening:
# the Yatra runs from Akshaya Tritiya to Bhai Dooj, so late April or May through November.
CAL_ORDER = [5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4]
for _i in CAL_ORDER:
    _mo = MONTHS[_i - 1]
    R("C", f"status_m{_i}", f"Main activity in {_mo}",
      f"In {_mo}, what was your main work or activity?",
      f"Main activity in {_mo} of the past year; code 1 is the Yatra work named in B1. Asked in "
      f"season-first order (May through April), not January first.", "cat", "activity",
      source="Monthly work calendar; seasonality of consumption and poverty per Dercon and Krishnan 2000 (their design is a three-round panel, not a monthly recall calendar -- the calendar format is project design)")

R("C", "knows_monthly_income", "Can recall earnings month by month", "Can you tell me roughly what you earned in each month of the past year, or would it be easier to give one total for the whole year?", "Gate: routes to the twelve monthly figures or to the annual-total fallback below. LEFT BLANK IF THE RESPONDENT DECLINES TO DISCUSS EARNINGS AT ALL: both routes then stay shut and the interview continues. Earnings are a control in the vulnerability models, not an identifying variable, so refusing them costs a covariate rather than the case -- and a required earnings question would have ended interviews. Worded as a genuine choice between two ways of answering, not as a test the respondent can fail -- and ANSWERED as a choice too: it was previously a yes/no, so the options read \"No / Yes\" against a question asking which of two things is easier.", "cat", "recall", skip="Ask everyone; may be left blank if the respondent declines to discuss earnings, and both earnings routes then stay shut", source="Apablaza et al. 2026 Q14/Q15 (the 'does not know' route out of monthly earnings)")
# Same season-first order as the activity row above. They ran May-April and January-December
# respectively, so the enumerator met the two halves of one calendar in different orders.
for _i in CAL_ORDER:
    _mo = MONTHS[_i - 1]
    R("C", f"income_m{_i}", f"Earnings in {_mo} (Rs)", f"How much did you earn from all your work in {_mo}, after costs? (Rs)",
      f"Net earnings in {_mo}. Filled by the tablet as 0 when status_m{_i} is No paid work.", "money",
      skip=f"Ask only if knows_monthly_income = 1; automatic 0 if status_m{_i} = 8 (no paid work); may be left blank",
      source="Apablaza et al. 2026 Q14 (monthly earnings), asked month by month to avoid heaping on one typical figure")
R("C", "income_annual_total", "Total earnings from all work in the past year (Rs)", "Thinking of the whole past year, about how much did you earn in total from all your work, after costs? (Rs)", "Annual total, asked only of respondents who could not give month-by-month figures. Combined with pct_income_yatra and the work calendar to rebuild monthly earnings in Stata.", "money", skip="Ask only if knows_monthly_income = 0; may be left blank", source="Apablaza et al. 2026 Q15 (fallback when monthly earnings are not known), adapted to an annual total for a seasonal workforce")
R("C", "pct_income_yatra", "Share of the year's earnings that came from Yatra work (out of 100)", "Out of every 100 rupees you earned in the whole year, how many came from your Yatra work? (The rest is counted as coming from your other work.)", "Yatra / non-Yatra split of the annual total, used to reweight it onto the calendar. Asked as 'out of every 100 rupees' rather than as a percentage: the same number, in a form that does not ask the respondent to hold an abstract percentage scale. This is a quantity being divided, not a rating scale.", "count", skip="Ask only if knows_monthly_income = 0; may be left blank", source="Project design (the Yatra / non-Yatra split needed to reweight an annual total onto the work calendar)")
SEAS = ("Most workers here are migrants, so a single recent-recall figure would describe only the season in which the interview happens to fall. Asked as a usual monthly amount for each of the two seasons instead, matched to the Yatra-season/off-season split already used for the work calendar.")
R("C", "remit_out_yatra_pm", "Money usually sent home in a month, Yatra season (Rs)", "In a normal month during the Yatra season, how much money do you usually send to family or others living elsewhere? (Rs, 0 if none)", "Outward remittances, Yatra-season month. " + SEAS, "money", source="Project design (amount only; frequency dropped for length). A previous citation to NSS 64th Round practice was withdrawn 2026-09-28: no NSS schedule is held by this project and it could not be checked")
R("C", "remit_out_offseason_pm", "Money usually sent home in a month, off-season (Rs)", "In a normal month when the Yatra is closed, how much do you usually send? (Rs, 0 if none)", "Outward remittances, off-season month. " + SEAS, "money", source="Project design (amount only; frequency dropped for length). A previous citation to NSS 64th Round practice was withdrawn 2026-09-28: no NSS schedule is held by this project and it could not be checked")
R("C", "remit_mode", "How money is usually sent home", "How do you usually send it?", "Channel, not just amount. Bank and UPI transfers are near-costless and traceable; money orders and hand-carrying cost a fee, a trip, or both, and hand-carrying ties the transfer to someone physically travelling. Two households sending the same rupees are not equally well served.", "cat", "remitmode", skip="Ask only if remit_out_yatra_pm > 0 or remit_out_offseason_pm > 0", source="Project design (remittance channel as a financial-inclusion and cost measure)")
R("C", "remit_in_yatra_pm", "Money usually received in a month, Yatra season (Rs)", "In a normal month during the Yatra season, how much money do you usually receive from family or others? (Rs, 0 if none)", "Inward remittances, Yatra-season month. " + SEAS, "money", source="Project design (amount only; frequency dropped for length). A previous citation to NSS 64th Round practice was withdrawn 2026-09-28: no NSS schedule is held by this project and it could not be checked")
R("C", "remit_in_offseason_pm", "Money usually received in a month, off-season (Rs)", "In a normal month when the Yatra is closed, how much do you usually receive? (Rs, 0 if none)", "Inward remittances, off-season month. " + SEAS, "money", source="Project design (amount only; frequency dropped for length). A previous citation to NSS 64th Round practice was withdrawn 2026-09-28: no NSS schedule is held by this project and it could not be checked")
# NOTE the module: these are hours questions and belong with the others in B, but they are gated
# on the work calendar, which is asked HERE in C. A question placed before its own gate can
# never be shown -- so they live where the gate is answered, not where they read best.
R("C", "hours_day_offseason", "Hours worked per day outside the Yatra season", "In the months when the Yatra is closed and you are doing other work, on a normal working day, how many hours do you work in total?", OFFH, "count", skip="Ask only if any month in the calendar is other paid work (status 2 to 7)", source="Apablaza et al. 2026 Q13, asked a second time for the off-season (decomposed as hours/day x days/week, as in the Yatra-season pair)")
R("C", "days_week_offseason", "Days worked per week outside the Yatra season", "In those months, how many days a week do you usually work?", OFFH, "count", skip="Ask only if any month in the calendar is other paid work (status 2 to 7)", source="Apablaza et al. 2026 Q13, asked a second time for the off-season")

# ------------------------------------------------------------------ D  migration
R("D", "origin", "Place of permanent home", "Where is your permanent home?", "Origin of the respondent, as four buckets. Note what it does NOT measure: the pilot found 11 of 20 seasonal movers inside this same district, so this is a distance variable, not a mobility one. closure_base and the Module C location row carry mobility.", "cat", "origin", source="Project design (distance bucket); NOT an NSS classification -- the earlier citation to one was withdrawn 2026-09-28, no NSS schedule is held by this project")
R("D", "home_state", "State or union territory of the permanent home", "Which state is your permanent home in?", "State/UT of the permanent home, asked ONLY when the origin is another Indian state. The other three origin codes already give the answer: local and other-Uttarakhand-district are both Uttarakhand, and Nepal is Nepal. Asking it of everyone meant a respondent from the next valley was asked which state he lived in, and a Nepali worker had to hunt for an outside-India code in a 37-item list one question after saying Nepal. Stata fills the three known cases. The state is the level at which India sets its rural and urban poverty lines, which is why it is asked at all.", "cat", "state", skip="Ask only if origin = 3 (another Indian state)", source="Standard state/UT classification; needed to apply the right poverty line per respondent")
R("D", "home_rural_urban", "Usual home is in a village (1) or a town/city (2)", "Is that home in a village, or in a town or city?", "Rural/urban status of the permanent home, asked directly as the binary the poverty line actually needs. Replaces home_admin_level, a three-way village/town/city item that asked the respondent to perform a Census classification they have no way of making, and then selected a Rs 2,515 or Rs 3,639 line off the answer. Also stops being a constructed variable: it was derived from home_admin_level, which meant a 45% swing in the threshold rested on a derivation from a subjective tier.", "cat", "ruralurban", source="Rural and urban poverty lines (Sethu et al. 2024)")

# ---- what happens at closure -----------------------------------------------------------------
# NOT gated on origin. The gate this block originally carried -- "ask only if origin is not Local" --
# was wrong in the direction that destroyed the module: 11 of the 20 seasonal migrants in the pilot
# were from this same district (pilot/livelihood_clean.dta, residency_pattern x local), so gating on
# non-local would have skipped most of the people who actually move. Seasonal movement here is mostly
# LOCAL movement, up-valley for the season and down-valley at closure, and a migrant dummy built on
# district boundaries measures almost none of it.
# closure_base was one question doing two jobs. Its stem -- "do you and your household stay here, or
# go to your home place?" -- named two subjects in a single breath and offered a binary while the
# options were four, so a respondent had to parse a compound before answering. Split into the two
# facts it was compressing. The same four cells come out, in Stata, from two plain yes/no answers.
R("D", "resp_returns_at_closure", "Respondent goes to the home place when the Yatra closes", "When the Yatra closes for the season, do YOU go to your home place?", "Whether the RESPONDENT moves. This is the assumption the whole two-season design rests on: every consumption, remittance and coping item in Modules C, E and I is asked twice on the premise that he is somewhere else once the Yatra shuts. The pilot suggests it is false for a large minority -- 23 of 46 respondents lived here year-round.", "bin", "yn", source="Project design; categories from the pilot's own residency_pattern distribution (n=46)")
R("D", "hh_at_home_place", "The rest of the household lives at the home place year-round", "And do the rest of your household live at your home place all year, or are they here with you during the season?", "Whether the HOUSEHOLD is split. Module E's Yatra-season wording (\"you and anyone staying with you here\") is written for exactly the split case and until now had nothing to key off; the pilot found 3 of 46 working here with family elsewhere. Also fixes a real error in the consumption aggregate -- see n_here_season.", "bin", "yn", source="Project design (split-household measurement, underpinning Module E)")
R("D", "n_here_season", "People the respondent's on-site spending covers during the season", "During the Yatra season, how many people are you feeding and spending on here, counting yourself?", "The denominator the Yatra-season consumption figures actually belong to. Until this existed, per-capita consumption divided an on-site figure covering \"you and anyone staying with you here\" by the FULL household size, so a man supporting himself here for six months while his family of five lived at the home place was recorded at a fifth of his real per-capita consumption and pushed below the poverty line by arithmetic. Asked only of split households, because for everyone else it is hhsize.", "count", skip="Ask only if hh_at_home_place = 1", source="Project design (season-specific denominator for per-capita consumption)")
R("D", "years_coming_here", "Years the respondent has been coming here for the season", "How many years have you been coming here for the Yatra season?", "Duration of the relationship with this worksite, which years_in_yatra_work does not give: that counts seasons in the CURRENT kind of work, so a porter who spent six years portering and then four running a stall reads as four. A first-year worker has neither the network nor the savings of a fifteen-year one, and that is an exposure term the VEP model wants.", "count", skip="Ask only if resp_returns_at_closure = 1", source="Project design (duration of the seasonal relationship)")
R("D", "came_here_reason", "Main reason for first coming here to work", "What was the main reason you first came here to work?", "Push or pull, kept separate from prev_occ_reason, which is about changing WORK -- the old combined item gave a migrant who took a new job on arrival two true answers. Someone driven here by debt or by land too small to live on is in a different position from someone drawn by better pay, at identical current earnings.", "cat", "comereason", skip="Ask only if origin is not Local (same district)", source="Project design (push/pull as a vulnerability covariate)")

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
# asked in this module. They sat in Module C at first and 06_form_fill_check.py caught it -- a gate
# that is answered AFTER the question it controls can never open, so all three were unreachable.
# ---- where the respondent was living, as a spell rather than twelve questions ------------------
# This replaces loc_m1..loc_m12. The job is the same -- stop the instrument assuming its own key
# fact, that people are somewhere else once the Yatra shuts -- but twelve select_ones to establish
# what is almost always a single contiguous absence was a sixth of the interview for one variable.
# Asked as the spell instead: the month they left and the month they came back. months_here,
# months_home_base and months_third_place are all still derived, in Stata, from these three items.
R("D", "left_here_month", "Month the respondent last left the Yatra route", "In the past year, which month did you last leave here and go to your home place?", "Start of the absence. Together with returned_here_month this gives the months spent at the home place, and by subtraction the months spent here -- which is the measured season length, and therefore also the answer to the mid-month season-boundary problem: each respondent's boundary is their own reported month, not a constant we impose.", "cat", "month", skip="Ask only if resp_returns_at_closure = 1", source="Project design (measured seasonal base, asked as a spell)")
R("D", "returned_here_month", "Month the respondent came back to the Yatra route", "And which month did you come back here?", "End of the absence. A returned month EARLIER in the calendar than the left month is the normal case, not an error -- the absence straddles the new year, because the Yatra closes in November and reopens in April or May.", "cat", "month", skip="Ask only if resp_returns_at_closure = 1", source="Project design (measured seasonal base, asked as a spell)")
# Dropped 2026-10-01, three questions, each traced to its consumers before it went:
#   months_away_for_work  the INTENSIVE margin of off-season migration, in months. Nothing
#         regressed on it. It built months_third_place and months_home_base, which appear in no
#         covariate vector and in no deprivation indicator -- the mobility term the VEP models
#         actually use is closure_labour_migrant, and that is built from the yes/no above, not from
#         the months. months_here, the season weight on consumption and income, comes from the
#         absence SPELL (left_here_month, returned_here_month) and is untouched. The proposed
#         replacement -- "is your usual residence different from your hometown" -- was NOT added:
#         origin, resp_returns_at_closure and hh_at_home_place already answer it between them.
#   worked_other_places   prior mobility over the whole working life. It was in the VEP adaptive-
#   other_places_detail   capacity vector and nowhere else, and it is the weakest member of it:
#         "have you ever worked elsewhere" over a lifetime is answered Yes by most of this sample
#         (22 of 45 in the pilot had changed occupation at all), so it carries little variance, and
#         prev_occ plus target_occ already give the occupational-mobility history the
#         transferability analysis reads. Removed from X_adapt rather than kept for completeness.
R("D", "would_move_for_work", "Would go away for work in the coming year if this ended", "If this work here ended, would you go away from your home place to look for work in the coming year?", "Stated mobility, which is the constraint the task-distance measure cannot see: a worker whose skills fit a destination perfectly but who will not leave is structurally displaced just the same. Pairs with target_occ -- that asks WHAT they would do, this asks whether they would move to do it -- and is read against worked_away_in_closure, the revealed version. Given a concrete horizon (\"in the coming year\") rather than left as an open hypothetical, following the VASyR 2025 practice of horizoning intention items; an unbounded \"would you ever\" is answered on disposition rather than on circumstance.", "cat", "yndk", source="Project design; horizoned intention item after VASyR 2025 (move_accom_yesno, asked over a stated 6-month horizon)")
R("D", "migration_referral", "Who arranged or helped get this work", "Who mainly helped you get this work, or arranged it for you?", "The old list mixed two different things -- who TOLD you about the work and who EMPLOYS or places you -- and put a thekedar and an agent in one box although they are different relationships: a thekedar is who you work for, an agent is a middleman who places you and is usually paid for it. Splitting them is the point: an agent-placed worker has a debt or fee relationship an informally referred worker does not. \"Political or community leader\" is dropped; it was an analyst's category, not one a respondent would recognise as describing how they got their job. Ungated as of 2026-09-28: it used to be asked only of non-local respondents, but who placed you is a question about the employment relationship, not about migration -- a local worker placed by an agent carries the same fee or debt relationship a Nepali one does, and gating it on a district boundary meant we could never see that.", "cat", "referral", source="Project design (referral channel as a proxy for social capital and for placement debt)")
R("D", "migration_referral_other", "Who helped, if not on the list (verbatim, optional)", "Who was it? Write what they say.", "Free text, NOT required, for referral channels the seven codes do not hold. The item is a proxy for social and political capital in getting access to work here, so a channel we failed to anticipate is exactly the one worth recording.", "text", skip="Ask only if migration_referral = 7 (Other); may be left blank")
# years_since_migration was dropped: redundant with years_in_yatra_work (Module B) for this study's
# purposes -- "how long have you been doing this work" is the more analytically useful duration, and
# asking both a migration-duration and a work-tenure figure was asking the same thing twice in most cases.

# ------------------------------------------------------------------ E  consumption
E_NOTE = "Report for the household's usual place of living, including home-produced items valued at market price."
HC = "HCES 2022-23, MoSPI Appendix A"  # https://www.mospi.gov.in/.../HCES-22-23/AppendixA.pdf
IH = "IHDS-II Income and Social Capital Questionnaire, Q14"  # ihds.umd.edu
GH = "Nigeria GHS-Panel Wave 3, Household Questionnaire, Sections 10B/11"
SEASE = ("Workers here are migrants: the on-site figure at the time of interview would not represent a whole year, and asking about the 'usual homeplace' alone would miss on-site spending during the Yatra season. So each item is asked as a usual monthly amount for each of the two seasons, matched to the Yatra-season/off-season split already used for the work calendar (Module B/C). This replaces a single-point 30-day or 7-day actual recall with two 'usual month' figures, following the usual/typical recall approach used where recall decay or seasonal change is the bigger concern (Beegle et al. 2012; Deaton and Grosh 2000).")
YSPLIT = ("During the Yatra season the household itself may be split (the respondent here, some family elsewhere, linked by the remittances already asked in Module C), so the Yatra-season question asks about spending by 'you and anyone staying with you here' -- what the respondent can actually observe -- rather than 'your household', which they may not fully know during the season when part of it is elsewhere. The off-season question keeps 'your household', since the family is assumed reunited at the usual home by then.")
def EP(name, label, item_text, note, src):
    R("E", name + "_yatra_pm", label + ", Yatra-season month (Rs)", "In a normal month during the Yatra season, how much do you (and anyone staying with you here) spend on " + item_text + "? (Rs)", note + " " + SEASE + " " + YSPLIT, "money", source=src)
    R("E", name + "_offseason_pm", label + ", off-season month (Rs)", "In a normal month when the Yatra is closed, how much does your household spend on " + item_text + "? (Rs)", note + " " + SEASE, "money", skip=SEASGATE, source=src)

SEASGATE = "Ask only if spend_differs_by_season = 1"
R("E", "spend_differs_by_season", "Household spending differs between the two seasons", "Leaving aside money you send home -- is what your household spends in a normal month during the Yatra season different from what it spends when the Yatra is closed?", "Gate for the off-season half of every seasonal pair. Where a household says spending is the same, the off-season figures are not asked and Stata copies the Yatra-season figure across, halving this module for those respondents. NOTE the risk this carries: a gate that saves nine questions is an invitation to answer \"same\", and the short branch is more attractive to a tired respondent and a hurrying enumerator. If a large share take it, check that share against the pilot before trusting the consumption aggregate -- an over-used gate would bias measured consumption toward the Yatra-season level, which is about a third higher.", "bin", "yn", source="Project design (respondent-gated seasonal recall); the underlying two-season design follows Beegle et al. 2012 and Deaton and Grosh 2000 on usual-period recall")
EP("cons_staples", "Cereals, pulses, sugar and salt", "cereals (rice, wheat, other grains), pulses, sugar and salt, bought or from your own stock",
   "Staple foods bought less often.", HC + ", Sections 5.1-5.3 (30-day); " + IH + " 14.1-14.6 (30-day, same items)")
EP("cons_perishables", "Milk, vegetables, fruit, meat, oil, spices, tea", "milk and milk products, vegetables, fruit, egg/fish/meat, cooking oil, spices, and tea or coffee, bought or from your own stock",
   "Perishables bought often.", HC + ", Sections 6.1-6.8 (7-day actual recall in HCES; asked here as a usual monthly figure instead, for the reason above)")
FOODOWN_NOTE = ("Non-purchased food, one aggregate figure (HCES/IHDS record the source per item, too long for this interview). Framed as 'if you had to buy it' rather than telling the respondent to value it 'at market price': that phrase assumes a precision (knowing the exact market worth of one's own produce) most respondents would not have; asking what it would have cost to buy is the same imputation, in a question an actual person can answer.")
R("E", "cons_food_own_yatra_pm", "Home-grown or gifted food, Yatra-season month (Rs)", "If you (and anyone staying with you here) had not grown, raised or been given any of your food, about how much would it have cost to buy in a normal month during the Yatra season? (Rs, 0 if you buy everything)", FOODOWN_NOTE + " " + SEASE + " " + YSPLIT, "money", source="Calvo and Dercon 2007; Eze and Iheonu 2025 (non-purchased food, aggregate approach)")
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

SITEMEALS = ("Worksite subsistence. The consumption module asks what the HOUSEHOLD usually spends, but during the season the respondent lives at the worksite, often apart from that household, and his own subsistence there has a different cost structure: paid lodging, bought meals, no home production. cons_rent catches the lodging; nothing caught the meals. SCOPE: this pair is PERSONAL, not household, spending. It is descriptive of the worksite economy and must NOT be added into cons_pc_pm -- the VEP welfare measure stays household consumption per capita, and adding this would double-count against cons_food_out.")
EP("cons_packaged_food", "Biscuits, namkeen, packaged snacks and drinks", "biscuits, namkeen, chips, packaged snacks, cold drinks or bottled water",
   "HCES Section 7.2, packaged processed food -- the other half of Section 7. cons_food_out covers 7.1, SERVED processed food (a meal or tea bought and eaten out); this covers packaged items bought and eaten anywhere, which on a trek route is a real and separate category. Omitting it put our consumption aggregate below the total-MPCE concept the poverty line is calibrated against, which biased poverty UPWARD.",
   HC + ", Section 7.2 (7-day in HCES; usual monthly here, as for every other seasonal item)")
EP("cons_pan_tobacco", "Pan, tobacco and intoxicants", "pan, gutka, bidi, cigarettes, tobacco or alcohol",
   "HCES Section 12 (12.1 pan, 12.2 tobacco, 12.3 intoxicants), asked here as ONE item rather than three: the three-way split serves HCES's item-code detail, not a poverty aggregate, and one figure is easier to answer and harder to double-count. NOT counted as food -- HCES keeps pan/tobacco/intoxicants as its own MPCE category, so it enters total_cons_pm directly and not cons_food_pm. A sensitive item: the enumerator records what is offered and does not press.",
   HC + ", Sections 12.1-12.3 (7-day in HCES; usual monthly here, and combined into one figure)")
# DELIBERATELY NOT ASKED, having checked them against the source rather than leaving them silent:
#   HCES S11.3 entertainment (30-day) -- for a worker living at the worksite through the season this
#     is close to zero, and it is a small share of rural MPCE. Documented exclusion, not an oversight.
#   HCES S13.3 bedding (365-day) -- small, annual, and mostly incurred by the home household rather
#     than by the worker here. Documented exclusion.
# Both understate consumption slightly and therefore overstate poverty slightly; the direction is
# stated in the write-up rather than silently absorbed.
R("E", "cons_clothing_12m", "Clothing and footwear spending, last 12 months (Rs)", "In the last 12 months, how much did your household spend on clothes and footwear? (Rs)", "Annual clothing and footwear spending; already spans both seasons, so asked once, not split. Converted to monthly by dividing by 12.", "money", source=HC + ", Sections 13.1-13.2 (365-day). " + IH + " 14.38-14.39 (365-day). " + GH + " instead uses a 6-month recall for clothing (items 401-441); we follow the two India sources, since one of them (HCES) underlies our poverty line")
R("E", "cons_education_12m", "Education spending, last 12 months (Rs)", "In the last 12 months, how much on education: fees, books, uniforms, tuition? (Rs)", "Annual education spending; already spans both seasons, so asked once.", "money", source=HC + ", Section 10.1 (365-day). " + IH + " 14.35-14.37 (365-day, same items). " + GH + " asks school fees inside its education/roster module, per child, not as a household total, so it is not directly comparable")
R("E", "cons_medical_hosp_12m", "Medical spending, hospital stays, last 12 months (Rs)", "In the last 12 months, how much did your household pay for any hospital admission or stay? (Rs, 0 if none)", "Hospitalisation spending; the lumpy, infrequent part of medical spending, at a 12-month recall that already spans both seasons. Together with the non-hospitalisation item above, this is the out-of-pocket health measure.", "money", source=HC + ", Section 10.2 (365-day, hospitalisation). " + IH + " 14.34 (365-day, in-patient). " + GH + " instead uses one combined 6-month medical item (less detail); we follow the matching HCES/IHDS split")
R("E", "cons_durables_12m", "Durable goods spending, last 12 months (Rs)", "In the last 12 months, how much on durable goods: furniture, utensils, cooking appliances, phone, jewellery or ornaments, bicycle or vehicle parts? (Rs)", "Annual durables spending; already spans both seasons, so asked once.", "money", source=HC + ", Section 14 (365-day, 10 sub-groups). " + IH + " 14.40-14.48 (365-day). " + GH + " (12-month tier: durables, appliances, building materials). All three agree on the 12-month recall; insurance premiums, which IHDS (14.50) and the Nigeria survey (items 510-513) count here, are excluded, following HCES and standard national-accounts practice (insurance is a financial item, not consumption) -- premiums are covered instead by the insurance items in Module G")

# cooks_own_meals_here and meal_spend_day_self were dropped 2026-09-30. meal_spend_day_self existed
# to capture a migrant's own cost of living here, but it never entered cons_food_pm or any other
# aggregate -- it appeared in the do-files only inside an assert -- while cons_food_out_yatra_pm asks
# the same thing as a monthly figure and does feed the aggregate. Adding it in would have
# double-counted. cooks_own_meals_here existed only to gate it. The asymmetry a reviewer spotted --
# buying meals led to a follow-up and cooking them did not -- was the symptom: someone who cooks here
# has their ingredient spending in cons_staples and cons_perishables already.

# ------------------------------------------------------------------ F  housing and assets
HOMENOTE = "Self-reported, not enumerator-observed: by design the interview happens away from the respondent's usual home (Kedarnath route sites, not their native place), so the enumerator cannot see it."
R("F", "floor_material", "Main floor material at usual home", "What is the main material of the floor at your usual home?", HOMENOTE, "cat", "floor", source="NITI Aayog National MPI housing indicator")
R("F", "roof_material", "Main roof material at usual home", "What is the main material of the roof at your usual home?", HOMENOTE, "cat", "roof", source="NITI Aayog National MPI housing indicator")
R("F", "wall_material", "Main wall material at usual home", "What are the walls of your usual home mainly made of?", HOMENOTE + " NITI's housing indicator is deprived if the FLOOR is natural material OR the ROOF OR THE WALL is rudimentary. Wall material was simply not asked before, so one of the three limbs could not be evaluated at all.", "cat", "wall", source="NITI Aayog National MPI housing indicator (wall limb)")
R("F", "accom_type_here", "Where the respondent sleeps during the season", "While you are here for the season, where do you sleep?", "Accommodation at the WORKSITE, which nothing else in this module describes -- floor_material, roof_material and the rest are about the usual home, and for a seasonal migrant that is not where he spends six months of the year. Feeds the security and social inclusion dimension of the Lyons et al. (2023) MLI, whose settlement-conditions indicator exists for exactly this case. Deprived at codes 4, 5 and 7: sleeping at the workplace, under canvas, or in the open.", "cat", "accomhere", source="Lyons et al. 2023, Table 2 (area/settlement conditions), adapted to a labour-migrant setting")
R("F", "electricity", "Usual home has an electricity connection", "Does your usual home have an electricity connection?", HOMENOTE, "bin", "yn", source="NITI Aayog National MPI")
R("F", "toilet_type", "Type of toilet at usual home", "What kind of toilet does your household use at your usual home?", HOMENOTE + " NITI counts a household deprived if the facility is unimproved OR improved but SHARED with other households, so a plain own-toilet yes/no cannot decide the indicator: it misses an unshared but unimproved pit latrine, and it misses a flush toilet shared between four families.", "cat", "toilet", source="NITI Aayog National MPI sanitation indicator (improved/unimproved and shared/not)")
R("F", "drinking_water", "Main source of drinking water at usual home", "What is your main source of drinking water at your usual home?", HOMENOTE + " Codes 1-6 are improved sources, 7-9 unimproved, following the JMP/NFHS taxonomy NITI Aayog's MPI indicator rests on.", "cat", "water", source="NITI Aayog National MPI drinking-water indicator (JMP improved/unimproved taxonomy)")
R("F", "water_on_premises", "Drinking water is available on the premises", "Is the drinking water available at the house itself?", "On-premises vs. fetched. NITI counts even an IMPROVED source as deprived when it is more than a 30-minute round trip away, so source alone cannot decide the indicator -- this and the next item supply the missing limb.", "bin", "yn", source="NITI Aayog National MPI drinking-water indicator (30-minute round-trip rule)")
R("F", "water_fetch_minutes", "Minutes for a round trip to fetch water", "How long does it take to go there, get the water and come back? (minutes, round trip)", "Round-trip fetching time. The 30-minute threshold is NITI's own; asked as a duration rather than a yes/no so the cutoff can be varied in robustness checks instead of being baked into the question.", "count", skip="Ask only if water_on_premises = 0", source="NITI Aayog National MPI drinking-water indicator (30-minute round-trip rule)")
R("F", "cooking_fuel", "Main cooking fuel at usual home", "What does your household mainly use to cook at your usual home?", HOMENOTE + " Replaces a yes/no LPG question. NITI Aayog's indicator names the dirty fuels explicitly -- dung, agricultural crops, shrubs, wood, charcoal or coal -- so a fuel LIST is required to apply it; a binary cannot. NOTE on kerosene: NITI's list does not name it, so it is NOT counted as deprived here, although the global MPI does count it. Recorded separately so either rule can be applied later.", "cat", "fuel", source="NITI Aayog National MPI cooking-fuel indicator (its own list of dirty fuels)")
R("F", "owns_tv", "Owns a television", "Does your household own: a television?", "Durable asset.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "owns_radio", "Owns a radio", "... a radio?", "Durable asset.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "owns_bicycle", "Owns a bicycle", "... a bicycle?", "Durable asset.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "owns_motorcycle", "Owns a motorcycle or scooter", "... a motorcycle or scooter?", "Durable asset.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "owns_car", "Owns a car, jeep or truck", "... a car, jeep or truck?", "Any car, jeep or truck, whether used for work or not. NITI treats car-or-truck ownership as its own limb, separate from the small-asset count, so it must cover work vehicles too -- owns_work_vehicle in the productive-asset block may overlap with this by design.", "bin", "yn", source="NITI Aayog National MPI assets indicator (car or truck limb)")
R("F", "owns_phone", "Household owns any telephone (mobile or landline)", "... a telephone of any kind, mobile or landline?", "Any phone in the household. On NITI's asset list and previously not asked: smartphone_owned in Module G is the respondent's own smartphone, a digital-inclusion measure, which is a different thing from whether the household owns a telephone at all.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "owns_computer", "Owns a computer or laptop", "... a computer or laptop?", "On NITI's asset list and previously not asked. Expected to be near-zero in this population, which is itself the finding.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "owns_animal_cart", "Owns an animal cart", "... a cart pulled by an animal?", "On NITI's asset list and previously not asked.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "owns_fridge", "Owns a refrigerator", "... a refrigerator?", "Durable asset.", "bin", "yn", source="NITI Aayog National MPI assets indicator")
R("F", "land_unit", "Unit the household measures its land in", "In what unit do you count your land -- nali, bigha, acres or hectares?", "Asked before the amount because a hill household thinks in nali and converting to acres in their head is an error the instrument should absorb, not create. Stata converts to acres for the asset index.", "cat", "landunit", source="Project design (local land units, Uttarakhand)")
R("F", "land_cultivable_acres", "Cultivable land owned or cultivated (in the unit given)", "And how much CULTIVABLE land is that? Do not count the land the house stands on.", "Cultivable land only. The old wording said \"agricultural land\" without excluding the homestead, so a landless household with a house on a tenth of an acre could report land it cannot farm -- and this variable now gates the crop-insurance question and stands in for productive capacity.", "num", source="Chaudhuri et al. 2002 asset covariate")
PRODNOTE = "A count would treat a goat and a buffalo, or a jeep and a hand-cart, as equally valuable productive assets, which they are not; a list of binaries at least separates asset types, even without a value weight."
R("F", "owns_cow_buffalo", "Owns any cows or buffaloes", "Does your household own any cows or buffaloes?", PRODNOTE, "bin", "yn", source="Chaudhuri et al. 2002 asset covariate")
R("F", "owns_goat_sheep", "Owns any goats or sheep", "Does your household own any goats or sheep?", PRODNOTE, "bin", "yn", source="Chaudhuri et al. 2002 asset covariate")
R("F", "owns_pony_mule", "Owns any ponies or mules", "Does your household own any ponies or mules?", PRODNOTE, "bin", "yn", source="Project design (pilot livelihood survey)")
R("F", "owns_shop_stall", "Owns a shop or stall used for work", "Does your household own a shop or stall that you use to earn?", PRODNOTE, "bin", "yn", source="Chaudhuri et al. 2002 asset covariate")
R("F", "owns_work_vehicle", "Owns a vehicle used for work", "Does your household own a vehicle you use to earn (for example a jeep, truck or taxi)?", PRODNOTE, "bin", "yn", source="Chaudhuri et al. 2002 asset covariate")
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
R("G", "loan_purpose", "What the loan was taken for", "What did you take it for?", "Purpose separates a loan that buys a pony -- an investment in the livelihood -- from one that covers a hospital bill or a wedding, which is distress borrowing. The same outstanding balance means opposite things in the two cases, and nothing in the instrument could tell them apart.", "cat", "loanpurpose", skip="Ask only if took_loan_12m = 1", source="Project design (investment against distress borrowing)")
R("G", "loan_amount_borrowed", "Amount originally borrowed (Rs)", "How much did you borrow in total? (Rs)", "The principal. The instrument asked only what was still outstanding, so a household that had repaid most of a large loan and one that took a small loan looked identical, and the repayment burden could not be computed at all.", "money", skip="Ask only if took_loan_12m = 1", source="Project design (loan size, for the debt-burden measures)")
R("G", "loan_amount", "Total amount still owed (Rs)", "How much of that loan is still left to repay? (Rs)", "Outstanding DEBT STOCK, not the amount borrowed. The instrument previously recorded who lent but never how much is owed -- which is the quantity that decides whether a shock turns into poverty.", "money", skip="Ask only if took_loan_12m = 1", source="Islam and Chowdhury 2025 (financial distress and household vulnerability to poverty)")
R("G", "pays_interest", "Pays interest on the loan", "Do you pay interest on it?", "Gate for the rate question. The rate item previously read \"0 if none, leave blank if not known\" -- two different \"if not\" branches in one instruction -- which is unanswerable. Interest-free borrowing from relatives is common, so this is a real branch, not a formality.", "bin", "yn", skip="Ask only if took_loan_12m = 1", source="Project design (informal lending is often interest-free)")
R("G", "loan_interest_per100_pm", "Interest per Rs 100 borrowed, per month", "On every 100 rupees you borrowed, about how much interest do you pay in a month? (Rs; 0 if none, leave blank if not known)", "Interest as rupees per hundred per month, which is how informal lending is actually quoted here. ENUMERATOR RULE, because people answer in whichever unit they think in: rupees per 100 per month and PERCENT PER MONTH are the same number, so a \"3 percent\" answer is entered as 3. If they give an ANNUAL rate, divide by 12 before entering (36 percent a year becomes 3). If they quote a flat amount on the whole loan, work it back per 100 first. An annual percentage rate is not asked directly because most respondents would have to compute it, and would compute it badly.", "num", skip="Ask only if took_loan_12m = 1; may be left blank", source="Project design (informal-credit pricing as locally quoted)")
R("G", "loan_against_asset", "Loan is secured against an asset", "Did you have to give something as security for it -- an animal, a vehicle, jewellery, land or your business?", "Secured vs. unsecured. A secured loan turns a productive asset into collateral, so one shock can cost the household both the repayment AND its means of earning -- the asset-smoothing mechanism the instrument could not otherwise see.", "bin", "yn", skip="Ask only if took_loan_12m = 1", source="Carter and Zimmerman 2000; Chiwaula et al. 2011 (asset-based vulnerability)")
R("G", "loan_collateral", "What was pledged as security", "What did you have to give as security?", "WHAT was pledged, not merely whether something was. A binary cannot tell a shop pledging its stock -- ordinary commerce -- from a household pledging its jewellery or its only buffalo, which is distress. The type is the signal; the fact of collateral is not.", "cat", "collat", skip="Ask only if loan_against_asset = 1", source="Carter and Zimmerman 2000; Zimmerman and Carter 2003 (asset-based coping)")
R("G", "n_health_insured", "Household members covered by health insurance or a scheme", "How many people in your household are covered by any health insurance or health scheme, including government ones? (0 if none)", "A COUNT, not a category. Health, life and crop cover are not alternatives -- a household can hold all three -- yet the old single categorical forced a choice and dumped any household with two into an uninformative \"more than one\". A count also shows PARTIAL coverage, which no binary can.", "count", source="NITI Aayog National MPI health-insurance indicator; Lyons et al. 2023")
R("G", "n_life_insured", "Household members with life insurance", "How many people in your household have life insurance? (0 if none)", "Count of life-insured members, asked separately from health cover for the reason above.", "count")
R("G", "has_crop_insurance", "Household has crop insurance", "Is your crop insured?", "Asked only of households with cultivable land -- it is meaningless for the rest, and the old categorical offered it to everyone.", "bin", "yn", skip="Ask only if land_cultivable_acres > 0")
# Restructured 2026-10-01. The ten named schemes were OPTIONS; they are now a PROBE LIST in the
# enumerator hint, and what gets recorded is what the respondent says, coded in the office like the
# occupation fields. The reason the list existed is unchanged and still honoured -- a bare "did you
# get a government benefit?" is a recall task people fail, so the names must be read out -- but a
# fixed ten-item list decides in advance which benefits count, and the list was ours, not
# Uttarakhand's: a state scheme, a pension paid under a name the respondent actually uses, or a new
# transfer would all have landed in "some other scheme" and lost its identity. Free text keeps the
# name. The cost is that the scheme categories now come out of the office coding step rather than
# off the tablet, which GETTING_THE_DATASET.md states as its own step.
R("G", "govt_any_benefit", "Household received from any government scheme, last 12 months", "In the last 12 months, did your household get anything from any government scheme? Read the list out before you take an answer.", "Whether the household touched the public safety net at all. The enumerator hint carries the eight-scheme probe list that is read out; the names themselves go in the free-text item below. A No here, AFTER the list has been read, is a real No -- which is the job the old code 10 was doing.", "bin", "yn", source="Project design; scheme names as administered in Uttarakhand")
R("G", "govt_schemes_detail", "Which schemes, in the respondent's words (coded in the office)", "Which ones? Write down every scheme they name, in their own words.", "Verbatim scheme names, office-coded afterwards against the Uttarakhand scheme list. IMPORTANT ITEM: this is now the ONLY place the identity of a benefit is recorded, so an answer left at 'a government scheme' loses the distinction between a ration card, a widow pension and MGNREGA wages -- which protect against entirely different things. Required when govt_any_benefit = 1, unlike the other verbatim fields, for that reason.", "text", skip="Ask only if govt_any_benefit = 1", source="Project design; coded in the office against the Uttarakhand scheme list")
R("G", "ration_portable_here", "Can draw the ration entitlement at the worksite", "Can you draw your ration here, or only at your home place?", "Portability of the food entitlement under One Nation One Ration Card, and the closest real analogue to the legal-residency indicator in Lyons et al. (2023): a migrant whose entitlement works only at his home place is outside the food safety net for the half of the year he is earning, which is exactly when a shock would bite. UNGATED as of 2026-10-01: it was gated on the ration-card code in the scheme check-all, and that code no longer exists as a code -- so 'no ration card' is an OPTION here instead of a gate. One question in place of a question plus a gate, and the non-cardholder is now recorded explicitly rather than by absence.", "cat", "portable", source="Lyons et al. 2023, Table 2 (legal residency), adapted; One Nation One Ration Card")
R("G", "smartphone_owned", "Owns a smartphone", "Do you own a smartphone?", "Smartphone ownership.", "bin", "yn", source="VEP adaptive-capacity covariate; STEP digital items")
R("G", "uses_digital_payment", "Uses UPI or another digital payment", "Do you ever use UPI or another way of paying by phone?", "Binary. The old never/sometimes/often scale asked respondents to rate their own frequency on an undefined scale; \"sometimes\" and \"often\" are not comparable between two people and carry nothing a binary does not.", "bin", "yn", source="VEP adaptive-capacity covariate; STEP digital items")
R("G", "n_can_transact_online", "Household members who can pay by phone unaided", "How many people in your household can make a payment by phone themselves, without help? (0 if none)", "Household digital capability rather than the respondent's own use: it says who in the household can actually move money, and therefore something about who controls it.", "count", source="Project design (intra-household financial capability)")

# ------------------------------------------------------------------ H  health
R("H", "morbidity_15d", "Anyone ill in the last 15 days", "In the last 15 days, was anyone in your household ill?", "Illness in the last 15 days.", "bin", "yn", source="NSS health module (15-day recall) [source not held by this project; citation unverified as of 2026-09-28]")
R("H", "morbidity_coping_15d", "How the household coped with the cost of this illness", "How did the household mainly cope with the cost of this: used savings; borrowed money; sold or pawned assets; cut other consumption; got help from relatives or community; or something else?", "Coping response to the illness reported above; same coping list as the Module I shock question.", "cat", "coping", skip="Ask only if morbidity_15d = 1", source="Project design (a reported illness with no cost/coping follow-up said nothing about its burden)")
R("H", "morbidity_cost_15d", "Amount spent on this illness, last 15 days (Rs)", "About how much did the household spend on this in the last 15 days (medicine, doctor or clinic fees, travel for care)? (Rs)", "Out-of-pocket cost of the illness reported above.", "money", skip="Ask only if morbidity_15d = 1", source="Project design")
R("H", "func_limitation", "Difficulty walking or climbing steps (Washington Group)", "Do you have difficulty walking or climbing steps?", "Washington Group Short Set item 3, asked verbatim with its own four-point scale and deprived at the standard cutoff of a lot of difficulty or cannot do it at all. One item rather than the full six, and the mobility one on purpose: this workforce carries loads and people up a 16-kilometre climb, so walking and climbing is both the function that matters most to the livelihood and the one most likely to be lost. Gives the Lyons et al. health dimension a disability indicator, which the NITI MPI has none of, and enters the VEP models as a sensitivity covariate. State the limit in the write-up: one item is not the WG-SS and cannot carry its prevalence estimate.", "cat", "wgdiff", source="Washington Group on Disability Statistics, Short Set item 3 (mobility), verbatim; Lyons et al. 2023 health dimension")
R("H", "hospitalization_365d", "Anyone admitted to hospital in the last 12 months", "In the last 12 months, was anyone in your household admitted to hospital overnight?", "Hospital admission.", "bin", "yn", source="NSS health module (365-day recall) [source not held by this project; citation unverified as of 2026-09-28]")
R("H", "health_access_barrier_3m", "Unable to get needed medical care, last 3 months", "In the last 3 months, was there a time when someone in your household needed medical care but could not get it?", "Healthcare-access barrier (unmet need), distinct from having insurance cover.", "bin", "yn", source="VASyR 2025 barriers_health_case_access_phc_m (primary-care access barriers); Lyons et al. 2023 Table 2 indicator 2 'healthcare access'")
NITIH = ("NITI Aayog's Health dimension is three indicators -- Nutrition (1/6), Child and Adolescent "
         "Mortality (1/12) and Maternal Health (1/12) -- and this instrument previously had NONE of "
         "them, substituting a project-built health-access measure. Two of the three need no "
         "household roster and are added here. NUTRITION CANNOT BE COLLECTED: NITI defines it on "
         "anthropometry (measured height, weight, BMI) and a read-aloud interview at a worksite "
         "cannot produce that, so the MPI built from this instrument is a TEN-of-twelve-indicator "
         "index and must be reported as such, never as the National MPI.")
R("H", "child_death_5y", "A child or adolescent under 18 died in the household, last 5 years", "In the last five years, has any child or young person under 18 in your household died?", "NITI's Child and Adolescent Mortality indicator, verbatim in its own terms. One question, no roster needed. " + NITIH, "bin", "yn", source="NITI Aayog National MPI, Child and Adolescent Mortality (weight 1/12)")
R("H", "birth_last_5y", "A woman in the household gave birth in the last 5 years", "In the last five years, did any woman in your household give birth?", "Gate for the two maternal-health questions. " + NITIH, "bin", "yn", source="NITI Aayog National MPI, Maternal Health (weight 1/12)")
R("H", "anc_4_visits", "Mother had at least 4 antenatal check-ups for the most recent birth", "For the most recent birth, did she have at least four check-ups before the delivery?", "First limb of NITI's Maternal Health indicator. \"Don't know\" was REMOVED 2026-10-01. The old reasoning was that a don't-know is conservative because the indicator tests anc != 1, so it counts as deprived -- but that is exactly the danger: a male respondent who cannot recall is then recorded as a deprived household, and a sample with many such respondents reports a maternal-health deprivation rate built out of ignorance rather than out of care not received. The item is now a plain yes/no and the burden moves to the probe (see the hint): ask the mother if she is there, and otherwise ask how many times she went and code four or more.", "cat", "yn", skip="Ask only if birth_last_5y = 1", source="NITI Aayog National MPI, Maternal Health (antenatal care limb)")
R("H", "skilled_birth_attendant", "Who conducted the most recent delivery", "Who conducted that delivery -- a doctor, a nurse or ANM, an ASHA or Anganwadi worker, a dai, or nobody trained?", "Second limb of NITI's Maternal Health indicator; NITI counts the household deprived if EITHER limb fails. Asked as the CADRE rather than as yes/no: \"a doctor, nurse or trained midwife\" named no cadre anybody here uses, and an ASHA or Anganwadi worker -- who commonly does accompany a birth in these districts -- would have been heard as a yes. NFHS and NITI count only a doctor, nurse, ANM, LHV or qualified midwife as skilled; an ASHA, an Anganwadi worker and a dai are explicitly NOT, so putting them in the list as their own codes is what keeps the indicator correct. Deprived unless code 1 or 2.", "cat", "birthattend", skip="Ask only if birth_last_5y = 1", source="NITI Aayog National MPI, Maternal Health (assisted delivery limb); skilled-provider definition per NFHS")

# ------------------------------------------------------------------ I  shocks
R("I", "distress_event_last365d", "Shocks in the last 12 months (check all that apply)", "In the last 12 months, did any of these happen -- to your household, or to the Yatra route you work on? Check every one that applies.", "Check-all, replacing \"record the most serious one\". That instruction asked the enumerator to rank another household's misfortunes against each other, which they are in no position to do and which threw away every shock but one. The list also gains four COVARIATE shocks (codes 5-8) that hit the whole route at once; every code in the old list was household-idiosyncratic, so the covariate-versus-idiosyncratic decomposition could not be identified from this data at all.", "multi", "distress", source="VEP exposure covariate (Azeem et al. 2016); shock inventory following Gunther and Harttgen 2009, via Fujii 2016 section 4")
# Shock MAGNITUDE, for whichever event the respondent names as the hardest. Incidence alone cannot
# support a vulnerability-as-uninsured-exposure-to-risk analysis: VER asks how far consumption moves
# per unit of shock, and without a size there is no per unit.
# Split in two on 2026-10-01. The single item asked for "earnings lost AND money spent, in all",
# which is two quantities in different kinds and asks the respondent to add them -- and to value his
# own forgone work, which he can only do by guessing at a wage we have already measured. Asked as
# the two facts instead: how much work was lost, and how much money went out. shock_loss_total then
# values the lost work at the respondent's OWN measured weekly earnings in Stata, which is both more
# accurate than his estimate and a quantity the two limbs can be reported separately against.
R("I", "shock_work_lost_weeks", "Weeks of work lost because of the worst shock", "Thinking of whichever of those hit you hardest -- about how many weeks of work did you lose because of it? (0 if none)", "The TIME limb of the shock. Asked in weeks rather than months because this is a six-month earning season: three weeks lost at the peak is a large shock and would round to zero months, while weeks divide cleanly into the monthly calendar afterwards. Valued at the respondent's own measured earnings in shock_loss_total rather than at his estimate of them.", "count", skip="Ask only if distress_event_last365d names a real shock (not code 9, nothing happened)", source="Ligon and Schechter 2003; Dercon and Krishnan 2000 (VER needs shock magnitude, not only incidence)")
R("I", "shock_money_spent", "Money the household had to spend because of the worst shock (Rs)", "And about how much money did your household have to spend because of it -- treatment, repairs, replacing what was lost? (Rs, 0 if nothing)", "The CASH limb of the shock: money that actually left the household, separate from earnings it never received. A rough figure is expected -- the quantity of interest is the order of magnitude against household consumption, not the rupee.", "money", skip="Ask only if distress_event_last365d names a real shock (not code 9, nothing happened)", source="Ligon and Schechter 2003; Dercon and Krishnan 2000 (VER needs shock magnitude, not only incidence)")
R("I", "shock_month", "Month the worst shock happened", "And in which month did that one happen?", "Shock TIMING, which is what matches the event to the monthly income calendar in Module C and to the season the household was in. A shock during the Yatra season and the same shock during the closure are different events for a household earning its whole year in six months.", "cat", "month", skip="Ask only if distress_event_last365d names a real shock (not code 9, nothing happened)", source="Dercon and Krishnan 2000 (seasonal timing of shocks); project design")
R("I", "shock_coping", "How the household coped (check all that apply)", "How did your household manage? Check every one they used.", "Check-all. The single-answer version forced a choice between \"sold or pawned assets\" and \"cut consumption\" -- which are precisely the two responses asset-smoothing theory (Carter and Zimmerman) says to compare, since a household facing a survival constraint may cut consumption specifically to defend its assets. Made mutually exclusive, the test was impossible.", "multi", "coping", skip="Ask only if any shock was reported", source="Coping strategies in VEP studies; Carter and Zimmerman 2000 on asset versus consumption smoothing")
RCSI = ("The reduced Coping Strategy Index (rCSI): five food-coping questions, standard WFP weights (1, 2, 1, "
        "1, 3) applied when the index is built. The Kedarnath instrument otherwise has no food-security "
        "module, which is a gap for a poverty-vulnerability survey; these five short questions close it at "
        "low cost instead of a full dietary-diversity module, left out to stay inside the 45-minute limit. "
        "Kept as day-counts (0-7), not collapsed to yes/no: this is the standard, validated WFP/FAO "
        "specification (frequency x severity), and no comparably-standard binary version was found on "
        "checking; a day-count also takes about as long to answer as a yes/no in practice, so little "
        "interview time is saved by simplifying it.")
RCSIS = ("Workers here are migrants, interviewed during the Yatra season: a single 'last 7 days' recall would "
         "describe only their on-site coping at the work site, not their household's usual pattern, which may "
         "look very different in the off-season (different household members present, different food access). "
         "So each item is asked as a usual-week day-count for each season, the same Yatra-season/off-season "
         "split already used for the calendar (Module B/C) and consumption (Module E).")
VASYR_NOTE = ("Worded to match VASyR's own item text exactly (its stem: 'Strategy to cope with a lack of "
              "food or money to buy it: ...'), not a paraphrase for this project -- only the recall framing "
              "(a normal week per season, instead of VASyR's literal 'last 7 days') is adapted, for the "
              "migrant-seasonality reason below; the coping behaviour itself is worded exactly as VASyR asks it.")
def CP(name, label, item_text):
    R("I", name + "_yatra_wk", label + ", usual week in Yatra season", "In a normal week during the Yatra season, to cope with a lack of food or money to buy it, how many days did your household " + item_text + "? (0-7 days)", "rCSI Yatra-season item. " + VASYR_NOTE + " " + RCSIS, "count", source="VASyR 2025 (exact item wording); WFP rCSI; " + RCSI)
    R("I", name + "_offseason_wk", label + ", usual week off-season", "In a normal week when the Yatra is closed, to cope with a lack of food or money to buy it, how many days did your household " + item_text + "? (0-7 days)", "rCSI off-season item. " + VASYR_NOTE + " " + RCSIS, "count", source="VASyR 2025 (exact item wording); WFP rCSI; " + RCSI)

CP("cope_less_pref_food", "Days relied on less expensive/preferred food", "rely on less expensive/less preferred food")
CP("cope_borrow_food", "Days borrowed food/relied on help from others", "borrow food and/or rely on help from friends/relatives")
CP("cope_reduce_meals", "Days reduced number of meals eaten per day", "reduce the number of meals eaten per day")
CP("cope_reduce_portion", "Days reduced portion size of meals", "reduce portion size of meals")
CP("cope_restrict_adult", "Days restricted adult consumption for children", "restrict consumption of adults/mothers in order for young children to eat")

# ------------------------------------------------------------------ J  ropeway
R("J", "ropeway_stance", "View on the proposed Kedarnath ropeway", "A ropeway is proposed between Gaurikund and Kedarnath. Are you in favour, neutral, or against?", "Stated stance; no rating scale. Asked only on the Kedarnath route (site = 1): the question names a specific proposal, and reading it to a Hemkund respondent asks him about a project that is not his.", "cat", "stance", source="Project design")
R("J", "trek_dependent", "Main work is carrying or guiding on the trek", "Is your main work carrying, transporting or guiding people or goods on foot along the pilgrimage trek?", "Direct exposure flag (factual); not inferred from job title.", "bin", "yn", source="Project design (see tasks_module W4: exposure must be asked directly)")

# ------------------------------------------------------------------ K  job quality (Apablaza et al. 2026, Appendix 2, read
# directly and used with its own skip logic. Not reproduced: Q1-Q4 (household-roster demographics --
# ours is a no-roster, aggregate-report design; Q4 itself is adapted as main_income_earner in Module A)
# and the open-text Q6/Q7 (occupation/workplace sector -- already covered by occupation's 13 groups,
# which blend occupation and workplace type for this specific economy). Q14/Q15 (single-point earnings
# + a fallback range if unknown) are not reproduced either: the 12-month calendar (Module C) already
# asks earnings, month by month, which is more information than one point-in-time figure or its range.
KA = "Apablaza et al. 2026, Appendix 2 "
KSKIP = "Ask only if job_situation is 1, 2 or 3 (currently working)"
# Apablaza Q5 routes three ways, so the module has three gates, not one:
#   1-3 (working)          -> the whole job-quality block below (KSKIP)
#   4-7 (studying/trained/retired/unpaid care) -> skip to Q21 wants_more_work (KTAIL)
#   8   (unemployed, seeking)                  -> skip to Q22/Q23 (hours wanted, job search)
#   9-11 (sick/inactive/don't know)            -> end the module entirely
KTAIL = "Ask if job_situation is 1 to 7 (Apablaza routes codes 4-7 straight to this question)"
R("K", "job_situation", "Work situation during the last month", "Which best describes your situation during the last month: you work for pay full-time; you work for pay part-time or do occasional jobs; you study and work; you only study; you are only being trained for work; you are retired or pensioned; you do unpaid household tasks or care for others; you are unemployed and actively looking for work; you are sick or disabled and cannot work; or none of these?", "Screening item, Apablaza's full eleven-category set (Q5), coded from the answer rather than read aloud. The categories are kept apart because Apablaza routes them to three different places (see the gate comment above); collapsing them would lose the routing. In practice codes 4-6 almost never fire, since the sample is recruited at the Yatra worksite.", "cat", "jobsit", source=KA + "Q5 (all eleven categories, with its own three-way routing)")
# employer_type was dropped 2026-09-30. It asked employment status a SECOND time, in Apablaza's Q8
# taxonomy, minutes after employment_type asked it in Module B -- two overlapping lists, no check that
# they agreed, and only the Module B answer ever reached the analysis. Q8 is also the worse instrument
# here: its codes cross status with institutional sector (private company / public sector / armed
# forces / domestic service), so a porter paid by a thekedar or a shop worker paid by the shop owner --
# employed by an individual, not a firm, which is most of this sample -- had no true option but
# "employee of a private company". The one category Q8 had that Module B lacked, unpaid family worker,
# has been added to emptype instead.
R("K", "job_permanence", "Type of job: permanent, seasonal, casual, probationary or fixed-term", "Is your job: permanent; seasonal or temporary; occasional or casual; on probation; or fixed-term?", "Job permanence, Apablaza's five categories kept separate rather than merging probation with fixed-term.", "cat", "jobperm", skip=KSKIP, source=KA + "Q9")
R("K", "contract_status", "Has a signed contract", "Do you have a signed contract? Yes, signed; yes but not yet signed; no contract.", "Contract status, wage workers only.", "cat", "contract", skip=KSKIP + "; and employment_type is 3 or 4 (wage workers) -- self-employed skip to the next question", source=KA + "Q11")
R("K", "workplace_registered", "Workplace or business is registered", "Is your workplace or business registered, for example with a taxpayer or GST number, a shop or trade licence, the Yatra registration, or a union?", "Registered enterprise (Apablaza asks about a taxpayer number).", "bin", "yn", skip=KSKIP, source=KA + "Q12 (widened to local registrations)")
# Gated to wage workers as of 2026-10-01. An own-account pony owner was being asked whether his
# EMPLOYER deducts a pension, provides health insurance, and grants paid leave. He has no employer;
# the questions have no answer for him and reading them out costs the enumerator credibility.
# contract_status was already gated this way; these three were not.
R("K", "pension_contrib", "Contributes to a pension system", "Do you contribute to any pension system? Yes, the employer deducts it; yes, voluntarily; no.", "Pension contribution.", "cat", "pension", skip=KSKIP, source=KA + "Q16")
R("K", "work_health_ins", "Has health insurance through work", "Do you have health insurance through your work? Yes; only private or other insurance; none; don't know.", "Work-related health insurance.", "cat", "workins", skip=KSKIP, source=KA + "Q17")
R("K", "leave_rights", "Has right to paid leave (holiday, sick or maternity)", "Do you have the right to paid holiday, sick or maternity leave?", "Leave rights. Apablaza asks this of everyone still in the block, not only wage workers (a self-employed respondent can simply answer no), so the wage-worker-only skip used earlier is dropped to match.", "cat", "yndk", skip=KSKIP, source=KA + "Q18")
R("K", "injured_ever", "Ever physically injured at work", "Have you ever been physically injured at your workplace?", "Injury history.", "cat", "yndk", skip=KSKIP, source=KA + "Q19")
R("K", "workplace_injury_12m", "Anyone injured or killed at your workplace, last 12 months", "In the last 12 months, was anyone physically injured or killed at your workplace because of work?", "Recent workplace injury or death (hazard evidence).", "cat", "yndk", skip=KSKIP, source=KA + "Q20")
R("K", "wants_more_work", "Would like to work more", "Would you like to work more hours than you do?", "Involuntary underemployment. Gated at codes 1-7, not 1-3: Apablaza routes the studying, in-training, retired and unpaid-care categories (4-7) directly to this question, so gating it on 'currently working' would drop exactly the respondents it is meant to reach.", "cat", "yndk", skip=KTAIL, source=KA + "Q21")
R("K", "more_hours_day", "Additional hours per DAY wanted", "On a working day, how many MORE hours would you like to work?", "Extra hours wanted.", "count", skip="Ask if wants_more_work = 1, or if job_situation = 8 (Apablaza routes the unemployed-and-seeking category here directly)", source=KA + "Q22")
R("K", "months_looked_for_work", "Months spent looking for work", "Across the months when you had no paid work, about how many MONTHS in total were you looking for work?", "Job-search duration in weeks -- Apablaza's own unit (Q23) -- rather than a plain yes/no, tied to the idle months already identified in the work calendar (Module C) rather than to a single point in time. Fires on the calendar OR on job_situation = 8: the calendar gate is this project's own improvement (it anchors the recall to months the respondent has already named), but on its own it would miss a respondent who is unemployed and seeking right now, which is the case Apablaza routes here.", "count", skip="Ask if any month in the calendar is 'No paid work', or if job_situation = 8", source=KA + "Q23 (duration in weeks, tied to the calendar instead of a single point in time)")
R("K", "first_job_ever", "Current/most recent work was the respondent's first job ever", "Was your current work the first paid job you ever had?", "Ever had a prior job at all -- a coarse mobility/entry marker.", "cat", "yndk", source=KA + "Q24")

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
    R("L", nm, lab[:70] + " (task grid)" if len(lab) <= 62 else lab[:80], f"Do you {lab[0].lower() + lab[1:]}? ",
      f"Task {no} of the full 27-task list (tasks_module). Three answers: regular now / done before / never; not a rating.", "cat", "task3", source=src)
R("L", "drove_twowheeler", "Has driven a motorcycle or scooter (licence or not)", "Have you ever driven a motorcycle or scooter, with or without a licence?", "Factual driving experience by vehicle class.", "bin", "yn", skip="Ask only if tk_drive is 1 or 2", source="Level ladder without licences: people drive without holding a licence")
R("L", "drove_car", "Has driven a car or jeep (licence or not)", "... a car or jeep?", "Factual driving experience by vehicle class.", "bin", "yn", skip="Ask only if tk_drive is 1 or 2", source="Level ladder without licences")
R("L", "drove_heavy", "Has driven a truck or bus (licence or not)", "... a truck or bus?", "Factual driving experience by vehicle class.", "bin", "yn", skip="Ask only if tk_drive is 1 or 2", source="Level ladder without licences")
R("L", "read_at_work", "Reads anything at work", "In your work, do you read anything (notes, rate lists, tickets, messages)?", "Reading used at work (factual).", "bin", "yn", source="STEP module 6A")
R("L", "calc_at_work", "Works out prices or costs at work", "In your work, do you work out prices or costs?", "Arithmetic used at work (factual).", "bin", "yn", source="STEP module 6A")

# ------------------------------------------------------------------ CONSTRUCTED (built in Stata from the asked variables)
def C(name, label, desc, formula, kind="num", lset=None, source="Constructed"):
    R("X", name, label, "Not asked. Constructed.", desc, kind, lset, origin="constructed", formula=formula, source=source)

C("education_years", "Years of schooling completed", "The direct year count (years_schooling) when the respondent knew it; otherwise the midpoint of the fallback bracket (education_level_cat: 0/2/7/11 for no-formal/some-primary/primary-complete/secondary-plus); missing if the respondent preferred not to say.",
  "years_schooling if knows_years_schooling==1, else bracket midpoint from education_level_cat", source="NITI Aayog National MPI")
C("hoh_female", "Sex of the household head", "Derived from the gendered relationship categories: husband/father/son/brother/other-male imply a male head, wife/mother/daughter/sister/other-female a female head, and when the respondent IS the head it is their own sex. Replaces a separate male/female question.", "from hoh_relation; = female if hoh_relation==1", "bin", "sex")
# home_rural_urban stopped being constructed on 2026-09-28 and is now asked directly in Module D.
# It was derived from home_admin_level (village -> rural, town or city -> urban), which put a 45%
# swing in the poverty line -- Rs 2,515 against Rs 3,639 -- behind a three-way tier the respondent
# was in no position to classify. The binary is what the line needs and what a respondent can answer.

# ---- measured seasonal base, from the Module C location row -----------------------------------
C("months_here", "Months living on the Yatra route in the past year", "Derived from the absence spell: 12 minus the months between left_here_month and returned_here_month, or 12 for a respondent who never leaves. This is the measured length of the respondent OWN season, in place of a constant applied to everyone, and it is what the mid-month Yatra-start problem resolves to -- the boundary is the month they reported, not one we chose. Built straight from the spell as of 2026-10-01; it used to be 12 minus months_home_base minus months_third_place, which routed the season weight -- the weight on every consumption and income figure in the study -- through the months_away_for_work answer. It no longer depends on it.", "12 - months_away_total", "count", source="Project design (measured from the absence spell, Module C)")
# months_home_base and months_third_place dropped 2026-10-01 with months_away_for_work, the only
# question either was built from. Neither appeared in a covariate vector or a deprivation
# indicator. The absence spell still gives months_away_total and months_here.
C("closure_labour_migrant", "Sold labour away from both bases during the closure", "1 if the respondent reported working away during the closure. Type B in the closure-regime typology and the mobility variable that actually carries information in this population, in place of a migrant dummy built on district boundaries -- which the pilot shows would classify 11 of 20 seasonal movers as non-movers.", "worked_away_in_closure==1", "bin", "yn", source="Project design (off-season labour migration)")
C("cons_pc_denom_season", "People the Yatra-season consumption figures cover", "n_here_season for a split household, hhsize for everyone else. This is the fix for a real error in the poverty headcount: per-capita consumption divided the Yatra-season figure -- which covers only \"you and anyone staying with you here\" -- by the FULL household size, so a man supporting himself here for six months while a family of five lived at the home place was recorded at a fraction of his true per-capita consumption and counted as poor by arithmetic. The off-season half keeps hhsize, because by then the household is reunited.", "n_here_season if split_household==1, else hhsize", "count", source="Project design (season-specific denominator)")
C("stays_all_year", "Does not move at all when the Yatra closes", "1 if the respondent does not go to the home place at closure. The case the two-season design of this instrument does NOT fit: for these respondents the Yatra-season and off-season questions describe the same place, and the pair should be checked for a suspiciously high identical-answer rate at the pilot.", "resp_returns_at_closure==0", "bin", "yn", source="Project design (assumption check on the two-season recall design)")
C("split_household", "Respondent and household are in different places during the season", "1 if the rest of the household lives at the home place year-round. The case Module E Yatra-season wording was written for, and the case whose per-capita consumption was being computed wrongly until n_here_season existed.", "hh_at_home_place==1", "bin", "yn", source="Project design (split-household measurement, underpinning Module E)")
C("credit_institutional", "Borrowed from an institutional lender", "1 if the household borrowed in the last 12 months from a bank, cooperative, RRB, microfinance institution or SHG (credit_source 1-4); 0 otherwise, INCLUDING households that did not borrow at all. Defined for every respondent on purpose: credit_source itself is now gated behind took_loan_12m, so using it directly as a VEP covariate would drop every non-borrower from the regression.", "took_loan_12m==1 & inrange(credit_source,1,4)", "bin", "yn", source="VEP adaptive-capacity covariate")
C("credit_informal", "Borrowed from an informal lender", "1 if the household borrowed from a moneylender, relative, friend, employer or contractor (credit_source 5-8); 0 otherwise, including non-borrowers. Separated from institutional credit because the two have opposite signs for vulnerability.", "took_loan_12m==1 & inrange(credit_source,5,8)", "bin", "yn", source="VEP adaptive-capacity covariate")
C("migrant", "Migrant: permanent home is outside the district", "1 if origin is not Local (same district).", "origin > 1", "bin", "yn")
C("health_access_tier", "Health-access tier of the site", "Remoteness of the interview site along the route, derived from the interview GPS rather than from an enumerator-coded cluster: the route runs from the road-head and its hospital up to the shrine, so position along it is what determines how reachable care is. Latitude bands (research team's route crosswalk): below 30.58 Good, 30.58 to 30.66 Moderate, 30.66 and above Poor. Bands, not coordinates, enter the analysis, so the exported data still carries no named site.",
  "from gps_lat: 3 if <30.58; 2 if 30.58-30.66; 1 if >=30.66", "cat", "tier", source="Project design; VEP exposure covariate")
C("health_access_deprived", "Health-access deprived (project measure, NOT an MPI indicator)", "1 if the site tier is Poor, or Moderate and nobody in the household has health cover. health_insurance_covered was REMOVED: it asked whether \"your household\" is covered, which for a split migrant household -- the worker here, the family elsewhere -- does not name a group the respondent can answer for. n_health_insured, a count of covered members, replaces it and is strictly more informative. This variable is also no longer part of the MPI: the health dimension now uses NITI's own mortality and maternal indicators, so this is kept only as a VEP exposure covariate.", "tier==1 | (tier==2 & n_health_insured==0)", "bin", "yn", source="Project design (health-access exposure covariate; not a NITI indicator)")

C("yatra_months", "Months of Yatra work in the past year", "Count of calendar months with status 1 (Yatra work).", "count of status_m1-status_m12 == 1", "count")
C("yatra_start_month", "First month of Yatra work", "First calendar month coded Yatra work.", "first m with status_m == 1", "cat", "month")
C("yatra_end_month", "Last month of Yatra work", "Last calendar month coded Yatra work.", "last m with status_m == 1", "cat", "month")
C("offseason_months_worked", "Months of paid work outside the Yatra work", "Months coded 2 to 7 (any paid activity other than Yatra work).", "count of status_m in 2..7", "count")
C("months_no_work", "Months in the year without any paid work", "Months coded 8.", "count of status_m == 8", "count")
C("offseason_primary", "Main activity outside the Yatra season", "The activity that fills most of the non-Yatra months (ties go to the lower code; all months idle gives 8).", "modal status_m among months where status_m != 1", "cat", "activity")
C("income_from_fallback", "Earnings came from the annual-total fallback, not the monthly calendar", "1 if the respondent could not give month-by-month earnings and was routed to income_annual_total + pct_income_yatra instead. Carry this into every VEP regression as a robustness split: fallback respondents have a flatter within-season earnings profile by construction (see income_seasonality_cv), so their estimated variance is not measured the same way as everyone else's.",
  "knows_monthly_income == 0", "bin", "yn", source="Project design (measurement-mode flag for the Apablaza Q15-style fallback)")
C("yatra_income", "Annual work income from Yatra months (Rs)", "Calendar path: sum of monthly earnings in the months coded Yatra work. Fallback path: the annual total times the respondent's own Yatra share.",
  "knows_monthly_income==1: sum income_m if status_m==1; else income_annual_total * pct_income_yatra/100", "money")
C("non_yatra_income", "Annual work income from other months (Rs)", "Calendar path: sum of monthly earnings in the other months. Fallback path: the annual total times the remaining share.",
  "knows_monthly_income==1: sum income_m if status_m!=1; else income_annual_total * (100-pct_income_yatra)/100", "money")
C("income_pm_yatra_eq", "Earnings per Yatra-season month, fallback path (Rs)", "Yatra earnings spread evenly across the months the calendar codes as Yatra work. Defined for fallback respondents only; for calendar respondents the actual monthly figures are used instead.",
  "yatra_income / yatra_months if income_from_fallback==1", "money")
C("income_pm_other_eq", "Earnings per non-Yatra month, fallback path (Rs)", "Non-Yatra earnings spread evenly across the remaining months. Defined for fallback respondents only.",
  "non_yatra_income / (12 - yatra_months) if income_from_fallback==1", "money")
C("remittance_outward_annual", "Total outward remittances, annual (Rs)", "Yatra-season months at the Yatra-season usual amount, other months at the off-season usual amount.",
  "yatra_months*remit_out_yatra_pm + (12-yatra_months)*remit_out_offseason_pm", "money", source="NSS 64th Round practice, applied to the calendar [source not held by this project; citation unverified as of 2026-09-28]")
C("remittance_inward_annual", "Total inward remittances, annual (Rs)", "Yatra-season months at the Yatra-season usual amount, other months at the off-season usual amount.",
  "yatra_months*remit_in_yatra_pm + (12-yatra_months)*remit_in_offseason_pm", "money", source="NSS 64th Round practice, applied to the calendar [source not held by this project; citation unverified as of 2026-09-28]")
C("total_annual_income", "Total annual income (Rs)", "Work income plus inward remittances. Outward remittances are not subtracted.", "yatra_income + non_yatra_income + remittance_inward_annual", "money")
C("yatra_income_share", "Share of annual income from Yatra months", "Yatra income divided by total annual income (an Exposure covariate in the VEP model).", "yatra_income / total_annual_income")
C("income_seasonality_cv", "Income seasonality: CV of the 12 monthly earnings", "Calendar path: coefficient of variation across the twelve reported monthly earnings (n-1 divisor). Fallback path: the same CV computed on a two-level series -- income_pm_yatra_eq in each Yatra month, income_pm_other_eq in each other month -- so the variable is never missing and no respondent silently drops out of the FGLS for want of it. IMPORTANT: the fallback series has no within-season variation by construction, so its CV captures only the between-season swing and is a LOWER BOUND on true seasonality. Always run the VEP arms with income_from_fallback interacted or split; do not treat the two paths as the same measurement.",
  "calendar: rowsd(income_m1..12)/rowmean(income_m1..12); fallback: CV of the two-level series built from income_pm_yatra_eq and income_pm_other_eq over yatra_months and 12-yatra_months",
  source="Azeem et al. 2016; Khandker 2012; Dercon and Krishnan 2000")
CSEAS = ("Workers are migrants, so a consumption module fielded during the Yatra season cannot be treated as "
         "representative of the whole year. Every seasonal item (module E, 9 pairs) is combined the same way: "
         "Yatra-season months at the Yatra-season usual amount, other months at the off-season usual amount, "
         "then divided by 12 for a monthly-equivalent figure -- the same weighting already used for income.")
for _nm, _lab in [("staples", "Staples"), ("perishables", "Perishables"), ("food_own", "Home-grown/gifted food"),
                  ("food_out", "Food eaten outside"), ("fuel", "Fuel and light"), ("routine_misc", "Toiletries/consumables"),
                  ("transport_comm", "Transport/communication"), ("rent", "Rent"), ("med_nonhosp", "Medical, non-hospital"), ("packaged_food", "Packaged snacks and drinks"), ("pan_tobacco", "Pan, tobacco and intoxicants")]:
    C(f"cons_{_nm}_pm", f"{_lab}, annual-average month (Rs)", f"{_lab} spending, weighted by the length of the Yatra season and the rest of the year.",
      f"(yatra_months*cons_{_nm}_yatra_pm + (12-yatra_months)*cons_{_nm}_offseason_pm)/12", "money", source=CSEAS)
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
C("n_children_u15", "Household children under 15", "The two asked bands added: children under 6 plus children aged 6 to 14. Asked directly until 2026-10-01, alongside the 6-to-14 count that is a subset of it -- which made the respondent subtract one from the other and let the two contradict. Two disjoint bands partition it exactly, so this is now arithmetic and the contradiction cannot arise.", "n_children_u6 + n_children_6_14", "count", source="Adult-equivalent scales (Claro et al. 2010; Awuni et al. 2023)")
C("cons_pc_ae_pm", "Consumption per adult equivalent per month (Rs)", "Household consumption divided by (adults + 0.5 x children under 15), where adults = household size minus children under 15. One simple scale; the choice of scale is a sensitivity check.",
  "total_cons_pm / (hhsize - n_children_u15 + 0.5*n_children_u15)", "money", source="Adult-equivalent practice (Awuni et al. 2023; Claro et al. 2010 on per-capita versus adult-equivalent)")
C("poverty_line", "Poverty line applying to this respondent (Rs per capita per month)", "Sethu, Surya and Ruthu (2024) construct TWO lines for 2022-23 by the Rangarajan method: Rs 2,515 per capita per month rural and Rs 3,639 urban. Which applies is decided by home_rural_urban -- the respondent's USUAL place of residence, not the Yatra worksite. Until this variable existed the build applied the rural line to everyone, which measured urban-resident workers against a line 31 percent too low and understated their poverty.", "2515 if home_rural_urban==1, else 3639", "money", source="Sethu, Surya and Ruthu 2024 (Rangarajan method on HCES 2022-23), both lines")
C("poor", "Poor: consumption below the applicable line", "1 if per-capita monthly consumption is below the rural or urban line that applies to this respondent.", "cons_pc_pm < poverty_line", "bin", "yn", source="Sethu, Surya and Ruthu 2024")
C("poor_sensitivity_cpi", "Poor on the Rs 1,850 line (sensitivity)", "1 if below the Rangarajan and Dev 2024 CPI-adjusted line; robustness only.", "cons_pc_pm < 1850", "bin", "yn", source="Rangarajan and Dev 2024")
C("durables_count", "Number of durables owned (0-6, legacy)", "Legacy six-item count kept only so earlier outputs stay reproducible. DO NOT use for the MPI: the asset indicator is mpi_asset_deprived, which applies NITI's actual rule to its actual eight-item list.", "owns_tv + owns_radio + owns_bicycle + owns_motorcycle + owns_car + owns_fridge", "count")
C("productive_assets_count", "Number of productive/livelihood assets owned (0-6)", "Sum of the six productive-asset binaries (livestock, pony/mule, shop/stall, work vehicle, work equipment).",
  "owns_cow_buffalo + owns_goat_sheep + owns_pony_mule + owns_shop_stall + owns_work_vehicle + owns_work_equipment", "count")
C("water_deprived", "MPI: deprived on drinking water", "NITI rule, BOTH limbs: deprived if the source is unimproved (codes 7-9), OR the source is improved but the round trip to fetch it takes over 30 minutes. The second limb could not be evaluated at all before water_on_premises and water_fetch_minutes existed.", "inrange(drinking_water,7,9) | (water_on_premises==0 & water_fetch_minutes>30)", "bin", "yn", source="NITI Aayog National MPI drinking-water indicator")
C("cooking_fuel_deprived", "MPI: deprived on cooking fuel", "NITI rule: deprived if the household cooks with firewood, dung, crop residue/shrubs, charcoal or coal (codes 6-10). Kerosene (5) is NOT counted, because NITI's own list does not name it; the global MPI does count it, so this is a documented departure and the raw fuel code is retained so either rule can be applied later.", "inlist(cooking_fuel,6,7,8,9,10)", "bin", "yn", source="NITI Aayog National MPI cooking-fuel indicator")
C("mpi_asset_count", "Number of the eight NITI small assets owned (0-8)", "Radio, TV, telephone, computer, animal cart, bicycle, motorbike, refrigerator -- NITI's own list. Car or truck is NOT in this count; it is a separate limb of the indicator.", "owns_radio + owns_tv + owns_phone + owns_computer + owns_animal_cart + owns_bicycle + owns_motorcycle + owns_fridge", "count", source="NITI Aayog National MPI assets indicator")
C("mpi_asset_deprived", "MPI: deprived on assets", "NITI rule exactly: deprived if the household does not own MORE THAN ONE of the eight small assets AND does not own a car or truck. The previous version summed six assets into a plain count, which is not NITI's rule and is not comparable to any published National MPI figure.", "mpi_asset_count <= 1 & owns_car == 0", "bin", "yn", source="NITI Aayog National MPI assets indicator")
C("child_school_dep", "MPI: school-age child not attending", "1 if any child aged 6 to 14 is not attending school; missing if no such child.", "n_children_out_school > 0 if n_children_6_14 > 0", "bin", "yn", source="NITI Aayog National MPI")
# ---- shocks and coping: the check-all exports split into binaries ---------------------------
# Code 9 is "nothing of this kind happened" -- the escape option on a required multi-select, not a
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
C("shock_covariate", "Suffered a COVARIATE shock", "1 if any of: natural disaster, road or bridge blocked, Yatra stopped or disrupted, sharp fall in customers or prices (codes 3, 5, 6, 7). These hit the whole route at once, so they are the shocks a ropeway -- or a flood year -- delivers to everyone simultaneously. Separating them from idiosyncratic shocks is what makes the covariate/idiosyncratic variance decomposition identifiable.", "any of shock_3 shock_5 shock_6 shock_7", "bin", "yn", source="Gunther and Harttgen 2009, via Fujii 2016 section 2.2")
C("shock_idiosyncratic", "Suffered an IDIOSYNCRATIC shock", "1 if any of: illness or death of an earning member, crop or livestock loss, loss of business or assets, lost the work (codes 1, 2, 4, 8). These hit one household at a time.", "any of shock_1 shock_2 shock_4 shock_8", "bin", "yn", source="Gunther and Harttgen 2009, via Fujii 2016 section 2.2")
C("coped_sold_assets", "Coped by selling or pawning assets", "1 if selling or pawning assets was among the responses. Kept as its own variable because the asset-smoothing test compares it directly against cutting consumption, and the two are no longer mutually exclusive.", "cope_3", "bin", "yn", source="Carter and Zimmerman 2000")
C("coped_cut_consumption", "Coped by cutting consumption", "1 if cutting consumption was among the responses. See coped_sold_assets -- a household doing BOTH, or cutting consumption precisely in order to avoid selling, is the case the single-answer item could not represent.", "cope_4", "bin", "yn", source="Carter and Zimmerman 2000; Zimmerman and Carter 2003")
# ---- NITI Aayog National MPI: the indicators, at NITI's own weights -------------------------
# Health 1/3 = Nutrition 1/6 + Child & Adolescent Mortality 1/12 + Maternal Health 1/12
# Education 1/3 = Years of Schooling 1/6 + School Attendance 1/6
# Standard of Living 1/3 = seven indicators at 1/21 each
# NUTRITION IS NOT COLLECTED -- it requires anthropometry. Its 1/6 is therefore redistributed
# across the remaining eleven in proportion to their own weights, and the resulting index MUST be
# reported as an ELEVEN-of-twelve-indicator adaptation, not as the National MPI. See
# mpi_nutrition_proxy_dep and mpi_score_lyons below for the substituted companion score.
C("mpi_mortality_dep", "MPI: child or adolescent mortality", "NITI: a child or adolescent under 18 died in the household in the last five years.", "child_death_5y == 1", "bin", "yn", source="NITI Aayog National MPI (1/12)")
C("mpi_maternal_dep", "MPI: maternal health", "NITI: a woman who gave birth in the last five years did not have at least four antenatal visits for the most recent birth, OR was not assisted by trained personnel at that birth. Households with no birth in the window are NOT deprived, per NITI's own treatment.", "birth_last_5y==1 & (anc_4_visits!=1 | skilled_birth_attendant!=1)", "bin", "yn", source="NITI Aayog National MPI (1/12)")
C("mpi_schooling_dep", "MPI: years of schooling", "NITI: not even one household member aged 10 or older has completed six years of schooling.", "any_member_6yr_schooling == 0", "bin", "yn", source="NITI Aayog National MPI (1/6)")
C("mpi_attendance_dep", "MPI: school attendance", "NITI: any school-aged child is not attending school up to the age at which they would complete class 8. Not deprived where the household has no child in that range.", "n_children_out_school > 0 if n_children_6_14 > 0", "bin", "yn", source="NITI Aayog National MPI (1/6)")
C("mpi_housing_dep", "MPI: housing", "NITI: the floor is natural material, OR the roof OR the wall is rudimentary. All three limbs are now collected; the wall limb was previously missing entirely.", "floor_material==1 | roof_material==1 | wall_material==1", "bin", "yn", source="NITI Aayog National MPI (1/21)")
C("mpi_sanitation_dep", "MPI: sanitation", "NITI: unimproved or no facility, OR improved but shared with other households.", "inlist(toilet_type,1,2,3)", "bin", "yn", source="NITI Aayog National MPI (1/21)")
C("mpi_electricity_dep", "MPI: electricity", "NITI: the household has no electricity.", "electricity == 0", "bin", "yn", source="NITI Aayog National MPI (1/21)")
C("mpi_bank_dep", "MPI: bank account", "NITI: no household member has a bank account or a post office account.", "has_bank_account == 0", "bin", "yn", source="NITI Aayog National MPI (1/21)")
C("mpi_score", "MPI deprivation score (11 of NITI's 12 indicators, reweighted)", "Weighted sum of the eleven collected indicators -- mortality, maternal health, years of schooling, school attendance, cooking fuel, sanitation, drinking water, electricity, housing, assets and bank account. Nutrition (1/6) cannot be collected without anthropometry, so the remaining weights are scaled up proportionally to sum to 1. REPORT THIS AS AN ADAPTATION, never as the National MPI, and name the absent indicator. mpi_score_lyons is the companion that substitutes rather than omits. (The label said TEN until 2026-10-01; eleven of the twelve are collected, and the formula always summed eleven.)",
  "(1/12*mortality + 1/12*maternal + 1/6*schooling + 1/6*attendance + 1/21*(fuel+sanitation+water+electricity+housing+assets+bank)) / (1 - 1/6)", "num", source="NITI Aayog National MPI structure, nutrition omitted")
C("mpi_poor", "MPI-poor (deprivation score at or above 1/3)", "Alkire-Foster identification at the standard k = 33.3 percent cutoff.", "mpi_score >= 1/3", "bin", "yn", source="Alkire and Foster 2011; NITI Aayog National MPI")
C("rcsi_yatra_wk", "rCSI, Yatra-season usual week", "Weighted sum of the five Yatra-season food-coping day-counts, standard WFP weights (1,2,1,1,3).",
  "cope_less_pref_food_yatra_wk + 2*cope_borrow_food_yatra_wk + cope_reduce_meals_yatra_wk + cope_reduce_portion_yatra_wk + 3*cope_restrict_adult_yatra_wk",
  "count", source="WFP reduced Coping Strategy Index")
C("rcsi_offseason_wk", "rCSI, off-season usual week", "Weighted sum of the five off-season food-coping day-counts, standard WFP weights (1,2,1,1,3).",
  "cope_less_pref_food_offseason_wk + 2*cope_borrow_food_offseason_wk + cope_reduce_meals_offseason_wk + cope_reduce_portion_offseason_wk + 3*cope_restrict_adult_offseason_wk",
  "count", source="WFP reduced Coping Strategy Index")
C("rcsi_score", "Reduced Coping Strategy Index (rCSI), annual average", "Yatra-season and off-season weekly rCSI, weighted by the length of each season from the work calendar -- the same weighting already used for income and consumption.",
  "(yatra_months*rcsi_yatra_wk + (12-yatra_months)*rcsi_offseason_wk)/12",
  "num", source="WFP reduced Coping Strategy Index; season-weighting as in Module E/C")
C("food_coping_deprived", "Food-coping deprived (rCSI above 20)", "1 if annual-average rCSI exceeds 20, the cutoff used by Lyons et al. 2023 (from VASyR).", "rcsi_score > 20", "bin", "yn", source="Lyons et al. 2023 Table 2 indicator 3 cutoff")
C("shock_earnings_lost", "Earnings lost to the worst shock, at measured wages (Rs)", "Weeks of work lost times the respondent's own weekly earnings in the season the shock fell in -- Yatra-season weekly earnings if shock_month is inside the measured season, off-season weekly earnings otherwise. The respondent is never asked to value his own forgone work: he reports the weeks, and the wage is the one this instrument already measured from him.", "shock_work_lost_weeks * (season-matched weekly earnings)", "money", source="Project design (the time limb of shock magnitude, valued at measured earnings)")
C("shock_loss_total", "Total cost of the worst shock: earnings lost plus money spent (Rs)", "The two limbs added. This is what shock_loss_amount used to ask the respondent to add up in his head -- including valuing his own lost work -- and it replaces it everywhere, including in shock_loss_share. Report the limbs separately too: a shock that costs only time and a shock that costs only cash are different events for a household with no savings.", "shock_earnings_lost + shock_money_spent", "money", source="Ligon and Schechter 2003; Dercon and Krishnan 2000")

# ---- NITI Nutrition: the one indicator this instrument cannot collect, and the substitute ----
# NITI defines Nutrition (weight 1/6) on ANTHROPOMETRY -- measured height, weight and BMI for
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
C("mpi_nutrition_proxy_dep", "MPI nutrition SUBSTITUTE: food-coping deprived (not anthropometry)", "food_coping_deprived, standing in for NITI's Nutrition indicator in mpi_score_lyons only. NOT a measure of undernourishment and must never be labelled as one: it is the Lyons et al. (2023) food-coping indicator, rCSI above 20, occupying the 1/6 weight NITI gives to a measurement this instrument cannot take.", "food_coping_deprived == 1", "bin", "yn", source="Lyons et al. 2023 Table 2 indicator 3, substituted for NITI Aayog Nutrition (1/6); Alkire and Foster 2011 on indicator substitution")
C("mpi_score_lyons", "MPI deprivation score, 12 of 12 with the Lyons food-coping substitute", "All twelve NITI weights filled, with the food-coping indicator in the Nutrition slot at 1/6 and no reweighting. Report alongside mpi_score, never instead of it, and state the substitution.", "mpi_score with (1/6)*mpi_nutrition_proxy_dep in place of the reweighting", "num", source="NITI Aayog National MPI structure; Lyons et al. 2023 nutrition substitute")
C("mpi_poor_lyons", "MPI-poor under the substituted score (score at or above 1/3)", "Alkire-Foster identification at k = 33.3 percent on mpi_score_lyons. The gap between this headcount and mpi_poor is the sensitivity of the result to the nutrition substitution.", "mpi_score_lyons >= 1/3", "bin", "yn", source="Alkire and Foster 2011; NITI Aayog National MPI")
C("hours_week_yatra", "Hours worked per week in the Yatra season", "Hours per day times days per week.", "hours_day_yatra * days_week_yatra", "count", source="Apablaza et al. 2026 Q13 (decomposed into hours/day x days/week when asked, for ease of recall)")
C("hours_week_offseason", "Hours worked per week outside the Yatra season", "Hours per day times days per week, off-season. Missing for respondents with no off-season paid work at all.", "hours_day_offseason * days_week_offseason", "count", source="Apablaza et al. 2026 Q13")
C("hours_week_annual", "Average weekly hours across the months actually worked", "Yatra-season and off-season weekly hours, weighted by how many months of each the calendar records. Averaged over WORKED months only, so idle months do not drag the figure to zero -- idleness is measured by months_no_work, and counting it here too would penalise it twice.", "(yatra_months*hours_week_yatra + offseason_months_worked*hours_week_offseason) / (yatra_months + offseason_months_worked)", "num", source="Apablaza et al. 2026 Q13, weighted onto the work calendar")
C("work_income_pm", "Average monthly work income over the year (Rs)", "(Yatra income + other work income) divided by 12.", "(yatra_income + non_yatra_income)/12", "money", source="Apablaza et al. 2026 Q14")
KS = "Apablaza et al. 2026, Table 3 (five-domain core; thresholds from the table, inputs from Appendix 2)"
C("emp_dep_access", "Employment deprivation: access", "1 if idle more than 6 months and spent any weeks looking for work, or wants more work while working under 20 hours a week in EITHER season. The under-20 limb previously tested Yatra-season hours only, where this workforce runs 60-90 hours a week, so it could never fire and the indicator collapsed onto its other limb.", "(months_no_work>6 & weeks_looked_for_work>0) | (wants_more_work==1 & (hours_week_yatra<20 | hours_week_offseason<20))", "bin", "yn", source=KS + ": unemployed >6 months OR <20 h/week involuntary")
C("emp_dep_comp", "Employment deprivation: compensation", "1 if average monthly work income is below 67 percent of the sample median (the fallback threshold in Table 3).", "work_income_pm < 0.67 * median(work_income_pm)", "bin", "yn", source=KS + ": fallback <67% of median; the PPP-line version needs a checked conversion factor")
C("emp_dep_sec", "Employment deprivation: security", "1 if a wage worker has no signed contract, or a self-employed worker's business is not registered.", "wage: contract_status != 1; self-employed: workplace_registered == 0", "bin", "yn", source=KS + ": no written contract (registration for the self-employed)")
C("emp_dep_stab", "Employment deprivation: stability", "Apablaza Table 3 sets TWO tenure thresholds -- wage workers deprived under 6 months, self-employed under 12 months -- where this file previously applied a single under-1-year rule to everyone, which marked wage workers with 6 to 12 months of tenure as deprived when Table 3 would not. Tenure here is counted in Yatra SEASONS, and one season is roughly six months of work, so the two thresholds map cleanly onto under 1 season for wage workers and under 2 for the self-employed. The casual-job limb is an ADDITION to Table 3, whose fallback (temporary/casual) is meant for use only when tenure is unavailable; it is kept because occasional work is a real instability here, but note it covers code 3 only -- code 2 (seasonal) would mark almost this entire sample deprived and would measure the season, not the job.", "wage (employment_type 3/4): years_in_yatra_work < 1; self-employed (1/2): < 2; OR job_permanence == 3", "bin", "yn", source=KS + ": tenure, wage <6mo and self-employed <12mo; casual limb is a project addition")
C("emp_dep_cond", "Employment deprivation: working conditions", "1 if someone was injured or killed at the workplace in the last 12 months, or the worker has neither work health insurance nor a pension.", "workplace_injury_12m==1 | (work_health_ins==3 & pension_contrib==3)", "bin", "yn", source=KS + ": hazards OR (no health insurance AND no pension); injury is the hazard evidence in Appendix 2")
C("emp_dep_count", "Employment deprivations (count of 5)", "Number of the five employment indicators in which the worker is deprived.", "sum of the five emp_dep_ indicators", "count", source=KS)
C("emp_dep_score", "Employment deprivation score (equal weights, 0-1)", "Count divided by 5.", "emp_dep_count / 5", "num", source=KS)
C("emp_poor_k2", "Employment-poor: deprived in 2 or more of 5", "1 if two or more indicators; k = 2 of 5 is the project's choice, to be varied in robustness.", "emp_dep_count >= 2", "bin", "yn", source=KS + "; cut-off is the project's choice")
C("tk_regular_n", "Number of the 12 tasks done regularly", "Count of task answers equal to 1.", "count of tk_* == 1", "count")
C("tk_prior_n", "Number of the 12 tasks done before elsewhere", "Count of task answers equal to 2.", "count of tk_* == 2", "count")

# ---- multiple work-holding: the check-all list, split into binaries -------------------------
for _k, _lab in sorted(LSETS["occ"].items()):
    C(f"other_act_{_k}", f"Other activity: {_lab}"[:80], f"1 if '{_lab}' was ticked in the check-all list of other paid activities.",
      f"other_activity_types contains {_k}", "bin", "yn", source="Split from the select_multiple export")
C("n_other_act_checked", "Number of other activities actually ticked", "Count of the boxes ticked in the check-all list. Compared against the respondent's own count (n_other_activities); a mismatch is a data-quality flag, not a silent loss.",
  "sum of other_act_1..13", "count")
C("other_act_mismatch", "Ticked count differs from the stated count", "1 if the number of activities ticked does not equal the number the respondent said they had. Expected to be small; if it is not, the item needs rewording before scale-up.",
  "n_other_act_checked != n_other_activities", "bin", "yn")

# ---- ex-ante direction of the required skill move (Nawakitphaitoon and Ormiston 2016) --------
# Ormiston transferability is ASYMMETRIC: t_ij (share of i's skills usable in j) is not t_ji (share
# of j's requirements i already has), and N&O read the asymmetry as direction -- "higher
# transferability rates should accompany worker movement from entry-level jobs to more advanced
# positions. In contrast, occupational switches from complex to simple jobs result in the
# obsolescence of previously applicable skills." So the pair (coverage, retention) classifies what
# KIND of retraining a move needs, before anyone moves. No extra question: both come from the task
# grid already asked. Computed here against the closest of the 13 occupations in this survey; the
# tasks_module repeats it against the wider regional destination set and the ropeway jobs.
TRANSNOTE = ("Worker's own task profile uses codes 1 AND 2 (does it now, or has done it before "
             "elsewhere) -- prior capability outside the current job is exactly what a transfer "
             "question is about. Destination profiles are the occupation-level share of workers "
             "doing each task (Gathmann and Schonberg's q_oj).")
C("best_alt_occupation", "Closest alternative occupation in task space", "Of the 13 occupations, the one (other than the respondent's own) whose task profile is closest to the respondent's. " + TRANSNOTE,
  "argmax over j != own occupation of cosine(worker profile, q_j)", "cat", "occ", source="Gathmann and Schonberg 2010")
C("task_cover_best", "Share of the closest alternative's tasks the worker already does", "Coverage: of the tasks that alternative occupation requires, the share this worker can already perform. Ormiston's t_ji direction -- can the worker step in?",
  "sum(q_best * worker) / sum(q_best)", source="Nawakitphaitoon and Ormiston 2016 (Ormiston 2014 transferability)")
C("task_retain_best", "Share of the worker's own tasks the closest alternative uses", "Retention: of the tasks this worker can perform, the share that alternative occupation would actually use. Ormiston's t_ij direction -- how much of their skill survives the move?",
  "sum(q_best * worker) / sum(worker)", source="Nawakitphaitoon and Ormiston 2016 (Ormiston 2014 transferability)")
C("skill_move_type", "Ex-ante type of skill move required", "Direction of the move implied by the coverage/retention pair, both split at 0.5: high-high lateral (move needs little retraining); low coverage but high retention means the destination needs skills the worker lacks while their own still count, i.e. UPSKILLING; high coverage but low retention means the worker has more than the destination uses and much of it goes idle, i.e. DOWNSKILLING; low-low means the skill sets barely overlap, i.e. RESKILLING. " + TRANSNOTE,
  "from (task_cover_best, task_retain_best), each split at 0.5", "cat", "movetype", source="Nawakitphaitoon and Ormiston 2016, section 2.2 (asymmetry of T_ij read as direction)")

# ------------------------------------------------------------------ BUILD STAMP
# The build stamp: today's date plus a short hash of the asked question set. Shown in the web form's
# header and written into every exported row as form_build, so a field report can be matched to the
# form that produced it -- a service worker can serve a stale copy of the page indefinitely, and a
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
