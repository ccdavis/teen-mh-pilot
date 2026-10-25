<!-- Generated review chunk: what-the-phone-ban-evidence-says-about-this -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-what-the-phone-ban-evidence-says-about-this)

Context: Teen Distress Pilot → Part 4 · The interaction (H3): phones in the same hours as high-pressure school → What the phone-ban evidence says about this

Editable source entry points: [scripts/report/90_build_report.py:440](../../../scripts/report/90_build_report.py#L440)

---

### What the phone-ban evidence says about this

PISA 2022 allows an initial test of whether school phone bans matter more for academically anxious students. Because PISA 2022 did not include general schoolwork-anxiety items, we use the PISA mathematics-anxiety index (asked of all students) as a proxy for academic pressure, splitting students at their country's median. We estimate the same within-country regression as above, interacting the school ban indicator with high mathematics anxiety separately by sex.

| Outcome                 | Sex   | Ban, low-anxiety students (SE) | Ban, high-anxiety students | Difference (SE) | High vs low anxiety, no ban |
|-------------------------|-------|--------------------------------|----------------------------|-----------------|-----------------------------|
| Lonely at school        | girls | -0.27 (0.68)                   | -1.15                      | -0.88 (0.93)    | +8.2                        |
| Lonely at school        | boys  | +1.12 (0.53)                   | -0.81                      | -1.94 (0.98)    | +7.4                        |
| Nervous without device  | girls | -0.75 (0.60)                   | -0.49                      | +0.26 (0.78)    | +9.3                        |
| Nervous without device  | boys  | +0.13 (0.53)                   | +0.19                      | +0.06 (0.81)    | +5.8                        |
| Belonging index         | girls | +2.34 (1.60)                   | +2.46                      | +0.11 (1.90)    | -22.7                       |
| Belonging index         | boys  | +0.32 (1.43)                   | +1.91                      | +1.59 (2.11)    | -19.2                       |
| Life satisfaction index | girls | +3.09 (3.41)                   | +2.23                      | -0.86 (4.53)    | -25.3                       |
| Life satisfaction index | boys  | +2.54 (3.26)                   | +0.71                      | -1.82 (4.93)    | -25.2                       |

Binary items in percentage points and scale indices in hundredths of an SD; regressions include country fixed effects, socio-economic status, private/public school type, and grade controls, student weights, and school-clustered standard errors across 441,992 students with non-missing mathematics anxiety.

Students with above-median mathematics anxiety are substantially lonelier at school (+8.2 pp among girls and +7.4 pp among boys in non-ban schools), and the association between attending a ban school and lower loneliness is larger for them: −1.15 pp for high-anxiety girls versus −0.27 pp for low-anxiety girls (interaction −0.88 pp, SE 0.93), and −0.81 pp versus +1.12 pp for boys (interaction −1.94 pp, SE 0.98). These interaction estimates point in the direction H3 predicts, though they are noisy and rely on mathematics anxiety as a proxy for broader academic pressure. Notably, school bans reduce daily in-school phone use by virtually the same amount (~13 percentage points) in both anxiety groups, so any difference in well-being would reflect differential sensitivity to removing phones rather than differential compliance. A more direct test of H3 requires pairing school phone policies with a direct measure of schoolwork pressure, which the 2021/22 HBSC microdata can support.
