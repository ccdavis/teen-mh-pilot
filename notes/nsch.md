# NSCH 2016-2025: parent-reported anxiety/depression, screen time, state adoption and state phone bans (Phase 2, item 1.A.2)

Built 2026-10-24. Scripts: `scripts/download/nsch/fetch_nsch.py` (download), `scripts/download/nsch/extract_nsch.py` (slim parquet),
`scripts/analysis/28_nsch.py` (all tests; tables `results/tables/nsch_*.csv`), `scripts/report/parts/nsch.py` (report section).
Raw files and their documentation: `data/external/nsch/README.md`. Extract: `data/extracts/nsch/nsch_6_17.parquet` (293,751 children 6-17).

## 1. Access route

Census posts the public-use topical files by year at `https://www2.census.gov/programs-surveys/nsch/datasets/<year>/` as SAS and Stata
zips (no CSV; the guessed `nsch_2023e_topical_CSV.zip` and `nsch_2024e_topical_CSV.zip` therefore 404). Directory listings work and
nothing is blocked. Files: `nsch_<year>_topical_Stata.zip` for 2016-2022, 2024, 2025 and `nsch_2023e_topical_Stata.zip` for 2023; each
unzips to `nsch_<year>e_topical.dta` plus a `.do` carrying variable and value labels. 2024 is released and so is 2025 (posted
2026-10-05, 45,139 children). Codebooks (`<year>-NSCH-Topical-Variable-List.pdf`), frequencies, methodology reports, FAQs, the
multi-year and analytic guides and the 2016-2019 crosswalk were downloaded from `technical-documentation/{codebook,methodology}/`.
The earlier NCHS telephone rounds (2003, 2007, 2011-12) were not pulled: different mode, different screen-time item (TV hours only
plus a separate computer item) and no "currently has" follow-up in 2003; they would not extend any of the tests below.

Blocked: the HRSA MCHB data brief on adolescent mental and behavioral health (2023 data),
`https://mchb.hrsa.gov/sites/default/files/mchb/data-research/nsch-data-brief-adolescent-mental-behavioral-health-2023.pdf`, returns an
Akamai "Access Denied" (HTTP 403) page to curl, to curl with browser headers and to WebFetch from this host; the HRSA landing page
403s as well. Its figures in `nsch_literature.csv` come from a search-engine summary and are flagged unverified. NCBI Bookshelf
(`NBK608531`, the same brief) sits behind a reCAPTCHA.

## 2. Design, weights, variance

Address-based mail/web survey, one randomly selected child per household, stratified by state (and within state by a
high-child-probability stratum, `STRATUM` 1/2A). Field period runs from June of the survey year into the following January-March
(2016: 2016-06-10 to 2017-01; 2017: 2017-08-07 to 2018-02; 2023: 2023-06-23 to 2024-01-19; 2024: 2024-06-21 to 2025-02-07;
2025: 2025-06-20 to 2026-03-06). Weighted overall response rates: 40.7, 37.4, 43.1, 42.4, 42.4, 40.3, 39.1, 35.8, 36.3, 34.7% for
2016-2025. The public file has no interview date, so exposure to a school-year policy can only be assigned by survey year.
Weight `FWC` (child weight, sums to the child population of each state); the Census guide says to divide by the number of years when
pooling, which does not change weighted means or regression coefficients. The sampling unit is the household, so there is no cluster
below the state stratum: individual-level models use heteroskedasticity-robust (HC1) standard errors with `FWC` as weights; state-year
panels and the ban and adoption models cluster by state (51 clusters). Cell standard errors in the trend tables are the design-free
weighted-binomial approximation `sqrt(sum(w^2 (x-p)^2))/sum(w)`, which ignores stratification (slightly conservative).

Children aged 6-17 kept per year (0-17 file totals in parentheses): 2016 35,718 (50,212); 2017 15,438 (21,599); 2018 21,954 (30,530);
2019 21,259 (29,433); 2020 30,636 (42,777); 2021 30,173 (50,892); 2022 34,362 (54,103); 2023 33,638 (55,162); 2024 37,534 (51,375);
2025 33,039 (45,139). Ages 12-17: 20,708; 8,909; 12,587; 12,230; 17,539; 16,166; 19,028; 18,397; 21,960; 19,691 (176,215 in all).

## 3. Items and coding (variable names are lower-case in the Stata files; `nsch_items.csv` lists years present)

Mental health (all forms, all years, identical wording 2016-2025):
- `K2Q33A` "Has a doctor or other health care provider EVER told you that this child has ... Anxiety Problems?" (1 yes, 2 no);
  `K2Q33B` "If yes, does this child CURRENTLY have these problems?"; `K2Q33C` "If yes, are they: 1 Mild 2 Moderate 3 Severe".
- `K2Q32A/B/C` the same for Depression; `K2Q31A/B/C` ADD/ADHD; `K2Q34A/B/C` "Behavioral or Conduct Problems" (this header adds
  "or educator" to the provider list).
- Coding: `anx_cur` = 1 if ever told and currently yes, 0 if never told or told but not current, NaN otherwise; `anx_modsev` = current
  and moderate/severe (mild current coded 0). Same for `dep_*`, `adhd_cur`, `beh_cur`. `anx_ever`, `dep_ever` are the ever-told items.
- HRSA's briefs note that 2016-2017 responses to the condition items differ in pattern from 2018+; the wording itself did not change.
  The trend tables keep all years and the part shows 2016-17 on the same axis, flagged in the caption of the field-period note.

Screen time (the key item change):
- 2016-2017: two items, `K7Q60_R` "ON AN AVERAGE WEEKDAY, about how much time does this child usually spend in front of a TV watching TV
  programs, videos, or playing video games?" and `K7Q91_R` "... spend with computers, cell phones, handheld video games, and other
  electronic devices, doing things other than schoolwork?", each 1 None, 2 <1 h, 3 1 h, 4 2 h, 5 3 h, 6 4+ h.
- 2018-2025: one item `SCREENTIME` "ON MOST WEEKDAYS, about how much time did this child spend in front of a TV, computer, cellphone or
  other electronic device watching programs, playing games, accessing the internet or using social media? Do not include time spent
  doing schoolwork." 1 <1 h, 2 1 h, 3 2 h, 4 3 h, 5 4+ h. (Wu et al. 2024 likewise drop 2016-17 as non-comparable.)
- Coding: `screen_cat` (five labels), `screen_hrs` midpoints 0.5/1/2/3/4.5, dummies `scr_lt1`, `scr_2`, `scr_3`, `scr_4p` with 1 hour as
  the reference (the category with the lowest prevalence and the published inflection point). 2016-17: `screen_hrs_1617` = sum of the
  two items' midpoints (0, .5, 1, 2, 3, 4.5 each; range 0-9), used only in a separate 2016-2017 block of `nsch_screen_gradient.csv`.
  The 2018 item change is not a 2019 change: the brief's "changed in 2019?" question is answered "2018".

Sleep, bullying, engagement, activity, neighbourhood (forms T2/T3 = ages 6-17 unless noted):
- `HOURSLEEP` "DURING THE PAST WEEK, how many hours of sleep did this child get on most weeknights?" 1 <6 ... 4 8 h ... 7 11+;
  `sleep_lt8` = codes 1-3; `HOURSLEEP05` is the 0-5 version (naps included) and is not used.
- Bullying: 2016-17 `BULLIED` "How well do each of the following phrases describe this child? ... is bullied, picked on, or excluded by
  other children" (definitely/somewhat/not true); 2018+ `BULLIED_R` "DURING THE PAST 12 MONTHS, how often was this child bullied, picked
  on, or excluded by other children?" 1 never, 2 1-2 times, 3 1-2 times/month, 4 1-2 times/week, 5 almost every day, and `BULLY`
  (perpetration) with the same scale. `bullied_monthly` = codes 3-5, `bullied_weekly` = 4-5, `bullied_any` = 2-5; 2016-17 kept as
  `bullied_true_1617` and not pooled.
- School engagement `K7Q82_R` cares about doing well in school, `K7Q83_R` does all required homework (2016-17 definitely/somewhat/not
  true; 2018+ always/usually/sometimes/never); flourishing `K6Q71_R` curiosity, `K6Q73_R` bounces back, `K7Q70_R` argues, `K7Q84_R`,
  `K7Q85_R` on the same changing scale. `engaged` = always/usually on both school items, 2018+ only.
- `K7Q02R_R` days missed school (1 none ... 5 11+, 6 not enrolled); `PHYSACTIV` days with 60 min activity (1 0 days ... 4 every day);
  `K10Q40_R`/`K10Q41_R` child is safe in neighbourhood/at school (definitely agree ... definitely disagree); `K10Q11-14` neighbourhood
  amenities; `K7Q30-33` sports, clubs, lessons, events; `MAKEFRIEND`; `K4Q22_R` saw a mental health professional in the past 12 months
  (1 yes, 2 no but needed, 3 no, not needed); `OUTDOORSWKDAY/WKEND` outdoor play exist only for 2021-2024 and only on the 0-5 form (T1),
  so there is no outdoor-play item for 6-17; `GRADES` (2022+), `VAPE` (2022+), `BODYIMAGE` (2022+) are kept in the extract but unused.
- Covariates: `SC_AGE_YEARS`, `SC_SEX` (1 male, 2 female), `SC_RACE_R` x `SC_HISPANIC_R` -> `raceeth` (Hispanic; White, Black, Asian,
  other/multiracial non-Hispanic; the 2025 file drops the "some other race alone" code), `FPL_I1` (first of six poverty-ratio implicates,
  50-400, capped by Census) -> `fpl_cat` <100/100-199/200-399/400+, `HIGRADE` highest adult education (<HS, HS, >HS) -> `pared`,
  `FIPSST` state, `METRO_YN`/`MPC_YN`, `A1_MENTHEALTH` caregiver's own mental health (kept, not used).

## 4. Tests and specifications (`scripts/analysis/28_nsch.py`)

1. Screen gradient (`nsch_screen_gradient.csv`, `nsch_screen_prevalence.csv`): 2018-2025 pooled; `outcome*100 ~ scr_lt1 + scr_2 + scr_3 +
   scr_4p + C(age) + girl + C(raceeth) + C(fpl_cat) + C(pared) | state^year`, weights FWC, HC1; by sex (all/girls/boys) and age group
   (6-11, 12-17, 6-17); outcomes current anxiety, depression, moderate/severe versions, ADD/ADHD and behavior problems as contrasts;
   also a linear per-hour slope, a year-FE-only 4+ h coefficient, period splits 2018-19 and 2022-25, and the 2016-17 summed-item block.
2. Trends (`nsch_trends_state_year.csv`): weighted prevalence, SE and n by year x state (0 = national) x sex x age group for anxiety,
   depression, ADHD, moderate/severe, ever-told, 4+ h screen, sleep <8 h, monthly bullying, mental-health treatment.
3. Adoption (`nsch_adoption.csv`): state-year 12-17 (and 6-11) rates merged with the NTIA `hh_teen12_17` /
   `person_uses_smartphone_internet` share, waves Nov 2017, 2019, 2021, 2023, linearly interpolated within 2017-2023 (primary) and
   flat-extrapolated to 2016 and 2024-25 (sensitivity, as `19_us_dose_rttt.py` does); `rate ~ smart10 | state + year`, weights = cell n,
   CRV1 state. The NTIA cross-state mean/SD/min/max by wave is appended to the same table.
4. Phone bans (`nsch_ban_did.csv`, `nsch_florida_series.csv`): `data/compiled/phone_bans/state_phone_bans.csv`; mandates = policy_type
   "statewide bell-to-bell ban" or "ban during instructional time" with `effective_school_year` start year s (Florida 2023; Indiana,
   Louisiana, South Carolina 2024; 19 states 2025); "requires districts to adopt a policy" states (Minnesota 2024; Alaska, Arizona,
   Idaho, New Mexico 2025) get a separate `polreq_post` indicator. Because the field period (June to winter) straddles the school-year
   start, survey year s is coded `post_partial` (took effect during the field period) and years >= s+1 `post_full`. Designs: state-year
   panel DiD (cell n weights, CRV1 state), individual DiD with the covariates above and state + year FE (FWC, CRV1 state), event studies
   with k = year - s in {<= -4, -3, -2, [-1], 0, +1, +2}, a Florida-only panel (other mandate states dropped once treated), and the 6-11
   age group as a low-exposure comparison (the bans cover K-12 but few 6-11-year-olds carry phones). Identification: "+1" rests on four
   states (one year each), "+2" on Florida alone; 2025 is also the year the national series turns down.
5. Mediators (`nsch_mediators.csv`): screen dummies -> sleep <8 h, bullied monthly/weekly, engaged, daily activity (same specification
   as 1); then the anxiety/depression/ADHD gradient with sleep and bullying added as controls (attenuation = 1 - with/without).
6. Literature (`nsch_literature.csv`): hand-entered rows with URL and a `verified` flag.

## 5. Results summary (all numbers are in `results/tables/nsch_*.csv`; the part reads them from there)

Trends (national, weighted, ages 12-17): girls' current anxiety 11.5% (2016) -> 13.7 (2018) -> 16.3 (2020) -> 20.2 (2022) -> 21.7%
(2024) -> 17.3% (2025); girls' current depression 6.8 -> 12.4% (2022) -> 10.6 (2024) -> 8.3% (2025); boys' anxiety 8.5 -> 12.3% (2024)
-> 12.2% (2025), boys' depression 4.9 -> 5.3-6.5% flat. Ages 6-11 anxiety 6.9 -> 9.7% (2024) -> 9.4% (2025). The 2025 wave is the
first decline in the series (girls' anxiety -4.3 pp, SE 0.8; depression -2.3, SE 0.6), coinciding with the lowest response rate (34.7%)
and an extended field period (to 2026-03-06).

Screen gradient (2018-2025 pooled, 4+ h vs 1 h, covariates + state x year FE, HC1): girls 12-17 anxiety +14.5 (SE 1.0) pp, depression
+10.2 (0.8); boys 12-17 +7.0 (0.8) and +5.5 (0.6); girls 6-11 anxiety +5.5 (0.8); contrasts: ADD/ADHD boys 12-17 +7.2 (1.1), behavior
problems boys 6-11 +8.3 (1.0). Year-FE-only 4+ h coefficient for girls' anxiety is about the same as the covariate-adjusted one. Per-hour
slopes for 12-17 girls' anxiety are similar in 2018-19, 2022-25 and the summed 2016-17 items. 4+ h share: 38% of 12-17, 18% of 6-11.
Comparison values from Phase 1 tables: GSHS girls 3+ h mobile phone: loneliness +8.2 (1.4), suicidal ideation +10.1 (1.5) pp; MICS girls
15-17 own daily internet/phone use within cluster: -0.1 (1.4) / -2.2 (1.2) pp on caregiver-reported anxiety.

Mediators (12-17, 2018-2025): 4+ h vs 1 h -> sleep <8 h +10.6 (SE 1.2) pp girls, +9.2 (1.2) boys; bullied monthly+ +8.6 (0.7) girls,
+5.4 (0.7) boys; adding sleep and
bullying lowers the girls' 4+ h anxiety coefficient from 14.6 to 11.4 (22% attenuation) and depression from 10.1 to 7.6 (25%); boys
7.1 -> 5.1 and 5.3 -> 3.9. Sleep alone attenuates 5%; bullying does most of it.

Adoption (NTIA teen-household smartphone-internet share, 2017-2023 within waves, state + year FE, CRV1 state, 357 state-years):
girls 12-17 anxiety +0.34 (SE 0.7) pp per +10 points, depression -0.62 (0.6); boys -0.57 (0.7) and +0.06 (0.5). The NTIA share was
already 57.3% in 2017 (cross-state SD 5.9) and 62.8% in 2023 (SD 5.6): no adoption transition remains in the NSCH years, so this is a
null-variation result, as the brief anticipated.

Phone bans (12-17; `nsch_ban_did.csv`, `nsch_ban_permutation.csv`, `nsch_ban_florida_placebo.csv`, `nsch_florida_series.csv`).
Treated: Florida (full years 2024, 2025), Indiana, Louisiana, South Carolina (full year 2025), 19 states with 2025-26 mandates (event
time 0 only in 2025). Florida's own series is thin (96-192 girls 12-17 per year; girls' anxiety 22.6% in 2022, 13.5, 13.8, 12.0% in
2023-25 vs 20.0, 20.5, 22.2, 17.6% elsewhere). Full-year DiD on girls' anxiety: individual, population-weighted -5.57 (CRV1 2.29);
state-year panel, equal state weights -1.58 (2.12); panel, population weights -5.18 (2.23). Boys: -3.05 (1.04) / -3.96 (1.28) / -2.73
(1.04). Depression: girls -0.97 (0.66) / +0.04 (0.87); boys -0.42 (0.62) / -1.40 (1.01). Permutation inference (observed schedule
reassigned 400 times; two-sided p = share of placebo |coef| >= observed): girls' anxiety p 0.44 (equal) / 0.05 (population); boys 0.00 /
0.17; girls' ADHD contrast -3.83 (p 0.025) / -4.03 (p 0.04). Pre-trend leads small (girls anxiety -1.45 (1.30) at -2, +0.08 (1.05) at -3).
Ages 6-11 move the other way (+0.5 / +2.4 pp, p 0.72 / 0.20). Florida-only design (each of the 16 never-mandate states treated alone from
2023-24 as placebo, n = 16): girls' anxiety -6.25 is below every placebo (SD 2.79, p 0.06) and so is girls' ADHD -4.06 (p 0.00); boys
-2.09 (p 0.38). Reading: the early-ban states' parents report fewer anxiety diagnoses after the mandates, but ADHD falls as much,
depression does not fall, the magnitude depends on weighting, and two-year effects rest on Florida alone. No ban-specific signal; the
cluster-robust SEs in the Florida-only rows (0.3-0.6) are not valid with one treated cluster and the part uses the placebo distribution
instead. Rerun when the 2026 file adds full post-years for the 2025-26 wave (the script reads treatment timing from the compiled ban table).

## 6. Gaps and follow-ups

- No interview month in the public file; the school-year exposure coding is approximate. The restricted-use NSCH (Census RDC) has
  interview dates and county, which would allow a within-year before/after design around the August school-year start and the
  Orange County (FL) bell-to-bell ban.
- The ban test identifies two post years from one state; the 2026 and 2027 files will add the 2025-26 wave's full years (19 states)
  and should be rerun with the same script (treatment coding reads the compiled ban table, so updating that table is enough).
- Parent-reported diagnosed conditions depend on access to care; the `K4Q22_R` treatment item is in the trend tables for that purpose
  but not analysed further.
- 2016-17 are not pooled with 2018+ for screen time, bullying or engagement; the trend tables show them side by side.
- Literature: the HRSA data brief and the Forrest et al. 2025 JAMA figures could not be verified against the source from this host.
