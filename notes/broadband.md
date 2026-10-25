# County broadband coverage (NTIA NBM 2010-14, FCC 477 2014-21), the AT&T December-2010 footprint, and county youth suicide -- methods note

Built 2026-10-24. Code: `scripts/download/broadband/` (`fetch_broadband_files.py`, `fetch_fcc_area_tables.py`, `build_county_broadband.py`,
`wonder_county_suicide.py`), analysis `scripts/analysis/34_broadband_instruments.py` (tables `results/tables/bb_*.csv`), report part
`scripts/report/parts/broadband.py`. Raw files and every URL: `data/external/broadband/README.md`. Compiled (committed): `data/compiled/broadband/`.

## 1. Access

- NTIA: the plan's URL https://www.ntia.gov/page/national-broadband-map-data returns 404. The State Broadband Initiative (SBI) archive is
  https://www2.ntia.doc.gov/node/762 with a page per round and all files under https://www2.ntia.doc.gov/files/broadband-data/ (reachable, ~15 MB/s).
  Nine rounds exist (June 2010 ... June 2014); the first two are on 2000 Census blocks, the rest on 2010 blocks. The national block CSVs are
  0.5-2.1 GB zipped (6-15 GB unzipped), concatenations of per-state exports with repeated header lines (and, in June 2010, a 17-column variant
  with a `FREQUENCY` field), so they are split by header line (`split_by_header.awk`) and read part by part with duckdb. The Analyze summary
  tables (county shares by technology and speed tier, 2011-2014) are CSV/xls/xlsx and read directly (duckdb `read_xlsx`, xlrd for the two .xls).
- FCC: www.fcc.gov returns 403 to curl and to headless Chromium, so the Form 477 index pages were unreadable; the fixed-deployment block files
  for Dec 2014 - Jun 2016 are on transition.fcc.gov (URL pattern `form477/BroadbandData/Fixed/<Mon><yy>/Version%20<n>/US-Fixed-with-Satellite-<Mon><yyyy>.zip`,
  9-11 GB each unzipped) and the Dec 2016 - Jun 2021 county Area Tables are on opendata.fcc.gov (Socrata; pulled with the SODA API, county rows
  only). FCC staff block population estimates (2010 blocks, pop2010 and pop2015) were taken from transition.fcc.gov via the links on the
  Wayback copy of the staff-block-estimates page. The FCC mobile Form 477 products (provider x technology shapefiles, no county summary) were
  not pulled. catalog.data.gov's API returned 404.
- Census 2000 SF1 geographic headers (block POP100) from www2.census.gov for the 2000-block rounds; checked against state totals.
- CDC WONDER: the API refuses sub-national geography, but the request form does not. `wonder_county_suicide.py` drives https://wonder.cdc.gov/ucd-icd10.html
  (D76, 1999-2020) and ucd-icd10-expanded.html (D157, 2018-2023) with Playwright: click "I Agree", set Group by = County (and Sex), Five-Year
  Age Groups 10-14 and 15-19, Injury Intent = Suicide (*U03, X60-X84, Y87.0), the period's years, all states, measures deaths/population/crude
  rate, show suppressed and zero rows, export TSV. Ten county requests (periods 1999-2002 all; 2003-07, 2008-12, 2013-17 from D76 and 2018-22
  from D157, all and by sex) plus four state x year requests, 10-20 s apart; the 2008-12 by-sex request timed out twice at the server and is missing.

## 2. Construction of the compiled tables

`county_broadband_panel.csv` (72,278 rows = 3,151 counties x 23 rounds, 6.4 MB): `fips, round (YYYY-MM), year_frac, source, population`
and population-weighted shares of county population with service available: `wireline_any/ge3/ge10/ge25`, `fixed_any/ge10/ge25` (wireline +
terrestrial fixed wireless), `fixedwireless_any`, `mobile_any/ge3` (terrestrial mobile wireless, NBM code 80), `att_mobile_any` (2010 rounds), and
the Analyze table's any-technology tiers `anytech_ge3/ge10/ge25`. Source codes: SBI-blocks-2000, NBM-analyze, NBM-analyze+SBI-blocks-2010,
FCC477-blocks, FCC477-area (defined in the build script's docstring).
- SBI block files (June and Dec 2010, 2000 blocks; Dec 2013 and June 2014, 2010 blocks): a block is covered at a tier if any provider record of
  the technology class has MAXADDOWN at or above the tier code (2 = 200 kbps, 5 = 3 Mbps, 7 = 10 Mbps, 8 = 25 Mbps). Wireline = codes 10/20/30
  (DSL, copper), 40/41 (cable), 50 (fibre), 90 (power line); fixed wireless 70/71; mobile 80; satellite 60 and "other" 0 excluded. The small-block
  file (blocks under 2 sq mi) and the road-segment/address file (large blocks) are combined; June 2010 has no large-block file, so its wireline
  shares are not used. County share = sum of block population covered / county population (Census 2000 block POP100 for the 2010 rounds, FCC
  pop2010 for 2013-14); all blocks in the Census file count, so blocks absent from the SBI file are uncovered.
- Analyze tables (Jun 2011 - Jun 2014): county rows, population metric; NTIA's own population-weighted shares (`anywline`, `terrmobilewless`,
  `advdl_grNk`, ...). The speed tiers there are any-technology (including mobile), so they are kept under `anytech_*`; for Dec 2013 and June 2014
  the wireline/fixed tiers come from the block files.
- FCC 477 block files (Dec 2014 - Jun 2016): consumer records; wireline techcodes 10-12, 20, 30, 40-43, 50, 90; fixed adds 70; tiers 0.2, 3,
  10/1 and 25/3 Mbps (download/upload); weights FCC pop2015.
- FCC Area Tables (Dec 2016 - Jun 2021): county rows for technology sets `acfo` (wireline), `acfow` (fixed terrestrial) and `w` at tiers 0.2, 10, 25;
  share = population with 1+ providers / total, summing urban/rural and tribal rows. Later "Status V2" versions used where published.
- Seams: NBM Dec 2013 - FCC Dec 2014 means are close (wireline_ge25 0.54 -> 0.62, wireline_ge10 0.74 -> 0.73, wireline_any 0.89 -> 0.87; FCC
  self-reports are known to overstate availability relative to the SBI's validated polygons, Myers & Hooper 2026 fn. 3). Means by round are in
  `results/tables/bb_panel_summary.csv`.

`county_att_mobile_2010.csv` (3,141 counties): `att_share_dec2010` = share of county 2000 population in blocks with any AT&T Inc. (HOCONUM 130077:
AT&T Mobility LLC, New Cingular Wireless PCS LLC et al.) TRANSTECH-80 record in the December 2010 release; `att_share_bg_dec2010` = Myers & Hooper's
variant (block-group mean of block coverage, block groups weighted by 2000 population); `att_area_share_dec2010` weights blocks by the polygon's
area share (`PCT_BLK_IN_SHAPE`); `att_share_jun2010` from the first release (incomplete: AT&T appears in 42 states and 3.6 M blocks against 51 and
4.9 M in December, so June is a check only); `verizon_/sprint_/tmobile_share_dec2010` (HOCONUM 131425, 131244, 130403 incl. the "T-Mobile" roll-up);
`any_mobile_share`, `mobile_ge3_share`, `n_blocks`, `population_2000`, and `mh_group` = treated (>0.9), control (<0.1), intermediate on the
block-group variant. Result: 892 treated / 1,447 control / 802 intermediate counties (Myers & Hooper: 822 / 1,490 / 795; they also reassign
counties where AT&T acquired Alltel's CDMA networks). Mean county share 0.44 (0.85 population-weighted); 75% in metro counties vs 25% non-metro;
correlation with Verizon's share 0.22, with the LTE onset year of the county's metro -0.26. Every record in the wireless file is at least 200 kbps,
so "any coverage" is the SBI's broadband definition; most mobile records are coded 3-6 Mbps (3G).

How this differs from Myers & Hooper: same public release and carrier definition; they average block coverage within block groups before weighting
(our `att_share_bg_dec2010` reproduces this), use the June 2010 release to remove Alltel-acquired CDMA markets, and exclude intermediate counties
in their binary analyses. We use the continuous share as the main regressor and report their binary contrast alongside.

`county_youth_suicide_periods.csv` (fips, period, sex, deaths, population, rate_per100k = deaths / summed annual population x 100,000 = average
annual rate, suppressed flag, database, county name): 3,147 counties (D76) / 3,142 (D157). Suppression: deaths 1-9 are "Suppressed", zeros are
shown. All-sex 2003-07: 1,441 counties reportable (about 56% of youth live in reportable counties in both 2003-07 and 2013-17).
`state_youth_suicide_year.csv`: state x year x sex deaths and population 1999-2024 (D76 1999-2020; the expanded database, now "2018-2024",
2018-2024; the analysis uses D76 through 2017 and the expanded file from 2018 where available). Counts under 10 are suppressed even at state
level for small states and for girls in most states (about a quarter of the D76 state-years for all sexes, most girl rows), so the state series
is used for all youth and boys; the girls' series is thin.

## 3. Analyses (34_broadband_instruments.py)

Panel: `results/tables/state_survey_county_grade_series.csv` from 23_state_surveys.py (county x grade x year x item x sex; MN 1998-2019, ME
2009-2023, WA 2010-2025, PA 2015-2025, IL 2018-2024, CA 2013-2019), unweighted county x grade series, county x grade and state x year fixed
effects, SE clustered by 2013 CBSA (county outside CBSAs), as in Phase 1. Re-read at the end of the session (the file is being extended by
another agent; rerun the script after it changes).

1. Continuous dose. Each measure is interpolated linearly to the survey spring (year + 0.25; the nearest round is used within half a year at the
   ends, so 2010 surveys get the June 2010 round and 2021 surveys the June 2021 round). Coefficients per +10 pp; `pct_per_within_sd` = coefficient
   x within-county SD of the dose / mean outcome. Samples 2010-2021 and 2010-2019. Minnesota's pre-2013 sadness item (30-day wording) is excluded
   from the sadness runs. Results `bb_dose_results.csv`. Headline (2010-21, all sexes): considered suicide +0.37 (0.10) pp per 10 pp at wireline
   25 Mbps, +0.41 (0.18) at 10 Mbps, +0.62 (0.29) any wireline, +0.21 (0.14) fixed 25/3; sad/hopeless +0.06 (0.19), +0.10 (0.24), -0.27 (0.47),
   +0.15 (0.16); mobile coverage 2010-14: -0.44 (0.23) ideation, -0.64 (0.51) sadness. One within-county SD of the 25 Mbps measure (14 pp) is
   +2.8% of the ideation mean, against Churchill & Johnson's 9.3-16.5% per state SD.
2. AT&T footprint x post-2007, Minnesota. Event-style `value ~ i(year, att, ref=2007) | county x grade + year`, pooled `att x post` (post = 2010+),
   Myers-Hooper binary, Verizon comparison, pre-trend slope 1998-2007, long differences (2007->2013, 2007->2019, placebos 2001->2007 and
   1998->2004; unweighted and 2000-population weighted; with metro and log-population controls). Minnesota has no sample sizes in the county
   tables, so the panel regressions are unweighted. Results `bb_att_event_mn.csv`, `bb_att_did_mn.csv`, `bb_att_longdiff_mn.csv`. Headline:
   considered suicide (grade 9) att x post -1.59 (0.82) pp, binary -1.66 (0.90); attempted -0.72 (0.43); 30-day sadness -1.02 (0.45); hopeless
   -0.94 (0.51); nervous -0.60 (0.48); stress -0.81 (0.77); pre-trends -0.24 to +0.15 pp per wave; event coefficients for ideation 2010 -1.03,
   2013 -0.58, 2016 -1.52, 2019 -1.80 (SE about 1.4). Long difference 2007->2019 on ideation -1.52 (0.98) weighted, +0.37 (1.53) with metro and
   log-population controls. Differential trend 2010-2019 pooled over six states (`bb_att_trend_states.csv`): -2.01 (0.97) pp per decade for
   ideation, -0.41 (3.35) for sadness. Maine (16 counties) cross-sectional correlations between -0.2 and +0.1.
3. Youth suicide. County: change in the average annual rate between pooled periods on att (and on 2010-14 broadband growth), state FE, youth
   population weights; three samples (reportable counties; all counties with suppressed counts set to 5; counties with 50,000+ youths a year).
   The reportable sample is dominated by small counties with zero deaths and the imputed sample by the imputation; the large-county sample has
   no AT&T variation (165 counties, mean share 0.97). Results `bb_suicide_results.csv`, `bb_suicide_desc.csv`, `bb_suicide_samples.csv`; the
   2003-07 -> 2013-17 AT&T coefficient is +1.23 (0.48) per 100,000 on reportable counties and -2.04 (0.63) imputed. State level (the fallback):
   `rate ~ att_state x post-2007 | state + year`, 1999-2023, youth-population weights, SE by state, plus 1999-2007 pre-trend, event coefficients
   and long differences (`bb_suicide_state_results.csv`, `bb_suicide_state_event.csv`), plus a version controlling the state's non-metro
   population share x post-2007, because AT&T's 2010 footprint is an urbanicity proxy and the 2010s youth-suicide rise was concentrated in
   rural states. Headline (all youth, 1,162 state-years, 50 states): att_state x post-2007 -1.87 (0.73) deaths per 100,000 per year, i.e.
   youth suicide rose less where AT&T coverage was higher; pre-trend +0.30 (1.24) per decade, placebo change 1999-02 -> 2003-07 +0.17 (0.64);
   with the non-metro share x post control the AT&T term is +0.68 (1.64) and the non-metro term +3.36 (1.92). Boys -2.71 (1.07) -> +0.54 (2.32)
   with the control; girls +0.03 (0.83) (most girl state-years suppressed). The AT&T "effect" on youth suicide is the rural suicide trend.

## 4. Literature (one row each; numbers checked against the abstracts on 2026-10-24)

- Myers & Hooper 2026, NBER WP 35310 (June 2026, revised October 2026), https://www.nber.org/papers/w35310: public NTIA SBI Dec-2010 AT&T coverage,
  Poisson and synthetic DiD event studies; births 15-19 fall 2.0-9.0%, 20-24 1.5-7.2%, 12-53% of the 2007-11 GFR decline (the report's Part 2 text
  cites 4.5-8.0% and 33-52% from press coverage of the June version; the October abstract gives the ranges above).
- Churchill & Johnson 2026, NBER WP 34614, https://www.nber.org/papers/w34614 (SSRN 6019608): state broadband access from FCC data 2009-2019 and
  National/State YRBS; +9.3-16.5% suicidal ideation per SD, largest for girls. The NBER PDF was not downloadable from this host (403); the
  broadband measure's exact definition comes from The 74's report of the paper (FCC county deployment figures 2009-2019, aggregated to states).
- Johnson & Persico 2024, NBER WP 32517, https://www.nber.org/papers/w32517: county broadband 2000-2008; a 10% rise in access lowers county
  suicides 1.01%, working-age adults, via poverty and unemployment.
- Wang 2026, Journal of Information Economics 4(1), https://doi.org/10.58567/jie04010001: state connections per capita 2006-2023, IV with river/coast
  distance and 1870 rail; one SD (0.06) lowers the 15-24 crude suicide rate by 4.97 per 100,000.
- Donati et al. 2025, Arenas-Arroyo et al. 2025, Golin 2022, McDool et al. 2020, Guo 2023: already summarized in the report; rows in the part
  give identifying variation and direction only.
- Not found: any published U.S. study pairing NBM/Form 477 county availability with YRBS or NSDUH adolescent outcomes at county level, or a
  county-level "internet and suicide" paper for adolescents beyond the two above (searches 2026-10-24).

## 5. Gaps and caveats

- The county youth suicide test is defeated by suppression (counts under 10 in 5-year 10-19 cells); a restricted-use NVSS file or the NCHS
  Research Data Center would be needed. The state series is unsuppressed but has 51 units and little AT&T variation outside the rural West.
- The NBM-to-FCC seam (2014) mixes validated SBI polygons with FCC self-reports; county x grade fixed effects absorb a level shift but not a
  county-specific one. The Analyze tiers are any-technology; wireline tiers exist only for Dec 2010, Dec 2013, Jun 2014 and the FCC rounds, and
  the 2011-2013 values of `wireline_ge10/ge25` are interpolated across a three-year gap.
- Mobile coverage ends in June 2014 (FCC mobile shapefiles not processed); the June 2010 AT&T share is incomplete and is a check only.
- Minnesota's county tables are grade 9 only for the suicide items after 2010 and have no sample sizes; the 30-day sadness item ends in 2010.
- The 2008-12 by-sex WONDER county request timed out; the 1999-2002 period was pulled for all sexes only.
