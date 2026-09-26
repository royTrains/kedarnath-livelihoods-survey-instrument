# VASyR worked example (Lyons, Kass-Hanna & Montoya Castano, 2023)

Replicates the *method* of Lyons, A.C., Kass-Hanna, J. and Montoya Castano, A.
(2023) "A multidimensional approach to measuring vulnerability to poverty
among refugee populations," *Journal of International Development* 35(7):
2014-2045 (working-paper version: ERF WP No. 1472, 2021): a multidimensional
livelihood index (MLI, Alkire-Foster) from the VASyR survey, fed into
Chaudhuri et al. (2002)'s 3-stage FGLS to get vulnerability to future poverty.

## Real data: `vasyr_real_example.do`

The real VASyR microdata is in `vasyr/` at the repo root: `UNHCR_LBN_2025_VASYR_data_main_v2.1.csv` (household, 3,546 rows, 975
columns) and `..._data_member_v2.1.csv` (individual roster, 16,006 rows).
This is the **2025 wave**, not the 2018 wave Lyons et al. use, so it is a real
analysis of real Syrian-refugee-in-Lebanon households, but not a replication
of their reported numbers, and the 2025 questionnaire doesn't carry every
2018 item under the same name. Run order:

1. `build_vasyr_real.py` -- reads both CSVs, aggregates the member roster to
   household level, and maps 21 columns onto Lyons et al.'s Table 2
   indicators. Writes `vasyr_real_raw.csv` (3,490 households: the 3,545 with
   a member roster minus 55 with no identifiable head-of-household row).
   **Documented proxies** (the rest are exact or near-exact matches to
   Table 2's wording):
   - `age` in the member file is banded (00-04/05-11/12-17/18-24/25-49/
     50-59/60+), not a single year. Working-age (Lyons: 15-64) is
     approximated as 18-59; "adult" (Lyons: 10+) as 18+; "child 6-14" as the
     05-11/12-17 bands. Household-head age uses the band midpoint.
   - `adult_schooling`: the 2025 file has no clean grade-to-years crosswalk,
     so this uses "never attended school" for every adult (18+) instead of
     Lyons' "all members 10+ have under 6 years of schooling" -- a coarser
     cutoff, most likely understating deprivation next to the real Table 2
     definition.
   - `underemployment`: no "days worked last month" item on file; uses
     `job_opp_avail_yn` ("are job opportunities available?", asked of
     under-occupied working-age members) as a labour-market-slack proxy.
   - `healthcare_access`: "did not select 'no barrier' " on the primary-care
     access-barriers question, in place of Lyons' "unable to access primary
     care or be hospitalized when needed."
   - `area_settlement`: reported shelter/infrastructure damage (collapsed
     shelter, non-functional sanitation pipes, unusable latrine) as a proxy
     for poor site conditions -- Lyons' own definition already folds in
     "poor sanitation conditions" and "low standard living conditions."
   - `housing_stability`: changed accommodation in the last 12 months (the
     file has no 6-month version, and no "planning to move due to high rent"
     item outside the eviction sub-module).
   - Household economic status: the ~40-item SMEB/MEB expenditure basket
     Lyons use isn't reconstructed here; `total_income_usd_dec` (30-day
     household income) is used instead, split into quartiles the same way
     SMEB/MEB splits expenditure into bands.
   - Geography: district (26 categories) is used directly as the fixed
     effect, rather than crosswalked up to Lyons' 8 governorates.
   Every exact match (legal residency, curfew, host-community interaction,
   the 21-day rCSI food-coping items, the 7-day food-group diet count,
   electricity/toilet/water/cooking-fuel/assets/crowding/shelter-type) is
   built straight off named VASyR items with no proxying.
2. `vasyr_real_example.do` -- imports `vasyr_real_raw.csv`, builds the MLI
   (same Table 2 dimension weights) and runs the 3-stage FGLS. Output:
   `vasyr_real_example.dta`, `vasyr_real_example.log`.

**Results (N=3,490 households, 2025 wave):** headcount H=0.519, intensity
A=0.415, MLI=H\*A=0.216 -- notably higher than Lyons et al.'s 2018 figures
(H=0.365, MLI=0.159), consistent with Lebanon's currency collapse and
deepening economic crisis since 2019-2023. Vulnerability-to-poverty groups:
1,144 chronic poor (32.8%), 536 transient poor (15.4%), 668 escaped poverty
(19.1%), 1,142 non-poor (32.7%); overall vulnerability rate 48.1%. FGLS
Stage-3 coefficients point the expected way: larger/married-head households
and the poorest income quartile are more deprived; an employment-based main
income source is significantly less deprived (matching Lyons et al.'s own
finding), as is each successively richer income quartile.

## All-Stata version: `vasyr_stata_only.do`

Same real 2025 VASyR data and the same mapping as above, but as a single
do-file that imports the two original CSVs directly (no Python step): member
file collapsed to household level with `collapse`/`egen`, main file's two
column names over Stata's 32-character limit captured by CSV column position
(384, 440) rather than typed out, then the same MLI + 3-stage FGLS. It also
drops 5 of 3,549 imported rows with a blank `id` -- a handful of stray
unmatched quote characters in free-text write-in answers make Stata's default
CSV quote-binding merge a few source rows together (noted on import; using
`bindquote(nobind)` to avoid it misaligns far more rows elsewhere in the
file, so dropping the 5 is the smaller fix). Results on N=3,488: H=0.519,
A=0.415, MLI=0.215; 1,152 chronic poor, 541 transient, 658 escaped, 1,137
non-poor; vulnerability rate 48.5% -- matching the Python-built version above
to within the 2-row difference.

## Synthetic fallback: `vasyr_synthetic_example.do`

Kept as a minimal illustration of the method alone, for when the real
microdata isn't at hand. Simulates n=600 households with the same 21
indicators and equal-dimension weights, prevalence calibrated to Lyons et
al.'s Table 2, and a single latent "poverty risk" factor (function of
education, employment, dependents, income group and a governorate shift) so
the FGLS step has something real to estimate. MLI/H/A land in the same
range as the paper (0.180 vs. their 0.159) and the governorate gradient
matches direction (Beirut/Mount Lebanon lower poverty, Baalbek-Hermel/Bekaa
higher). It demonstrates the procedure, not a finding.

## Procedure (both versions)

1. Alkire-Foster MLI: 21 binary indicators across 5 dimensions (health &
   food security, education, living standards, employment, security &
   social inclusion), equal 0.20 weight per dimension split evenly across
   each dimension's indicators (Table 2). Deprivation score = weighted sum;
   poor if score >= 0.33; MLI = H (headcount) x A (average intensity among
   the poor).
2. 3-stage FGLS on the deprivation score (Section 5.2 / Table 4): Stage 1
   OLS of the score on household and geography-FE covariates; Stage 2 OLS
   of the squared residuals on the same covariates for a predicted variance;
   Stage 3 WLS of the score on the covariates, weighted by the inverse of
   that predicted variance. A household is vulnerable if the FGLS-predicted
   probability that its future score exceeds 0.33 is >= 0.5 (eq. 8), i.e. if
   its predicted score itself is >= 0.33 (the model is symmetric normal).
3. Cross-tabulates current poverty x vulnerability into chronic / transient /
   escaped / non-poor, as in the Kedarnath instrument's own VtP do-file
   (`replication/kedarnath_vtp_analysis.do`), which already uses the same
   3-stage FGLS machinery for its MPI arm.
