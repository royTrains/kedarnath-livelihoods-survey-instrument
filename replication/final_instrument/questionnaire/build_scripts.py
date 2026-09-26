# -*- coding: utf-8 -*-
"""Write the two enumerator interview scripts (English and Hindi) as Markdown.

Generated from dictionary.py and translations_hi.py, so the scripts cannot drift out of step with
the form the tablet is actually running. Re-run after any change to either.

A script is not the questionnaire. The questionnaire is a list of variables; a script is what a
person says out loud, in order, with the joins between sections, the prompts for open answers, and
the instructions the enumerator follows but never reads aloud. Those instructions are marked and
indented so they are visually impossible to confuse with the spoken text.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dictionary import ROWS, LSETS, MODULES
from translations_hi import HI, HI_LSETS

# Natural joins between modules -- the sentence that carries the respondent from one topic to the
# next. Without these a read-aloud interview lurches between subjects and feels like an interrogation.
BRIDGE_EN = {
    "A": "First, a few things about you and the people you live with.",
    "B": "Now I want to ask about your work here during the Yatra season.",
    "C": "Next I would like to go through the whole year, month by month. Take your time.",
    "D": "Now a few questions about where your home is.",
    "E": "The next part is about what your household usually spends. Rough amounts are fine — nobody expects exact figures.",
    "F": "Now about the house you usually live in, and things your household owns.",
    "G": "A few short questions about banking, loans and schemes.",
    "H": "Now about health in your household.",
    "I": "The next few questions are about food, and about difficult times.",
    "J": "Now I want to ask what you think about the proposed ropeway.",
    "K": "A few questions about the conditions of your work.",
    "L": "Last part. I will read out some kinds of work, and you tell me whether you do them.",
}
BRIDGE_HI = {
    "A": "सबसे पहले, आपके और आपके घर के लोगों के बारे में कुछ बातें।",
    "B": "अब मैं यात्रा के मौसम में आपके काम के बारे में पूछूँगा/पूछूँगी।",
    "C": "अब मैं पूरे साल के बारे में, एक-एक महीने करके पूछूँगा/पूछूँगी। आराम से सोचकर बताइए।",
    "D": "अब कुछ सवाल कि आपका घर कहाँ है।",
    "E": "अगला हिस्सा आपके घर के ख़र्च के बारे में है। अंदाज़ा बता दीजिए, बिल्कुल सही आँकड़े की ज़रूरत नहीं है।",
    "F": "अब उस घर के बारे में जहाँ आप आम तौर पर रहते हैं, और घर के सामान के बारे में।",
    "G": "बैंक, उधार और सरकारी योजनाओं पर कुछ छोटे सवाल।",
    "H": "अब आपके घर में सेहत के बारे में।",
    "I": "अगले कुछ सवाल खाने के बारे में हैं, और मुश्किल वक़्त के बारे में।",
    "J": "अब मैं जानना चाहूँगा/चाहूँगी कि प्रस्तावित रोपवे के बारे में आप क्या सोचते हैं।",
    "K": "आपके काम के हालात पर कुछ सवाल।",
    "L": "आख़िरी हिस्सा। मैं कुछ तरह के काम बताऊँगा/बताऊँगी, आप बताइए कि आप वे करते हैं या नहीं।",
}

MODTITLE_HI = {
    "P": "आवरण, सहमति और रिकॉर्ड", "A": "आप और आपका घर", "B": "काम और काम का इतिहास",
    "C": "साल भर का काम और कमाई; भेजा-मिला पैसा", "D": "आना-जाना और घर की जगह",
    "E": "घर का ख़र्च", "F": "मकान, सुविधाएँ और सामान", "G": "बैंक, बीमा और योजनाएँ",
    "H": "सेहत", "I": "खाना, मुश्किलें और उनसे निपटना", "J": "रोपवे",
    "K": "काम की गुणवत्ता", "L": "काम-काज और हुनर (छोटा हिस्सा)",
}

CONSENT_EN = """We are doing a study on the livelihoods of people who work on the Yatra route. I would like
to ask you some questions about your work, your household and your spending.

Taking part is your choice. You can stop at any time, and you can skip any question you do not want to
answer. Nothing you tell me will be linked to your name, and nothing you say will affect your work here
or any government benefit.

Do you agree to take part?"""

CONSENT_HI = """हम यात्रा मार्ग पर काम करने वाले लोगों के रोज़गार पर एक अध्ययन कर रहे हैं। मैं आपसे आपके काम,
आपके घर और आपके ख़र्च के बारे में कुछ सवाल पूछना चाहूँगा/चाहूँगी।

इसमें शामिल होना आपकी मर्ज़ी है। आप कभी भी रोक सकते हैं, और जिस सवाल का जवाब नहीं देना चाहते उसे छोड़ सकते हैं।
आप जो बताएँगे वह आपके नाम से नहीं जोड़ा जाएगा, और उससे यहाँ आपके काम या किसी सरकारी सुविधा पर कोई असर नहीं पड़ेगा।

क्या आप इसमें शामिल होना चाहते हैं?"""

CLOSE_EN = """That is everything. Thank you for your time — I know the season is busy and this took a while.

Is there anything you want to ask me, or anything about your work you think we have missed?"""

CLOSE_HI = """बस इतना ही। आपका बहुत-बहुत धन्यवाद — सीज़न में काम बहुत रहता है और इसमें वक़्त लगा।

क्या आप मुझसे कुछ पूछना चाहते हैं, या अपने काम के बारे में कुछ ऐसा है जो हमसे छूट गया हो?"""

# Open-ended items need a probe, not just a question. One probe, then stop.
PROBE_EN = {
    "occupation_detail": "Write what they DO and who for, not just a job title. Include the goods or food they sell if that is the work.",
    "ropeway_opinion": "If they stop after a few words, ask ONCE: \"Anything else?\" Then stop. Do not argue, agree, or offer examples.",
    "prev_occ": "Write it in their words. If they name a place or an employer, write that too.",
    "target_occ": "Do not suggest anything. \"Don't know\" and \"there is no other work for me\" are real answers — write them down as said.",
}
PROBE_HI = {
    "occupation_detail": "सिर्फ़ काम का नाम नहीं — वे करते क्या हैं और किसके लिए, यह लिखिए। अगर बेचने का काम है तो क्या बेचते हैं, वह भी।",
    "ropeway_opinion": "अगर वे दो शब्द कहकर रुक जाएँ, तो एक बार पूछिए: \"और कुछ?\" फिर रुक जाइए। बहस मत कीजिए, सहमति मत जताइए, और उदाहरण मत दीजिए।",
    "prev_occ": "उनके ही शब्दों में लिखिए। अगर वे जगह या मालिक का नाम लें तो वह भी लिखिए।",
    "target_occ": "कोई सुझाव मत दीजिए। \"पता नहीं\" और \"मेरे लिए कोई और काम नहीं है\" — ये भी असली जवाब हैं, जैसे कहें वैसे लिख लीजिए।",
}

# Items enumerators must not let slide. Everything is required, but these carry information nothing
# else in the instrument can recover if they are answered lazily.
IMPORTANT = {
    "occupation_detail": ("The 14 groups above are deliberately coarse. THIS is the only place the real "
                          "job gets recorded, and the whole skills analysis is coded from it. \"Shop owner\" "
                          "could be a plank selling prasad or a three-storey general store -- write enough "
                          "that someone who was not there can tell which.",
                          "ऊपर के 14 समूह जान-बूझकर मोटे रखे गए हैं। असली काम सिर्फ़ यहीं दर्ज होता है, और हुनर का "
                          "पूरा विश्लेषण इसी से बनता है। \"दुकान का मालिक\" एक तख़्त पर प्रसाद बेचने वाला भी हो सकता है "
                          "और तीन मंज़िला परचून की दुकान भी — इतना लिखिए कि जो वहाँ मौजूद नहीं था वह भी फ़र्क़ समझ सके।"),
    "native_language_other": ("DO NOT skip this. The language list is long but India is longer. If their "
                              "language is not on it, type what they actually say -- this item stands in "
                              "for caste, and a bare \"other\" loses it for this respondent.",
                              "इसे छोड़ें नहीं। भाषाओं की सूची लंबी है, पर भारत उससे भी बड़ा है। अगर उनकी भाषा सूची में "
                              "नहीं है, तो वे जो कहें वही लिखिए — यह सवाल जाति के सवाल की जगह लेता है, और सिर्फ़ "
                              "\"अन्य\" लिख देने से यह जानकारी हमेशा के लिए चली जाती है।"),
}

LBL = {"en": {"note": "ENUMERATOR", "opts": "Options", "skip": "Ask only if", "rec": "Record",
              "mod": "Module", "consent": "Consent", "close": "Closing", "stop": "If they say no, thank them and stop."},
       "hi": {"note": "सर्वेक्षक के लिए", "opts": "विकल्प", "skip": "तभी पूछें जब", "rec": "दर्ज करें",
              "mod": "खंड", "consent": "सहमति", "close": "समापन", "stop": "अगर वे मना करें, तो धन्यवाद कहकर बातचीत यहीं रोक दें।"}}

KINDHINT = {"en": {"money": "amount in rupees, whole number", "count": "whole number",
                   "num": "number", "text": "write the answer in words, verbatim"},
            "hi": {"money": "रुपये में रक़म, पूरी संख्या", "count": "पूरी संख्या",
                   "num": "संख्या", "text": "जवाब जैसा कहा जाए वैसा शब्दों में लिखें"}}


def build(lang):
    L, out = LBL[lang], []
    asked = [r for r in ROWS if r["origin"] == "asked"]
    title = ("Kedarnath Yatra Worker Survey — Interview Script (English)" if lang == "en"
             else "केदारनाथ यात्रा कामगार सर्वेक्षण — साक्षात्कार स्क्रिप्ट (हिंदी)")
    out.append(f"# {title}\n")
    out.append("> " + ("Read the plain text aloud, exactly as written. Indented blocks marked "
                       "**ENUMERATOR** are for you only — never read them out. Choice lists are not read "
                       "aloud unless the respondent is struggling; ask the question, listen, and code the "
                       "closest option."
                       if lang == "en" else
                       "सादा लिखा हुआ हिस्सा जैसा लिखा है वैसा ही बोलकर पढ़ें। **सर्वेक्षक के लिए** लिखे हिस्से सिर्फ़ आपके "
                       "लिए हैं — उन्हें कभी ज़ोर से न पढ़ें। विकल्पों की सूची तब तक न पढ़ें जब तक जवाब देने वाले को दिक़्क़त न हो; "
                       "सवाल पूछिए, सुनिए, और सबसे नज़दीकी विकल्प दर्ज कीजिए।") + "\n")
    out.append(f"## {L['consent']}\n")
    out.append((CONSENT_EN if lang == "en" else CONSENT_HI) + "\n")
    out.append(f"> **{L['note']}:** {L['stop']}\n")

    n = 0
    for code, en_title in MODULES:
        rows = [r for r in asked if r["module"] == code]
        if not rows:
            continue
        shown = en_title if lang == "en" else MODTITLE_HI.get(code, en_title)
        out.append(f"\n---\n\n## {L['mod']} {code} — {shown}\n")
        out.append((BRIDGE_EN if lang == "en" else BRIDGE_HI).get(code, "") + "\n")
        for r in rows:
            n += 1
            q = r["question"] if lang == "en" else HI.get(r["name"], r["question"])
            out.append(f"**{n}.** {q}\n")
            notes = []
            if r["skip"]:
                # dictionary skip text often already opens with "Ask only if ..."; don't say it twice
                sk = r["skip"]
                for pre in ("Ask only if ", "Ask if ", "Automatic "):
                    if sk.startswith(pre):
                        sk = sk[len(pre):] if pre != "Automatic " else sk
                        break
                notes.append(f"{L['skip']}: {sk}")
            if r["lset"]:
                src = LSETS[r["lset"]] if lang == "en" else HI_LSETS.get(r["lset"], LSETS[r["lset"]])
                opts = " · ".join(f"{k} {v}" for k, v in src.items())
                kind = "select all that apply" if r["kind"] == "multi" else L["opts"]
                if lang == "hi" and r["kind"] == "multi":
                    kind = "जो-जो लागू हो सब चुनें"
                notes.append(f"{kind}: {opts}")
            elif r["kind"] in KINDHINT[lang]:
                notes.append(f"{L['rec']}: {KINDHINT[lang][r['kind']]}")
            if r["name"] in IMPORTANT:
                out.append("> ⚠️ **" + ("IMPORTANT" if lang == "en" else "ज़रूरी") + "** — " +
                           IMPORTANT[r["name"]][0 if lang == "en" else 1] + "\n")
            probe = (PROBE_EN if lang == "en" else PROBE_HI).get(r["name"])
            if probe:
                notes.append(probe)
            if notes:
                out.append("> **" + L["note"] + ":** " + "  \n> ".join(notes) + "\n")
        out.append(f"> _{L['mod']} {code} " + ("complete._" if lang == "en" else "पूरा हुआ।_") + "\n")

    out.append(f"\n---\n\n## {L['close']}\n")
    out.append((CLOSE_EN if lang == "en" else CLOSE_HI) + "\n")
    out.append("> **" + L["note"] + ":** " +
               ("Record anything volunteered here in the notes field. Check the form is complete "
                "before leaving — you cannot come back."
                if lang == "en" else
                "यहाँ जो कुछ वे अपने आप बताएँ, उसे नोट वाले ख़ाने में दर्ज करें। जाने से पहले देख लें कि फ़ॉर्म पूरा भरा है — "
                "दोबारा आना मुमकिन नहीं होगा।") + "\n")
    out.append(f"\n_{n} " + ("questions in all. Generated from dictionary.py — do not edit by hand._"
                             if lang == "en" else
                             "सवाल कुल मिलाकर। dictionary.py से बना है — हाथ से न बदलें।_"))
    return "\n".join(out)


for lang, fn in (("en", "Interview_script_EN.md"), ("hi", "Interview_script_HI.md")):
    p = os.path.join(HERE, fn)
    open(p, "w", encoding="utf-8").write(build(lang))
    print(p)
