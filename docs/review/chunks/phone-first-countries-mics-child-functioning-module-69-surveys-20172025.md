<!-- Generated review chunk: phone-first-countries-mics-child-functioning-module-69-surveys-20172025 -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-phone-first-countries-mics-child-functioning-module-69-surveys-20172025)

Context: Teen Distress Pilot → Part 2 · Phones and social media (H1) → Phone-first countries: MICS Child Functioning Module (69 surveys, 2017–2025)

Editable source entry points: [scripts/report/90_build_report.py:306](../../../scripts/report/90_build_report.py#L306)

---

### Phone-first countries: MICS Child Functioning Module (69 surveys, 2017–2025)

MICS6 and MICS7 surveys (2017 onward) administer the Washington Group / UNICEF Child Functioning Module for children aged 5–17, asking the mother or primary caregiver how often the child "seems very anxious, nervous or worried" and how often the child seems "very sad or depressed" (daily, weekly, monthly, a few times a year, or never), using identical wording across countries. In the same households, women aged 15–49 (and men in roughly half the surveys) report mobile-phone ownership and how often they used the internet and a mobile phone over the past three months, while the household questionnaire records home internet access. Reading all 69 MICS samples with the module on the IPUMS-MICS server (the 68 used in Phase 1 plus Bangladesh 2025, released in October 2026) yields 544,018 children with valid responses and weights across 68 surveys (54 of which also include the young-adult internet items).

##### Prevalence across surveys

![Chart: mics_scatter](../../figures/mics_scatter.png)

One point per survey (ages 10–17, across the 54 surveys that also record young-adult internet use). Cross-survey variation in caregiver-reported anxiety is wide—ranging from under 1% in Laos, Tuvalu, Vietnam, and Turkmenistan to 40–50% in Tunisia, Afghanistan, the Central African Republic, and Chad—and largely reflects national reporting norms, which is why all tests below compare children within the same country and region.

##### Use and symptoms within countries

![Chart: mics_coef](../../figures/mics_coef.png)

Cluster rows regress children's daily/weekly anxiety on the share of 15–24-year-olds in their sampling cluster who use the internet almost daily (or own a mobile phone, or the household internet share), with survey-by-region fixed effects, household wealth quintile, urban/rural status, and age controls, and standard errors clustered by sampling cluster. Own-use rows link 15–17-year-olds to their own individual record in the women's or men's questionnaire (85% of girls matched, 24% of boys) and compare users with non-users within the same sampling cluster.

Girls aged 10–17 living in sampling clusters where more young adults use the internet daily are reported as slightly more anxious (+0.24 pp per 10-percentage-point rise in the cluster share, SE 0.12). However, a similar positive association appears for 5–9-year-old girls (+0.14 pp, SE 0.11), who are too young to use phones themselves, indicating that this reflects characteristics of more connected communities rather than adolescent phone use. Cluster-level mobile-phone ownership is *negatively* associated with caregiver-reported anxiety across all age and sex groups; household internet access shows a small positive association for 10–17-year-old girls (+0.21 pp per 10 points, SE 0.12, and +0.01 pp at ages 5–9); and caregiver-reported depression shows no positive relationship with any connectivity measure. Comparing 15–17-year-olds who use the internet or a phone daily with non-users in the same sampling cluster—the closest MICS equivalent to individual-level screen exposure—yields point estimates for girls that are near zero or slightly negative: −0.1 pp on anxiety (SE 1.4) and −1.8 pp on depression (SE 1.3) for daily internet use, and −2.2 pp on anxiety (SE 1.2) for daily phone use. For boys, the within-cluster own-phone-use coefficients are positive (+4.4 pp on anxiety and +5.5 pp on depression, SE 2.3 and 1.9), though these rely on the roughly one-quarter of boys interviewed in the men's sub-sample. The learning and friendship functioning items show no meaningful association in either sex.

##### Two-round countries

| Country | Ages  | Sex   | Rounds      | Anxious daily/weekly % | Depressed daily/weekly % |
|---------|-------|-------|-------------|------------------------|--------------------------|
| BGD     | 10-14 | boys  | 2019 → 2025 | 6.8 → 4.1              | 9.3 → 5.5                |
| BGD     | 10-14 | girls | 2019 → 2025 | 6.9 → 3.9              | 8.5 → 5.7                |
| BGD     | 15-17 | boys  | 2019 → 2025 | 7.2 → 5.0              | 7.7 → 6.0                |
| BGD     | 15-17 | girls | 2019 → 2025 | 9.0 → 7.1              | 9.2 → 8.3                |
| KGZ     | 10-14 | boys  | 2018 → 2023 | 11.3 → 7.5             | 7.0 → 6.3                |
| KGZ     | 10-14 | girls | 2018 → 2023 | 13.1 → 8.2             | 7.5 → 7.4                |
| KGZ     | 15-17 | boys  | 2018 → 2023 | 10.7 → 9.3             | 5.5 → 4.3                |
| KGZ     | 15-17 | girls | 2018 → 2023 | 11.9 → 12.7            | 6.5 → 6.8                |
| MNG     | 10-14 | boys  | 2018 → 2023 | 7.5 → 11.2             | 4.4 → 7.6                |
| MNG     | 10-14 | girls | 2018 → 2023 | 9.9 → 13.3             | 6.3 → 9.0                |
| MNG     | 15-17 | boys  | 2018 → 2023 | 15.0 → 11.9            | 7.4 → 7.5                |
| MNG     | 15-17 | girls | 2018 → 2023 | 20.5 → 16.0            | 13.7 → 10.6              |
| TKM     | 10-14 | boys  | 2019 → 2024 | 0.8 → 4.7              | 0.7 → 2.8                |
| TKM     | 10-14 | girls | 2019 → 2024 | 0.8 → 2.1              | 0.9 → 1.7                |
| TKM     | 15-17 | boys  | 2019 → 2024 | 0.8 → 4.3              | 0.6 → 1.3                |
| TKM     | 15-17 | girls | 2019 → 2024 | 1.7 → 4.8              | 0.8 → 3.1                |
| TUN     | 10-14 | boys  | 2018 → 2023 | 42.7 → 30.1            | 15.8 → 13.8              |
| TUN     | 10-14 | girls | 2018 → 2023 | 37.5 → 28.0            | 12.9 → 14.5              |
| TUN     | 15-17 | boys  | 2018 → 2023 | 40.7 → 34.6            | 15.5 → 17.5              |
| TUN     | 15-17 | girls | 2018 → 2023 | 39.6 → 30.9            | 16.3 → 20.8              |

Countries with both a MICS6 and a MICS7 round on the server (Pakistan is excluded because its rounds sample different provinces). Turkmenistan rises from a very low baseline; Bangladesh (2019 → 2025, the newest MICS7 release, over a period of rapid smartphone diffusion), Kyrgyzstan and Tunisia decline; Mongolia is mixed.

**Assessment.** Across 68 MICS surveys, neither local young-adult connectivity nor a teenage girl's own daily internet or phone use predicts caregiver-reported anxiety or depression within sampling clusters, and the small positive cluster correlation for girls' anxiety is shared by 5–9-year-olds. Three qualifications apply: the outcome is reported by caregivers rather than adolescents themselves; the exposure measures current use rather than exogenous network rollout timing; and only five countries currently offer repeated MICS rounds with the module.

#### DHS-8 self-reports beyond Nepal

The Phase 1 report used one survey with adolescent self-reports of depression and anxiety outside the school-based GSHS: the Nepal 2022 DHS. The DHS Program's optional DHS-8 mental-health module administers the GAD-7 and PHQ-9 to women (and, in some surveys, men) aged 15–49 together with the standard internet-frequency and smartphone items, so every additional survey that fields it is a second self-report test of the MICS caregiver null. We read the final reports of all 31 DHS surveys with fieldwork from 2019 released by October 2026, checked the DHS-8 recode data dictionaries, and inventoried the IPUMS DHS integrated files. 4 surveys carry both scales (Nepal 2022, Mozambique 2022–23, Bangladesh 2022, Zambia 2024), 1 carries the PHQ-9 only (Lesotho 2023–24), 4 ask only whether a provider ever diagnosed depression or anxiety (Kenya 2022, Madagascar 2021, Mali 2023–24, DR Congo 2023–24), and the remaining 22, including the Jordan 2023 and Cambodia 2021–22 surveys named in the Phase 2 plan, have no mental-health chapter and no RECMTH file in their recode. The DHS Program API and STATcompiler publish no indicator from the module, so the published figures below were parsed from the final-report tables.
