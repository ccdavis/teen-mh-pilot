# DHS-8 mental-health module beyond Nepal (Phase 2, item 1.A.3)

Compiled 2026-10-24. Scripts: `scripts/download/dhs8/download_final_reports.py` (API listings + final-report PDFs),
`scripts/download/dhs8/parse_final_reports.py` (published tables -> `data/compiled/dhs8/`), `scripts/extract/dhs_extract.py`
(IPUMS DHS sample files -> `data/ipums/dhs/<sample>.parquet` -> `data/extracts/dhs/<sample>_slim.parquet`),
`scripts/analysis/29_dhs8_pooled.py` (-> `results/tables/dhs8_*.csv`), report part `scripts/report/parts/dhs8.py`.

## Access routes

- **Final reports** (free PDFs): all 31 DHS surveys with fieldwork from 2019 and a final report by 2026-10-24, listed with URLs and bytes in
  `data/external/dhs8/README.md`. The DHS Program API (`api.dhsprogram.com/rest/dhs/indicators`, 4,655 indicators) and STATcompiler carry
  **no** indicator from the mental-health module, so prevalence by age had to be parsed from the report tables (one value per line in the PDF
  text; the parser reads the Age, Residence and Total rows of each table and checks that score categories sum to 100 and that the report's
  "with symptoms" column equals the categories above its cutoff; all 30 tables pass).
- **Microdata**: DHS recode files need a registered DHS Program project; IPUMS DHS needs an IPUMS account. Neither credential was available.
  The IPUMS DHS internal sample files became reachable over the user's VPN (`ssh gp1.pop.umn.edu`,
  `/pkg/ipums/dhs/output_data/current/parquet/<sample>/<sample>_dhs.P.parquet`; the sample directories are symlinks into
  `output_data/versions/<sample>/vNNN/`, versions recorded in `data/ipums/dhs/_full/VERSIONS.txt`). The server has no pyarrow/duckdb, so the
  35 non-India 2019+ IR/MR files (577 MB) were copied whole with `tar chf - | tar xf -` into the gitignored `data/ipums/dhs/_full/` and the
  needed columns projected locally. Only aggregates are committed.
- **Recode variable names** (DHS-8, from the World Bank Microdata Library data dictionaries of Lesotho 2023-24 [catalog 6411], Zambia 2024
  [8096] and Jordan 2023 [6288]): women's file RECMTH: `mth1`-`mth7` GAD-7 items, `mth8`-`mth16` PHQ-9 items, `mth17`/`mth18a-x` help seeking,
  `mth19` ever told has depression, `mth20` ever told has anxiety, `mth21` medication, `mth22` PHQ score, `mth23` referral, `mth24` GAD score;
  men's file MRECMTH `mmth1`-`mmth24`. Internet: `v171a` (use ever / last 12 months), `v171b` (frequency last month: 0 not at all,
  1 less than weekly, 2 at least weekly, 3 almost every day); phone: `v169a` owns a mobile, `v169c` smartphone; design: `v005` weight,
  `v001` cluster, `v021` PSU, `v022` strata, `v012` age, `v025` residence, `v106` education, `v190` wealth. Jordan 2023 has no RECMTH file.
  In Lesotho the GAD items are labelled "NA -" (not fielded). IPUMS DHS names: DEPRESSIONSCORE (MTH22), GADSCORE (MTH24), DEPRESSIONREFER,
  DEPRESSIONDIAG, ANXIETYDIAG, the 16 item variables (GADNERVOUS2WK ... DEPHURTSELF2WK), INTERNETEVYR, INTERNETMO, CELLPHONSELF,
  CELLPHONESMART, MOBPHONE; men's files add the suffix MN.

## Module inventory (`data/compiled/dhs8/dhs8_module_inventory.csv`)

| Survey | Module | Women | Men | IPUMS DHS (Oct 2026) |
|---|---|---|---|---|
| Nepal 2022 | PHQ-9 + GAD-7 | 7,442 in the men's-survey household subsample | 4,913 | np2022ir with scores and internet/phone items; no men's file |
| Mozambique 2022-23 | PHQ-9 + GAD-7 | all 13,183 women | 5,380 | mz2022ir with scores and CELLPHONESMART; INTERNETMO/INTERNETEVYR not integrated; no men's file |
| Bangladesh 2022 | PHQ-9 + GAD-7 | 20,029 ever-married women in long-questionnaire households | no men's survey | bd2022ir complete |
| Zambia 2024 | PHQ-9 + GAD-7 | all 13,951 women | 12,585 | not in IPUMS DHS |
| Lesotho 2023-24 | PHQ-9 only | 3,297 (subsample) | 3,215 | ls2023ir without the module variables |
| Kenya 2022 | diagnosis only | men's-survey households | yes | ke2022ir DEPRESSIONDIAG, ANXIETYDIAG, CELLPHONESMART (no INTERNETMO) |
| Madagascar 2021 | diagnosis only | all women | men 15-59 | mg2021ir DEPRESSIONDIAG + INTERNETEVYR; mg2021mr DEPRESSIONDIAGMN + INTERNETMOMN |
| Mali 2023-24, DR Congo 2023-24 | diagnosis only | all women | yes | not in IPUMS DHS |
| 22 others incl. Jordan 2023, Cambodia 2021-22, Tanzania 2022, Ghana 2022, Philippines 2022 | none | | | |

Published cutoffs: PHQ-9 >= 10 everywhere; "symptoms of anxiety" = GAD-7 >= 6 in Nepal, Mozambique and Bangladesh (categories 0-5 / 6-14 /
15-21, so GAD-7 >= 10 is not recoverable from those reports) and GAD-7 >= 10 in Zambia (categories 0-4 / 5-9 / 10-14 / 15-21). Nepal also
tabulates TPO Nepal's national cutoffs (GAD-7 >= 7 and PHQ-9 >= 11 for 15-19; >= 9 / >= 10 for adults; Table 19.5).

## Published prevalence, ages 15-19 (weighted, from the report tables)

| Survey | Sex | n | PHQ-9 >= 10 | Anxiety (report def.) | Ever told: depression |
|---|---|---|---|---|---|
| Nepal 2022 | women | 1,322 | 4.5 | 18.3 (>= 6) | 1.1 |
| Nepal 2022 | men | 985 | 1.6 | 10.0 (>= 6) | 0.3 |
| Mozambique 2022-23 | women | 3,050 | 8.6 | 21.6 (>= 6) | 0.8 |
| Mozambique 2022-23 | men | 1,386 | 2.1 | 6.6 (>= 6) | 0.1 |
| Bangladesh 2022 | women (ever-married) | 1,729 | 3.7 | 12.9 (>= 6) | 2.6 |
| Lesotho 2023-24 | women | 649 | 7.3 | not asked | 8.1 |
| Lesotho 2023-24 | men | 616 | 4.0 | not asked | 4.1 |
| Zambia 2024 | women | 3,292 | 0.7 | 0.5 (>= 10) | 0.7 |
| Zambia 2024 | men | 3,002 | 0.4 | 0.2 (>= 10) | 0.9 |
| Kenya 2022 (ever told depression or anxiety) | women / men | 3,125 / 3,175 | - | - | 2.5 / 1.6 |

Zambia's levels are an order of magnitude below the others (women 15-49: PHQ-9 >= 10 about 1-2%), which looks like a reporting-norm or
administration difference of the kind seen across MICS surveys rather than a real gap; it is a reason to compare within surveys only.

## Microdata coding (`scripts/analysis/29_dhs8_pooled.py`)

- Sample: women with valid PHQ-9 and GAD-7 (DEPRESSIONSCORE <= 27, GADSCORE <= 21; 99 = not in the module universe): Nepal 7,442, Mozambique
  13,183, Bangladesh 19,987. Age groups 15-19 / 20-24 / 25-49 from AGE.
- Outcomes: PHQ-9 >= 10, GAD-7 >= 10, GAD-7 >= 6 (report definition), continuous scores.
- Exposures: `net_daily` = INTERNETMO == 3, `net_weekly` = INTERNETMO >= 2; INTERNETMO is 9 (NIU) for women who never used the internet or
  not in the last 12 months (INTERNETEVYR 0 or 12) in Bangladesh, and these are coded as non-users (in Nepal IPUMS already codes them 0).
  `smart` = CELLPHONESMART == 1 (9 = owns no phone -> 0), `ownphone` = CELLPHONSELF == 1. Mozambique has no internet variables in IPUMS.
- Weights PERWEIGHT/1e6 (v005); the module subsamples (Nepal) are random household subsamples, and the weighted means reproduce the
  report tables exactly (PHQ-9 >= 10 at 15-19: 4.5 / 8.6 / 3.7; GAD-7 >= 6: 18.3 / 21.6 / 12.9), so no module-specific weight is needed.
  Pooled models normalise each survey's weights to sum to its n.
- Models: pyfixest `feols`, cluster FE (`cl` = sample x CLUSTERNO) with C(WEALTHQ) + C(EDUCLVL) + C(AGE) controls, CRV1 by cluster;
  pooled models use `| cl + sample^WEALTHQ + sample^EDUCLVL + sample^AGE`. "none" rows swap the FE for an urban dummy (Phase 1 comparison).
  A precision-weighted average of the per-survey cluster-FE estimates is written alongside the pooled regression (`sample == "meta"`).
- Replication: the Nepal 15-19 daily-internet rows equal `results/tables/dhs_nepal_2022.csv` to 1e-6 (PHQ-9 >= 10 +2.306 (2.367),
  GAD-7 >= 10 +3.459 (2.919), n = 1,293); the script asserts this.

## Key estimates (women; pp; cluster-robust SE)

| Exposure, ages 15-19 | Nepal | Bangladesh | Mozambique | Pooled | Pooled 25-49 |
|---|---|---|---|---|---|
| Daily internet -> PHQ-9 >= 10 | +2.31 (2.37) | -0.34 (1.83) | n/a | +0.79 (1.46), n 2,770 | -0.32 (0.54) |
| Daily internet -> GAD-7 >= 10 | +3.46 (2.92) | +0.61 (1.34) | n/a | +1.82 (1.47) | -0.37 (0.60) |
| Smartphone -> PHQ-9 >= 10 | -2.22 (1.71) | +1.54 (1.89) | +0.87 (1.57) | +0.36 (1.01), n 5,841 | -0.54 (0.45) |
| Smartphone -> GAD-7 >= 10 | -0.36 (2.28) | +2.05 (1.46) | +1.82 (1.80) | +1.38 (1.05) | -0.36 (0.50) |

Daily internet use at 15-19: Nepal 42.1%, Bangladesh 27.0% (36.1% used the internet in the last 12 months among women actually asked; the
report's 24.2% counts short-questionnaire women as non-users); smartphone 52.2% / 34.8% / 18.6% (Nepal / Bangladesh / Mozambique).
Diagnosis-only set (`dhs8_diag.csv`): Kenya 15-19 women, smartphone -> ever diagnosed depression -0.09 (1.34), n 2,904, base 1.4%;
Madagascar women ever-internet +0.73 (0.77); Madagascar men daily internet -0.51 (0.47).

## Literature

`data/compiled/dhs8/dhs8_literature.csv` (11 entries, DOI/URL, numbers checked against the full text where accessible; the Bangladesh
internet-use paper and the Zambia IPV paper are known only from login-walled author summaries and are marked NOT VERIFIED; the Lesotho
paper's figures come from the authors' public summary). No published analysis models adolescents separately or uses internet frequency or
smartphone ownership as the exposure of interest.

## Gaps and what a follow-up needs

- Men's PHQ-9/GAD-7 files (Nepal NPMR82FL, Mozambique MZMR81FL, Zambia ZMMR81FL, Lesotho LSMR81FL) and the Zambia 2024 women's file
  (ZMIR81FL) are not in IPUMS DHS; Mozambique's v171a/v171b and Lesotho's mth* are not yet integrated. A DHS Program data request
  (https://dhsprogram.com/data/new-user-registration.cfm) for these recode files, placed in `data/external/dhs8/microdata/`, would allow a
  five-survey, two-sex pool; the raw variable names above are what `29_dhs8_pooled.py` would need mapped onto the IPUMS names.
- The IPUMS DHS integration pulls here are internal copies; a user with an IPUMS DHS extract converts it to parquet as
  `data/ipums/dhs/<sample>.parquet` (IPUMS variable names) and runs `scripts/extract/dhs_extract.py` then `29_dhs8_pooled.py`.
- Bangladesh's 15-19 group is ever-married only; Nepal's and Mozambique's are all women.
- Cross-survey levels differ by an order of magnitude (Zambia), so only within-survey contrasts are used.
