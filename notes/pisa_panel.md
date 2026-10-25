# PISA 2012–2022 student panel: school loneliness, life satisfaction and digital use

Methods note for `scripts/analysis/32_pisa_panel.py`, report part `scripts/report/parts/pisa_panel.py`, tables `results/tables/pisa_panel_*.csv`.
Plan item: `notes/phase2_plan.md` 1.B.3. Extends the PISA 2022 phone-ban section and the H3 test that used mathematics anxiety as a proxy.

## Access route

| Wave | Files (data/external/pisa_panel/<year>/) | Route |
|---|---|---|
| 2012 | INT_STU12_DEC03.zip (fixed-width text, 1.13 GB unpacked, 480,174 students, 65 systems), INT_SCQ12_DEC03.zip (18,139 schools), SPSS control files | The live OECD links (`www.oecd.org/content/dam/.../pisa-2012-datasets/main-survey/data-sets-in-txt-format/INT_STU12_DEC03.zip`, as used by the EdSurvey R package) return HTTP 403 to curl and WebFetch from this host; `webfs.oecd.org/pisa/INT_STU12_DEC03.zip` and `/pisa2012/` return 404. The two zips were taken from the Internet Archive's 2022-04-02 captures of the former `www.oecd.org/pisa/pisaproducts/` URLs (raw `id_` mode) and pass `unzip -t`; the SPSS control files are still served by www.oecd.org (HTTP 200) and give positions, labels and missing codes. Read straight from the zip with `pandas.read_fwf` in chunks (`extract_2012.py`); never unpacked. |
| 2015 | PUF_SPSS_COMBINED_CMB_STU_QQQ.zip (440 MB; CY6_MS_CMB_STU_QQQ.sav + CY6_MS_CMB_STU_QQ2.sav), PUF_SPSS_COMBINED_CMB_SCH_QQQ.zip, Codebook_CMB.xlsx | webfs.oecd.org (HTTP 200). Life satisfaction ST016Q01NA and the bullying items are in the separate QQ2 file, merged on CNTSTUID. |
| 2018 | SPSS_STU_QQQ.zip (501 MB; STU/CY07_MSU_STU_QQQ.sav), SPSS_SCH_QQQ.zip, PISA2018_CODEBOOK.xlsx | webfs.oecd.org (HTTP 200). |
| 2022 | existing `data/extracts/pisa2022/` (see notes/pisa2022.md) | — |

The student SAVs are unpacked, read with `pyreadstat` `usecols`, and deleted (`extract_sav.py`), so only the verified zips are kept. A machine
restart interrupted the 2015 and 2018 student downloads; they were resumed with `curl -L -C -` (both servers advertise byte ranges) and verified.
Slim parquet files: `data/extracts/pisa_panel/pisa{2012,2015,2018}_{student,school}.parquet`, harmonized stack `pisa_panel_student.parquet`
(`build_panel.py`), item crosswalk `pisa_panel_items.csv`.

## Item mapping (verified against each wave's control file or codebook)

| Harmonized | 2012 | 2015 | 2018 | 2022 | Coding |
|---|---|---|---|---|---|
| lonely / belong / outsider / awkward | ST87Q06 / Q03 / Q01 / Q04 | ST034Q06TA / Q03TA / Q01TA / Q04TA | same | same | 1 = strongly agree or agree (4-point scale, 1 = strongly agree) |
| belong_idx | BELONG (WLE) | BELONG | BELONG | BELONG | as published; each wave is scaled separately (OECD mean 0, SD 1), so levels are not comparable across waves — the item dichotomies are used for trends |
| lifesat | — | ST016Q01NA (QQ2 file) | ST016Q01NA | ST016Q01NA | 0–10; lifesat_low = 0–4, lifesat_high = 9–10 |
| hrs_school | IC05Q01 "Internet at school" (typical weekday) | IC005Q01TA | IC005Q01TA | ST326Q01JA + ST326Q04JA (digital resources at school for learning + for leisure, hours/day) | 2012–18: 7 categories no time, 1–30 min, 31–60 min, 1–2 h, 2–4 h, 4–6 h, >6 h → 0, .25, .75, 1.5, 3, 5, 7 h. 2022: 9 categories none, ≤1, 1–2, …, 6–7, >7 h → .5-step midpoints, learning + leisure summed (leisure-only kept as hrs_school_leis) |
| hrs_out | IC06Q01 "Internet out-of-school – weekday" | IC006Q01TA | IC006Q01TA | ST326Q02JA + ST326Q05JA (before/after school, learning + leisure) | as above |
| hrs_wkend | IC07Q01 | IC007Q01TA | IC007Q01TA | ST326Q03JA + ST326Q06JA | as above |
| sch_1h, out_2h, out_4h | derived | | | | hrs_school > 1; hrs_out > 2; hrs_out > 4 (category boundaries shared by all waves; the ">3 h" cut used for 2022 in Phase 1 is not a boundary in 2012–18) |
| band_out | derived | | | | none, ≤1 h, 1–2 h, 2–4 h, 4–6 h, >6 h |
| first_net_lt7 / lt10 | IC04Q01 (≤6, 7–9, 10–12, 13+, never) | IC004Q01TA (same) | IC004Q01HA (≤3, 4–6, 7–9, 10–12, 13+, never) | — | lt7 = first Internet access at ≤6 (2018: ≤3 or 4–6); lt10 adds 7–9 |
| socnet_daily | IC08Q05 | IC008Q05TA | IC008Q05TA | — | almost every day / every day |
| chat_school_daily | IC10Q01 | IC011Q01TA | IC011Q01TA | — | chatting online at school almost every day / every day |
| phone_school_daily | — | — | — | IC170Q02JA | every day / several times a day (not available = 0) |
| anxtest, anx1–5 | — | ANXTEST (WLE), ST118Q01NA–Q05NA (1 strongly disagree … 4 strongly agree) | — | — | ANXTEST standardized over the analysis sample; hi_anx = above country median |
| anxmat | ANXMAT | — | — | ANXMAT | wave-specific scaling |
| sch_policy | — | — | school SC156Q01HA "its own written statement about the use of digital devices" | — | 1 yes, 0 no |
| ban | — | — | — | school SC190Q02JA | 1 yes |
| private | school SC01Q01 | school SC013Q01TA | school SC013Q01TA | school PRIVATESCH | 1 private |
| girl, grade, age, escs, immig, wt, oecd | ST04Q01, GRADE, AGE, ESCS, IMMIG, W_FSTUWT, OECD | ST004D01T, … | … | … | 2015 OECD code 2 ("not applicable", sub-national entities) → 0 |
| ict_country | derived | | | | 1 if more than half of the system's students answered hrs_out (ICT familiarity module administered) |

School policy items before 2022: none on phones. 2012 school file has computer counts (SC11), shortages (SC14Q07–09) and a maths computer-use
policy item (SC40Q01); 2015 only computer counts and ratios (SC004, RATCMP1/2); 2018 adds the digital-device capacity battery SC155 and the
policy/statement battery SC156, of which SC156Q01HA is used.

Rotated design in 2012: the student questionnaire had three forms and each student answered two of the three rotated blocks; the belonging block
(ST87) and the ICT module (separate booklet in 43 systems) are therefore missing for about a third of students by design. The final student
weight is used without adjustment, as OECD does for rotated items.

## Analyses (all with W_FSTUWT; student-level models have country fixed effects and school-clustered SEs via pyfixest CRV1)

1. Country × sex × wave weighted means (`_country_wave.csv`) and trends as unweighted means of country means (`_trends.csv`), both for all
   systems that asked an item and for balanced sets (item present in every wave shown). An item counts as asked when more than half of the
   system's students answered it.
2. Two-way fixed-effects panel (`_fe.csv`): cell means of lonely, belong, life satisfaction (and the 0–4 share) on mean in-school and
   out-of-school hours (or the >1 h / >4 h shares, reported per 10 pp), country and wave FE, with and without mean ESCS, clustered by country,
   ICT-module systems observed in at least two waves; 2012–2018 (identical item) and 2012–2022 (2022 total device hours, flagged).
3. Long differences (`_longdiff.csv`, `_longdiff_fit.csv`): 2012→2018 for loneliness and belonging, 2015→2018 and 2018→2022 for life
   satisfaction, with OLS slopes of the outcome change on the hours change across systems (robust SEs) and the correlation.
4. 2015 student-level H3 test (`_h3_2015.csv`, `_h3_desc.csv`): outcome ~ anx + sch_1h + out_4h + anx×sch_1h + anx×out_4h + ESCS + grade
   (+ sex) | country, by sex; anx is ANXTEST in SD units (also the above-median indicator and a continuous-hours version). Outcomes: lonely,
   belong (pp), life satisfaction (points), life satisfaction 0–4 (pp), belonging index (hundredths of SD).
5. Dose–response by wave (`_dose.csv`, `_dose_slope.csv`, `_dose_steepen.csv`): weighted means and country-FE contrasts of life
   satisfaction and loneliness by out-of-school hours band (reference 1–2 h), by sex and wave; linear slopes per hour (in-school and out-of-
   school jointly); and a pooled 2015+2018 model on systems with the module in both waves with slope × 2018 interactions (country-wave FE),
   which is the test of steepening. 2022 is shown with its own item and flagged.
6. 2018 school policy (`_policy2018.csv`): outcome ~ sch_policy + ESCS + private + grade (+ sex) | country, school-clustered, by sex, for
   in-school use (chatting at school daily, >1 h, hours), out-of-school >4 h (placebo), loneliness, belonging, life satisfaction.

## Literature (verified where marked)

- Twenge, Haidt, Blake, McAllister, Lemon, Le Roy (2021) "Worldwide increases in adolescent loneliness", *J. Adolescence* 93: 257–269,
  https://doi.org/10.1016/j.adolescence.2021.06.006. Abstract (Europe PMC, verified): PISA 2000, 2003, 2012, 2015, 2018; 37 countries;
  n = 1,049,784; school loneliness (the six ST034 items) rose 2012–2018 in 36 of 37 countries, more among girls; higher where smartphone
  access and Internet use were higher; unemployment negatively related; GDP, inequality and fertility unrelated.
- Haidt and Rausch (2026) World Happiness Report chapter "Social media is harming adolescents at a scale large enough to cause changes at the
  population level", https://www.worldhappiness.report/ed/2026/social-media-is-harming-adolescents-at-a-scale-large-enough-to-cause-changes-at-the-population-level/
  (verified from the page): 40 of 47 PISA systems with 2015 and 2018 data show significant life-satisfaction declines, "strong and universal for
  both boys and girls"; school loneliness up 2012–2018 in 34 of 35 countries.
- OECD (2017) PISA 2015 Results (Volume III): Students' Well-Being, https://doi.org/10.1787/9789264273856-en. Overview PDF (verified):
  OECD-average life satisfaction 7.31, 34.1% very satisfied (9–10), 11.8% not satisfied (0–4); 29% of girls vs 39% of boys very satisfied,
  14% of girls vs 9% of boys not satisfied; 85% disagree that they feel lonely at school; 59% often worry that a test will be difficult, 66%
  worry about poor grades, 55% very anxious even if well prepared; "extreme Internet users" (>6 h/weekday outside school) report life
  satisfaction 0.4 points lower and 17% lonely vs 14% (low), 12% (moderate, 1–2 h) and 13% (high, 2–6 h); 16% exceed 6 h on weekdays, 26% on weekends.
- OECD (2019) PISA 2018 Results (Volume III): What School Life Means for Students' Lives, https://doi.org/10.1787/acd78851-en. From the OECD
  summary page (the volume itself is not reachable from this host, HTTP 403): 67% of students satisfied (7–10) on average across OECD countries,
  down 5 pp from 2015; agreement with "I make friends easily" and "I feel like I belong at school" down about 2 pp 2015–2018 (Table III.B1.9.2).
  Not independently verified against the volume text.
- OECD PISA 2022 country notes (not reachable from this host) are quoted in search results as giving an OECD-average 16% lonely at school in
  2022 and a not-satisfied share rising from 11% (2015) to 16% (2018) and 18% (2022); unverified — the harmonized file reproduces these series directly.
- Mao and See (2025) "Early Exposure, ICT Use, and Teenage Well-being Outcomes", CHILD Working Paper 121, Collegio Carlo Alberto,
  https://econpapers.repec.org/RePEc:cca:wchild:121 (abstract): PISA 2015 and 2018; early device exposure (≤6) instrumented by parental-
  occupation ICT intensity raises school belonging at 15, no clear effect on life satisfaction.
- Fang and Mo (2026) "The impact of educational digitalization on life satisfaction: an empirical analysis based on PISA 2022", *Frontiers in
  Psychology* 17: 1740535, https://doi.org/10.3389/fpsyg.2026.1740535 (PMC, verified): n = 41,490; school digitalisation (IC172) → life
  satisfaction direct β = 0.032 in PLS-SEM; cross-sectional.
- Critiques: no published reanalysis of the Twenge et al. PISA loneliness trend was found in two searches; the relevant methodological
  literature concerns measurement invariance of PISA affective scales across countries (e.g. a five-factor PISA 2018 well-being model reached
  metric invariance in 9 of 36 country tests and scalar invariance in 1; Coventry/Nazarbayev group). The 2012→2015 shift from paper to
  computer administration in most systems (ADMINMODE) is a candidate artefact for the 2012–2015 step in the loneliness series.
- "Marciano et al." in the brief: no PISA-based Marciano paper was found; her work (Marciano, Camerini et al.) uses Swiss cohorts and reviews.

## Results summary (results/tables/pisa_panel_*.csv, run 2026-10-24)

Samples: 2012 480,174 students / 65 systems (43 ICT); 2015 519,334 / 73 (46 ICT; life satisfaction in 50); 2018 612,004 / 80 (53 ICT; life
satisfaction in 72); 2022 613,744 / 80 (75 with ST326 hours; life satisfaction in 73). Pooled weighted loneliness 12.2, 15.9, 19.0, 19.7%;
life satisfaction 7.33, 7.11, 6.90; Internet hours outside school on weekdays 2.09, 2.84, 3.56 (2022 total device hours 3.63).

Trends (balanced sets, mean of country means): lonely girls 10.4 → 15.7 → 16.4 → 18.4%, boys 12.8 → 16.1 → 17.1 → 15.8% (53 systems);
OECD girls 8.6 → 15.5 → 16.2 → 18.4, OECD boys 9.3 → 14.1 → 14.9 → 14.1. Belong (all) 81.8 → 73.2 → 71.0 → 75.2%. Life satisfaction (41
systems) girls 7.16 → 6.82 → 6.37, boys 7.62 → 7.38 → 7.23; share at 0–4 girls 13.7 → 18.2 → 21.9%, boys 9.9 → 13.7 → 13.8%. ICT systems
(2012–2018 balanced): out-of-school hours 2.37 → 3.14 → 3.62, >4 h 18.8 → 32.5 → 40.5%; in-school 0.65 → 1.17 → 1.59 h, >1 h 16.9 → 29.2 →
39.7%; first Internet access before 10: 54.7 → 60.0 → 64.4%; social networks daily flat at 72–74%. The largest loneliness step (2012 → 2015)
coincides with the paper-to-computer mode change.

Two-way FE (country + wave, ESCS, clustered by country; coefficient per hour per weekday, 2012–2018, 43 systems, 118 cells per sex):
lonely — out-of-school −0.81 (1.16) girls, −0.08 (1.55) boys; in-school +1.40 (1.02), +0.95 (1.37). Belong — out-of-school −2.33 (0.92) girls,
−2.62 (1.23) boys; in-school −2.03 (1.30), −0.70 (1.81). Life satisfaction (2015–2018, 33 systems) — out-of-school +0.10 (0.15), +0.05 (0.21).
2012–2022 (2022 total device hours; 56 systems): belong out-of-school −1.38 (0.84) girls, −1.00 (0.89) boys; others near zero.
Long differences 2012→2018 (34 systems): Δlonely +6.9 pp girls / +5.6 boys, Δhrs_out +1.41 / +1.15 h; slope of Δlonely on Δhrs_out −1.00 (1.49),
−0.78 (1.66); Δbelong −10.2 / −9.7 pp, slope −2.07 (1.09) r = −0.27, −2.86 (0.98) r = −0.32. 2015→2018 (33): Δlifesat −0.33 / −0.21, slope +0.09
(0.11), +0.09 (0.21). 2018→2022 (42): Δlifesat −0.45 / −0.13, slope +0.05 (0.06), −0.01 (0.07).

2015 H3 (46 systems, 310,964 students; ANXTEST per SD; country FE, ESCS, grade, school-clustered): anxiety main effect lonely +4.05 (0.27)
girls / +1.84 (0.26) boys, life satisfaction −0.351 (0.017) / −0.243 (0.017). In-school >1 h: lonely +1.29 (0.45) / +2.15 (0.46), life
satisfaction +0.030 (0.028) / +0.082 (0.028). Out-of-school >4 h: lonely +1.57 (0.42) / +0.29 (0.45), life satisfaction −0.340 (0.027) /
−0.123 (0.025). Interactions anxiety × in-school: lonely −1.00 (0.49) / +0.39 (0.49), life satisfaction +0.047 (0.031) / +0.016 (0.032);
anxiety × out-of-school: lonely −1.42 (0.43) / −0.70 (0.43), life satisfaction +0.091 (0.029) / +0.099 (0.029). Same signs with the above-
median split and the continuous-hours version. High-anxiety students are not heavier users (24.1 vs 23.8% >1 h at school; 31.8 vs 29.9% >4 h
outside school among girls).

Dose–response (country-FE contrasts vs 1–2 h, ESCS, grade): life satisfaction, girls, >6 h: −0.42 (2015), −0.60 (2018), −0.42 (2022 item);
boys −0.19, −0.36, −0.14; none: −0.22 / −0.35 (girls 2015/2018). Share at 0–4, girls >6 h: +5.5, +8.3, +5.3 pp. Linear slopes per hour outside
school (life satisfaction): girls −0.065 (0.005) 2015, −0.095 (0.009) 2018, −0.040 (0.005) 2022; boys −0.030, −0.053, −0.024. Steepening test
(40 systems in both 2015 and 2018, country-wave FE): girls 2015 slope −0.063 (0.006), change in 2018 −0.022 (0.010); boys −0.027 (0.006),
−0.026 (0.009); share at 0–4: +0.305 (0.136), +0.274 (0.124) pp per hour. Loneliness: out-of-school slope ≈ 0 (girls +0.09 (0.10), boys
−0.22 (0.11)); in-school slope +0.52 (0.14) girls, +0.98 (0.14) boys pp per hour, 2018 changes −0.02 (0.19), −0.12 (0.19).

2018 written digital-device policy (SC156Q01HA; 570,172 students with ESCS and grade in 80 systems, 62.7% in policy schools; 64% in the
loneliness regression sample of 505,479 students in 77 systems): >1 h at school +2.79 (0.79) pp,
chatting at school daily +0.17 (0.63), out-of-school >4 h +1.08 (0.63) (placebo), lonely −0.67 (0.35) (girls −0.02 (0.47), boys −1.29
(0.49)), belong +0.67 (0.42), belonging index +2.7 (0.85) hundredths SD, life satisfaction +0.02 (0.03).

Reading: trends match H1/H2's premise; the within-country panel ties out-of-school hours to belonging but not to loneliness or life
satisfaction; the student-level gradient is J-shaped, steeper for girls, and steepened 2015 → 2018; in-school use relates to school
loneliness and out-of-school use to life satisfaction; test anxiety does not amplify either (interactions opposite to H3); the 2012 → 2015
step is a mode-change candidate (H0). Gaps: no pre-2022 phone-ban item; 2022 hours item not comparable; no U.S. in the ICT module before
2018; the 2012 ICT module was a separate optional booklet.
