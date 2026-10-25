# State youth surveys: county / district-level depression and suicidal-ideation series (Phase 1; Phase 2 additions 2026-10-24)

Compiled 2026-09-16. Panel: `data/extracts/state_surveys/state_survey_county_panel.csv`
(columns: state, geography_type, geography_name, geography_fips, year, grade_or_age, sex, item, value_pct, n, source_url, note).
Per-state extracts sit next to it (`mn_mss_county.csv`, `wa_hys_county.csv`, `ca_chks_county.csv`, `me_miyhs_county.csv`,
`pa_pays_county.csv`, `il_iys_county.csv`); rebuild with `uv run python scripts/download/state_surveys/parse_<st>.py` (California: `parse_ca.py` then `parse_ca_calschls.py`) then `combine.py`.
Raw downloads: `data/external/state_surveys/<st>/` (README there). Download scripts: `scripts/download/state_surveys/{wa,pa,me,il,ca_calschls}_download.py`,
kidsdata via headless Chromium `scratchpad/kd_download.py` (kidsdata.org and health.state.mn.us HTML pages sit behind Cloudflare /
bot filters; the MDH .xlsx files and AskHYS endpoints are directly fetchable).

Item codes used (beyond the target list, extra codes are kept so wording differences are never silently pooled):
`sad_hopeless` (YRBS 2-week sad/hopeless, except MN 1998-2010, see below), `depressed_2wk` (PHQ-2 item 2), `anhedonia_2wk` (PHQ-2 item 1),
`considered_suicide`, `planned_suicide`, `attempted_suicide`, `suicide_attempt_injury`, `self_harm`, `screen_time_3plus`, `social_media_daily`,
MN-only 30-day items `stress_high`, `hopeless_30d`, `nervous_30d`; PA-only `depressed_sad_most_days`, `mental_health_good`, `life_not_worth_it`,
`no_good_at_all`, `failure`.

## Minnesota Student Survey (MSS) -- 87 counties + 51 community health boards + state, 1998-2019
Source: MDH "Minnesota Student Survey selected single-year results by state, county and community health board, 1998-2019" (XLS, 2020),
https://www.health.state.mn.us/data/mchs/surveys/mss/docs/singleyear/msssingleyr2019.xlsx (kept in data/external/state_surveys/mn/).
Sheet `Template 4` (Section 4 Mental Health) holds the county x indicator x year x grade matrix; regular public schools only; counties with a
single participating district are included; suppressed cells are "--". Grades: 6/9/12 through 2010; 5/8/9/11 from 2013 (grade 5 not asked MH items).
Wording by era (all "percent who ..."):
- 1998-2010 Q51 `sad_hopeless`: "felt sad all or most of the time in the last 30 days" -- NOT the YRBS 2-week item; do not splice with 2013+ items.
- 1998-2010 Q52 `hopeless_30d`: felt discouraged or hopeless (extremely so / quite a bit), last 30 days. Q53 `nervous_30d`; Q50 `stress_high`
  "felt under great stress or pressure (almost more than I could take)" -- general, not school-specific.
- 1998-2010 Q54b `considered_suicide`: "had suicidal thoughts in the last year"; Q54c `attempted_suicide`: "tried to kill self in the last year".
- 2013, 2016 Q61b `considered_suicide`: "seriously considered attempting suicide during the last year"; Q62 `attempted_suicide` (the second block
  in the workbook is mislabelled "Q61b" in the header row but the lookup-sheet formulas and the magnitudes identify it as attempted suicide).
- 2016, 2019 P50b `depressed_2wk`: PHQ-2 "bothered by feeling down, depressed or hopeless over the past two weeks" (% more than half the days or
  nearly every day); P50a `anhedonia_2wk` likewise. 2019 P52b/P53b considered/attempted suicide; Q60/P51 `self_harm`.
- "Long-term mental health problem" and the 2016+ screen-time items are NOT in the trends workbook (only in the MDE interactive tables).
Gap (re-checked 2026-10-24): the 2022 and 2025 county tables are still not obtainable from this host. MDE's MSS page
(https://education.mn.gov/MDE/dse/health/mss/) says "State, county and district results for 2013, 2016, 2019, 2022, and 2025 are
available in online interactive reports (https://pub.education.mn.gov/MDEAnalytics/DataTopic.jsp?TOPICID=242) and downloadable PDF
tables (https://pub.education.mn.gov/MDEAnalytics/DataTopic.jsp?TOPICID=11)". Both WebFOCUS pages open as an empty shell whose report
frame (`pub.education.mn.gov/ibi_apps/WFServlet?IBIF_ex=mdea_ddl_topic_select_PAGELAUNCH&TOPICID=11`) is redirected to a Radware
bot-manager hCaptcha (`validate.perfdrive.com`) in headless Chromium (tried once, stopped at the CAPTCHA as instructed). The MSS site
`https://mss.mn.gov/MSS/` (index, `/data/`, `/data/dataqual/` "submit a MSS data request") answers every URL with a Radware challenge
page to curl, and `https://www.health.state.mn.us/data/mchs/surveys/mss/statewidetables.html` returns 403. What a request should ask
for: the 2022 and 2025 MSS county tables (all 87 counties plus the community health boards) for grades 8, 9 and 11, for the PHQ-2 items
(down/depressed/hopeless and little interest, % more than half the days or nearly every day), long-term mental health problem,
seriously considered suicide and attempted suicide (past 12 months), self-harm, and the 2022/2025 screen-time and social-media items,
by sex, in the layout of the 2019 "single-year results by state, county and community health board" workbook (`Template 4`), so that
parse_mn.py extends without change; contacts: mde.studentsurvey@state.mn.us (MDE), health.stats@state.mn.us (MDH), or the request
form at https://mss.mn.gov/MSS/data/dataqual/ from a browser that can pass the challenge. Minnesota matters because its 2024-25
district-policy mandate makes the 2025 MSS the first post-policy county wave in any of these surveys. The 2022 MDH mental-health
crosstab workbook (metro vs Greater Minnesota only) is saved as mn/msscrosstabs2022.xlsx.

## Washington Healthy Youth Survey (HYS) -- 38-39 counties + 9 ESDs, 2010-2025 (biennial; 2020 wave ran in 2021)
Source: AskHYS frequency reports, https://www.askhys.net/SurveyResults/FrequencyReports; direct endpoint
`GetReport?year=Y&reportLevel=<id>&reportLable=<Excel|Multi-grade (6/8/10/12)|Grade 10>` (ids differ by year; see wa/index.csv).
Formats: 2023/2025 Excel (one workbook per geography, sheet per grade, one row per response option, weighted % and 95% CI, N);
2014-2021 multi-grade PDFs; 2012 single-grade PDFs (grades 8/10/12); 2010 Word .doc (converted with soffice to wa/doc2010/*.txt).
Grades 8, 10, 12 (12th dropped statewide from 2023, so 2023/2025 have 6/8/10 only; grade 6 not asked the YRBS items).
Wording (stable 2010-2025): `sad_hopeless` "During the past 12 months, did you ever feel so sad or hopeless almost every day for two weeks or more in a
row that you stopped doing some usual activities?"; `considered_suicide` "...did you ever seriously consider attempting suicide?";
`attempted_suicide` = 100 - % "0 times" on "how many times did you actually attempt suicide?".
Screen items: 2023/2025 h128 "On an average school day, how many hours do you spend in front of a TV, computer, smart phone, or other electronic
device watching shows or videos, playing games, accessing the Internet, or using social media?" -> `screen_time_3plus` = 3 + 4 + 5+ hours;
h129 social media frequency -> `social_media_daily` = about once a day or more. (2018/2021 screen items exist in the PDFs under different wording
-- "hours ... playing video or computer games or using a computer for something that is not school work" -- not extracted.)
County estimates are weighted only where the county sample is a census/representative sample; the reports flag small samples with "**".
2018 `considered_suicide` and 2014 `sad_hopeless` initially parsed sparsely because the multi-grade PDF interleaves the column header inside the
question text; the parser strips those header lines.

## California Healthy Kids Survey (CHKS) via kidsdata.org -- 55 counties + state, 2011-13 .. 2017-19 windows
Source CSV exports (headless-browser "All data for this indicator"): topics 662/387 (chronic sad/hopeless by grade, by gender x grade) and
1825/1826 (considered suicide). Files: ca/kidsdata_topic{662,387,1825,1826}_all.csv.
Wording: `sad_hopeless` "During the past 12 months, did you ever feel so sad or hopeless almost every day for two weeks or more that you stopped
doing some usual activities?"; `considered_suicide` "...seriously consider attempting suicide?" (grades 9, 11, non-traditional only).
Grades 7, 9, 11, NT; two-school-year pooled windows; `year` = end year of the window (2013 = 2011-12 + 2012-13). Estimates are WestEd
county aggregates of all participating schools (not necessarily representative of the county).
kidsdata.org still ends at 2017-19 for topics 662/387/1825/1826 (checked 2026-10-24 with headless Chromium: the available windows are
2011-13 .. 2017-19). Phase 2 therefore adds the WestEd county "Main Report" PDFs from the CalSCHLS report search
(https://calschls.org/reports-data/search-lea-reports/; a plain POST `sbmt=1&county=<1..58>&county_rep=County+Reports` lists one row per
county report with its window and a PDF on data.calschls.org, e.g. `Alameda_County_2123_Sec_CHKS.pdf`), downloaded by
`ca_calschls_download.py` into ca/calschls/ (windows 2015-17, 2017-19, 2019-21, 2021-23 and 2023-25: 52, 52, 48, 52 and 48 county reports, 254 PDFs; `index.csv` lists all 431 county
report rows the form returns) and parsed by `parse_ca_calschls.py`. Tables used: "Chronic Sad or Hopeless Feelings, Past 12 Months" and
"Seriously Considered Attempting Suicide, Past 12 Months" (% Yes, grades 7/9/11/NT; the 2017-19 reports number them A8.4/A8.5, the
2019-21 and later reports A7.1/A7.2) and "Social and Emotional Health by Gender" (Male/Female rows by grade, 2019-21 onward; the non-binary
and "something else" rows are not kept). Values are integers (the reports round), read by x-position so that a blank or dashed cell
(fewer than 10 respondents) leaves the grade missing rather than shifting columns. The 2019-21 reports also give grade 7 for considered
suicide, which kidsdata lacks for earlier windows, so 23_state_surveys.py keeps grades 9 and 11 for that item. Where a report window
overlaps kidsdata (2015-17 and 2017-19) the kidsdata row is kept and the report value written to
`data/compiled/state_surveys/ca_chks_source_overlap.csv`: the two sources agree within rounding (mean |difference| 0.25 pp, maximum
0.5 pp over the overlapping cells). Same caveat as before: county aggregates of participating schools, not county-representative, and
the 2019-21 window straddles remote instruction (the reports' "Instructional Model" tables show the mix).
2023-25 is the newest window; the statewide mandate (AB 3216, district policies by 2026-07-01) applies only from 2026-27, so all
California waves are pre-ban.

## Maine Integrated Youth Health Survey (MIYHS) -- 16 counties, high school (9-12), 2009-2023 biennial
Source: https://www.maine.gov/miyhs/<year>-results ; county "High School Detailed Tables" (2009, 2011 PDF; 2015-2023 SAS HTML saved as .xls plus PDF)
and county "High School Report" core reports (2013; and counties without detailed tables in 2021/2023). Detailed tables give Total / Female / Male
x Total and Grade 9-12 rows with % , 95% CI and weighted N answering yes (N stored in `n`). Core reports give the county total (9-12, all) for the
survey year and the previous wave (used only where the detailed tables are missing).
Wording: hn42 `sad_hopeless` YRBS 2-week item (% yes); hn43/44 `considered_suicide`; `attempted_suicide` (% 1+ times) 2017-2021 only;
`screen_time_3plus` 2017-2021 = the MIYHS non-school screen-time item (3+ hours; see hn code in the report). Middle-school (7-8) county tables also
exist on the same pages and were downloaded only for HS; MS not parsed. 2021 was administered in fall 2021 (pandemic shift).
Some counties lack a public county report in a given year (small or non-participating; e.g. Aroostook/Hancock/Kennebec 2021).

## Pennsylvania Youth Survey (PAYS) -- 60 county profile reports, 2015-2025 (biennial, fall of odd years)
Source: PCCD county profile reports (Bach Harrison PDFs) for 2019, 2023 and 2025, https://www.pa.gov/agencies/pccd/programs-and-services/juvenile-justice-and-delinquency-prevention/pays
(2019-pays/2019-pays-county-reports/*.pdf, 2023-pays/2023-pays-county-reports/*.pdf, 2025-pays/2025-county-reports/2025-<county>-county-profile-report.pdf;
the 2025 links are in the page's "2025 County Reports" accordion, in the server-rendered HTML, so no browser was needed). Each report's
"Suicide risk" table lists County Y-4, County Y-2, County Y and State Y for grades 6/8/10/12/All, so the three editions cover 2015-2025
(values for 2021 and 2023 are taken from the 2025 edition where both exist). The 2025 edition's "Mental health concerns" table lists the six
items in a different column order (overall mental health good, depressed/sad most days, life not worth it, no good at all, failure,
self-harm; 2023: self-harm first), so parse_pa.py reads the order from the table header instead of assuming it. Edition overlap
(`data/compiled/state_surveys/pa_pays_report_overlap.csv`): the 2021 and 2023 county and state values printed in the 2025 reports are
compared with the 2023 reports' values at run time: all 5,586 overlapping 2021/2023 cells (60 counties + state, 5 grades, 11 items) are
identical in the 2023 and 2025 editions. Between the 2019 and 2023 editions 844 of 1,120 overlapping cells are identical and the 276 that
differ are all `suicide_attempt_injury` (the 2023 edition recalculated earlier years on the attempters-only denominator; mean difference
25 pp), so that item is not comparable across editions and the later edition is kept.
Items: `sad_hopeless` "So sad stopped doing usual activities" (YRBS wording in questionnaire), `considered_suicide`, `planned_suicide`,
`attempted_suicide` (yes/no item from 2023, previously number of times), `suicide_attempt_injury` (2023+: denominator = attempters);
2023 and 2025 reports also give the "Mental health concerns" table: `self_harm`, `depressed_sad_most_days` ("In the past 12 months have
you felt depressed or sad MOST days, even if you feel OK sometimes?"), `life_not_worth_it`, `no_good_at_all`, `failure`, and
`mental_health_good` (2023+; the 2025 report footnote mis-dates its introduction to 2025). Grade "6-12" = all grades. State rows
(geography_type=state) included. PAYS county samples are the participating schools (not weighted to the county); PCCD reports 267,000+
participants statewide in 2025. Philadelphia: the 2019 and 2023 editions publish only a "charter schools only" Philadelphia report; the 2025 edition calls the same
series "Philadelphia County" (its 2021 and 2023 columns equal the 2023 edition cell for cell, 85 of 85), so combine.py gives the series one
name and a note. Pennsylvania has no statewide phone mandate (2024 pouch-grant programme only; a House bill in 2026), so
its 2025 wave is a no-mandate comparison for the post-2021 downturn. 2011/2013 county reports are not on the current site.

## Illinois Youth Survey (IYS) -- 53-82 counties, 2018-2024 (biennial)
Source: county frequency-report PDFs, https://iys.cprd.illinois.edu/results/county (2024) and .../results/archives (2018, 2020, 2022);
files il/iys_<year>_<county>.pdf. Table "(6) Mental, Social and Physical Health": `sad_hopeless` YRBS 2-week item and `considered_suicide`
(grades 10/12 only), percent rounded to integers, N = number answering yes, columns 8th/10th/12th (a county report is published only for grades
with enough participating schools). Not weighted to the county. The county "snapshot" workbooks 2010-2024 (il/*.xlsx) hold substance use only.
Gap: 2008-2016 county reports are no longer linked on the rebuilt IYS site (the archive pages all serve the same 2018+ list); would need Wayback
or a CPRD request.

## Not done / quick checks
- Iowa Youth Survey: county reports (2005-2021) are on Iowa Publications Online (publications.iowa.gov), which rejects requests from this host
  ("Request Rejected") and the old iowayouthsurvey.idph.iowa.gov site is dead; the HHS page links only state and judicial-district PDFs.
- Colorado Healthy Kids Colorado: results are published by health-statistics region (21 regions) in CDPHE dashboards/PDFs; not fetched.
- Oregon Student Health Survey / Oregon Healthy Teens: county PDFs exist on oregon.gov (2019, 2020, 2022); not fetched.
- Wisconsin YRBS: DPI publishes county-level only through CESA/regional and district dashboards; Vermont YRBS: supervisory-union reports (PDF)
  on healthvermont.gov; neither fetched.

## Coverage (county rows only; state/CHB/ESD rows also present)

| state | item | years | counties | rows |
|---|---|---|---|---|
| CA | considered_suicide | 2013 2015 2017 2019 2021 2023 2025 | 55 | 2946 |
| CA | sad_hopeless | 2013 2015 2017 2019 2021 2023 2025 | 55 | 3451 |
| IL | considered_suicide | 2018 2020 2022 2024 | 75 | 407 |
| IL | sad_hopeless | 2018 2020 2022 2024 | 82 | 635 |
| ME | attempted_suicide | 2017 2019 2021 | 16 | 594 |
| ME | considered_suicide | 2009 2011 2013 2015 2017 2019 2021 2023 | 16 | 1479 |
| ME | sad_hopeless | 2009 2011 2013 2015 2017 2019 2021 2023 | 16 | 1486 |
| ME | screen_time_3plus | 2017 2019 2021 | 16 | 645 |
| MN | anhedonia_2wk | 2016 2019 | 87 | 502 |
| MN | attempted_suicide | 1998 2001 2004 2007 2010 2013 2016 2019 | 87 | 2051 |
| MN | considered_suicide | 1998 2001 2004 2007 2010 2013 2016 2019 | 87 | 2051 |
| MN | depressed_2wk | 2016 2019 | 87 | 502 |
| MN | hopeless_30d | 1998 2001 2004 2007 2010 | 87 | 1291 |
| MN | nervous_30d | 1998 2001 2004 2007 2010 | 87 | 1291 |
| MN | sad_hopeless | 1998 2001 2004 2007 2010 | 87 | 1291 |
| MN | self_harm | 2013 2016 2019 | 87 | 760 |
| MN | stress_high | 1998 2001 2004 2007 2010 | 87 | 1291 |
| PA | attempted_suicide | 2015 2017 2019 2021 2023 2025 | 60 | 1747 |
| PA | considered_suicide | 2015 2017 2019 2021 2023 2025 | 60 | 1747 |
| PA | depressed_sad_most_days | 2019 2021 2023 2025 | 60 | 1196 |
| PA | failure | 2019 2021 2023 2025 | 60 | 1196 |
| PA | life_not_worth_it | 2019 2021 2023 2025 | 60 | 1196 |
| PA | mental_health_good | 2023 2025 | 60 | 599 |
| PA | no_good_at_all | 2019 2021 2023 2025 | 60 | 1196 |
| PA | planned_suicide | 2015 2017 2019 2021 2023 2025 | 60 | 1747 |
| PA | sad_hopeless | 2015 2017 2019 2021 2023 2025 | 60 | 1747 |
| PA | self_harm | 2019 2021 2023 2025 | 60 | 1196 |
| PA | suicide_attempt_injury | 2015 2017 2019 2021 2023 2025 | 60 | 1746 |
| WA | attempted_suicide | 2010 2012 2014 2016 2018 2021 2023 2025 | 38 | 787 |
| WA | considered_suicide | 2010 2012 2014 2016 2018 2021 2023 2025 | 38 | 799 |
| WA | sad_hopeless | 2010 2012 2014 2016 2018 2021 2023 2025 | 38 | 799 |
| WA | screen_time_3plus | 2023 2025 | 37 | 239 |
| WA | social_media_daily | 2023 2025 | 37 | 239 |

Total rows 44704; county rows 40849; geography types {'county': 40849, 'CHB': 2772, 'esd': 735, 'state': 348}.
