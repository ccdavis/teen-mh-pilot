# HBSC published trend data (country x wave x sex x age)

Compiled 2026-09-16. Output: `data/extracts/hbsc/hbsc_published_trends.csv` (12,489 rows) plus
`data/extracts/hbsc/hbsc_published_trends_pdf_crosscheck.csv` (3,957 rows; PDF-extracted 2014/2018 values kept
only for validation). Scripts: `scripts/hbsc/` (`chart_extract.py`, `build_published.py`, `parse_2001.py`,
`parse_1998.py`, `parse_1994.py`, `build_final.py`; intermediate `data/extracts/hbsc/_pdf_chart_raw.csv`). Raw downloads: `data/external/hbsc/`.

## Columns
`country, wave, year_end, age, sex (boy|girl|all), item, value_pct, source_doc, source_page_or_table, note`.
`country = "HBSC average"` rows carry the cross-national averages printed in each source (unweighted mean of
participating countries; the set of countries differs by wave, so averages are not a consistent panel).

## Items
| item | definition | waves |
|---|---|---|
| `schoolwork_pressure` | feel pressured by schoolwork "some" or "a lot" (%) | 2001/02 - 2021/22 |
| `schoolwork_pressure_a_lot` | pressured "a lot" only (1997/98 Fig. 5.8) - NOT comparable with the above | 1997/98 |
| `multiple_complaints` | 2+ of the 8 HBSC-SCL complaints more than once a week (%) | 2001/02 - 2021/22 |
| `high_life_satisfaction` | Cantril ladder >= 6 (%) ("above the middle" in 2001/02) | 2001/02 - 2013/14 |
| `life_satisfaction_mean_0_10` | mean Cantril score (not a %) - the only LS statistic published for 2017/18 and 2021/22 | 2013/14 - 2021/22 |
| `like_school` | like school "a lot" (%) | 1997/98 - 2021/22 |
| `feel_low_weekly`, `feel_nervous_weekly` | complaint more than once a week (%) | 2013/14 - 2021/22 |
| `feel_low_at_least_weekly` | "at least once a week" (1997/98 Fig. 3.1) / "once a week or more" (1993/94 Fig. 6.10) - NOT comparable with `feel_low_weekly` | 1993/94, 1997/98 |
| `problematic_social_media` | Social Media Disorder Scale, 6+ of 9 items (%) | 2017/18, 2021/22 |
| `intense_social_media` | "almost all the time throughout the day" online contact with at least one friend category (%) | 2017/18, 2021/22 |

## Coverage (countries with boy/girl values, excluding HBSC average)
| item | 93/94 | 97/98 | 01/02 | 05/06 | 09/10 | 13/14 | 17/18 | 21/22 |
|---|---|---|---|---|---|---|---|---|
| schoolwork_pressure | - | (27, "a lot") | 35 | 41 | 39 | 42 | 46 | 45 |
| multiple_complaints | - | - | 35 | 41 | 39 | 42 | 44 | 44 |
| high_life_satisfaction | - | - | 34 | 39 | 39 | 42 | - | - |
| life_satisfaction_mean | - | - | - | - | - | 39 | 39 | 44 |
| like_school | - | 28 | 35 | 41 | 39 | 42 | 46 | 45 |
| feel_low_weekly / nervous | (23, >=weekly) | (28, >=weekly) | - | - | - | 42 | 45 | 44 |
| problematic_social_media | - | - | - | - | - | - | 43 | 43 |
| intense_social_media | - | - | - | - | - | - | 43 | 42 |

United States: 1997/98, 2001/02, 2005/06, 2009/10 (all items available in those reports). Canada, England,
Scotland, Wales, Ireland, Germany, France, Netherlands and the Nordic countries: all waves in which they took part.

## Sources

### HBSC Data Browser (machine-readable; primary source for 2013/14, 2017/18, 2021/22)
`https://data-browser.hbsc.org/` is a WordPress/Svelte site whose front end loads three static CSVs:
`/wp-content/uploads/csvs/data.csv` (country x survey year x age x sex, ~18k rows, 55 measures),
`metadata.csv` (measure definitions/notes) and `FAS.csv` (family-affluence splits). Saved as
`data/external/hbsc/data_browser_data.csv`, `data_browser_metadata.csv`, `data_browser_FAS.csv`.
The site is behind Cloudflare and rejects plain curl; a browser User-Agent string is enough.
Measures used: `sch_pressure`, `sch_satis`, `multihealth`, `d_feellow`, `d_nervous`, `SMPdum`,
`EMC_intensive`, `lifesat_mean`. Browser rows for `HBSC AVERAGE (GENDER)/(TOTAL)` are kept as
`country = "HBSC average"`. `sex = "all"` for countries comes from the browser field `sort_gender`
(both sexes combined; the browser uses it for sorting; unrounded in 2022) - flagged in `note`.
The browser has **no** "high life satisfaction (>=6)" measure, only the mean.
Cite: Health Behaviour in School-aged Children study (2023), Data browser (findings from the 2021/22
international HBSC survey), https://data-browser.hbsc.org.

### International reports (PDF; WHO IRIS bitstreams via the DSpace REST API `/server/api/pid/find?id=hdl:10665/<handle>`)
| wave | file | handle | pages used (PDF index) |
|---|---|---|---|
| 1993/94 | `hbsc_1993_94_health_of_youth.pdf` (King et al. 1996, *The health of youth*; Google-Drive copy linked from hbsc.org) | - | p.107 = printed p.97, Fig. 6.10 (feel low). Text layer unusable; OCR (RapidOCR) of 220-dpi render. No "like school a lot" or schoolwork-pressure by-country figure (Fig. 8.9 is "school is a nice place to be"). |
| 1997/98 | `hbsc_1997_98_health_and_health_behaviour.pdf` (Currie et al. 2000, E67880) | 10665/108253 | p.27 Fig. 3.1 (feel low >= weekly), p.51 Fig. 5.1 (like school a lot), p.64 Fig. 5.8 (pressured a lot). Landscape pages with rotated text; parsed from text flow (male list, female list, country list per age panel; panel order taken from the order of the age labels, verified against coordinates on p.27). |
| 2001/02 | `hbsc_2001_02_young_peoples_health_in_context_1_9789289013727-eng.pdf` (Currie et al. 2004) | 10665/107560 | p.57 Fig. 2.16 (like school), p.61 Fig. 2.19 (pressured), p.72 Fig. 3.2 (2+ complaints), p.73 Fig. 3.3 (LS above middle). One decimal place. Belgium (French) missing for LS. |
| 2005/06 | `hbsc_2005_06_inequalities.pdf` (Currie et al. 2008) | 10665/326503 | like school p.58-59, pressure p.66-67, high LS p.80-81, multiple complaints p.84-85 |
| 2009/10 | `hbsc_2009_10_social_determinants.pdf` (Currie et al. 2012) | 10665/326406 | like school p.65-66, pressure p.73-74, high LS p.91-92, multiple complaints p.95-96 |
| 2013/14 | `hbsc_2013_14_growing_up_unequal.pdf` (Inchley et al. 2016) | 10665/326320 | like school p.67-68, pressure p.75-76, high LS p.91-92, multiple complaints p.95-96 (only high LS used as primary; the rest go to the cross-check file) |
| 2017/18 | `hbsc_2017_18_vol2_key_data.pdf` (Inchley et al. 2020, Spotlight vol. 2) | 10665/332104 | intensive online contact p.45-46, PSMU p.49-50, multiple complaints p.61-62, feel low p.69-70, nervous p.73-74, like school p.129-130, pressure p.131-132 (cross-check only; charts carry 2014 and 2018 columns) |
| 2021/22 | `hbsc_2021_22_vol1_mental_health.pdf` (10665/373201), `vol6_social_media.pdf`, `vol7_social_contexts.pdf` (10665/379486) | | Not used for numbers: the chart text in these PDFs has no Unicode mapping (garbled extraction) and everything in them is in the data browser. Vol. 1 reports mean LS only. |

PDF page numbers above are 1-based PDF page indices (as in `source_page_or_table`), not the printed folio.

### Extraction method for 2005/06-2017/18 charts
Country names and bar-end value labels were pulled with PyMuPDF word coordinates (`scripts/hbsc/chart_extract.py`):
for each right-aligned country label, the two numbers vertically adjacent to it are the girl (upper) and boy (lower)
values. The girl/boy assignment was validated against the data browser: 2018 values match in 1,845 of 1,848
comparable cells (the 3 differences are 1-point rounding), 2014 values match except +/-1-point differences for Austria, Norway, Belgium (Flemish),
Finland, Iceland and Greenland - these look like later data revisions in the browser's 2014 file rather than
extraction errors. The 2005/06 and 2009/10 assignment was checked visually on rendered pages (e.g. 2009/10 p.74:
Turkey 69/68, United States 54/42, Netherlands 31/17; 2005/06 p.67: Turkey 60/61, USA 60/51) and against the
printed HBSC-average rows.

## Caveats
- **Revisions**: the data browser's 2014 numbers are (slightly) revised relative to the 2013/14 report; the browser is
  used as primary for 2014-2022 so that the three recent waves are internally consistent. The original 2013/14 and
  2017/18 report values are in the cross-check file.
- **Definition changes**: `schoolwork_pressure_a_lot` (1997/98) and `feel_low_at_least_weekly` (1993/94, 1997/98) are
  separate item codes because the thresholds differ from later waves. 1993/94 wording is "felt low or depressed".
- **High life satisfaction stops at 2013/14**: from 2017/18 the international reports and browser publish only mean
  Cantril scores. Use `life_satisfaction_mean_0_10` for 2014-2022 or compute >=6 shares from the microdata.
- **Country naming**: harmonised to browser spelling (Czechia, North Macedonia, United States, Belgium (Flemish)/(French),
  Greenland, Russian Federation). "Northern Ireland" appears only in 1993/94 and 1997/98. Germany, France and
  Russia are regional samples in 1993/94 and 1997/98. Belgium (Flemish)/(French) and the UK nations are reported
  separately throughout.
- **HBSC average** rows are simple means over the countries in that wave's report/browser; the country set changes
  (e.g. central Asian countries join in 2017/18+; United States leaves after 2009/10; Israel, Turkey and Russia are
  absent in some waves).
- **sex = all**: only available as browser `sort_gender` (2014-2022) and as the printed "HBSC average (total)".
  Older reports print boy/girl only.
- **Rounding**: 2005/06 onwards values are integers as printed; 2001/02 has one decimal; browser 2022 `sort_gender`
  totals are unrounded.
- **Not found / not extracted**: 2021/22 high life satisfaction (not published); 1993/94 schoolwork pressure and
  like-school-a-lot (no by-country figure); 1997/98 multiple complaints and life satisfaction (not in that report);
  a 2021/22 data annex in Excel (none published - the browser CSVs are the machine-readable equivalent).
- OCR (1993/94) tokens all had confidence >= 0.94; one row (Denmark, age 11) was transcribed manually.
