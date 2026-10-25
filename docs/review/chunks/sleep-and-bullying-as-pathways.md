<!-- Generated review chunk: sleep-and-bullying-as-pathways -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-sleep-and-bullying-as-pathways)

Context: Teen Distress Pilot → Part 2 · Phones and social media (H1) → Who reports the symptoms: U.S. caregivers and adolescents (NSCH 2016–2025, NHIS 2021–2024) → Parent-reported anxiety and depression in the United States: NSCH 2016–2025 → Sleep and bullying as pathways

Editable source entry points: [scripts/report/90_build_report.py:1](../../../scripts/report/90_build_report.py#L1)

---

| 4+ h vs 1 h, ages 12–17 | Girls: base   | Girls: + sleep, bullying | Girls: attenuation | Boys: base   | Boys: + sleep, bullying | Boys: attenuation |
|-------------------------|---------------|--------------------------|--------------------|--------------|-------------------------|-------------------|
| Current anxiety         | +14.61 (0.79) | +11.38 (0.76)            | 22%                | +7.06 (0.77) | +5.07 (0.76)            | 28%               |
| Current depression      | +10.05 (0.61) | +7.57 (0.59)             | 25%                | +5.30 (0.39) | +3.94 (0.40)            | 26%               |
| Current ADD/ADHD        | +3.29 (0.88)  | +1.60 (0.87)             | 51%                | +6.89 (0.97) | +4.88 (0.96)            | 29%               |

The 4+ hour coefficient on anxiety and depression (ages 12–17, 2018–2025) before and after adding weeknight sleep below 8 hours and bullying victimization (monthly or more, weekly or more) as controls; attenuation is the share of the base coefficient removed.

Parents who report heavy screen use also report less sleep and more bullying: four or more weekday hours is associated with +10.62 (1.24) pp more girls and +9.16 (1.17) pp more boys sleeping under eight hours, and with +8.60 (0.73) pp (girls) and +5.41 (0.72) pp (boys) more being bullied at least monthly. Both predict current anxiety strongly in the same models (short sleep +5.31 (0.71) pp, monthly bullying +25.18 (1.48) pp for girls), but adding them removes only 22% of the girls' 4+ hour anxiety gradient (+14.61 (0.79) to +11.38 (0.76)) and 25% of the depression gradient. Most of the cross-sectional association runs through neither sleep nor bullying as the NSCH measures them; the Leung and Torres (2021) finding below that sleep does not mediate the 2018 gradient holds in the pooled years.

##### State smartphone adoption

| Outcome            | Girls 12–17  | Boys 12–17   | Girls 6–11   | Boys 6–11    | State-years |
|--------------------|--------------|--------------|--------------|--------------|-------------|
| Current anxiety    | +0.34 (0.72) | -0.57 (0.72) | +0.18 (0.56) | -0.26 (0.51) | 357         |
| Current depression | -0.62 (0.53) | +0.06 (0.43) | -0.17 (0.27) | -0.16 (0.26) | 357         |
| Current ADD/ADHD   | +0.03 (0.64) | -0.16 (0.66) | -0.41 (0.51) | +0.20 (0.88) | 357         |

Percentage points of the parent-reported outcome per 10-point rise in the NTIA share of persons in teen households who use a smartphone for internet access (CPS supplements, November 2017, 2019, 2021 and 2023, interpolated between waves), on state-by-year cells 2017–2023 with state and year fixed effects, weighted by cell size, standard errors clustered by state (51 jurisdictions).

By the time the NSCH begins, teen-household smartphone use had already reached 57% nationally with a cross-state standard deviation of 5.9 points, and it moved to 63% (SD 5.6) by 2023. The within-state changes left are small and noisy, and the coefficients are correspondingly unstable: +0.34 (0.72) pp per 10 points for girls' anxiety and -0.62 (0.53) pp for depression at ages 12–17, with similar-sized estimates at ages 6–11. This is the saturation problem anticipated in the adoption section: after 2017 the NTIA series has no adoption transition left to exploit, so the NSCH cannot repeat the 2011–2019 YRBS test and these rows should be read as a null-variation result rather than a null effect.

##### The first statewide school phone bans: a first look

![Chart: nsch_bans](../../figures/nsch_bans.png)

Left: weighted share of 12–17-year-olds with parent-reported current anxiety in Florida (HB 379, instructional-time ban from the 2023–24 school year; shaded) and in all other states, with 95% intervals for Florida. Right: event-study coefficients from the individual-level model (ages 12–17, covariates, state and year fixed effects, standard errors clustered by state), relative to the year before each mandate's first school year; treated states are Florida (2023–24), Indiana, Louisiana and South Carolina (2024–25) and the 19 states whose mandates took effect in 2025–26 and are observed only at event time 0.

| Outcome                     | Girls 12–17: in force, full year | Girls: took effect during field period | Girls: Florida only, full years (placebo SD) | Boys 12–17: in force, full year | Boys: took effect during field period | Boys: Florida only, full years (placebo SD) | Ages 6–11: in force, full year |
|-----------------------------|----------------------------------|----------------------------------------|----------------------------------------------|---------------------------------|---------------------------------------|---------------------------------------------|--------------------------------|
| Current anxiety             | -5.57 (2.29)                     | -4.11 (1.29)                           | -6.25 (2.79)                                 | -3.05 (1.04)                    | +0.12 (0.67)                          | -2.09 (1.84)                                | +2.40 (1.58)                   |
| Current depression          | -0.97 (0.66)                     | -2.48 (0.67)                           | -0.87 (3.01)                                 | -0.42 (0.62)                    | -0.10 (0.44)                          | -0.88 (2.18)                                | -0.09 (0.20)                   |
| Current ADD/ADHD (contrast) | -4.19 (1.19)                     | -2.24 (0.87)                           | -4.06 (1.93)                                 | +0.18 (1.88)                    | +2.01 (1.05)                          | +1.72 (3.62)                                | +2.38 (1.88)                   |

Difference-in-differences coefficients (pp) from weighted individual-level models with covariates, state and year fixed effects, and state-clustered standard errors. "In force, full year" = survey years after the mandate's first school year; "took effect during field period" = the survey year whose June–winter field period straddles the mandate's start. States that only require districts to adopt a policy (Minnesota 2024–25; Alaska, Arizona, Idaho and New Mexico 2025–26) carry a separate indicator. The Florida-only columns come from the state-year panel with the other mandate states dropped once treated; because one treated state leaves no valid cluster-robust standard error, the figure in parentheses is the standard deviation of the same coefficient across the 16 states without any mandate when each is treated alone from 2023–24. Ages 6–11 are also covered by the bans but rarely carry phones.

| Years relative to the mandate's first school year      | Girls 12–17, anxiety | Boys 12–17, anxiety | Girls 12–17, depression | Boys 12–17, depression |
|--------------------------------------------------------|----------------------|---------------------|-------------------------|------------------------|
| ≤ −4 (placebo)                                         | +0.44 (0.88)         | -1.66 (0.93)        | -1.53 (1.03)            | -0.53 (0.61)           |
| −3 (placebo)                                           | +0.08 (1.05)         | -0.01 (1.19)        | -1.03 (0.79)            | +0.53 (0.69)           |
| −2 (placebo)                                           | -1.45 (1.30)         | -0.55 (0.73)        | -2.30 (1.19)            | +0.59 (0.71)           |
| 0: first school year, field period straddles the start | -4.43 (1.61)         | -0.48 (0.97)        | -3.55 (0.99)            | -0.06 (0.59)           |
| +1: in force for a full school year                    | -5.69 (2.99)         | -2.17 (2.04)        | -1.52 (0.89)            | +0.33 (1.07)           |
| +2 (Florida only)                                      | -6.59 (1.30)         | -5.54 (0.77)        | -2.57 (0.86)            | -1.43 (0.60)           |

Event-study coefficients (pp) with the year before the first school year as the reference; "≤ −4" pools all earlier years. The "0" row is identified by 23 states, "+1" by Florida, Indiana, Louisiana and South Carolina, and "+2" by Florida alone.

Florida's parent-reported anxiety among 12–17-year-old girls was 22.6% in 2022 and 13.5% in 2023 against 20.0% and 20.5% elsewhere, then 13.8% and 12.0% in the two full post-ban years against 22.2% and 17.6% in other states. The Florida series rests on roughly 100–190 girls a year, so its year-to-year swings of five to ten points are mostly noise. In the pooled, population-weighted individual model a mandate in force for a full school year is associated with -5.57 (2.29) pp on girls' current anxiety and -0.97 (0.66) pp on depression, and with -3.05 (1.04) and -0.42 (0.62) pp for boys; with each treated state counted once (the state-year panel) the girls' anxiety estimate shrinks to -1.58 (2.12) pp while the boys' is -3.96 (1.28) pp, so the answer depends on whether Florida, Texas and New York are weighted by population. The placebo leads are small (-1.45 (1.30) and +0.08 (1.05) pp for girls at −2 and −3), and the 6–11 comparison group moves the other way (+2.40 (1.58) pp).

| Mandate in force, full year      | Equal state weights: coef (cluster SE) | Permutation SD | Permutation p | Population weights: coef (cluster SE) | Permutation SD | Permutation p |
|----------------------------------|----------------------------------------|----------------|---------------|---------------------------------------|----------------|---------------|
| Anxiety, girls 12–17             | -1.58 (2.12)                           | 2.07           | 0.45          | -5.18 (2.23)                          | 2.72           | 0.05          |
| Anxiety, boys 12–17              | -3.96 (1.28)                           | 1.44           | 0.00          | -2.73 (1.04)                          | 1.96           | 0.17          |
| Depression, girls 12–17          | +0.04 (0.87)                           | 1.82           | 0.98          | -0.91 (0.70)                          | 1.81           | 0.60          |
| Depression, boys 12–17           | -1.40 (1.01)                           | 1.33           | 0.31          | -0.58 (0.60)                          | 1.20           | 0.57          |
| ADD/ADHD (contrast), girls 12–17 | -3.83 (2.47)                           | 1.75           | 0.03          | -4.03 (1.20)                          | 1.86           | 0.04          |
| ADD/ADHD (contrast), boys 12–17  | -2.75 (2.26)                           | 2.02           | 0.17          | +0.28 (1.80)                          | 2.43           | 0.92          |
| Anxiety, ages 6–11 (comparison)  | +0.49 (1.54)                           | 1.19           | 0.72          | +2.35 (1.52)                          | 1.76           | 0.20          |
