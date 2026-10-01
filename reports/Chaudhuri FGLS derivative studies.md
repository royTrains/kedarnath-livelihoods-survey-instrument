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

## What this did not cover, and why

The research ran as six parallel topic searches — the estimator and its critics, South Asia, East and
Southeast Asia, Africa, non-monetary extensions, and rest-of-world plus recent methods. **All six were
terminated by an API rate limit before any wrote output.** Their final messages did establish the route
that worked, and this report is built on it: the bibliographic APIs rather than web search.

Consequently this inventory is **complete for what the citation graph and those search phrases can
reach**, and incomplete in three specific ways:

1. **No full-text screening.** A work appears here because its indexed metadata or abstract carries an
   FGLS phrase. Confirming that each one runs the three-stage procedure rather than merely naming it
   requires reading the methods sections. The 135 are candidates with verified bibliographic details,
   not 135 confirmed implementations.
2. **The 37 unverified entries are unresolved.** Several are likely genuine older working papers whose
   DOIs predate registration. They need a direct check at the issuing institution.
3. **No regional or thematic synthesis.** Grouping the 135 by setting, dataset, poverty line,
   vulnerability threshold and headline rate — the comparison table a methods section wants — was the
   job of the six topic researchers and did not happen.

Each of the three is a bounded, resumable task against the file that now exists.

---

## Recommended next step

Screen the 135 verified entries down to confirmed implementations, and extract for each the setting,
the poverty line, the vulnerability threshold and the headline vulnerability rate against measured
poverty. That turns this inventory into the comparison table the methods section needs, and it is
mechanical work on a file of DOIs rather than open-ended searching.

---

*Sources: the OpenAlex and Crossref public APIs, queried 2026-10-01. Every DOI in the inventory can be
re-resolved at https://doi.org/ to re-check it independently.*
