# Phase 2 Plan: Public-Use Data Extensions and Literature Context

> **Status, 2026-10-24.** Phase 2 was carried out on 2026-10-24; the results are in the report (`docs/`), the methods notes in `notes/<source>.md`,
> and the scripts in `scripts/download/<source>/` and `scripts/analysis/27`–`34`. Outcome by item:
>
> | Item | Status |
> |---|---|
> | 1.A.1 NHIS Sample Child + NHIS-Teen | Sample Child 2021–2024 public files used; **NHIS-Teen microdata are Research Data Center only** (no public-use file exists), so the comparison is population-level against NCHS's published teen estimates (`notes/nhis.md`) |
> | 1.A.2 NSCH | Done, 2016–2025 (the 2025 file was posted 2026-10-05); screen gradient, trends, state adoption, first phone-ban DiD (`notes/nsch.md`) |
> | 1.A.3 DHS-8 | Done for Nepal, Mozambique and Bangladesh via IPUMS DHS; **Jordan 2023 and Cambodia 2021–22 never fielded the module**; Lesotho's PHQ-9, Zambia 2024 and the men's files need a DHS Program request (`notes/dhs8.md`) |
> | 1.B.1 NVSS / CDC WONDER | Done, 1999–2024, national monthly by age and sex via the WONDER API; county counts are suppressed under 10 (`notes/nvss.md`) |
> | 1.B.2 Monitoring the Future | Published 12th-grade data volumes 1996–2012 compiled; **microdata blocked** (ICPSR login and Cloudflare); `31_mtf.py` runs the student-level models once the ICPSR files are placed (`notes/mtf.md`) |
> | 1.B.3 PISA 2012–2022 | Done, four waves, 2.2 million students, including the 2015 ANXTEST interaction (`notes/pisa_panel.md`) |
> | 1.C.1 county waves | PAYS 2025 and CHKS 2019–21, 2021–23, 2023–25 added; **Minnesota 2022/2025 blocked** by a bot-manager CAPTCHA (request specification in `notes/state_surveys.md`) |
> | 1.C.2 YRBS 2025 | Released 2026-09-21 and used; DiD on Indiana, Louisiana and South Carolina (Florida left the YRBS) in `33_yrbs_ban_did.py` (`notes/yrbs_2025.md`) |
> | 1.C.3 broadband instruments | Done: NTIA National Broadband Map 2010–14, FCC Form 477 2014–21, AT&T December 2010 footprint; county youth suicide limited by suppression (`notes/broadband.md`) |
> | Also added | ATUS 2025 and Bangladesh MICS 2025 from the IPUMS internal copies |

This document records the plan for the next phase of empirical work and literature integration following the Phase 1 public-data pilot (`docs/Teen_Distress_Pilot.md`). It covers:
1. **Public-use microdata and administrative series** available now (without restricted-data applications) that directly test the open questions identified by the pilot.
2. **Near-term updates** to the county and state panels already built in Phase 1.
3. **Key empirical literature** from both the smartphone/social-media camp (H1) and the school-pressure/autonomy camp (H2/H3) that contextualizes, substantiates, or challenges the pilot's findings.

---

## 1. High-Priority Public-Use Datasets to Pull and Analyze

### A. Resolving the Caregiver vs. Adolescent Self-Report Divergence (Conclusion #3)
Across the Phase 1 international datasets, heavy phone/internet use predicts distress when adolescents report both their own use and their own symptoms (GSHS 2022–23, Nepal 2022 DHS), but shows no relationship when caregivers report the child's symptoms (67 MICS surveys, `n = 507,478`). Two public U.S. datasets and new DHS-8 waves allow us to test why:

1. **NHIS-Teen Linked to the NHIS Sample Child File (NCHS, July 2021–2024, public-use microdata)**
   - **Access:** NCHS public-use files (`cdc.gov/nchs/nhis/data-questionnaires-documentation.htm`).
   - **Structure:** The annual NHIS Sample Child interview asks parents the exact Washington Group / UNICEF Child Functioning anxiety (`ANXFREQ`) and depression (`DEPFREQ`) items used in MICS. NCHS then invites a subsample of those same 12–17-year-olds to complete the self-administered **NHIS-Teen** questionnaire, which measures teen self-reported PHQ-2, GAD-2, non-school weekday screen hours, sleep routines, bullying, peer support, and stressful school/life events.
   - **Test:** Link the Sample Child and NHIS-Teen files on household/child identifiers (`HHX`) and estimate the screen-time and social-media associations on the *exact same adolescents* using (a) parent-reported daily/weekly anxiety and depression vs. (b) teen self-reported PHQ-2/GAD-2. This directly separates low parent–child agreement on internalizing symptoms from shared self-report bias.

2. **National Survey of Children's Health (NSCH, HRSA/Census, 2016–2024 annual + 2003, 2007, 2011–12 waves, ~50,000 children/year)**
   - **Access:** Census Bureau NSCH public-use microdata (`census.gov/programs-surveys/nsch/data/datasets.html`). Includes state identifiers (`FIPSST`) in the public file.
   - **Variables:** Parent-reported current anxiety and depression (diagnosis + mild/moderate/severe rating), daily recreational screen hours, weekday sleep hours, school engagement, bullying victimization, and neighborhood safety / outdoor play indicators.
   - **Tests:**
     - Estimate the U.S. parent-report screen-time gradient by age and sex to compare directly against MICS and YRBS.
     - Test state-level smartphone adoption and 2023–25 state school phone bans on parent-reported anxiety/depression using `FIPSST`.

3. **Additional DHS-8 Mental Health Module Releases (Mozambique 2022–23, Jordan 2023, Lesotho 2023–24, Cambodia 2021–22)**
   - **Access:** DHS Program / IPUMS DHS (`dhsprogram.com`, `idhs.ipums.org`).
   - **Structure:** Expands `scripts/analysis/21_dhs_mental_health.py` beyond Nepal 2022 (`n = 1,379` ages 15–19 with PHQ-9/GAD-7) and Kenya 2022 (doctor diagnosis only). Mozambique 2022–23 and subsequent DHS-8 releases administer the standardized PHQ-9 and GAD-7 scales alongside `INTERNETMO` and `CELLPHONESMART`.
   - **Test:** Pool all DHS-8 surveys with PHQ-9/GAD-7 to obtain precise within-cluster estimates of adolescent daily internet use and smartphone ownership on self-reported depression and anxiety in low- and middle-income countries.

---

### B. Testing School-Calendar Seasonality and Student-Level Homework × Screen Interactions (H2 & H3)
The Phase 1 report notes that H2 predicts distress concentrated during the school year (while ACS public files lack interview month) and that PISA 2022 lacked a general schoolwork-pressure item. Three public datasets address these gaps directly:

1. **CDC WONDER / NVSS Monthly Mortality Series (1999–2024) & NSSP / WISQARS Emergency Department Visits**
   - **Access:** CDC WONDER Underlying Cause of Death monthly tabulations (`wonder.cdc.gov`) and NCHS Vital Statistics Rapid Release / NVSS public mortality files.
   - **Variables:** Monthly suicide counts and rates (ICD-10 `X60–X84`, `Y87.0`) by age group (`12–17` vs. `18–24` and `25–34`), sex, year, and calendar month (`Jan–Dec`), plus state/census-division breakdowns.
   - **Tests:**
     - Replicate the school-calendar drop in adolescent suicide during summer break (`June–August` vs. `September–May`) at ages 12–17 (and its absence at ages 18–24).
     - **Decisive H1 vs. H2/H3 decomposition:** Test whether the post-2010 surge in adolescent suicide (particularly among girls) occurred disproportionately during the nine school months (`Sept–May`) or rose equally in proportional terms during the summer months (`June–Aug`).

2. **Monitoring the Future (MTF) Public-Use Microdata (ICPSR / NAHDAP, Grades 8, 10, and 12, 1991–2024)**
   - **Access:** NAHDAP / ICPSR public-use cross-sectional files (`icpsr.umich.edu/web/NAHDAP/series/35`).
   - **Variables:** Depressive affect, loneliness, self-derogation, weekly homework hours, academic grades, college expectations, daily social-media and gaming/screen hours, unstructured in-person socializing with friends (evenings out, time with peers), sleep, and census region.
   - **Tests:**
     - Estimate the student-level **H3 interaction** (`homework hours × social-media hours`) on depressive affect and loneliness by sex and grade.
     - Track the joint contribution of rising homework hours, declining unsupervised in-person socializing (central to both Haidt's *play-based childhood* and Gray's *independent activity* thesis), and rising social-media hours across 1991–2024.

3. **Multi-Wave PISA Student/School Microdata Panel (2012, 2015, 2018, 2022)**
   - **Access:** OECD PISA public data repository (`oecd.org/en/about/programmes/pisa/pisa-data.html`).
   - **Variables:**
     - 6-item school loneliness / sense of belonging index (`BELONG`): present in **2012, 2015, 2018, and 2022**.
     - Overall life satisfaction (`ST016Q01NA`): present in **2015, 2018, and 2022**.
     - Schoolwork and test anxiety scale (`ANXTEST`): present in **2015** (directly measuring the schoolwork-anxiety construct that PISA 2022 replaced with `ANXMAT`).
     - ICT Familiarity Questionnaire (age at first digital device/internet, weekday hours online at school vs. outside school): present in **2012, 2015, 2018, and 2022**.
   - **Tests:**
     - Build a 4-wave within-country panel (2012–2022) testing how country- and school-level changes in in-school vs. out-of-school digital use co-move with school loneliness (`BELONG`) and life satisfaction.
     - In PISA 2015, test the student-level interaction between `ANXTEST` (schoolwork/test anxiety) and in-school digital device use on school loneliness and life satisfaction.

---

### C. Immediate Extensions to the Existing U.S. County & Broadband Panels
1. **State Youth Survey County Waves Already Posted:**
   - **Pennsylvania PAYS 2025 county profile PDFs** (`pa.gov` PCCD site): Extend `scripts/download/state_surveys/parse_pa.py` from 2015–2023 to 2015–2025 to test whether Pennsylvania exhibits the same post-2021 downturn in sadness and suicidality seen in Washington (2025) and Illinois (2024).
   - **California CHKS 2019–21 and 2021–23 county PDFs** (`calschls.org` report repository): Extend California's 55-county panel past 2017–19.
   - **Minnesota MSS 2022 and 2025 county tables** (MDE Analytics / MDH request): Add post-2019 waves, including the first post-ban county wave following Minnesota's 2024–25 school phone policy mandate.
2. **2025 YRBS Combined National and State Microdata:**
   - Run the pre-specified difference-in-differences test on early statewide school phone ban adopters—Florida (2023–24) and Indiana, Louisiana, and South Carolina (2024–25)—against non-mandate states across the 2021, 2023, and 2025 YRBS waves.
3. **County/Tract Broadband and Early iPhone Coverage Instruments:**
   - **NTIA State Broadband Initiative (SBI) / National Broadband Map (2010–2014)** and **FCC Form 477 (2014–2021)** public archives: Replace binary metro LTE launch dates with continuous county-level 3G/4G and fixed-broadband population coverage shares.
   - **AT&T 2007–2011 Exclusive iPhone Carrier Monopoly Instrument (Myers & Hooper 2026)**: Test pre-2011 county AT&T 3G network coverage against the Minnesota (1998–2019) and Maine (2009–2023) county mental-health panels and NVSS county youth suicide rates.

---

## 2. Key Literature Incorporated into the Report

### A. Broadband, Early Smartphone Monopoly, and Youth Mental Health (H1)
- **Churchill, Brandyn F., and Kathryn R. Johnson (2026).** *"Broadband Internet Access and Adolescent Mental Health in the U.S."* NBER Working Paper No. 34614 (`https://www.nber.org/papers/w34614`).
  - Pairs state-level FCC broadband expansion (2009–2019) with National and State YRBS data; finds a 1-SD increase in broadband access raises adolescent suicidal ideation by 9.3%–16.5%, concentrated among girls (alongside cyberbullying and body dissatisfaction) and reduced sleep among boys.
- **Myers, Caitlin K., and Ezekiel Hooper (2026).** *"Is the iPhone Birth Control? Causal Evidence from AT&T's 2007–2011 Carrier Monopoly."* NBER Working Paper No. 35310 (`https://www.nber.org/papers/w35310`).
  - Exploits AT&T's exclusive U.S. iPhone carrier agreement (June 2007 – February 2011) interacted with pre-existing county AT&T network coverage; finds early iPhone diffusion reduced births at ages 15–19 by 2.0%–9.0% (October 2026 revision; 4.5%–8.0% in the June 2026 version), with time-use trends consistent with less in-person interaction. The paper's treatment is the public NTIA December 2010 State Broadband Initiative release of AT&T's mobile footprint, which Phase 2 reconstructs at county level. Explains why U.S. geographic separation in smartphone adoption began during the 2007–2011 AT&T 3G window rather than the 2011–2013 4G LTE upgrade window.
- **European Broadband Instrumental-Variable Studies Reviewed in McClean, Rausch, and Haidt (2025):**
  - **Italy:** Donati, Dante, Ruben Durante, Francesco Sobbrio, and Dijana Zejcirovic (2025). *"Lost in the Net? Broadband Internet and Youth Mental Health."* *Journal of Health Economics* 103: 102989 (`https://doi.org/10.2139/ssrn.3949645`).
  - **Spain:** Arenas-Arroyo, Esther, Daniel Fernández-Kranz, and Natalia Nollenberger (2025). *"High Speed Internet and the Widening Gender Gap in Adolescent Mental Health: Evidence from Spanish Hospital Records."* *Journal of Health Economics* (`https://doi.org/10.1016/j.jhealeco.2025.103014`). Fiber-to-the-home (FTTH) rollout (2007–2019) increased adolescent hospital mental-health and self-harm diagnoses, heavily concentrated among girls.
  - **Germany:** Golin, Marta (2022). *"The Effect of Broadband Internet on the Gender Gap in Mental Health: Evidence from Germany."* *Health Economics* 31(S2): 6–21 (`https://doi.org/10.1002/hec.4570`).
  - **United Kingdom:** McDool, Emily, Philip Powell, Jennifer Roberts, and Karl Taylor (2020). *"The Internet and Children's Psychological Wellbeing."* *Journal of Health Economics* 69: 102274 (`https://doi.org/10.1016/j.jhealeco.2019.102274`).

### B. School Calendars, Pandemic School Closures, and Declining Independent Activity (H2 & H3)
- **Hansen, Benjamin, Joseph J. Sabia, and Jessamyn Schaller (2024).** *"In-Person Schooling and Youth Suicide: Evidence from School Calendars and Pandemic School Closures."* *Journal of Human Resources* 59(S): S135–S172 (`https://doi.org/10.3368/jhr.1222-12710R2`; NBER WP 30795). Building on **Hansen, Benjamin, and Matthew Lang (2011)**, *"Back to School Blues: Seasonality of Youth Suicide and the Academic Calendar,"* *Economics of Education Review* 30(5): 850–861 (`https://doi.org/10.1016/j.econedurev.2011.04.012`).
  - Demonstrates that youth suicides (ages 12–18, unlike 19–25) drop sharply every summer and winter break, fell by ~25% (25–38% relative to January 2020) in spring 2020 when schools closed for COVID-19 (despite surging screen use), and rose again across counties as in-person schooling resumed.
- **Gray, Peter, David F. Lancy, and David F. Bjorklund (2023).** *"Decline in Independent Activity as a Cause of Decline in Children's Mental Well-Being: Summary of the Evidence."* *The Journal of Pediatrics* 260: 113352 (`https://doi.org/10.1016/j.jpeds.2023.02.004`).
  - Synthesizes the multi-decade decline in children's unsupervised play, independent mobility, and autonomy alongside rising academic structure—a mechanism on which Gray and Part II of Haidt's *The Anxious Generation* (*"The Decline of the Play-Based Childhood"*) largely converge.
