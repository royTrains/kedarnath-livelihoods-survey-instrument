# Chaudhuri FGLS derivative studies

*A verified inventory of the literature that applies the three-stage FGLS vulnerability-as-expected-poverty
estimator this study uses. Every entry was taken from the OpenAlex citation graph and then confirmed
independently against Crossref; nothing here is reconstructed from memory.*

---

## How this was built, and what the verification means

**The seed work.** Shubham Chaudhuri, Jyotsna Jalan and Asep Suryahadi (2002), *Assessing household
vulnerability to poverty from cross-sectional data: A methodology and estimates from Indonesia*,
Columbia University Department of Economics Discussion Paper. **doi:10.7916/d85149gf** ·
OpenAlex `W1515753611`.

This settles a question the project has been carrying: the paper the entire monetary arm rests on has a
resolvable DOI at Columbia Academic Commons, and OpenAlex records **474 citations** to it. It can now be
cited from the source rather than secondhand.

**Method.** The citing set was queried for the phrases that mark actual use of the procedure rather than
a passing citation — "feasible generalized least squares", "feasible generalised least squares",
"three-step feasible", "three-stage feasible", "vulnerability as expected poverty", and two broader
variants. Each candidate's DOI was then resolved at Crossref and the two sources' titles compared. An
entry appears as verified only where **both independent sources agree**.

**Result.** 172 candidates. **135 confirmed by both sources. 37 not confirmed**, held separately in the
notes under `UNVERIFIED - DO NOT CITE` with the reason for each — mostly works OpenAlex records without
a DOI (older RePEc and MPRA working papers), which may well be genuine but cannot be verified this way
and so must not be cited on this evidence.

Of the 135 verified, roughly **124 are journal articles** and 11 are preprints or working papers
(SSRN, Research Square, RePEc), which are flagged as such in the notes.

**Full inventory:** `research_notes/Chaudhuri FGLS derivative studies/07_openalex_crossref_harvest.md`
— 135 entries with full author lists, titles, journals, volume, issue, pages, DOIs, citation counts, and
both sources' type records.

---

## What the inventory shows

**The estimator is a live standard, not a historical one.** Verified applications by period:

| Period | Verified works |
|---|---|
| 2005–2009 | 7 |
| 2010–2014 | 21 |
| 2015–2019 | 41 |
| 2020–2024 | 61 |
| 2025–2026 | 5 (partial years) |

The range runs 2006 to 2026. More than half the verified literature postdates 2015, and the 2020–2024
block is the largest. For a progress report this is the useful finding: **the method does not need
defending as current.** It needs only to be applied correctly and its known weaknesses acknowledged.

**It travels across outcomes.** The verified set includes applications to consumption poverty, food
poverty and food insecurity, multidimensional deprivation, asset poverty, health-related poverty, and
relative poverty. Among the verified entries are a Colombian multidimensional application
(*Social Indicators Research*, doi:10.1007/s11205-022-02961-2), a tropical-cyclone application
(*International Journal of Disaster Risk Reduction*, doi:10.1016/j.ijdrr.2022.103404), and food-poverty
work in *World Development* (doi:10.1016/j.worlddev.2016.10.015).

**It travels across settings.** Verified applications cover China, India, Pakistan, Bangladesh, Vietnam,
Indonesia, Ghana, Nigeria, Ethiopia, Malawi, Congo, Colombia, and Syrian refugees in Lebanon, among
others.

**Methodological challengers are identifiable and few.** The clearest in the verified set is Hohberg et
al., *Vulnerability to poverty revisited: Flexible modeling and better predictive performance*,
**Journal of Economic Inequality**, doi:10.1007/s10888-017-9374-6, with a companion distributional-
regression paper in *PLoS ONE* (doi:10.1371/journal.pone.0226514). There is also a multilevel
longitudinal variant in the *Journal of Development Studies* (doi:10.1080/00220388.2016.1265942).
Anyone defending a cross-sectional FGLS application should expect to be asked about these.

---

## One citation correction for our own review

OpenAlex and Crossref both record **Feeny and McDonald as 2015**, doi:10.1080/00220388.2015.1075974,
while the *Journal of Development Studies* issue is 52(3), 447–464, dated 2016. This is the ordinary
online-first/issue split. Our progress-report review cites it as 2016, which matches the issue and is
defensible, but the DOI year is 2015 — worth settling one way and keeping consistent, since this paper
is load-bearing for the multidimensional arm.

---

## Stage two: screened to implementations

The 135 were then screened against their indexed abstracts, because a work appearing in the harvest
proves its bibliographic details, not that it runs the procedure. Each is labelled with what the
abstract actually supports:

| Label | Count | What it means |
|---|---|---|
| **CONFIRMED** | 18 | The abstract names the estimator — FGLS, three-stage, or Chaudhuri |
| **LIKELY** | 49 | Names a vulnerability-to-poverty measure but not the estimator |
| **UNCLEAR** | 32 | Neither appears; the matching phrase sits in the full text |
| **NO ABSTRACT** | 36 | None indexed; cannot be screened this way |

Table: `research_notes/Chaudhuri FGLS derivative studies/08_screened_comparison_table.md`, with
setting, journal, every percentage the abstract reports, and any threshold figure, per entry.

### The 18 confirmed implementations

These can be cited as definite applications on the evidence gathered.

| Year | Authors | Setting | Journal | DOI |
|---|---|---|---|---|
| 2025 | Xu et al. | China | Archives of Public Health | 10.1186/s13690-025-01821-y |
| 2024 | Khosla and Jena | India | Margin: Journal of Applied Economic Research | 10.1177/00252921241308210 |
| 2023 | Wei et al. | China | Global Health Action | 10.1080/16549716.2023.2260142 |
| 2023 | De and Som | India | Research Square (preprint) | 10.21203/rs.3.rs-3185956/v1 |
| 2022 | Khosla and Jena | India | Review of Development Economics | 10.1111/rode.12928 |
| 2022 | Su and Guo | China | Discrete Dynamics in Nature and Society | 10.1155/2022/3960691 |
| 2022 | Ma et al. | China | Frontiers in Public Health | 10.3389/fpubh.2022.776901 |
| 2021 | Xiang et al. | China | Global Health Journal | 10.1016/j.glohj.2021.07.004 |
| 2020 | Ouoya et al. | Congo | Humanities and Social Sciences Communications | 10.1057/s41599-020-00674-w |
| 2019 | Adepoju et al. | Nigeria | Int. Journal of Scientific Research in Sci. and Tech. | 10.32628/ijsrst19668 |
| 2019 | Ouoya | — | Studies and Scientific Researches: Economics | 10.29358/sceco.v0i30.441 |
| 2018 | Atake | Burkina Faso, Niger, Togo | Health Economics Review | 10.1186/s13561-018-0210-x |
| 2018 | Zhang et al. | China | Int. Journal of Environmental Research and Public Health | 10.3390/ijerph15061253 |
| 2018 | Hohberg et al. | Germany | Journal of Economic Inequality | 10.1007/s10888-017-9374-6 |
| 2016 | Zereyesus et al. | Ghana | World Development | 10.1016/j.worlddev.2016.10.015 |
| 2015 | Haq | Pakistan | Pakistan Development Review | 10.30541/v54i4i-iipp.915-929 |
| 2012 | Novignon et al. | Ghana | Health Economics Review | 10.1186/2191-1991-2-11 |
| 2012 | Islam et al. | Bangladesh | Journal of Statistical Computation and Simulation | 10.1080/00949655.2012.656310 |

One of these is new to the project and worth having: **Khosla and Jena (2024)**, *Margin: The Journal
of Applied Economic Research*, doi:10.1177/00252921241308210 — a fourth Khosla paper beyond the three
already on the shelf.

### Where the method has actually been used

Settings across the confirmed and likely sets, counted from indexed abstracts:

| Setting | Works |
|---|---|
| China | 17 |
| Ethiopia | 7 |
| India | 3 |
| Nigeria | 3 |
| Indonesia | 3 |
| Ghana, Malawi | 2 each |
| Congo, Burkina Faso, Niger, Togo, Germany, Bangladesh, South Africa | 1 each |

**This is a finding in its own right.** The estimator's recent empirical centre of gravity is China,
by a factor of five over India. For an Indian application the implication is favourable: the method is
well established, and the Indian evidence base using it is thin enough that a careful application adds
to it rather than repeating it.

---

## What this did not cover, and why

The research ran as six parallel topic searches — the estimator and its critics, South Asia, East and
Southeast Asia, Africa, non-monetary extensions, and rest-of-world plus recent methods. **All six were
terminated by an API rate limit before any wrote output.** Their final messages did establish the route
that worked, and this report is built on it: the bibliographic APIs rather than web search.

Three specific limits remain:

1. **117 of the 135 are not confirmed implementations.** 49 are likely, 32 unclear, 36 have no indexed
   abstract. Confirming each requires opening its methods section. The screening narrows that job from
   135 papers to a labelled queue, but does not do it.
2. **The 37 unverified entries are unresolved.** Mostly older RePEc and MPRA working papers OpenAlex
   records without a DOI. They may well be genuine and need a direct check at the issuing institution.
3. **The percentage columns are unlabelled.** The table carries every figure each abstract reports, in
   order, as candidates for the vulnerability-rate and poverty-rate columns. Which is which has to be
   read off the paper. No figure in that table should be quoted without that check.

---

## Recommended next step

Work the CONFIRMED 18 first: they are already citable, and reading 18 methods sections yields the
poverty line, the vulnerability threshold and the headline rates for a comparison table that would
stand in a methods section. Then take the 49 LIKELY as the second pass.

---

*Sources: the OpenAlex and Crossref public APIs, queried 2026-10-01. Every DOI in the inventory and the
screened table can be re-resolved at https://doi.org/ to re-check it independently.*
