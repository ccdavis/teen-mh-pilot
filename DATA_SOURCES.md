# Data sources

Each entry gives the provider, how to obtain the data, what was used, and the script that consumes it. Microdata are not included in this repository; compiled public tables are in `data/compiled/` and computed results in `results/tables/`.

## IPUMS microdata (registration required; free)

| Source | Access | Samples used | Variables used | Consumed by |
|---|---|---|---|---|
| **IPUMS USA** (ACS 1-year) | usa.ipums.org extract system | us2005a–us2024a | `scripts/extract/README.md` (person, household, disability, internet items, PERWT and REPWTP1–80) | `scripts/extract/acs_extract_sql.py` → `scripts/analysis/02–06, 09, 10, 12` |
| **IPUMS CPS** (Computer and Internet Use Supplement) | cps.ipums.org | Oct 2009, Oct 2010, Jul 2011, Oct 2012, Jul 2013, Jul 2015, Nov 2017, Nov 2019, Nov 2021, Nov 2023 | CI* items, WTFINL, CISUPPWT, CIPWT, METFIPS, STATEFIP | `scripts/extract/cps_internet_supplement.sql`, `scripts/analysis/cps_ci_sanity.py`. Note: IPUMS CPS carries only part of the supplement (no mobile items); the mobile series come from the raw NTIA/Census files below |
| **IPUMS ATUS** | timeuse.ipums.org | at2003–at2024 (activity and respondent records) | ACTIVITY, DURATION, WT06/WT20, AGE, SEX, DAY, MONTH, HOLIDAY, SCHLCOLL, STATEFIP | `scripts/extract/atus_extract.sql.template` → `scripts/analysis/07, 08` |
| **IPUMS International** | international.ipums.org | ke2009a, ke2019a, mx2010a, mx2020a | DISMNTL, Washington Group difficulty items, CELL, INTERNET, source ICT items, GEO2, PERWT | `scripts/extract/ipumsi_extract.sql` → `scripts/analysis/11` |
| **IPUMS DHS** | idhs.ipums.org | Nepal 2022, Kenya 2022 women's files | DEPRESSIONSCORE, GADSCORE, DEPRESSIONDIAG, ANXIETYDIAG, INTERNETMO, CELLPHONESMART, WEALTHQ, EDUCLVL, CLUSTERNO, PERWEIGHT | `scripts/extract/dhs_extract.sql` → `scripts/analysis/21` |
| **IPUMS MICS** | mics.ipums.org | all MICS6/MICS7 samples with the Child Functioning Module (68 samples, 2017–2024): children 5–17 (fs), women (wm), men (mn), household (hh) files | ANXIFREQ, DEPRESSFREQ, DIFF* items, AGEFS, SEXFS, WEIGHTFS, WINDEX5, URBAN, REGIONW, CLUSTER; INTFREQ3MO, PHONEFREQ3MO, MOBILEWM/MN, INTEVER; household INTERNET, MOBILE, COMPUTER | `scripts/extract/mics_reader.py`, `scripts/extract/mics_extract.py` → `scripts/analysis/18` |

## U.S. public surveys and series

| Source | Access | Used | Consumed by |
|---|---|---|---|
| NSDUH state estimates (youth major depressive episode, 12–17), 2005–06 to 2018–19 and 2021–22 to 2023–24 | SAMHSA, samhsa.gov/data (State Prevalence Estimates datasets) | `BSAE`, `ste_sae` for outcome MDE / MDEYR, age group 1 | `scripts/analysis/12` |
| YRBS Youth Risk Behavior Survey, 2023 combined national and state datasets (1991–2023) | CDC, cdc.gov/yrbs/data | sad/hopeless, considered suicide, plan, attempt; sex, grade, weight, site | `scripts/analysis/12, 13` |
| NHANES depression screener (PHQ-9) 2005–2023 | CDC, wwwn.cdc.gov/nchs/nhanes | DPQ010–DPQ090, DEMO weights (public file is ages 18+) | `scripts/analysis/12` |
| NTIA Internet Use Survey (CPS supplement raw files), 2009–2023 | Census Bureau CPS supplement files (www2.census.gov/programs-surveys/cps) with NTIA's harmonization (github.com/ntiadc/ntia-internet-use-survey) | household mobile data plan, smartphone internet use, internet use, by state and CBSA | `scripts/download/ntia_build.py` → `data/compiled/ntia/` → `scripts/analysis/19, 23` |
| State youth surveys with county tables: Minnesota Student Survey, Washington Healthy Youth Survey, California Healthy Kids Survey (via kidsdata.org), Maine Integrated Youth Health Survey, Pennsylvania Youth Survey, Illinois Youth Survey | State education/health department sites (URLs in `notes/state_surveys.md`) | sadness, suicidal ideation, attempts, screen-time items by county and year | `scripts/download/state_surveys/` → `data/compiled/state_surveys/` → `scripts/analysis/23, 24` |
| NCES SSOCS and School Pulse Panel (share of schools prohibiting phones) | nces.ed.gov Digest tables 233.50/233.60; SPP releases | national series 2009–10 to 2024–25 | `scripts/download/phone_bans/` → `data/compiled/phone_bans/` |

## U.S. policy and infrastructure tables (compiled here)

| Table | Sources | Script |
|---|---|---|
| LTE launch dates by carrier and metro, 2010–2013, mapped to 2013 CBSAs | Carrier press releases and press reprints; Census CBSA delineation files | `scripts/download/lte/` → `data/compiled/lte/` |
| State school accountability policy timing 2005–2019 (Race to the Top, ESEA waivers, Common Core aligned tests, teacher evaluation, exit exams) | ed.gov archives, corestandards.org (archived), CEP, NCTQ, Kraft et al. (2020), Achieve, Education First | `scripts/download/school_policy/` → `data/compiled/school_policy/` |
| State and district phone-ban policies, effective school years | Ballotpedia, Education Week, KFF, NCSL, state statutes | `scripts/download/phone_bans/` → `data/compiled/phone_bans/` |

## International surveys and series

| Source | Access | Used | Consumed by |
|---|---|---|---|
| WHO Global School-based Student Health Survey, 165 public-use country-rounds 2003–2023 | WHO NCD Microdata Repository (extranet.who.int/ncdsmicrodata), per-entry terms acceptance, no registration | loneliness, worry/sleep, suicidality items; 2022–23 mobile-phone-hours items | `scripts/download/gshs/` → `scripts/analysis/14, 20, 22` |
| HBSC published international reports 1993/94–2021/22 and the HBSC data browser | hbsc.org, WHO Europe (iris.who.int), data-browser.hbsc.org | schoolwork pressure, multiple complaints, life satisfaction, social-media items by country, wave, age, sex | `scripts/download/hbsc/` → `data/compiled/hbsc/` → `scripts/analysis/15` |
| PISA 2022 student and school questionnaire files | OECD PISA 2022 database (webfs.oecd.org/pisa2022) | school item SC190Q02JA (phones not allowed on premises), student loneliness/belonging, device items, well-being indices, ANXMAT | `scripts/download/pisa2022/` → `scripts/analysis/25, 26` |
| ITU connectivity indicators 2005–2024 | ITU DataHub (api.datahub.itu.int v3 download endpoint); GSMA Mobile Connectivity Index | mobile-broadband subscriptions, 3G/4G population coverage, internet users | `scripts/download/itu_build.py` → `data/compiled/itu/` → `scripts/analysis/22` |
| World Bank WDI | api.worldbank.org | internet users %, mobile subscriptions, GDP per capita, population | `scripts/download/wdi_fetch.py` → `data/compiled/wdi/` → `scripts/analysis/14` |

## Literature compiled in the report

The causal studies of school phone bans (Beland & Murphy 2016; Kessel et al. 2020; Beneito & Vicente-Chirivella 2022; Abrahamsson 2024; Goodyear et al. 2025; Figlio & Özek 2025; Allcott et al. 2026; Lichand et al. 2026; OECD 2023) are tabulated with sources in `data/compiled/phone_bans/phone_ban_studies.csv`. The Anxious Generation evidence discussed in the report is linked from the report text.
