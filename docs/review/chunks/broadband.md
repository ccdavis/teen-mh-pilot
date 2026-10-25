<!-- Generated review chunk: broadband -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-broadband)

Context: Teen Distress Pilot → Part 2 · Phones and social media (H1) → Continuous broadband coverage and the AT&T 2010 footprint at county level

Editable source entry points: [scripts/report/90_build_report.py:1](../../../scripts/report/90_build_report.py#L1)

---

### Continuous broadband coverage and the AT&T 2010 footprint at county level

Part 2 interpreted the null for 4G LTE launch dates as a timing problem: the 2011-13 metro upgrades came after smartphones and mobile social media had already spread, and were compressed into two years. This section replaces the launch dates with two public county series that carry more variation. The first is continuous coverage: the share of each county's population with wireline, fixed and mobile broadband available, by advertised speed tier, from the NTIA State Broadband Initiative's National Broadband Map (nine semiannual rounds, June 2010 to June 2014, block-level files aggregated with Census block populations and NTIA's county "Analyze" tables) spliced to the FCC Form 477 fixed-deployment files and county Area Tables (fourteen rounds, December 2014 to June 2021). The second is the instrument used by [Myers and Hooper (2026)](https://www.nber.org/papers/w35310): the share of county population living in 2000 Census blocks with any AT&T Mobility mobile-wireless coverage in the December 2010 release, a snapshot of the network that carried the iPhone during AT&T's June 2007 to February 2011 exclusivity. Myers and Hooper use this same public release (not a proprietary carrier map), code a block as covered if any AT&T polygon touches it, and classify counties with more than 90% of population covered as treated and under 10% as control; our reconstruction yields 892 treated, 1,447 control and 802 intermediate counties against their 822, 1,490 and 795, with a mean county share of 44%. AT&T's 2010 footprint is metropolitan (75% of population covered in metro counties versus 25% elsewhere) and only loosely related to the 4G timing used in Part 2 (correlation with the LTE onset year -0.26; counties whose metro had LTE by the 2012 school year averaged 76% coverage versus 29% for later or undated metros) or to Verizon's footprint (r = +0.22). Methods, sources and carrier roll-ups are in `notes/broadband.md`; the compiled tables are `data/compiled/broadband/county_broadband_panel.csv` and `county_att_mobile_2010.csv`.

Across all counties, wireline availability was already high in December 2010 (87% of population on average) and barely moved to 2021 (92%); the variation is in speed. Wireline service at 25 Mbps or faster reached 25% of county population in December 2010, 54% in December 2013, 67% in December 2016 and 82% in June 2021, mostly cable DOCSIS 3 upgrades that reached rural counties last. Mobile wireless covered 95% of county population in December 2010 and 98% by June 2014, when the NTIA series ends; the FCC's later mobile data are provider shapefiles without a county summary and were not used.

#### Continuous dose, 2010-2021

The design is Phase 1's: county-by-grade series with county-by-grade and state-by-year fixed effects, standard errors clustered by 2013 CBSA, each coverage measure interpolated to the survey spring. The coefficients are per 10 percentage points of county population gaining access.

![Chart: bb_coefficients](../../figures/bb_coefficients.png)

Left: effect of +10 pp of county population covered on the share of students sad or hopeless (CA, IL, ME, PA, WA) and considering suicide (CA, IL, ME, MN, PA, WA), 2010-2021, county x grade and state x year fixed effects, 95% intervals clustered by CBSA. Right: Minnesota 1998-2019, coefficient on the county's AT&T December-2010 coverage share interacted with each survey wave (2007, the last pre-iPhone wave, is the reference), county x grade and year fixed effects; a value of -1 means that a fully covered county moved 1 pp lower than an uncovered county relative to 2007.

<table>
<colgroup>
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
</colgroup>
<thead>
<tr class="header">
<th>County coverage measure</th>
<th>Sad/hopeless, all</th>
<th>girls (CA, ME)</th>
<th>boys (CA, ME)</th>
<th>Considered suicide, all</th>
<th>girls (CA, ME)</th>
<th>boys (CA, ME)</th>
<th>Considered suicide, all, 2010-19 only</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Any wireline (DSL, cable, fiber)</td>
<td>-0.44 (0.42)<br />
<span class="small">n=1752, 218 counties</span></td>
<td><strong>-1.43 (0.61)</strong><br />
<span class="small">n=755, 69 counties</span></td>
<td>+0.01 (0.35)<br />
<span class="small">n=755, 69 counties</span></td>
<td><strong>+0.64 (0.30)</strong><br />
<span class="small">n=1691, 294 counties</span></td>
<td>+0.43 (0.77)<br />
<span class="small">n=535, 69 counties</span></td>
<td>+0.81 (0.54)<br />
<span class="small">n=535, 69 counties</span></td>
<td>+0.59 (0.31)</td>
</tr>
<tr class="even">
<td>Wireline, 10 Mbps or faster</td>
<td>+0.00 (0.23)<br />
<span class="small">n=1752, 218 counties</span></td>
<td>-0.41 (0.39)<br />
<span class="small">n=755, 69 counties</span></td>
<td>+0.35 (0.27)<br />
<span class="small">n=755, 69 counties</span></td>
<td><strong>+0.42 (0.18)</strong><br />
<span class="small">n=1691, 294 counties</span></td>
<td>+0.75 (0.42)<br />
<span class="small">n=535, 69 counties</span></td>
<td><strong>+0.78 (0.27)</strong><br />
<span class="small">n=535, 69 counties</span></td>
<td><strong>+0.40 (0.19)</strong></td>
</tr>
<tr class="odd">
<td>Wireline, 25 Mbps or faster</td>
<td>+0.01 (0.18)<br />
<span class="small">n=1752, 218 counties</span></td>
<td>-0.25 (0.26)<br />
<span class="small">n=755, 69 counties</span></td>
<td>+0.04 (0.22)<br />
<span class="small">n=755, 69 counties</span></td>
<td><strong>+0.35 (0.09)</strong><br />
<span class="small">n=1691, 294 counties</span></td>
<td>+0.40 (0.29)<br />
<span class="small">n=535, 69 counties</span></td>
<td>+0.29 (0.23)<br />
<span class="small">n=535, 69 counties</span></td>
<td><strong>+0.46 (0.12)</strong></td>
</tr>
<tr class="even">
<td>Fixed terrestrial, 25/3 Mbps</td>
<td>+0.08 (0.15)<br />
<span class="small">n=1752, 218 counties</span></td>
<td>-0.20 (0.21)<br />
<span class="small">n=755, 69 counties</span></td>
<td>-0.11 (0.20)<br />
<span class="small">n=755, 69 counties</span></td>
<td>+0.23 (0.13)<br />
<span class="small">n=1691, 294 counties</span></td>
<td>+0.38 (0.24)<br />
<span class="small">n=535, 69 counties</span></td>
<td>+0.22 (0.26)<br />
<span class="small">n=535, 69 counties</span></td>
<td>+0.17 (0.16)</td>
</tr>
<tr class="odd">
<td>Mobile wireless (3G/4G), 2010-14 only</td>
<td>-0.64 (0.51)<br />
<span class="small">n=330, 52 counties</span></td>
<td>-</td>
<td>-</td>
<td>-0.44 (0.23)<br />
<span class="small">n=502, 138 counties</span></td>
<td>-</td>
<td>-</td>
<td>-0.44 (0.23)</td>
</tr>
<tr class="even">
<td>Any technology, 10 Mbps, 2011-14 only</td>
<td>-0.22 (0.42)<br />
<span class="small">n=212, 50 counties</span></td>
<td>-</td>
<td>-</td>
<td>+0.52 (0.45)<br />
<span class="small">n=212, 50 counties</span></td>
<td>-</td>
<td>-</td>
<td>+0.52 (0.45)</td>
</tr>
</tbody>
</table>

Coefficient (SE) per +10 pp of county population covered, county x grade series 2010-2021 (the mobile measure ends in 2014). Bold: \|t\| \> 1.96. The last column repeats the all-sex ideation estimate on 2010-2019 surveys, before the pandemic waves.

Any-wireline availability, which varies little, is unrelated to sadness (-0.44 (0.42) pp per 10 pp) and weakly positive for suicidal ideation (+0.64 (0.30)). The speed tiers that did spread during the decade are positively associated with ideation: +0.42 (0.18) pp per 10 pp of population gaining 10 Mbps wireline and +0.35 (0.09) for 25 Mbps, with n = 1,691 county-grade-years in 294 counties; restricted to 2010-2019 the 25 Mbps estimate is +0.46 (0.12) and the 10 Mbps estimate +0.40 (0.19). Sadness shows nothing comparable (+0.01 (0.18) for 25 Mbps). Where sex splits exist (California and Maine), the ideation gradient is similar for girls (+0.40 (0.29)) and boys (+0.29 (0.23)), and girls' sadness is if anything negative (-0.25 (0.26)). Mobile coverage over 2010-2014, the measure closest to smartphone access, points the other way: -0.44 (0.23) for ideation and -0.64 (0.51) for sadness, in the counties (mostly rural) that were still gaining 3G/4G coverage.

Two scalings put the ideation gradient in context. Within-county variation in 25 Mbps wireline coverage over the period has a standard deviation of 14 pp, so one within-county standard deviation corresponds to +2.7% of the mean ideation rate (17.8%); [Churchill and Johnson](https://www.nber.org/papers/w34614) report 9.3-16.5% per state-level standard deviation of access. The Phase 1 metro LTE contrast on the same panels gave -0.72 (0.43) pp for ideation and +0.64 (0.87) for sadness, and the NTIA smartphone-adoption dose +0.06 (0.15) per 10 pp. The wireline-speed gradient is therefore the first positive county-level connectivity association in these panels, but it is a gradient in cable upgrades that arrived late in rural counties whose ideation rates also rose late, with state-by-year effects removing only the state-wide part of that timing; it is not a smartphone measure, and the mobile measure that is one has the opposite sign.

#### The AT&T 2010 footprint and Minnesota's 1998-2019 county series
