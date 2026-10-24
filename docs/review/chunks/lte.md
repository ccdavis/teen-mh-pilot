<!-- Generated review chunk: lte -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-lte)

Context: Teen Distress Pilot → Part 2 · Phones and social media (H1) → 4G rollout across U.S. metros

Editable source entry points: [scripts/report/90_build_report.py:213](../../../scripts/report/90_build_report.py#L213)

---

### 4G rollout across U.S. metros

If the arrival of fast mobile data drove the initial upturn in adolescent distress, teenagers in metropolitan areas that received commercial 4G LTE earliest should have experienced an earlier rise in cognitive difficulty and sadness.

We compiled commercial 4G LTE launch dates from carrier press releases and trade-press archives covering 967 carrier-market launches (Verizon 442, AT&T 243, Sprint 234, T-Mobile 47). Mapped to 2013 CBSA boundaries, these records establish a first-launch date for 98 of the 100 largest metropolitan areas and 279 of the 311 metros identified in the public ACS. Verizon's initial December 2010 rollout covered 36 of these metros, followed by 125 metros in 2011, 96 in 2012, and 14 in 2013. Each market's treatment onset is assigned to the first school year beginning after its initial commercial launch. Remaining coverage gaps (primarily Verizon's smaller 2013 rural market waves and roughly 44 AT&T launch dates outside the top 100 metros) are documented in the methods note.

#### Descriptive: onset cohorts

![Chart: onset_cohorts](../../figures/onset_cohorts.png)

Population-weighted ACS cognitive-difficulty rate for 12–17-year-olds in metros grouped by first commercial LTE launch, indexed to each cohort's 2008–10 mean.

If early 4G availability accelerated adolescent distress, metros in the December 2010 and 2011 launch waves should have pulled ahead of the 2012–13 wave between 2011 and 2013. Through 2013, however, the three cohorts move closely together. Starting in 2014, girls in the December 2010 cohort drift higher (reaching an index of 127 by 2019 versus 110–116 in later cohorts), but that earliest cohort consists of the 36 largest metros—where the affluent-teen composition shift documented in Part 1 is concentrated—and the divergence appears three years after launch. In the event-study regressions below, the coefficients for girls four to six years after launch are +0.6 to +1.1 pp with standard errors near 1 pp.

#### Event study

![Chart: event_study](../../figures/event_study.png)

Estimated effect by school year relative to initial LTE launch (with the year prior to launch as the reference period), including market and year fixed effects, population weights, and standard errors clustered by market. Green: the 279 metros with a dated launch, identifying off rollout timing alone. Grey: adds the 32 undated metros and state non-metro remainders coded as never treated (an upper-bound contrast, since rural areas received LTE around 2013–14).

| Onset definition | Sample                    | 12–17 all    | Girls        | Boys         | 65+ placebo  | 25–49        |
|------------------|---------------------------|--------------|--------------|--------------|--------------|--------------|
| First carrier    | dated metros              | +0.02 (0.15) | −0.04 (0.19) | +0.03 (0.27) | +0.03 (0.15) | +0.11 (0.08) |
| Verizon          | dated metros              | +0.01 (0.16) | −0.11 (0.20) | +0.05 (0.29) | +0.07 (0.16) | +0.11 (0.08) |
| Second carrier   | dated metros              | −0.01 (0.15) | −0.11 (0.17) | +0.20 (0.23) | +0.28 (0.14) | +0.09 (0.07) |
| First carrier    | \+ non-metro as untreated | 0.00 (0.09)  | −0.08 (0.10) | +0.11 (0.13) | +0.12 (0.11) | −0.10 (0.06) |

Static difference-in-differences coefficient on "LTE in force" in percentage points, with standard errors in parentheses. Permuting onset dates across markets yields a placebo standard error of roughly 0.07 pp for the full panel.

**Assessment.** Staggered 4G LTE launch dates across U.S. metropolitan areas do not predict the timing of the rise in the ACS cognitive-difficulty item. For girls, the 95% confidence interval rules out effects larger than +0.33 pp on the dated-metro sample and +0.12 pp when including non-metro controls, compared with a national 2010–2019 increase of roughly 0.5 pp. Three limitations prevent this null result from ruling out H1: commercial LTE launches were compressed into a narrow 2011–2012 window across most major metros; adolescent social-media norms spread across markets through national platforms; and the ACS disability item captures only a fraction of internalizing distress. What the result does establish is that a metro-level rollout design using the ACS cannot detect a smartphone effect. In the next subsection we re-run the same geographic timing test on county-level youth mental-health surveys, and in the reconciliation section we compare our setup with Elaine Guo's British Columbia wireless study, which found a large effect on clinical school designations in rural mountain towns.
