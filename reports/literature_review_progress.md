# Vulnerability on the Yatra Route

*Literature review and research gap for the progress report. Compiled only from the papers held in
`literature/`; nothing outside that folder is used. Works marked † are cited by the held papers but
their own texts are not in the folder — check any direct quotation against the original.*

---

## 1. Grounding: sustainable livelihoods

The study sits in the sustainable livelihoods tradition. In the formulation Chambers and Conway† gave
it and **Krantz** reproduces, *"a livelihood comprises the capabilities, assets (including both
material and social resources) and activities required for a means of living"*, and it is sustainable
*"when it can cope with and recover from stresses and shocks and maintain or enhance its capabilities
and assets"*.

Two commitments follow, and both shape the instrument. A livelihood is a **portfolio**, so the unit of
analysis is the household's whole asset base rather than its wage — **Krantz** and **Mensah** both note
that the portfolio, tangible and intangible together, is the framework's most complex component.
And sustainability is defined by the capacity to absorb shocks, which makes the approach inherently
forward-looking. That is the same stance the vulnerability literature formalises, and the reason these
two bodies of work belong in one design.

---

## 2. Vulnerability to poverty, and the method this study uses

Poverty measurement is *ex post*. **Klasen and Waibel (2015)** put the contrast plainly: poverty work
"determines actual poverty levels ex post", while vulnerability research "tries to examine the ex ante
poverty risk of households" — the propensity to be made poor by what has not happened yet.

**Gallardo (2018)**, surveying the field critically, supplies the caution to carry into any
application: estimated parameters alone do not identify who is vulnerable, that requires comparing a
normal against a risky counterfactual, and *"the relevant risk threshold for identifying the vulnerable
people remains diffuse"*. The threshold is a choice, and should be reported as a sweep rather than a
finding.

**Hoddinott and Quisumbing†**, as **Feeny and McDonald (2016)** relay, classify the empirical
approaches into three: vulnerability as expected poverty (VEP), as uninsured exposure to risk (VER),
and as low expected utility (VEU). **Chiwaula et al. (2011)** report the verdict of practice —
*"in empirical studies the expected poverty measures are dominant"*. **Ceesay and Morelli (2026)** and
**Eze and Iheonu (2025)** give the same three-way split and the same constraint on VER: it works after
the fact and "may be inconclusive when only cross-sectional data are available".

**This study uses VEP, estimated by the three-stage feasible generalised least squares procedure of
Chaudhuri, Jalan and Suryahadi (2002)†.** **Feeny and McDonald (2016)** state the reason it fits here:
the approach is chosen "due to its applicability to cross-sectional data, its ability to estimate a
headcount measure of vulnerability and the ease of interpreting results".

### 2.1 The derivative literature

The procedure is a standing method, not a one-off. Of the papers held here, **28 describe or apply the
three-stage FGLS**. **Azeem et al. (2018)** list the lineage themselves, calling it "a standard approach
that has been widely used to estimate vulnerability using cross-sectional data". Grouped by what each
adds:

**Method statements and critiques**

| Work | Contribution |
|---|---|
| Chaudhuri, Jalan & Suryahadi (2002)† | The three-stage FGLS itself. Also concede the limit their successors act on: *"Poverty reflects deprivation on multiple fronts, and hence vulnerability to poverty ought also to be a multidimensional concept"* (quoted in Feeny & McDonald 2016) |
| Pritchett, Suryahadi & Sumarto (2000) | Proposes the measure, applied to Indonesia |
| Hoddinott & Quisumbing (2008) | The three-way classification of empirical approaches; the densest treatment of the estimator held here |
| Gallardo (2018) | Critical survey; the identification threshold "remains diffuse" |
| Fujii (2016) | Review of concepts and measurement; the hazard critique this study answers |
| Hohberg et al. (2018), Germany | Flexible (distributional) modelling against the standard FGLS; better predictive performance |
| Cafiero & Vakis | Risk and vulnerability in poverty analysis; positions the measure among alternatives |
| Calvo & Dercon (2007) | Axiomatic alternative; distinguishes their measure from expected-poverty approaches |

**Applied to consumption poverty**

| Work | Setting | What it adds |
|---|---|---|
| Jha et al. (2018) | Rural India, panel 1999 & 2006 | Chronic poverty small, transient poverty high; shocks do the work |
| Azeem et al. (2016) | Punjab, Pakistan (~90,000 hh) | Organises covariates as **adaptive capacity, sensitivity, exposure** — the structure this study adopts. Vulnerability 56% against poverty 38% |
| Khosla et al. (2023) | Odisha, India | Rural livelihood programmes and capabilities; social capital and productive assets raise consumption |
| Klasen & Waibel (2015) | South-East Asia | Drivers, measurement and policy; the ex-ante framing |
| Chiwaula et al. (2011) | Cameroon & Nigeria, fishing | Asset-based variant |
| Mahanta & Das (2017) | Brahmaputra Valley, Assam | Flood-induced vulnerability — a named covariate hazard |
| Eze & Iheonu (2025) | Nigeria | Health shocks, quasi-experimental |
| Wang & Fu (2021) | Rural China | Digital financial inclusion |
| Zhang et al. (2024) | Rural China | Human capital of grassroots leaders |
| Zang et al. (2024) | China | Air pollution as a driver |
| Zheng & Ma (2023) | Jiangsu, China | Agricultural commercialisation and dietary diversity |
| Wei et al. (2023) | China | Health poverty alleviation programme |
| Shi et al. (2025) | China | Public services |
| Ding (2022) | China | Urban against rural comparison |
| Ngepah et al. (2023) | South Africa | Education and vulnerability |
| Islam & Chowdhury (2025) | Canada | Financial distress; the method outside a developing-country setting |
| Awuni et al. (2023) | Ghana | COVID-19 effects and social protection |
| Ceesay & Morelli (2026) | Rural West Africa | Cross-country application |
| Échevin (2013) | Sub-Saharan Africa | Vulnerability to **asset** poverty |

**Extended to multidimensional deprivation — the strand this study joins**

| Work | Setting | What it adds |
|---|---|---|
| Feeny & McDonald (2016) | Solomon Islands, Vanuatu | Runs the FGLS on a **deprivation score** rather than consumption, from cross-sectional data, because semi-subsistence living makes consumption poverty "notoriously difficult to measure". Vulnerability exceeds poverty and is driven by **volatility** in expected wellbeing more than by its level |
| Azeem et al. (2018) | Punjab, Pakistan | Runs monetary and multidimensional vulnerability side by side. **18% of multidimensionally poor households are missed by the monetary measure**; the choice of measure matters greatly for identifying the poor and much less for identifying the vulnerable |
| Lyons et al. (2023) | Lebanon, Syrian refugees | The fullest extension: 21 indicators across five dimensions, including a security and social inclusion dimension they describe as among the first of its kind, with the same FGLS run on the resulting score |
| Khosla & Jena (2023) | India | Multidimensional measure used for beneficiary targeting |
| Khosla & Jena (2022) | Odisha, India | MGNREGA and the PDS against vulnerability; 42% of households vulnerable |
| Khosla & Jena (2024) | Rural India, 17,468 hh | Public health insurance (RSBY) and *ex ante* vulnerability; VtP 33% against a poverty headcount of 27% |

**Apablaza et al. (2026)** are not an FGLS paper but supply the employment dimension this study adds,
across five domains, arguing that for developing economies *"the traditional distinction between formal
and informal work … is no longer useful"*, and noting that own-account operators, casual day-labourers
and multiple jobholders "often fall outside standard sampling frames".

### 2.2 Seasonality

**Dercon and Krishnan (2000)** remain the reference: roughly 1,450 rural Ethiopian households surveyed
three times over eighteen months, with consumption and poverty varying sharply by season, driven both
by shocks and by rational responses to predictable seasonal incentives. Their seasonality is recovered
from **survey rounds timed to seasons**, not from within a single visit.

---

## 3. Occupational transferability

What a displaced worker can do next is a separate literature. **Nawakitphaitoon and Ormiston (2016)**
set out its two estimators — a "market" approach after Shaw† from observed occupational changes, and a
"skills" approach after Ormiston† from knowledge, skills and abilities shared across occupations —
and show that although the two produce very different estimates, both predict the earnings losses of
displaced workers.

**Martins-Neto et al.** apply skills commonality to forced displacement with Brazilian register data,
finding it shortens unemployment spells and raises the probability of transiting to another occupation.
**Neffke et al. (2024)** classify displaced workers into stayers, upskillers, downskillers, reskillers
and lateral switchers, and estimate the cost of displacement for each — the typology this study uses
*ex ante*. **Gathmann and Schönberg (2010)** supply the task-distance measure.

For Indian informal work, **Sengupta et al. (2021)** map the skills of nearly 1,500 Bangalore slum
workers and argue for *"retiring the concept of 'unskilled' when referring to informal workers"*.
**Pelz et al. (2024)** come nearest to the setting — 2,000 rural households sampled by distance from
Jharkhand coal mines — but measure livelihood composition, not vulnerability, and coal closure is a
contraction where a ropeway is a substitution.

---

## 4. The gap

**Fujii (2016)** names the opening: most vulnerability studies *"abstract from specific hazards and
analyze vulnerability from the perspective of stochastic consumption"*, and because appropriate policy
depends on the hazard at issue, more research is needed linking specific hazards to poverty. A proposed
ropeway is a specific, announced, dated hazard to a walking-portering economy — not a draw from a
consumption variance.

Four gaps follow from what this corpus does and does not contain.

1. **No pilgrimage or seasonal religious-tourism labour economy appears in it.** Across some ninety
   papers, none concerns pilgrimage. Tourism enters twice and neither is a vulnerability study.
2. **Vulnerability and transferability never meet.** The skills papers measure unemployment duration
   and earnings loss, never vulnerability to poverty; the vulnerability papers treat shocks as
   stochastic and none uses a skills-distance measure.
3. **Seasonality is recovered from panel rounds.** No held design measures a two-regime annual
   livelihood from a single cross-section.
4. **The work dimension is proposed but not fielded** on the informal, own-account, multiple-jobholding
   workers Apablaza et al. themselves identify as missing from standard frames.

> **Research question.** How vulnerable to poverty are the workers of a seasonal pilgrimage economy,
> and how far is that vulnerability explained by the transferability of their skills to the work that
> would remain, or arrive, if the route they walk were replaced?

---

### Sources note

† Chaudhuri, Jalan & Suryahadi (2002); Chambers & Conway (1992); Hoddinott & Quisumbing (2003);
Shaw (1984); Ormiston (2014). Described here as the held papers describe them; their own texts are not
in `literature/`. Chaudhuri et al. in particular is the estimator the whole monetary arm runs on and
should be obtained before the methods section quotes it.
