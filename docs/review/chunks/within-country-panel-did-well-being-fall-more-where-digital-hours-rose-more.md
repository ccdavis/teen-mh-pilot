<!-- Generated review chunk: within-country-panel-did-well-being-fall-more-where-digital-hours-rose-more -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-within-country-panel-did-well-being-fall-more-where-digital-hours-rose-more)

Context: Teen Distress Pilot → Part 4 · The interaction (H3): phones in the same hours as high-pressure school → PISA 2012–2022: school loneliness, life satisfaction and digital use across waves → Within-country panel: did well-being fall more where digital hours rose more?

Editable source entry points: [scripts/report/90_build_report.py:1](../../../scripts/report/90_build_report.py#L1)

---

| Change                                                | Period      | Sex   | Mean Δ outcome | Mean Δ out-of-school h | Slope on Δ in-school h (SE) | Slope on Δ out-of-school h (SE) | Systems |
|-------------------------------------------------------|-------------|-------|----------------|------------------------|-----------------------------|---------------------------------|---------|
| Δ lonely at school (pp)                               | 2012 → 2018 | girls | +6.91          | +1.41 h                | +1.73 (1.10) (r = 0.27)     | -1.00 (1.49) (r = -0.14)        | 34      |
| Δ lonely at school (pp)                               | 2012 → 2018 | boys  | +5.58          | +1.15 h                | +0.99 (1.45) (r = 0.12)     | -0.78 (1.66) (r = -0.09)        | 34      |
| Δ belongs at school (pp)                              | 2012 → 2018 | girls | -10.17         | +1.41 h                | -2.64 (1.60) (r = -0.38)    | -2.07 (1.09) (r = -0.27)        | 34      |
| Δ belongs at school (pp)                              | 2012 → 2018 | boys  | -9.74          | +1.15 h                | -0.98 (2.16) (r = -0.12)    | -2.86 (0.98) (r = -0.32)        | 34      |
| Δ life satisfaction (points)                          | 2015 → 2018 | girls | -0.33          | +0.51 h                | +0.06 (0.15) (r = 0.07)     | +0.09 (0.11) (r = 0.12)         | 33      |
| Δ life satisfaction (points)                          | 2015 → 2018 | boys  | -0.21          | +0.48 h                | +0.01 (0.19) (r = 0.01)     | +0.09 (0.21) (r = 0.07)         | 33      |
| Δ life satisfaction (points), 2022 total device hours | 2018 → 2022 | girls | -0.45          | +0.52 h                | +0.19 (0.10) (r = 0.29)     | +0.05 (0.06) (r = 0.11)         | 42      |
| Δ life satisfaction (points), 2022 total device hours | 2018 → 2022 | boys  | -0.13          | +0.46 h                | +0.11 (0.08) (r = 0.20)     | -0.01 (0.07) (r = -0.02)        | 42      |

Long differences in weighted country means; slopes from OLS across systems with heteroskedasticity-robust SEs.

#### PISA 2015: test anxiety × in-school versus out-of-school Internet use (H3)

H3 predicts that the harmful association of digital use is concentrated among students under academic pressure and for use inside the school day. PISA 2015 is the one wave with a direct schoolwork-anxiety scale and the weekday hours split by location, in 45 ICT-module systems (302,326 students with anxiety, hours, ESCS and grade). Students above their country's median test anxiety are not heavier in-school users: 24.0% of them exceed 1 hour at school against 23.7% of lower-anxiety students, and 30.0% versus 28.9% exceed 4 hours outside school. The regressions below interact standardised ANXTEST with both use indicators, with country fixed effects, ESCS and grade, student weights and school-clustered SEs.

![Chart: pisa_panel_h3](../../figures/pisa_panel_h3.png)

Interaction coefficients (per SD of test anxiety) with 95% confidence intervals; the life-satisfaction coefficient is multiplied by 10 for display. A positive value for loneliness or low life satisfaction, or a negative value for belonging or life satisfaction, means the use indicator is more harmful for anxious students.

| Outcome                    | Sex   | Mean | Test anxiety (per SD) | In-school \>1 h    | Out-of-school \>4 h | Anxiety × in-school | Anxiety × out-of-school | n       |
|----------------------------|-------|------|-----------------------|--------------------|---------------------|---------------------|-------------------------|---------|
| Lonely at school (pp)      | girls | 15.6 | **+4.05 (0.27)**      | **+1.29 (0.45)**   | **+1.57 (0.42)**    | **-1.00 (0.49)**    | **-1.42 (0.43)**        | 153,205 |
| Lonely at school (pp)      | boys  | 16.8 | **+1.84 (0.26)**      | **+2.15 (0.46)**   | +0.29 (0.45)        | +0.39 (0.49)        | -0.70 (0.43)            | 149,121 |
| Belongs at school (pp)     | girls | 75.3 | **-2.98 (0.29)**      | **-1.77 (0.52)**   | **-2.58 (0.47)**    | **+1.23 (0.49)**    | +0.76 (0.48)            | 152,842 |
| Belongs at school (pp)     | boys  | 72.5 | **-1.40 (0.30)**      | **-1.23 (0.52)**   | **-1.93 (0.49)**    | -0.16 (0.52)        | **+1.26 (0.48)**        | 148,821 |
| Life satisfaction (points) | girls | 7.3  | **-0.351 (0.017)**    | +0.030 (0.028)     | **-0.340 (0.027)**  | +0.047 (0.031)      | **+0.091 (0.029)**      | 134,352 |
| Life satisfaction (points) | boys  | 7.5  | **-0.243 (0.017)**    | **+0.082 (0.028)** | **-0.123 (0.025)**  | +0.016 (0.032)      | **+0.099 (0.029)**      | 130,607 |
| Life satisfaction 0-4 (pp) | girls | 12.5 | **+3.75 (0.24)**      | +0.24 (0.38)       | **+3.71 (0.37)**    | **-1.04 (0.42)**    | -0.57 (0.40)            | 134,352 |
| Life satisfaction 0-4 (pp) | boys  | 10.3 | **+1.81 (0.25)**      | +0.29 (0.37)       | **+1.67 (0.34)**    | +0.40 (0.42)        | **-1.20 (0.38)**        | 130,607 |

Main effects are evaluated at mean anxiety; the interaction is the change in the use coefficient per SD of ANXTEST. Binary outcomes in percentage points, life satisfaction in points on the 0–10 scale.

Test anxiety itself is strongly associated with worse outcomes: one SD raises girls' loneliness by 4.0 pp (boys 1.8) and lowers life satisfaction by 0.35 points (boys 0.24). In-school Internet use above 1 hour is itself linked to more loneliness (+1.29 (0.45) pp for girls, +2.15 (0.46) for boys) whereas heavy out-of-school use mainly lowers life satisfaction (-0.34 (0.03) points for girls, -0.12 (0.03) for boys). The interactions are the H3 test proper: for loneliness the anxiety × in-school term is -1.00 (0.49) pp for girls and +0.39 (0.49) for boys, against anxiety × out-of-school terms of -1.42 (0.43) and -0.70 (0.43); for life satisfaction the in-school interactions are +0.047 (0.031) and +0.016 (0.032) points, the out-of-school interactions +0.091 (0.029) and +0.099 (0.029). Every interaction that is distinguishable from zero has the sign opposite to H3's prediction: among more anxious students heavy use is less, not more, strongly associated with loneliness and low life satisfaction, and in-school use is not singled out. The above-median anxiety split and the continuous-hours version (results/tables/pisa_panel_h3_2015.csv) give the same picture.

#### Dose–response by wave
