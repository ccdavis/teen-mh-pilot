<!-- Generated review chunk: adoption-rather-than-rollout-smartphone-use-against-the-state-youth-survey -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-adoption-rather-than-rollout-smartphone-use-against-the-state-youth-survey)

Context: Teen Distress Pilot → Part 2 · Phones and social media (H1) → Adoption rather than rollout: smartphone use against the state youth survey

Editable source entry points: [scripts/report/90_build_report.py:329](../../../scripts/report/90_build_report.py#L329)

---

### Adoption rather than rollout: smartphone use against the state youth survey

Because commercial 4G launch dates are a coarse measure of when teenagers actually went online on phones, we next test whether state-level smartphone adoption predicts adolescent sadness. Using the harmonized NTIA series (the share of persons in households with a 12–17-year-old who use a smartphone for internet, interpolated between the 2011–2019 CPS waves) against the YRBS state files across 43 states from 2011 to 2019, with state and year fixed effects:

| Outcome                               | Measure of adoption                | Effect per +10 pp of adoption (SE) |
|---------------------------------------|------------------------------------|------------------------------------|
| YRBS sad/hopeless, girls              | teen-household smartphone internet | **+0.92 (0.43)**                   |
| YRBS sad/hopeless, boys               | same                               | +0.33 (0.40)                       |
| YRBS sad/hopeless, girls              | household mobile data plan         | +0.49 (0.51)                       |
| ACS cognitive difficulty 12–17, girls | teen-household smartphone internet | −0.04 (0.07)                       |

The state-level estimates align with the pattern predicted by H1—positive for girls rather than boys, and appearing on the self-reported YRBS sadness item rather than the ACS disability screener—but the evidence is fragile: it rests on five biennial YRBS waves, interpolated state adoption shares, and a p-value near 0.03 across 43 state clusters. Moreover, the county-level version of the same regression in the state youth surveys does not reproduce this relationship, so we treat the state-level correlation as suggestive.
