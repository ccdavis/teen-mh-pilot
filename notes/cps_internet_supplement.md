# CPS Computer and Internet Use Supplement (NTIA) – IPUMS CPS extract

Source: IPUMS CPS (cps.ipums.org), the monthly samples carrying the Computer and Internet Use Supplement; household variables attached to each person record.
Extract SQL: `scripts/extract/cps_internet_supplement.sql` (duckdb, against the extract converted to parquet). Sanity script: `scripts/analysis/cps_ci_sanity.py` (`uv run python scripts/cps_ci_sanity.py`).
Output: `data/extracts/cps/cps_ci_<sample>.parquet`, one person-level file per sample, uniform schema (columns absent in a year are NULL).
Unweighted code frequencies for every CI item by sample: `notes/cps_ci_code_freqs.csv`.

## Headline caveat: the mobile items are NOT in IPUMS

IPUMS CPS harmonizes only a subset of the supplement (variable group `compint_compint`, checked on the website and in `tt_samplevariables`).
None of the 2011+ NTIA items on **mobile/cellular data plans at home, smartphone/tablet ownership or use, internet use on a mobile device,
or social networking** are harmonized, and the parquet files carry no unharmonized (`UH_*`) supplement columns either (the `UH_` columns are all
basic-monthly items). So a mobile-internet adoption measure cannot be built from this server's IPUMS data. For that you need the raw NTIA/Census
public-use files (NTIA "Download NTIA Internet Use Survey Datasets", https://www.ntia.gov/page/download-ntia-internet-use-survey-datasets;
CSV/Stata/R with Census tech docs; sample code at https://github.com/ntiadc/ntia-internet-use-survey). In those files the relevant raw items
are, from memory of the Census tech docs (verify against each wave's record layout): `HEMOBDAT` (household uses a mobile data plan to go online at home, 2015+),
`HEMPHONE`/`PEMPHONE` (smartphone in household / person uses smartphone, 2015+), `PENETUSE`-type person "uses internet anywhere" item, `PESOCIAL`
(social networking, 2013+), and in 2011-2013 `HEMOBILE`/`PEMOBIL` style items for "mobile device" access.
The IPUMS extract here still provides the state/metro identifiers, weights, and the household home-internet and person-use items, so it can serve as the
frame and for a home-internet (any connection) measure, but not for a mobile-specific measure.

## Samples carrying the supplement (2009-2023)

Identified from `tt_samplevariables` (samples with any `CI*` item; CITIZEN excluded) and confirmed by DESCRIBE on the parquet:

| sample | month | notes |
|---|---|---|
| cps2009_10s | Oct 2009 | Internet Use supplement (part of Oct school enrollment); items CINETHH, CICONTYP, CINTUSE, CIHSNET |
| cps2010_10s | Oct 2010 | household-level only (all HH members identical); CINETHH, CICONTYP, CIHHCOMP, CIUSECMP, CINONET, CINONTMO, CINT*H items |
| cps2011_07s | Jul 2011 | first NTIA-designed wave; person items, CIPWT introduced |
| cps2012_10s | Oct 2012 | household-level only (all HH members identical) |
| cps2013_07s | Jul 2013 | asked ONLY of MISH 2-4 and 6-8 (half sample); MISH 1 and 5 are NIU on every item |
| cps2015_07s | Jul 2015 | NTIA wave; only 11 CI vars harmonized |
| cps2017_11s | Nov 2017 | " |
| cps2019_11s | Nov 2019 | " |
| cps2021_11s | Nov 2021 | " |
| cps2023_11s | Nov 2023 | " ; METAREA (1990-based) discontinued, use METFIPS |

`cps2014_10s` carries a non-zero CISUPPWT in metadata/parquet but no supplement items (it is the Oct school-enrollment sample); excluded.
Expected months matched exactly (Oct 2009, Jul 2011, Oct 2012, Jul 2013, Jul 2015, Nov 2017/2019/2021/2023) plus Oct 2010.

## Variable availability (harmonized CI items; x = present/non-null in extract)

Household-type items: CINETHH (HH has internet connection, 2009-10; universe = HHs where respondent uses internet/computer, so NIU!=no-internet),
CICONTYP, CIHHCOMP, CIUSECMP, CINUMCMP, CICOMPYR, CIHSNET, CINONET, CINONTMO, CISTPNET, CINTOUTH/CINTLIBH/CINTOTHHH/CINTSCHH (HH-level "any member uses internet outside home / at library / other house / school", 2010 and 2012).
Person items: CINTUSE (uses internet anywhere, 2009 only), CINETHP (accesses internet at home, 2011+; in 2015+ universe is all civilians 3+, effectively the HEINHOME household item), CINTOUT (uses internet outside home, 2013+),
CINTOTHH, CINTLIB, CINTSCH (locations), CIEMAIL, CINTJBSR, CINTPHON, CIHFORWK, CINTFUN, CIPRIV2 (random-respondent items, weight with CIPWT; age 15+ in practice).
No item covers mobile devices, data plans, smartphones, or social networking.

## Availability matrix (non-null in sample)

| var       | cps2009_10s   | cps2010_10s   | cps2011_07s   | cps2012_10s   | cps2013_07s   | cps2015_07s   | cps2017_11s   | cps2019_11s   | cps2021_11s   | cps2023_11s   |
|:----------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|
| CICOMPYR  |               |               | x             |               |               |               |               |               |               |               |
| CICONTYP  | x             | x             |               |               |               |               |               |               |               |               |
| CIEMAIL   |               |               | x             | x             | x             | x             | x             | x             | x             | x             |
| CIHFORWK  |               |               | x             | x             | x             | x             | x             | x             | x             | x             |
| CIHHCOMP  |               | x             |               |               |               |               |               |               |               |               |
| CIHSNET   | x             | x             | x             | x             | x             |               |               |               |               |               |
| CINETHH   | x             | x             |               |               |               |               |               |               |               |               |
| CINETHP   |               |               | x             | x             | x             | x             | x             | x             | x             | x             |
| CINONET   |               | x             | x             | x             | x             |               |               |               |               |               |
| CINONTMO  |               | x             | x             | x             | x             |               |               |               |               |               |
| CINTFUN   |               |               | x             | x             | x             |               |               |               |               |               |
| CINTJBSR  |               |               | x             | x             | x             | x             | x             | x             | x             | x             |
| CINTLIB   |               |               | x             |               | x             | x             | x             | x             | x             | x             |
| CINTLIBH  |               | x             |               | x             |               |               |               |               |               |               |
| CINTOTHH  |               |               | x             |               | x             | x             | x             | x             | x             | x             |
| CINTOTHHH |               | x             |               | x             |               |               |               |               |               |               |
| CINTOUT   |               |               |               |               | x             | x             | x             | x             | x             | x             |
| CINTOUTH  |               | x             |               | x             |               |               |               |               |               |               |
| CINTPHON  |               |               | x             | x             | x             | x             | x             | x             | x             | x             |
| CINTSCH   |               |               | x             |               | x             | x             | x             | x             | x             | x             |
| CINTSCHH  |               | x             |               | x             |               |               |               |               |               |               |
| CINTUSE   | x             |               |               |               |               |               |               |               |               |               |
| CINUMCMP  |               |               | x             | x             |               |               |               |               |               |               |
| CIPRIV2   |               |               | x             |               |               |               |               |               |               |               |
| CISTPNET  |               |               | x             | x             | x             |               |               |               |               |               |
| CIUSECMP  |               | x             |               |               |               |               |               |               |               |               |

Value codes (all items): 1 = No, 2 = Yes, 97 = Don't know (CIEMAIL/CINTJBSR/CINTPHON), 98 = No response, 99 = NIU. CICONTYP: 1 dial-up, 2 faster, 3 both, 99 NIU.
CINUMCMP: 0,1,2,3(=3+),98,99. CIHSNET/CINONET/CISTPNET: reason codes (see `tt_variable_labels`; 99 NIU).

## Weights and scaling

All weights are stored as integers with 4 implied decimals (`decim`=4 in `variables`): WTFINL, HWTFINL, CISUPPWT, CIPWT. The extract divides by 10,000, so
weights are in persons/households. Check: sum(WTFINL) = sum(CISUPPWT) = 302.2M (2009) ... 331.0M (2023) = civilian non-institutional population; sum(HWTFINL) over
PERNUM=1 = 119-133M households. CISUPPWT equals WTFINL in every sample here (IPUMS notes: supplement weights equal basic weights; children are included).
CIPWT (2011+) is the random-respondent weight: non-zero for exactly one person age 15+ per household (2011-12: 53.5k HHs; 2013+: only MISH 2-4/6-8 HHs in 2013, ~41-43k HHs after);
sums to 195-250M = population 15+. Use CISUPPWT for CINETHP/CINTOUT/location items and household items; use CIPWT (restricted to CIPWT>0) for CIEMAIL/CINTJBSR/CINTPHON/CIHFORWK/CINTFUN.

## Geography

STATEFIP (51 codes incl. DC). METFIPS = CBSA FIPS code (99998 = unidentified/nonmetro, 99999 = missing); 260-295 identified codes, ~81-83% of population in an identified
metro. METAREA (1990-based IPUMS code, 9997/9998/9999 = other/NIU/missing) exists through 2021 but not in cps2023_11s (NULL there); use METFIPS. The METFIPS code
set changes in 2015 (264 -> 295 codes) and again in 2017 (260) with CBSA delineation updates. COUNTY (FIPS, 0 = not identified) is identified for ~43-45% of persons.
Also included: METRO (metro/central-city status), CBSASZ (CBSA size class), INDIVIDCC, FAMINC, HHTENURE (missing 2017+), MISH, CPSID, CPSIDP.

## Sanity checks (national, weighted)

## Rows and weighted totals

| SAMPLE      |   YEAR |   MONTH |   n_persons |   n_hh |   pop_wtfinl_m |   pop_cisuppwt_m |   pop_cipwt_m |   n_cipwt_pos |   hh_hwtfinl_m |
|:------------|-------:|--------:|------------:|-------:|---------------:|-----------------:|--------------:|--------------:|---------------:|
| cps2009_10s |   2009 |      10 |      134675 |  54324 |         302.22 |           302.22 |        nan    |             0 |         119.36 |
| cps2010_10s |   2010 |      10 |      134982 |  54332 |         304.94 |           304.94 |        nan    |             0 |         119.66 |
| cps2011_07s |   2011 |       7 |      133923 |  53524 |         305.95 |           305.95 |        243.69 |         53524 |         119.30 |
| cps2012_10s |   2012 |      10 |      132747 |  53704 |         309.28 |           309.28 |        248.11 |         53704 |         122.18 |
| cps2013_07s |   2013 |       7 |      131128 |  53108 |         310.94 |           310.94 |        249.88 |         40009 |         123.03 |
| cps2015_07s |   2015 |       7 |      128711 |  52690 |         316.01 |           316.01 |        194.56 |         41528 |         125.73 |
| cps2017_11s |   2017 |      11 |      127907 |  52491 |         321.08 |           321.08 |        206.48 |         42953 |         127.38 |
| cps2019_11s |   2019 |      11 |      118097 |  49528 |         324.86 |           324.86 |        214.26 |         41344 |         130.49 |
| cps2021_11s |   2021 |      11 |      102413 |  43302 |         325.85 |           325.85 |        218.53 |         36559 |         132.68 |
| cps2023_11s |   2023 |      11 |       99634 |  42204 |         330.97 |           330.97 |        231.05 |         36648 |         132.80 |

## Household any home internet (all NIU treated as No; NOTE: mobile data-plan item is NOT in IPUMS)

| SAMPLE      |   YEAR |   hh_any_home_internet_hwt |   hh_any_home_internet_personwt |   hh_any_home_internet_among_answered |   share_hh_with_answer |
|:------------|-------:|---------------------------:|--------------------------------:|--------------------------------------:|-----------------------:|
| cps2009_10s |   2009 |                      0.687 |                           0.735 |                                 0.896 |                  0.767 |
| cps2010_10s |   2010 |                      0.710 |                           0.758 |                                 0.926 |                  0.767 |
| cps2011_07s |   2011 |                      0.704 |                           0.754 |                                 0.993 |                  0.709 |
| cps2012_10s |   2012 |                      0.747 |                           0.792 |                                 0.747 |                  1.000 |
| cps2013_07s |   2013 |                      0.556 |                           0.589 |                                 0.741 |                  0.750 |
| cps2015_07s |   2015 |                      0.734 |                           0.775 |                                 0.734 |                  1.000 |
| cps2017_11s |   2017 |                      0.779 |                           0.819 |                                 0.779 |                  1.000 |
| cps2019_11s |   2019 |                      0.798 |                           0.833 |                                 0.798 |                  1.000 |
| cps2021_11s |   2021 |                      0.818 |                           0.848 |                                 0.818 |                  1.000 |
| cps2023_11s |   2023 |                      0.848 |                           0.872 |                                 0.848 |                  1.000 |

## Persons 15-24 (CISUPPWT; CIPWT for random-respondent items). NIU treated as No.

| SAMPLE      |   YEAR |   n_15_24 |   uses_internet_anywhere_CINTUSE |   internet_at_home_CINETHP |   internet_outside_home_CINTOUT |   any_use_proxy |   email_CIEMAIL_cipwt |   internet_phone_calls_CINTPHON_cipwt |
|:------------|-------:|----------:|---------------------------------:|---------------------------:|--------------------------------:|----------------:|----------------------:|--------------------------------------:|
| cps2009_10s |   2009 |     17404 |                            0.827 |                    nan     |                         nan     |           0.827 |               nan     |                               nan     |
| cps2010_10s |   2010 |     17402 |                          nan     |                    nan     |                         nan     |           0.000 |               nan     |                               nan     |
| cps2011_07s |   2011 |     17342 |                          nan     |                      0.749 |                         nan     |           0.809 |                 0.742 |                                 0.153 |
| cps2012_10s |   2012 |     16655 |                          nan     |                      0.830 |                         nan     |           0.830 |                 0.711 |                                 0.200 |
| cps2013_07s |   2013 |     16496 |                          nan     |                      0.619 |                           0.475 |           0.675 |                 0.724 |                                 0.227 |
| cps2015_07s |   2015 |     16189 |                          nan     |                      0.771 |                           0.738 |           0.852 |                 0.892 |                                 0.446 |
| cps2017_11s |   2017 |     15307 |                          nan     |                      0.786 |                           0.733 |           0.851 |                 0.910 |                                 0.605 |
| cps2019_11s |   2019 |     13725 |                          nan     |                      0.789 |                           0.746 |           0.850 |                 0.900 |                                 0.641 |
| cps2021_11s |   2021 |     11703 |                          nan     |                      0.804 |                           0.735 |           0.856 |                 0.934 |                                 0.735 |
| cps2023_11s |   2023 |     11420 |                          nan     |                      0.836 |                           0.770 |           0.885 |                 0.931 |                                 0.746 |

Interpretation:
- `hh_any_home_internet_hwt` = share of households (HWTFINL, one row per HH) in which any member is coded Yes on CINETHH (2009-10) or CINETHP (2011+), NIU treated as No.
  This is a clean "any home internet" measure only in 2012 and 2015-2023 (universe = everyone; `share_hh_with_answer` = 1.00): 74.7% (2012), 73.4% (2015), 77.9%, 79.8%, 81.8%, 84.8% (2023).
  In 2009-2011 the item is only asked of internet/computer-using respondents, and in 2013 only of MISH 2-4/6-8 (so the 0.556 is a half-sample artifact; restrict to MISH in (2,3,4,6,7,8) and it is 0.741).
- Persons 15-24: the requested "uses the internet on a mobile device" is unavailable. Closest proxies: CINETHP (home access), CINTOUT (uses internet outside home), and `any_use_proxy` (any location Yes).
  2010 and 2012 have no person-level use items (household-only waves). CINTPHON (internet phone/video calls, CIPWT) rising 15% -> 75% tracks smartphone-era adoption but is not a device measure.

## Geography coding check


| SAMPLE      |   n_metfips_ident |   n_metfips_codes |   n_metarea_ident |   n_county_ident |   n_states |   share_pop_metfips_ident |
|:------------|------------------:|------------------:|------------------:|-----------------:|-----------:|--------------------------:|
| cps2009_10s |             97695 |               264 |             97695 |            59226 |         51 |                     0.807 |
| cps2010_10s |             98389 |               264 |             98389 |            59790 |         51 |                     0.806 |
| cps2011_07s |             97756 |               264 |             97756 |            59201 |         51 |                     0.810 |
| cps2012_10s |             97949 |               264 |             97949 |            59346 |         51 |                     0.813 |
| cps2013_07s |             96557 |               264 |             96557 |            58565 |         51 |                     0.812 |
| cps2015_07s |             94198 |               295 |             94198 |            55900 |         51 |                     0.822 |
| cps2017_11s |             94714 |               260 |             94714 |            56082 |         51 |                     0.828 |
| cps2019_11s |             87309 |               260 |             87309 |            51200 |         51 |                     0.827 |
| cps2021_11s |             76442 |               260 |             76442 |            44391 |         51 |                     0.834 |
| cps2023_11s |             74065 |               260 |                 0 |            42954 |         51 |                     0.832 |


