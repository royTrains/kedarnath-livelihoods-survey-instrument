"""Builds task_items.csv: every task-module question, with response codes and the source it rests on.

Rules for this module (from the project owner):
  - no rating-style questions (no numeric scales, no Likert)
  - every item is tied to a source in the literature folder, or marked NEW
  - grounding: DIRECT = wording/idea taken from a published survey or classification
               ADAPTED = same idea, recast (e.g. a scale turned into yes/no) or extended
               NEW = route-specific, has no published counterpart, needs a field check
"""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))

T1_RESP = "1 = yes, regularly in my main Yatra work last season | 2 = not in my main work, but done before elsewhere (other job, off-season work or at home, more than a few days in total) | 3 = never | 97 = does not know"

# id, short label, read-aloud wording, group3 (Gathmann-Schoenberg), class5 (Autor-Levy-Murnane / Spitz-Oener), grounding, source
TASKS = [
 (1, "Carry loads on foot", "Carry loads or luggage on foot", "manual", "non-routine manual", "ADAPTED",
  "GS 2010 task 'pack, ship or transport'; NCO 9621.9900 luggage porters, 9621.0500 baggage porter. 'On foot on the trail' is NEW."),
 (2, "Carry a passenger", "Carry a passenger (palki, dandi, kandi)", "manual", "non-routine manual", "NEW",
  "No NCO-2015 code for palki/dandi bearers (documented gap); nearest NCO 9331.0100 hand and pedal vehicle driver. Needs union check."),
 (3, "Load, unload, stack, count goods", "Load, unload, stack or count goods", "manual", "routine manual", "DIRECT",
  "NCO 9333.0100 Loader and Unloader (shifting, stacking, counting loads)."),
 (4, "Pack or tie goods", "Pack or tie goods so they can be moved", "manual", "routine manual", "DIRECT",
  "GS 2010 task 'pack, ship or transport'; NCO 5223.0100 Shop Assistant (packs goods)."),
 (5, "Lead or control pack animals", "Lead, load or control pack animals such as ponies or mules", "manual", "non-routine manual", "DIRECT",
  "NCO 9332.0400 Pack Animal Driver (drives animal laden with goods, loads and unloads)."),
 (6, "Feed or care for animals", "Feed, groom or care for animals", "manual", "non-routine manual", "DIRECT",
  "NCO 9332.0400 (feeds animals, cleans stables)."),
 (7, "Drive a motor vehicle", "Drive a motor vehicle (car, jeep, tempo, bus)", "manual", "non-routine manual", "DIRECT",
  "NCO 8322.0501 Light Motor Vehicle Driver; Sengupta et al. 2021 skill 'driving'; Autor-Levy-Murnane 2003, Table I lists truck driving as a non-routine manual example."),
 (8, "Operate an engine or machine", "Operate an engine, machine or other equipment", "manual", "routine manual", "DIRECT",
  "GS 2010 'equip or operate machines'; Spitz-Oener 2006 routine manual; STEP module 6B 'operate heavy machines'."),
 (9, "Repair by hand", "Repair or fix things by hand (vehicles, tools, saddles, buildings)", "manual", "non-routine manual", "DIRECT",
  "GS 2010 'repair, renovate or reconstruct'; Spitz-Oener 2006 non-routine manual."),
 (10, "Electrical or wiring work", "Do electrical or wiring work", "manual", "non-routine manual", "DIRECT",
  "NCO 7411.0100 Electrician, General (installs, maintains, repairs electrical equipment; NSQF level 4)."),
 (11, "Build or construct", "Build or construct (masonry, carpentry, trail or road work)", "manual", "non-routine manual", "DIRECT",
  "GS 2010 'manufacture, install or construct'; NCO 9313.9900 building construction labourers."),
 (12, "Check equipment for safety", "Check equipment or loads for safety before use (saddle, rope, brakes)", "analytical", "routine cognitive", "ADAPTED",
  "NCO 8343.1700 Aerial Ropeway Operator (checks cages clamped, rope in working order); Pal et al. 2026 task 'inspect machine and tools for potential faults'."),
 (13, "Judge if weather or route is safe", "Judge whether the weather or route is safe and decide whether to go", "analytical", "non-routine analytic", "NEW",
  "No published counterpart. Idea anchored in the non-routine problem-solving task of Autor-Levy-Murnane 2003 and the 30-minute problem-solving item of Autor-Handel 2013."),
 (14, "Sell goods or services", "Sell goods or services to customers or pilgrims", "interactive", "non-routine interactive", "DIRECT",
  "GS 2010 'sell, buy or advertise'; Spitz-Oener 2006 'selling'; NCO 5223.0100 Shop Assistant, 4212.0100 Booking Clerk (issues tickets)."),
 (15, "Bargain over prices or fares", "Bargain or agree prices and fares", "interactive", "non-routine interactive", "DIRECT",
  "Spitz-Oener 2006 'negotiating'."),
 (16, "Handle cash and payments", "Handle cash, give change or take digital payments", "analytical", "routine cognitive", "ADAPTED",
  "NCO 4211.0100 Cashier (receives and counts cash); Sengupta et al. 2021 skill 'handling cash'. 'Digital payments' is NEW."),
 (17, "Buy stock or arrange supplies", "Buy stock or arrange supplies from suppliers", "interactive", "non-routine interactive", "DIRECT",
  "GS 2010 'sell, buy'; Spitz-Oener 2006 'buying'; NCO 5151.0600 Hotel and Restaurant Keeper (purchases food stuff), 1120.2000 Retail proprietor (buys merchandise)."),
 (18, "Cook or prepare food or drink", "Cook or prepare food or drink", "manual", "non-routine manual", "DIRECT",
  "NCO 5120.0200 Cook, Institutional; 5212.9900 Street Food Vendors (Dhabawala)."),
 (19, "Serve guests", "Serve guests (food, rooms, luggage)", "manual", "non-routine manual", "DIRECT",
  "GS 2010 'serve or accommodate'; Spitz-Oener 2006 'serving or accommodating'; NCO 5131.0200 Steward, Hotel; 5151.0800 Room Bearer."),
 (20, "Clean rooms or public areas", "Clean rooms, utensils or public areas", "manual", "non-routine manual", "DIRECT",
  "GS 2010 'cleaning'; NCO 9112.9900 helpers and cleaners in hotels and establishments; Autor-Levy-Murnane 2003, Table I lists janitorial services as non-routine manual."),
 (21, "Guide or explain to visitors", "Guide or explain routes, sites or rituals to visitors", "interactive", "non-routine interactive", "DIRECT",
  "NCO 5113.0200 Tourist Guide; Spitz-Oener 2006 'advising customers'."),
 (22, "First aid or help the sick", "Give first aid or help sick or injured people", "manual", "non-routine manual", "ADAPTED",
  "GS 2010 'nurse or treat others'."),
 (23, "Keep order or watch property", "Keep order among crowds, queues or turns (baari), or watch over property", "manual", "non-routine manual", "ADAPTED",
  "GS 2010 'secure'; NCO 5414.0501 Gateman / Unarmed Security Guard. Keeping a turn rotation (baari) is NEW."),
 (24, "Coordinate by phone, radio, signals", "Coordinate with others by phone, radio or signals", "interactive", "non-routine interactive", "DIRECT",
  "NCO 8343.1700 Aerial Ropeway Operator (communicates by telephone or buzzer); GS 2010 'organise, coordinate'."),
 (25, "Keep records or accounts", "Keep records or accounts (tickets, bookings, bills)", "analytical", "routine cognitive", "DIRECT",
  "GS 2010 'calculate or do bookkeeping'; Spitz-Oener 2006 routine cognitive; NCO 4212.0100 Booking Clerk (maintains record of sale)."),
 (26, "Supervise or hire others", "Supervise, hire or organise other people's work", "interactive", "non-routine interactive", "DIRECT",
  "GS 2010 'employ, manage personnel, organise'; Spitz-Oener 2006 'employing or managing personnel'; STEP 'supervise others'."),
 (27, "Teach or train others", "Teach or train others", "interactive", "non-routine interactive", "DIRECT",
  "GS 2010 'teach or train others'."),
]

ITEMS = []
for n, lab, words, g3, c5, ground, src in TASKS:
    ITEMS.append(dict(module="T1", block="Tasks performed", variable=f"t1_{n:02d}", label=lab, wording=words,
                      response=T1_RESP, group3=g3, class5=c5, grounding=ground, source=src))

ITEMS.append(dict(module="T1", block="Tasks performed", variable="t1_28", label="Main task",
    wording="Of the tasks you do regularly, which ONE takes most of your working time?",
    response="task number chosen from those coded 1 above",
    group3="", class5="", grounding="DIRECT",
    source="GS 2010: each worker also reports whether a task is his main activity; Autor-Handel 2013 asks about the share of the workday."))

T2 = [
 ("t2_01", "Trips per day", "In the busiest weeks, how many trips do you make in a day? (asked only if a carrying or animal task is coded 1)",
  "whole number", "NEW", "Route-specific count. Replaces the STEP 1-10 physical-effort scale, which is a rating. Needs union check."),
 ("t2_02", "Heavy lifting", "Do you regularly lift or carry a load as heavy as a 25 kg sack of flour or rice?",
  "1 yes | 2 no", "ADAPTED", "STEP module 6B: 'do you regularly have to lift or pull anything weighing at least ...' (item label verified in STEP Philippines file; the exact weight in STEP must be checked)."),
 ("t2_03", "Same tasks every day", "Is your work mostly the same tasks, day after day?",
  "1 yes | 2 no", "ADAPTED", "STEP module 6B 'short, repetitive tasks' (frequency scale recast as yes/no); Autor-Handel 2013 routine-task item."),
 ("t2_04", "Learning new things", "Do you learn new things in your work each season?",
  "1 yes | 2 no", "ADAPTED", "STEP module 6B 'learning new things' (frequency scale recast as yes/no)."),
 ("t2_05", "Who decides how you work", "Who decides how you do your work?",
  "1 I decide | 2 shared (for example with a union or partner) | 3 someone else (owner, union, customer)", "ADAPTED",
  "Apablaza et al. 2026, Table 4: 'autonomy to decide how and when tasks are performed'; STEP autonomy index."),
 ("t2_06", "Direct contact with customers", "Do you deal directly with customers or pilgrims on every working day?",
  "1 yes | 2 no", "ADAPTED", "Autor-Handel 2013 PDII items on face-to-face contact with customers or clients (share of day recast as yes/no)."),
 ("t2_07", "People you direct", "How many people do you regularly direct or supervise?",
  "whole number (0 if none)", "ADAPTED", "Autor-Handel 2013 'proportion of workday managing or supervising others'; STEP 'supervise others' (recast as a count)."),
 ("t2_08", "Time it took you to learn", "How long did it take YOU to learn your work well?",
  "number of months or seasons (enumerator codes to bins later)", "ADAPTED",
  "STEP module 6B 'how long would it take someone to learn to do this work well' (recast as the respondent's own experience)."),
]
for v, lab, w, r, gr, s in T2:
    ITEMS.append(dict(module="T2", block="Job conditions", variable=v, label=lab, wording=w, response=r,
                      group3="", class5="", grounding=gr, source=s))

T3 = [
 ("t3_01", "Read at work", "In your work, do you read anything (notes, rate lists, tickets, messages, notices)?",
  "1 yes | 2 no", "DIRECT", "STEP module 6A: 'do you read anything at this work, including very short notes or instructions' (label verified)."),
 ("t3_02", "Write at work", "In your work, do you write anything (names, amounts, messages)?",
  "1 yes | 2 no", "ADAPTED", "Companion to the STEP module 6A reading item; STEP tests writing only through the language items."),
 ("t3_03", "Calculate prices", "In your work, do you work out prices or costs?",
  "1 yes | 2 no", "DIRECT", "STEP module 6A: 'calculate prices or costs' (label verified)."),
 ("t3_04", "Multiply, divide, percentages", "In your work, do you multiply, divide, or work out change or discounts?",
  "1 yes | 2 no", "DIRECT", "STEP module 6A: 'perform any other multiplication or division' and 'use or calculate fractions, decimals or percentages' (labels verified)."),
 ("t3_05", "Lack of literacy cost a job", "Has not being able to read, write or do sums ever kept you from a job or a better job?",
  "1 yes | 2 no", "DIRECT", "STEP module 6A: 'has a lack of reading and writing skills ever kept you from ...' (label verified)."),
 ("t3_06", "Languages spoken", "For each language: can you speak it well enough to work with customers? (Hindi, Garhwali or local language, Nepali, English, other)",
  "yes / no for each language", "ADAPTED", "Sengupta et al. 2021 language skills (speaking, listening); the scale is dropped."),
 ("t3_07", "Languages read and written", "For each language: can you read and write it?",
  "yes / no for each language", "DIRECT", "STEP module 7 asks read/write for each language (labels verified)."),
 ("t3_08", "Phone", "What phone do you use? (none | basic phone | smartphone; own or shared)",
  "list", "ADAPTED", "Sengupta et al. 2021 'mobile phone usage', 'internet usage'; Pal et al. 2026 'use internet on phone'; project pilot variable digital_smartphone_use."),
 ("t3_09", "Phone use", "What do you use the phone for? (calls | messages or WhatsApp | internet, search or maps | digital payments)",
  "multiple answers", "ADAPTED", "Pal et al. 2026 generic-skills block; project pilot variable digital_payment_use."),
 ("t3_10", "Computer use", "In the last 12 months, have you used a computer or tablet? If yes, for what?",
  "yes / no; then list", "DIRECT", "STEP module 6B computer-use items (labels verified); Pal et al. 2026 (about 33% of workers used computers)."),
 ("t3_11", "Ever took a course", "Have you ever completed a training course or apprenticeship (not school)?",
  "1 yes | 2 no", "DIRECT", "STEP module 2: 'did you participate in any training or program, not as part of a formal education' (label verified)."),
 ("t3_12", "Type of course", "What kind of course was it? (driving | cooking or hospitality | guiding or trekking | electrical or technical | building trades | animal care | first aid or safety | computer | other)",
  "multiple answers", "ADAPTED", "STEP module 2 course types (computer, basic skills, language, occupation-specific, personal development) recast to local trades."),
 ("t3_13", "Certificate", "Did you receive a certificate?",
  "1 yes | 2 no", "ADAPTED", "NCO-2015 links some jobs to Qualification Packs with NSQF levels (for example electrician level 4, loader level 3)."),
 ("t3_14", "Who ran the course", "Who ran the course? (government scheme | NGO | private | union or association | employer)",
  "single answer", "ADAPTED", "Pal et al. 2026 'access to skilling opportunities' section."),
 ("t3_15", "Licences held", "Do you hold any of these? Please show it if you can. (two-wheeler licence | car licence | heavy vehicle licence | guide or trekking permit | food registration | ITI or skill certificate | first-aid certificate | security-guard certificate | none)",
  "multiple answers; enumerator records seen / not seen", "ADAPTED", "NCO 8322.0501 (a valid driving licence is required); NCO qualification packs for electrician (level 4), gateman (level 4)."),
 ("t3_16", "How you learned your work", "How did you learn your main work? (family or inherited | watching others | on the job | on my own | a course)",
  "multiple answers", "ADAPTED", "Pal et al. 2026: most workers learned by doing and from peers, only about one quarter had formal training first."),
]
for v, lab, w, r, gr, s in T3:
    ITEMS.append(dict(module="T3", block="Generic skills and credentials", variable=v, label=lab, wording=w, response=r,
                      group3="", class5="", grounding=gr, source=s))

cols = ["module", "block", "variable", "label", "wording", "response", "group3", "class5", "grounding", "source"]
out = os.path.join(HERE, "task_items.csv")
with open(out, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    for it in ITEMS:
        w.writerow(it)

# sanity checks the checklist relies on
assert len(TASKS) == 27
assert sum(1 for t in TASKS if t[3] == "analytical") == 4
assert sum(1 for t in TASKS if t[3] == "manual") == 16
assert sum(1 for t in TASKS if t[3] == "interactive") == 7
c5 = {}
for t in TASKS:
    c5[t[4]] = c5.get(t[4], 0) + 1
print("items written:", len(ITEMS), "->", out)
print("group3:", {g: sum(1 for t in TASKS if t[3] == g) for g in ("analytical", "manual", "interactive")})
print("class5:", c5)
print("grounding:", {g: sum(1 for i in ITEMS if i['grounding'] == g) for g in ("DIRECT", "ADAPTED", "NEW")})
