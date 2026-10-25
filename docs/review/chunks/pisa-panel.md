<!-- Generated review chunk: pisa-panel -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-pisa-panel)

Context: Teen Distress Pilot → Part 4 · The interaction (H3): phones in the same hours as high-pressure school → PISA 2012–2022: school loneliness, life satisfaction and digital use across waves

Editable source entry points: [scripts/report/90_build_report.py:1](../../../scripts/report/90_build_report.py#L1)

---

### PISA 2012–2022: school loneliness, life satisfaction and digital use across waves

PISA has asked 15-year-olds the same six sense-of-belonging statements since 2000 ("I feel lonely at school", "I feel like I belong at school", ...), a 0–10 life-satisfaction question since 2015, and, in the systems that chose the ICT familiarity module, how long they spend on the Internet on a typical weekday at school and outside school (2012, 2015 and 2018; identical seven categories from "no time" to "more than 6 hours"). PISA 2022 replaced the Internet items with hours per day on digital resources for learning and for leisure, at school and before/after school, which we sum to total device hours and flag wherever 2022 enters a digital-use comparison. Stacking the four public-use files gives 2,225,175 students: 480,174 in 65 systems in 2012 (43 with the ICT module), 519,334 in 73 in 2015 (46), 612,002 in 80 in 2018 (53) and 613,665 in 80 in 2022. Life satisfaction is available for 50, 72 and 73 systems in 2015, 2018 and 2022. In 2012 the belonging block sat in two of the three rotated questionnaire forms, so about a third of students have no belonging items by design; all estimates use the final student weights. The 2015 wave also carries the five-item test-anxiety scale (ANXTEST: "I often worry that it will be difficult for me to take a test", "I worry that I will get poor grades at school", "Even if I am well prepared for a test I feel very anxious", "I get very tense when I study", "I get nervous when I don't know how to solve a task at school"), which is the direct schoolwork-anxiety measure that the Phase 1 H3 test had to proxy with mathematics anxiety in 2022.

#### Trends

![Chart: pisa_panel_trends](../../figures/pisa_panel_trends.png)

Unweighted means of weighted country means, restricted to systems that asked the item in every wave shown (balanced sets). Solid lines are OECD members, dotted lines partner systems. Life satisfaction was first asked in 2015. The grey band marks 2020.

Among OECD systems, the share of girls who agree they feel lonely at school moved from 8.6% in 2012 to 15.5% in 2015, 16.2% in 2018 and 18.4% in 2022; for boys the path is 9.3% → 14.1% → 14.9% → 14.1%. Partner systems started higher (13.2% of girls, 18.0% of boys in 2012) and reached 18.4% and 19.3% in 2022. Agreement with "I feel like I belong at school" fell from 82.7% to 73.8% among girls and from 81.0% to 76.5% among boys across all systems in the balanced set. Mean life satisfaction among OECD girls went from 7.01 in 2015 to 6.74 in 2018 and 6.27 in 2022, against 7.58, 7.36 and 7.21 for boys, so the sex gap in life satisfaction widened from 0.57 to 0.94 points. Over the same years weekday Internet time in the ICT-module systems rose from 2.37 hours outside school and 0.65 hours at school in 2012 to 3.62 and 1.59 hours in 2018; the share above 4 hours outside school went from 19% to 40% and the share above 1 hour at school from 17% to 40%. The largest single step in loneliness is 2012 → 2015, the wave in which most systems moved from paper to computer-delivered questionnaires and the belonging block left the rotated design; the 2015 → 2022 changes are smaller and, for OECD boys, flat.

#### Within-country panel: did well-being fall more where digital hours rose more?

The country-sex-wave means are regressed on the mean in-school and out-of-school weekday hours with country and wave fixed effects, so that the estimates use only within-country changes net of the common wave trend; the mean ESCS of the cell is controlled and standard errors are clustered by country. The 2012–2018 rows use the identical Internet-hours item; the 2012–2022 rows add the 2022 total device hours.

| Outcome (country means)    | Waves     | Girls: in-school h | Girls: out-of-school h | Boys: in-school h | Boys: out-of-school h | Cells / systems |
|----------------------------|-----------|--------------------|------------------------|-------------------|-----------------------|-----------------|
| Lonely at school (pp)      | 2012-2018 | +1.40 (1.02)       | -0.81 (1.16)           | +0.95 (1.37)      | -0.08 (1.55)          | 118 / 43        |
| Lonely at school (pp)      | 2012-2022 | +0.33 (0.63)       | -0.22 (0.58)           | -0.18 (0.72)      | -0.52 (0.51)          | 184 / 56        |
| Belongs at school (pp)     | 2012-2018 | -2.03 (1.30)       | **-2.33 (0.92)**       | -0.70 (1.81)      | **-2.62 (1.23)**      | 118 / 43        |
| Belongs at school (pp)     | 2012-2022 | -0.71 (1.39)       | -1.38 (0.84)           | -0.17 (1.29)      | -1.00 (0.89)          | 184 / 56        |
| Life satisfaction (points) | 2012-2018 | +0.008 (0.169)     | +0.097 (0.149)         | -0.044 (0.214)    | +0.052 (0.212)        | 66 / 33         |
| Life satisfaction (points) | 2012-2022 | +0.113 (0.097)     | +0.053 (0.068)         | +0.158 (0.100)    | -0.032 (0.087)        | 126 / 48        |
| Life satisfaction 0-4 (pp) | 2012-2018 | -1.40 (1.78)       | -0.35 (1.53)           | -0.78 (2.08)      | -2.74 (1.95)          | 66 / 33         |
| Life satisfaction 0-4 (pp) | 2012-2022 | -1.24 (1.04)       | -0.15 (0.68)           | **-1.99 (0.90)**  | +0.87 (0.78)          | 126 / 48        |

Coefficient per additional hour per weekday (SE); bold when \|t\| \> 1.96. Cells are country × sex × wave means for ICT-module systems observed in at least two waves. Life satisfaction rows start in 2015.

With country and wave effects removed, changes in out-of-school hours do not track changes in loneliness (-0.81 (1.16) pp per hour for girls and -0.08 (1.55) for boys over 2012–2018) or in life satisfaction (+0.097 (0.149) and +0.052 (0.212) points per hour), but they do track the fall in school belonging: agreement that one belongs at school moves by -2.33 (0.92) pp per additional out-of-school hour among girls and -2.62 (1.23) among boys, an association that weakens to -1.38 (0.84) and -1.00 (0.89) once the 2022 total-device item is added. In-school hours add nothing beyond that. The long differences show the same pattern. Between 2012 and 2018 the loneliness share rose by +6.9 pp among girls and +5.6 pp among boys in the 34 systems with the ICT module in both waves, while out-of-school hours rose by +1.41 hours; the cross-country slope of the loneliness change on the hours change is -1.00 (1.49) pp per hour for girls (r = -0.14) and -0.78 (1.66) for boys (r = -0.09), whereas belonging changed by -10.2 pp among girls and -9.7 pp among boys with slopes of -2.07 (1.09) (r = -0.27) and -2.86 (0.98) (r = -0.32) pp per hour. The 2015 → 2018 fall in life satisfaction (-0.33 points for girls, -0.21 for boys) is unrelated to the hours change (+0.09 (0.11) and +0.09 (0.21) points per hour).
