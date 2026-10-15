# School accountability / testing-pressure policy timing, 2005-2019 ("T2 school pressure" arm)

Built 2026-09-16 by `scripts/school_policy/build_state_policy_timing.py` (re-run with
`uv run python scripts/school_policy/build_state_policy_timing.py`). All dated cells are hard-coded in that
script with a source URL, and every cell has a matching row in the events file.

## Outputs (`data/extracts/school_policy/`)

| file | shape | content |
|---|---|---|
| `state_policy_timing.csv` | 51 rows (50 states + DC) | one row per state; dates as YYYY-MM (or year / school year) |
| `state_policy_events.csv` | 519 rows | long: `state, policy, date, value, source_url, note, conflict_or_alt` (one row per state x policy x date x source) |
| `state_year_policy.csv` | 765 rows (51 x 2005-2019) | 0/1 in-force indicators + `pressure_index` (simple sum, 0-5) |

Source downloads and text extractions are in `data/external/school_policy/` (archived ed.gov pages fetched via
web.archive.org with curl; PDFs from ERIC/NCTQ/Achieve/Education First; Wikipedia/corestandards captures; parsed
CSVs `esea_flex_state_pages_parsed.csv`, `corestandards_2012_adoption_dates.csv`).

## Year convention for `state_year_policy.csv`

`year` = the school year ending in spring of that calendar year (2013 = SY 2012-13). Rules:

* `rttt_winner`: 1 from the school year containing the award under the same month rule as the waivers (awards through
  September count from the school year ending that year: Phase 1 March 2010 and Phase 2 August 2010 -> 2010; Phase 3
  December 2011 -> 2012) through 2015 (four-year grants, most with no-cost extensions into 2015). 0 after. (Until
  2026-10-15 Phase 3 was coded from 2011.)
* `waiver_in_force`: 1 from the school year containing the approval date (Feb-Sept 2012 approvals -> 2012)
  through 2016 (all ESEA flexibility waivers void Aug 1 2016). WA = 0 from 2015 (revoked Apr 24 2014); OK kept
  at 1 for 2015 (revoked Aug 28 2014, reinstated Nov 2014). Never-approved: CA (statewide; 8 CORE districts had a
  district waiver from Aug 6 2013), IA, MT, NE, ND, VT, WY.
* `cc_aligned_test_in_force`: 1 from `common_core_aligned_test_first_year` (first spring administration of an
  operational statewide test aligned to CCSS or a CCSS-derived rebrand) onward; forced to 0 for states that
  formally repealed CCSS before/after testing (IN and OK never had one; SC = 1 in 2015 only, since SC READY 2016
  targets the replacement SC standards). Rebrands (FL, AZ, GA, AL, PA, MO, NJ, LA, TN, WV, KY, NY) stay 1 -
  their replacement standards are CCSS revisions per Achieve/ECS. KY = 2012, NY/NC/MN/DC = 2013, UT/AL = 2014,
  TN = 2017 (2016 TNReady failure), IA = 2019, most others 2015.
* `teacher_eval_test_based_in_force`: 1 from Kraft et al. (2020) Table A1 "Implement Evaluation" year (first
  year student-growth/test-based evaluations were implemented statewide). DC = 2009 (DCPS IMPACT; district-level).
  Never by 2016: CA, IA, MT, VT (no policy), NE, WY (law passed, never implemented). NCTQ 2019 reports that AK, AR,
  KS, KY, ME, NM, NC, OK, WI, WY and DC dropped the growth requirement between 2015 and 2019 - the exact drop year
  is NOT captured, so the indicator stays 1 through 2019 for those states (flag `teacher_eval_dropped_by_2019`).
* `exit_exam_in_force`: 1 if the graduating class of `year` had to pass a state exam to receive a diploma
  (`hs_exit_exam_first_class` .. `hs_exit_exam_last_class_required`), using CEP 2010 Table 1 for the 2009-10
  status and predecessor exams (`PRIOR_EXAM`, approximate first class) so that 2005-2009 is not understated for
  MD/MN/MS/NC/OH/SC/TN etc. Counts: 24-25 states 2008-2012, 17 in 2015-16, 13 in 2017-19 (matches EdWeek's "13
  states in 2019").
* `pressure_index` = plain sum of the five indicators (no weighting).

## Column notes for `state_policy_timing.csv`

1. **Race to the Top** - `rttt_phase`, `rttt_award_date`. Verified against the archived ed.gov awards page
   (Phase 1 Mar 29 2010: DE, TN; Phase 2 Aug 24 2010: DC, FL, GA, HI, MD, MA, NC, NY, OH, RI; Phase 3 Dec 22 2011:
   AZ, CO, IL, KY, LA, NJ, PA). Wikipedia says Dec 23 2011 for Phase 3 (recorded in `conflict_or_alt`).
2. **ESEA flexibility** - `esea_waiver_approved_date` from each state's archived ed.gov page
   (`.../esea-flexibility/map/{st}.html`, capture Sept 2015). First batch Feb 9 2012: CO, FL, GA, IN, KY, MA, MN,
   NJ, OK, TN (+ NM Feb 15). Window 2 approvals May 29-Aug 8 2012; Window 3 Sept 2012-Sept 2013 (AK/HI/WV May 20
   2013, AL Jun 12, NH Jun 26, ME Aug 12, PA Aug 20, TX Sep 30 2013); IL Apr 18 2014 (its page header still said
   "under review" but posted the approved Apr 18 2014 request). Revocations/reinstatement and the Aug 1 2016
   expiry are separate events. Renewal-letter dates (2015) are in `esea_flex_state_pages_parsed.csv`.
3. **Common Core** - `common_core_adopted_date` from the June 2012 capture of corestandards.org "In the States"
   (each state's board vote with the state's own press release linked in the events note); AZ (Jun 28 2010) and
   MN (2010, ELA only, month unverified) added from other sources. **Conflict:** corestandards listed Wyoming as
   "June 16, 2010" but WY adopted in June 2012; table uses 2012-06. Non-adopters AK, NE, TX, VA.
   `common_core_first_full_implementation_school_year` = first school year with K-12 ELA *and* math implemented,
   from Achieve, *Closing the Expectations Gap 2013*, p.39 (state self-reports as of 2013; IN/OK never got there).
   `common_core_aligned_test_first_year`, `consortium` (2010 membership -> what was actually used spring 2015),
   `consortium_test_spring_2015`, `parcc_exit_date` (Wikipedia PARCC participation table, month-level, secondary
   source), `sbac_exit_date` (year-level, secondary). `common_core_repeal_or_replace_date` + `_type`: formal
   repeals IN 2014-03-24, OK 2014-06-05, SC 2014-06; review/replace laws MO 2014-07 (new standards 2016-04),
   TN 2015-05 (2017-18), LA 2016-03, NJ 2016-05, WV 2015-12-17, AZ board vote 2015-10-26; renames FL 2014-02-18,
   GA 2015-02-19, AL 2013-11; KY review law 2017-02. Other states revised without repeal (AR, MS, NH, NY 2017,
   UT, WI, MA 2017, OH 2017) - not coded.
4. **Teacher evaluation** - `teacher_eval_test_based_law_year` / `teacher_eval_implemented_year` from Kraft,
   Brunner, Dougherty & Schwegman (2020, *J. Public Econ.*; EdWorkingPaper 19-169) Appendix Table A1, which was
   itself built from NCTQ Yearbooks and state statutes. Cross-checks: `teacher_eval_nctq2011_significant` (NCTQ
   Oct 2011 list of 17 states + DCPS whose evaluations are "significantly" informed by growth),
   `teacher_eval_nctq2015_status` (NCTQ 2015: no policy = CA, IA, MT, NE, VT; waiver-only = AL, NH, TX),
   `teacher_eval_dropped_by_2019` (NCTQ 2019). The NCTQ 2015 per-state figures are check-mark images and did not
   extract; the ECS/NCTQ database pages were not fetchable.
5. **Exit exams** - `hs_exit_exam_class_of_2010` from CEP, *State High School Tests: Exit Exams and Other
   Assessments* (Dec 2010), Table 1 (24 states; OK/OR/RI/WA-HSPE started with later classes; WA's WASL already
   applied from class of 2008). Drop years (first class not required): NC 2011, TN 2012, MN 2013, AL 2014 (board
   vote Nov 2013), AK 2014 (HB 278, retroactive), AZ 2015 (law Feb 20 2015), CA 2015 (SB 725/SB 172), GA 2015
   (board plan Apr 2011 for 9th graders entering 2011-12; HB 91 Mar 2015 retroactive), SC 2015 (Act 155 Apr 14
   2014), AR 2015 (approximate), ID 2017, MS 2017 (ECS; NCES 2017 says through class of 2018 - conflict), NV 2017
   (AB 288 of 2013; class of 2016 last), OK 2017 (HB 3218 of 2016), WA 2020 (HB 1599 of 2019). PA and RI never
   enforced their planned exams; CT/CO never had one in this window.
6. **Opt-out 2015** - `optout_2015_pct` only where a statewide percentage was published: NY 20% (NYSED), CO ~11%
   (CDE median), RI 12% (RIDE), NJ 4.6% (grades 3-8). Counts (FairTest Nov 2015) in `optout_2015_count` for 14
   states. `ed_participation_letter_2015` = the 13 states ED wrote to in Dec 2015 for <95% participation
   (CA, CO, CT, DE, ID, IL, ME, NY, NC, OR, RI, WA, WI).

## Coverage summary

| item | states with a value | notes |
|---|---|---|
| RTTT award | 19 (+32 none) | all verified |
| ESEA waiver approval date | 44 incl. DC (+7 never) | all from archived ed.gov state pages |
| CC adoption date | 47 (45 states + DC + MN-ELA) | 46 with day-level date; MN year only; WY conflict |
| CC full implementation SY | 47 | Achieve 2013 self-reports |
| CC aligned test first year | 45 | WY unverified; IN/OK/AK/NE/TX/VA none |
| CC repeal/replace/rename | 13 events | secondary sources for GA/AL/OK/SC (Wikipedia/ECS) |
| PARCC / SBAC exit dates | 18 / 8 | Wikipedia + Education First (secondary) |
| Teacher-eval law / implemented year | 47 / 45 | Kraft et al. Table A1; DC from NCTQ |
| Exit exam status class of 2010 | 51 | CEP 2010 |
| Exit exam drop year | 15 | AR approximate; MS/ID conflicts noted |
| Opt-out 2015 pct / count | 4 / 14 | |

## Not verified / caveats

* ESEA per-state pages for CA and MT were not archived (CA = CORE districts only; MT never applied).
* Teacher-evaluation *drop* years after 2015 (11 jurisdictions per NCTQ 2019) are not dated; also several
  states delayed consequences/hold-harmless in 2014-16 (not coded).
* Consortium membership/exits and the 2014-15 test-by-state list rely on Wikipedia and Education First (the
  EdWeek interactive maps could not be fetched); the 2014-15 counts (18 SBAC, 11+DC PARCC) match EdWeek.
* Colorado's PARCC exit (2018) and Wyoming's first aligned PAWS year are unverified.
* Arkansas exit-exam drop year (2015) inferred from absence in ECS's May 2016 list and FairTest 2017.
* Predecessor exit-exam start years (`PRIOR_EXAM`) are approximate and only matter for 2005-2009.
* Alabama's waiver approval: page text says Jun 12 2013, approved document dated Jun 21 2013.
* The EdWeek 2014-15 opt-out map and the NCTQ 2013 "Connect the Dots" state table were not obtainable.
