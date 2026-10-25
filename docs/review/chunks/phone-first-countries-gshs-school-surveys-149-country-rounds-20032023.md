<!-- Generated review chunk: phone-first-countries-gshs-school-surveys-149-country-rounds-20032023 -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-phone-first-countries-gshs-school-surveys-149-country-rounds-20032023)

Context: Teen Distress Pilot → Part 2 · Phones and social media (H1) → Phone-first countries: GSHS school surveys (149 country-rounds, 2003–2023)

Editable source entry points: [scripts/report/90_build_report.py:238](../../../scripts/report/90_build_report.py#L238)

---

### Phone-first countries: GSHS school surveys (149 country-rounds, 2003–2023)

The WHO Global School-based Student Health Survey (GSHS) asks school-attending adolescents (primarily ages 13–17) in over 100 low- and middle-income countries identical questions on loneliness, anxiety-related sleep loss, and suicidality in waves starting in 2003. From the 165 public-use country-round files in the WHO microdata repository, 149 rounds contained usable mental-health items and survey weights after harmonization, including 91 rounds across 39 countries surveyed at least twice. We first test whether within-country changes in adolescent distress track national internet penetration from the World Bank (controlling for log GDP per capita), and then examine student-level phone hours and ITU mobile-network coverage below.

![Chart: gshs](../../figures/gshs.png)

Each point plots a country's change from its first to its last GSHS wave (weighted prevalence) against the change in the national internet-user share over the same interval.

| Outcome          | Sex   | Sample                   | Effect of +10 pp internet users (SE) |
|------------------|-------|--------------------------|--------------------------------------|
| lonely           | girls | 79 rounds / 34 countries | +1.04 (0.83)                         |
| lonely           | boys  | 79 rounds / 34 countries | -0.18 (0.59)                         |
| worried sleep    | girls | 77 rounds / 33 countries | +0.14 (0.87)                         |
| worried sleep    | boys  | 77 rounds / 33 countries | -0.78 (0.54)                         |
| suicide consider | girls | 67 rounds / 30 countries | +0.02 (1.27)                         |
| suicide consider | boys  | 67 rounds / 30 countries | -0.42 (0.99)                         |
| suicide plan     | girls | 70 rounds / 31 countries | +0.86 (0.74)                         |
| suicide plan     | boys  | 70 rounds / 31 countries | -0.35 (0.69)                         |
| suicide attempt  | girls | 35 rounds / 19 countries | +0.30 (0.90)                         |
| suicide attempt  | boys  | 35 rounds / 19 countries | -0.50 (0.38)                         |
| no close friends | girls | 79 rounds / 34 countries | +0.48 (0.33)                         |
| no close friends | boys  | 79 rounds / 34 countries | -0.16 (0.36)                         |

Country and year fixed effects, log GDP per capita control, inverse-variance weights, and standard errors clustered by country.

**Assessment.** Across the full 34-country panel, within-country growth in national internet penetration shows no statistically significant relationship with adolescent distress: for girls, a 10-percentage-point increase in internet users is associated with +1.04 pp in loneliness (SE 0.83) and +0.02 pp in suicidal ideation (SE 1.27), while the point estimates for boys are slightly negative. (An earlier partial extract of 72 rounds had suggested a +2.5 pp effect for girls on both outcomes, which disappeared once the remaining 77 rounds were added—a useful illustration of how sensitive country-round panels are to sample coverage.) National internet penetration is also a coarse proxy that pools adult and youth access. The two subsections below turn to the 2022–23 GSHS waves that ask students directly about daily mobile-phone hours and to the ITU mobile-broadband coverage series.

##### Asking adolescents directly: mobile-phone hours in the 2022–23 rounds

Five recent GSHS rounds (Ghana 2022, India 2022, Jamaica 2023, Morocco 2023, and Wallis and Futuna 2023) added a question on "hours per day you used a mobile phone in the past 7 days," pairing each student's self-reported phone time with the same student's loneliness and suicidality responses.

![Chart: gshs_hours](../../figures/gshs_hours.png)

Regressions include country fixed effects and age controls, survey weights, and standard errors clustered by school across 7,708 girls and 7,102 boys (including students without a phone). Compared with students using a phone under three hours a day or not at all, girls at three or more hours report loneliness +8.2 pp (SE 1.4), suicidal ideation +10.1 pp (SE 1.5), and suicide attempts +5.6 pp (SE 1.6); the corresponding differences for boys are +5.3, +3.6, and +1.9 pp. Distress rises steadily across higher-use categories: relative to under one hour per day, girls reporting more than eight hours per day have +19.5 pp higher loneliness, +17.4 pp higher suicidal ideation, and +13.7 pp higher suicide attempts. Students without a mobile phone sit a few percentage points above the under-one-hour group rather than below it.

This individual-level dose-response gradient matches the pattern documented in Western surveys: substantial in magnitude, roughly twice as steep for girls as for boys, and increasing monotonically with daily hours above one hour. Because it is a cross-sectional self-report association, however, it cannot distinguish the effect of phone use on distress from reverse causation or shared underlying vulnerabilities. What it does show is that the 2022–23 GSHS rounds (alongside incoming MICS7 adolescent modules) are strong candidates for linking to subnational mobile-coverage rollout maps, since exposure is measured directly on the adolescent rather than inferred from national or adult averages.

##### Network coverage at country level (ITU)

Replacing World Bank internet penetration with the ITU mobile-network series allows us to test country-level 3G and 4G population coverage and active mobile-broadband subscriptions using the same two-way fixed-effects specification (country and year fixed effects, inverse-variance weights, and country-clustered standard errors across countries with two or more GSHS rounds).

| Exposure (per +10 points)           | Countries / rounds (loneliness) | Lonely, girls | Lonely, boys | Considered suicide, girls | …boys        | Attempted, girls | …boys        |
|-------------------------------------|---------------------------------|---------------|--------------|---------------------------|--------------|------------------|--------------|
| Mobile-broadband subs per 100 (ITU) | 22 / 47                         | +0.21 (0.54)  | +0.03 (0.42) | +0.28 (0.43)              | +0.35 (0.48) | +0.31 (0.44)     | +0.30 (0.50) |
| 3G population coverage (ITU)        | 17 / 36                         | -0.72 (0.28)  | +0.25 (0.26) | +0.10 (0.59)              | +0.28 (0.44) | -0.08 (0.32)     | +0.36 (0.36) |
| 4G population coverage (ITU)        | 15 / 32                         | -0.40 (0.41)  | -0.48 (0.38) | -0.51 (0.63)              | -0.20 (0.59) | -0.64 (0.43)     | -0.45 (0.69) |
| Internet users % (ITU)              | 33 / 78                         | +0.93 (0.86)  | -0.19 (0.60) | -0.04 (1.20)              | -0.54 (1.07) | +0.37 (1.02)     | -0.22 (0.86) |

Sample counts in the second column refer to the loneliness item; suicidal ideation and suicide attempts are available in 1 to 3 fewer countries per row.

None of the country-level ITU series supports H1. Across the 15 countries with repeated 4G data, a 10-percentage-point increase in 4G coverage has slightly negative point estimates across all outcomes (from −0.20 to −0.64 pp, with standard errors of 0.38–0.69). For 3G coverage (17 countries), the coefficient on girls' loneliness is negative (−0.72 pp, SE 0.28) and the suicidality estimates are near zero; for active mobile-broadband subscriptions (22 countries), estimates range from +0.03 to +0.35 pp with standard errors around 0.4–0.5 pp. Because national coverage series move with broader economic development and pool urban and rural areas together, local cluster-level coverage remains the necessary test.
