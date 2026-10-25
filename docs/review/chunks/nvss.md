<!-- Generated review chunk: nvss -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-nvss)

Context: Teen Distress Pilot → Part 3 · School pressure (H2) → School-calendar seasonality of adolescent suicide and the summer-vs-school decomposition of the rise (NVSS, 1999–2024)

Editable source entry points: [scripts/report/90_build_report.py:1](../../../scripts/report/90_build_report.py#L1)

---

### School-calendar seasonality of adolescent suicide and the summer-vs-school decomposition of the rise (NVSS, 1999–2024)

Suicide deaths are the one adolescent-distress series that is counted, not asked, in every month of every year since 1999. The school-pressure (H2) and interaction (H3) hypotheses predict that whatever drove the post-2010 rise operated through the school year, so the increase should be concentrated in September–May; a phone or social-media mechanism that operates year-round (H1) predicts a proportional rise in summer and school months alike. [Hansen and Lang (2011)](https://doi.org/10.1016/j.econedurev.2011.04.012) and [Hansen, Sabia and Schaller (2024)](https://doi.org/10.3368/jhr.1222-12710R2) established the seasonal pattern itself: suicides at ages 12–18 fall every summer while young-adult suicides do not. Whether the *rise* of the 2010s followed the same calendar has not, as far as we can find, been tested; we do so here with the public CDC WONDER monthly tabulations of the National Vital Statistics System (ICD-10 X60–X84, Y87.0, \*U03), ages 12–17 against 18–24 and 25–34, by sex, with July 1 single-year-age populations as denominators and exposure adjusted for the length of each month (31,967 suicides at 12–17, 106,331 at 18–24 and 167,764 at 25–34 over 1999–2024). Data for 1999–2020 come from the 1999–2020 database (bridged-race populations) and 2021–2024 from the 2018–2024 single-race database; the two agree exactly on deaths in the overlap years.

![Chart: nvss_monthly](../../figures/nvss_monthly.png)

Monthly suicide rate per 100,000 person-years at ages 12–17 by sex, 2008–2024; shaded bands are June–August; the orange band marks the March–May 2020 school closures. Monthly counts are ~39 for girls and ~92 for boys in 2015–19, so single months are noisy.

#### The summer drop exists at 12–17 and not at 18–24 or 25–34

Pooling 1999–2019, the 12–17 suicide rate in June–August is 0.81 times the September–May rate (95% CI 0.78–0.83), a 19% summer deficit; it is 0.80 for girls and 0.81 for boys. At 18–24 the ratio is 1.01 (0.99–1.03) and at 25–34 1.07 (1.06–1.09): the young-adult and adult summer rates are, if anything, slightly higher than their school-month rates, as in Hansen and Lang. December, when students are out of school for its last ten days, is lower than the other school months at every age (the familiar holiday dip), but by more at 12–17 (0.80, 0.76–0.84) than at 18–24 (0.92) or 25–34 (0.94). A Poisson regression of monthly counts on summer and December indicators with year fixed effects gives the same picture (table), and the magnitudes match Hansen, Sabia and Schaller's 15.6–22.0% summer deficit from restricted county data. The depth of the trough has not changed: the summer ÷ school ratio at 12–17 was 0.83 in 2008–2010, 0.80 in 2015–2019 and 0.84 in 2021–2024.

| Ages  | Sex   | Deaths 1999–2019 | Rate | Sep–May | Jun–Aug | Summer ÷ school ratio (95% CI) | Dec ÷ other school months | Poisson log-ratio, summer (SE) |
|-------|-------|------------------|------|---------|---------|--------------------------------|---------------------------|--------------------------------|
| 12-17 | Girls | 6,491            | 2.5  | 2.6     | 2.1     | 0.80 (0.75–0.85)               | 0.79 (0.72–0.87)          | **-0.25 (0.03)**               |
| 12-17 | Boys  | 17,623           | 6.5  | 6.8     | 5.5     | 0.81 (0.78–0.84)               | 0.81 (0.76–0.85)          | **-0.24 (0.02)**               |
| 12-17 | Both  | 24,114           | 4.6  | 4.8     | 3.9     | 0.81 (0.78–0.83)               | 0.80 (0.76–0.84)          | **-0.24 (0.02)**               |
| 18-24 | Girls | 13,177           | 4.3  | 4.3     | 4.4     | 1.03 (0.99–1.07)               | 0.88 (0.82–0.94)          | +0.02 (0.02)                   |
| 18-24 | Boys  | 68,147           | 21.2 | 21.2    | 21.3    | 1.01 (0.99–1.02)               | 0.93 (0.90–0.95)          | -0.00 (0.01)                   |
| 18-24 | Both  | 81,324           | 13.0 | 12.9    | 13.1    | 1.01 (0.99–1.03)               | 0.92 (0.89–0.94)          | +0.00 (0.01)                   |
| 25-34 | Girls | 24,209           | 5.6  | 5.5     | 5.9     | 1.09 (1.06–1.12)               | 0.94 (0.89–0.98)          | **+0.08 (0.01)**               |
| 25-34 | Boys  | 101,130          | 22.9 | 22.5    | 24.1    | 1.07 (1.06–1.09)               | 0.93 (0.91–0.96)          | **+0.06 (0.01)**               |
| 25-34 | Both  | 125,339          | 14.3 | 14.1    | 15.1    | 1.07 (1.06–1.09)               | 0.94 (0.92–0.95)          | **+0.06 (0.01)**               |

Pooled 1999–2019 rates per 100,000 person-years. The summer ÷ school ratio is the June–August rate divided by the September–May rate with a Poisson 95% CI; the Poisson column is the log rate ratio of summer months relative to the other school months (September–May excluding December) from a model with year fixed effects and robust (HC1) standard errors.

#### Did the rise follow the school calendar?

We compare 2008–2010, the trough before the increase, with 2015–2019, the plateau at the top of the pre-pandemic rise (the 2005–2009 and 1999–2003 baselines in `nvss_decomposition.csv` give the same answer). For girls aged 12–17 the September–May rate rose from 2.2 to 4.1 per 100,000 (+82%), and the June–August rate from 1.8 to 3.2 (+80%); for boys the changes are +59% in school months and +51% in summer. The test statistic is the ratio of the two period ratios, school-month post ÷ pre over summer post ÷ pre: for girls, boys and both sexes together the school-month and summer increases are statistically indistinguishable (ratios of ratios 1.01, 95% CI 0.83–1.23; 1.05, 95% CI 0.93–1.19; 1.04, 95% CI 0.94–1.16). A rise confined to the school year, with summer flat at its 2008–2010 level, would give a ratio of ratios equal to the school-month ratio itself, 1.65; the upper confidence limit of 1.16 excludes it and allows at most 16% more growth in school months than in summer. Because school months carry 75% of the year's person-time, 80% of the absolute increase in annual deaths per 100,000 at 12–17 accrued in September–May, against the 75% expected if the rise were seasonally neutral. The Poisson model on monthly counts (month fixed effects, period indicator and a period × summer interaction, exposure offset) gives a post × summer log-ratio of -0.01 (0.09) for girls, -0.05 (0.06) for boys and -0.04 (0.05) pooled; a negative-binomial fit returns the same coefficients. The young-adult comparison behaves as a placebo should: at 18–24 the ratio of ratios is 1.02 (0.97–1.08), and the triple-difference coefficient (12–17 vs 18–24, post × summer × teen) is -0.02 (0.06) pooled, +0.05 (0.11) for girls. Other baselines agree: the ratio of ratios is 0.98 (0.90–1.07) from 1999–2003, 1.05 (0.97–1.15) from 2005–2009, and 1.00 (0.90–1.11) for 2008–2010 against 2021–2024.

![Chart: nvss_decomp](../../figures/nvss_decomp.png)

Percent change in the suicide rate from 2008–2010 to 2015–2019 in school months (September–May) and summer (June–August), by age group and sex, with Poisson 95% confidence intervals.
