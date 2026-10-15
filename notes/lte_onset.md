# U.S. LTE (4G) launch dates by metropolitan market — methods note

Purpose: treatment timing (first LTE availability by CBSA and by carrier) for an event study.
Built 2026-09-16 from carrier press releases and contemporaneous tech-press copies of them.

## Files (`data/external/lte/`)

| file | what |
|---|---|
| `lte_launches_long.csv` | one row per (carrier, market-as-announced, launch date). Columns: `carrier`, `market_name_as_announced`, `state`, `launch_date` (YYYY-MM-DD, or YYYY-MM when only the month is known/bracketed), `cbsa_code` (2013 CBSA, blank if no CBSA), `cbsa_name`, `cbsa_type`, `source_url`, `source_note`, `confidence`. |
| `lte_onset_by_cbsa.csv` | one row per CBSA (big-four carriers only; MetroPCS excluded): `first_launch_date`, `first_carrier`, `second_carrier_date`, `verizon_date`, `att_date`, `sprint_date`, `tmobile_date` (+ a `*_confidence` for each), `n_carriers`, `n_sources`, `pop_2013`, `pop_rank_2013` (rank among metropolitan statistical areas, Census 2013 estimates). |
| `list1_2013.xls`, `list2_2013.xls` | Census Feb-2013 CBSA delineation files (counties; principal cities) used for name matching. |
| `cbsa-est2013-alldata.csv` | Census population estimates (for ranking). |
| `att_lte_markets_1512.pdf` | AT&T's own "4G LTE markets" one-pager (26 markets, ~Jan 2012). |

Code: `scripts/lte_waves_raw.py` (every wave transcribed with its URL) and `scripts/build_lte_launches.py`
(`uv run --with xlrd python scripts/build_lte_launches.py`). Re-run after editing the raw file.

## Method

1. For each carrier, located the national "we are launching LTE in N new markets on date D" press release
   for each rollout wave (Verizon issued one roughly monthly on a Thursday 2011-2012; AT&T, Sprint and
   T-Mobile less regularly), or, when the carrier site blocked fetching, a same-day tech-press article that
   reprinted the release's market list verbatim (Engadget, Droid-Life, TechCrunch, Phone Scoop, AppleInsider,
   PhoneArena, etc.). For AT&T, many markets were only announced through per-city PRNewswire releases
   ("AT&T 4G LTE Available In X"), which were searched individually for the larger CBSAs.
2. Every named market was transcribed as announced (state codes normalized to two letters) into
   `lte_waves_raw.py` with the wave date, the URL actually used, a note, and a confidence grade:
   `high` = carrier release / verbatim wire copy; `medium` = tech-press summary or a bracketed month;
   `low` = leaked/planned schedule or a fragment of a list (see `source_note`).
3. Markets were mapped to 2013 CBSA codes by matching the first city token against the CBSA principal-city
   list (list2) and CBSA-title cities (list1) within the same state, with ~400 manual overrides for nicknames
   ("Greater Lehigh Valley" -> Allentown; "Twin Cities"; "Greater Hampton Roads"; "Quad Cities"; "Tri-Cities";
   "Northern New Jersey" -> New York) and suburbs/counties mapped to their parent CBSA (Oakland -> SF, Tacoma ->
   Seattle, Frederick MD -> Washington, Anne Arundel -> Baltimore, Bronx/Brooklyn -> New York). Every manual code
   is validated against the delineation file; a market announced as two metros (e.g. "Raleigh-Durham",
   "Greensboro/Winston-Salem", "Salt Lake City-Ogden") yields one row per CBSA. 15 announced places have no
   2013 CBSA (Lake of the Ozarks MO, Logan WV, Lamar/La Junta CO, Richfield UT, McCook NE, Brattleboro VT,
   Bedford PA, Dillon SC, Grand Rapids MN, West Point MS, Shenandoah County VA, USVI) and keep a blank code.
4. Per-CBSA onset takes, for each carrier, the earliest date among `high`/`medium` rows (falling back to `low`
   rows only if nothing better exists); `first_launch_date` is the earliest carrier date. Month-only dates sort
   as the end of that month. Interpret a YYYY-MM date as "live by the end of that month".

## Headline numbers (from the build script output)

- 967 long rows (Verizon 442, AT&T 243, Sprint 234, T-Mobile 47, MetroPCS 1). Confidence: Verizon 413 high /
  29 medium; AT&T 97 high / 92 medium / 54 low; Sprint 225 high / 9 medium; T-Mobile 7 high / 10 medium / 30 low.
- 505 CBSAs have a first-launch date (332 metropolitan, 173 micropolitan).
- Top-50 metros: 49/50 any carrier (Verizon 49, AT&T 47, Sprint 30, T-Mobile 31).
- Top-100 metros: 98/100 any carrier (Verizon 98, AT&T 80, Sprint 46, T-Mobile 37).
  Missing: Riverside-San Bernardino and Oxnard-Thousand Oaks (both inside Verizon's/AT&T's "Los Angeles" launch
  footprint but never announced as separate markets; no source gives a date).
- Top-150 metros: 146/150 any carrier (Verizon 141, AT&T 106, Sprint 69, T-Mobile 37).

## Waves captured (source in each row of the long file)

**Verizon** (all with full lists unless noted): 2010-12-05 (39 metros); 2011-04-21 (6); 2011-05-19 (10);
2011-06-16 (19); 2011-07-21 (28); 2011-08-18 (15); 2011-09-15 (26); 2011-10-20 (22); 2011-11-17 (14);
2011-12-15 (11); 2012-01-19 (5); 2012-02-16 (1); 2012-04-19 (27); 2012-05-17 (28); 2012-06-21 (46);
2012-07-19 (33); 2012-08-16 (34); 2012-10-18 (21 of 23); 2012-11-15 (partial, 5 named); 2012-12-20 (29).
Verizon reached 190 markets by end-2011, 470 by end-2012 and ~500 by mid-2013.

**AT&T**: 2011-09-18 (5); 2011-11-06 (4); 2011-11-20 (6); 2012-01-05 (11); 2012-02-15 (3); spring 2012 (10,
bracketed by the 2012-03-12 announcement and AT&T's 2012-05-10 infographic; New Orleans/Baton Rouge exact
2012-05-17); Nashville 2012-06-20; Buffalo 2012-07-09; Miami/Ft Lauderdale/WPB 2012-07-26; 2012-09-06 (9);
Albany 2012-09-12; Philadelphia 2012-09-14; 2012-09-20 (8 incl. Detroit, Seattle, Portland, Pittsburgh,
Sacramento; Cincinnati same day); week of 2012-11-12 (8, incl. Denver, Twin Cities 11-15, Tacoma 11-14);
2012-11-16 (17); Grand Rapids MI 2012-12-10; 2012-12-18 (5); 2012-12-21 (10; 124 markets at year-end 2012);
Norfolk 2013-02-05; Tallahassee 2013-02-25; Augusta 2013-03-14; Fresno/Reno 2013-04-03; 2013-05-03 (16);
Colorado Springs 2013-06-05; 2013-07-02/03 (35); 2013-08-07 (13; 359 markets); Des Moines 2013-11-06;
plus 50 markets announced 2013-08-21 as "by year-end 2013" (recorded as 2013-12, low confidence).

**Sprint**: 2012-07-15 (15); 2012-08-29 (4); 2012-11-13 (9); 2012-11-26 (11); 2012-12-19 (6); 2013-01-28 (4,
incl. Boston); 2013-03-04 (9); 2013-04-18 (21, incl. Los Angeles, Charlotte, Memphis, Norfolk);
2013-06-17 (22, incl. Miami, New Orleans, Tampa, Raleigh); 2013-07-29 (41, incl. Philadelphia, Nashville,
Portland, Oakland, Jacksonville); 2013-09-16 (34, incl. Oklahoma City); 2013-10-29 (45 + remaining NYC
boroughs); 2013-12-16 (70 markets; only the 9 named examples captured, incl. San Diego, Orlando, Louisville,
Birmingham, Little Rock, Madison).

**T-Mobile**: 2013-03-26 (7 metros, official). Then only: a leaked internal schedule (Wirefly, 2013-05-03)
listing May and June 2013 launches for ~30 metros (recorded as YYYY-MM, `low`), and T-Mobile's 2013-07-10 release
naming 10 large metros among the 116 then live (recorded as 2013-07 upper bound, `medium`). T-Mobile's full
116- (Jul 2013), 154- (Sep 2013) and 233-market (Oct 2013) lists exist but were not retrievable as text.

**MetroPCS**: Las Vegas 2010-09-21 (first U.S. LTE; kept out of the onset file).

## Known gaps and caveats

- Verizon: the 2012-03-15 wave (~7 markets), a September-2012 wave (~16 markets implied by counts 371 -> 387),
  the rest of the 2012-11-15 wave, and all 2013 waves (~30 mostly small markets) were not captured. Detroit is
  not in any captured list although Verizon "expanded" Detroit on 2011-06-16; recorded as 2011-06 upper bound.
  Riverside-San Bernardino, Oxnard, Santa Rosa, Vallejo, Trenton, Ann Arbor were never announced as separate
  Verizon markets (covered as part of LA / Bay Area / NY-Philadelphia / Detroit launches; no date assigned).
  Anchorage, Corpus Christi and Naples have no Verizon date found (likely 2013 launches).
- AT&T: no Wikipedia/complete compiled list exists; coverage comes from wave articles plus per-city releases.
  About 9 markets launched between 2012-09-20 and 2012-11-12 and most of Jan-Apr 2013 (a HowardForums tracker,
  which could not be fetched, counts 2 + 9 + 14 + 47 launches in those months) are missing. Among top-150
  metros the AT&T date is still missing for: Allentown, Asheville, Brownsville, Cape Coral, Davenport, Dayton,
  Fayetteville (NC and AR), Flint, Fort Wayne, Greensboro, Winston-Salem, Hickory, Huntington, Jackson MS,
  Knoxville, Lakeland, Little Rock, Madison, Manchester-Nashua, McAllen, Montgomery, Myrtle Beach, Reading,
  Richmond, Rockford, Salem OR, Salisbury, Salt Lake City, Santa Barbara, Savannah, Scranton, Springfield MO,
  Tulsa, Visalia, Wichita, Worcester, Youngstown (plus the LA/Bay/NY suburbs above). Most of these were on
  AT&T's "by end of 2012" list of 2012-09-06 and almost certainly launched Oct 2012 - mid 2013; the AT&T Q-end
  totals (60 on 2012-09-06, 103 on 2012-11-16, 124 on 2012-12-21, 359 on 2013-08-07) bound them.
  The 50 "by end-2013" markets are planned dates, flagged `low`.
- Sprint: 4 markets launched Sep-Oct 2012 (19 -> 23) and ~5 in Jan 2013 are unnamed; the 2013-12-16 wave is
  9/70; Chicago, Washington DC, Denver, Phoenix, Seattle, San Francisco proper, Detroit, Salt Lake City,
  Milwaukee etc. have no Sprint date (they were in the unlisted Dec-2013 batch or launched in 2014).
- T-Mobile per-metro dates are month-level and mostly `low`; treat T-Mobile as "2013-H1/H2" rather than dated.
- "Market" boundaries are the carriers', not CBSAs': a launch often covered only the core of a CBSA at first
  ("expansion" releases, which are not recorded here, added suburbs over the following 6-18 months).
- Sources that blocked fetching (PhoneArena, BusinessWire, T-Mobile newsroom, HowardForums, about.att.com,
  web.archive.org from the fetch tool) were used only through search-result snippets where noted in
  `source_note`; those rows carry `medium`/`low` confidence. The archived Verizon newsroom
  (news.verizonwireless.com, 2,000+ releases indexed in the Wayback CDX) is the natural next step to close the
  Verizon gaps; a crawl was started but archive.org connections dropped after ~15 pages.
