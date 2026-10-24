<!-- Generated review chunk: rollout-and-adoption-at-county-level-state-youth-surveys -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-rollout-and-adoption-at-county-level-state-youth-surveys)

Context: Teen Distress Pilot → Part 2 · Phones and social media (H1) → Rollout and adoption at county level, state youth surveys

Editable source entry points: [scripts/report/90_build_report.py:408](../../../scripts/report/90_build_report.py#L408)

---

### Rollout and adoption at county level, state youth surveys

#### LTE onset at county level

We link counties to 2013 CBSAs and their initial commercial 4G LTE launch dates. The unit of observation is a county-by-grade panel series with county-by-grade and state-by-year fixed effects, ensuring that changes in which grades a state surveys cannot register as changes in distress. Non-metro and undated counties serve as the comparison group (providing an upper-bound contrast, since rural LTE arrived around 2013–14), and standard errors are clustered by CBSA (or by county outside metro areas). Because the state surveys are biennial or triennial, no single pre-launch year is observed for every cohort, so event-study specifications pool the three years prior to LTE launch as the reference period.

| Panel                                                                                                        | DiD on "LTE in force" (pp) |
|--------------------------------------------------------------------------------------------------------------|----------------------------|
| Sad/hopeless, WA + ME counties, 2009-2019 (54 counties, 26 dated-metro, 130 county-grade series)             | +0.64 (SE 0.87)            |
| Considered suicide, WA + ME + MN counties, 1998-2019 (141 counties, 59 dated-metro, 217 county-grade series) | -0.72 (SE 0.43)            |
| Considered suicide, MN counties, 1998-2019 (87 counties, 33 dated-metro, 87 county-grade series)             | -1.82 (SE 0.67)            |

#### Smartphone adoption at the metro level

| Outcome            | Sex    | Effect per +10 pp teen-household smartphone internet (SE) | Counties / CBSAs | States                 |
|--------------------|--------|-----------------------------------------------------------|------------------|------------------------|
| sad hopeless       | all    | +0.13 (0.13)                                              | 89 / 42          | CA, IL, ME, PA, WA     |
| sad hopeless       | female | +0.22 (0.25)                                              | 32 / 21          | CA, ME                 |
| sad hopeless       | male   | -0.11 (0.14)                                              | 32 / 21          | CA, ME                 |
| considered suicide | all    | +0.06 (0.15)                                              | 105 / 46         | CA, IL, ME, MN, PA, WA |
| considered suicide | female | -0.04 (0.33)                                              | 31 / 21          | CA, ME                 |
| considered suicide | male   | -0.39 (0.13)                                              | 31 / 21          | CA, ME                 |

NTIA CBSA smartphone-internet shares interpolated between waves (restricted to CBSAs with at least 30 unweighted respondents), with county-by-grade and state-by-year fixed effects and standard errors clustered by CBSA, 2011–2019.

**Assessment.** Measuring self-reported sadness and suicidal ideation at the county level yields the same conclusion as the ACS metro panel: neither 4G LTE launch timing nor metro-level smartphone adoption predicts where adolescent distress rose fastest. The only coefficient exceeding two standard errors—Minnesota suicidal ideation after LTE onset (−1.82 pp, SE 0.67)—is negative and reflects the continuation of metro counties' steeper pre-2011 decline rather than a discrete break at LTE launch. Likewise, the positive state-level YRBS correlation between smartphone adoption and girls' sadness does not carry over to the county panels (+0.13 pp per 10 points overall across five states, SE 0.13; +0.22 pp for girls in California and Maine, SE 0.25). Across counties with very different connectivity timelines, the 2010s rise occurred almost simultaneously, and the recent post-2021 waves show a broad decline.
