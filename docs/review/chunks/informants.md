<!-- Generated review chunk: informants -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-informants)

Context: Teen Distress Pilot → Part 2 · Phones and social media (H1) → Who reports the symptoms: U.S. caregivers and adolescents (NSCH 2016–2025, NHIS 2021–2024)

Editable source entry points: [scripts/report/90_build_report.py:662](../../../scripts/report/90_build_report.py#L662)

---

### Who reports the symptoms: U.S. caregivers and adolescents (NSCH 2016–2025, NHIS 2021–2024)

The MICS result above rests on caregivers describing their children, while the GSHS and DHS-8 gradients come from adolescents describing themselves. Two U.S. surveys separate the informant from the setting: the National Survey of Children's Health asks parents about diagnosed, current anxiety and depression alongside a graded screen-time item, and the National Health Interview Survey asks parents the MICS items while a subsample of the same 12–17-year-olds answers the PHQ-2 and GAD-2 in NHIS-Teen.

#### Parent-reported anxiety and depression in the United States: NSCH 2016–2025

The National Survey of Children's Health (HRSA/Census) asks a parent or caregiver each year whether a doctor or other health care provider has *ever* told them the child has anxiety problems or depression, whether the child *currently* has the condition, and how severe it is, alongside a single weekday screen-time item ("on most weekdays, about how much time did this child spend in front of a TV, computer, cellphone or other electronic device … do not include time spent doing schoolwork"), weeknight sleep, bullying victimization, school engagement, and the state of residence. It is the U.S. counterpart to the MICS caregiver reports above: the same informant, but asked about diagnosed conditions rather than how often the child seems anxious or sad. We use the public-use topical files for 2016–2025 (293,751 children aged 6–17, of whom 167,215 are 12–17; the 2025 file was released in October 2026), with survey weights, and treat 2016–17 separately because the screen-time item was split into TV and device questions in those two years.

##### Trends 2016–2025

![Chart: nsch_trends](../../figures/nsch_trends.png)

Weighted share of children whose parent reports a current condition, by survey year, with 95% intervals (one child per household; stratification ignored). Solid lines ages 12–17, dotted lines ages 6–11. Grey band = 2020; the NSCH is fielded from June into the following winter, so a survey year straddles two school years.

Parent-reported current anxiety among girls aged 12–17 rose from 11.5% in 2016 to a peak of 21.7% in 2024, and current depression from 6.8% to 12.4% in 2022; boys rose from 8.5% to 12.3% on anxiety with little change on depression. The 2025 survey is the first in the series to fall: girls' anxiety dropped by -4.33 (1.09) pp to 17.3% and depression by -2.32 (0.82) pp to 8.3%, while boys changed by -0.06 (0.87) pp and -0.28 (0.50) pp. Among 6–11-year-olds anxiety rose from 6.5% to 10.1% and was 9.4% in 2025. The parent series therefore matches the self-report surveys in the report on both ends: a female-led rise through the early 2020s and a downturn in the most recent wave, here between the 2024 and 2025 field periods. Two cautions apply to the last point: the 2025 response rate (34.7%) is the lowest in the series and the field period was extended to March 2026, and a single-year drop in a diagnosis-based item can reflect access to care as well as symptoms.

##### The caregiver screen-time gradient

![Chart: nsch_gradient](../../figures/nsch_gradient.png)

Pooled 2018–2025, weighted prevalence by the parent's answer to the weekday screen-time item, with 95% intervals. 37.7% of 12–17-year-olds and 18.4% of 6–11-year-olds are reported at four or more hours.

| Parent-reported outcome                            | Girls 12–17   | Boys 12–17   | Girls 6–11   | Boys 6–11    | Mean 12–17 | Mean 6–11 |
|----------------------------------------------------|---------------|--------------|--------------|--------------|------------|-----------|
| Currently has anxiety problems                     | +14.53 (0.79) | +7.02 (0.77) | +5.49 (0.80) | +4.81 (0.74) | 14.7%      | 8.4%      |
| … moderate or severe                               | +9.49 (0.61)  | +4.46 (0.49) | +3.09 (0.52) | +3.30 (0.57) | 7.9%       | 4.0%      |
| Currently has depression                           | +10.24 (0.61) | +5.51 (0.39) | +2.75 (0.42) | +2.05 (0.52) | 7.8%       | 1.9%      |
| … moderate or severe                               | +6.49 (0.41)  | +2.97 (0.29) | +1.44 (0.27) | +0.95 (0.24) | 4.2%       | 0.8%      |
| Currently has ADD/ADHD (contrast)                  | +3.07 (0.88)  | +7.18 (0.95) | +1.32 (0.84) | +5.58 (0.93) | 13.0%      | 10.8%     |
| Currently has behavior/conduct problems (contrast) | +3.74 (0.50)  | +5.23 (0.82) | +4.91 (0.81) | +8.31 (0.92) | 6.9%       | 9.1%      |

Percentage-point difference between children at 4+ hours and children at 1 hour on most weekdays (the reference category), from weighted linear probability models with single-year age, sex, race/ethnicity, income as a share of the poverty line, highest parental education, and state-by-year fixed effects; heteroskedasticity-robust standard errors in parentheses (one sampled child per household). 2018–2025 pooled.

Unlike the MICS caregivers, U.S. parents report a steep gradient. Girls aged 12–17 whose parents place them at four or more weekday hours are +14.53 (0.79) pp more likely to be reported with current anxiety and +10.24 (0.61) pp more likely with current depression than girls at one hour, against means of 14.7% and 7.8%; for boys the differences are +7.02 (0.77) and +5.51 (0.39) pp. The covariates and state-by-year effects remove little of the raw gap (+15.26 (0.80) pp for girls' anxiety with year effects only). The gradient is roughly linear from one hour upward and is absent or reversed below one hour, as in the published NSCH analyses. For scale, the self-reported GSHS gradient for girls using a mobile phone three or more hours a day was +8.19 (1.41) pp on loneliness and +10.09 (1.49) pp on suicidal ideation, while the MICS caregiver reports gave -0.12 (1.44) pp (daily internet use) and -2.24 (1.24) pp (daily phone use) on girls' anxiety within sampling clusters. U.S. caregivers, asked about diagnosed and current conditions rather than how often the child seems anxious, report a gradient at least as steep as the adolescents' own reports in GSHS. Three features argue against reading the U.S. gradient as a phone effect on its own. It is present at ages 6–11 (+5.49 (0.80) pp for girls' anxiety), where phone ownership is uncommon and the item mostly captures television and games. It is as large or larger for the contrast outcomes that no phone account predicts: current ADD/ADHD is +7.18 (0.95) pp higher for boys and behavior or conduct problems +8.31 (0.92) pp higher for 6–11-year-old boys at 4+ hours, a pattern consistent with children who already have a condition spending more time on screens, or with parents who worry about a child also counting their hours more. And it barely changed across the periods when adolescent screen time jumped and then receded:

| Outcome, ages 12–17 (girls / boys)      | 2018–19                     | 2022–25                     | 2018–25                     | 2016–17, two items summed   |
|-----------------------------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|
| Current anxiety, pp per weekday hour    | +3.38 (0.44) / +1.85 (0.33) | +4.38 (0.28) / +2.19 (0.23) | +3.96 (0.21) / +2.09 (0.17) | +1.34 (0.25) / +0.72 (0.18) |
| Current depression, pp per weekday hour | +2.26 (0.38) / +1.78 (0.27) | +2.79 (0.25) / +1.20 (0.18) | +2.68 (0.18) / +1.43 (0.13) | +1.14 (0.17) / +0.56 (0.14) |
| Current ADD/ADHD, pp per weekday hour   | +0.95 (0.30) / +2.16 (0.42) | +1.38 (0.21) / +1.97 (0.29) | +1.20 (0.16) / +1.95 (0.21) | +0.81 (0.25) / +0.56 (0.24) |

Linear slope in percentage points per reported weekday hour (categories coded 0.5, 1, 2, 3 and 4.5 hours), same specification as above. The 2016–17 column sums the separate TV and device items of those years (0 to 9 hours), so its scale is not identical.

##### Sleep and bullying as pathways
