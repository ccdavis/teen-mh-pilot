<!-- Generated review chunk: dhs8 -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-dhs8)

Context: Teen Distress Pilot → Part 2 · Phones and social media (H1) → Phone-first countries: MICS Child Functioning Module (69 surveys, 2017–2025) → DHS-8 self-reports beyond Nepal

Editable source entry points: [scripts/report/90_build_report.py:1](../../../scripts/report/90_build_report.py#L1)

---

| Survey                            | Module         | Women asked                                                                | Men asked                                         | Internet frequency item                      | Smartphone item | IPUMS DHS file (October 2026)                                                                              |
|-----------------------------------|----------------|----------------------------------------------------------------------------|---------------------------------------------------|----------------------------------------------|-----------------|------------------------------------------------------------------------------------------------------------|
| Nepal 2022                        | PHQ-9 + GAD-7  | women 15-49 in the men's-survey household subsample (n = 7,442)            | yes, men 15-49 in the same households (n = 4,913) | yes                                          | yes             | np2022ir: DEPRESSIONSCORE, GADSCORE, ANXIETYDIAG, INTERNETMO, CELLPHONESMART; no men's file                |
| Bangladesh 2022                   | PHQ-9 + GAD-7  | ever-married women 15-49 in the long-questionnaire households (n = 20,029) | no (no men's survey)                              | yes                                          | yes             | bd2022ir: DEPRESSIONSCORE, GADSCORE, ANXIETYDIAG, INTERNETMO, CELLPHONESMART                               |
| Mozambique 2022-23                | PHQ-9 + GAD-7  | all women 15-49 (n = 13,183)                                               | yes, men 15-49 (n = 5,380)                        | yes (in the report; not yet in IPUMS DHS)    | yes             | mz2022ir: DEPRESSIONSCORE, GADSCORE, CELLPHONESMART; INTERNETMO/INTERNETEVYR not integrated; no men's file |
| Zambia 2024                       | PHQ-9 + GAD-7  | all women 15-49 (n = 13,951)                                               | yes, men 15-49 (n = 12,585)                       | yes                                          | yes             | not in IPUMS DHS (sample not yet released there)                                                           |
| Lesotho 2023-24                   | PHQ-9 only     | women 15-49 in a household subsample (n = 3,297)                           | yes, men 15-49 (n = 3,215)                        | yes                                          | yes             | ls2023ir integrated without the mental-health variables                                                    |
| Madagascar 2021                   | diagnosis only | women 15-49                                                                | yes, men 15-59                                    | ever-use only (women); frequency (men)       | no              | mg2021ir: DEPRESSIONDIAG, DEPRESSIONTR, INTERNETEVYR; mg2021mr: DEPRESSIONDIAGMN, INTERNETMOMN             |
| Kenya 2022                        | diagnosis only | women 15-49 in the men's-survey households                                 | yes, men 15-49                                    | no frequency item in IPUMS (v171a/b fielded) | yes             | ke2022ir: DEPRESSIONDIAG, ANXIETYDIAG, CELLPHONESMART                                                      |
| Mali 2023-24                      | diagnosis only | women 15-49                                                                | yes, men 15-49                                    | yes                                          | yes             | not in IPUMS DHS                                                                                           |
| Congo Democratic Republic 2023-24 | diagnosis only | women 15-49                                                                | yes, men 15-49                                    | yes                                          | yes             | not in IPUMS DHS                                                                                           |

DHS surveys with any mental-health content among the 31 final reports released for 2019+ fieldwork. Raw recode names: GAD-7 items mth1–mth7, PHQ-9 items mth8–mth16, provider diagnosis mth19/mth20, scores mth22/mth24 (men: mmth\*), internet v171a/v171b, smartphone v169c.

##### Published prevalence at ages 15–19

![Chart: dhs8_prev](../../figures/dhs8_prev.png)

Percentage of 15–19-year-olds with a PHQ-9 score of 10 or more, from the final-report tables (weighted). Zambia's levels are an order of magnitude below the other surveys; the anxiety columns of the table use each report's own cutoff (GAD-7 ≥ 6 in Nepal, Mozambique and Bangladesh; ≥ 10 in Zambia).

| Survey             | Sex   | Ages  | n (weighted) | PHQ-9 ≥ 10 (%) | PHQ-9 ≥ 5 (%) | Anxiety, report definition (%) | GAD-7 ≥ 10 (%) | Ever told had depression (%) |
|--------------------|-------|-------|--------------|----------------|---------------|--------------------------------|----------------|------------------------------|
| Bangladesh 2022    | women | 15-19 | 1,729        | 3.7            | 23.8          | 12.9 (GAD-7 \>= 6)             |                | 2.6                          |
| Lesotho 2023-24    | men   | 15-19 | 616          | 4.0            | 19.2          | not asked                      |                | 4.1                          |
| Lesotho 2023-24    | women | 15-19 | 649          | 7.3            | 20.0          | not asked                      |                | 8.1                          |
| Mozambique 2022-23 | men   | 15-19 | 1,386        | 2.1            | 11.0          | 6.6 (GAD-7 \>= 6)              |                | 0.1                          |
| Mozambique 2022-23 | women | 15-19 | 3,050        | 8.6            | 23.9          | 21.6 (GAD-7 \>= 6)             |                | 0.8                          |
| Nepal 2022         | men   | 15-19 | 985          | 1.6            | 11.0          | 10.0 (GAD-7 \>= 6)             |                | 0.3                          |
| Nepal 2022         | women | 15-19 | 1,322        | 4.5            | 18.3          | 18.3 (GAD-7 \>= 6)             |                | 1.1                          |
| Zambia 2024        | men   | 15-19 | 3,002        | 0.4            | 5.1           | 0.2 (GAD-7 \>= 10)             | 0.2            | 0.9                          |
| Zambia 2024        | women | 15-19 | 3,292        | 0.7            | 6.3           | 0.5 (GAD-7 \>= 10)             | 0.5            | 0.7                          |

Severity tables of the DHS-8 mental-health chapters, ages 15–19 (the 20–24 and 25–49 rows, the residence splits and the source table and page numbers are in `results/tables/dhs8_prevalence_published.csv`). Bangladesh interviewed ever-married women only, so its 15–19 group is a selected (early-married) population. Lesotho did not field the GAD-7. For the diagnosis-only surveys the share of 15–19-year-olds ever told by a provider that they had depression or anxiety is Congo Democratic Republic 2023-24 men 0.5%; Congo Democratic Republic 2023-24 women 0.7%; Kenya 2022 men 1.6%; Kenya 2022 women 2.5%; Madagascar 2021 men 0.2%; Madagascar 2021 women 1.0%; Mali 2023-24 men 1.0%; Mali 2023-24 women 2.1%.

##### Microdata: pooled within-cluster estimates

IPUMS DHS has integrated the women's files of three of the four PHQ-9/GAD-7 surveys (Nepal, Mozambique, Bangladesh; Zambia 2024 and all men's files are not yet available there, and Mozambique's file does not yet carry the internet-frequency item). Weighted means from these files reproduce the final-report tables exactly (for example PHQ-9 ≥ 10 at 15–19: Nepal 4.5% vs 4.5% published; Mozambique 8.6% vs 8.6%; Bangladesh 3.7% vs 3.7%), and the Nepal rows reproduce the Phase 1 estimates to the third decimal. We then re-ran the Nepal specification on each survey and on the pooled file: women who use the internet almost daily (or weekly or more, or who own a smartphone or any phone) are compared with non-users in the same sampling cluster, with wealth quintile, education level and single-year age controls, survey weights, and standard errors clustered by sampling cluster; the pooled rows add survey-by-cluster fixed effects, let the control effects differ by survey, and normalise each survey's weights to its sample size. Among 15–19-year-old women, 42.1% in Nepal and 27.0% in Bangladesh use the internet almost daily, and 52.2%, 34.8% and 18.6% (Nepal, Bangladesh, Mozambique) own a smartphone.

![Chart: dhs8_coef](../../figures/dhs8_coef.png)

Percentage-point difference in screening positive between users and non-users in the same sampling cluster, by age group; circles PHQ-9 ≥ 10, diamonds GAD-7 ≥ 10; black markers are the pooled survey-by-cluster fixed-effects estimates. The 25–49 group is the falsification contrast.

| Exposure                  | Ages  | Nepal · PHQ-9 ≥ 10 | Bangladesh · PHQ-9 | Mozambique · PHQ-9 | Pooled · PHQ-9 | Nepal · GAD-7 ≥ 10 | Bangladesh · GAD-7 | Mozambique · GAD-7 | Pooled · GAD-7 | Pooled n |
|---------------------------|-------|--------------------|--------------------|--------------------|----------------|--------------------|--------------------|--------------------|----------------|----------|
| almost-daily internet use | 15-19 | +2.31 (2.37)       | -0.34 (1.83)       | —                  | +0.79 (1.46)   | +3.46 (2.92)       | +0.61 (1.34)       | —                  | +1.82 (1.47)   | 2,770    |
|                           | 20-24 | +1.39 (2.49)       | +0.28 (0.98)       | —                  | +0.52 (0.94)   | +3.57 (2.55)       | +0.16 (1.00)       | —                  | +0.90 (0.97)   | 4,411    |
|                           | 25-49 | -1.05 (1.13)       | -0.04 (0.61)       | —                  | -0.32 (0.54)   | -2.97 (1.32)       | +0.60 (0.66)       | —                  | -0.37 (0.60)   | 19,884   |
| weekly+ internet use      | 15-19 | +2.42 (2.28)       | -0.94 (1.70)       | —                  | +0.47 (1.38)   | +2.80 (2.42)       | +0.58 (1.25)       | —                  | +1.51 (1.25)   | 2,770    |
|                           | 20-24 | +3.01 (2.42)       | -0.99 (0.87)       | —                  | -0.20 (0.85)   | +3.71 (2.74)       | -0.49 (0.89)       | —                  | +0.34 (0.90)   | 4,411    |
|                           | 25-49 | -0.71 (1.13)       | -0.28 (0.56)       | —                  | -0.40 (0.51)   | -1.61 (1.29)       | +0.42 (0.60)       | —                  | -0.11 (0.56)   | 19,884   |
| owns a smartphone         | 15-19 | -2.22 (1.71)       | +1.54 (1.89)       | +0.87 (1.57)       | +0.36 (1.01)   | -0.36 (2.28)       | +2.05 (1.46)       | +1.82 (1.80)       | +1.38 (1.05)   | 5,841    |
|                           | 20-24 | -1.30 (2.59)       | +0.08 (0.77)       | +0.58 (3.16)       | -0.02 (0.95)   | +3.04 (3.02)       | +0.09 (0.74)       | -1.62 (2.64)       | +0.16 (0.89)   | 6,981    |
|                           | 25-49 | -1.67 (1.04)       | -0.15 (0.54)       | -0.59 (1.24)       | -0.54 (0.45)   | -2.59 (1.11)       | +0.68 (0.56)       | -1.43 (1.54)       | -0.36 (0.50)   | 27,332   |
| owns a phone              | 15-19 | -1.70 (1.84)       | +1.24 (1.59)       | +1.30 (1.50)       | +0.70 (0.96)   | -1.01 (2.34)       | +1.08 (1.18)       | +2.95 (1.95)       | +1.58 (1.12)   | 5,841    |
|                           | 20-24 | -3.96 (3.42)       | +0.87 (0.75)       | +1.83 (2.36)       | +0.76 (0.96)   | -3.61 (3.53)       | +1.10 (0.72)       | +2.57 (2.47)       | +1.17 (0.99)   | 6,981    |
|                           | 25-49 | -1.03 (1.21)       | +0.58 (0.50)       | -0.81 (1.48)       | +0.05 (0.50)   | -0.33 (1.44)       | +1.27 (0.52)       | -0.28 (1.61)       | +0.70 (0.54)   | 27,332   |

Coefficients in percentage points with cluster-robust standard errors in parentheses; women only. Full results, the continuous-score and GAD-7 ≥ 6 outcomes, the urban/rural splits and a precision-weighted average of the per-survey estimates are in `results/tables/dhs8_estimates.csv`.
