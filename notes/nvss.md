# NVSS monthly suicide mortality (CDC WONDER), 1999-2024: school-calendar seasonality and the decomposition of the post-2010 rise

Compiled 2026-10-24. Scripts: `scripts/download/nvss/wonder_fetch.py` (API pull, raw XML in `data/external/nvss/wonder/`, parsed tables
in `data/compiled/nvss/`), `scripts/analysis/30_nvss_seasonality.py` (results in `results/tables/nvss_*.csv`), report section
`scripts/report/parts/nvss.py`. Data README with every file: `data/external/nvss/README.md`.

## Access route

CDC WONDER XML API, `POST https://wonder.cdc.gov/controller/datarequest/D76` (Underlying Cause of Death 1999-2020) and `.../D158`
(Underlying Cause of Death 2018-2024, Single Race), form fields `request_xml` and `accept_datause_restrictions=true`. The request XML
mirrors the interactive form; the script posts the "I Agree" step, reads every field's default from the returned form and overrides
group-bys, cause list, ages, years and display options. What was blocked or awkward:
- `https://wonder.cdc.gov/wonder/help/WONDER-API.html` (the API documentation) returned HTTP 404; parameter names were taken from the forms.
- wonder.cdc.gov returns HTTP 403 to python-requests' default user agent; curl's default UA (`curl/8.5.0`) is accepted.
- HTTP 429 "API/XML requests must have at least 15 seconds between consecutive requests" (first run used 4 s); now 16 s.
- Suppression: cells of 1-9 deaths are returned as "Suppressed" even nationally when the table is grouped by single-year age or when
  by-sex monthly cells are small. The main tables filter on single-year ages (12-17, 18-24, 25-34, 12-14, 15-17, 12-18, 35-54)
  without grouping by age, which returns the age-group total per year x month x sex; the by-sex 12-17 series still has 8 suppressed
  months (girls, early 2000s), 12-18 has 2, 15-17 has 21 and 12-14 has 206 of 528. A parallel both-sexes query per group is never
  suppressed, and a suppressed female (male) month is recovered internally as both-sexes minus male (female) for period aggregates only.
  The WONDER data-use agreement forbids presenting counts of nine or fewer: every published table is passed through `mask_small()`, which
  blanks any death count of 1-9 (zeros are shown), and the monthly table keeps the suppressed by-sex cells blank.
- Populations are "Not Applicable" whenever Month or Weekday is a group-by, so denominators come from year x single-year-age x sex
  queries (bridged-race July 1 estimates in D76; single-race postcensal estimates in D158, including Vintage 2024 for 2024).
- The year/month finder accepts month codes (`F_D76.V1 = 2015/06`), which is how the weekday tables are pooled over the school months
  (September-May) or summer months (June-August) of 1999-2019 and 2021-2024; grouping by Month gives year-specific months and the
  resulting weekday cells were 71% suppressed at 12-17.
- Fallback not needed: NCHS public-use mortality files `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/mortality/mort<year>us.zip`
  (1999-2024 all present, 82-166 MB each) and NBER's conversions at `https://data.nber.org/mortality/<year>/` were reachable on 2026-10-24.

## Coding

- Cause of death: ICD-10 113 cause list group 124 "Intentional self-harm (suicide)" = *U03, X60-X84, Y87.0 (WONDER code `GR113-124`).
- Age groups from single-year ages: 12-17 (primary; Hansen-Lang/HSS use 12-18 or 14-18, so 12-18 is also tabulated), 18-24 and 25-34
  (no school calendar), 12-14 and 15-17 (sub-splits), 35-54 (adult reference).
- Seasons: summer = June-August; school months = September-May; December is also tabulated separately (winter break).
- Exposure: person-years = July 1 population x days in month / days in year; rates per 100,000 person-years. Seasonal "index" = month rate
  / period mean rate (so a month with no seasonality has index 1 after the days-in-month adjustment).
- Periods: 1999-2003 (early baseline), 2005-2009, 2008-2010 (pre-rise trough: the 12-17 rate was flat at its 2007-2010 low before the
  increase that begins in 2011-12 for girls and 2013-14 for boys), 2011-2014, 2015-2019 (pre-pandemic plateau), 2020, 2021-2024.
- Data vintage: D76 (1999-2020) for 1999-2020; D158 (2018-2024) for 2021-2024. Deaths agree exactly in the 2018-2020 overlap
  (`results/tables/nvss_db_overlap.csv`); populations differ only through the bridged-race vs single-race estimate series.

## Estimation

- Summer/school ratio: (summer deaths / summer exposure) / (school deaths / school exposure), Poisson CI on the log scale (SE = sqrt(1/d1 + 1/d0)).
- Decomposition: for pre and post period, the post/pre rate ratio in school months and in summer; the "ratio of ratios" (school / summer)
  with SE = sqrt(sum of 1/deaths over the four cells); the share of the absolute increase in annual deaths per 100,000 accruing in
  September-May (seasonally neutral = school months' 75% share of person-time).
- Monthly-count regressions (statsmodels): Poisson GLM with log exposure offset and HC1 robust SEs; negative binomial (alpha by ML) as a
  check. (a) Seasonality 1999-2019: `deaths ~ summer + December + C(year)`. (b) Decomposition: `deaths ~ C(month) + post + post x summer`
  for 2008-10 vs 2015-19 (also 2005-09 vs 2015-19, 2015-19 vs 2021-24, 2008-10 vs 2021-24). (c) Triple difference 12-17 vs 18-24 and vs
  25-34: `deaths ~ C(month) x teen + post + post x summer + teen x post + teen x post x summer`.
- 2020: expected monthly counts from a Poisson model fit to 2015-2019 (`deaths ~ C(month) + t`, exposure offset) extrapolated to 2020
  and 2021, with prediction SE folded into the observed/expected CI; second variant = 2019 annual rate x 2015-19 seasonal index x 2020
  exposure. Windows: Jan-Feb, Mar-May (closures), Jun-Aug, Sep-Dec 2020, Jan-May 2021 (reopening).
- Day of week: deaths per calendar day (exact counts of each weekday in the pooled months) on Monday-Friday vs Saturday-Sunday, in school
  months vs summer, 1999-2019 and 2021-2024, by age group and sex.

## Results (`results/tables/nvss_*.csv`, run of 2026-10-24; CIs are Poisson 95%)

- Coverage: 31,967 suicides at 12-17, 106,331 at 18-24 and 167,764 at 25-34 over 1999-2024. D76 and D158 agree exactly on deaths in
  2018-2020 (756 year x month x age-group x sex cells, maximum difference 0; `nvss_db_overlap.csv`); populations agree to < 0.01%.
  181 suppressed by-sex months were recovered from both-sexes totals for internal aggregates; 68 cells remain missing, all in 12-14.
- Seasonality 1999-2019, summer (Jun-Aug) / school-month (Sep-May) rate ratio: 12-17 0.81 (0.78-0.83), girls 0.80 (0.76-0.85), boys
  0.81 (0.78-0.84); 15-17 0.82; 12-18 0.84; 18-24 1.01 (0.99-1.03); 25-34 1.07 (1.06-1.09); 35-54 1.07. Poisson with year fixed
  effects, summer vs other school months: 12-17 0.79 (0.76-0.82), 18-24 1.00, 25-34 1.07. December vs other school months: 12-17 0.80,
  18-24 0.92, 25-34 0.94 (a holiday dip at every age, deeper at 12-17). Summer ratio at 12-17 by period: 0.78 (1999-2003), 0.84
  (2005-09), 0.83 (2008-10), 0.81 (2011-14), 0.80 (2015-19), 0.81 (2020), 0.84 (2021-24): the trough did not change depth across the rise.
- Decomposition 2008-10 -> 2015-19, ages 12-17: school-month rate 4.03 -> 6.64 per 100,000 (+65%), summer 3.36 -> 5.31 (+58%); ratio of
  ratios (school / summer) 1.04 (0.94-1.16). Girls +82% vs +80%, RoR 1.01 (0.83-1.23); boys +59% vs +51%, RoR 1.05 (0.93-1.19). Share of
  the absolute increase accruing in Sep-May: 80% (seasonally neutral = 75%). Poisson post x summer: -0.04 (SE 0.05) pooled, -0.01 (0.09)
  girls, -0.05 (0.06) boys; negative binomial identical. Placebo groups: 18-24 RoR 1.02 (0.97-1.08), 25-34 1.00 (0.96-1.04). Triple
  difference teen x post x summer: -0.02 (0.06) vs 18-24, -0.05 (0.06) vs 25-34. Alternative baselines at 12-17: 1999-2003 -> 2015-19
  RoR 0.98 (0.90-1.07); 2005-09 -> 2015-19 1.05 (0.97-1.15); 2008-10 -> 2021-24 1.00 (0.90-1.11); 2008-10 -> 2011-14 1.04 (0.93-1.16);
  2015-19 -> 2021-24 0.96 (0.88-1.04). A rise confined to the school year would give RoR = the school-month ratio, 1.65; excluded.
- Annual 12-17 rates per 100,000: girls 2.05 (2008), 3.92 (2019), 4.28 (2024); boys 5.33, 8.62, 7.01; both 3.73, 6.32, 5.68.
  2021-24 vs 2015-19: school months -5%, summer -1% (girls +4% / +8%, boys -10% / -5%).
- 2020-2021, ages 12-17 both sexes, observed vs trend model (vs 2019-level model): Jan-Feb 2020 -7% (+6%); Mar-May 2020 -33%, ratio 0.67
  (0.60-0.76) (-23%), girls -27%, boys -35%; Jun-Aug 2020 -12% (+1%); Sep-Dec 2020 +1% (+16%); Jan-May 2021 -14%, ratio 0.86
  (0.79-0.94) (+3%). 18-24 Mar-May 2020 -9% (-3%); 25-34 -4%. Mar-May 2021 rate 6.81 vs 5.19 in Mar-May 2020 (+31%). The trend model
  extrapolates the 2015-19 slope into 2021 and overshoots boys' plateau, so the 2019-level comparison is the safer reference for 2021.
- Day of week, deaths per calendar day Mon-Fri / Sat-Sun: 1999-2019 at 12-17, school months 1.19 (1.15-1.23), summer 1.11 (1.04-1.18),
  school / summer 1.07 (1.00-1.15); Monday 3.70 and Saturday 2.81 deaths per day in school months. 18-24: 0.98 in both seasons; 25-34:
  1.01 / 1.00. 2021-24 at 12-17: 1.15 (1.08-1.23) school, 1.11 (0.98-1.25) summer.
- Reading: the school *level* effect (summer trough, weekday excess, closure drop) is precise at 12-17 and absent at 18-24 and 25-34; the
  2008-2019 *rise* was seasonally proportional, so its driver was not confined to the school year. For the mortality series this counts
  against H2 as the explanation of the rise and is what H1 (or any year-round driver) predicts; the 2021 reopening is ambiguous.

## Literature (numbers checked against the abstracts or full text on 2026-10-24)

| Study | Data | Finding |
|---|---|---|
| Hansen & Lang 2011, *Economics of Education Review* 30(5): 850-861, https://doi.org/10.1016/j.econedurev.2011.04.012 | State x month suicide rates 1980-2004, NVSS multiple-cause public-use files; youth 14-18 vs 19-25 | Summer lowers the 14-17 rate by 1.38 per 100,000 and the 17-year-old rate by 1.64; youth suicide (Table 7) -0.83 per 100,000 in summer; no summer drop at 18 by September, none at 19-25 (whose summer rate is significantly higher); weather, economic conditions and SAD do not explain it. Verified from the full text. |
| Hansen, Sabia & Schaller 2024, *J. Human Resources* 59(S): S227-S255, https://doi.org/10.3368/jhr.1222-12710R2; NBER WP 30795 (Dec 2022) | Restricted county x month NVSS counts 1990-2020, ages 12-18 vs 19-25; SafeGraph K-12 foot traffic | Relative to January, 12-18 suicides 15.6-22.0% lower in June-August (largest in July) and ~19% lower in December; August-start counties rise in August, September-start in September; March-May 2020 25.4-38% below January 2020 (abstract: "fell 25 percent in March 2020"); return to in-person instruction +12-18% (16.1-17.6% in the main columns); young adults +1-3% in summer. Verified from the NBER text and JHR abstract. Note: the Phase 1 report quotes "18-25%" for the 2020 decline; the paper's figures are 25% (abstract) and 25-38% (Table 1, relative to January 2020); 12-18% is the reopening effect. |
| Lueck, Kearl, Lam & Claudius 2015, *Am. J. Emergency Medicine* 33(5): 682-684, https://doi.org/10.1016/j.ajem.2015.02.055 | 3,223 pediatric psychiatric ED visits (danger to self or others), one academic ED, 2009-2012, mean age 13.8 | 82.7% of visits in school weeks vs 68.6% of time in school, IRR 2.18; UTI control IRR 1.25. Verified (abstract). |
| Plemmons et al. 2018, *Pediatrics* 141(6): e20172426, https://doi.org/10.1542/peds.2017-2426 | PHIS, 31 children's hospitals, ages 5-17, 2008-2015, 115,856 SI/SA encounters | Share of encounters 0.66% -> 1.82%; larger increases at 15-17 and 12-14 and for girls; lowest in summer, highest in spring and fall, pattern persisting over the period. Verified (abstract). The "October nearly twice July" figure comes from press coverage, not the abstract. |
| Carbone, Holzer & Vaughn 2019, *J. Pediatrics* 206: 225-231, https://doi.org/10.1016/j.jpeds.2018.10.017 | HCUP ED data 2010-2014, 874,872 child/adolescent and 5.56 million adult visits | Increases 2010-14: 5-11 +37.9%, 12-14 +82.0%, 15-17 +51.6%, 18-24 +26.8%, 25+ +19.0%; school-year seasonality for children and adolescents, none for adults. Verified (abstract). |
| Kim, Krause & Lane 2023, *JAMA Network Open* 6(7): e2324183, https://doi.org/10.1001/jamanetworkopen.2023.24183 | Commercial claims ED visits/hospitalizations for suicidality, ages 10-19, 2016-2021 | April peak IRR 1.15 (1.11-1.19), July nadir IRR 0.63 (0.61-0.66) in pre-COVID years and 2021; April-May 2020 lowest of that year; annual rate 1,006 (2019) -> 942 (2020) -> 1,160 per 100,000 (2021). Verified (abstract). |
| Radhakrishnan et al. 2023, *MMWR* 72(38): 1032-1040, https://doi.org/10.15585/mmwr.mm7238a3 | NSSP ED visits ages 5-17, Jan 2018-Jun 2023 | Suicidal ideation / self-harm visit ratios, fall and spring semester vs preceding summer: 1.13-2.00 at 10-14 and 1.15-1.74 at 15-17 in every school year 2018-19 to 2022-23. Verified (report tables). |
| To, Messias, Burch & Chibnall 2024, *BMC Psychiatry* 24: 856, https://doi.org/10.1186/s12888-024-06309-7 | CDC WONDER monthly suicides 2015-2020 (X60-X84) by age group | Ages 15-24 are the only group with a September-October peak (October 9.04% of annual deaths) and June trough (7.87%); summer incidence lower than at 25+ every year (2020: 3.62 vs 4.63 per 100,000, IRR 0.78). Verified (abstract/results). |
| Romer 2020, *PLOS ONE* 15(1): e0227545, https://doi.org/10.1371/journal.pone.0227545 | Reanalysis of Bridge et al.'s 10-17 monthly suicide series around *13 Reasons Why* (April 2017) | The April 2017 increase for boys was no larger than the March increase once secular trends and autocorrelation are modelled; illustrates how school-year seasonality can be mistaken for a media effect. Abstract checked. |

No published study decomposes the 2010-2019 rise in U.S. adolescent suicide into school-month and summer components (searches on
2026-10-24: Google-indexed literature, Europe PMC); the closest are Plemmons et al. (hospital encounters: seasonal pattern "persisted" over
the 2008-2015 rise) and the MMWR semester ratios, which are stable across 2018-2023.

## Gaps and follow-ups

- WONDER monthly tables are national; the API refuses sub-national geography, so the county-level school-start-date design of Hansen,
  Sabia and Schaller cannot be reproduced here. The NCHS public-use files have no geography after 2004; the restricted-use files would be needed.
- Deaths are dated by date of death, not of the precipitating event; month-of-death misclassification around month boundaries is small.
- The 12-17 by-sex monthly series has 8 suppressed girls' months (early 2000s); 12-14 by sex is unusable monthly and is reported only in
  period aggregates recovered from both-sexes totals.
- School calendars vary (August starts in the South and Mountain West), so "summer = June-August" understates the contrast; a late-August
  start would move some school exposure into August.
- 2024 populations are Vintage 2024 postcensal estimates served by WONDER on the download date and may be revised.
