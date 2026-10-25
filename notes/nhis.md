# NHIS Sample Child 2021–2024 and NHIS-Teen: parent vs teen report of adolescent anxiety and depression (Phase 2, item 1.A.1)

Compiled 2026-10-24. Scripts: `scripts/download/nhis/01_download_nhis.py` (acquisition + manifest), `02_extract_child.py` (slim parquet
`data/extracts/nhis/child_2021_2024.parquet`, 31,777 sample children 0–17), `03_compile_teen_published.py` (`data/compiled/nhis/nhis_teen_query_tool.csv`,
`nhis_teen_published.csv`), `scripts/analysis/27_nhis_teen_parent.py` (results `results/tables/nhis_*.csv`), report part `scripts/report/parts/nhis.py`.
Raw files and their documentation: `data/external/nhis/README.md`.

## Access route and what was blocked

- NHIS Sample Child public-use CSVs 2021–2024, codebooks, survey descriptions: downloaded from ftp.cdc.gov (all 200 OK; 38 files, 65.8 MB; SHA-256 in
  `data/external/nhis/manifest.csv`).
- **NHIS-Teen microdata: not public.** https://www.cdc.gov/nchs/nhis/teen/index.html: "NHIS-Teen data are available only through the NCHS Research Data
  Center (RDC). There is no public-use NHIS-Teen file available." Probed and absent: `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHIS/2022/teen2122csv.zip`
  (404), `.../Datasets/NHIS/NHIS-Teen/`, `.../Datasets/NHIS-Teen/`, `.../Datasets/NHIS/teen/` (all 404); the 2021–2025 year directories contain only
  adult/child/income/paradata/pair-weight files; the IPUMS internal NHIS/IHIS trees on gp1.pop.umn.edu have no teen files. The public Sample Child files carry
  no NHIS-Teen permission or participation flag, so the linked sample cannot be identified either.
- Consequence: the person-level tests in the plan (agreement/kappa between parent items and teen PHQ-2/GAD-2; screen gradient on the same adolescents
  under both informants; severity, sex and age moderation of agreement; sleep/bullying controls on the teen gradient) cannot be run from public data.
  They are replaced by (a) population-level comparisons of the two informants for the same months and the same parent-reported subgroups, using the
  NCHS public aggregates, and (b) a comparison of each informant's own-report gradient (parent screen item → parent symptom items in the public file;
  teen screen hours → teen PHQ-2/GAD-2 from NCHS Data Brief 513 / Zablotsky et al. 2025). An RDC proposal is required for the linked test.

## Items and coding

Parent (Sample Child; respondent is the parent/guardian in nearly all cases):
- `ANXFREQ_C` "How often does [child] seem very anxious, nervous, or worried? daily, weekly, monthly, a few times a year, or never" (ages 5–17; same wording as
  MICS CF items). `anx_dw` = daily or weekly; `anx_daily` = daily. `DEPFREQ_C` "seem very sad or depressed" → `dep_dw`, `dep_daily`. 7/8/9 set to missing
  (≤0.4% of 12–17-year-olds). No ANXLEVEL/DEPLEVEL and no diagnosed-anxiety/depression item exist in these files.
- `SCREENTIME_C` (2022, 2024 only): "On most weekdays, does [child] spend more than 2 hours a day in front of a TV, computer, cellphone or other electronic device
  watching programs, playing games, accessing the internet, or using social media? Do not include time spent doing school work" → `scr2` (1 yes / 0 no).
  Yes/no with a 2-hour threshold: 81% of 12–17-year-olds are "yes", so it separates light users from everyone else, not heavy users from the rest.
- `BULLYVIC_C` (2021, 2022 only; ages 12–17): frequency bullied, picked on or excluded in past 12 months → `bully_any` (≥ 1–2 times), `bully_month` (≥ 1–2 per month).
- `MHRX_C`, `MHTHRPY_C` (past-12-month medication / counseling for emotions, concentration, behavior or mental health) → `mhcare` = either.
- Covariates: `AGEP_C` (single years), `SEX_C`, `HISPALLP_C` (collapsed to Hispanic / NH White / NH Black / NH Asian / NH other), `RATCAT_C` (<200% / 200–399% / 400+% FPL,
  first imputed-income value), `MAXEDUCP_C` (HS or less / some college or associate / bachelor's+), `REGION`, `URBRRL` (large metro / medium-small metro / nonmetro;
  2024 uses the 2023 scheme `URBRRL23`), `SRVY_YR`. Unknown covariate values are kept as an "Unknown" category.
- Weights `WTFA_C`; SEs clustered on `PSTRAT` × `PPSU` (PSU codes repeat across strata). The hand linearisation in `wm()` matches pyfixest CRV1 to three decimals.
- NHIS-Teen fielding periods: July 2021–Dec 2022 (18 m) and July 2021–Dec 2023 (30 m). Parent estimates for those periods use 2021 Q3–Q4 (`INTV_QRT` ≥ 3) with
  2021 weights doubled, plus full 2022 (and 2023). Only the relative year weights matter for proportions.

Teen (NHIS-Teen, self-administered web/paper; from NCHS publications and the Interactive Summary Health Statistics for Teens):
- GAD-2 (GAD1 "feeling nervous, anxious, or on edge", GAD2 "not being able to stop or control worrying"), PHQ-2 (PHQ1 "little interest or pleasure", PHQ2 "feeling
  down, depressed, or hopeless"), past 2 weeks, 0–3 each, symptomatic if sum ≥ 3. Screen hours: "On most weekdays, how many hours do you spend a day in front of a
  TV, computer, cellphone or other electronic device ..." (<1, 1, 2, 3, 4+ hours; schoolwork excluded). Bullying: "how often were you bullied, picked on, or excluded
  by other youth" past 12 months. NHIS-Teen weight (Sample Child weight × non-permission × non-participation adjustments by recursive partitioning; see the
  30-month weighting report). Response: 7,323 eligible sample children 12–17 (2021 Q3–2023 Q4), 60.4% parent permission, 46.2% teen participation among permitted,
  overall 27.9%, n = 1,958 (Data Brief 513 and PCD analyses use n = 1,952 with valid screen time).
- Public aggregates: 50 indicators × parent-reported subgroups × 2 periods, Korn–Graubard CIs; teen SEs in `nhis_agreement.csv` are approximated as (CI width)/3.92.

## Samples

| NHIS year | Sample children 12–17 | valid ANXFREQ_C | screen item | bullying item | 5–11 |
|---|---|---|---|---|---|
| 2021 | 3,207 | 3,192 | — | 3,120 | 2,888 |
| 2022 | 2,758 | 2,753 | 2,675 | 2,659 | 2,740 |
| 2023 | 2,899 | 2,889 | — | — | 2,777 |
| 2024 | 3,194 | 3,186 | 3,159 | — | 3,034 |

## Results (results/tables)

- `nhis_prevalence.csv`, `nhis_prevalence_age.csv`: parent-reported daily/weekly and daily anxiety and sadness by year × sex × age group and by single year of age.
  12–17, 2021–2024 pooled: anxious d/w 19.4% (boys 15.5, girls 23.5); sad d/w 7.5% (5.4 / 9.7); 5–11: 13.9% and 3.8%. By year (all 12–17): anxious d/w 16.9 (2021),
  22.8 (2022), 19.3 (2023), 18.5 (2024); girls 20.9 → 28.4 → 23.0 → 21.7; sad d/w 7.1 → 9.1 → 7.6 → 6.3.
- `nhis_agreement.csv` (population-level, not person-level): parent vs teen prevalence by subgroup, both periods. July 2021–Dec 2023: anxiety 19.7% parent d/w vs 19.7%
  teen GAD-2 ≥ 3 (ratio 1.00), but boys 15.3 vs 10.7 (1.43) and girls 24.3 vs 29.1 (0.84); 12–14 18.2 vs 15.6, 15–17 21.2 vs 23.8. Depression 7.9 vs 17.8 (0.44; boys 0.50,
  girls 0.42). Bullied past year 23.4 vs 34.0 (0.69). 2+ h screen 81.0 vs 90.9 (0.89). Girl/boy ratio 1.6 (parent) vs 2.7 (teen) for anxiety.
- `nhis_screen_gradient.csv`: parent-reported 2+ h screen → parent-reported symptoms, 2022+2024, LPM with year FE (unadjusted) or + age, sex, race/ethnicity, income,
  parental education, region, urbanicity (adjusted): anxious d/w +5.1 pp (SE 1.5), 16.9 → 21.8%, PR 1.29, n = 5,823; sad d/w +4.7 (0.8), 3.7 → 8.9%, PR 2.40;
  boys +4.8 (2.0) / +4.0 (0.8); girls +4.8 (2.3) / +4.8 (1.3); 12–14 +5.9 (2.1) / +4.4 (1.1); 15–17 +3.9 (2.4) / +5.2 (1.3); 5–11 comparison +2.8 (1.1) / +1.0 (0.7).
  With a parent-reported bullying control (2022 only): +4.6 (2.3) and +5.2 (1.2). Teen rows (NCHS): 4+ h vs <4 h anxiety 12.3 → 27.1% (+14.8 pp, SE 2.2; PR 2.21, APR 2.12,
  1.67–2.71), depression 9.5 → 25.9% (+16.4, 2.2; PR 2.74, APR 2.51, 1.89–3.35), n = 1,952.
- `nhis_bully_gradient.csv`: parent-reported bullied → parent-reported anxious d/w +21.1 pp (1.7), 14.7 → 37.2%, PR 2.54; sad d/w +12.3 (1.2), PR 3.43 (2021–22, n = 5,767);
  teen (Data Brief 514) 14.5 → 29.8% (PR 2.06) and 12.1 → 28.5% (PR 2.36).
- `nhis_validity.csv`: mental-health therapy or medication in past year by parent-reported frequency (12–17): anxious daily 63.2%, weekly 48.5%, monthly 30.8%, never 7.9%; sad daily 64.2%, never 10.0%.
- `nhis_published.csv`: the compiled literature numbers used by the part (copy of `data/compiled/nhis/nhis_teen_published.csv`). `nhis_sample.csv`: the table above.

## Interpretation and limits

- The anxiety totals coincide, but parents compress the girl–boy and age contrasts and report less than half the depression the teenagers report; the direction (parent
  below teen) also holds for bullying and screen time, and matches the linked NHIS-Teen papers on health-care use and ACEs. Part of the depression gap is item, not informant:
  in adults answering both sets about themselves (NHSR 172, 2019 NHIS) the PHQ-8 classifies more people as depressed than the WG item while the WG item classifies more
  as anxious than the GAD-7.
- Both informants show a screen gradient in their own reports (parent depression PR 2.4 vs teen 2.7; parent anxiety PR 1.3 vs teen 2.2). Both are single-informant designs,
  so neither separates association from shared-reporting bias; the exposure thresholds differ (2+ vs 4+ hours); NHIS-Teen has not published the gradient by sex.
- The MICS own-use test was cross-informant (adolescent's own use from the women's/men's questionnaire, caregiver's report of symptoms). The NHIS evidence says parent
  reports do register heavy use and distress together, but with less sensitivity to exactly the contrasts (girls, older teens, depression) that carry the H1 self-report
  findings, so a caregiver outcome has limited power for a girl-specific association.
- Small, 2+ h parent screen item, cross-sectional, and NHIS-Teen's 27.9% response (weighted by NCHS's CTREE adjustments) are the main caveats.

## Literature using NHIS-Teen (verified against the PDF/HTML text)

- Zablotsky B, Arockiaraj B, Haile G, Ng AE. Daily screen time among teenagers: United States, July 2021–December 2023. NCHS Data Brief 513, 2024.
  https://www.cdc.gov/nchs/products/databriefs/db513.htm — 50.4% of 12–17-year-olds report 4+ hours; anxiety symptoms 27.1% vs 12.3%, depression 25.9% vs 9.5% (4+ vs <4 h).
- Zablotsky B, Ng AE, Black LI, Haile G, Bose J, Jones JR, et al. Associations between screen time use and health outcomes among US teenagers. Prev Chronic Dis 2025;22:240537.
  https://doi.org/10.5888/pcd22.240537 — n = 1,952; Poisson PR 2.21 (anxiety) and 2.74 (depression), APR 2.12 (1.67–2.71) and 2.51 (1.89–3.35); no sex or age interaction reported for these outcomes.
- Haile G, Arockiaraj B, Zablotsky B, Ng AE. Bullying victimization among teenagers: United States, July 2021–December 2023. NCHS Data Brief 514, 2024.
  https://www.cdc.gov/nchs/products/databriefs/db514.htm — 34.0% bullied; anxiety 29.8% vs 14.5%, depression 28.5% vs 12.1%.
- Ng AE, Bottoms-McClain L, Black LI, Zablotsky B, Bose J. Comparison of parent and teen reports of teen healthcare use: United States, July 2021–December 2023. NHSR 219, 2025.
  https://dx.doi.org/10.15620/cdc/174622 — parents report more use (doctor visit 91.4% vs 83.0%); weighted Cohen's kappa 0.08–0.42.
- Ng AE, Swedo E, Zablotsky B, Black LI, Niolon PH, Bose J, Blumberg SJ. Parent-teen concordance of selected adverse childhood experiences ... Child Abuse Negl 2025;163:107339.
  https://doi.org/10.1016/j.chiabu.2025.107339 — parents report fewer ACEs (neighborhood violence 6.5% vs 15.5%); kappa 0.27–0.53, PABAK 0.41–0.88.
- Zablotsky B, Ng AE, Black LI, Bose J, Jones JR, Maitland AK, Blumberg SJ. Perceived social and emotional support among teenagers: United States, July 2021–December 2022.
  NHSR 206, 2024. https://dx.doi.org/10.15620/cdc/156514 — anxiety 12.9% vs 33.1% and depression 8.0% vs 31.1% by support; compares teen and parent support reports (teen n = 1,157, parent n = 4,379).
- Katz SM, Claussen AH, Black LI, Leeb RT, Newsome K, Danielson ML, Zablotsky B. ADHD and teen self-report on health behaviors and social-emotional wellbeing. J Dev Behav Pediatr 2025;46(2):e155–e161.
  https://doi.org/10.1097/dbp.0000000000001350 — parent-reported ADHD → teen-reported bullying aPR 1.64, >4 h screen aPR 1.26.
- Ng AE, Tkach N, Black LI, Alcalá HE. Selected teen-reported ACEs and mental health care use. Acad Pediatr 2025:103159. https://doi.org/10.1016/j.acap.2025.103159 — n = 1,677.
- Related: Zablotsky B, Weeks JD, Terlizzi EP, Madans JH, Blumberg SJ. Assessing anxiety and depression: a comparison of NHIS measures. NHSR 172, 2022.
  https://www.cdc.gov/nchs/data/nhsr/nhsr172.pdf — adults 2019; ~90% agreement WG vs GAD-7/PHQ-8 after collapsing the lowest categories; 2.1%/1.6% extreme discordance.
  De Los Reyes A, et al. The validity of the multi-informant approach to assessing child and adolescent mental health. Psychol Bull 2015;141(4):858–900.
  https://doi.org/10.1037/a0038498 — 341 studies; mean cross-informant r = 0.25 internalizing, 0.30 externalizing.
- No NCHS publication to date reports parent–teen agreement on the anxiety/depression items (checked the NHIS-Teen citation list updated 2026-01-13).

## Follow-up

An NCHS RDC proposal (https://www.cdc.gov/rdc/application-process/index.html) for NHIS-Teen linked to the Sample Child file would allow: kappa and sensitivity/specificity of
ANXFREQ_C/DEPFREQ_C against GAD-2/PHQ-2 by sex and age; the cross-informant screen gradient (teen hours → parent symptoms, and parent 2+ h → teen screener); and the
severity moderation test (PHQ-2 ≥ 5). NCHS's Interactive Summary Health Statistics can also be requested to add a screen-time row variable, which would give the teen
gradient by sex without an RDC visit. The NSCH section (plan 1.A.2) supplies the parent-report gradient with graded screen hours.
