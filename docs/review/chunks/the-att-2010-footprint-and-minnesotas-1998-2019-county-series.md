<!-- Generated review chunk: the-att-2010-footprint-and-minnesotas-1998-2019-county-series -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-the-att-2010-footprint-and-minnesotas-1998-2019-county-series)

Context: Teen Distress Pilot → Part 2 · Phones and social media (H1) → Continuous broadband coverage and the AT&T 2010 footprint at county level → The AT&T 2010 footprint and Minnesota's 1998-2019 county series

Editable source entry points: [scripts/report/90_build_report.py:1](../../../scripts/report/90_build_report.py#L1)

---

Minnesota's biennial-to-triennial county tables (1998, 2001, 2004, 2007, 2010, 2013, 2016, 2019; 87 counties) are the only county series that bracket the iPhone-exclusivity window. If early smartphone access raised distress, counties with AT&T coverage should have pulled above uncovered counties after 2007. They did not. Relative to 2007, fully covered counties were -1.03 (1.37) pp lower in 2010, -0.58 (1.39) in 2013 and -1.80 (1.40) in 2019 on grade-9 suicidal ideation, with pre-period coefficients of +1.25 (1.35) (1998) and +0.93 (1.36) (2004). Pooled, AT&T coverage x post-2007 is -1.59 (0.82) pp for ideation (mean 21.4% before 2007), -0.72 (0.43) for attempts, and -1.02 (0.45) for the 30-day sadness item that ends in 2010; the Myers-Hooper binary contrast gives -1.66 (0.90) for ideation. Pre-trends are flat (-0.24 (0.40) pp per wave for ideation). Verizon's footprint, whose customers could not buy an iPhone until February 2011, shows no comparable pattern (+2.67 (1.95)).

| Minnesota item                               | Mean to 2007 (%) | Pre-trend 1998-2007 (pp per wave) | AT&T share x post-2007 (pp) | Treated vs control x post (pp) | Verizon share x post (pp) | n / counties |
|----------------------------------------------|------------------|-----------------------------------|-----------------------------|--------------------------------|---------------------------|--------------|
| Considered suicide (grade 9, 1998-2019)      | 21.4             | -0.24 (0.40)                      | -1.59 (0.82)                | -1.66 (0.90)                   | +2.67 (1.95)              | 684 / 87     |
| Attempted suicide (grade 9, 1998-2019)       | 6.4              | -0.16 (0.23)                      | -0.72 (0.43)                | **-0.98 (0.43)**               | -0.00 (0.78)              | 684 / 87     |
| Sad all/most of the last 30 days (1998-2010) | 11.8             | -0.13 (0.22)                      | **-1.02 (0.45)**            | **-1.18 (0.44)**               | -0.86 (0.95)              | 1291 / 87    |
| Discouraged or hopeless, 30 days (1998-2010) | 12.3             | -0.18 (0.20)                      | -0.94 (0.51)                | -0.85 (0.49)                   | -2.64 (1.10)              | 1291 / 87    |
| Nervous or worried, 30 days (1998-2010)      | 13.8             | +0.15 (0.20)                      | -0.60 (0.48)                | -0.65 (0.47)                   | -1.42 (1.18)              | 1291 / 87    |
| Under great stress, 30 days (1998-2010)      | 30.4             | -0.25 (0.34)                      | -0.81 (0.77)                | -1.04 (0.74)                   | +0.78 (1.33)              | 1291 / 87    |

Minnesota Student Survey county series, county x grade and year fixed effects, standard errors clustered by CBSA (county outside CBSAs). AT&T share is the share of county population in blocks with AT&T mobile coverage, December 2010 (0-1), so a coefficient is the difference between a fully covered and an uncovered county. The 30-day items were last asked in 2010. "Treated vs control" follows Myers and Hooper (\>90% vs \<10%, intermediate counties dropped).

![Chart: bb_scatter](../../figures/bb_scatter.png)

Left: Minnesota counties, change in grade-9 suicidal ideation between the 2007 and 2019 waves against the AT&T December-2010 coverage share (blue: metropolitan counties; dotted line: population-weighted fit, slope -1.52 (0.98) pp per unit share; +0.37 (1.53) with metro and log-population controls; the 2001-2007 placebo change gives +0.19 (0.81)). Right: states, change in the average annual youth (10-19) suicide rate between 2003-07 and 2013-17 against the state population-weighted AT&T share (CDC WONDER, no suppression at state level).

Extending the same test to the five states whose county series begin after 2007 can only ask whether high-AT&T counties kept diverging during 2010-2019. Pooled across all six states with county-by-grade and state-by-year effects, the differential trend is -2.01 (0.97) pp per decade for ideation (318 counties) and -0.41 (3.35) for sadness; by sex in California and Maine, -7.56 (3.48) for girls and -4.49 (2.64) for boys. Maine's 16 counties show no cross-sectional gradient in 2009 and none in the 2009-2019 change (correlations between -0.2 and +0.1).

#### County and state youth suicide

CDC WONDER's web form (the API refuses sub-national queries) supplied suicide deaths and population for ages 10-19 by county for 1999-2002, 2003-07, 2008-12, 2013-17 and 2018-22, with counts under 10 suppressed. Suppression binds hard at this age: only about 56% of youth live in counties with reportable counts in both 2003-07 and 2013-17, and the reportable set mixes large counties with small counties that happened to record zero deaths. The AT&T estimate changes sign with the treatment of suppressed cells (+1.23 (0.48) deaths per 100,000 per year, for a fully covered versus uncovered county, on reportable counties; -2.04 (0.63) when suppressed counts are set to the midpoint 5), and the 176 large counties where suppression is rare have almost no AT&T variation (mean share 99%, SD 0.01). The county suicide test is therefore not informative with public data; the state series, which has no suppression, is the usable fallback.

| Youth (10-19) suicide, change in deaths per 100,000 per year, 2003-07 to 2013-17, on AT&T share (0-1) | n (share of U.S. youth)     | No controls      | Metro + log youth population                                     |
|-------------------------------------------------------------------------------------------------------|-----------------------------|------------------|------------------------------------------------------------------|
| Counties with unsuppressed counts in both periods (zeros reported, 1-9 suppressed)                    | 903 (56% of youth)          | **+1.23 (0.48)** | +0.70 (0.56)                                                     |
| All counties, suppressed counts set to the midpoint 5                                                 | 3138 (100%)                 | **-2.04 (0.63)** | -1.04 (0.66)                                                     |
| girls, unsuppressed counties                                                                          | 1752 (28%)                  | **+0.24 (0.09)** | -0.06 (0.04)                                                     |
| girls, all counties, midpoint-imputed                                                                 | 3138 (100%)                 | **-4.06 (0.90)** | -0.18 (1.29)                                                     |
| boys, unsuppressed counties                                                                           | 959 (49%)                   | **+2.05 (0.63)** | **+1.65 (0.80)**                                                 |
| boys, all counties, midpoint-imputed                                                                  | 3138 (100%)                 | **-4.18 (1.10)** | -2.37 (1.30)                                                     |
| **States, all youth**: state AT&T share x post-2007, 1999-2024 state x year panel, state + year FE    | 1162 state-years, 50 states | **-1.87 (0.73)** | +0.68 (1.64) <span class="small">(non-metro share x post)</span> |
| **States, girls**: state AT&T share x post-2007, 1999-2024 state x year panel, state + year FE        | 557 state-years, 50 states  | +0.03 (0.83)     | +3.94 (3.91) <span class="small">(non-metro share x post)</span> |
| **States, boys**: state AT&T share x post-2007, 1999-2024 state x year panel, state + year FE         | 1092 state-years, 49 states | **-2.71 (1.07)** | +0.54 (2.32) <span class="small">(non-metro share x post)</span> |

County rows: change in the average annual suicide rate per 100,000 youths aged 10-19 between 2003-07 and 2013-17, regressed on the AT&T December-2010 coverage share with state fixed effects and youth-population weights. State rows: state x year panel 1999-2024 (CDC WONDER, no suppression for all youth and boys), rate on the state's population-weighted AT&T share x post-2007 with state and year fixed effects, youth-population weights and standard errors clustered by state; the last column adds the state's non-metro population share x post-2007. Bold: \|t\| \> 1.96.

At state level, youth suicide rose by -1.87 (0.73) deaths per 100,000 per year more after 2007 in a fully AT&T-covered state than in an uncovered one (mean pre-2007 rate 4.4); the 1999-2007 pre-trend is +0.30 (1.24) per decade and the 1999-2002 to 2003-07 placebo change +0.17 (0.64). Girls: +0.03 (0.83); boys: -2.71 (1.07). With the state non-metro population share x post-2007 added, the AT&T coefficient is +0.68 (1.64) and the non-metro term +3.36 (1.92): the 2010s rise in youth suicide was a rural rise, and the AT&T 2010 footprint is first of all an urbanicity map. Fifty-one states give little power, and state-year counts for girls are mostly suppressed, so this is a weak test.

#### What the broadband literature identifies
