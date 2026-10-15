# GSHS (WHO/CDC Global School-based Student Health Survey) acquisition and stacking

Purpose: adolescent distress outcomes (loneliness, worry-induced sleeplessness, suicidal ideation/plan/attempt,
no close friends) across many LMIC country-rounds 2003-2023, for the mobile-internet-arrival design.

## Source and access
- Sole live source: WHO NCD Microdata Repository (NADA), collection GSHS,
  https://extranet.who.int/ncdsmicrodata/index.php/catalog/GSHS . Enumerated with the NADA JSON API
  `index.php/api/catalog/search?collection=GSHS&ps=500&format=json` (165 entries, all `data_access_type=direct`).
- Access: no login/registration. Each catalog entry requires a per-entry click-through acceptance of the
  public-use terms (POST `accept` with the `ncsrf` token on `/catalog/<id>/get-microdata`), after which the data
  files are listed at `/catalog/<id>/download/<fileid>`. Terms: statistical research only, no redistribution,
  no re-identification, cite WHO/CDC GSHS, send WHO copies of publications (ncdmonitoring@who.int).
- CDC's former GSHS pages (cdc.gov/gshs, incl. archive.cdc.gov) now return 404; CDC transferred hosting to WHO.
- Variable names + labels per entry via `api/catalog/<idno>/variables`; value labels come from the Stata .dta files
  (every entry ships CSV + DTA of the "Public Use" file).

## Scripts and outputs
- `scripts/gshs/01_download_gshs.py`: enumerate, accept terms, download all data files sequentially (1.5 s sleeps),
  writes `data/external/gshs/<ISO3>_<YEAR>/{files.json, catalog.json, variables.json, data files}`.
- `scripts/gshs/02_stack_gshs.py`: harmonize + stack -> `data/extracts/gshs/gshs_stacked.parquet`,
  `gshs_inventory.csv` (country-round), `gshs_files.csv` (per data file, with source-variable mapping and QN checks).

## Status (2026-09-16 18:50)
- Download of all 165 catalog entries was started in the background (`nohup uv run python scripts/gshs/01_download_gshs.py`,
  log in the session scratchpad `gshs/download.log`); ~13 s per entry, slower for Argentina 2012/2018 (24 provincial files each).
  It is idempotent: re-running skips finished entries. When it ends, run `uv run python scripts/gshs/02_stack_gshs.py`
  to rebuild the stacked parquet + inventory over everything downloaded. As of this note 13/165 entries were down and
  stacked (110,586 students) with all mappings validated against the CDC QN* dichotomies (agreement = 1.0 wherever both exist).
- Full WHO catalog listing (165 country-rounds with catalog ids) saved to `data/compiled/gshs/gshs_who_catalog_165.csv` (written by `scripts/download/gshs/01_download_gshs.py`).

## Harmonization (02_stack_gshs.py)
Items are located by variable-label regex (Q-numbers shift across rounds: e.g. lonely = Q22 nearly always, but suicide
consider = Q24 in 2013+ core vs Q25 in 2007-2012; parents-understand Q53 vs Q56). Recoding uses the .dta value-label text,
falling back to the standard CDC codes when a file has no labels (`coding_<item>` = labels/assumed in gshs_files.csv).
- lonely, worried_sleep, parents_understand: 1 if "Most of the time"/"Always", 0 if Never/Rarely/Sometimes.
- sad_hopeless (2003-2012 rounds only), suicide_consider, suicide_plan: Yes=1/No=0.
- suicide_attempt: 1 if "1 time" or more, 0 if "0 times" (item absent in most pre-2013 questionnaires: ARG 2007, AIA 2009, BRB 2011 ...).
- no_close_friends: 1 if "0" close friends, 0 otherwise.
- pa_days: days physically active 60+ min in past 7 days (0-7, parsed from label). sit_3plus: sitting 3+ hours/day.
- age_yrs: integer parsed from label (bottom/top codes vary: "11 or younger" and "16 or older" in 2007 vs "18 or older" in 2013+;
  raw_age preserved). female 0/1 from Male/Female labels. grade = raw country-specific code.
- weight/psu/stratum: taken from columns named weight|wt, psu|cluster, stratum|strata (case-insensitive); all rounds so far use
  `weight`, `psu`, `stratum`.
- Raw items kept as raw_<construct>; source variable name in src_<construct>. Any item whose label mentions
  internet/phone/computer/screen/online/social media/cyber/TV/video game is kept as net_<varname> (so far only
  "Cyber bullied in past 12 months", q68, Argentina 2018; 2017+ rounds to be checked when downloaded).
- Rounds shipping a national file plus subnational parts (Antigua+Barbuda 2009, Algeria 2011 two regions, Argentina 2012/2018
  provinces) stack only the national file (`national_file` flag); the parts are listed in gshs_files.csv with stacked=False.
- Validation: for every recoded indicator, agreement with the CDC-derived QN<n> variable of the same question number is
  reported as qncheck_<item> in gshs_files.csv (all 1.0 so far).
- Known gaps: Algeria 2011 omitted the mental-health module; Barbados 2011 lacks the suicide items.

## Status update (18:58)
- 49/165 entries downloaded and stacked (249,053 students); download continuing in background. All QN agreement checks = 1.0;
  every round has `weight`/`psu`/`stratum`.
- Rounds whose public-use file omits the mental-health module entirely (Q22-Q27 absent; not a mapping failure):
  Algeria 2011, Chile 2013, Colombia 2007, Ghana 2007, Eswatini 2003. Suicide items absent (lonely present) in
  Barbados 2011, Cook Islands 2011, Djibouti 2007, Egypt 2006/2011. suicide_attempt absent in most pre-2013 rounds.

## Status update (19:05): 69/165 rounds stacked, 318,900 students (target of 60 met); download continuing
- All 69 use `weight`/`psu`/`stratum`; all QN agreement checks = 1.0.
- Phone/internet items exist in the 2022-2023 rounds (new "ot_" module): GHA 2022 and IND 2022: `ot_mobilehours`
  (hours/day mobile phone past 7 days) + `ot_b_mobilehours` (3+ h/day), `in_cyberbull`; JAM 2023 additionally
  `ot_mobilephone` (regular access to a mobile phone), `ot_screentime` (screen time on school day), `ot_parmediarule`
  (parental rules on social media/internet). 2017-2019 rounds have only cyberbullying (ARG 2018 q68, BOL 2018 q100).
  These are kept in the stacked file as `net_<varname>` columns (raw codes; see variables.json for labels).
- No suicide items: BRB 2011, CHL 2013, COK 2011, COL 2007, DJO 2007, DZA 2011, EGY 2006, EGY 2011, GHA 2007, IND 2007, SWZ 2003.
