# Kedarnath Yatra Worker Survey — Interview Script (English)

> Read the plain text aloud, exactly as written. Indented blocks marked **ENUMERATOR** are for you only — never read them out. Choice lists are not read aloud unless the respondent is struggling; ask the question, listen, and code the closest option.

## Consent

We are doing a study on the livelihoods of people who work on the Yatra route. I would like to ask you some questions about your work, your household and your spending.

Taking part is your choice. You can stop at any time, and you can skip any question you do not want to answer. Nothing you tell me will be linked to your name, and nothing you say will affect your work here or any government benefit.

If you say no, I will not ask you any questions. I will write down only that you said no, the date and time, and what was happening at the time, such as crowding or weather. I will not write down your name, your sex, your age, or where you are. No answers are recorded.

> **ENUMERATOR:** If they say no, thank them and stop.


---

## Module A — Respondent and household

First, a few things about you and the people who live in your household.

**1.** How old are you? (completed years)

> **ENUMERATOR:** Record: number

**2.** Record sex; ask if unsure: are you male or female?

> **ENUMERATOR:** Options: 0 Male · 1 Female

**3.** Who is the head of your household — is it you, or someone else? If someone else, how are they related to you?

> **ENUMERATOR:** Options: 1 Self (respondent is the head) · 2 Husband · 3 Wife · 4 Father · 5 Mother · 6 Son · 7 Daughter · 8 Brother · 9 Sister · 10 Other male relative · 11 Other female relative · 12 Other, non-relative (male) · 13 Other, non-relative (female)

**4.** What is your native language, the language you first learned at home?

> **ENUMERATOR:** Options: 1 Garhwali · 2 Kumaoni · 3 Hindi · 4 Nepali · 5 Bhojpuri · 6 Assamese · 7 Bengali · 8 Bodo · 9 Dogri · 10 Gujarati · 11 Kannada · 12 Kashmiri · 13 Konkani · 14 Maithili · 15 Malayalam · 16 Manipuri (Meitei) · 17 Marathi · 18 Odia · 19 Punjabi · 20 Sanskrit · 21 Santali · 22 Sindhi · 23 Tamil · 24 Telugu · 25 Urdu · 96 Other Indian language · 97 Other / foreign language

**5.** Which language is it? Write down exactly what they say.

> ⚠️ **IMPORTANT** — DO NOT skip this. The language list is long but India is longer. If their language is not on it, type what they actually say -- this item stands in for caste, and a bare "other" loses it for this respondent.

> **ENUMERATOR:** Ask only if: native_language is 96 (other Indian language) or 97 (other / foreign language)  
> Record: write the answer in words, verbatim

**6.** Where is your permanent home?

> **ENUMERATOR:** Options: 1 Local (same district) · 2 Other Uttarakhand district · 3 Other Indian state · 4 Nepal

**7.** Which state or union territory is your permanent home in?

> **ENUMERATOR:** Options: 1 Andhra Pradesh · 2 Arunachal Pradesh · 3 Assam · 4 Bihar · 5 Chhattisgarh · 6 Goa · 7 Gujarat · 8 Haryana · 9 Himachal Pradesh · 10 Jharkhand · 11 Karnataka · 12 Kerala · 13 Madhya Pradesh · 14 Maharashtra · 15 Manipur · 16 Meghalaya · 17 Mizoram · 18 Nagaland · 19 Odisha · 20 Punjab · 21 Rajasthan · 22 Sikkim · 23 Tamil Nadu · 24 Telangana · 25 Tripura · 26 Uttar Pradesh · 28 West Bengal · 29 Andaman and Nicobar Islands · 30 Chandigarh · 31 Dadra and Nagar Haveli and Daman and Diu · 32 Delhi · 33 Jammu and Kashmir · 34 Ladakh · 35 Lakshadweep · 36 Puducherry

**8.** Is that home in a village, or in a town or city?

> **ENUMERATOR:** Options: 1 Village (rural) · 2 Town or city (urban)

**9.** Are you currently married, never married, or widowed/divorced/separated?

> **ENUMERATOR:** Options: 1 Currently married · 2 Never married · 3 Widowed/divorced/separated

**10.** Do you know exactly how many years of schooling you completed, counting from class 1?

> **ENUMERATOR:** Options: 0 No · 1 Yes  
> How to code: A level is NOT a No. If they answer '8th', '12th pass', 'ITI', 'BA', 'MA' — code YES and convert it on the next screen. Code No only if they cannot say how far they went at all.

**11.** How many years of schooling did you complete in total? (0 if none)

> **ENUMERATOR:** Ask only if: knows_years_schooling = 1  
> Record: whole number  
> How to code: Enter a NUMBER counted from class 1, never a level. Class 1 to 12 = that class number. ITI or diploma after 10th = 12. Bachelors = 15, or 16 if the course ran four years — ASK how long it ran. Masters = 17, or 18 after a four-year bachelors. If they dropped out part way through a year, count the completed years only.

**12.** Which is closest: no formal education; some schooling but did not finish primary; finished primary but not secondary; or finished secondary or higher?

> **ENUMERATOR:** Ask only if: knows_years_schooling = 0  
> Options: 1 No formal education · 2 Some schooling, did not complete primary · 3 Completed primary but not secondary · 4 Completed secondary or higher · 98 Prefer not to say

**13.** Apart from school and college, have you ever completed any training course or apprenticeship?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**14.** How many members live in your household, including you?

> **ENUMERATOR:** Record: whole number

**15.** Counting everyone in your household aged 10 or above, has at least one of them finished six years of schooling or more?

> **ENUMERATOR:** Ask only if: the respondent's own schooling does not already settle it: years_schooling < 6, or the bracket is not 'completed secondary or higher'  
> Options: 0 No · 1 Yes  
> How to code: The respondent is himself a household member. If HE has six years or more the answer is Yes — do not send him looking for someone else. The screen is skipped automatically wherever his own answer already settles it.

**16.** How many of them are children under 6 years old?

> **ENUMERATOR:** Record: whole number

**17.** And how many are aged 6 to 14?

> **ENUMERATOR:** Record: whole number

**18.** How many of these children go to school now?

> **ENUMERATOR:** Ask only if: n_children_6_14 > 0  
> Record: whole number

**19.** How many of them, including you, earn money?

> **ENUMERATOR:** Record: whole number

**20.** Among those who earn money, are you the main income earner in your household?

> **ENUMERATOR:** Ask only if: n_earners > 1 (if the respondent is the only earner, this is automatic)  
> Options: 0 No · 1 Yes

> _Module A complete._


---

## Module B — Work and work history

Now about the work you do here on the Yatra route, and the work you did before this.

**21.** What is your main work during the Yatra season? Ask what they do and code the closest group; do not read the list aloud unless needed.

> **ENUMERATOR:** Options: 1 Pony/mule worker (works the animals, does not own them) · 2 Pony/mule owner (owns the animals) · 3 Porter (carries on own back/shoulders - goods, luggage, or a person in a kandi) · 4 Palki / dandi bearer (carries a person on a palanquin, as part of a team) · 5 Dhaba, tea stall or food stall WORKER (prepared food or tea) · 6 Dhaba, tea stall or food stall OWNER (prepared food or tea) · 7 Shop WORKER (goods: prasad, puja items, clothes, general store) · 8 Shop OWNER (goods, not prepared food) · 9 Hotel / lodge WORKER · 10 Hotel / lodge OWNER · 11 Driver (any motor vehicle) · 12 Guide · 13 Wage labourer (construction, loading, odd jobs) · 14 Other

**22.** In your own words, what exactly is your main work here? Write down what they say — what they actually do, and who for. Do not tick a box for this one.

> ⚠️ **IMPORTANT** — The 14 groups above are deliberately coarse. THIS is the only place the real job gets recorded, and the whole skills analysis is coded from it. "Shop owner" could be a plank selling prasad or a three-storey general store -- write enough that someone who was not there can tell which.

> **ENUMERATOR:** Record: write the answer in words, verbatim  
> Write what they DO and who for, not just a job title. Include the goods or food they sell if that is the work.

**23.** In this main work, are you: working on your own account without hired workers; running a business with hired workers; a regular monthly wage-earner; or a daily/casual wage-earner?

> **ENUMERATOR:** Options: 1 Own-account (self-employed, no hired workers) · 2 Employer/business owner (self-employed) · 3 Regular wage or salary · 4 Casual or daily wage labour · 5 Unpaid family worker

**24.** Who employs you? A private company; a government or public body; a household (domestic work); a contractor or agent; or an individual employer?

> **ENUMERATOR:** Ask only if: employment_type is 3 or 4 (regular or casual wage worker)  
> Options: 1 Private company · 2 Government or public body · 3 A household (domestic work) · 4 A contractor or agent · 5 An individual employer · 97 Don't know  
> How to code: ENUMERATOR: private company = a registered firm or hotel chain; government or public body = a government department, Yatra board, PWD or other public office; household = a family that hires them for domestic work; contractor or agent = a thekedar or agent who arranged and pays for the work; individual employer = one person who pays them directly, such as a shop or dhaba owner. If the respondent says 'the owner' or 'the boss' without more, ask who arranged the job. If they came through an agent (see the migration referral question), code 4. If unsure, code 97 and write the words in the notes.

**25.** Besides your main work, what other paid work do you do during the Yatra season? Check every one that applies; leave blank if there is none. Ask and code the closest group for each; do not read the list aloud unless needed.

> **ENUMERATOR:** Ask only if: May be left blank  
> select all that apply: 1 Pony/mule worker (works the animals, does not own them) · 2 Pony/mule owner (owns the animals) · 3 Porter (carries on own back/shoulders - goods, luggage, or a person in a kandi) · 4 Palki / dandi bearer (carries a person on a palanquin, as part of a team) · 5 Dhaba, tea stall or food stall WORKER (prepared food or tea) · 6 Dhaba, tea stall or food stall OWNER (prepared food or tea) · 7 Shop WORKER (goods: prasad, puja items, clothes, general store) · 8 Shop OWNER (goods, not prepared food) · 9 Hotel / lodge WORKER · 10 Hotel / lodge OWNER · 11 Driver (any motor vehicle) · 12 Guide · 13 Wage labourer (construction, loading, odd jobs) · 14 Other  
> How to code: ENUMERATOR: hauling luggage or goods on the back, shoulders or a head-load, for pilgrims or shops, is code 3 (porter). Carrying a person in a kandi is also code 3; carrying a person on a palanquin as part of a team is code 4. Hauling luggage or goods on a pony or mule is code 1 if the respondent works the animal for someone else, and code 2 if they own it.

**26.** Taking all of that other work together, about how much do you usually earn from it in a month? (Rs; leave blank if there is no other work)

> **ENUMERATOR:** Ask only if: May be left blank  
> Record: amount in rupees, whole number

**27.** Does your household own a shop or stall that you use to earn?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**28.** During one Yatra season, how many different employers or businesses do you work in? (1 if you stay with the same one, or run the same one, all season)

> **ENUMERATOR:** Record: whole number

**29.** How many years have you been in this work? Write it as a decimal if needed, for example 1.5 for one year and six months, or 0.5 for six months.

> **ENUMERATOR:** Record: number  
> How to code: ENUMERATOR: only if the person has been in this job one year or more. Write the number of years; use a decimal for part years (1.5 = one year and six months).

**30.** In the Yatra season, on a normal working day, how many hours do you work in total, across all your work?

> **ENUMERATOR:** Record: whole number

**31.** How many days a week do you usually work in the season?

> **ENUMERATOR:** Record: whole number

**32.** In the last ten years, did you change your main kind of work?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**33.** What was your previous main work? Write down exactly what they say, in their words — do not pick from a list.

> **ENUMERATOR:** Ask only if: prev_occ_change = 1  
> Record: write the answer in words, verbatim  
> Write it in their words. If they name a place or an employer, write that too.

**34.** Looking ahead a few years, what work would you like to be doing? Write down exactly what they say, in their words — do not pick from a list, and do not prompt with examples. If they want to carry on exactly as they are, write that.

> **ENUMERATOR:** Record: write the answer in words, verbatim  
> Do not suggest anything. "Don't know" and "there is no other work for me" are real answers — write them down as said.

**35.** What was the main reason you changed?

> **ENUMERATOR:** Ask only if: prev_occ_change = 1  
> Options: 1 Better income · 2 Lost the previous work · 3 Work ended with the season · 4 Family reasons · 5 Health or injury · 6 Other

> _Module B complete._


---

## Module C — Monthly calendar of work and income

Now I want to go through the last twelve months, one month at a time. For each month I will ask what work you were mainly doing, and then what you usually earned. It is easiest to start with the Yatra months and fill the rest afterwards.

**36.** In the past year, how many months did you work here in the Yatra season? Count the months you spent getting ready for it as well.

> **ENUMERATOR:** Record: whole number

**37.** And in the past year, how many months did you have no paid work at all?

> **ENUMERATOR:** Record: whole number

**38.** In the remaining months — not the Yatra season, and not the months with no work — what was your main work? Code the closest one.

> **ENUMERATOR:** Ask only if: May be left blank if the Yatra months and the idle months already account for all twelve  
> Options: 2 Farming (crops) · 3 Livestock (animals) · 4 Casual or daily wage labour · 5 Construction work · 6 Own small shop, stall or trade · 7 Salaried job · 96 Some other work · 0 There were no such months

**39.** Thinking of the whole past year, about how much did you earn in total from all your work, after costs? (Rs)

> **ENUMERATOR:** Ask only if: May be left blank if the respondent declines to discuss earnings  
> Record: amount in rupees, whole number

**40.** Out of every 100 rupees of that, how many came from your Yatra work? (The rest is counted as coming from your other work.)

> **ENUMERATOR:** Ask only if: income_annual_total was given; may be left blank  
> Record: whole number

**41.** Which range is closest to what you usually earn in a month from work? Under Rs 5,000; Rs 5,000 to 10,000; Rs 10,000 to 20,000; Rs 20,000 or more; or don't know?

> **ENUMERATOR:** Ask only if: income_annual_total was left blank; may be left blank  
> Options: 1 Under Rs 5,000 · 2 Rs 5,000 to 10,000 · 3 Rs 10,000 to 20,000 · 4 Rs 20,000 or more · 97 Don't know

**42.** In the months when the Yatra is closed and you are doing other work, on a normal working day, how many hours do you work in total?

> **ENUMERATOR:** Ask only if: there are months that are neither Yatra nor idle (12 - months_worked_yatra - months_no_paid_work > 0)  
> Record: whole number

**43.** In those months, how many days a week do you usually work?

> **ENUMERATOR:** Ask only if: there are months that are neither Yatra nor idle (12 - months_worked_yatra - months_no_paid_work > 0)  
> Record: whole number

> _Module C complete._


---

## Module D — Migration, home place and remittances

Now a few questions about where your home is, and what you do when the Yatra closes for the season.

**44.** When the Yatra closes for the season, do YOU go to your home place?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**45.** For most of the year, do the rest of your household live in your home village or town?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**46.** Is the money you send home different in the Yatra season from when the Yatra is closed?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**47.** In a normal month during the Yatra season, how much money do you usually send to family or others living elsewhere? (Rs, 0 if none)

> **ENUMERATOR:** Record: amount in rupees, whole number

**48.** In a normal month when the Yatra is closed, how much do you usually send? (Rs, 0 if none)

> **ENUMERATOR:** Ask only if: remit_differs_by_season = 1  
> Record: amount in rupees, whole number

**49.** How do you usually send it?

> **ENUMERATOR:** Ask only if: remit_out_yatra_pm > 0 or remit_out_offseason_pm > 0  
> Options: 1 From my own phone (UPI or net banking) · 2 In person at a bank branch or bank mitra / CSP · 3 Money order or post office · 4 Sent with someone going home · 5 Carried it myself · 6 Through an agent or middleman · 7 Other

**50.** In a normal month during the Yatra season, how much money do you usually receive from family or others? (Rs, 0 if none)

> **ENUMERATOR:** Record: amount in rupees, whole number

**51.** In a normal month when the Yatra is closed, how much do you usually receive? (Rs, 0 if none)

> **ENUMERATOR:** Ask only if: remit_differs_by_season = 1  
> Record: amount in rupees, whole number

**52.** How many people from your household work in the same business or establishment as you, counting yourself?

> **ENUMERATOR:** Record: whole number

**53.** How many years have you been coming here for the Yatra season?

> **ENUMERATOR:** Ask only if: resp_returns_at_closure = 1  
> Record: whole number

**54.** What was the main reason you first came here to work?

> **ENUMERATOR:** Ask only if: origin is not Local (same district)  
> Options: 1 No work at home · 2 Pay is better here · 3 Family or people from my village were already here · 4 Land at home is too little to live on · 5 Debt to repay · 6 A contractor or agent brought me · 7 Married into / moved with family · 8 Some other reason

**55.** What was that reason? Write down what they say.

> **ENUMERATOR:** Ask only if: came_here_reason = 8 (some other reason). May be left blank.  
> Record: write the answer in words, verbatim

**56.** Last year, in the months when the Yatra was closed, did you work away from your home place?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**57.** Where did you go, and what work did you do there? Write what they say.

> **ENUMERATOR:** Ask only if: worked_away_in_closure = 1; may be left blank  
> Record: write the answer in words, verbatim

**58.** If this work here ended, would you go away from your home place to look for work in the coming year?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**59.** Who mainly helped you get this work, or arranged it for you?

> **ENUMERATOR:** Options: 1 A family member already working here · 2 A friend or someone from the village · 3 A thekedar or contractor I now work for · 4 An agent or middleman who placed me (usually for a fee) · 5 No one; I found it myself · 6 The employer called me directly · 7 Someone else

**60.** Who was it? Write what they say.

> **ENUMERATOR:** Ask only if: migration_referral = 7 (Other); may be left blank  
> Record: write the answer in words, verbatim

> _Module D complete._


---

## Module E — Household consumption

Now about what your household usually spends in a month. For each thing I will ask twice — once for a normal month during the Yatra season, and once for a normal month when the Yatra is closed — because spending is often quite different in the two. Rough figures are fine.

**61.** Leaving aside money you send home — is what your household spends in a normal month during the Yatra season different from what it spends when the Yatra is closed?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**62.** In a normal month during the Yatra season, how much does your household spend on cereals (rice, wheat, other grains), pulses, sugar and salt, bought or from your own stock? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

**63.** In a normal month when the Yatra is closed, how much does your household spend on cereals (rice, wheat, other grains), pulses, sugar and salt, bought or from your own stock? (Rs)

> **ENUMERATOR:** Ask only if: spend_differs_by_season = 1  
> Record: amount in rupees, whole number

**64.** In a normal month during the Yatra season, how much does your household spend on milk and milk products, vegetables, fruit, egg/fish/meat, cooking oil, spices, and tea or coffee, bought or from your own stock? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

**65.** In a normal month when the Yatra is closed, how much does your household spend on milk and milk products, vegetables, fruit, egg/fish/meat, cooking oil, spices, and tea or coffee, bought or from your own stock? (Rs)

> **ENUMERATOR:** Ask only if: spend_differs_by_season = 1  
> Record: amount in rupees, whole number

**66.** If your household had not grown, raised or been given any of your food, about how much would it have cost to buy in a normal month during the Yatra season? (Rs, 0 if you buy everything)

> **ENUMERATOR:** Record: amount in rupees, whole number

**67.** If your household had not grown, raised or been given any of your food, about how much would it have cost to buy in a normal month when the Yatra is closed? (Rs, 0 if you buy everything)

> **ENUMERATOR:** Ask only if: spend_differs_by_season = 1  
> Record: amount in rupees, whole number

**68.** In a normal month during the Yatra season, how much does your household spend on meals, tea and snacks eaten outside the home, including any an employer gave free, at their market value? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

**69.** In a normal month when the Yatra is closed, how much does your household spend on meals, tea and snacks eaten outside the home, including any an employer gave free, at their market value? (Rs)

> **ENUMERATOR:** Ask only if: spend_differs_by_season = 1  
> Record: amount in rupees, whole number

**70.** In a normal month during the Yatra season, how much does your household spend on fuel and light: cooking fuel, firewood, electricity, kerosene, candles? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

**71.** In a normal month when the Yatra is closed, how much does your household spend on fuel and light: cooking fuel, firewood, electricity, kerosene, candles? (Rs)

> **ENUMERATOR:** Ask only if: spend_differs_by_season = 1  
> Record: amount in rupees, whole number

**72.** In a normal month during the Yatra season, how much does your household spend on soap, toiletries, cleaning goods and other small household items? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

**73.** In a normal month when the Yatra is closed, how much does your household spend on soap, toiletries, cleaning goods and other small household items? (Rs)

> **ENUMERATOR:** Ask only if: spend_differs_by_season = 1  
> Record: amount in rupees, whole number

**74.** In a normal month during the Yatra season, how much does your household spend on local transport (bus, shared jeep, auto) and phone or internet charges? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

**75.** In a normal month when the Yatra is closed, how much does your household spend on local transport (bus, shared jeep, auto) and phone or internet charges? (Rs)

> **ENUMERATOR:** Ask only if: spend_differs_by_season = 1  
> Record: amount in rupees, whole number

**76.** In a normal month during the Yatra season, how much does your household spend on rent for the home (0 if owned, and 0 for any period spent living for free)? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

**77.** In a normal month when the Yatra is closed, how much does your household spend on rent for the home (0 if owned, and 0 for any period spent living for free)? (Rs)

> **ENUMERATOR:** Ask only if: spend_differs_by_season = 1  
> Record: amount in rupees, whole number

**78.** In a normal month during the Yatra season, how much does your household spend on medicine, doctor's or clinic fees and tests, not counting a hospital stay? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

**79.** In a normal month when the Yatra is closed, how much does your household spend on medicine, doctor's or clinic fees and tests, not counting a hospital stay? (Rs)

> **ENUMERATOR:** Ask only if: spend_differs_by_season = 1  
> Record: amount in rupees, whole number

**80.** In a normal month during the Yatra season, how much does your household spend on biscuits, namkeen, chips, packaged snacks, cold drinks or bottled water? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

**81.** In a normal month when the Yatra is closed, how much does your household spend on biscuits, namkeen, chips, packaged snacks, cold drinks or bottled water? (Rs)

> **ENUMERATOR:** Ask only if: spend_differs_by_season = 1  
> Record: amount in rupees, whole number

**82.** In a normal month during the Yatra season, how much does your household spend on pan, gutka, bidi, cigarettes, tobacco or alcohol? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

**83.** In a normal month when the Yatra is closed, how much does your household spend on pan, gutka, bidi, cigarettes, tobacco or alcohol? (Rs)

> **ENUMERATOR:** Ask only if: spend_differs_by_season = 1  
> Record: amount in rupees, whole number

**84.** In the last 12 months, how much did your household spend on clothes and footwear? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

**85.** In the last 12 months, how much on education: fees, books, uniforms, tuition? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

**86.** In the last 12 months, how much did your household pay for any hospital admission or stay? (Rs, 0 if none)

> **ENUMERATOR:** Record: amount in rupees, whole number

**87.** In the last 12 months, how much on durable goods: furniture, utensils, cooking appliances, phone, jewellery or ornaments, bicycle or vehicle parts? (Rs)

> **ENUMERATOR:** Record: amount in rupees, whole number

> _Module E complete._


---

## Module F — Housing, amenities and assets

Now some questions about your house and the things your household has.

**88.** What is the main material of the floor at your usual home?

> **ENUMERATOR:** Options: 1 Mud/kaccha · 2 Cement/mud-cement · 3 Tile/mosaic/marble

**89.** What is the main material of the roof at your usual home?

> **ENUMERATOR:** Options: 1 Thatch/wood/mud · 2 Tin/GI sheet · 3 Concrete/RCC

**90.** What are the walls of your usual home mainly made of?

> **ENUMERATOR:** Options: 1 Mud, thatch, bamboo or other natural material · 2 Unburnt brick, wood or tin · 3 Burnt brick, cement, concrete or stone

**91.** While you are here for the season, where do you sleep?

> **ENUMERATOR:** Options: 1 At my own usual home (I live here) · 2 Rented room or house · 3 Room or dormitory the employer provides · 4 Sleeps at the shop, dhaba or workplace · 5 Tent or temporary shelter · 6 Lodge, dharamshala or ashram · 7 In the open, or a verandah · 8 Somewhere else

**92.** Does your usual home have an electricity connection?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**93.** What kind of toilet does your household use at your usual home?

> **ENUMERATOR:** Options: 1 No toilet / open defecation · 2 Pit latrine without slab or open pit · 3 Improved toilet, but shared with other households · 4 Improved toilet, used only by this household

**94.** What is your main source of drinking water at your usual home?

> **ENUMERATOR:** Options: 1 Piped into the house or yard · 2 Public tap or standpipe · 3 Handpump, tubewell or borewell · 4 Protected well or protected spring · 5 Rainwater collection · 6 Bottled, packaged or community RO · 7 Unprotected well or unprotected spring · 8 River, stream, pond or canal · 9 Tanker truck or cart with drum

**95.** Is the drinking water available at the house itself?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**96.** How long does it take to go there, get the water and come back? (minutes, round trip)

> **ENUMERATOR:** Ask only if: water_on_premises = 0  
> Record: whole number

**97.** What does your household mainly use to cook at your usual home?

> **ENUMERATOR:** Options: 1 LPG or cylinder gas · 2 Piped natural gas · 3 Electricity · 4 Biogas (gobar gas plant) · 5 Kerosene · 6 Firewood · 7 Dung cakes (gobar) · 8 Crop residue, straw or shrubs · 9 Charcoal · 10 Coal or lignite

**98.** In what unit do you count your land — nali, bigha, acres or hectares?

> **ENUMERATOR:** Options: 1 Nali · 2 Bigha · 3 Acres · 4 Hectares · 5 No land

**99.** And how much CULTIVABLE land is that? Do not count the land the house stands on.

> **ENUMERATOR:** Record: number

**100.** Which of these does your household own? Read the list out and check every one they say: television, radio, bicycle, motorcycle or scooter, car/jeep/truck, telephone of any kind, computer or laptop, animal cart, refrigerator.

> **ENUMERATOR:** Ask only if: May be left blank if the household owns none of them  
> select all that apply: 1 Television · 2 Radio · 3 Bicycle · 4 Motorcycle or scooter · 5 Car, jeep or truck · 6 Telephone of any kind (mobile or landline) · 7 Computer or laptop · 8 Cart pulled by an animal · 9 Refrigerator

**101.** And which of these animals does your household own? Cows or buffaloes, goats or sheep, ponies or mules.

> **ENUMERATOR:** Ask only if: May be left blank if the household owns no animals  
> select all that apply: 1 Cows or buffaloes · 2 Goats or sheep · 3 Ponies or mules

**102.** Do you use a vehicle to earn money — for example hauling goods, transporting people, or running a taxi? It does not have to be yours.

> **ENUMERATOR:** Options: 0 No · 1 Yes

**103.** Does your household own equipment or tools that you use to earn?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**104.** What are they? Write what they say. Leave blank if they cannot say.

> **ENUMERATOR:** Ask only if: owns_work_equipment = 1; may be left blank  
> Record: write the answer in words, verbatim

> _Module F complete._


---

## Module G — Finance, insurance and schemes

Now about savings, loans, insurance and government schemes.

**105.** Does anyone in your household have a bank account or a post office account?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**106.** In the last 12 months, did you or anyone in your household borrow money?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**107.** Who was the main lender?

> **ENUMERATOR:** Ask only if: took_loan_12m = 1  
> Options: 1 Nationalised or public-sector bank · 2 Private bank · 3 Cooperative bank or RRB · 4 Microfinance institution or SHG · 5 Moneylender · 6 Relative or friend · 7 Employer or contractor (advance) · 8 Other

**108.** What did you take it for?

> **ENUMERATOR:** Ask only if: took_loan_12m = 1  
> Options: 1 Medical or hospital costs · 2 Buying an animal, vehicle or equipment for work · 3 Shop stock or business · 4 Food or daily household needs · 5 A wedding, funeral or ceremony · 6 House building or repair · 7 Education · 8 Repaying another loan · 9 Something else

**109.** How much did you borrow in total? (Rs)

> **ENUMERATOR:** Ask only if: took_loan_12m = 1  
> Record: amount in rupees, whole number

**110.** How much of that loan is still left to repay? (Rs)

> **ENUMERATOR:** Ask only if: took_loan_12m = 1  
> Record: amount in rupees, whole number

**111.** Do you pay interest on it?

> **ENUMERATOR:** Ask only if: took_loan_12m = 1  
> Options: 0 No · 1 Yes

**112.** On every 100 rupees you borrowed, about how much interest do you pay in a month? (Rs; 0 if none, leave blank if not known)

> **ENUMERATOR:** Ask only if: took_loan_12m = 1; may be left blank  
> Record: number

**113.** Did you have to give anything as security for it? If so, what — jewellery, land, animals, a vehicle, shop stock, a house, or something else?

> **ENUMERATOR:** Ask only if: took_loan_12m = 1  
> Options: 0 Nothing was given as security · 1 Jewellery or ornaments · 2 Land · 3 Animals · 4 A vehicle · 5 Shop stock or business goods · 6 House or building · 7 Something else

**114.** How many people in your household are covered by any health insurance or health scheme, including government ones? (0 if none)

> **ENUMERATOR:** Record: whole number

**115.** How many people in your household have life insurance? (0 if none)

> **ENUMERATOR:** Record: whole number

**116.** Is your crop insured?

> **ENUMERATOR:** Ask only if: land_cultivable_acres > 0  
> Options: 0 No · 1 Yes

**117.** In the last 12 months, did your household get anything from any government scheme? Read the list out before you take an answer.

> **ENUMERATOR:** Options: 0 No · 1 Yes  
> How to code: READ THE LIST OUT; do not ask the bare question, because people fail to recall the category and say no. Ration card or PDS grain; MGNREGA work or job card; old-age, widow or disability pension; PM-KISAN; Ujjwala LPG; PM-SYM or Atal Pension; Ayushman Bharat or a health card; a housing scheme (PMAY or state). Any one of them is a Yes.

**118.** Which ones? Write down every scheme they name, in their own words.

> **ENUMERATOR:** Ask only if: govt_any_benefit = 1  
> Record: write the answer in words, verbatim  
> How to code: Write the scheme names in their own words, all of them, including any not on the list you just read. Office-coded afterwards, so do not try to fit the answer to a category.

**119.** Do you own a smartphone?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**120.** How many people in your household can make a payment by phone themselves, without help? (0 if none)

> **ENUMERATOR:** Record: whole number

> _Module G complete._


---

## Module H — Health

Now a few questions about health in your household. You may leave out any of these.

**121.** In the last 15 days, was anyone in your household ill?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes

**122.** How did the household mainly cope with the cost of this: used savings; borrowed money; sold or pawned assets; cut other consumption; got help from relatives or community; or something else?

> **ENUMERATOR:** Ask only if: morbidity_15d = 1. May be left blank  
> Options: 1 Used savings · 2 Borrowed money · 3 Sold or pawned assets · 4 Cut consumption · 5 Help from relatives/community · 6 Paid it out of normal earnings, nothing given up · 7 Something else (say what)

**123.** About how much did the household spend on this in the last 15 days (medicine, doctor or clinic fees, travel for care)? (Rs)

> **ENUMERATOR:** Ask only if: morbidity_15d = 1. May be left blank  
> Record: amount in rupees, whole number

**124.** Do you have difficulty walking or climbing steps?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 1 No difficulty · 2 Some difficulty · 3 A lot of difficulty · 4 Cannot do it at all

**125.** In the last 12 months, was anyone in your household admitted to hospital overnight?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes

**126.** In the last 3 months, was there a time when someone in your household needed medical care but could not get it?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes

**127.** In the last five years, has any child or young person under 18 in your household died?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes  
> How to code: Say the lead-in before you ask: "The next question is about a death in the family. You do not have to answer it." Then ask it once. Do NOT probe, do not ask for details, and do not ask again if they go quiet -- leave it blank and move on. A blank here is a correct and complete answer; NITI's own rule treats an unanswered mortality item as not deprived.

**128.** In the last five years, did any woman in your household give birth?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes

**129.** For the most recent birth, did she have at least four check-ups before the delivery?

> **ENUMERATOR:** Ask only if: birth_last_5y = 1. May be left blank  
> Options: 0 No · 1 Yes  
> How to code: Ask the mother herself if she is there. If not, probe: did she go for check-ups before the birth, and about how many times? Four or more is Yes; two or three is No. Do not accept a shrug — ask how many times she went.

**130.** Who conducted that delivery — a doctor, a nurse or ANM, an ASHA or Anganwadi worker, a dai, or nobody trained?

> **ENUMERATOR:** Ask only if: birth_last_5y = 1. May be left blank  
> Options: 1 Doctor · 2 Nurse, ANM or LHV · 3 ASHA or Anganwadi worker only · 4 Dai (traditional birth attendant) · 5 Nobody trained; family only  
> How to code: Code who CONDUCTED the delivery, not who was in the room. An ASHA or Anganwadi worker accompanying a birth is code 3, not a nurse: NITI counts only a doctor, nurse, ANM or LHV as skilled. A dai is code 4. If an ANM conducted it and an ASHA brought her, that is 2.

> _Module H complete._


---

## Module I — Food security, shocks and coping

Now about food, and about any difficult times in the last year and how your household managed.

**131.** In the last 12 months, did any of these happen — to your household, or to the Yatra route you work on? Check every one that applies.

> **ENUMERATOR:** select all that apply: 9 Nothing of this kind happened · 1 Serious illness or death of an earning member · 2 Crop failure or livestock loss · 3 Damage from a natural disaster (flood, landslide, fire) · 4 Loss of business, goods or assets · 5 Road or bridge blocked, route closed · 6 Yatra stopped early or badly disrupted · 7 Sharp fall in customers or prices · 8 Lost the work or the work stopped

**132.** Thinking of whichever of those hit you hardest — about how many weeks of work did you lose because of it? (0 if none)

> **ENUMERATOR:** Ask only if: distress_event_last365d names a real shock (not code 9, nothing happened)  
> Record: whole number

**133.** And about how much money did your household have to spend because of it — treatment, repairs, replacing what was lost? (Rs, 0 if nothing)

> **ENUMERATOR:** Ask only if: distress_event_last365d names a real shock (not code 9, nothing happened)  
> Record: amount in rupees, whole number

**134.** And in which month did that one happen?

> **ENUMERATOR:** Ask only if: distress_event_last365d names a real shock (not code 9, nothing happened)  
> Options: 1 January · 2 February · 3 March · 4 April · 5 May · 6 June · 7 July · 8 August · 9 September · 10 October · 11 November · 12 December

**135.** How did your household manage? Check every one they used.

> **ENUMERATOR:** Ask only if: any shock was reported  
> select all that apply: 1 Used savings · 2 Borrowed money · 3 Sold or pawned assets · 4 Cut consumption · 5 Help from relatives/community · 6 Paid it out of normal earnings, nothing given up · 7 Something else (say what)

**136.** In the last 12 months, was there a time when, because of a lack of money or other resources, you had to skip a meal?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes

**137.** In the last 12 months, was there a time when, because of a lack of money or other resources, you ate less than you thought you should?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes

**138.** In the last 12 months, was there a time when, because of a lack of money or other resources, your household ran out of food?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes

**139.** In the last 12 months, was there a time when, because of a lack of money or other resources, you were hungry but did not eat?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes

**140.** In the last 12 months, was there a time when, because of a lack of money or other resources, you went without eating for a whole day?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes

> _Module I complete._


---

## Module J — Ropeway

Now a few questions about the ropeway that has been proposed for this route. It is only a proposal — nothing has been built. There is no right answer and nothing you say here goes to anyone but us.

**141.** A ropeway is proposed for this route. Are you in favour, neutral, or against?

> **ENUMERATOR:** Options: 1 Support · 2 Neutral · 3 Oppose · 98 Prefer not to say  
> How to code: Name the alignment for the route you are on: on the Kedarnath side it is the ropeway proposed between Gaurikund and Kedarnath, on the Hemkund side between Govindghat and Hemkund. Both are proposed, and the four ropeway questions are asked on BOTH routes -- they used to be asked only on the Kedarnath side, which left the Hemkund interviews with no ropeway data at all. If the respondent has not heard of it, say that it is proposed and not yet built, then take the answer; do not explain what it would do.

**142.** If the ropeway is built, what do you think will happen to your own work? More work for you; less work; about the same; or don't know?

> **ENUMERATOR:** Options: 1 More work for me · 2 Less work for me · 3 About the same · 97 Don't know

**143.** Who do you think will get most of the jobs the ropeway creates? People from these villages; people from outside the area; nobody will get jobs; or don't know?

> **ENUMERATOR:** Options: 1 People from these villages · 2 People from outside the area · 3 Nobody will get jobs · 97 Don't know

**144.** Do you think the ropeway will improve the livelihoods of people here? Yes; no; or don't know?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**145.** Is your main work carrying, transporting or guiding people or goods on foot along the pilgrimage trek?

> **ENUMERATOR:** Options: 0 No · 1 Yes

> _Module J complete._


---

## Module K — Job quality (Apablaza et al. 2026 questions)

Now a set of questions about the conditions of your work — hours, pay, contract and so on. These come from a standard list used in many countries, so one or two may not fit your situation. Say so and we will move on.

**146.** Do you have a signed contract? Yes, signed; yes but not yet signed; no contract.

> **ENUMERATOR:** Ask only if: employment_type is 3 or 4 (wage workers) — self-employed skip to the next question  
> Options: 1 Yes, signed · 2 Yes, but not yet signed · 3 No contract

**147.** Is your workplace or business registered, for example with a taxpayer or GST number, a shop or trade licence, the Yatra registration, or a union?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**148.** Do you contribute to any pension system? Yes, the employer deducts it; yes, voluntarily; no.

> **ENUMERATOR:** Options: 1 Yes, employer deducts it · 2 Yes, contributes voluntarily · 3 No

**149.** Do you have health insurance through your work? Yes; only private or other insurance; none; don't know.

> **ENUMERATOR:** Options: 1 Yes, through work · 2 Only private or other insurance · 3 None · 4 Don't know

**150.** Do you have the right to paid holiday, sick or maternity leave?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**151.** Have you ever been physically injured at your workplace?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**152.** In the last 12 months, was anyone physically injured at your workplace because of work?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**153.** And in the last 12 months, did anyone die at your workplace because of work?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**154.** Would you like to work more hours than you do?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**155.** On a working day, how many MORE hours would you like to work?

> **ENUMERATOR:** Ask only if: wants_more_work = 1  
> Record: whole number

**156.** Across the months when you had no paid work, about how many MONTHS in total were you looking for work?

> **ENUMERATOR:** Ask only if: months_no_paid_work > 0  
> Record: whole number

**157.** Was your current work the first paid job you ever had?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**158.** Have you completed any college, diploma or university course?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**159.** Are you enrolled in any pension, insurance or social-security scheme? For example, EPFO or PM-SYM pension, or Ayushman Bharat health cover.

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**160.** For more than half of your working day, do you work at very high speed?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**161.** For more than half of your working day, do you work to tight deadlines?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**162.** For more than half of your working day, do you not have enough time to finish your tasks?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**163.** For more than half of your working day, do you work in a tiring or painful position?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**164.** For more than half of your working day, do you carry or move heavy loads?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**165.** For more than half of your working day, do you make the same movements again and again?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**166.** For more than half of your working day, are you exposed to loud noise?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

**167.** For more than half of your working day, are you exposed to extreme heat or cold?

> **ENUMERATOR:** Options: 0 No · 1 Yes · 97 Don't know

> _Module K complete._


---

## Module L — Tasks and skills (short block)

Now I will read out some kinds of work-tasks and ask whether you do them. There is no right or wrong answer — we are trying to understand what skills the work here actually uses.

**168.** Do you load, unload, stack or count goods? 

> **ENUMERATOR:** Options: 1 Yes, regularly in my main Yatra work · 2 Not in my main work, but done before elsewhere · 3 Never done

**169.** Do you drive a motor vehicle? 

> **ENUMERATOR:** Options: 1 Yes, regularly in my main Yatra work · 2 Not in my main work, but done before elsewhere · 3 Never done

**170.** Do you operate an engine or machine? 

> **ENUMERATOR:** Options: 1 Yes, regularly in my main Yatra work · 2 Not in my main work, but done before elsewhere · 3 Never done

**171.** Do you do electrical or wiring work? 

> **ENUMERATOR:** Options: 1 Yes, regularly in my main Yatra work · 2 Not in my main work, but done before elsewhere · 3 Never done

**172.** Do you check equipment or the route for safety? 

> **ENUMERATOR:** Options: 1 Yes, regularly in my main Yatra work · 2 Not in my main work, but done before elsewhere · 3 Never done

**173.** Do you sell goods or services? 

> **ENUMERATOR:** Options: 1 Yes, regularly in my main Yatra work · 2 Not in my main work, but done before elsewhere · 3 Never done

**174.** Do you handle cash and payments? 

> **ENUMERATOR:** Options: 1 Yes, regularly in my main Yatra work · 2 Not in my main work, but done before elsewhere · 3 Never done

**175.** Do you cook or prepare food or drink? 

> **ENUMERATOR:** Options: 1 Yes, regularly in my main Yatra work · 2 Not in my main work, but done before elsewhere · 3 Never done

**176.** Do you serve guests or customers? 

> **ENUMERATOR:** Options: 1 Yes, regularly in my main Yatra work · 2 Not in my main work, but done before elsewhere · 3 Never done

**177.** Do you clean rooms or public areas? 

> **ENUMERATOR:** Options: 1 Yes, regularly in my main Yatra work · 2 Not in my main work, but done before elsewhere · 3 Never done

**178.** Do you guide or explain things to visitors? 

> **ENUMERATOR:** Options: 1 Yes, regularly in my main Yatra work · 2 Not in my main work, but done before elsewhere · 3 Never done

**179.** Do you coordinate work by phone, radio or signals? 

> **ENUMERATOR:** Options: 1 Yes, regularly in my main Yatra work · 2 Not in my main work, but done before elsewhere · 3 Never done

**180.** Have you ever driven a motorcycle or scooter, with or without a licence?

> **ENUMERATOR:** Ask only if: tk_drive is 1 or 2  
> Options: 0 No · 1 Yes

**181.** ... a car or jeep?

> **ENUMERATOR:** Ask only if: tk_drive is 1 or 2  
> Options: 0 No · 1 Yes

**182.** ... a truck or bus?

> **ENUMERATOR:** Ask only if: tk_drive is 1 or 2  
> Options: 0 No · 1 Yes

**183.** In your work, do you read anything (notes, rate lists, tickets, messages)?

> **ENUMERATOR:** Options: 0 No · 1 Yes

**184.** In your work, do you work out prices or costs?

> **ENUMERATOR:** Options: 0 No · 1 Yes

> _Module L complete._


---

## Module M — Access to common resources (short block)

Last, a few questions about the forest and common land around where you work — firewood, fodder, grazing and water. Some of this is not allowed in some places, and that is a perfectly good answer: we only want to know what is possible and what is not. Nothing you say goes to the Forest Department or to anyone else, and you can leave any of these out.

**185.** Where you work, is it allowed to take firewood, fodder or forest produce from the forest or common land? Ask what they understand the rule to be; do not correct them.

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 1 Yes, it is allowed · 0 No, it is not allowed · 2 Allowed only with a permit or a fee · 97 Don't know

**186.** In this Yatra season or last Yatra season, did you or anyone staying with you here collect firewood or dead wood from common land or forest in the Yatra region or workplace region?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes · 2 No, it is not allowed here · 97 Don't know

**187.** In this Yatra season or last Yatra season, did you or anyone staying with you here cut grass or fodder from common land in the Yatra region or workplace region?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes · 2 No, it is not allowed here · 97 Don't know

**188.** In this Yatra season or last Yatra season, did you or anyone staying with you here collect herbs, mushrooms or wild fruit from the forest in the Yatra region or workplace region?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes · 2 No, it is not allowed here · 97 Don't know

**189.** In this Yatra season or last Yatra season, did any animal of yours or of anyone staying with you here graze on common pasture in the Yatra region or workplace region?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes · 2 No, it is not allowed here · 97 Don't know

**190.** In this Yatra season or last Yatra season, has anyone you or someone staying with you here been stopped from using a common forest, pasture or path, or been asked to pay to use it, in the Yatra region or workplace region?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes · 97 Don't know

**191.** In this Yatra season or last Yatra season, has a common place you used to collect from or graze on been closed, because of a landslide, flood, road or bridge damage, or construction work, in the Yatra region or workplace region?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 0 No · 1 Yes · 97 Don't know

**192.** On your route or near your worksite, can you use a common water source (spring, tap or stream) without paying?

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 1 Yes, free to use · 2 A source exists but we must pay · 3 No source nearby · 97 Don't know

**193.** In the Yatra region or workplace region, who decides who may use the common land and forest? Ask and code what they name; do not read the list.

> **ENUMERATOR:** Ask only if: May be left blank  
> Options: 1 Village head or panchayat · 2 Forest department · 3 Local committee or community group · 4 Nobody decides; it is open to all · 97 Don't know

> _Module M complete._


---

## Closing

That is everything. Thank you for your time — I know the season is busy and this took a while.

Is there anything you want to ask me, or anything about your work you think we have missed?

> **ENUMERATOR:** Record anything volunteered here in the notes field. Check the form is complete before leaving — you cannot come back.


_193 questions in all. Generated from dictionary.py — do not edit by hand._