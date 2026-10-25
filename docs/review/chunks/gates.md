<!-- Generated review chunk: gates -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-gates)

Context: Teen Distress Pilot → Part 1 · The rise, and whether public data can measure it → Does the ACS item measure adolescent distress?

Editable source entry points: [scripts/report/90_build_report.py:98](../../../scripts/report/90_build_report.py#L98)

---

### Does the ACS item measure adolescent distress?

Before using the ACS cognitive-difficulty item as an outcome, we test it against three criteria: whether its national timing matches established adolescent depression and sadness surveys, whether its increase is concentrated among girls, and whether state-level changes in the ACS item move with state-level changes in clinical depression. Because the public NHANES depression screener (PHQ-9) is released only for respondents aged 18 and older (the adolescent file is restricted), NHANES enters as an 18–24 benchmark.

#### National timing

![Chart: val_timing](../../figures/val_timing.png)

All series in percent, with 95% CIs. NSDUH points sit at the midpoint of each two-year period; the 2021+ NSDUH estimates use a new web mode and DSM-5 criteria and are not directly comparable to earlier years. YRBS sad/hopeless was first asked in 1999.

NSDUH past-year major depressive episodes among 12–17-year-olds held steady at roughly 8% from 2005 through 2010–11 and then rose in nearly every two-year wave to 15% by 2018–19. YRBS persistent sadness was flat from 1999 through 2011 before rising through 2019. The ACS cognitive-difficulty series turns upward around 2012 and accelerates after 2019. It inflects at roughly the same time as the mental-health surveys, though its relative increase over the 2010s is much smaller—about +13% overall, compared with +85% in NSDUH.

#### Sex pattern

| Series                         | Sex   | 2009–11 | 2017–19 | Relative change |
|--------------------------------|-------|---------|---------|-----------------|
| ACS cognitive difficulty 12–17 | boys  | 5.3     | 5.8     | +9%             |
| ACS cognitive difficulty 12–17 | girls | 2.9     | 3.4     | +17%            |
| YRBS sad/hopeless              | boys  | 20.3    | 24.1    | +19%            |
| YRBS sad/hopeless              | girls | 34.9    | 43.9    | +26%            |
| YRBS considered suicide        | boys  | 11.5    | 12.6    | +10%            |
| YRBS considered suicide        | girls | 18.3    | 23.1    | +26%            |
| NHANES PHQ-9 ≥10, 18–24        | boys  | 5.3     | 7.7     | +46%            |
| NHANES PHQ-9 ≥10, 18–24        | girls | 9.9     | 12.3    | +24%            |

Across all four sources, the relative increase is larger for girls than for boys. The ACS item passes this check: if the 2010s increase were driven primarily by childhood ADHD or learning-disability diagnoses, boys would dominate the change.

#### Do states move together?

![Chart: val_state](../../figures/val_state.png)

51 jurisdictions (50 states plus DC). Each point plots a state's change in both measures between 2008–10 and 2017–19; the dashed line is the OLS fit (slope 0.37, SE 0.18, r = 0.22).

In cross-section, state levels of the ACS item and NSDUH depression do not correlate, which is unsurprising given that one is a broad disability screener and the other is a diagnostic interview. Over time, however, their within-state changes move together: a state-and-period fixed-effects regression of NSDUH youth depression on the ACS cognitive-difficulty rate yields a slope of 0.14 (SE 0.05, p = 0.01) across 714 state-period observations, and the decade-long changes from 2008–10 to 2017–19 correlate at r = 0.22 (slope 0.37, SE 0.18). Against the YRBS state files (43 states, by sex), the ACS rate co-moves with persistent sadness at a slope of 0.30 (SE 0.19) with state-by-sex and year-by-sex fixed effects, though not with suicidal ideation.

**Assessment.** The ACS cognitive-difficulty item reproduces the female-led rise and co-moves with depression within states, making it usable for fine-grained geographic tests where no mental-health survey exists. Even so, it captures only about a sixth of the proportional rise in adolescent depression, and its girl-specific change is small relative to metro-level sampling error. For that reason, we pair every U.S. ACS test with state and county youth mental-health surveys.
