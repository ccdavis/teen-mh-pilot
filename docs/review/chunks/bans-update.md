<!-- Generated review chunk: bans-update -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-bans-update)

Context: Teen Distress Pilot → Part 4 · The interaction (H3): phones in the same hours as high-pressure school → School phone bans → Post-2021 waves and the first post-ban observations

Editable source entry points: [scripts/report/90_build_report.py:1](../../../scripts/report/90_build_report.py#L1)

---

Phase 1 ended with the observation that the post-2021 waves of the state youth surveys showed a broad decline in sadness that began before any statewide phone mandate. Two new county waves and the 2025 YRBS state files now extend that record. Pennsylvania's 2025 county profile reports (60 counties) and California's CalSCHLS county reports for 2019-21 and 2021-23 (and 2023-25 where posted) were added to the county panel; the CDC released the 2025 combined YRBS state files on 21 September 2026, which allows the pre-specified difference-in-differences for the first statewide mandates (Indiana's instructional-time ban and Louisiana's and South Carolina's bell-to-bell bans, all in force in 2024-25). Minnesota's 2022 and 2025 county tables remain behind a bot-manager CAPTCHA (`notes/state_surveys.md`), and Florida, the earliest mandate state, left the YRBS after 2021.

##### County-mean sadness through the newest waves

![Chart: bans_update_state_trends](../../figures/bans_update_state_trends.png)

Unweighted county means of the share of students sad or hopeless for two or more weeks, over the grades each state reports in every wave (as in Part 1), with the national YRBS for comparison (dotted). Dashed verticals mark the first school year a statewide mandate is in force (Maine 2026-27; California district-policy mandate 2026-27; Illinois 2027-28); Washington has guidance only and Pennsylvania no mandate. Grey band: 2020.

Every state with a post-2021 wave has now turned down, and in every case the first wave below the peak precedes the state's mandate or the state has none. Pennsylvania's 2025 wave (fall 2025, no statewide mandate; the state funded lockable pouches) continues the 2021 to 2023 decline: county-mean sadness 31.5% (2021), 28.1% (2023), 25.8% (2025), and considered suicide 19.6%, 17.0%, 15.5%. California's county reports for 2019-21 and 2021-23 (a mandate applies only from 2026-27) put county-mean sadness at 32.4% (2017-19), 39.2% (2019-21) and 37.0% (2021-23), falling to 31.5% in 2023-25. Washington fell from 40.7% (2021) to 27.1% (2025) under guidance only, Illinois from 40.7% (2022) to 34.7% (2024) three years before its 2027-28 ban, and Maine was flat between 2021 (36.6%) and 2023 (36.3%) before its 2026-27 ban. Nationally the YRBS shows 42.1% (2021), 39.7% (2023) and 33.3% (2025) sad or hopeless (girls 56.6 to 43.4%, boys 28.6 to 23.9%), considered suicide 21.9% to 14.5%, while the share using social media several times a day or more rose from 77.1% to 80.3%.

| State (county survey) | Peak wave    | First wave below the peak | Newest wave  | Statewide policy (2026-09)           | In force from | Downturn relative to mandate |
|-----------------------|--------------|---------------------------|--------------|--------------------------------------|---------------|------------------------------|
| Washington            | 2021 (40.7%) | 2023 (31.3%)              | 2025 (27.1%) | guidance/recommendation only         | none          | before the mandate           |
| Maine                 | 2021 (36.6%) | 2023 (36.3%)              | 2023 (36.3%) | statewide bell-to-bell ban           | 2026-27       | before the mandate           |
| Illinois              | 2022 (40.7%) | 2024 (34.7%)              | 2024 (34.7%) | statewide bell-to-bell ban           | 2027-28       | before the mandate           |
| Pennsylvania          | 2021 (31.5%) | 2023 (28.1%)              | 2025 (25.8%) | none                                 | none          | before the mandate           |
| California            | 2021 (39.2%) | 2023 (37.0%)              | 2025 (31.5%) | requires districts to adopt a policy | 2026-27       | before the mandate           |

Peak and first post-peak wave of county-mean sadness in each state survey against the first school year with a statewide mandate in force (`data/compiled/phone_bans/state_phone_bans.csv`, status September 2026).

##### 2025 YRBS: states with a mandate in force in 2024-25 against states without one

Treated: Indiana (ban during instructional time, 2024-25), Louisiana (bell-to-bell ban, 2024-25), South Carolina (bell-to-bell ban, 2024-25). Controls: the 23 other states in the 2025 YRBS state files with no mandate in force before 2025-26; the "clean" subset (10 states) also excludes states that enacted a law before the end of the spring-2025 fieldwork. State-year cells are weighted equally with state and year fixed effects; standard errors are clustered by state, and because only three states are treated the bracketed p-value comes from randomization inference over every possible assignment of three treated states. The placebo repeats the design on 2017-2023 with 2021-23 as a false post period. Florida and Minnesota, the other two 2024-25 mandate states, have no 2025 YRBS data, and item coverage differs across the treated states (South Carolina asked no suicide items in 2021 and has no 2023 wave; Indiana has no 2025 attempt item), so the considered-suicide rows rest on two states and the attempt row on Louisiana alone.

| Outcome                           | Sex   | DiD 2021-23 vs 2025 (SE) \[RI p\] | Clean controls only   | Placebo: 2017-19 vs 2021-23 | Treated / control states |
|-----------------------------------|-------|-----------------------------------|-----------------------|-----------------------------|--------------------------|
| Sad or hopeless                   | all   | -4.84 (1.84) \[0.01\]             | -6.11 (1.94) \[0.00\] | -1.17 (1.39) \[0.64\]       | 3 / 21; placebo 2 / 21   |
|                                   | girls | -3.45 (2.23) \[0.17\]             | -5.82 (2.44) \[0.01\] | -3.92 (3.23) \[0.25\]       | 3 / 21; placebo 2 / 21   |
|                                   | boys  | -6.38 (1.80) \[0.00\]             | -6.43 (1.98) \[0.01\] | +1.62 (1.32) \[0.56\]       | 3 / 21; placebo 2 / 21   |
| Considered suicide                | all   | -3.46 (0.53) \[0.02\]             | -4.12 (0.61) \[0.02\] | -2.78 (0.65) \[0.13\]       | 2 / 21; placebo 2 / 20   |
|                                   | girls | -5.21 (0.73) \[0.03\]             | -6.95 (0.83) \[0.02\] | -5.08 (1.39) \[0.05\]       | 2 / 21; placebo 2 / 20   |
|                                   | boys  | -1.56 (0.69) \[0.26\]             | -1.10 (0.84) \[0.45\] | -0.42 (0.71) \[0.81\]       | 2 / 21; placebo 2 / 20   |
| Attempted suicide                 | all   | -5.77 (0.36) \[0.05\]             | -5.38 (0.52) \[0.10\] | +0.50 (2.03) \[0.75\]       | 1 / 21; placebo 2 / 19   |
|                                   | girls | -4.86 (0.49) \[0.05\]             | -4.82 (0.76) \[0.20\] | -2.14 (2.61) \[0.10\]       | 1 / 21; placebo 2 / 19   |
|                                   | boys  | -6.66 (0.44) \[0.05\]             | -5.84 (0.77) \[0.10\] | +3.22 (1.35) \[0.03\]       | 1 / 21; placebo 2 / 19   |
| Social media several times a day+ | all   | +6.04 (2.74) \[0.03\]             | +5.54 (2.95) \[0.09\] | \-                          | 2 / 14                   |
|                                   | girls | +5.02 (3.91) \[0.11\]             | +4.82 (4.12) \[0.15\] | \-                          | 2 / 14                   |
|                                   | boys  | +7.18 (1.57) \[0.02\]             | +6.44 (1.86) \[0.07\] | \-                          | 2 / 14                   |

Percentage-point difference-in-differences from `results/tables/yrbs25_ban_did.csv`; weighted state estimates from the 2023 and 2025 combined YRBS files. The social-media item (several times a day or more) exists only for 2023 and 2025, so it has no placebo. Treated/control counts are the states observed both before and after.

![Chart: bans_update_event](../../figures/bans_update_event.png)

Event study for sad or hopeless: treated-minus-control difference by wave relative to 2021 (state and year fixed effects, 95% intervals from state-clustered SEs; 2015-2025, 3 treated and 23 control states).
