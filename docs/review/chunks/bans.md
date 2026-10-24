<!-- Generated review chunk: bans -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-bans)

Context: Teen Distress Pilot → Part 4 · The interaction (H3): phones in the same hours as high-pressure school → School phone bans

Editable source entry points: [scripts/report/90_build_report.py:490](../../../scripts/report/90_build_report.py#L490)

---

### School phone bans

School phone restrictions are the one policy intervention that both the phone-centered and interaction hypotheses predict should matter, and they have shifted markedly over the past fifteen years. Below we combine national school-policy surveys, our 51-state legislative tracker, existing quasi-experimental evaluations, and PISA 2022 microdata to assess what school phone bans do.

#### Bans and sadness on one time axis

![Chart: bans_vs_sadness](../../figures/bans_vs_sadness.png)

Top: principal-reported share of U.S. public schools prohibiting non-academic phone use during school hours (NCES SSOCS; 2013–14 is from a smaller Fast Response Survey; question wording changed in 2017–18), the 2024–25 School Pulse Panel estimates (77% prohibiting use during any class, 30% all day), and the cumulative share of states with a statewide bell-to-bell or instructional-time mandate in force. Bottom: NSDUH past-year major depressive episode (ages 12–17), YRBS persistent sadness by sex, and county-mean sadness from the Washington, Maine, and Illinois youth surveys. Grey band = 2020.

Plotted on a common timeline, U.S. school phone restrictions and adolescent distress moved in opposite directions over two successive cycles. Between 2009–10 and 2015–16—the years when smartphones replaced feature phones—the share of public schools prohibiting cell-phone use fell from 91% to 66%, while youth depression and sadness rose from their 2011–13 lows. School prohibitions then rebounded to 77% by 2019–20, and a wave of state legislation between 2023 and 2026 has pushed mandatory class-time or bell-to-bell bans into a majority of states; over the same post-2021 window, adolescent sadness fell across every state survey with recent data. Because these are aggregate national series, however, the timing alignment is only suggestive: sadness continued to rise through 2019–2021 even after school prohibitions began recovering, and the post-2021 downturn started before most state laws took effect. Two non-exclusive mechanisms could account for the recent decline:

- **Gradual school re-restriction and broader norm shifts.** The recovery in school restrictions after 2016, combined with growing concern among parents, educators, and teenagers themselves, may have curbed the most disruptive in-school phone use even before statutory state mandates arrived. That interpretation is consistent with the PISA 2022 cross-section and Norway's middle-school ban study, though the aggregate U.S. timing is loose.
- **Shifts in platform content.** If the 2012–2019 rise was driven primarily by peer social comparison on photo-sharing networks (Instagram, Snapchat), the subsequent shift of teen screen time toward algorithmic short-form video feeds (TikTok, YouTube) could keep total screen hours high while generating less acute social-comparison distress. Because public surveys do not track platform mix over time, our data cannot test this channel directly.

#### Lags and enforcement

Two practical features of school phone bans also affect how the aggregate timeline and upcoming state evaluations should be interpreted:

- **Effects take a year or two to materialize.** Quasi-experimental studies consistently find adjustment lags after a ban is introduced. In the 2026 U.S. Yondr-pouch study (Allcott et al.), student subjective well-being *dipped* by 0.20 SD in the adoption year before turning positive (+0.16 SD) in year two; in Norway (Abrahamsson 2024), reductions in bullying and mental-health visits grew over three years; and in Florida (Figlio and Özek 2025), student suspensions rose 12% in year one before fading in year two as test-score gains emerged. If school bans require a year of administrative adjustment before improving school climate, the 2015–16 trough in U.S. restrictions would register around 2017–18 and the 2024–25 state mandates around 2026–27. Evaluations of the new U.S. laws will therefore need at least two post-ban waves rather than a single immediate post-year.
- **Stated policy differs from actual enforcement.** PISA 2022 measures both principal-reported school bans and student-reported daily smartphone use at school. Across 52 education systems with both items, a median 46% of students in ban schools still reported using a smartphone at school daily (versus 62% in non-ban schools), and in 24 systems a majority of students in ban schools did so. Enforcement in the United States in 2022 was particularly weak: 70.1% of students in U.S. ban schools used a smartphone daily at school compared with 81.7% in non-ban schools (an 11.6-point gap, versus gaps of 30–46 points in Japan, Taiwan, Switzerland, and Brunei). Stated school policies in the pre-2024 U.S. data were thus loosely enforced, and any effects estimated from early state mandates will represent a lower bound on strict bell-to-bell enforcement.

Country-by-country daily in-school smartphone rates in ban and non-ban schools are reported in `results/tables/pisa_ban_enforcement_by_country.csv`.

##### The national school-policy series

![Chart: phone_bans_trend](../../figures/phone_bans_trend.png)

Principal-reported share of public schools prohibiting non-academic cell-phone use during school hours (NCES SSOCS; the 2013–14 point comes from a smaller Fast Response Survey, and the item wording changed in 2017–18). The 2024–25 School Pulse Panel asks about class time rather than all school hours: 77% prohibit phones in any class, and 30% prohibit them both in class and outside class.

#### State bans and what can be tested when

| Policy type                          | Effective school year | N   | States                                                                                                                                                |
|--------------------------------------|-----------------------|-----|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| ban during instructional time        | 2024-25               | 1   | Indiana                                                                                                                                               |
| ban during instructional time        | 2025-26               | 5   | Iowa, Nevada, North Carolina, Tennessee, West Virginia                                                                                                |
| ban during instructional time        | 2026-27               | 2   | Michigan, Wisconsin                                                                                                                                   |
| requires districts to adopt a policy | 2024-25               | 1   | Minnesota                                                                                                                                             |
| requires districts to adopt a policy | 2025-26               | 4   | Alaska, Arizona, Idaho, New Mexico                                                                                                                    |
| requires districts to adopt a policy | 2026-27               | 5   | California, Colorado, Connecticut, Delaware, Wyoming                                                                                                  |
| statewide bell-to-bell ban           | 2023-24               | 1   | Florida                                                                                                                                               |
| statewide bell-to-bell ban           | 2024-25               | 2   | Louisiana, South Carolina                                                                                                                             |
| statewide bell-to-bell ban           | 2025-26               | 14  | Alabama, Arkansas, District of Columbia, Kentucky, Missouri, Nebraska, New Hampshire, New York, North Dakota, Ohio, Oklahoma, Oregon, Texas, Virginia |
| statewide bell-to-bell ban           | 2026-27               | 8   | Georgia, Hawaii, Kansas, Maine, New Jersey, Rhode Island, Utah, Vermont                                                                               |
| statewide bell-to-bell ban           | 2027-28               | 2   | Illinois, Maryland                                                                                                                                    |

Compiled from Ballotpedia, Education Week, KFF, and enacted state statutes; classification differences across trackers are documented in the data file. Florida's HB 379 (instructional time, 2023–24) was the earliest statewide mandate.

Nearly all statewide phone bans took effect in fall 2024, fall 2025, or fall 2026. Because the latest mental-health survey waves currently in hand are from spring 2023 (YRBS, Pennsylvania, Maine), spring 2024 (Illinois), and fall 2025 (Washington, which has state guidance rather than a mandate), post-ban statewide mental-health outcomes are not yet observed in our panel. The upcoming 2025 YRBS state files will permit an initial difference-in-differences test comparing early-ban states—Florida (2023–24) and Indiana, Louisiana, and South Carolina (2024–25)—against states without a mandate across the 2021, 2023, and 2025 waves, by sex. As subsequent waves of the state county surveys are released, the county panel will test Minnesota's 2024–25 district-policy mandate, Maine's and California's 2026–27 mandates, and Illinois's 2027–28 bell-to-bell ban using the same county-by-grade panel structure developed for LTE above. Obtaining NCES restricted-use SSOCS files (which include state and county identifiers) would also enable a school-level panel design across the 2010–2024 relaxation and re-tightening cycle.

#### What the causal literature already shows
