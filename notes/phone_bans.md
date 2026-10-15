# School smartphone bans: policy timing, national prevalence, and causal evidence

Built 2026-09-16 by `scripts/phone_bans/build_phone_bans.py` (re-run with
`uv run python scripts/phone_bans/build_phone_bans.py`). Every row is hard-coded in that script with a source
URL. Source downloads/extractions: `data/external/phone_bans/` (README there). Status date for policy: 2026-09-16.

## Outputs (`data/extracts/phone_bans/`)

| file | rows | content |
|---|---|---|
| `state_phone_bans.csv` | 51 (50 states + DC) | state, policy_type, law_or_rule_citation, date_enacted, effective_school_year, grades_covered, source_url, note |
| `district_phone_bans.csv` | 7 | large-district bans with dates (LAUSD, NYC, Orange County FL, Clark County NV, DCPS, Houston ISD, Montgomery County MD) |
| `school_phone_prohibition_national.csv` | 11 | NCES SSOCS/FRSS 2009-10..2021-22, School Pulse Panel 2024-25, plus flagged non-NCES rows |
| `phone_ban_studies.csv` | 12 | annotated causal/quasi-experimental studies + key descriptive/review references |

## 1. State policy timing

`policy_type` is the *current* (2026-09-16) statewide requirement, one of: statewide bell-to-bell ban (27 incl. DC),
ban during instructional time (8), requires districts to adopt a policy (10), guidance/recommendation only (2),
none (4). `date_enacted` = signing/adoption date of the law or rule that established the current status
(earlier steps are in `law_or_rule_citation`/`note`); `effective_school_year` = first school year the current
status is in force (for laws with a mid-year deadline, e.g. Ohio 2026-01-01, SC Jan 2025, the year containing it).

| type | states |
|---|---|
| bell-to-bell | AL 25-26, AR 25-26, DC 25-26, FL (K-8 25-26; instr. time 23-24 for all), GA (K-8 26-27, 9-12 27-28), HI (K-8 26-27), IL 27-28, KS 26-27, KY 25-26, LA 24-25, ME 26-27, MD 27-28, MO 25-26, NE 25-26, NH 25-26, NJ 26-27, NY 25-26, ND 25-26, OH 25-26 (Jan 2026), OK 25-26, OR 25-26 (Jan 2026), RI 26-27, SC 24-25 (Jan 2025), TX 25-26, UT 26-27 (class-time 25-26), VT 26-27, VA 25-26 |
| instructional time | IN 24-25, IA 25-26, MI 26-27, NV 25-26, NC 25-26, TN 25-26, WV 25-26, WI 26-27 |
| requires district policy | AK 25-26, AZ 25-26, CA 26-27 (AB 3216, by 2026-07-01), CO 26-27, CT 26-27, DE 26-27, ID 25-26, MN 24-25 (by 2025-03-15), NM 25-26, WY 26-27 |
| guidance only | MT (governor letter 2024-08), WA (OSPI 2024-09; 2026 study law) |
| none | MA (both chambers passed differing bills), MS, PA ($100M pouch grants 2024; House bill 2026), SD (bill failed 2026-03) |

First movers for event-study purposes: FL HB 379 (signed 2023-05-09, instructional time 2023-24; Orange County
bell-to-bell Aug 2023); IN (2024-25 instructional); LA, SC (2024-25 bell-to-bell); then the big 2025-26 wave
(AL, AR, KY, MO, NE, NH, NY, ND, OH, OK, OR, TX, VA + instructional-time IA, NV, NC, TN, WV); 2026-27 (GA K-8, HI,
KS, ME, NJ, RI, UT full-day, VT + MI, WI); 2027-28 (IL, MD, GA 9-12).

Classification conflicts (recorded in `note`): Arizona, Idaho and North Carolina are counted as bell-to-bell by
EdWeek but their statutes only require "limit during the school day" (AZ), a "distraction-free" policy (ID) or an
instructional-time prohibition (NC); Ballotpedia counts Iowa and Nevada as statewide bans though the statutes
target class time. Counts therefore differ across trackers (EdWeek July 2026: "at least 39 states + DC require a
ban or restriction"; Ballotpedia Dec 2025: 35 + DC; this table: 45 jurisdictions with any mandate incl. policy-only).

Sources: Ballotpedia state table (primary, with quoted statute text), EdWeek tracker (counts only; the table is an
embedded visualization), KFF (Apr 2025 cross-check), state press/news for 2026 actions (MD, WY, WA, CT, MA, SD, OK,
DC, HI, ID, VA 2025, FL 2025). NCSL page not fetched.

## 2. National share of schools prohibiting phones

| year | survey | share | SE | item |
|---|---|---|---|---|
| 2009-10 | SSOCS | 90.9 | 0.67 | prohibited use of cell phones and text messaging devices during school hours |
| 2013-14 | FRSS 106 (not SSOCS) | 75.9 | 1.07 | same wording; smaller sample, mixed mode |
| 2015-16 | SSOCS | 65.8 | 1.36 | same wording |
| 2017-18 | SSOCS | 70.3 | 1.30 | prohibited *non-academic* use of cell phones or *smartphones* during school hours (wording change) |
| 2019-20 | SSOCS | 76.9 | 1.03 | pandemic caveat |
| 2021-22 | SSOCS | 76.1 | 0.76 | latest SSOCS (Digest 2023 table 233.50) |
| 2024-25 | School Pulse Panel, Dec 2024 (n=1,490) | 77 | - | students cannot have phones during *any class* (elementary 86, high 55); 30% also ban outside class (bell-to-bell proxy) |
| 2024-25 / 2025-26 | Phones in Focus educator survey (non-probability) | 60 -> 74 | - | bell-to-bell policy; HS ~50%, elementary/middle ~90% |

The SSOCS item asks about *school hours* while the SPP item asks about *class time*, so 77% (2024-25) is not
comparable to 76% (2021-22); the 30% "all classes + outside class" SPP figure is the closest bell-to-bell measure.
The SSOCS series is U-shaped: 91% in 2009-10 (pre-smartphone-saturation, a "no phones" norm) falling to 66% in
2015-16 as schools allowed devices, then rising again. No SSOCS was fielded in 2023-24 and no NCES release with a
2025-26 cellphone-policy item was found. The 2023-24 SPP only had a "use of devices when not permitted" impact item
(16% severe negative impact).

### Sub-national identifiers in SSOCS

Per the 2019-20 public-use DFUM (NCES 2024-054), the public-use file carries only composite school characteristics:
`FR_LVELX` (level), `FR_SIZE` (enrollment category), `FR_URBAN` (4-category urbanicity collapsed from `FR_LOC12`),
plus percent-minority and other categorical composites. Appendix D lists what is *restricted-use only*: `FR_FIPST`
(FIPS state), `FR_STCNTY` (state+county FIPS), `CENREGN` (census region), `FR_CCDID` (NCES school ID), `FR_LEAID`
(district ID), `FR_LOC12` (12-category locale), exact enrollment/race counts, and several questionnaire counts.
So: **state and even census region are restricted-use only; urbanicity (4 categories) and school level are public.**
State-level prohibition shares would require an NCES restricted-use license (and SSOCS samples ~2,500-4,800
schools, so state cells would be thin). Public-use files 2009-10 .. 2021-22 are at
https://nces.ed.gov/surveys/ssocs/data_products.asp. SPP public-use files are similarly national only.

## 3. Causal / quasi-experimental studies

| study | country | design | domain | headline |
|---|---|---|---|---|
| Beland & Murphy 2016 | England | school-level DiD, 91 schools | achievement | +6.4% SD GCSE; ~+14% SD for lowest achievers |
| Kessel et al. 2020 | Sweden | replication DiD | achievement | null; rejects small gains |
| Beneito & Vicente-Chirivella 2022 | Spain | SCM/DiD, 2 regions | achievement, bullying | Galicia PISA math +10.7, science +12.7 pts; bullying cases -9.5 to -18% |
| Abrahamsson 2024 (JHR forthcoming) | Norway | staggered event study, ~400 middle schools | mental health, bullying, achievement | girls: fewer GP/specialist psych visits (~60% fewer specialist), bullying down (~-46% after 3 yrs), GPA +0.08 SD; boys null |
| Goodyear et al. 2025 (SMART Schools) | England | cross-sectional, 30 schools | well-being (null) | WEMWBS diff -0.48 (95% CI -2.05, 1.06) |
| Figlio & Ozek 2025 | Florida (1 large district) | DiD on pre-ban phone activity | achievement, discipline, attendance | yr1 suspensions +12% (Black males ISS +30%), fade; yr2 test +1.1 percentile; fewer unexcused absences |
| Allcott et al. 2026 | US national (Yondr pouches) | staggered DiD, ~5,000 schools | achievement, well-being, bullying, discipline | test ~0 (HS math +0.024 SD); well-being -0.2 SD at adoption -> +0.16 SD by yr 2; no change in online bullying |
| Lichand et al. 2026 | Rio de Janeiro | DiD strict vs lax pre-policy schools | achievement | +0.06 SD |
| Kohnstamm/Oberon 2025 | Netherlands | descriptive monitoring | reported climate | 75% better concentration, 59% climate, 28% learning (leader reports) |
| OECD PISA 2022 Vol. II | cross-national | associational | distraction | ban schools: less reported distraction, but 29-30% still use phones several times/day |
| Bottger & Zierer 2024; Campbell et al. 2024 | reviews | meta/scoping | all | d = 0.16 pooled; mixed |

Reading for the pilot: the only design with mental-health *outcomes* from registers is Abrahamsson (girls only,
Norway, school-level bans up to 2018); the two U.S. quasi-experiments (Figlio-Ozek, Allcott et al.) find small
achievement effects, transitory discipline spikes, and (Allcott) a delayed positive well-being effect with no
bullying change; the English cross-sectional study is null on well-being. Effect sizes are modest everywhere
(0.02-0.08 SD achievement) except the Spanish regional PISA estimates.

## Gaps / caveats

* Abrahamsson PDF not retrievable (NHH open-access host DNS failure, SSRN 403); magnitudes are from the abstract
  and press summaries - verify before quoting. Journal version: Journal of Human Resources (per Allcott et al. refs).
* EdWeek's state table is an embedded visualization; only its headline counts were captured. NCSL not fetched
  (web-search budget exhausted).
* Unverified details: Connecticut 2025 Public Act number/date for HB 7009 sec. 5; Idaho SB 1032 signing day;
  Oklahoma HB 1276 signing date; Delaware SB 106 effective year; Minnesota 2026 K-8 bill outcome; DC Council act
  text (press only); NC HB 959 session-law number.
* Digest 2022 table 233.60 (2019-20 by school level/urbanicity) was downloaded but the cell-phone row did not
  extract cleanly; read it from the HTML if a 2019-20 breakdown is needed.
* No NCES prevalence figure exists for 2022-23, 2023-24 or 2025-26; the Phones in Focus rows are a non-probability
  educator survey and should not be spliced onto the SSOCS series.
* Dutch "Disconnect to Reconnect" (2025, PMC12966246) on ban types and student well-being was not retrieved.
